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
        self.objects = {}



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

    def taskLoop(self):
        while self.inTask:
            for action in self.task['loop']:
                self.executeAction(action)

    def stopTask(self):
        self.inTask = False

    def parseTask(self, task_name):
        with open('tasks.cfg', 'r') as file:
            lines = file.readlines()
            print(lines)
            for i in range(len(lines)):
                print(lines[i])
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
                        task['loop'] = task['loop'].split(',')
                        return task
    #will call appropiate functions in controller/python libs to execute action
    def executeAction(self, action):
        actionList = action.split(' ')

        action = actionList[0]
        param = actionList[1:] if len(actionList) > 1 else None
        
        print(action)
        print(param)

        if action == 'see':
            self.objects = self.controller.getObjects()
            pass
        
        elif action == 'wait':
            #[0] = time
            sleep(int(param[0]))
            pass

        elif action == 'click':
            #[0] = object to click
            self.controller.clickObject(param[0],self.objects)
            pass


    def start(self):
        pass
        # self.initialize()
        # while True:
        #     img, img0 = self.controller.getScreencap()
        #     objects = self.master.detect(img, img0)

if __name__ == '__main__':
    client = BotClient(None, 1)
    client1 = BotClient(None, 1)
    client2 = BotClient(None, 1)

    print(client.giveTask('farm_common_trees'))
    client.startTask()