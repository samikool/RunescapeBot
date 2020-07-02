import argparse
import threading

from botstarter import start
from server import MasterServer
from time import sleep



class master:
    server = server('0.0.0.0', 4000)
    bots=[]
    def __init__(self, numbots):
        pass
    def start(self):
        self.server.start()
        
        
if(__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument('--numbots', type=int, default=1, help='specifies the number of bots to be started')
    opt = parser.parse_args()

    master = master(numbots=opt.numbots)
    master.start()