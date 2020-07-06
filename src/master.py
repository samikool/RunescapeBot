import argparse
import threading
import botutils 

from botclient import BotClient
from time import sleep
from yolo.runemodel import rune_model


class Master:
    def __init__(self, numbots=None):

        if(numbots == None):
            raise ValueError('numbots must have a value >= 1')
        
        self.numbots = numbots
        self.bots = []
        self.model = rune_model()
        self.model.load(self.model.opt)
        sleep(5)
        
    def detect(self, img, img0):
        return self.model.detect(img, img0)
        
    def start(self):
        for i in range(self.numbots):
            #botutils.startBots(self.numbots)
            self.bots.append(BotClient(self, i))

        for i in range(self.numbots):
            client_thread = threading.Thread(target=self.bots[i].start)
            client_thread.start()

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('--numbots', type=int, required=True, help='specifies the number of bots to be started')
    opt = parser.parse_args()

    print("Starting:",opt.numbots)

    master = Master(numbots=opt.numbots)
    master.start()