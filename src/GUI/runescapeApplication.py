import kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.config import Config
from kivy.lang import Builder
from kivy.app import App
from kivy.graphics import *
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

import sys
sys.path.append('..')

import utils

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

kv = Builder.load_file('/git/runescapebot/src/GUI/runescape.kv')

class BotListArea(ScrollView):
    def __init__(self, **kwargs):
        super(BotListArea, self).__init__(**kwargs)
        self.layout = GridLayout(
            cols=1, 
            spacing=10, 
            size_hint=(1,1), 
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
       
    def refreshBots(self,bots):
        self.layout.clear_widgets()

        def callback(instance):
            botnum = int(instance.text.split(" ")[1])
            App.get_running_app().selectBot(botnum)
            getSecondWindow()

        for b in bots:
            label = "Bot "+str(b)
            btn = Button(text=label, size_hint=(1,1))
            btn.bind(on_press=callback)
            self.layout.add_widget(btn)

class StartBotArea(FloatLayout):    
    def __init__(self, **kwargs):
        super(StartBotArea, self).__init__(**kwargs)
        self.app = App.get_running_app()

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def on_enter(self):
        App.get_running_app().refreshBots()

class SecondWindow(Screen):
    def __init__(self, **kwargs):
        super(SecondWindow, self).__init__(**kwargs)

class ThirdWindow(Screen):
    def __init__(self, **kwargs):
        super(ThirdWindow, self).__init__(**kwargs)

        self.taskNames = utils.getAllTaskNames()
        self.groupNames = utils.getAllGroupNames()

        self.selectedTask = None
        self.isTask = None

        self.params = self.ids.params
        self.taskList = self.ids.taskList
        self.selectedTasks = self.ids.selectedTasks

        self.taskList.bind(minimum_height=self.taskList.setter('height'))
        self.selectedTasks.bind(minimum_height=self.selectedTasks.setter('height'))

        self.refreshTasks()

    def refreshTasks(self):

        def callback(instance):
            if instance.text.startswith("t"):
                name = instance.text.split(":")[1]
                self.selectedTask = name
                self.isTask = True

            elif instance.text.startswith("g"):
                name = instance.text.split(":")[1]
                self.selectedTask = name
                self.isTask = False

            self.refreshTasks()

        self.taskList.clear_widgets()

        for t in self.taskNames:
            self.taskList.add_widget(Button(
                    text="t:"+str(t),
                    size_hint=(1,1),
                    on_press=callback
            ))

        for g in self.groupNames:
            self.taskList.add_widget(Button(
                    text="g:"+str(g),
                    size_hint=(1,1),
                    on_press=callback
            ))

        if self.selectedTask: 
            self.selectedTasks.clear_widgets()
            self.selectedTasks.add_widget(Button(text=self.selectedTask,size_hint=(1,1)))

    def confirmButton(self):
        #this is where we would send the task or task loop to the bot 
        p = self.params.text
        if p == '':
            p = []
        else:
            p = p.split(",")
        print(p)
        
        if(self.isTask):
            App.get_running_app().giveTask(self.selectedTask, p)
        else:
            App.get_running_app().giveGroup(self.selectedTask)

        

        self.clearData()
        getMainWindow()

    def cancelButton(self):
        self.clearData()
        getSecondWindow()

    def clearData(self):
        self.params.text = ""
        self.selectedTasks.clear_widgets()
        self.selectedTask = None
        self.isTask = None
    
 

class FourthWindow(Screen):
    def __init__(self, **kwargs):
        super(FourthWindow, self).__init__(**kwargs)
        self.getPassword = 'password'
        self.getUsername = 'username'
        self.getWorld = 'world'
        self.ids.username.text = self.getUsername
        self.ids.password.text = self.getPassword
        self.ids.world.text = self.getWorld

    def confirmButton(self):
        #pass the information over
        u = self.ids.username.text
        p = self.ids.password.text 
        w = self.ids.world.text
        App.get_running_app().changeLogin(u,p,w)
        getSecondWindow()

    def cancelButton(self):
        getSecondWindow()

def getMainWindow():
    App.get_running_app().sm.current = 'main'

def getSecondWindow():
    App.get_running_app().sm.current = 'second'

def getThirdWindow():
    App.get_running_app().sm.current = 'third'

def getFourthWindow():
    App.get_running_app().sm.current = 'fourth'

class Controller(App):
    def build(self):
        self.title = 'RunescapeBot'

        #this names the different screens so you can switch between them 
        self.sm = ScreenManager()
        self.sm.add_widget(MainWindow(name = 'main'))
        self.sm.add_widget(SecondWindow(name='second'))
        self.sm.add_widget(ThirdWindow(name='third'))
        self.sm.add_widget(FourthWindow(name = 'fourth'))
        
        return self.sm

    def setMaster(self, master):
        self.master = master

    def getMaster(self):
        return self.master

    def selectBot(self, num):
        self.selectedBot = num

    def giveTask(self,t, p):
        self.master.giveTask(self.selectedBot, t, p)

    def giveGroup(self, g):
        self.master.giveGroup(self.selectedBot, g)

    def startBot(self):
        input = str(self.sm.screens[0].ids['start'].ids['botnumInput'].text)
        startNum = int()
        
        if "," in input:
            num = int(input.split(",")[0])
            numBots = int(input.split(",")[1])
            self.master.startBots(num, numBots)
        else:
            self.master.startBot(int(input))
        self.refreshBots()

    def refreshBots(self):
        self.sm.screens[0].ids['botlist'].refreshBots(self.master.bots)

    def killBot(self):
        self.master.killBot(self.selectedBot)
        getMainWindow()

    def changeLogin(self, username, password, world):
        self.master.changeLogin(self.selectedBot, username, password, world)
        

def create(master):
    app = Controller()
    app.setMaster(master)
    app.run()