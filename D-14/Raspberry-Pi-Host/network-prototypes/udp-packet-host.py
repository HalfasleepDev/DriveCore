import socket
import json
import struct
import threading
import time
import io
import cv2
from picamera2 import Picamera2
from PIL import Image               # pillow
import numpy as np

from udpProtocolHost import (broadcast_packet, auth_status_packet, version_info_packet,
                             setup_info_packet, handshake_complete_packet, current_time, 
                             keyboard_command_ack_packet, frame_ack_packet)

#TODO:
'''
- [x] Create a command file
- [x] brodcast
- [X] HandShake
- [x] Commands
- [x] Video
'''

# === CONFIG ===
VIDEO_PORT = 5555
CONTROL_PORT = 4444
BROADCAST_PORT = 9999
CHUNK_SIZE = 1024

handshake_complete = threading.Event()
client_ip = None
handshake_status = True
client_ip = None
handshake_complete = threading.Event()

TIMEOUT_MS = 500
last_timestamp = None
# ------ Temp Variables ------
# --- Credentials --- 
USERNAME = "test"
PASSWORD = "123"
# --- Version ---
host_ver = "1.3"
supported_ver = ["1.3"]
# --- Vehicle Info ---
vehicle_model = "D-14"
control_scheme = "wasd"
# --- PWM Tune Settings ---
# TODO: change to global?
MIN_DUTY_SERVOt = 900   # Leftmost position in µs
MAX_DUTY_SERVOt = 2100  # Rightmost position in µs 
NEUTRAL_SERVOt = 1500   # Center position in µs

MIN_DUTY_ESCt = 1310    # Minimum throttle
MAX_DUTY_ESCt = 1750    # Maximum throttle
NEUTRAL_DUTY_ESCt = 1500  # Neutral position
BRAKE_ESCt = 1470     # Should trigger the brake in the esc


# === ADVERTISE HOST IP ===
def broadcast_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = json.dumps(broadcast_packet(VIDEO_PORT, CONTROL_PORT))
    while not handshake_complete.is_set():
        sock.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))
        print("Broadcasting...")
        time.sleep(1)

# === HANDLE HANDSHAKE LOGIC ===
def listen_for_handshake():
    global client_ip, handshake_status
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", CONTROL_PORT))
    print("Waiting for client handshake...")

    def send(payload, addr):
        sock.sendto(json.dumps(payload).encode(), addr)

    while (not handshake_complete.is_set()) and handshake_status:

        data, addr = sock.recvfrom(1024)
        payload = json.loads(data.decode())

        payloadType = payload.get("type")

        if payloadType == "credentials":
            print(f"[Handshake]: Credentials received from {addr}: {payload}")
            client_ip = addr[0]
            send(auth_status_packet(handle_client_response(payload)), addr)
            '''response = {"type": "auth_status", "status": "ok"}
            sock.sendto(json.dumps(response).encode(), addr)
            handshake_complete.set()
            break'''
        elif payloadType == "version_request":
            print(f"[Handshake]: Client version recieved from {addr}: {payload}")
            send(version_info_packet(host_ver, handle_client_response(payload)), addr)
        
        elif payloadType == "setup_request":
            print(f"[Handshake]: Setup request recieved from {addr}: {payload}")
            send(setup_info_packet(vehicle_model, control_scheme), addr)
        
        elif payloadType == "handshake_tune_setup":
            print(f"[Handshake]: Applying tune setup from {addr}: {payload}")
            apply_tune(payload)
            send(handshake_complete_packet(True), addr)
            handshake_complete.set()

# === Handle Client responces ===
def handle_client_response(payload):
    if payload.get("type") == "credentials":
        if (payload.get("username") != USERNAME) and (payload.get("password") != PASSWORD):
            print("[Handshake]: Invalid credentials.")
            return False
        else:
            return True
    elif payload.get("type") == "version_request":
        if payload.get("client_ver") in supported_ver:
            return True
        else:
            return False

    elif payload.get("type") == "":
        return
    elif payload.get("type") == "":
        return
    elif payload.get("type") == "":
        return

# === apply vehicle tune ===
def apply_tune(payload):
    global MIN_DUTY_SERVOt, MAX_DUTY_SERVOt, NEUTRAL_SERVOt, MIN_DUTY_ESCt, MAX_DUTY_ESCt, NEUTRAL_DUTY_ESCt, BRAKE_ESCt

    if payload.get("type") == "handshake_tune_setup":
        MIN_DUTY_SERVOt = payload.get("min_duty_servo")       # Leftmost position in µs
        MAX_DUTY_SERVOt = payload.get("max_duty_servo")       # Rightmost position in µs 
        NEUTRAL_SERVOt = payload.get("neutral_duty_servo")        # Center position in µs

        MIN_DUTY_ESCt = payload.get("min_duty_esc")         # Minimum throttle
        MAX_DUTY_ESCt = payload.get("max_duty_esc")         # Maximum throttle
        NEUTRAL_DUTY_ESCt = payload.get("neutral_duty_esc")     # Neutral position
        BRAKE_ESCt = payload.get("brake_esc")            # Should trigger the brake in the esc

# === HANDLE POST-HANDSHAKE COMMANDS ===
def handle_control(sock, addr, payload):
    global last_timestamp
    now = current_time()
    incoming_time = payload.get("timestamp")
    command = payload.get("command")

    if last_timestamp is not None:
        gap = now - last_timestamp
        if gap > TIMEOUT_MS:
            print(f"Delay > {TIMEOUT_MS}ms: {gap}ms since last packet")
    last_timestamp = now

    print(f"Command: {command} | From: {addr} | Time diff: {now - incoming_time}ms")

    ack = keyboard_command_ack_packet(command)
    sock.sendto(json.dumps(ack).encode(), addr)

# === COMMAND RECEIVER ===
def command_listener():
    global client_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", CONTROL_PORT))
    print("Listening for control commands...")

    while True:
        data, addr = sock.recvfrom(1024)
        payload = json.loads(data.decode())
        payloadType = payload.get("type")

        if payloadType == "keyboard_command":
            handle_control(sock, addr, payload)
        else:
            pass

# === VIDEO STREAMING ===
'''def video_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"format": "XRGB8888", "size": (1280, 720)})
    picam2.configure(config)
    picam2.start()
    print(f"Starting video stream to {client_ip}")

    while handshake_complete.is_set():
        frame = picam2.capture_array()
        stream = io.BytesIO()
        #Image.fromarray(frame).save(stream, format='JPEG', quality=50)
        im = Image.fromarray(frame)
        rgb_im = im.convert('RGB')
        rgb_im.save(stream, format='JPEG', quality=50)
        data = stream.getvalue()
        total = len(data)
        n_chunks = (total + CHUNK_SIZE - 1) // CHUNK_SIZE
        timestamp = int(time.time() * 1000)  # ms
        header = json.dumps({
            "chunks": n_chunks,
            "timestamp": timestamp
        }).encode()
        sock.sendto(header, (client_ip, VIDEO_PORT))
        #header = json.dumps(frame_ack_packet(n_chunks)).encode
        #sock.sendto(header, (client_ip, VIDEO_PORT))
        #sock.sendto(struct.pack("!I", n_chunks), (client_ip, VIDEO_PORT))
        for i in range(n_chunks):
            chunk = data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            sock.sendto(chunk, (client_ip, VIDEO_PORT))
'''
def video_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"format": "RGB888", "size": (1280, 720)},
        controls={"FrameRate": 60}
    )
    picam2.configure(config)
    picam2.start()

    print(f"Streaming video to {client_ip}:{VIDEO_PORT}")

    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
        data = buffer.tobytes()

        timestamp = int(time.time() * 1000)
        header = json.dumps({
            "chunks": (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE,
            "timestamp": timestamp
        }).encode()
        sock.sendto(header, (client_ip, VIDEO_PORT))

        for i in range(0, len(data), CHUNK_SIZE):
            sock.sendto(data[i:i + CHUNK_SIZE], (client_ip, VIDEO_PORT))

# === MAIN ===
if __name__ == "__main__":
    threading.Thread(target=broadcast_ip, daemon=True).start()
    listen_for_handshake()
    handshake_complete.wait()
    threading.Thread(target=command_listener, daemon=True).start()
    
    video_stream()
