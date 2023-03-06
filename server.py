import socket
from _thread import start_new_thread
import threading
import sys
import random

class Server:
    def __init__(self, host1, port1, host2, port2, host3, port3, log_name, name):
        # host1 and port1 are for this server
        self.host1 = host1
        self.port1 = port1
        self.host2 = host2
        self.port2 = port2
        self.host3 = host3
        self.port3 = port3
        self.log_name = log_name
        # our convention depends on knowing if this is server A, B, or C:
        # - if A, you create socket to B and C (bind call + listen)
        # - if B, you create socket to C and connect to A
        # - if C, you just connect to existing A and B sockets

        # A must be made before B, B must be made before C
        # DO THE LOGIC HERE
        self.name = name

        # used whenever a data structure gets updated
        self.ds_lock = threading.Lock()
        # list of tuples: (host, port, msg)
        self.network_queue = []
        self.clock_rate = random.randint(1, 6)
        # initialize the logic clock to be at time 0
        self.clock = 0

        self.socket_a = 0
        self.socket_b = 0
        self.socket_c = 0
	
        # START 3 THREADS HERE: ONE FOR LISTENING TO HOST2/PORT2, ONE FOR LISTENING TO HOST3/PORT3, AND ONE PROCESS THREAD

    def listening(self, s):
        # logic for the threads that listen to other servers and updates network queue
        # this depends on if self.name is A, B, or C (you either bind or connect)
	    while True:
			c, addr = s.accept()
			print('Connected to :', addr[0], ':', addr[1])
    
    def process(self):
        # all logic for reading queue/doing shit
        pass
    


def main():
	args = sys.argv[1:]
	assert len(sys.argv) == 8, f"provide h1, p1, h2, p2, h3, p3, file_name, name"
	
	me = Server(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])


if __name__ == '__main__':
	main()
	