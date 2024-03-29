import select
import time
import socket as sck

MAX_SN_SIZE = 10

PACKET_TO_LOSE = ['0000000852', '0000000027', '0000000358']
NEED_TO_LOSE_PACKET = True


class FileService:

    def __init__(self, file_name, socket, receiver_address):
        self.file_name = file_name
        self.socket = socket
        self.receiver_address = receiver_address

    def send_file(self):
        try:
            with open(self.file_name, 'rb') as file:
                file_len = len(file.read())
                if send_data(self.socket, self.receiver_address, str(file_len).encode()) == -1:
                    return

                file.seek(0)
                part_of_file = file.read(8192)
                packet_num = 0
                while part_of_file:
                    send_data(self.socket, self.receiver_address, part_of_file, packet_num)
                    part_of_file = file.read(8192)
                    packet_num += 1
        except FileNotFoundError:
            print("File doesn't exist!")
            send_data(self.socket, self.receiver_address, str(-1).encode())

    def get_file(self):
        file_len = int(get_data(self.socket)[0].decode())
        if file_len == -1:
            print('Unable to receive file!')
            return

        with open(self.file_name, 'wb') as file:
            file_data = bytes()
            received_sns = []
            while True:
                packet, address = get_data(self.socket, 10000)
                sn = packet[:MAX_SN_SIZE].decode()
                if sn in received_sns:
                    continue

                part_of_file = packet[MAX_SN_SIZE:]
                file_data += part_of_file
                file.write(part_of_file)
                received_sns.append(sn)
                print(f"Received {len(file_data)}, expect {file_len}, sn - {sn}")
                if len(file_data) == file_len:
                    break


def make_packet(packet_num, encoded_data):
    sn = make_sn(packet_num)
    packet = sn.encode() + encoded_data
    return packet, sn


def send_data(socket, address, encoded_data, packet_num=0):
    packet, sn = make_packet(packet_num, encoded_data)
    # if sn in PACKET_TO_LOSE and NEED_TO_LOSE_PACKET:
    #     print('LOST PACKET (PACKET TO LOSE)')
    # else:
    socket.sendto(packet, address)
    try:
        wait_acknowledge(socket, encoded_data, packet_num, address)
    except sck.error:
        print('Unable to send data!')
        return -1


def get_data(socket, read_size=1024):
    packet, address = socket.recvfrom(read_size)
    sn = packet[:MAX_SN_SIZE]
    socket.sendto(sn, address)
    return packet, address


def wait_acknowledge(socket, encoded_data, packet_num, address):
    for i in range(1, 6):
        timeout = i * 10
        read_sockets, _, _ = select.select([socket], [], [], timeout)

        global NEED_TO_LOSE_PACKET

        if len(read_sockets) == 0:
            print(f"Didn't receive acknowledge! Resend packet {packet_num}")

            NEED_TO_LOSE_PACKET = False

            send_data(socket, address, encoded_data, packet_num)
            break

        accepted_sn, address = socket.recvfrom(100)
        print(f"Received sn {accepted_sn.decode()}")
        NEED_TO_LOSE_PACKET = True
        accepted_sn = accepted_sn[:MAX_SN_SIZE].decode()
        sn = make_sn(packet_num)
        if accepted_sn != sn:
            time.sleep(timeout)
            print(f'Got {accepted_sn}, expected {sn}. It is wrong!')
            send_data(socket, address, encoded_data, packet_num)
        else:
            return
    else:
        print('RAISING')
        raise sck.error


def make_sn(sn):
    return (MAX_SN_SIZE - len(str(sn))) * '0' + str(sn)
