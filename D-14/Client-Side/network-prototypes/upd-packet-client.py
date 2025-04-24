from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage, QKeyEvent
from PySide6.QtCore import QTimer, Qt
import socket
import struct
import sys
import cv2
import numpy as np
import json
import time
import threading
from queue import Queue  

from udpProtocolClient import (credential_packet, version_request_packet, 
                               setup_request_packet, send_tune_data_packet,
                               current_time, keyboard_command_packet)

#TODO:
'''
- [x] Create a command file
- [x] brodcast
- [X] HandShake
- [x] Commands
- [x] Video
'''

# ------ Network Settings ------
BROADCAST_PORT = 9999
CHUNK_SIZE = 1024
BUFFER_SIZE = 65536

server_ip = None
video_port = None
control_port = None
handshake_done = threading.Event()

# ------ Temp Variables ------
# --- Credentials --- 
username = "test"
password = "123"
# --- Version ---
client_ver = "1.3"
supported_ver = ["1.3"]
# --- PWM Tune Settings ---
MIN_DUTY_SERVO = 900   # Leftmost position in µs
MAX_DUTY_SERVO = 2100  # Rightmost position in µs 
NEUTRAL_SERVO = 1500   # Center position in µs

MIN_DUTY_ESC = 1310    # Minimum throttle
MAX_DUTY_ESC = 1750    # Maximum throttle
NEUTRAL_DUTY_ESC = 1500  # Neutral position
BRAKE_ESC = 1470     # Should trigger the brake in the esc
# --- Vehicle Setup ---
control_scheme = str
vehicle_model = str

# ------- Control setup ------
command_queue = Queue()
MAX_RETRIES = 3

# ====== Discover Broadcast ======
def discover_host():
    global server_ip, video_port, control_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT)) #'<broadcast>'
    print("[Broadcast]: Listening for broadcast...")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            payload = json.loads(data.decode())
            if payload.get("type") == "advertise":
                server_ip = addr[0]
                video_port = payload.get("video_port")
                control_port = payload.get("control_port")
                print(f"[Broadcast]: Found host: {server_ip}, Video: {video_port}, Control: {control_port}")
                break
        except ConnectionRefusedError:
            print("[Broadcast] ConnectionRefusedError")

    sock.close()

# ------ Preform Handshake ------
def perform_handshake():
    handshake_status = True

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)

    def send(payload):
        sock.sendto(json.dumps(payload).encode(), (server_ip, control_port))

    pending_action = "send_credentials"

    while (not handshake_done.is_set()) & handshake_status:

        if pending_action == "send_credentials":
            send(credential_packet(username, password))
            pending_action = None

        elif pending_action == "auth_failed":
            #! Error message
            print("[Handshake][Error]: authentication failed")
            handshake_status = False
            pending_action = None
        
        elif pending_action == "version_request":
            send(version_request_packet(client_ver))
            pending_action = None
        
        elif pending_action == "version_request_failed":
            #! Error message
            print("[Handshake][Error]: Incompatable Host Ver")
            handshake_status = False
            pending_action = None

        elif pending_action == "send_client_version_failed":
            #! Error message
            print("[Handshake][Error]: Incompatable Client Ver")
            handshake_status = False
            pending_action = None
        
        elif pending_action == "setup_request":
            send(setup_request_packet())
            pending_action = None

        elif pending_action == "send_tune_data":
            send(send_tune_data_packet("handshake", MIN_DUTY_SERVO, MAX_DUTY_SERVO, NEUTRAL_SERVO, 
                                       MIN_DUTY_ESC, MAX_DUTY_ESC, NEUTRAL_DUTY_ESC, BRAKE_ESC))
            pending_action = None

        elif pending_action == "handshake_complete":
            #* Done message
            print("[Handshake]: handshake is complete")
            print(f"[Status]: Successfully connected to {vehicle_model}")
            print(f"[Status]: Using {control_scheme} control scheme")
            pending_action = None
            handshake_status = False
            handshake_done.set()
            

        '''elif pending_action == "":
            pending_action = None'''
        
        # TODO: add other actions
        
        # === Inbound messages ===
        try:
            data, _ = sock.recvfrom(2048)
            payload = json.loads(data.decode())
            pending_action = handle_server_response(payload)

        except socket.timeout:
            print("Waiting for server...")
            continue
    sock.close()

def handle_server_response(payload):
    global vehicle_model, control_scheme
    # ------ Authentication ------
    if payload.get("type") == "auth_status":
        if payload.get("status"):
            #* Done message
            print("[Handshake]: Authentication succsessful")
            return "version_request"                                #* <--- pass
        else:
            return "auth_failed"
    
    # ------ Check Version Compatability ------
    elif payload.get("type") == "version_info":
        if payload.get("client_compatablity"):
            # grab host ver here
            #* Done message
            print("[Handshake]: Client is compatable")
            if payload.get("host-version") in supported_ver:
                #* Done message
                print("[Handshake]: Host is compatable")
                return "setup_request"                              #* <--- pass
            else:
                return "version_request_failed"
        else:
            return "send_client_version_failed"
    # ------ Gather Vehicle Setup Info ------
    elif payload.get("type") == "setup_info":
        vehicle_model = payload.get("vehicle_model")
        control_scheme = payload.get("control_scheme")
        #* Done message
        print("[Handshake]: Gathered vehicle setup info")
        return "send_tune_data"                                     #* <--- pass
    
    elif payload.get("type") == "handshake_complete":
        if payload.get("status"):
            return "handshake_complete"                             #* <--- pass
        
    elif payload.get("type") == "":
        return

def send_command(cmd: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)

    packet = keyboard_command_packet(cmd)
    sock.sendto(json.dumps(packet).encode(), (server_ip, control_port))

    try:
        data, _ = sock.recvfrom(1024)
        ack = json.loads(data.decode())
        now = current_time()
        delay = now - ack["timestamp"]
        print(f"ACK: {ack['command']} | RTT: {delay}ms")
    except socket.timeout:
        print("No ACK for command:", cmd)
    sock.close()

class DriveCoreUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore Client")
        self.setFocusPolicy(Qt.StrongFocus)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.frame_chunks = []
        self.total_chunks = 0
        self.current_chunks = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

        self.last_frame_time = time.time()
        self.frame_counter = 0
        self.fps = 0
        self.last_video_latency_ms = 0
        self.last_frame_timestamp = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_video)
        self.timer.start(1)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_W:
            send_command("UP")
        elif key == Qt.Key_S:
            send_command("DOWN")
        elif key == Qt.Key_A:
            send_command("LEFT")
        elif key == Qt.Key_D:
            send_command("RIGHT")
        elif key == Qt.Key_Space:
            send_command("BRAKE")

    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        if key in [Qt.Key_W, Qt.Key_S]:
            send_command("NEUTRAL")
        elif key in [Qt.Key_A, Qt.Key_D]:
            send_command("CENTER")

    def receive_video(self):
        try:
            while True:
                data, _ = self.sock.recvfrom(BUFFER_SIZE)

                # === HEADER PACKET (contains JSON: chunks + timestamp) ===
                try:
                    header = json.loads(data.decode())
                    self.total_chunks = header["chunks"]
                    self.last_frame_timestamp = header["timestamp"]
                    self.frame_chunks = []
                    self.current_chunks = 0
                    continue  # Don't count header as chunk
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass  # Not a JSON header → it's a frame chunk

                # === FRAME CHUNKS ===
                self.frame_chunks.append(data)
                self.current_chunks += 1

                 # === Drop frame if excessive chunks ===
                if self.current_chunks > self.total_chunks:
                    print("⚠️ Dropping overdue frame")
                    self.frame_chunks.clear()
                    self.current_chunks = 0

                # === Display full frame ===
                if self.current_chunks == self.total_chunks:
                    frame_data = b''.join(self.frame_chunks)

                    now = int(time.time() * 1000)
                    self.last_video_latency_ms = now - self.last_frame_timestamp

                    self.display_frame(frame_data)

                    self.frame_chunks = []
                    self.current_chunks = 0

        except BlockingIOError:
            pass

    def display_frame(self, data):
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            # === FPS calculation ===
            self.frame_counter += 1
            now = time.time()
            elapsed = now - self.last_frame_time
            if elapsed >= 1.0:
                self.fps = self.frame_counter / elapsed
                self.frame_counter = 0
                self.last_frame_time = now

            # === Overlay text ===
            overlay = f"FPS: {self.fps:.1f} | Latency: {self.last_video_latency_ms} ms"
            cv2.putText(img, overlay, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # === Show frame ===
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    discover_host()
    perform_handshake()
    handshake_done.wait()
    app = QApplication(sys.argv)
    client = DriveCoreUI()
    client.sock.bind(("", video_port))
    client.show()
    sys.exit(app.exec())
