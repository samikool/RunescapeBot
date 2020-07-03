import threading

from connection import Connection

class BotClient:
    def __init__(self, client_num):
        self.conn = Connection('localhost', 4000)
        self.client_num = client_num
    
    def start(self):
        threading.Thread(target=self.conn.start())