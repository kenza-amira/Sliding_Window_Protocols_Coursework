# /* Kenza Amira s1813674 */
import sys
import time
import math
from socket import *


class Sender1:
    def __init__(self, host, port, file_name=''):
        self.host = host
        self.port = port
        self.file_name = file_name

    @staticmethod
    def segmentation(file_data):
        ''' This function segments the file into multiple packets of size 1024'''
        total_bytes = len(file_data)
        packet_size = 1024
        number_of_packets = int(math.ceil((total_bytes/packet_size)))
        packets = []
        for i in range(number_of_packets):
            content = file_data[(packet_size * i):(packet_size * (i + 1))]
            packets.append(content)
        return packets

    @staticmethod
    def header_processing(packets):
        ''' 
            This function takes care of generating headers for each packet.
            This includes sequence number and End-Of-File byte.
        '''
        for i in range(len(packets)):
            sequence_number = int(i).to_bytes(2, 'big')
            if i == len(packets) - 1:
                EOF = int(1).to_bytes(1, 'big')
            else:
                EOF = int(0).to_bytes(1, 'big')
            header = sequence_number + EOF
            packets[i] = header + packets[i]
        return packets  

    def send_file(self):
        '''
            This function constitutes the sender loop. It initializes the sender connection
            and sends all the packets.
        '''
        # Initialize conenction
        s = socket(AF_INET, SOCK_DGRAM)
        address = (self.host, self.port)
        s.connect(address)
        with open(self.file_name, 'rb') as to_send:
            file_data = to_send.read()
            all_packets = self.header_processing(self.segmentation(file_data))
            # Sending packets
            for i in range(len(all_packets)):
                s.sendto(all_packets[i], address)
                # Sleep so packets arrive in order
                time.sleep(0.02)
        # Closing the socket
        s.close()


if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]

    sender = Sender1(HOST, PORT, FILE_NAME)
    sender.send_file()
    print("File Sent!")
