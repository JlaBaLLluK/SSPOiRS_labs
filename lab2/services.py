import socket
import select


class FileService:
    def __init__(self, file_name, sock):
        self.file_name = file_name
        self.socket = sock

    def send_file(self, current_file_size):
        try:
            with open(self.file_name, 'rb') as file:
                self.socket.send((str(len(file.read())) + '\n').encode())
                file.seek(0)
                self.socket.sendfile(file, current_file_size)
        except FileNotFoundError:
            print("File doesn't exist!")
            self.socket.send((str(-1) + '\n').encode())

    def receive_file(self):
        real_file_length = int(read_socket(self.socket))
        if real_file_length == -1:
            print("File doesn't exist!")
            return

        with open(self.file_name, 'ab') as file:
            file_data = bytes()
            current_file_length = file.tell()
            while True:
                ready = select.select([self.socket], [], [], 20)
                if len(ready[0]) != 0:
                    read_data = self.socket.recv(8192)
                    current_file_length += len(read_data)
                    file.write(read_data)
                    print(f"Received: {current_file_length}, expect: {real_file_length}")
                else:
                    raise socket.error

                if current_file_length == real_file_length:
                    break

            file.write(file_data)
            file.close()

    def get_current_file_size(self):
        try:
            with open(self.file_name, 'rb') as file:
                from server.server import Server
                return len(file.read()) if Server.OLD_USER_CONNECTED else 0
        except FileNotFoundError:
            return 0


def read_socket(sock):
    byte = sock.recv(1).decode()
    data = ''
    while byte != '\n':
        data += byte
        byte = sock.recv(1).decode()

    return data
