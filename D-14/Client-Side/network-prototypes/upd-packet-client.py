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

BROADCAST_PORT = 9999
CHUNK_SIZE = 1024
BUFFER_SIZE = 65536

server_ip = None
video_port = None
control_port = None
handshake_done = threading.Event()

def discover_host():
    global server_ip, video_port, control_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            payload = json.loads(data.decode())
            if payload.get("type") == "advertise":
                server_ip = addr[0]
                video_port = payload.get("video_port")
                control_port = payload.get("control_port")
                print(f"Discovered host at {server_ip}")
                break
        except:
            continue
    sock.close()

def perform_handshake():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)

    def send(payload):
        sock.sendto(json.dumps(payload).encode(), (server_ip, control_port))

    send({"type": "credentials", "username": "greg", "password": "secure123"})
    time.sleep(0.2)
    send({"type": "version_request"})
    time.sleep(0.2)
    send({"type": "client_version", "version": "1.0.0"})
    time.sleep(0.2)
    send({
        "type": "setup_request",
        "vehicle_model": "RCX-7",
        "control_scheme": "WASD",
        "num_cameras": 1,
        "num_sensors": 2,
        "sensor_types": ["lidar", "imu"],
        "local_processing": True,
        "https_cam_addr": "http://192.168.0.5/cam"
    })

    handshake_done.set()
    sock.close()

def send_command(cmd: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    packet = {
        "type": "command",
        "command": cmd,
        "assist": None,
        "timestamp": int(time.time() * 1000)
    }
    try:
        sock.sendto(json.dumps(packet).encode(), (server_ip, control_port))
        data, _ = sock.recvfrom(1024)
        ack = json.loads(data.decode())
        print(f"✅ Command ACK: {ack}")
    except socket.timeout:
        print("⚠️ No ACK for command:", cmd)
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
                if len(data) == 4:
                    self.total_chunks = struct.unpack("!I", data)[0]
                    self.frame_chunks = []
                    self.current_chunks = 0
                else:
                    self.frame_chunks.append(data)
                    self.current_chunks += 1
                    if self.current_chunks == self.total_chunks:
                        frame_data = b''.join(self.frame_chunks)
                        self.display_frame(frame_data)
                        self.frame_chunks = []
                        self.current_chunks = 0
        except BlockingIOError:
            pass

    def display_frame(self, data):
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
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
