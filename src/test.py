#import pyautogui
import PIL.Image as im
import os
import cv2
import numpy as np
import imutils
from yolo.runemodel import Rune_model
from time import sleep
import subprocess

from navigator import Navigator
from controller import Controller
#########################################
# This file is for any random test code #
#########################################

############################
# Testing Micro Navigation #
############################

subprocess.call(['clear'])

navi = Navigator(Controller(1,None), 1280, 720)

#navi.printLocation()
navi.microNavigate(5440, 2147)



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