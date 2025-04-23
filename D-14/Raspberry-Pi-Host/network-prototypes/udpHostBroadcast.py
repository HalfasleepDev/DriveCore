import socket
import json
import time

BROADCAST_PORT = 9999
VIDEO_PORT = 5555
CONTROL_PORT = 4444

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

message = {
    "type": "advertise",
    "video_port": VIDEO_PORT,
    "control_port": CONTROL_PORT
}

print("Broadcasting every second... (Ctrl+C to stop)")
while True:
    sock.sendto(json.dumps(message).encode(), ('<broadcast>', BROADCAST_PORT))
    time.sleep(1) 