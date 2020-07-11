import threading
import random
import queue
import subprocess
import os
import numpy as np

from importlib import reload
import importlib
from controller import Controller
from time import sleep

#Will handle all the task logic
class BotClient:
    def __init__(self, master, client_num, model):
        self.client_num = client_num
        self.master = master
        self.inTask = False
        self.messageQ = queue.Queue()
        self.objects = {}
        self.task={}
        self.controller = Controller(client_num, model)

    def watchQ(self):
        while True:
            pass

    def sendMessage(self, message):
        self.messageQ.put(message)

    def giveTask(self, task_name):
        self.task = self.parseTask(task_name)
        return self.task

    def startTask(self):
        self.inTask = True
        self.taskLoop()

    def taskLoop(self):
        while self.inTask:
            for action in self.task['loop']:
                self.executeAction(action)

    def stopTask(self):
        self.inTask = False

    def parseTask(self, task_name):
        with open('tasks.cfg', 'r') as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if(lines[i].startswith('[')):
                    task = {}
                    while(True):
                        i+=1

                        if(lines[i].startswith('[')):
                            break

                        key = lines[i].split('=')[0].strip('\r\n')
                        value = lines[i].split('=')[1].strip('\r\n')
                        task[key] = value
                    
                    if(task['name'] == task_name):
                        task['loop'] = task['loop'].split(',')
                        print(task)
                        return task

    #will call appropiate functions in controller/python libs to execute action
    def executeAction(self, action):
        actionList = action.split(' ')

        action = actionList[0]
        param = actionList[1:] if len(actionList) > 1 else None
        
        print('Action:', action,'Params:',param)

        if action == 'see':
            self.objects = self.controller.getObjects()
        
        elif action == 'wait':
            #[0] = time
            sleep(int(param[0]))    

        elif action == 'farm':
            #[0] = object to farm

            #click on object to move there
            self.lastClickX, self.lastClickY, obj = self.controller.clickObject(param[0], self.objects)

            # #this sleep is to account for ping TODO: find a more consistant way to account for ping
            sleep(0.75)
            
            #lock bot until it stops moving
            self.executeAction('move')

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

            ################
            ##second attempt
            ################
            # assume we will walk up next to object so check for it based on the players location
            # try to predict the coordinates of where the object will be after bot walks to it
            # resolves problem of first attempt by not requiring another click or another 'look'

            xoffset = 0
            yoffset = 0

            offesetFac=.8

            #based on angle to object adjust offset on where to find object 
            if 315 < obj['angle'] and obj['angle'] < 45:
                #going to approach object from left
                xoffset = obj['width']*offesetFac

            elif 45 < obj['angle'] and obj['angle'] < 135:
                #going to approach object from bottom
                yoffset = -obj['height']*offesetFac

            elif 135 < obj['angle'] and obj['angle'] < 225:
                #going to approach object from right
                xoffset = -obj['width']*offesetFac

            elif 225 < obj['angle'] and obj['angle'] < 315:
                #going to approach object from top
                yoffset = obj['height']*offesetFac

            ######################
            ## Debugging prints ##
            ######################
            # print(obj)
            # print('Angle:', obj['angle'])
            # print('xOffset:',xoffset,'yOffset:',yoffset)
            # print('NewX:',(1280-36)//2 + xoffset,'NewY:',720//2 + yoffset)

            #while object is there chill until it's farmed then look again and repeat
            while True:
                self.executeAction('see')
                
                if(not self.controller.objectIsAtCoord((1280-36)//2 + xoffset, 720//2 + yoffset, param[0], self.objects)):
                    break
                sleep(3)

            #################
            # Third attempt #
            #################
            # use pyauto.screenshot difference and check difference after a tree is cut 
            # only screenshot around character and object and when it breaks threshhold object must be gone
            # problem: could be thrown off by other players or farmers
            # problem: might be hard to figure out exactly what area to screenshot - but could use angle then height and width to roughly encapsolate it 
            # if it took up a fairly constant % of the screen the results would be good
            
            #steps - figureout how to calculate screenshot height and width and 'offset' depending on angle im approaching it from 
            # maybe just have a big box around me in every direction, that is sort of based on object height-width? 

            # test with two accounts figure out threshold for player walking in 'my box' vs tree vs player farming another tree nearby

            # if it looks like theres a pretty consistant threshold make endless while in controller that given an obj will only break when the object disappears
            
            #boom - fastest and possible even more accurate than second idea, which still relies on the nueral network to reget objects 

        elif action == 'click':
            #[0] = object to click 
            #Save last click location
            self.lastClickX, self.lastClickY = self.controller.clickObject(param[0],self.objects)
        
        elif action == 'move':
            #will lock bot until it stops moving
            while(self.controller.moving()):
                sleep(0.1)

#for now put any logic you want to use to control bots here
def main(num,model):
    client = BotClient(None, num, model)
    client.giveTask('farm_common_trees')
    client.startTask()