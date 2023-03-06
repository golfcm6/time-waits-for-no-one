import socket
from _thread import start_new_thread
import threading
import sys
import random

class server:
    def __init__(self, host1, port1, host2, port2, host3, port3, log_name):
        # host1 and port1 are for this server
        self.host1 = host1
        self.port1 = port1
        self.host2 = host2
        self.port2 = port2
        self.host3 = host3
        self.port3 = port3
        self.log_name = log_name

        # used whenever a data structure gets updated
        self.ds_lock = threading.Lock()
        # list of tuples: (host, port, msg)
        self.network_queue = []
        self.clock_rate = random.randint(1, 6)
        # initialize the logic clock to be at time 0
        self.clock = 0

        # START 3 THREADS HERE: ONE FOR LISTENING TO HOST2/PORT2, ONE FOR LISTENING TO HOST3/PORT3, AND ONE PROCESS THREAD

    def listening(self, host, port):
        # logic for the threads that listen to other servers and updates network queue
        pass
    
    def process(self):
        # all logic for reading queue/doing shit
        pass

def main():
	args = sys.argv[1:]
	assert len(sys.argv) == 2, f"provide host address"
	
	host = args[0]
	port = 49153
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket binded to port", port)

	# put the socket into listening mode - we accept everything, so no need to specify a backlog
	s.listen()
	print("socket is listening")

	# a forever loop until client wants to exit
	while True:
		# establish connection with client
		c, addr = s.accept()

		print('Connected to :', addr[0], ':', addr[1])

		# Start a new thread
		start_new_thread(threaded, (c,))


if __name__ == '__main__':
	main()