import socket
from threading import Thread
from socketserver import ThreadingMixIn

class ClientThread(Thread):
    def __init__(self, ip, port, client_num, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.client_num = client_num
        self.conn = conn

    def run(self):

        while True:
            byte_data = self.conn.recv(2048)
            string_data = byte_data.decode('utf-8')

            print("Server received data:", string_data)
            
            if(string_data == 'EXIT'):
                break

            self.conn.send(byte_data)
        print('Client: ', self.client_num, ' closed connection...')

class MasterServer:
    clients = []
    connected_clients = 0
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self, host, port, buffer_size=1024):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.socket.bind((self.host, self.port))
        print('server listening...')
        while True:
            self.socket.listen(4)          
            conn, (ip,port) = self.socket.accept()
           
            print('client: ', self.connected_clients, ' connected...')

            client = ClientThread(ip, port, self.connected_clients, conn)
            client.start()

            self.connected_clients += 1

            self.clients.append(client)

server = MasterServer('0.0.0.0', 4000)
server.start()