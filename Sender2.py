# /* Kenza Amira s1813674 */
import sys
import time
from socket import *
from Sender1 import Sender1


class Sender2(Sender1):
    def __init__(self, host, port, file_name, timeout):
        super(Sender2, self).__init__(host, port, file_name)
        self.timeout  = timeout
        
    def read_file(self, filename):
        """ This function is a helper function to read a file.

        Args:
            filename (In our case JPG image): File to be read

        Returns:
            [bytes]: File in bytes
        """
        with open(filename, "rb") as file:
            if not file:
                sys.exit(0)
            data = file.read()
        return data

    def send_file(self):
        """
        This function is the sender loop with the stop and wait protocol. 
        """
        
        #Retranmissions variables
        re_trans = 0
        ack_size = 2
        
        #Getting packets to be sent from input file
        data = self.read_file(self.file_name)
        packet_list = self.header_processing(self.segmentation(data))
        
        # Initializing socket connection with input timeout
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(self.timeout)
        to = (self.host, self.port)
        
        # For throughput calculation
        start = time.time()
        # Iterating over packets to be sent
        for i in range(len(packet_list)):
            s.sendto(packet_list[i], to)
            # Implementing stop and wait protocol
            while True:
                # Wait for acknowledgement, if received the right ack, continue else if 
                # timeout re transmit packet and increase retransmission count
                try:
                    ack, _ = s.recvfrom(ack_size)
                    ack = int.from_bytes(ack, 'big')
                    if ack == i:
                        break
                except timeout:
                    re_trans += 1
                    s.sendto(packet_list[i], to)
        # For throughput calculation    
        end = time.time()
        # Close socket
        s.close()
        total_bytes = len(data)
        throughput = (total_bytes/1024)/(end - start)
        # Outputting number of retransmissions and throughput
        print(f"{re_trans} {throughput}")

if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    TIMEOUT = int(sys.argv[4])/1000

    sender = Sender2(HOST, PORT, FILE_NAME, TIMEOUT)
    sender.send_file()