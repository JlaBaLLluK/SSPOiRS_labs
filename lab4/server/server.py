import socket
from datetime import datetime
from services.services import FileService, read_socket
import threading


class Server:
    ALLOWED_COMMANDS = ['ECHO', 'TIME', 'EXIT', 'DOWNLOAD', 'UPLOAD']
    connected_users = []

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.creation_time = datetime.now()

    def start_server(self):
        self.socket.bind((self.address, self.port))
        print('BIND')
        self.socket.listen()
        print('LISTEN')

    def accept_connection(self):
        while True:
            connection, address = self.socket.accept()
            thread = threading.Thread(target=self.get_requests, args=(connection, address[0]))
            thread.start()

    def get_requests(self, connection, address):
        print('NEW THREAD STARTED')
        print(f'CONNECTION FROM {address}')
        while True:
            try:
                request = read_socket(connection)
                if self.handle_requests(request, connection, address) == -1:
                    break
            except socket.error:
                print('CONNECTION LOST')
                self.connected_users.append(address)
                break

    def handle_requests(self, request, connection, address):
        command = request.split()[0]
        if command.split(' ')[0] not in self.ALLOWED_COMMANDS:
            print('UNKNOWN COMMAND')
        elif command.split(' ')[0] == 'ECHO':
            print('ECHO command')
            connection.send((' '.join(request.split(' ')[1:]) + '\n').encode())
        elif command == 'TIME':
            print('TIME command')
            time = datetime.now() - self.creation_time
            connection.send((str(time.seconds) + ' seconds\n').encode())
        elif command == 'DOWNLOAD':
            print('DOWNLOAD started')
            fs = FileService(request.split()[1], connection)
            connection.send((str(1 if address in self.connected_users else 0) + '\n').encode())
            data_start_position = int(read_socket(connection))
            print(f'Send will be started from {data_start_position} bytes')
            fs.send_file(data_start_position)
            print('DOWNLOAD finished')
        elif command == 'UPLOAD':
            print('UPLOAD started')
            fs = FileService(request.split()[1], connection)
            data_start_position = fs.get_data_start_position(address, self)
            connection.send((str(data_start_position) + '\n').encode())
            fs.receive_file(data_start_position)
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
