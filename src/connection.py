# Python TCP Client A
import socket 

# tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# tcpClientA.connect((host, port))
# tcpClientA.close() 

class Connection:
    def __init__(self, host, port, BUFFER_SIZE=2000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    def connect(self):
        self.socket.connect((self.host, self.port))

    def handleRequests(self):
        while True:
            MESSAGE = input("tcpClientA: Enter message to continue/ Enter exit:")
            BYTE_MESSAGE = MESSAGE.encode('utf-8', 'strict')
            self.socket.send(BYTE_MESSAGE)

            if(MESSAGE=='EXIT'):
                break

            data = self.socket.recv(self.BUFFER_SIZE)
            print (" Client2 received data:", data.decode('utf-8', 'strict'))

    def send(self, message):
        byte_message = message.encode('utf-8', 'strict')
        self.socket.send(byte_message)

    def close(self):
        self.socket.close()

    def start(self):
        self.connect()
        self.handleRequests()
        self.close()

connection = Connection('localhost', 4000)
connection.start()