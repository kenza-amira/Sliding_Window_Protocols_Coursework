# /* Kenza Amira s1813674 */
import threading
import time

from Sender2 import Sender2
from socket import *
import sys

class Sender3(Sender2):
    def __init__(self, host, port, file_name, timeout, window_size):
        super(Sender3, self).__init__(host, port, file_name, timeout)
        # Setting window size
        self.window_size = window_size
        # Setting destination address
        self.dest = (self.host, self.port)
        # Getting file data
        self.file_data = self.read_file(self.file_name)
        # Generating packet sequence
        self.sequence = self.header_processing(self.segmentation(self.file_data))
        # Initializing Thread variables
        self.base = 0
        self.next = 0
        self.lock = threading.Lock()

    def send(self, s, e):
        """
        Send Function for the Go-Back-N protocol. All the work
        is done on the sender's side so the receiver code in
        Receiver3 will be as simple as Receiver2. This function is
        implemented following FSM given in Figure 3.20 from the textbook.

        Args:
            s (socket): Used socket
            e (Threding Event): Threading Event
        """
        # Start by checking if the window is full
        while (True):
            if self.base > len(self.sequence) - 1 or self.next > len(self.sequence) - 1:
                break
            if self.next < self.base + self.window_size:
            # If window is not full, packets are created ans sent
            # and all variables are updated
                for i in range(self.window_size):
                    s.sendto(self.sequence[self.next], self.dest)
                    with self.lock:
                        self.next += 1
                    if self.next >= len(self.sequence) - 1:
                        with self.lock:
                            self.next = len(self.sequence) - 1
                        break
            e.clear()
            if not e.wait(self.timeout):
                # If a timeout occurs, sender resends all packets that
                # have been previously sent but have not been acknowledged.
                for i in range(self.base, self.next):
                    s.sendto(self.sequence[i], self.dest)

    def receive(self, s, e):
        """
        This function describes the acknowledgment reception.
        This is a cumulative acknowledgment: i.e, an ack for a packer with
        sequence number n will be taken as indicating that all packets
        with a sequence number up to and including n have been correctly
        received at the receiver.

        Args:
            s (socket): Used socket
            e (Threading Event): Threading Event
        """
        ack_size = 2
        while True:
            ack, _ = s.recvfrom(ack_size)
            ack = int.from_bytes(ack, 'big')

            with self.lock:
                if ack == self.base:
                    # If we receive the acknowledgment, we send the next sequence
                    # and update all variables accordingly
                    if self.next <= len(self.sequence) - 1:
                        s.sendto(self.sequence[self.next], self.dest)
                    self.base += 1
                    if self.next < len(self.sequence) - 1:
                        self.next += 1
                    # Set event internal flag to true. All the threads waiting
                    # for that event object get awakened.
                    e.set()
                elif ack > self.base:
                    self.base = ack + 1
                    self.next = self.base
                    # Set event internal flag to true, equivalent
                    # to starting timer. All the threads waiting 
                    # for that event object get awakened.
                    e.set()

            if ack == len(self.sequence) - 1:
                break

    def send_file(self):
        # For throughput calculation
        start = time.time()

        # Initializing socket
        s = socket(AF_INET,  SOCK_DGRAM)

        # Starting threads
        event = threading.Event()

        sendThread = threading.Thread(target=self.send, args=(s, event))
        receiveThread= threading.Thread(target=self.receive, args=(s, event))
        
        sendThread.setDaemon(True)
        receiveThread.setDaemon(True)

        sendThread.start()
        receiveThread.start()

        sendThread.join()
        receiveThread.join()

        # Throughput Calculation
        end = time.time()
        total_bytes = len(self.file_data)
        print((total_bytes / 1024) / (end - start))


if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    TIMEOUT = int(sys.argv[4])/1000
    WINDOW_SIZE = int(sys.argv[5])

    sender3 = Sender3(HOST, PORT, FILE_NAME, TIMEOUT, WINDOW_SIZE)
    sender3.send_file()    