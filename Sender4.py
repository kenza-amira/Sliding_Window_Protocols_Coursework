# /* Kenza Amira s1813674 */
import threading
import time
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from socket import *

from Sender3 import Sender3

# THIS IS THE SAME THING AS GO-BACK-N ONLY DIFFERENCE IS THE RETRANSMITTING OF SINGLE PACKETS
class Sender4(Sender3):
    def __init__(self, host, port, file_name, timeout, win_size):
        super(Sender4, self).__init__(host, port, file_name, timeout, win_size)
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.next_frame = []
        self.window = []
        self.acked = []

    def single_packet_send(self, pkt):
        """
        Added function relative to retransmitting only a single packet where there has been an
        issue.
        Args:
            pkt: packet to be sent again.
        """
        e = threading.Event()
        self.s.sendto(self.sequence[pkt], self.dest)
        set_timer = threading.Thread(target=self.individual_check, args=(pkt, e))
        set_timer.setDaemon(True)
        set_timer.start()
        while True:
            if not e.wait(timeout=self.timeout):
                self.s.sendto(self.sequence[pkt], self.dest)
            else:
                break
        self.acked.append(pkt)

    def individual_check(self, pkt, e):
        """
        Added function relative to checking for single packet
        Args:
            pkt: Packet
            e (threading.Event): threading Event
        """
        while True:
            self.lock.acquire()
            if pkt not in self.window:
                # Setting internal clock
                e.set()
            self.lock.release()
            time.sleep(self.timeout * 0.25)

    def recv_all(self):
        buffer = 2
        while True:
            ack, _ = self.s.recvfrom(buffer)
            ack = int.from_bytes(ack, 'big')

            self.lock.acquire()
            if self.base <= ack <= self.base + self.window_size - 1:
                if ack in self.window:
                    self.window.remove(ack)
                    self.window.sort()
                    if ack == self.base:
                        # If we sent all of the window go to next
                        if len(self.window) == 0:
                            self.base = self.next
                        else:
                            self.base = self.window[0]
                        # Forward Window
                        for _ in range(self.window_size):
                            if self.next < self.base + self.window_size:
                                self.window.append(self.next)
                                self.next_frame.append(self.next)
                                self.next += 1
                        self.window.sort()
                        self.next_frame.sort()
            self.lock.release()

    def send_file(self):
        recv = threading.Thread(target=self.recv_all)
        recv.setDaemon(True)
        recv.start()

        self.lock.acquire()
        for i in range(self.window_size):
            if self.next < self.base + self.window_size:
                self.window.append(i)
                self.next_frame.append(i)
                self.next += 1
        self.window.sort()
        self.next_frame.sort()
        self.lock.release()

        # Start threading pool with no of threads at most equal to selected
        # window size
        with ThreadPoolExecutor(max_workers=self.window_size) as pool:
            start = float(time.perf_counter())
            while True:
                # Break if we sent everything
                if len(self.sequence) - 1 in self.acked and len(self.acked) == len(self.sequence):
                    break
                if len(self.next_frame) > 0:
                    self.lock.acquire()
                    for j in self.next_frame:
                        pool.submit(self.single_packet_send, j)
                        self.next_frame.remove(j)
                    self.lock.release()
                time.sleep(self.timeout * 0.125)
        end = float(time.perf_counter())
        total_bytes = len(self.file_data)
        print((total_bytes/1024)/(end - start))
        


if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    TIMEOUT = int(sys.argv[4])/1000
    WIN_SIZE = int(sys.argv[5])

    sender4 = Sender4(HOST, PORT, FILE_NAME, TIMEOUT, WIN_SIZE)
    sender4.send_file()