import os
import cv2
import graph
import ctypes
import utils

import argparse
import threading
import botutils 
import queue
from time import sleep

import botclient
import subprocess
import multiprocessing as mp
import numpy as np

from multiprocessing import Process
from multiprocessing.managers import BaseManager

from time import sleep
from yolo.runemodel import Rune_model
from graph import MapGraph
from menu import Menu



class MyManger(BaseManager):
    pass

class Master:
    def __init__(self):
        #load master variables
        self.menu = Menu(self)

        #load shared data structures clients will use
        mp.set_start_method('spawn')

        MyManger.register('model',Rune_model)
        MyManger.register('graph',graph.MapGraph)
        
        #TODO: break into functions # start manager
        self.manager = MyManger()
        self.manager.start()

        #load rune model
        self.model = self.manager.model()
        self.model.load()

        #load master mapgraph
        self.map_g = self.manager.graph()
        self.map_g.load()

        #load worldmap image
        self.worldmap = cv2.imread('worldmap.png')
 
        #load tasks from cfg file
        self.tasks = utils.parseTasks()
        
        #create communication data structs
        self.inQ = mp.Queue()
        threading.Thread(target=self.watchQ).start()
        self.outputs = {}
        
        #dictionary will hold process object bots are being ran in
        self.bots = {}

    def watchQ(self):
        while True:
            msg = self.inQ.get()
            print('master got:',msg)
    
    #starts a bot i is integer number corresponding to display bot is run on
    #should start at 1
    def startBot(self,i):
        if(i == 1):
            raise ValueError('bots must start on display 2 or greater, 1 is reserved for the master')
        self.bots[i] = dict()

        dispPID,deskPID = utils.createDisplay(i)
        if dispPID == None or deskPID == None:
            print('failed to create display')
            return False

        print('display:', dispPID, deskPID)


        clientPID = utils.startClient(i)
        if clientPID == None:
            print('failed to start client')
            return False

        print('client:', clientPID)


        port,vncPID = utils.startVNC(i)
        if port == None or clientPID == None:
            print('failed to start VNC')
            return False

        print('vnc:', port, vncPID)
   

        os.environ['DISPLAY']= ':'+str(i)
        self.outputs[i] = mp.Queue()
        process = Process(
                    target=botclient.create, 
                    args=[self.inQ, self.outputs[i], i, self.model, self.map_g, self.worldmap, self.tasks],
                )

        
        #store needed info about bot
        self.bots[i]['process'] = process
        self.bots[i]['dispPID'] = dispPID
        self.bots[i]['deskPID'] = deskPID
        self.bots[i]['clientPID'] = clientPID
        self.bots[i]['vncPID'] = vncPID
        self.bots[i]['dispNum'] = i

        process.start()

        #pid of process not set until after spawn
        self.bots[i]['processPID'] = process.pid
        print('process:', process.pid)

    def stopTask(self, i):
        self.outputs[i].put('stop')

    def giveTask(self, i, taskName, taskParams=None):
        self.outputs[i].put('task')
        self.outputs[i].put(taskName)
        self.outputs[i].put(taskParams)

    def giveTaskLoop(self, i, taskList, stopCond='count 1'):
        self.outputs[i].put('taskLoop')
        for msg in taskList:
            self.outputs[i].put(msg)

    def getTask(self,i,name=None):
        if(name):
            return self.tasks[name]
        else:
            return list(self.tasks.values())[i]

    #function will start multiple bots starting at s display and ending at num-1 display
    def startBots(self,s,num):
        if(s == 1):
            raise ValueError('bots must start on display 2 or greater, 1 is reserved for the master')

        for i in range(s,s+num):
            self.startBot(i)

    def killBot(self, i):
        utils.killBot(self.bots[i])
        del self.bots[i]
        del self.outputs[i]

               
#any options for actually starting bots goes here
if __name__ == '__main__' :
    #parser = argparse.ArgumentParser()
    #parser.add_argument('--numbots', type=int, required=True, help='specifies the number of bots to be started')
    #opt = parser.parse_args()

    # print("Starting:",opt.numbots)          

    # master = Master(numbots=opt.numbots)
    # master.start()

    subprocess.call('clear')
    master = Master()
    master.startBots(2,1)

    sleep(2)

    menu = master.menu

    #for now just sleep not sure what to do here
    while(True):
        print()
        print(menu.getMenu(), end='')
        menu.getInput()

    for bot in bots:
        bot.join()

    manager.shutdown()