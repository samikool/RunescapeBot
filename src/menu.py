class Menu():
    def __init__(self, master):
        self.state = '0'
        self.prevMenu = ''
        self.master = master

    #function will call processState() which will handle interacting with the user in the necessary way
    #then will strictly update the menu the user can interact with after its been handled
    def getMenu(self):

        #debugging s
        s = 'state:'+self.state+'\n'
        #s = ''
        
        #0 is main menu
        if self.state == '0':
            s += '1. List Online Bots\n'
            s += '2. List Tasks\n'
            s += '3. Start Bot\n'
            s += '4. Kill Bot\n'
            s += '5. Give Bot Tasks\n'
            s += '6. Stop Bot\'s Task\n'
        #01 is list bots
        elif self.state == '01':
            self.listBots()
            input('press enter to go back')
            s = self.goBack()
        #02 is list tasks
        elif self.state == '02':
            self.listTasks()
            input('press enter to go back')
            s = self.goBack()
        #03 is start bot
        elif self.state == '03':
            self.startBot()
            input('press enter to go back')
            s = self.goBack()
        #04 is kill bot
        elif self.state == '04':
            self.killBot()
            s = self.goBack()
        #05 is give bot task
        elif self.state == '05':
            self.giveTask()
            s = self.goBack()

        elif self.state == '06':
            self.stopTask()
            s = self.goBack()

        self.prevMenu = s
        return s

    def getInput(self):
        i = input('Select an option: ')
        self.state += i
    
    def goBack(self):
        self.state = self.state[:-1]
        return self.prevMenu

    def listBots(self):
        #01 is list bots
        for k in self.master.bots:
            print('Bot:'+str(k))

    def listTasks(self):
        #02 is list tasks
        i=1
        for t in self.master.tasks:
            print(str(i)+'. ' + str(t))
            i+=1

    def startBot(self):
        pass

    def killBot(self):
        while(True):
            self.listBots()
            i = input('Enter nothing to go back\nSelect Bot# to kill:')
            if i == '':
                break
            i = int(i)
            if i in self.master.bots:
                self.master.killBot(i)
                print('bot',i,'killed\n')
    def stopTask(self):
        self.listBots()
        i = input('Enter nothing to go back\nSelect Bot# to stop its current task:')
        if i == '':
            return
        i = int(i)
        if i in self.master.bots:
            self.master.stopTask(i)


    def giveTask(self):
        while(True):
            self.listBots()
            i = input('Enter nothing to go back\nSelect Bot# to Give Task:')
            if i == '':
                break
            bot = int(i)

            if bot in self.master.bots:
                i = input('Enter nothing to go back\n1. Give Bot Single Task\n2. Give Bot Task Loop\nSelect an option:')
                if i == '':
                    break
                i = int(i)
                
                if(i==1):
                    self.listTasks()
                    i = input('Enter nothing to go back\nSelect a task:')
                    if i == '':
                        break
                    i = int(i)

                    task = self.master.getTask(i-1)
                    name = task['name']
                    params = self.getTaskParams(task)
                    self.master.giveTask(bot, name, params)
                    
                elif(i==2):
                    taskList = []
                    while(True):
                        self.listTasks()
                        print('Current List:'+str(taskList[0::2]))
                        i = input('Enter nothing to go stop adding tasks\nSelect a task:')
                        if i == '':
                            break
                        i = int(i)

                        task = self.master.getTask(i-1)
                        name = task['name']
                        params = self.getTaskParams(task)

                        taskList.append(name)
                        taskList.append(params)
                        
                    i = input('how long do you want to run this loop(seconds):')
                    taskList.append('end')
                    taskList.append(int(i))

                    self.master.giveTaskLoop(bot,taskList)
                        

    def getTaskParams(self, task):
        if(task.get('required')):
            params = task.get('paramInfo')
            params = params.replace(',','\n')
            
            print(params)
            print('Press Enter to leave a paramater blank')
            
            paramList = []
            
            reqL = len(task.get('required').split(','))
            
            optL = 0
            if(task.get('optional')):
                optL = len(task.get('optional').split(','))

            for i in range(reqL+optL):
                paramList.append(input('Value of param '+str(i)+': '))    
            return paramList
        
        else:
            return None
                