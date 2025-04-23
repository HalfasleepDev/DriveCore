import socket
import json

BROADCAST_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', BROADCAST_PORT))

print("Listening for host broadcast...")
while True:
    data, addr = sock.recvfrom(1024)
    try:
        payload = json.loads(data.decode())
        if payload.get("type") == "advertise":
            print(f"Host discovered at {addr[0]} | Video: {payload['video_port']} | Control: {payload['control_port']}")
    except Exception as e:
        print("Invalid broadcast:", e)