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

from PIL import Image
import mss
import time

#Will handle all the task logic
class BotClient:
    def __init__(self, master, client_num, model):
        self.client_num = client_num
        self.master = master
        self.inTask = False
        self.messageQ = queue.Queue()
        self.objects = {}
        self.task={}
        self.allTasks= self.parseTasks()
        self.controller = Controller(client_num, model)

    def watchQ(self):
        while True:
            pass

    def sendMessage(self, message):
        self.messageQ.put(message)

    #function will parse task and ready it to be started
    #good for now might get weird with different arguments
    def giveTask(self, task_name, params:list=None):
        #key to replace #value to replace with
        def replaceInDict(d,key,value):
            for k in d:
                d[k] = d[k].replace(key,value)
                if(d[k]).endswith(' '):
                    d[k] = d[k][0:len(d[k])-1]

        task = self.allTasks[task_name]
        if task.get('required'):
            req = task.get('required').split(',')
            opt = task.get('optional').split(',') if task.get('optional') else None

            if len(req) > len(params):
                raise AssertionError('There are required parameters not present')
            for i,var in enumerate(req):
                replaceInDict(task,var,params[i])
            if opt:
                numLeft = len(params) - len(req)
                if(numLeft):
                    params = params[len(req):]
                    for i,var in enumerate(opt):
                        replaceInDict(task,var,params[i])
                else:
                    for i,var in enumerate(opt):
                        replaceInDict(task,var,'')
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

    #function will read tasks from cfg file
    def parseTasks(self):
        allTasks = dict()
        with open('tasks.cfg', 'r') as file: 
            lines = file.readlines()
            curTask = dict()
            reading=False
            for line in lines:
                line = line.strip('\n')
                if line.startswith('#'):
                    continue
                if line == '':
                    continue

                if line.startswith('['):
                    if reading:
                        allTasks[curTask['name']] = curTask
                        curTask = dict()
                    reading = not reading
                    continue
                    
                if reading:
                    key = line.split('=')[0]
                    value = line.split('=')[1]
                    curTask[key] = value           
        return allTasks
                    
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

            sleep(0.5)

            while(self.controller.farming()):
                print('farming...',end='\r')
                sleep(1)
            print('object farmed...')

        elif action == 'navigate':
            #[0] place to go to if [1] is None else rawX
            #[1] if set then rawY
            if(len(param)>1):
                #navigate to rawX rayW
                self.controller.navigate(int(param[0]),int(param[1]))
            else:
                self.controller.navigate(place=param[0])

        elif action == 'click':
            #[0] = object to click 
            #Save last click location
            self.lastClickX, self.lastClickY = self.controller.clickObject(param[1],self.objects)

        elif action == 'open' or action == 'close' or action == 'select':
            #[0] icon to select to open/close - should be name of object being opened ie inventory,map,etc..
            self.controller.clickIcon(param[0])

        elif action == 'move':
            #will lock bot until it stops moving
            while(self.controller.moving()):
                sleep(0.1)

#for now put any logic you want to use to control bots here
def main(num,model):
    client = BotClient(None, num, model)
    client.giveTask('farm_common_trees')
    client.startTask()