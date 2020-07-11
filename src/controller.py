import importlib
import os
import random

import copy
import cv2
import numpy as np
import imutils
import pyautogui

from time import sleep
from math import sqrt
from yolo.runemodel import Rune_model


#class will handle all interaction with the GUI
class Controller:
    # model = Rune_model()
    #pixel is roughly center of screen
    centerx=(1280-36)//2
    centery=720//2
    modelLoaded = False
    
    def __init__(self, display, model):
        Controller.model = model
        self.display=display

    def mouseLoop(self, num):
        while(True):
            print(str(num)+': '+str(pyautogui.position()))
            sleep(2)
    

    def screenshot(self, im_name='image.png'):
        pyautogui.screenshot(im_name)

    def findIcon(self, im_name=None):
        path = os.path.join(os.path.abspath(os.path.curdir), 'icons/'+str(im_name)+'.png')
        
        icon = pyautogui.locateOnScreen(path,confidence=.80)
        box = self.convertIconToBox(icon)

        return box
        
    def findAllIcons(self, im_name=None):
        path = os.path.join(os.path.abspath(os.path.curdir), 'icons/'+str(im_name)+'.png')

        iconList = list(pyautogui.locateAllOnScreen(path, confidence=.80))

        boxList = []
        for icon in iconList:
            boxList.append(self.convertIconToBox(icon))

        return boxList

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

    def clickIcon(self, icon=None):
        box = self.findIcon(icon)
        self.clickBox(box)
        

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
        im_one = np.array(pyautogui.screenshot())
        im_two = np.array(pyautogui.screenshot())
        
        error = self.mse(im_one, im_two)
        moving = True if error > thresh else False

        if(print):
            print('error:',error)
            print('moving:',moving)

        return moving

    #clicks in random location in box and returns values of where mouse clicked
    def clickBox(self,box):
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

        clickx,clicky = self.clickBox(minObj)
        minObj['angle'] = self.calcObjAngle(minObj)
        return clickx,clicky,minObj

    ##Function calulates angle between player and object
    def calcObjAngle(self, obj):
        #calc angle 
        vec1 = [1,0]
        vec2 = [obj['centerx'] - (1280-36)//2, obj['centery'] - 720//2]

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