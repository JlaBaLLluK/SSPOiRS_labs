import socket
from services import FileService, send_data, get_data


class Client:
    ALLOWED_COMMANDS = ['ECHO', 'TIME', 'EXIT', 'DOWNLOAD', 'UPLOAD']

    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.port = port

    def send_commands(self):
        print('Connected to server successfully.\nAllowed commands:\n1. ECHO <some-text>\n2. TIME\n'
              '3. DOWNLOAD <file-name>\n4. UPLOAD <file-name>\n5. EXIT')
        while True:
            request = input('> ')
            if self.handle_requests(request) == -1:
                break

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
        if send_data(self.socket, (self.address, self.port), request.encode()) == -1:
            return

        print(get_data(self.socket)[0].decode())

    def download_handler(self, request):
        if send_data(self.socket, (self.address, self.port), request.encode()) == -1:
            return

        fs = FileService(request.split()[1], self.socket, (self.address, self.port))
        fs.get_file()

    def upload_handler(self, request):
        if send_data(self.socket, (self.address, self.port), request.encode()) == -1:
            return

        fs = FileService(request.split()[1], self.socket, (self.address, self.port))
        fs.send_file()

    def exit_handler(self, request):
        if send_data(self.socket, (self.address, self.port), request.encode()) == -1:
            return

        self.socket.close()


if __name__ == '__main__':
    server_address = input('Input server address: ')
    server_port = int(input('Input server port: '))
    client = Client(server_address, server_port)
    client.send_commands()
