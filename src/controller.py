import importlib
import os
import random
import copy
import cv2
import numpy as np
import imutils
import pyautogui
import mss
import time
import PIL.Image as im

from time import sleep
from math import sqrt
from yolo.runemodel import Rune_model
from navigator import Navigator

#class will handle all interaction with the GUI
class Controller:
    # model = Rune_model()
    #pixel is roughly center of screen
    centerx=(1280-26)//2
    centery=(720+12)//2
    resH = 720
    resW = 1280
    modelLoaded = False
    
    def __init__(self, display, logger, model, map_g, worldmap):
        Controller.model = model
        self.display=display
        self.navigator = Navigator(self, logger, map_g, worldmap, self.resW, self.resH)
        self.logger = logger

    def mouseLoop(self, num):
        while(True):
            print(str(num)+': '+str(pyautogui.position()))
            sleep(2)

    def screenshot(self, im_name='image.png', ):
        pyautogui.screenshot(im_name)
        
    def type(self, s):
        pyautogui.write(s)
        
    def press(self,k):
        pyautogui.press(k)

    def pressMultiple(self,keys):
        #first keys are held last key is pressed
        hKeys = keys[0:len(keys)-1]
        pKey = keys[-1]

        #hold first keys down
        for k in hKeys:
            pyautogui.keyDown(k)

        #press final key
        pyautogui.press(pKey)

        #unhold first keys
        for k in hKeys:
            pyautogui.keyUp(k)

    #for some reason keyDown doesn't work in textfields
    def hold(self, k, i):
        if k == 'backspace':
            t0 = time.time()
            while(time.time()-t0 < i):
                pyautogui.press(k)
        else:
            pyautogui.keyDown(k)
            sleep(i)
            pyautogui.keyUp(k)

    def navigate(self,destX=0,destY=0,place=None):
        if(place):
            self.navigator.macroNavigate(place=place)
        else:
            self.navigator.macroNavigate(destX,destY)


    def findIcon(self, im_name=None, confidence=.80):
        path = os.path.join(os.path.abspath(os.path.curdir), 'icons/'+str(im_name)+'.png')
        
        icon = pyautogui.locateOnScreen(path,confidence=confidence)
        box = self.convertIconToBox(icon) if icon else None

        if box == None:
            self.logger.log('Couldn\'t find icon: '+ str(im_name))

        return box

    def clickIcon(self, ic_name, confidence=.80):
        box = self.findIcon(ic_name, confidence)
        if(box is None):
            return False
        self.clickIconBox(box)
        return True


    def findAllIcons(self, im_name=None, confidence=.80):
        path = os.path.join(os.path.abspath(os.path.curdir), 'icons/'+str(im_name)+'.png')

        iconList = list(pyautogui.locateAllOnScreen(path,confidence=confidence))

        boxList = []
        for icon in iconList:
            boxList.append(self.convertIconToBox(icon))

        return boxList

    def mapOpen(self):
        return self.navigator.mapOpen()

    def inventoryFull(self):
        top = 4
        bot = 3
        left = 16
        right = 16
        vgap = 5
        hgap = 10

        region = {}
        region['left'] = left+1049
        region['top'] = top+391
        region['width'] = 190-right-left
        region['height'] = 261-bot-top
        
        img = None
        with mss.mss() as sct:
            img = sct.grab(region)
            img = im.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

        rangeX = []
        rangeY = []

        for i in range(4):
            rangeX.append(range(i*32+i*hgap, i*hgap+(i+1)*32))
        for i in range(7):
            rangeY.append(range(i*32+i*vgap, i*vgap+(i+1)*32))

        item = []
        for ry in rangeY:
            for rx in rangeX:
                invC = 0
                itemC = 0
                for y in ry:
                    for x in rx:
                        r,g,b = img.getpixel((x,y))
                        if r == 62 and g == 53 and b == 41:
                            invC += 1
                        elif r == 59 and g == 50 and b == 38:
                            invC += 1
                        elif r == 64 and g == 54 and b == 44:
                            invC += 1
                        elif r == 64 and g == 56 and b == 45:
                            invC += 1
                        else:
                            itemC += 1
                
                #prevents divide by 0
                if not invC:
                    return False

                if itemC / invC > .10:
                    item.append(1)
                else:
                    item.append(0)
        return True if item.count(1) == 28 else False

    #this box could be useful for other things too
    #it represents what an 'object' looks like to our bot without the class name
    def convertIconToBox(self, icon):
        box = {
            'left': icon[0],
            'top': icon[1],
            'right': icon[0]+icon[2],
            'bottom': icon[1]+icon[3],
            'width': icon[2],
            'height': icon[3],
            'centerx': icon[0]+icon[2]/2,
            'centery': icon[1]+icon[3]/2,
        }
        
        return box
        
    ### TODO: MOVE UTIL FUNCTION
    def mse(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err

    def moving(self,thresh=100,print=False):
        #screenshot funcion takes ~100ms
        with mss.mss() as sct:
            im_one = np.array(sct.grab(sct.monitors[1]))
            sleep(0.05)
            im_two = np.array(sct.grab(sct.monitors[1]))
            
            error = self.mse(im_one, im_two)
            moving = True if error > thresh else False

            if(print):
                print('error:',error)
                print('moving:',moving)

            return moving

    def farming(self, thresh=400):
        with mss.mss() as sct:
            region={}
            region['top']=self.centery-25
            region['left']=self.centerx-25
            region['width']=50
            region['height']=50

            me = float('-inf')

            # t0 = time.time()
            
            s0 = sct.grab(region)
            sleep(0.25)
            s1 = sct.grab(region)

            e = self.mse(np.array(s0),np.array(s1))
            farming = True if e > thresh else False
            return farming

        #print('e:',e,'me:',me,'t:',time.time()-t0,end='\r')

    # TODO: implement
    def clickIconBox(self,box):
        pyautogui.moveTo(box['centerx'],box['centery'])
        sleep(0.05)
        pyautogui.click()

    def clickPixel(self,x,y):
        pyautogui.moveTo(x=x,y=y,duration=0.15)
        pyautogui.click()

    #clicks in random location in box and returns values of where mouse clicked
    def clickObjectBox(self,box):
        top = box['top']
        left = box['left']
        bottom = box['bottom']
        right = box['right']

        #padding is applied to every side of box to ensure we click the object
        padding = 10

        clickx = random.randint(left+padding, right-padding)
        clicky = random.randint(top+padding, bottom-padding)

        duration = random.uniform(.1, .5)
        
        pyautogui.moveTo(clickx, clicky, duration)
        pyautogui.click()
        
        return clickx, clicky


    ##Function will parse objects and click closest one
    #object is string name of object to click on
    #objects is map of objects returned from detect
    #Returns x and y location of where pointer clicked
    def clickObject(self, object, objects):
        clickableObjects = []
        
        for obj in objects:
            if(objects[obj]['class'] == object):
                clickableObjects.append(objects[obj])

        #find object that is minimum distance
        minObj = clickableObjects[0]
        minDis = self.dis(clickableObjects[0]['centerx'], clickableObjects[0]['centery'], self.centerx, self.centery)

        for i in range(1,len(clickableObjects)):
            objDis = self.dis(clickableObjects[i]['centerx'], clickableObjects[i]['centery'], self.centerx, self.centery)
            if(objDis < minDis):
                minDis = objDis
                minObj = clickableObjects[i]

        clickx,clicky = self.clickObjectBox(minObj)
        minObj['angle'] = self.calcObjAngle(minObj)
        return clickx,clicky,minObj

    ##Function calulates angle between player and object
    def calcObjAngle(self, obj):
        #calc angle 
        vec1 = [1,0]
        vec2 = [obj['centerx'] - self.centerx, obj['centery'] - self.centery]
        return self.angle(vec1,vec2)

    def angle(self, vec1, vec2):
        vec1 = vec1 / np.linalg.norm(vec1)
        vec2 = vec2 / np.linalg.norm(vec2)
        angle = np.arccos(np.clip(np.dot(vec1,vec2),-1.0, 1.0))

        if(vec2[1] > 0):
            angle = 360-angle*180/3.14159265359
        else:
            angle = angle*180/3.14159265359

        return angle

    def objectIsAtCoord(self, x, y, objectName, objects):
        # print(objects)
        for obj in objects:
            object = objects[obj]
            left  = objects[obj]['left']
            right  = objects[obj]['right']
            
            top = objects[obj]['top']
            bottom = objects[obj]['bottom']

            # print(left)
            # print(x)
            # print(right)

            # print(top)
            # print(y)
            # print(bottom)

            # input()

            if(left < x and x < right and top < y and y < bottom):
                print('object still there...', '\r')
                return True

        print('object gone...')
        return False

    def dis(self, x1, y1, x2, y2):
        return sqrt((x2-x1)**2 + (y2-y1)**2)

    #TODO Probably going to start taking two screenshots for better detection
    # Need to rework tree dataset first with only topdown photos    
    def getObjects(self):
        screenshot = pyautogui.screenshot()
        
        # s = screenshot.crop((0,0,640,720))
        # s1 = screenshot.crop((640,0,1280,720))

        #screenshot.save('screenshot.png')
        img0 = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # s0 = cv2.cvtColor(np.array(s), cv2.COLOR_RGB2BGR)
        # s10 = cv2.cvtColor(np.array(s1), cv2.COLOR_RGB2BGR)

        # Padded resize
        img = self.letterbox(img0, new_shape=736)[0]

        # si0 = self.letterbox(s0, new_shape=640)[0]
        # si1 = self.letterbox(s10, new_shape=640)[0]

        # si0 = si0[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        # si0 = np.ascontiguousarray(si0)

        # si1 = si1[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        # si1 = np.ascontiguousarray(si1)

        # self.model.detect(si0, s0)
        # self.model.detect(si1, s10)

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        return self.model.detect(img, img0)
        # return self.model._callmethod('detect', [img, img0])


    ### TODO: MOVE UTIL FUNCTION
    #Function does something to format screenshot I have no idea what
    def letterbox(self, img, new_shape=(416, 416), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
        # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better test mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = new_shape
            ratio = new_shape[0] / shape[1], new_shape[1] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return img, ratio, (dw, dh)