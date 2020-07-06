import threading
import random
import queue

from controller import Controller
from time import sleep

#Will handle all the task logic
class BotClient:
    controller = Controller()

    def __init__(self, master, client_num):
        self.client_num = client_num
        self.master = master
        self.inTask = False
        self.messageQ = queue.Queue()

    def watchQ(self):
        while True:
            pass

    def sendMessage(self, message):
        self.messageQ.put(message)

    def giveTask(self, task_name):
        self.task = self.parseTask(task_name)
        print(self.task)

    def startTask(self):
        self.inTask = True
        self.taskLoop()

    def taskLoop(self, task):
        while self.inTask:
            pass

    def stopTask(self):
        self.inTask = False

    def parseTask(self, task_name):
        with open('tasks.cfg', 'r') as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if(lines[i].startswith('[')):
                    task = {}
                    while(True):
                        i+=1

                        if(lines[i].startswith('[')):
                            break

                        key = lines[i].split('=')[0].strip('\r\n')
                        value = lines[i].split('=')[1].strip('\r\n')
                        task[key] = value
                    
                    if(task['name'] == task_name):
                        return task

    def start(self):
        pass
        # self.initialize()
        # while True:
        #     img, img0 = self.controller.getScreencap()
        #     objects = self.master.detect(img, img0)

if __name__ == '__main__':
    client = BotClient(None, 1)
    print(client.giveTask('farm_trees'))