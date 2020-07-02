

import sys
import os
import subprocess
from time import sleep

numBots = sys.argv[1]

def createDisplays(numDisplays):
    print('Creating '+ numDisplays + ' displays for the bots...')

    subprocess.call(['./createNewDisplay.sh', str(numBots)])
    
    print(numDisplays + ' displays created.')

def startVNC(displayNum):
    print('Starting VNC for '+ str(displayNum) +'...')

    subprocess.call(['./startVNC.sh', str(displayNum)])
    
    print('VNC for '+ str(displayNum) + ' created.')

def startClient(numBots):
    print('Starting ' + str(numBots) + ' clients')

    subprocess.call(['./startClient.sh', str(numBots)])

    print(str(numBots) + ' clients started' )

def startBots(numBots):
    createDisplays(numBots)
    startClient(numBots)

