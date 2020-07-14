import pyautogui
import numpy as np
import cv2

from PIL import Image
from time import sleep
import time
import mss
import math

class Navigator:
    def __init__(self, controller, resHorz, resVert):
        self.controller = controller
        self.resHorz = resHorz
        self.resVert = resVert
        #load worldmap ahead of time
        self.worldmap = cv2.imread('worldmap.png')
        #Region represents the bigMap #top,left,width,height
        self.bigmapRegion = (
            6,
            29,
            resHorz-263,  #263 pixels from right to end of map
            resVert-165-45-26-29 #165(chatbox) 45(botBorder) 26(taskbarH) 29(topWindowHeight)
        )

        #Region represents the overviewMap #top,left,width,height
        self.overviewRegion = (
            self.bigmapRegion[2] + 6 + 1 - 196 -2, #bigmapWidth leftBorder overviewOffset overviewWidth overviewBorder
            self.bigmapRegion[3] - 112 + 29 - 1, #bigmapHeight overviewHeight topWindowHeight overviewBorder
            196,    #width
            112,    #height
        )


    def printLocation(self):
        while True:
            t0=time.time()
            x,y = self.getLocation()
            print('x:',x,'y:',y,'time:',time.time()-t0,end='\r')
        
    def microNavigate(self,destX,destY):
        arrived = False
        print('navigating to x:',destX,':y',destY)
        while not arrived:
            curX, curY = self.getLocation()

            #find difference vector
            difX, difY = destX-curX, destY-curY

            vec1 = [1,0]
            vec2 = [difX, difY]

            #find distance to destination
            distance = np.linalg.norm(vec2)
            
            #find angle to object
            angle = self.controller.angle(vec1,vec2)*3.14159265359/180
            #convert angle to radians

            #x = clickableCompassRadius * cos(angle)
            x = 136/2*math.cos(angle)
            #y = clickableCompassRadius * sin(angle) # y needs to be flipped
            y = -(136/2*math.sin(angle))

            #convert relative xy to global xy
            #compass will always be centered here
            circX = self.resHorz - 118
            circY = 108

            #55 comes from the fact that the minimap represents 55 rawx rawy coords in every direction
            clickVecMag = 55 if distance >= 55 else distance
            clickVecMag /= 55

            x = circX + x*clickVecMag
            y = circY + y*clickVecMag

            self.controller.clickPixel(x,y)

            arrived = False if distance > 15 else True

            #debugging print
            #print('angle:',angle,'x:',x,'y:',y,'onComp:',compassContains,'dist:',distance,'arrived',arrived,'time:',time.time()-t0,end='\r')
            sleep(1)
        
        while(self.controller.moving()):
            sleep(1)
        curX,curY = self.getLocation()
        print('Arrived at x:',curX,'y:',curY)

    def macroNavigate(self,destX,destY):
        #calculate path based on nodes
        pass

    def compassContainsDest(self,curX,curY,destX,destY):
        minX = curX - 55
        maxX = curX + 55
        minY = curY - 55
        maxY = curY + 55
        #print(minX,curX,maxX,minY,curY,maxY,destX,destY)
        if minX < destX and destX < maxX and minY < destY and destY < maxY:
            return True
        return False

    #finds x,y coordiantes of bot
    def getLocation(self):
        # t0 = time.time()
        # #take big screenshot
        # fullshot = pyautogui.screenshot()
        # print('org:',time.time()-t0)
        
        fullshot = None
        t0 = time.time()
        with mss.mss() as sct:
            fullshot = sct.grab(sct.monitors[1])
            fullshot = Image.frombytes("RGB", fullshot.size, fullshot.bgra, "raw", "BGRX")

        #crop out relavent parts needed
        overviewShot = fullshot.crop((
            self.overviewRegion[0], 
            self.overviewRegion[1],
            self.overviewRegion[0]+self.overviewRegion[2],
            self.overviewRegion[1]+self.overviewRegion[3]
        ))

        bigMapShot = fullshot.crop((
            self.bigmapRegion[0],
            self.bigmapRegion[1],
            self.bigmapRegion[0]+self.bigmapRegion[2],
            self.bigmapRegion[1]+self.bigmapRegion[3]
        ))



        #find rough location based on overview
        pixelList = []
        for y in range(overviewShot.height):
            for x in range(overviewShot.width):
                pixel = overviewShot.getpixel((x,y))
                if pixel[0]>190 and pixel[1] < 100 and pixel[2] < 100:
                    pixelList.append((x,y))
        
        left = pixelList[0][0]
        top = pixelList[0][1]

        bottom = top + 10-1 #size of red box at default zoom
        right = left + 24-1
    
        #convert to cv2 image
        bigMapShot = cv2.cvtColor(np.array(bigMapShot), cv2.COLOR_RGB2BGR)

        #scale top,left,bottom,right to worldmap size
        worldmapWidth = len(self.worldmap[0])
        worldmapHeight = len(self.worldmap)

        widthScalar = worldmapWidth / self.overviewRegion[2] #width
        heightScalar = worldmapHeight / self.overviewRegion[3] #height

        leftOffset = int(round(left * widthScalar - 2*left,0))
        topOffset = int(round(top * heightScalar - 2*top,0))

        rightOffset  = int(round(right * widthScalar + 2*right,0))
        bottomOffset = int(round(bottom * heightScalar + 4*bottom,0))

        #get subimage based on scaled overviewBox
        adjustedWorldmap = self.worldmap[topOffset:bottomOffset, leftOffset:rightOffset]

        #match image to smaller template
        result = cv2.matchTemplate(adjustedWorldmap, bigMapShot, cv2.TM_SQDIFF)

        #get results of matching
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        #convert results to rough location
        top_left = min_loc
        top_left = (top_left[0]+leftOffset, top_left[1]+topOffset)
        bot_right = (top_left[0] + len(bigMapShot[0]), top_left[1] + len(bigMapShot))

        #convert rough location to precise location by finding the center
        x = (top_left[0] + bot_right[0]) // 2
        y = (top_left[1] + bot_right[1]) // 2

        return (x,y)

        


