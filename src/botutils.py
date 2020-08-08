import sys
import os
import subprocess
from time import sleep

def createDisplays(numBots):
    print('Creating ',numBots,' displays for the bots...')
    subprocess.call(['./createNewDisplay.sh', str(numBots)])
    print(numBots+ ' displays created.')

def startVNCs(numBots):
    print('Starting VNC for ',numBots,+'...')
    subprocess.call(['./startVNC.sh', str(numBots)])
    print('VNC for ',numBots+' created.')

def startClients(numBots): 
    print('Starting ',numBots,' clients')
    subprocess.call(['./startClient.sh', str(numBots)])
    print(numBots,' clients started' )

#more like create enviorments for bots
def startBots(self, numBots, create_displays=True, start_vnc=False, start_clients=True):
    if(create_displays):
        createDisplays(numBots)

    if(start_vnc):
        startVNCs(numBots)

    if(start_clients):
        startClients(numBots)