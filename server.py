import socket
from _thread import start_new_thread
import threading
import sys

from random import randint
import time

# def the three ports for different machines to establish connection with each other
PORT_A_B = 49151
PORT_A_C = 49152
PORT_B_C = 49153

LOG_PREFIX = "machine_log_"

class Server:
	def __init__(self, hostIP, name):

		# our convention depends on knowing if this is server A, B, or C:
		# - if A, you create socket to B and C (bind call + listen)
		# - if B, you create socket to C and connect to A
		# - if C, you just connect to existing A and B sockets

		# A must be made before B, B must be made before C
		self.name = name

		self.my_log = open(LOG_PREFIX + name + ".txt", "w")

		self.hostIP = hostIP
		
		# used whenever a data structure gets updated
		self.ds_lock = threading.Lock()
		# list of tuples: (host, port, msg)
		self.network_queue = []
		self.clock_rate = randint(1, 6)
		print(self.clock_rate)
		# initialize the logic clock to be at time 0
		self.clock = 0


		self.socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#TODO: sync with charles code, want variables for the names of socket_1 and socket_2, for the logs
		self.socket_1_name = ''
		self.socket_2_name = ''

		if name == "a":
			# set up two new sockets

			# socket for a <> b
			self.socket_1.bind((hostIP, PORT_A_B))
			self.socket_1.listen()

			# socket for a <> c
			self.socket_2.bind((hostIP, PORT_A_C))
			self.socket_2.listen()

			self.socket_1_name = "b"
			self.socket_2_name = "c"

		elif name == "b":
			# connect to existing socket for machine a
			try:
				# socket for a <> b
				self.socket_1.connect((hostIP, PORT_A_B))
				print("connected to machine a")
			except:
				print("could not connect to machine a, check status")
				assert False
			
			# socket for b <> c
			self.socket_2.bind((hostIP, PORT_B_C))
			self.socket_2.listen()

			self.socket_1_name = "a"
			self.socket_2_name = "c"
		
		else:
			try:
				# socket for a <> c
				self.socket_1.connect((hostIP, PORT_A_C))
				print("connected to machine a")
			except:
				print("could not connect to machine a, check status")
				assert False

			try:
				# socket for b <> c
				self.socket_2.connect((hostIP, PORT_B_C))
				print("connected to machine b")
			except:
				print("could not connect to machine b, check status")
				assert False
			
			self.socket_1_name = "a"
			self.socket_2_name = "b"
		

	def listening(self, s):
		# logic for the threads that listen to other servers and updates network queue
		# this depends on if self.name is A, B, or C (you either bind or connect)
		while True: 
			thread_input = s.recv(1024)
			# if this socket not receiving any info, close the socket
			if not thread_input:
				s.close()
				break

			thread_input = thread_input.decode("ascii")

			# sender is the machine the message originated from (a, b, c)
			# msg is the logical time of the sender (int)
			sender, msg = thread_input[:1], int(thread_input[1:])

			self.ds_lock.acquire()
			# add this message to the local network queue
			self.network_queue.append((sender, msg))
			self.ds_lock.release()




	def process(self):
		while True:
			# mimic doing self.clock_rate things per second with a 1 second sleep call at the start, then do the logic
			# time.sleep(1)
			# number of instructions completed thus far - stop when we hit clock_rate
			curr_count = 0

			while curr_count < self.clock_rate:
				self.my_log.close()
				self.my_log = open(LOG_PREFIX + self.name + ".txt", "a")
				# msgs in queue
				if self.network_queue != []:
					self.ds_lock.acquire()
					msg = self.network_queue.pop(0)
					self.ds_lock.release()

					# msg[0] is sender name, msg[1] is sender time
					# logical clock update rule
					self.clock = max(self.clock, msg[1]) + 1
					self.my_log.write('r|' + msg[0] + ' | ' + time.ctime() + ' | ' + str(len(self.network_queue)) + ' | ' + str(self.clock) + '\n')
				# no queue msg
				else:
					curr_op = randint(1, 10)

					# send message to socket_1
					if curr_op == 1:
						self.socket_1.send((self.name + str(self.clock)).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_1_name + ' | ' + time.ctime() + ' | ' + str(self.clock) + '\n')
					# send message to socket_2
					elif curr_op == 2:
						self.socket_2.send((self.name + str(self.clock)).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_2_name + ' | ' + time.ctime() + ' | ' + str(self.clock) + '\n')
					# send message to both socket_1 and socket_2
					elif curr_op == 3:
						self.socket_1.send((self.name + str(self.clock)).encode("ascii"))
						# time.sleep(0.0001)
						self.socket_2.send((self.name + str(self.clock)).encode("ascii"))
						self.clock += 1
						self.my_log.write('s|' + self.socket_1_name + self.socket_2_name + ' | ' + time.ctime() + ' | ' + str(self.clock) + '\n')
					else:
						self.clock += 1
						self.my_log.write('i' + ' | ' + time.ctime() + ' | ' + str(self.clock) + '\n')
					
				curr_count += 1
				time.sleep(1/self.clock_rate)



def main():
	args = sys.argv[1:]
	print(args)

	assert len(args) == 2, "provide hostIP, name"
	assert args[1] == "a" or args[1] == "b" or args[1] == "c", "machine must be named a, b, or c"

	machine_name = args[1]
	me = Server(args[0], args[1])


	if machine_name == "a":
		print("waiting on machine b, please wait ...")
		c, _ = me.socket_1.accept()
		print("connected to b")
		me.socket_1 = c

		print("waiting on machine c, please wait ...")
		c2, _ = me.socket_2.accept()
		print("connected to c")
		me.socket_2 = c2
	
	elif machine_name == "b":
		print("waiting on machine c, please wait ...")
		c, _ = me.socket_2.accept()
		print("connected to c")
		me.socket_2 = c


	start_new_thread(me.listening, (me.socket_1, ))
	start_new_thread(me.listening, (me.socket_2, ))
	start_new_thread(me.process, ())
	while True:
		continue



if __name__ == '__main__':
	main()
