#import pyautogui
import PIL.Image as im
import os
import cv2
import numpy as np
import imutils
import time

from time import sleep
from graph import Vertex
from graph import MapGraph

from botclient import BotClient
from yolo.runemodel import Rune_model

import subprocess
import mss

from navigator import Navigator
from controller import Controller
#########################################
# This file is for any random test code #
#########################################


#################
# Testing Graph #
#################

# g = MapGraph()

# v1 = Vertex('1',(5565,2318))
# v2 = Vertex('2',(5562,2198))
# v3 = Vertex('3', (5541,2102))

# g.addVertex(v1)
# g.addVertex(v2)
# g.addVertex(v3)
# g.addEdge(v1,v2)
# g.addEdge(v2,v3)
# g.addEdge(v1,v3)

#########################################
# Testing Screenshot Detect Object Gone #
#########################################
# def mse(imageA, imageB):
#         # the 'Mean Squared Error' between the two images is the
#         # sum of the squared difference between the two images;
#         # NOTE: the two images must have the same dimension
#         err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
#         err /= float(imageA.shape[0] * imageA.shape[1])
        
#         # return the MSE, the lower the error, the more "similar"
#         # the two images are
#         return err

# subprocess.call(['clear'])

# model = Rune_model()
# model.load()

client = BotClient(None, 1, None)
client.controller.screenshot()
    
#client.giveTask('go', ['lumbridge_north_farm'])
#client.giveTask('go',['1234','5678'])
#client.giveTask('farm_common_trees')
#client.executeAction('navigate lumbridge_north_farm')
# client.executeAction('open map')
# sleep(1)
# client.executeAction('open overview')
# sleep(4)
# client.executeAction('close map')
# client.giveTask('farm_common_trees')
# client.startTask()

# with mss.mss() as sct:
#         centerx=client.controller.centerx
#         centery=client.controller.centery
#         region={}
#         region['top']=centery-25
#         region['left']=centerx-25
#         region['width']=50
#         region['height']=50

#         me = float('-inf')
#         while True:
#                 t0 = time.time()
                
#                 s0 = sct.grab(region)
#                 sleep(0.25)
#                 s1 = sct.grab(region)

#                 e = mse(np.array(s0),np.array(s1))

#                 me = e if e > me else me

#                 print('e:',e,'me:',me,'t:',time.time()-t0,end='\r')

#                 #ss = im.frombytes("RGB", ss.size, ss.bgra, "raw", "BGRX")
#                 #ss.save('test2.png')
#                 sleep(1)



## LEFT OFF HERE
# use pyauto.screenshot difference and check difference after a tree is cut 
# this way has promise but need to find away to accurately screenshot the exact object or it won't work
# there are too many other variables that can affect the screenshot error

# # if 315 < obj['angle'] or obj['angle'] < 45:
# #     #going to approach object from left
# #     region['top'] = centery-obj['height']
# #     region['left'] = centerx

# # elif 45 < obj['angle'] and obj['angle'] < 135:
# #     #going to approach object from bottom
# #     region['top'] = centery-1.5*obj['height']
# #     region['left'] =centerx-obj['width']

# # elif 135 < obj['angle'] and obj['angle'] < 225:
# #     #going to approach object from right
# #    region['top'] = centery-obj['height']
# #    region['left'] =centerx-1.5*obj['width']

# # elif 225 < obj['angle'] and obj['angle'] < 315:
# #     #going to approach object from top
# #     region['top'] = centery
# #     region['left'] =centerx-obj['width']

# centerx = self.controller.centerx
# centery = self.controller.centery

# x1 = obj['centerx']-centerx
# y1 = obj['centery']-centery

# m = y1/x1
# b = centery - m*centerx

# xl = obj['left']
# yt = obj['top']
# xr = obj['right']
# yb = obj['bottom']

# yil = xl*m + b
# xit = (yt-b) / m
# yir = xr*m + b
# xib = (yb-b) / m



# points = [(xl,yil),(xit,yt),(xr,yir),(xib,yb)]
# pointsOnBox = []
# for p in points:
#     if xl <= p[0] and p[0] <= xr and yt <= p[1] and p[1] <= yb:
#         pointsOnBox.append(p)

# minDis = float('inf')
# minP = None
# for p in pointsOnBox:
#     dis = self.controller.dis(centerx,centery,p[0],p[1])
#     if(dis < minDis):
#         minDis = dis
#         minP = p

# xDif = obj['left']-minP[0]
# yDif = obj['top']-minP[1]            


# if  315 < obj['angle'] or obj['angle'] < 45:
#     #going to approach object from left-bottom tile
#     print('left-bottom')

# elif 45 < obj['angle'] and obj['angle'] < 90:
#     #going to approach object from bottom-left tile
#     print('bottom-left')
#     xDif += 37
#     yDif -= 12

# elif 90 < obj['angle'] and obj['angle'] < 135:
#     #going to approach object from bottom-right tile
#     print('bottom-right')
#     pass

# elif 135 < obj['angle'] and obj['angle'] < 180:
#     #going to approach object from right-bottom tile
#     print('right-bottom')
#     pass

# elif 180 < obj['angle'] and obj['angle'] < 225:
#     #going to approach object from right-top tile
#     pass

# elif 225 < obj['angle'] and obj['angle'] < 270:
#     #going to approach object from right
#     pass

# elif 240 < obj['angle'] and obj['angle'] < 300:
#     #going to approach object from top
#     pass

# elif 300 < obj['angle'] and obj['angle'] < 330:
#     #going to approach object from top-left
#     pass



# region = {}
# region['left'] = centerx + xDif
# region['top'] = centery + yDif
# region['width'] = obj['width']
# region['height'] = obj['height']

# for k in region.keys():
#     region[k] = int(region[k])

# print(obj)
# print(minP)
# print(xDif,yDif)
# print(region)



# # print(obj)
# # print(difVec[0], difVec[1])
# # print(region)

# with mss.mss() as sct:
#     ss=sct.grab(sct.monitors[1])
#     im = Image.frombytes("RGB", ss.size, ss.bgra, "raw", "BGRX")
#     im.save('im.png')

#     ss=sct.grab(region)
#     im = Image.frombytes("RGB", ss.size, ss.bgra, "raw", "BGRX")
#     im.save('imr.png')

#     maxErr = float('-inf')
#     while(True):
#         t0 = time.time()
#         ss1 = sct.grab(region)
#         sleep(0.1)
#         ss2 = sct.grab(region)

#         err = self.controller.mse(np.array(ss1),np.array(ss2))
#         maxErr = err if err > maxErr else maxErr
#         print('e:',err,'me:',maxErr,'t:',time.time()-t0, end='\r')
#         if maxErr > 200:
#             break

# with mss.mss() as sct:
#     client.executeAction('see')
#     print(client.objects)
#     centerx = client.controller.centerx
#     centery = client.controller.centery
#     #left
#     region = {
#         'top':centery-client.objects[1]['height'],
#         'left':centerx,
#         'width':2*client.objects[1]['width'],
#         'height':2*client.objects[1]['height']
#     } 
#     print(region)
#     input()
   
#     while(True):
#         t0 = time.time()
#         ss1 = sct.grab(sct.monitors[1])
#         input()
#         ss2 = sct.grab(sct.monitors[1])

#         err = mse(np.array(ss1),np.array(ss2))
#         print('e:',err,'t:',time.time()-t0, end='\r')
#         sleep(1)
##
## Attempt 2
##
# # assume we will walk up next to object so check for it based on the players location
# # try to predict the coordinates of where the object will be after bot walks to it
# # resolves problem of first attempt by not requiring another click

# xoffset = 0
# yoffset = 0

# offesetFac=.8

# #based on angle to object adjust offset on where to find object 
# if 315 < obj['angle'] or obj['angle'] < 45:
#     #going to approach object from left
#     xoffset = obj['width']*offesetFac

# elif 45 < obj['angle'] and obj['angle'] < 135:
#     #going to approach object from bottom
#     yoffset = -obj['height']*offesetFac

# elif 135 < obj['angle'] and obj['angle'] < 225:
#     #going to approach object from right
#     xoffset = -obj['width']*offesetFac

# elif 225 < obj['angle'] and obj['angle'] < 315:
#     #going to approach object from top
#     yoffset = obj['height']*offesetFac

######################
## Debugging prints ##
######################
# print(obj)
# print('Angle:', obj['angle'])
# print('xOffset:',xoffset,'yOffset:',yoffset)
# print('NewX:',(1280-36)//2 + xoffset,'NewY:',720//2 + yoffset)

#while object is there chill until it's farmed then look again and repeat
# while True:
#     self.executeAction('see')

#     if(not self.controller.objectIsAtCoord((1280-36)//2 + xoffset, 720//2 + yoffset, param[0], self.objects)):
#         break
#     sleep(3)

##############
#first attempt # not deleting yet incase second attempt doesn't work with other objects
##############
#after moving to object from first click look again and refind object
#click object again resetting its coordinates before the farm loop starts
#problem: sometimes it disappears since looking again takes a lot of time and it has already been farmed
#this leads the bot to clicking again when it shouldn't wasting some time
#results are good though, as the bot doesn't get 'locked up' since the second click just moves the bot 
#then the loop continues and it finds another tree

#look again to reset coordinates of object
# self.executeAction('see')

#reclick object 
# self.lastClickX, self.lastClickY = self.controller.clickObject(param[0], self.objects)

# while True:
#     self.executeAction('see')
#     if(not self.controller.objectIsAtCoord(self.lastClickX, self.lastClickY, param[0], self.objects)):
#         break



######################
# Testing Navigation #
######################

# subprocess.call(['clear'])

# navi = Navigator(Controller(1,None), 1280, 720)
# #navi.printLocation()
# navi.macroNavigate(place='lumbridge_north_farm')

#navi.macroNavigate(5846, 2025)

# ###########################
# # Rough code for location #
# ###########################

# ############
# # IMPORTANT: for faster/more updated code look at navigator.py locate function
# ############
# #map always opens in top left of game screen to chat window in height 
# #width constant 10 pixels away from minimap so calculated based on that

# subprocess.call(['rm', 'map.png', 'map1.png', 'map2.png', 'saved.png'])

# #fullmap sceenshot
# fullScreenShot = pyautogui.screenshot('map.png')


# #this could all be initialized on bot startup
# vertRes = 720
# horzRes = 1280

# #bigmap screenshot
# left = 6
# top = 29
# #verticalResolution - chatboxHeight (165) - bottomBorderThickness (45) - taskbarHeight (26) - topWindowHeight (29)
# height = vertRes - 165 - 45 - 26 - 29
# #horizontalResolution - constant (263) pixels of gui stuff
# width = horzRes - 263 
# bigMapShot = pyautogui.screenshot('map1.png', region=(left,top,width,height))

# #overview screenshot
# #get these numbers by resolution
# overviewWidth = 196
# overviewHeight = 112
# #width of big map + leftBorder (6) + 1 since overview starts one pixel in - overviewWidth (196) - overviewBorder (2) 
# left = width + 6 + 1 - 196 - 2 
# #height of big map - overviewHeight (112) + topWindowHeight(29) - overviewBorder(1)
# top = height - 112 + 29 - 1

# overviewShot = pyautogui.screenshot('map2.png', region=(left,top,overviewWidth,overviewHeight))

# im_width = overviewShot.width
# im_height = overviewShot.height

# pixelList = []
# for y in range(im_height):
#     for x in range(im_width):
#         # if (y == 48) and (122 < x and x < 148):
#         #     print(overviewShot.getpixel((x,y)))
#         pixel = overviewShot.getpixel((x,y))
        
#         if(pixel[0]>190 and pixel[1] < 100 and pixel[2] < 100):
#             pixelList.append((x,y))

# # for pixel in pixelList:
# #     overviewShot.putpixel(pixel, (0,0,255))


# left = pixelList[0][0]
# top = pixelList[0][1]

# bottom = top + 10-1
# right = left + 24-1

# overviewShot.putpixel((left,top), (0,0,255))
# overviewShot.putpixel((right,bottom), (0,0,255))

# #this is the box
# overviewShot.save('saved.png')
# print(left,top,' ',right,bottom)




# worldmap = im.open('worldmap.png')
# bigMapShot = cv2.imread('map1.png')
# worldmap = cv2.imread('worldmap.png')

# # result = cv2.matchTemplate(worldmap, bigMapShot, cv2.TM_SQDIFF)

# # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# # top_left = min_loc
# # bot_right = (top_left[0] + len(bigMapShot[0]), top_left[1] + len(bigMapShot))

# # print(top_left)
# # print(bot_right)

# worldmapWidth = len(worldmap[0])
# worldmapHeight = len(worldmap)

# widthScaler = worldmapWidth / overviewWidth
# heightScaler = worldmapHeight / overviewHeight

# bigLeftOffset = int(round(left * widthScaler - 2*left,0))
# bigTopOffset = int(round(top * heightScaler - 2*top,0))

# bigRightOffset  = int(round(right * widthScaler + 2*right,0))
# bigBottomOffset = int(round(bottom * heightScaler + 4*bottom,0))

# worldmap = worldmap[bigTopOffset:bigBottomOffset, bigLeftOffset:bigRightOffset]

# cv2.imwrite('subworldmap.png',worldmap)

# #print(bigLeftOffset, bigTopOffset, bigRightOffset, bigBottomOffset)

# result = cv2.matchTemplate(worldmap, bigMapShot, cv2.TM_SQDIFF)

# min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# top_left = min_loc
# top_left = (top_left[0]+bigLeftOffset, top_left[1]+bigTopOffset)
# bot_right = (top_left[0] + len(bigMapShot[0]), top_left[1] + len(bigMapShot))

# print('Rough Location:')
# print(top_left)
# print(bot_right)

# x = (top_left[0] + bot_right[0]) // 2
# y = (top_left[1] + bot_right[1]) // 2

# print('Precise Location')
# print('x:',x,'y:',y)





#take pic of bigmap and overview map

#process overview map to find rough location

#search worldmap only at rough location, for where bigmap fits in

#convert the matches coordiantes back into big map coordinates

#find center of that rectangle made my converted coordinates

#that is our raw x,y location


# def letterbox(img, new_shape=(416, 416), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
#     # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
#     shape = img.shape[:2]  # current shape [height, width]
#     if isinstance(new_shape, int):
#         new_shape = (new_shape, new_shape)

#     # Scale ratio (new / old)
#     r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
#     if not scaleup:  # only scale down, do not scale up (for better test mAP)
#         r = min(r, 1.0)

#     # Compute padding
#     ratio = r, r  # width, height ratios
#     new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
#     dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
#     if auto:  # minimum rectangle
#         dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
#     elif scaleFill:  # stretch
#         dw, dh = 0.0, 0.0
#         new_unpad = new_shape
#         ratio = new_shape[0] / shape[1], new_shape[1] / shape[0]  # width, height ratios

#     dw /= 2  # divide padding into 2 sides
#     dh /= 2

#     if shape[::-1] != new_unpad:  # resize
#         img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
#     top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
#     left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
#     img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
#     return img, ratio, (dw, dh)

# rune_modell = rune_model(cfg='yolo/cfg/yolov3-spp.cfg', 
#                         names='yolo/data/custom/custom.names', 
#                         weights='yolo/weights/best.pt', 
#                         source='yolo/data/custom/test_images')

# ###############
# Testing model #

# rune_modell.load(rune_modell.opt)

# #Screenshot into im0,img, need path and 
# screenshot = pyautogui.screenshot()

# #screenshot.save('screenshot.png')
# img0 = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# # Padded resize
# img = letterbox(img0, new_shape=416)[0]

# # Convert
# img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
# img = np.ascontiguousarray(img)

# rune_modell.detect(img, img0, 0)

# # cv2.imshow("Screenshot", imutils.resize(screenshot, width=416))
# # cv2.waitKey(0)