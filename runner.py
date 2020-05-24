import sys
from time import sleep
import win32.win32gui as win32gui

print(sys.path)

while(True):
    print(win32gui.GetForegroundWindow())
    sleep(3)