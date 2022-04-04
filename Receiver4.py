# /* Kenza Amira s1813674 */
import sys
from socket import *

from Receiver3 import Receiver3

class Receiver4(Receiver3):
    def __init__(self, port, file_name, window_size):
        super(Receiver4, self).__init__(port, file_name)
        self.window_size = window_size
    
    def receive_file(self):
        current_window = {}
        base = 0
        localhost = '127.0.0.1'
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(3)
        s.bind((localhost, self.port))
        with open(self.file_name, 'wb') as out:
            while True:
                try:
                    data, addr = s.recvfrom(self.buffer_size)
                    seq = int.from_bytes(data[0:2], 'big')
                except timeout:
                    break
                if base <= seq <= base + self.window_size - 1:
                    s.sendto(seq.to_bytes(2, 'big'), addr)
                    current_window[seq] = data[3:]
                    if seq == base:
                        out.write(data[3:])
                        del current_window[seq]
                        base += 1
                        forward = []
                        keys = list(current_window.keys())
                        keys.sort()
                        for i in keys:
                            if i == base:
                                forward.append(base)
                                out.write(current_window[i])
                                base += 1
                        for j in forward:
                            del current_window[j]
                elif base - self.window_size <= seq <= base - 1:
                    s.sendto(seq.to_bytes(2,'big'), addr)
                if data[2] == 1 and len(current_window) == 0:
                    for _ in range(10):
                        s.sendto(seq.to_bytes(2, 'big'), addr)
                    break
        s.close()
                    

if __name__ == '__main__':
    PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]
    WIN_SIZE = int(sys.argv[3])

    receiver = Receiver4(PORT, FILE_NAME, WIN_SIZE)
    receiver.receive_file()