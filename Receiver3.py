# /* Kenza Amira s1813674 */
from Receiver2 import Receiver2
from socket import *
import sys


class Receiver3(Receiver2):
    def receive_file(self):
        seq_lis = []
        localhost = '127.0.0.1'
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((localhost, self.port))
        seq_expect = 0
        with open(self.file_name, 'wb') as out:
            while True:
                data, addr = s.recvfrom(self.buffer_size)
                seq = int.from_bytes(data[0:2], 'big')
                if seq not in seq_lis:
                    if seq == seq_expect:
                        seq_lis.append(seq)
                        out.write(data[3:])
                        seq_expect += 1
                if len(seq_lis) > 0:
                    s.sendto((seq_lis[-1]).to_bytes(2, 'big'), addr)
                if data[2] == 1 and len(seq_lis) == seq + 1:
                    for _ in range(10):
                        s.sendto(seq.to_bytes(2, 'big'), addr)
                    break
            s.close()


if __name__ == '__main__':
    PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]

    receiver3 = Receiver3(PORT, FILE_NAME)
    receiver3.receive_file()