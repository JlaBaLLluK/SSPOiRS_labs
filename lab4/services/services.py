import os
import socket
import select


class FileService:
    def __init__(self, file_name, sock):
        self.file_name = file_name
        self.socket = sock

    def send_file(self, data_start_position):
        try:
            with open(self.file_name, 'rb') as file:
                self.socket.send((str(len(file.read())) + '\n').encode())
                file.seek(0)
                self.socket.sendfile(file, data_start_position)
        except FileNotFoundError:
            print("File doesn't exist!")
            self.socket.send((str(-1) + '\n').encode())

    def receive_file(self, data_start_position):
        real_file_length = int(read_socket(self.socket))
        if real_file_length == -1:
            print("File doesn't exist!")
            return

        with open(self.file_name, 'ab') as file:
            file_data = bytes()
            file.seek(data_start_position, os.SEEK_SET)
            file.truncate(data_start_position)
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

    def get_data_start_position(self, address, server_obj):
        try:
            with open(self.file_name, 'rb') as file:
                print(f'Address = {address}, server addresses - {server_obj.connected_users}')
                return len(file.read()) if address in server_obj.connected_users else 0
        except FileNotFoundError:
            return 0


def read_socket(sock):
    byte = sock.recv(1).decode()
    data = ''
    while byte != '\n':
        data += byte
        byte = sock.recv(1).decode()

    return data
