import pyautogui
from time import sleep


client = {'sam': 2}
client1 = {'sam': 2}

print(client == client1)

while(True):
    print(pyautogui.position())
    sleep(2)