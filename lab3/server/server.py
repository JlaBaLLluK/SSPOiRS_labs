import socket
import datetime

from services import FileService, get_data, send_data


class Server:
    ALLOWED_COMMANDS = ['ECHO', 'TIME', 'EXIT', 'DOWNLOAD', 'UPLOAD']

    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.creation_time = datetime.datetime.now()
        self.server_address = socket.gethostname()
        self.client_address = None
        self.port = port

    def start_server(self):
        self.socket.bind((self.server_address, self.port))
        print('BIND')
        self.get_requests()

    def get_requests(self):
        while True:
            request, self.client_address = get_data(self.socket)
            if self.handle_requests(request.decode()) == -1:
                self.socket.close()
                break

    def handle_requests(self, request):
        command = request.split()[0]
        if command == 'ECHO':
            print('ECHO command')
            if send_data(self.socket, self.client_address, ' '.join(request.split()[1:]).encode()) == -1:
                return
        elif command == 'TIME':
            print('TIME command')
            time = (datetime.datetime.now() - self.creation_time).seconds
            if send_data(self.socket, self.client_address, f'{time} seconds'.encode()) == -1:
                return
        elif command == 'DOWNLOAD':
            print('DOWNLOAD started')
            fs = FileService(request.split()[1], self.socket, self.client_address)
            fs.send_file()
            print('DOWNLOAD finished')
        elif command == 'UPLOAD':
            print('UPLOAD started')
            fs = FileService(request.split()[1], self.socket, (self.server_address, self.port))
            fs.get_file()
            print('UPLOAD finished')
        else:
            print('EXIT command')
            return -1


if __name__ == '__main__':
    server_port = int(input('Input server port: '))
    server = Server(server_port)
    server.start_server()
