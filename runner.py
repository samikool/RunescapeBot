import sys
import os
if(os.name == 'nt'):
    import win32.win32gui as win32gui
from time import sleep


print(os.name)

while(True):
    sleep(3)