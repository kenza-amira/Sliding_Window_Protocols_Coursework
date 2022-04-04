# /* Kenza Amira s1813674 */
import sys
from socket import *
from Receiver1 import Receiver1

class Receiver2(Receiver1):
    def __init__(self, port, file_name):
        super().__init__(port, file_name)
    
    def receive_file(self):
        """
        This function constitutes the receiver loop with a stop and wait protocol.
        """
        # Binding the socket
        localhost = '127.0.0.1'
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((localhost, self.port))
        
        # Initializing expected sequence number
        expected = 0

        with open(self.file_name, 'wb') as out:
            while True:
                data, addr = s.recvfrom(self.buffer_size)
                # Get Sequence Number
                seq = int.from_bytes(data[0:2], 'big')
                # If expected sequence number write to file and update
                # expected sequence number
                if seq == expected:
                    out.write(data[3:])
                    expected += 1
                # Send ack
                s.sendto(seq.to_bytes(2, 'big'), addr)
                # If end of file send 10 acknowledgment to sender to end
                # the process
                if data[2] == 1:
                    for _ in range(10):
                        s.sendto(seq.to_bytes(2, 'big'), addr)
                    break
        s.close()


if __name__ == '__main__':
    PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]
    receiver2 = Receiver2(PORT, FILE_NAME)
    receiver2.receive_file()