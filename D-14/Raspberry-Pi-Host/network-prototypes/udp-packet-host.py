import socket
import json
import struct
import threading
import time
import io
from picamera2 import Picamera2
from PIL import Image               # pillow

from udpProtocolHost import (broadcast_packet)

#TODO:
'''
- [x] Create a command file
- [x] brodcast
- [X] HandShake
- [ ] Commands
- [ ] Video
'''

# === CONFIG ===
VIDEO_PORT = 5555
CONTROL_PORT = 4444
BROADCAST_PORT = 9999
CHUNK_SIZE = 1024

HOST = "0.0.0.0" # get_local_ip

client_ip = None
handshake_complete = threading.Event()

# === ADVERTISE HOST IP ===
def broadcast_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while not handshake_complete.is_set():
        #message = json.dumps({"type": "advertise", "video_port": VIDEO_PORT, "control_port": CONTROL_PORT})
        message = json.dumps(broadcast_packet(VIDEO_PORT, CONTROL_PORT))
        sock.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))
        time.sleep(1)

# === HANDLE HANDSHAKE LOGIC ===
def handle_handshake(sock, addr, payload):
    global client_ip
    client_ip = addr[0]

    if payload.get("type") == "credentials":
        print(f"🔐 Received credentials from {addr}")
        sock.sendto(json.dumps({"type": "auth_status", "status": "ok"}).encode(), addr)

    elif payload.get("type") == "version_request":
        sock.sendto(json.dumps({"type": "version_info", "host_version": "1.0.2"}).encode(), addr)
        time.sleep(0.1)
        sock.sendto(json.dumps({"type": "request_client_version"}).encode(), addr)

    elif payload.get("type") == "client_version":
        print(f"📦 Client version: {payload['version']}")

    elif payload.get("type") == "setup_request":
        print(f"⚙️ Received setup from {addr}: {payload}")
        sock.sendto(json.dumps({"type": "setup_confirmed", "ready": True}).encode(), addr)
        handshake_complete.set()

# === HANDLE POST-HANDSHAKE COMMANDS ===
def handle_control(sock, addr, payload):
    if payload.get("type") == "command":
        command = payload["command"]
        print(f"🚗 Command received: {command}")

        # TODO: Add actual ESC/servo logic here

        ack = {
            "type": "command_ack",
            "command": command,
            "timestamp": payload.get("timestamp"),
            "status": "executed"
        }
        sock.sendto(json.dumps(ack).encode(), addr)

# === COMMAND RECEIVER ===
def command_listener():
    global client_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, CONTROL_PORT))
    print("Listening for control commands...")

    while True:
        data, addr = sock.recvfrom(2048)
        try:
            payload = json.loads(data.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON from {addr}")
            continue

        if not handshake_complete.is_set():
            handle_handshake(sock, addr, payload)
        else:
            handle_control(sock, addr, payload)

# === VIDEO STREAMING ===
def video_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"format": "RGB888", "size": (1280, 720)})
    picam2.configure(config)
    picam2.start()
    print(f"Starting video stream to {client_ip}")

    while handshake_complete.is_set():
        frame = picam2.capture_array()
        stream = io.BytesIO()
        Image.fromarray(frame).save(stream, format='JPEG', quality=50)
        data = stream.getvalue()
        total = len(data)
        n_chunks = (total + CHUNK_SIZE - 1) // CHUNK_SIZE
        sock.sendto(struct.pack("!I", n_chunks), (client_ip, VIDEO_PORT))
        for i in range(n_chunks):
            chunk = data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            sock.sendto(chunk, (client_ip, VIDEO_PORT))

# === MAIN ===
if __name__ == "__main__":
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=command_listener, daemon=True).start()
    handshake_complete.wait()
    video_stream()
