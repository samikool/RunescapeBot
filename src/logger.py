import time
import os

class Logger():
    def __init__(self, botnum):
        self.bnum = botnum
        self.fp = os.getcwd()+os.sep+'logs'+os.sep+'bot_'+str(botnum)+'.log'
        self.createFile()

    def prefix(self):
        t0 = time.asctime()
        return t0+': '
    
    def createFile(self):
        if not os.path.exists('logs'):
            os.mkdir('logs')

        with open(self.fp, 'w') as f:
            f.write(self.prefix()+'Logger for '+str(self.bnum)+' initialized.\n')

    def log(self,msg):
        with open(self.fp, 'a') as f:
            f.write(self.prefix()+msg+'\n')