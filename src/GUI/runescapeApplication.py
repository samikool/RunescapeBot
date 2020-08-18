import kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
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

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        app = App.get_running_app()
        #TODO change these to dicts
        self.bots = []
        self.currentLabels = []
        self.botBoolean = True

    def getBots(self):
        
        app = App.get_running_app()
        bots = app.master.bots

        def callback(instance):
            if int(instance.id) in self.bots:
                global selectedBot
                selectedBot = instance.id
                print("you clicked on " + str(instance.id))
                getSecondWindow()

        self.y = .7
        self.x = .2

        for i in bots:
            self.bots.append(i)
            label = "Bot "+str(i)

            if self.y > .4:
                i = Button(text = label, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                i.bind(on_press=callback)
                self.currentLabels.append(i)
                self.add_widget(i)
                self.y -= .1

            elif self.y <= .4:
                self.y = .7
                self.x = self.x + .1
                i = Button(text = label, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                i.bind(on_press=callback)
                self.currentLabels.append(i)
                self.add_widget(i)
                self.y -=.1

        print(self.currentLabels)

    #not using currently but can be used to refresh the bot list
    #possibly could make this automatic
    def refreshList(self):
        if self.currentLabels != []:
            for x in self.currentLabels:
                self.remove_widget(x)

            for n in self.currentLabels:
                self.currentLabels.remove(n)
        
        self.getBots()

    #This will be where we launch the bot to go do its tasks it was given
    def startBot(self):
        self.inputDisplay = self.ids.inputDisplay.text

        app = App.get_running_app()
        app.master.startBot(int(self.inputDisplay))

        # self.app.master.startBot(int(self.inputDisplay))

        print("started bot on input display #" + str(self.inputDisplay))
        if self.botBoolean == True:
            self.ids.success.visible = True
            self.ids.failure.visible = False
        if self.botBoolean == False:
            self.ids.failure.visible = True
            self.ids.success.visible = False
        self.refreshList()

class SecondWindow(Screen):
    def __init__(self, **kwargs):
        super(SecondWindow, self).__init__(**kwargs)

    #function to kill the bot
    #TODO Implement killing bot
    def killBot(self):
        global selectedBot

        app = App.get_running_app()
        app.master.killBot(int(selectedBot))
        
        self.deadBot = Label(text = (selectedBot + " has been killed"), pos_hint = {'center_y': .4, 'center_x': .5}, size_hint = (.2, .2))
        self.add_widget(self.deadBot)
        s = app.sm.get_screen('main')

        s.bots.remove(int(selectedBot))
        s.remove_widget(selectedBot)       


class ThirdWindow(Screen):
    def __init__(self, **kwargs):
        super(ThirdWindow, self).__init__(**kwargs)
        self.taskList = utils.getAllTaskNames() + utils.getAllGroupNames()
        self.taskWidgets = []
        self.selectedTasks = []
        self.selectedTaskWidgets = []
        self.getTasks()

    def getTasks(self):
        for y in self.taskWidgets:
            self.remove_widget(y)

        def callback(instance):
            if instance.id in self.taskList:
                taskSelected = str(instance.id)
                self.remove_widget(instance)
                self.selectedTasks.append(taskSelected)
                self.taskList.remove(instance.id)
                self.getSelectedTasks()
                self.getTasks()
                print("you clicked on " + str(instance.id))

        self.y = .85
        self.x = .14
        for i in self.taskList: 
            if self.y > .35:
                i = Button(text = i, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                self.taskWidgets.append(i)
                i.bind(on_press = callback)
                self.add_widget(i)
                self.y -= .05

            elif self.y < .35:
                self.y = .85
                self.x = self.x + .1
                i = Button(text = i, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                self.taskWidgets.append(i)
                i.bind(on_press = callback)
                self.add_widget(i)
                self.y -=.05

    def getSelectedTasks(self):
        self.y = .85
        self.x = .64
        for x in self.selectedTaskWidgets:
            self.remove_widget(x)

        def callback(instance):
            if instance.id in self.selectedTasks:
                print("you clicked on: " + str(instance.id))
                self.selectedTasks.remove(instance.id)
                self.taskList.append(instance.id)
                self.getSelectedTasks()
                self.getTasks()

        for i in self.selectedTasks:
            if self.y > .35:
                i = Button(text = i, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                self.selectedTaskWidgets.append(i)
                i.bind(on_press = callback)
                self.add_widget(i)
                self.y -= .05
            elif self.y < .35:
                self.y = .85
                self.x = self.x + .1
                i = Button(text = i, size_hint =(.05, .05), pos_hint = {'center_y': self.y, 'center_x': self.x}, background_color =(0, 0, 0, 0), id = str(i))
                self.selectedTaskWidgets.append(i)
                i.bind(on_press = callback)
                self.add_widget(i)
                self.y -=.05

            print(self.selectedTasks)

    def cancelButton(self):
        for x in self.selectedTaskWidgets:
            self.remove_widget(x)

        for y in self.taskWidgets:
            self.remove_widget(y)

        self.selectedTasks = []
        self.taskList = []
        self.selectedTaskWidgets = []
        self.taskWidgets = []
        self.getTasks()
        self.getSelectedTasks()
        getSecondWindow()

    def confirmButton(self):
        #this is where we would send the task or task loop to the bot 
        getMainWindow()
 

class FourthWindow(Screen):
    def __init__(self, **kwargs):
        super(FourthWindow, self).__init__(**kwargs)
        self.getPassword = 'password'
        self.getUsername = 'username'
        self.ids.username.text = self.getUsername
        self.ids.password.text = self.getPassword

    def loginChange(self):
        pass

    def confirmButton(self):
        #pass the information over
        getSecondWindow()

    def cancelButton(self):
        getSecondWindow()

 

def getMainWindow():
    app = App.get_running_app()
    print('here')
    app.sm.current = 'main'

def getSecondWindow():
    app = App.get_running_app()
    print('here1')
    app.sm.current = 'second'

def getThirdWindow():
    app = App.get_running_app()
    print('here2')
    app.sm.current = 'third'

def getFourthWindow():
    app = App.get_running_app()
    print('here3')
    app.sm.current = 'fourth'

class MyApp(App):
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

def create(master):
    app = MyApp()
    app.setMaster(master)
    app.run()


# if __name__ == '__main__':
#     MyApp().run()