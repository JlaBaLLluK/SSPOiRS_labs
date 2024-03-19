import socket


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self, address, port):
        try:
            self.socket.connect((address, port))
        except ConnectionError or TimeoutError:
            print('Unable connect to server.')
            exit()
        else:
            print('Connected to server successfully.\nAllowed commands:\n1. ECHO\n2. TIME\n3. EXIT.')

    def send_commands(self):
        while True:
            command = input('> ')
            self.socket.send(command.encode())
            response = self.socket.recv(1024).decode()
            if command != 'EXIT':
                print(response)
            else:
                self.socket.close()
                break


def main():
    client = Client()
    address = input('Input server address: ')
    port = int(input('Input server port: '))
    client.connect_to_server(address, port)
    client.send_commands()


if __name__ == '__main__':
    main()
