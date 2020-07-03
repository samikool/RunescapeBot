import argparse
import threading
import botutils 

from client import BotClient
from server import Server
from time import sleep
from yolo.runemodel import rune_model


class master:
    def __init__(self, numbots=None):

        if(numbots == None):
            raise ValueError('numbots must have a value >= 1')

        self.numbots = numbots
        self.server = Server('0.0.0.0', 4000)
        self.bots = []
        self.model = rune_model()
        self.model.load(self.model.opt)

    def start(self):
        server_thread = threading.Thread(target=self.server.start)
        for i in range(self.numbots):
            #botutils.startBots(self.numbots)
            self.bots.append(BotClient(i))

        server_thread.start()
        for i in range(self.numbots):
            client_thread = threading.Thread(target=self.bots[i].start)
            client_thread.start()

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('--numbots', type=int, required=True, help='specifies the number of bots to be started')
    opt = parser.parse_args()

    print(opt.numbots)

    master = master(numbots=opt.numbots)
    master.start()