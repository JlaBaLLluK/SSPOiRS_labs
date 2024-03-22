import socket
from datetime import datetime
from services import FileService, read_socket


class Server:
    ALLOWED_COMMANDS = ['ECHO', 'TIME', 'EXIT', 'DOWNLOAD', 'UPLOAD']
    OLD_USER_CONNECTED = False

    def __init__(self, address='localhost', port=8081):
        self.address = address
        self.last_connected_user = None
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.creation_time = datetime.now()

    def start_server(self):
        self.socket.bind((self.address, self.port))
        print('BIND')
        self.socket.listen()
        print('LISTEN')

    def accept_connection(self):
        while True:
            self.connection, self.address = self.socket.accept()
            if self.address == self.last_connected_user:
                self.OLD_USER_CONNECTED = True
            else:
                self.OLD_USER_CONNECTED = False

            print(f'CONNECTION FROM {self.address[0]}')
            self.get_requests()

    def get_requests(self):
        while True:
            try:
                request = read_socket(self.connection)
                if self.handle_requests(request) == -1:
                    break
            except socket.error:
                print('CONNECTION LOST')
                self.last_connected_user = self.address
                break

    def handle_requests(self, request):
        command = request.split()[0]
        if command.split(' ')[0] not in self.ALLOWED_COMMANDS:
            print('UNKNOWN COMMAND')
        elif command.split(' ')[0] == 'ECHO':
            print('ECHO command')
            self.connection.send((' '.join(request.split(' ')[1:]) + '\n').encode())
        elif command == 'TIME':
            print('TIME command')
            time = datetime.now() - self.creation_time
            self.connection.send((str(time.seconds) + ' seconds\n').encode())
        elif command == 'DOWNLOAD':
            print('DOWNLOAD started')
            fs = FileService(request.split()[1], self.connection)
            current_file_size = int(read_socket(self.connection))
            print(f'Send will be started from {current_file_size} bytes')
            fs.send_file(current_file_size)
            print('DOWNLOAD finished')
        elif command == 'UPLOAD':
            print('UPLOAD started')
            fs = FileService(request.split()[1], self.connection)
            current_file_size = fs.get_current_file_size()
            self.connection.send((str(current_file_size) + '\n').encode())
            fs.receive_file()
            print('UPLOAD finished')
        else:
            print('EXIT command')
            return -1


def main():
    address = socket.gethostname()
    port = int(input('Input server port: '))
    server = Server(address, port)
    server.start_server()
    server.accept_connection()


if __name__ == '__main__':
    main()
