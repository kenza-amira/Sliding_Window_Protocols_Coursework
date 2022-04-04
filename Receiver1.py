# /* Kenza Amira s1813674 */
import sys
from socket import *


class Receiver1:
    def __init__(self, port, file_name):
        self.host = '127.0.0.1'
        self.port = port
        self.file_name = file_name
        self.buffer_size = 1027


    def receive_file(self):
        '''
            This function is the receiver loop. It takes care of getting all the sent packet
            from the connection.
        '''
        # Binding socket
        s = socket(AF_INET, SOCK_DGRAM)
        localhost = '127.0.0.1'
        s.bind((localhost, self.port))
        print('Receiving File...')
        with open(self.file_name, 'wb') as out:
            while True:
                data, _ = s.recvfrom(self.buffer_size)
                out.write(data[3:])
                if data[2] == 1 or not data:
                    break
        # Closing the socket
        s.close()
        print(f"File received and stored at {self.file_name}") 


if __name__ == '__main__':
    PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]

    receiver = Receiver1(PORT, FILE_NAME)
    receiver.receive_file()
