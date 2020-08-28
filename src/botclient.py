import threading
import random
import queue
import subprocess
import os
import numpy as np
import utils

from logger import Logger
from controller import Controller
from time import sleep
from threading import local

from PIL import Image
import mss
import time

#Will handle all the task logic
class BotClient:
    def __init__(self, account, outQ, inQ, botnum, model, map_g, worldmap):
        self.outQ = outQ
        self.inQ = inQ
        self.botnum = botnum
        self.logger = Logger(botnum,printMsg=True)
        self.controller:Controller = Controller(botnum, self.logger, model, map_g, worldmap)
        self.account = account

        #Action Variables
        self.objects = dict()

        #start thread to watch queue for messages from master
        self.qThread = threading.Thread(target=self.watchQ, name='q')
        self.qThread.start()

    def watchQ(self):
        while True:
            msg = self.inQ.get()
            self.logger.log(str(self.botnum)+' got: '+str(msg))
            if(msg == 'task'):
                t = self.inQ.get()
                self.startTaskThread(t)

            elif(msg == 'group'):
                g = self.inQ.get()
                self.startTaskGroupThread(g)
            
            elif(msg == 'changelogin'):
                u = self.inQ.get()
                p = self.inQ.get()
                w = self.inQ.get()
                self.account = (u,p,w)                

            elif(msg == 'interrupt'):
                pass
            #for now there is not a good way to stop a task
            elif(msg == 'stop'):
                pass

    def sendMessage(self, message):
        self.outQ.put(message)

    #This is much cleaner and easier to follow, also will allow interruption and stopping
    #TODO: There still is probably a way to share all of this code though considering its almost identical
    #Maybe a tasker object could facilitate that better
    def startTaskThread(self, t:dict):
        self.taskThread = threading.Thread(target=self.startTask, args=[t])
        self.taskThread.start()

    def startTaskGroupThread(self, g:dict):
        self.taskGroupThread = threading.Thread(target=self.startTaskGroup, args=[g])
        self.taskGroupThread.start()

    def startTask(self, t:dict):
        d = local() #create data localized to thread
        d.done = self.getStopFunction(t['stop'], d)
        self.executeTask(t, d.done)
    
    def startTaskGroup(self, g:dict):
        d = local() #create data localized to thread
        d.done = self.getStopFunction(g['stop'], d)
        self.executeGroup(g, d.done)

    #TODO: TEST
    def executeGroup(self, g:dict, done):
        self.logger.log('executing preloop...')
        self.executeGroupLoop(g.get('preloop'))
        self.logger.log('done.')

        while(not done()):
            self.logger.log('executing loop...')
            self.executeGroupLoop(g.get('loop'))
            self.logger.log('done.')
        
        self.logger.log('executing post loop...')
        self.executeGroupLoop(g.get('postloop'))
        self.logger.log('done.')

    def executeTask(self, t:dict, done):
        self.logger.log('executing preloop...')
        self.executeTaskLoop(t.get('preloop'))
        self.logger.log('done.')

        while(not done()):
            self.logger.log('executing loop...')
            self.executeTaskLoop(t.get('loop'))
            self.logger.log('done.')
        
        self.logger.log('executing post loop...')
        self.executeTaskLoop(t.get('postloop'))
        self.logger.log('done.')

    def executeTaskLoop(self, l:list):
        if l is None: return
        for a in l: self.executeAction(a)

    def executeGroupLoop(self, l:list):
        if l is None: return
        for t in l: self.startTask(t)

    def interruptTaskLoopThread(self):
        pass

    def getStopFunction(self, s:str, d):
        def count(c:int=None):
            if not c:
                d.curC += 1
                self.logger.log('count check...' + str(d.curC == d.tgtC))
                return d.curC == d.tgtC
            d.curC = 0
            d.tgtC = c+1

        def timer(x):
            d.tt=0
            while(d.tt < x):
                t0=time.time()
                sleep(1)
                d.tt += time.time()-t0

        def cus_time(x=None):
            if not x: 
                self.logger.log('time check...')
                return not d.t.is_alive()

            d.t = threading.Thread(target=timer, args=[x])
            d.t.start()

        s = s.split(' ')
        if(s[0] == 'time'):
            self.logger.log('time init...')
            s[1] = int(s[1])
            cus_time(s[1])
            return cus_time

        if(s[0] == 'count'):
            self.logger.log('count init...')
            s[1] = int(s[1])
            count(s[1])
            return count
        
        #this one looks weird but is only for debugging
        if(s[0] == 'never'):
            def retTrue(): return True
            return retTrue

        if(s[0] == 'full'):
            return self.controller.inventoryFull
         
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
    return BotClient(account, outQ, inQ, botnum, model, map_g, worldmap)
    
    # sleep(5)
    
    # # t = utils.getTask('login_custom',['sam','sam','world418'])
    # t = utils.getTaskGroup('idle')
    # client.startTaskGroupThread(t)
    
    
    # while(True):
    #     sleep(3600)