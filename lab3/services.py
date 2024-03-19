import select
import time
import socket as sck

MAX_SN_SIZE = 10
# PACKET_LOST = False
# LOST_PACKETS = ['0000000852', '0000000027', '0000000358']


class FileService:

    def __init__(self, file_name, socket, receiver_address):
        self.file_name = file_name
        self.socket = socket
        self.receiver_address = receiver_address

    def send_file(self):
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

    def get_file(self):
        file_len = int(get_data(self.socket)[0].decode())
        with open(self.file_name, 'wb') as file:
            file_data = bytes()
            while True:
                packet, address = get_data(self.socket, 10000)
                file_data += packet
                file.write(packet)
                print(f"Received {len(file_data)}, expect {file_len}")
                if len(file_data) == file_len:
                    break


def make_packet(packet_num, encoded_data):
    sn = make_sn(packet_num)
    packet = sn.encode() + encoded_data
    return packet, sn


def send_data(socket, address, encoded_data, packet_num=0):
    packet, sn = make_packet(packet_num, encoded_data)
    socket.sendto(packet, address)
    # global PACKET_LOST
    # if sn in LOST_PACKETS and not PACKET_LOST:
    #     print('PACKET LOST')
    #     PACKET_LOST = True
    # else:
    #     socket.sendto(packet, address)
    try:
        wait_acknowledge(socket, encoded_data, packet_num, address)
    except sck.error:
        print('Unable to send data!')
        return -1


def get_data(socket, read_size=1024):
    packet, address = socket.recvfrom(read_size)
    sn = packet[:MAX_SN_SIZE]
    data = packet[MAX_SN_SIZE:]
    socket.sendto(sn, address)
    return data, address


def wait_acknowledge(socket, encoded_data, packet_num, address):
    for i in range(1, 6):
        timeout = i * 10
        # global PACKET_LOST
        read_sockets, _, _ = select.select([socket], [], [], timeout)
        if len(read_sockets) == 0:
            print("Didn't receive acknowledge!")
            send_data(socket, address, encoded_data, packet_num)
            # PACKET_LOST = False
            break

        accepted_sn, address = socket.recvfrom(MAX_SN_SIZE)
        accepted_sn = accepted_sn.decode()
        sn = make_sn(packet_num)
        if accepted_sn != sn:
            time.sleep(timeout)
            send_data(socket, address, encoded_data, packet_num)
            print(f'Got {accepted_sn}, expected {sn}. It is wrong!')
        else:
            break
    else:
        raise sck.error


def make_sn(sn):
    return (MAX_SN_SIZE - len(str(sn))) * '0' + str(sn)
