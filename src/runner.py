import os
import botclient
import subprocess
import multiprocessing as mp

from multiprocessing import Process
from multiprocessing.managers import BaseManager

from time import sleep
from yolo.runemodel import Rune_model

class MyManger(BaseManager):
    pass

if __name__ == '__main__':
    
    subprocess.call('clear')

    #define starting bot # this should match the dislay # you're using
    startBot = 1

    #define how many bots you want to start # must be at least 1
    numBots = 1

    mp.set_start_method('spawn')

    MyManger.register('model', Rune_model)
    
    manager = MyManger()
    manager.start()

    model = manager.model()
    model.load()

    bots = []

    for i in range(startBot,startBot+numBots):
        os.environ['DISPLAY']= ':'+str(i)
        process = Process(target=botclient.main, args=[i, model])
        bots.append(process)
        process.start()
        print('Bot:',i,'started')
        
    while(True):
        pass
        sleep(100)

    for bot in bots:
        bot.join()

    manager.shutdown()