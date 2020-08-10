import threading
import random
import queue
import subprocess
import os
import numpy as np

from logger import Logger
from controller import Controller
from time import sleep

from PIL import Image
import mss
import time

#Will handle all the task logic
class BotClient:
    def __init__(self, account, outQ, inQ, botnum, model, map_g, worldmap):
        self.outQ = outQ
        self.inQ = inQ
        self.botnum = botnum
        self.logger = Logger(botnum)
        self.controller = Controller(botnum, self.logger, model, map_g, worldmap)
        self.account = account

        self.inTask = False
        self.objects = dict()
        self.curTask = dict()

        #start thread to watch queue for messages from master
        if botnum != 1:
            self.qThread = threading.Thread(target=self.watchQ, name='q')
            self.qThread.start()

    def watchQ(self):
        while True:
            msg = self.inQ.get()
            self.logger.log(str(self.botnum)+' got: '+str(msg))
            if(msg == 'task'):
                taskName = self.inQ.get()
                params = self.inQ.get()
                task = self.cleanTask(taskName, params)

                self.giveTask(task)
                self.taskThread = threading.Thread(target=self.startTask, name='task')
                self.taskThread.start()
            elif(msg == 'taskLoop'):
                loop = self.inQ.get()

                self.taskThread = threading.Thread(target=self.startTaskLoop, args=[loop], name='task')
                self.taskThread.start()
            #for now there is not a good way to stop a task
            elif(msg == 'stop'):
                self.inTask = False
                while self.taskThread.isAlive:
                    sleep(1)
    def sendMessage(self, message):
        self.outQ.put(message)

    # TODO: this should probably be a util or tasks should be broken in an object
    def cleanTask(self, task_name, params:list=None):
        #key to replace #value to replace with
        def replaceInDict(d,key,value):
            for k in d:
                d[k] = d[k].replace(key,value)
                while d[k].endswith(' '):
                    d[k] = d[k][:-1]

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
                replaceInDict(task,' ,',',')
        return task

    #sets curTask to task passed in, this task should already be fully 'cleaned'
    def giveTask(self, task):
        self.curTask = task

    def startTask(self):
        self.inTask = True
        self.taskLoop()
    
    def startTaskLoop(self, loop):
        #mean main loop stops on time limit
        if loop['stop'].startswith('time'):

            for t in loop['preloop']:
                self.logger.log('executing preloop...')
                self.giveTask(t)
                self.startTask()
            self.logger.log('done.')
            
            #split time and make it int execute main loop for that amount of time
            
            self.logger.log('executing loop...')
            t0 = time.time()
            tf = float(loop['stop'].split(' ')[1])*60

            i=0
            while time.time()-t0 < tf:
                self.logger.log('iter:'+str(i))
                for t in loop['loop']:
                    self.giveTask(t)
                    self.startTask()
                i += 1
            self.logger.log('done.')

            self.logger.log('executing postloop')
            for t in loop['postloop']:
                self.giveTask(t)
                self.startTask()
            self.logger.log('done.')
            self.logger.log('task finished.')

        elif loop['stop'].startswith('count'):

            for t in loop['preloop']:
                self.logger.log('executing preloop...')
                self.giveTask(t)
                self.startTask()
            self.logger.log('done.')
            
            #split time and make it int execute main loop for that amount of time
            c = loop['stop'].split(' ')[1]
            c = int(c)
            
            self.logger.log('executing loop...')
            for i in range(c):
                self.logger.log('iter:'+str(i))
                for t in loop['loop']:
                    self.giveTask(t)
                    self.startTask()
                i += 1
            self.logger.log('done.')

            self.logger.log('executing postloop')
            for t in loop['postloop']:
                self.giveTask(t)
                self.startTask()
            self.logger.log('done.')
            self.logger.log('task finished.')

    def stopTask(self, t=None):
        if t:
            sleep(t)
        self.logger.log('stop task')
        self.inTask = False

    def taskLoop(self):
        #convert loop to list # need to do here to account for params
        if type(self.curTask['loop']) != list:
            self.curTask['preloop'] = self.curTask['preloop'].split(',') if self.curTask.get('preloop') else None 
            self.curTask['loop'] = self.curTask['loop'].split(',')
            self.curTask['postloop'] = self.curTask['postloop'].split(',') if self.curTask.get('postloop') else None 

        if(self.curTask['preloop']):
            self.logger.log('executing preloop...')
            for action in self.curTask['preloop']:
                self.executeAction(action)
            self.logger.log('done.')
        self.logger.log('executing loop...')
        if self.curTask['stop'].startswith('count'):
            c = int(self.curTask['stop'].split(' ')[1])
            for i in range(c):
                for action in self.curTask['loop']:
                    self.executeAction(action)
        
        elif self.curTask['stop'] == 'full':
            while not self.controller.inventoryFull():
                for action in self.curTask['loop']:
                    self.executeAction(action)

        elif self.curTask['stop'] == 'never':
            while self.inTask:
                for action in self.curTask['loop']:
                    self.executeAction(action)

        self.logger.log('done.')
        if(self.curTask['postloop']):
            self.logger.log('executing postloop')
            for action in self.curTask['postloop']:
                self.executeAction(action)   
            self.logger.log('done.') 
        
        self.logger.log('task finished.')
         
    #will call appropiate functions in controller/python libs to execute action
    def executeAction(self, action):
        actionList = action.split(' ')

        action = actionList[0]
        param = actionList[1:] if len(actionList) > 1 else None
        
        self.logger.log('Action: '+str(action)+' Params: '+str(param))

        if action == 'see':
            self.objects = self.controller.getObjects()
            self.logger.log(str(len(self.objects))+' objects detected...')
        
        elif action == 'wait':
            #[0] = time
            sleep(float(param[0]))    

        elif action == 'farm':
            #[0] = object to farm

            #click on object to move there
            self.lastClickX, self.lastClickY, obj = self.controller.clickObject(param[0],self.objects)

            # #this sleep is to account for ping TODO: find a more consistant way to account for ping
            sleep(1)
            
            #lock bot until it stops moving
            self.executeAction('move')

            sleep(0.75)

            while(self.controller.farming()):
                self.logger.log('farming...\r')
                sleep(1)
            self.logger.log('object farmed.')

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
            self.lastClickX, self.lastClickY, obj = self.controller.clickObject(param[0],self.objects)

        elif action == 'open' or action == 'close' or action == 'select':
            #[0] icon to select to open/close/select - should be name of object being opened ie inventory,map,etc..
            #[1] will be confidence if specified else a default .80 set in controller will be used
            conf = float(param[1]) if len(param) > 1 else 0.8
            self.controller.clickIcon(param[0], conf)
        elif action =='dropoff':
            #[0] is the item to dropoff at deposit box
            #[1] is the count 
            c = param[1]
            if c == 'all':
                self.executeAction('select all .95')
                sleep(0.25)
                # self.executeAction('select '+param[0])
                # sleep(0.2)
                while self.controller.findIcon(param[0]) != None:
                    self.executeAction('select '+param[0])
                    sleep(0.25)
            else:
                for i in range(int(c)):
                    self.executeAction('select '+param[0])
                    sleep(0.1)

            self.executeAction('select close_deposit')

        elif action == 'move':
            #will lock bot until it stops moving
            while(self.controller.moving()):
                sleep(0.1)
        elif action == 'hold':
            #[0]is key to hold
            #[1]is how long to hold
            self.controller.hold(param[0],float(param[1]))

        elif action == 'type':
            #[0] is the string to type
            #box to type in should already be selected
            self.controller.type(param[0])
        elif action == 'press':
            keys = param[0].split('+') if len(param[0].split('+')) > 1 else None
            if(keys):
                self.controller.pressMultiple(keys)
            else:
                self.controller.press(param[0])
        #login is a special action that is defined in code instead of as a task 
        elif action == 'login':
            self.executeAction('select world 0.5')
            self.executeAction('wait 0.25')
            self.executeAction('select '+self.account[2]+' .96')
            self.executeAction('select existinguser')
            self.executeAction('wait 0.25')
            self.executeAction('press shift+tab')
            self.executeAction('hold backspace 5')
            self.executeAction('type '+self.account[0])
            self.executeAction('press tab')
            self.executeAction('type '+self.account[1])
            self.executeAction('wait 0.25')
            self.executeAction('press enter')
            self.executeAction('wait 15')
            self.executeAction('select clicktoplay')
            self.executeAction('wait 3')
            self.executeAction('hold up 5')

#static funciton will create a botclient and start it
def create(account, outQ, inQ, botnum, model, map_g, worldmap):
    client = BotClient(account, outQ, inQ, botnum, model, map_g, worldmap)
    
    sleep(15)
    client.startTaskLoop(client.taskLoops['idle'])

    # t = client.cleanTask('goto', ['fal_top'])
    # t = client.cleanTask('farm_object',['oak_tree'])
    # t = client.cleanTask('goto',['port_sarim_dropoff'])
    # t = client.cleanTask('goto',['fal_south_tree_junction'])
    # t = client.cleanTask('dropoff_object',['logs', 'all'])
    # t = client.cleanTask('farm_object',['common_tree'])

    # t = client.cleanTask('idle', ['3600'])
    # client.giveTask(t)
    # client.startTask()

    while(True):
        sleep(3600)