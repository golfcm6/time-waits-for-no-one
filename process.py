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

LOG_FILE_NAME_PREFIX = 'machine_log_'

PROCESS_NAMES = ['a', 'b', 'c']

class Process:
	def __init__(self, host_ip, name):
		assert name in PROCESS_NAMES
		self.name = name
		self.log_file_name = LOG_FILE_NAME_PREFIX + name + '.txt'
		with open(self.log_file_name, 'w') as log:
			log.write(f'  E  |  M  |           Time           | Q | Clock\n')

		self.host_ip = host_ip
		self.network_queue_lock = threading.Lock()
		self.network_queue = [] # list of tuples: (host, port, msg)
		self.clock_rate = randint(1, 6)
		self.single_clock_tick_length = 1 / self.clock_rate
		print(f'The clock rate is {self.clock_rate}\n')
		# initialize the logic clock to be at time 0
		self.clock = 0

		self.sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(2)]
		self.socket_names = []

		# setup sockets dependent on process name
		# our convention depends on knowing if this is server A, B, or C:
		# - if A, you create socket to B and C (bind call + listen)
		# - if B, you create socket to C and connect to A
		# - if C, you just connect to existing A and B sockets
		# A must be made before B, B must be made before C
		if name == 'a':
			self.handle_sockets(listen_ports = [PORT_A_B, PORT_A_C])
			self.socket_names = ['b', 'c']

		elif name == 'b':
			self.handle_sockets(listen_ports = [PORT_B_C], connect_ports = [(PORT_A_B, 'a')])
			self.socket_names = ['a', 'c']
		
		else:
			self.handle_sockets(connect_ports = [(PORT_A_C, 'a'), (PORT_B_C, 'b')])
			self.socket_names = ['a', 'b']

	# bind and listen to listen_ports and try connecting to connect_ports
	def handle_sockets(self, listen_ports = [], connect_ports = []):
		# there should be exactly one fewer port than the number of processes
		assert len(listen_ports) + len(connect_ports) == len(PROCESS_NAMES) - 1
		i = 0
		for port in listen_ports:
			self.sockets[i].bind((self.host_ip, port))
			self.sockets[i].listen()
			i += 1
		for port, process_name in connect_ports:
			try:
				self.sockets[i].connect((self.host_ip, port))
				print(f'Connected to machine {process_name}')
			except:
				print(f'Could not connect to machine {process_name}, check status')
				raise ConnectionError
			i += 1

	# logic for the threads that listen to other servers and update network queue
	def listen(self, s):
		while True: 
			data = s.recv(1024)
			# if this socket is not receiving any info, then close the socket
			if not data:
				s.close()
				break

			data = data.decode('ascii')

			# sender is the machine the message originated from (a, b, c)
			# msg is the logical time of the sender (int)
			sender, msg = data[:1], int(data[1:])

			# add this message to the local network queue
			with self.network_queue_lock:
				self.network_queue.append((sender, msg))

	# send a message via all requested sockets
	def send_message(self, sockets):
		for socket in sockets:
			socket.send((self.name + str(self.clock)).encode('ascii'))

	# accept connections from all processes that were initialized after this process
	def accept_connections(self, process_names):
		for i, name in enumerate(process_names):
			print(f'Waiting on machine {name}, please wait ...')
			conn, _ = self.sockets[i].accept()
			print(f'Connected to {name}')
			self.sockets[i] = conn

	# run a single clock tick
	def one_tick(self):
		while True:
			start_time = time.time()
			with open(self.log_file_name, 'a') as log:
				# handle case with nonempty queue
				if self.network_queue:
					with self.network_queue_lock:
						msg = self.network_queue.pop(0)

					# msg[0] is sender name, msg[1] is sender time
					# logical clock update rule
					self.clock = max(self.clock, msg[1]) + 1
					log.write(f'read |  {msg[0]}  | {time.ctime()} | {len(self.network_queue)} | {self.clock}\n')
				# handle case with empty queue
				else:
					curr_op = randint(1, 10)

					# send message to socket 0
					if curr_op == 1:
						self.send_message([self.sockets[0]])
						self.clock += 1
						log.write(f'send |  {self.socket_names[0]}  | {time.ctime()} | - | {self.clock}\n')
					# send message to socket 1
					elif curr_op == 2:
						self.send_message([self.sockets[1]])
						self.clock += 1
						log.write(f'send |  {self.socket_names[1]}  | {time.ctime()} | - | {self.clock}\n')
					# send message to both socket 0 and socket 1
					elif curr_op == 3:
						self.send_message(self.sockets)
						self.clock += 1
						log.write(f'send | {" ".join(self.socket_names)} | {time.ctime()} | - | {self.clock}\n')
					else:
						self.clock += 1
						log.write(f'int  | --- | {time.ctime()} | - | {self.clock}\n')
			time.sleep(self.single_clock_tick_length - (time.time() - start_time))

def main():
	args = sys.argv[1:]
	assert len(args) == 2, 'Please provide host_ip and process name as arguments'
	machine_name = args[1]
	process = Process(*args)


	if machine_name == 'a':
		process.accept_connections(['b', 'c'])
	
	elif machine_name == 'b':
		process.accept_connections(['c'])

	for socket in process.sockets:
		start_new_thread(process.listen, (socket, ))

	while True:
		process.one_tick()


if __name__ == '__main__':
	main()
