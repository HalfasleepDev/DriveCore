#TODO: WORKS!!
import socket

HOST = '192.168.0.102' # Enter IP or Hostname of your server
PORT = 4444 # Pick an open Port (1000+ recommended), must match the server port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

#Lets loop awaiting for your input
while True:
	command = input('Enter your command: ')
	s.send(command.encode())
	reply = s.recv(1024)
	if reply.decode() == 'Terminate':
		break
	print(reply.decode())