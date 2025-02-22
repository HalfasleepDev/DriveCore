#WORKS!!

import socket

HOST = '192.168.0.102' # Server IP or Hostname
PORT = 4444 # Pick an open Port (1000+ recommended), must match the client sport
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#managing error exception
try:
	s.bind((HOST, PORT))
except socket.error:
	print ('Bind failed ')


s.listen(1)
print('Socket awaiting messages')
conn, addr = s.accept()
print('Connected')

# awaiting for message
while True:
	data = conn.recv(1024)
	print ('I sent a message back in response to: ', data.decode())
	reply = ''

    # process your message
	if data.decode() == 'Hello':
		reply = 'Hi, back!'
	elif data.decode() == 'This is important':
		reply = 'OK, I have done the important thing you have asked me!'

	#and so on and on until...
	elif data.decode() == 'quit':
		conn.send('Terminating')
		break
	else:
		reply = 'Unknown command'

	# Sending reply
	conn.send(reply.encode())
conn.close() # Close connections