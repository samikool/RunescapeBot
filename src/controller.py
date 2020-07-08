import pyautogui
import cv2
import numpy as np
import imutils
import random

from math import sqrt
from yolo.runemodel import Rune_model

#class will handle all interaction with the GUI
class Controller:
    model = Rune_model()
    #pixel is roughly center of screen
    centerx=1280//2
    centery=720//2
    
    def __init__(self):
        self.model.load(self.model.opt)
        pass
    
    #clicks in random location in box and returns values of where mouse clicked
    def clickBox(self,top,left,bottom,right):
        #padding is applied to every side of box to ensure we click the object
        padding = 20

        clickx = random.randint(left+20, right-20)
        clicky = random.randint(top+20, bottom-20)

        duration = random.uniform(.25, 1)
        
        pyautogui.moveTo(clickx, clicky, duration)
        pyautogui.click()
        
        return clickx, clicky

    ##object is string name of object to click on
    ##objects is map of objects returned from detect
    ##Function will parse objects and click closest one
    ##Return x and y location of where pointer clicked
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

        clickx,clicky = self.clickBox(minObj['top'], minObj['left'], minObj['bottom'], minObj['right'])
        return clickx,clicky

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
    
    def getObjects(self):
        screenshot = pyautogui.screenshot()

        #screenshot.save('screenshot.png')
        img0 = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Padded resize
        img = self.letterbox(img0, new_shape=416)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        return self.model.detect(img, img0)

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