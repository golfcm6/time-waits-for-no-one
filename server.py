import socket
from _thread import start_new_thread
import threading
import sys
import random
import time

class Server:
	def __init__(self, host1, port1, host2, port2, host3, port3, log_name, name):
		# host1 and port1 are for this server
		self.host1 = host1
		self.port1 = port1
		self.host2 = host2
		self.port2 = port2
		self.host3 = host3
		self.port3 = port3
		self.my_log = open(log_name, "a")
		self.name = name

		# used whenever a data structure gets updated
		self.ds_lock = threading.Lock()
		# list of tuples: (host, port, msg)
		self.network_queue = []
		self.clock_rate = random.randint(1, 6)
		# initialize the logic clock to be at time 0
		self.clock = 0

		# our convention depends on knowing if this is server A, B, or C:
		# - if A, you create socket to B and C (bind call + listen)
		# - if B, you create socket to C and connect to A
		# - if C, you just connect to existing A and B sockets

		# A must be made before B, B must be made before C

		self.socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#TODO: sync with charles code, want variables for the names of socket_1 and socket_2, for the logs
		self.socket_1_name = ''
		self.socket_2_name = ''
	
		# START 3 THREADS HERE: ONE FOR LISTENING TO HOST2/PORT2, ONE FOR LISTENING TO HOST3/PORT3, AND ONE PROCESS THREAD

		

	def listening(self, s):
		# logic for the threads that listen to other servers and updates network queue
		# this depends on if self.name is A, B, or C (you either bind or connect)
		while True: 
			c, addr = s.accept()    

	def process(self):
		while True:
			# mimic doing self.clock_rate things per second with a 1 second sleep call at the start, then do the logic
			time.sleep(1)
			# number of instructions completed thus far - stop when we hit clock_rate
			curr_count = 0

			while curr_count < self.clock_rate:
				# msgs in queue
				if self.network_queue != []:
					self.ds_lock.acquire()
					msg = self.network_queue.pop(0)
					self.ds_lock.release()

					# msg[0] is sender name, msg[1] is sender time
					# logical clock update rule
					self.clock = max(self.clock, msg[1]) + 1

					self.my_log.write('r|' + msg[0] + ' | ' + time.asctime() + ' | ' + len(self.network_queue) + ' | ' + str(self.clock) + '\n')
				
				# no queue msg
				else:
					curr_op = random.randint(1, 10)

					# send message to socket_1
					if curr_op == 1:
						self.socket_1.send(self.name + str(self.clock).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_1_name + ' | ' + time.asctime() + ' | ' + str(self.clock) + '\n')
					# send message to socket_2
					elif curr_op == 2:
						self.socket_2.send(self.name + str(self.clock).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_2_name + ' | ' + time.asctime() + ' | ' + str(self.clock) + '\n')
					# send message to both socket_1 and socket_2
					elif curr_op == 3:
						self.socket_1.send(self.name + str(self.clock).encode("ascii"))
						self.socket_2.send(self.name + str(self.clock).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_1_name + self.socket_2_name + ' | ' + time.asctime() + ' | ' + str(self.clock) + '\n')
					else:
						self.clock += 1
						self.my_log.write('i' + ' | ' + time.asctime() + ' | ' + str(self.clock) + '\n')
					
				curr_count += 1



def main():
	args = sys.argv[1:]
	assert len(sys.argv) == 8, f"provide h1, p1, h2, p2, h3, p3, file_name, name"
	
	this_server = Server(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])


if __name__ == '__main__':
	main()
