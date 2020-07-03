import socket 

from time import sleep

class Connection:
    def __init__(self, host, port, BUFFER_SIZE=2000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    def connect(self):
        self.socket.connect((self.host, self.port))

    def initConnection(self):
        INIT_MESSAGE = 'init'
        INIT_MESSAGE = INIT_MESSAGE.encode('utf-8', 'strict')
        self.socket.send(INIT_MESSAGE)

        data = self.socket.recv(self.BUFFER_SIZE)
        data = data.decode('utf-8', 'strict')
        self.conn_num = int(data)

        print('connection:',self.conn_num,'initialized...')

    def handleRequests(self):
        while True:
            MESSAGE = input('Enter message to continue/ Enter exit:')
            BYTE_MESSAGE = MESSAGE.encode('utf-8', 'strict')
            self.socket.send(BYTE_MESSAGE)

            if(MESSAGE=='EXIT'):
                break

            data = self.socket.recv(self.BUFFER_SIZE)
            print (" Client:",self.conn_num," received data:", data.decode('utf-8', 'strict'))
            sleep(1)

    def send(self, message):
        byte_message = message.encode('utf-8', 'strict')
        self.socket.send(byte_message)

    def close(self):
        self.socket.close()

    def start(self):
        self.connect()
        self.initConnection()
        self.handleRequests()
        self.close()

if(__name__ == '__main__'):
    connection = Connection('localhost', 4000)
    connection.start()