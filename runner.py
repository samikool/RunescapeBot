import sys
import os
if(os.name == 'nt'):
    import win32.win32gui as screen
elif(os.name == 'posix'):
    import wnck


from time import sleep


print(os.name)

while(True):
    sleep(3)