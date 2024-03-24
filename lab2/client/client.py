import socket
import time

from services.services import FileService, read_socket


class Client:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(20)
        self.is_connected = False
        self.address = address
        self.port = port
        self.unfinished_request = None

    def connect_to_server(self):
        try:
            self.socket.connect((self.address, self.port))
        except socket.error:
            print('Unable connect to server.')
        else:
            self.is_connected = True
            print('Connected to server successfully.\nAllowed commands:\n1. ECHO <some-text>\n2. TIME\n'
                  '3. DOWNLOAD <file-name>\n4. UPLOAD <file-name>\n5. EXIT')

    def send_commands(self):
        while True:
            try:
                request = input('> ')
                request += '\n'
                self.unfinished_request = request
                if self.handle_requests(request) == -1:
                    break
            except socket.error:
                self.socket.close()
                self.connection_lose_handler()

    def handle_requests(self, request):
        command = request.split()[0]
        if command == 'ECHO':
            self.echo_time_handler(request)
        elif command == 'TIME':
            self.echo_time_handler(request)
        elif command == 'DOWNLOAD':
            self.download_handler(request)
        elif command == 'UPLOAD':
            self.upload_handler(request)
        elif command == 'EXIT':
            self.exit_handler(request)
            return -1
        else:
            print('Unknown command!')

    def echo_time_handler(self, request):
        self.socket.send(request.encode())
        response = read_socket(self.socket)
        print(response)

    def download_handler(self, request):
        self.socket.send(request.encode())
        fs = FileService(request.split()[1], self.socket)
        fs.get_data_start_position()
        fs.receive_file()

    def upload_handler(self, request):
        self.socket.send(request.encode())
        fs = FileService(request.split()[1], self.socket)
        print(f'Send will be started from {fs.data_start_position} bytes')
        fs.send_file()

    def exit_handler(self, request):
        self.socket.send(request.encode())
        self.socket.close()

    def connection_lose_handler(self):
        self.is_connected = False
        print("Connection lost!")
        attempts_count = 1
        while attempts_count <= 3:
            time.sleep(20)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect_to_server()
            if self.is_connected:
                print('Making unfinished operation...')
                self.handle_requests(self.unfinished_request)
                break
            else:
                attempts_count += 1
        else:
            print('Unable reconnect to server! Finishing...')
            self.socket.close()
            exit()


def main():
    address = input('Input server address: ')
    port = int(input('Input server port: '))
    client = Client(address, port)
    client.connect_to_server()
    if not client.is_connected:
        return

    client.send_commands()


if __name__ == '__main__':
    main()
