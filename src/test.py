import pyautogui
import os
import cv2
import numpy as np
import imutils
from yolo.runemodel import Rune_model
from time import sleep

######################
# Testing navigation #
######################

#map always opens in top left of game screen to chat window in height 
#width constant 10 pixels away from minimap so calculated based on that

#fullmap sceenshot
pyautogui.screenshot('map.png')

vertRes = 720
horzRes = 1280


#bigmap screenshot
left = 6
top = 29
#verticalResolution - chatboxHeight (165) - bottomBorderThickness (45) - taskbarHeight (26) - topWindowHeight (29)
height = vertRes - 165 - 45 - 26 - 29
#horizontalResolution - constant (263) pixels of gui stuff
width = horzRes - 263 
pyautogui.screenshot('map1.png', region=(left,top,width,height))

#overview screenshot
#get these numbers by resolution
overviewWidth = 196
overviewHeight = 112
#width of big map + leftBorder (6) + 1 since overview starts one pixel in - overviewWidth (196) - overviewBorder (2) 
left = width + 6 + 1 - 196 - 2 
#height of big map - overviewHeight (112) + topWindowHeight(29) - overviewBorder(1)
top = height - 112 + 29 - 1

pyautogui.screenshot('map2.png', region=(left, top, overviewWidth, overviewHeight))



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
# ###############
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




