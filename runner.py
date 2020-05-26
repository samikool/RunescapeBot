import sys
import os
import subprocess
from time import sleep

numBots = sys.argv[1]

def killOldBots():
    print('Killing old bots')
    subprocess.call('killall X')
def createDisplays(numDisplays):
    print('Creating '+ numDisplays + ' displays for the bots...')

    subprocess.call(['./createNewDisplay.sh', str(numBots)])
    
    print(numDisplays + ' bots created.')

def startVNC(displayNum):
    print('Starting VNC for '+ str(displayNum) +'...')

    subprocess.call(['./startVNC.sh', str(displayNum)])
    
    print('VNC for '+ str(displayNum) + ' created.')


createDisplays(numBots)