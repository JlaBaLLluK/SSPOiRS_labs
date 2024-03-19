import socket
from datetime import datetime


class Server:
    ALLOWED_COMMANDS = ['ECHO', 'TIME', 'EXIT']

    def __init__(self, address='192.168.176.88', port=8081):
        self.address = address
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
            self.connection, address = self.socket.accept()
            print(f'CONNECTION FROM {address[0]}')
            self.handle_commands()

    def handle_commands(self):
        while True:
            command = self.connection.recv(1024).decode()
            if command.split(' ')[0] not in self.ALLOWED_COMMANDS:
                self.connection.send('Unknown command.'.encode())
                print('UNKNOWN COMMAND')
                continue

            if command.split(' ')[0] == 'ECHO':
                print('ECHO command')
                self.connection.send(' '.join(command.split(' ')[1:]).encode())
            elif command == 'TIME':
                print('TIME command')
                time = datetime.now() - self.creation_time
                self.connection.send(str(time).encode())
            else:
                print('EXIT command')
                self.connection.close()
                break


def main():
    server = Server()
    server.start_server()
    server.accept_connection()


if __name__ == '__main__':
    main()
