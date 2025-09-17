# Final Pi Script: Acts as UDP Server, streams video and IMU after host sends data

import socket
import struct
import time
import json
import cv2
import numpy as np
from picamera2 import Picamera2
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

# === Config ===
VIDEO_PORT = 5005
IMU_PORT = 5006
JPEG_QUALITY = 70
MAX_PACKET_SIZE = 1024

# === Setup camera ===
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
picam2.start()

# === Setup IMU ===
mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_250,
    afs=AFS_2G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ
)
mpu.configure()

# === Setup sockets ===
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
imu_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

video_sock.bind(("", VIDEO_PORT))
imu_sock.bind(("", IMU_PORT))

video_sock.settimeout(0.1)
imu_sock.settimeout(0.1)

# === Wait for host to contact ===
print("Waiting for host to contact video port...")
while True:
    try:
        _, addr = video_sock.recvfrom(1024)
        HOST_IP = addr[0]
        break
    except socket.timeout:
        continue

print(f"Connected to host at {HOST_IP}. Beginning stream...")

frame_id = 0
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]

while True:
    # === Capture and encode frame ===
    frame = picam2.capture_array()
    _, jpeg = cv2.imencode('.jpg', frame, encode_param)
    jpeg_bytes = jpeg.tobytes()

    frame_id += 1
    total_packets = len(jpeg_bytes) // MAX_PACKET_SIZE + 1
    for i in range(total_packets):
        chunk = jpeg_bytes[i * MAX_PACKET_SIZE:(i + 1) * MAX_PACKET_SIZE]
        header = struct.pack("HHH", frame_id, i, total_packets)
        video_sock.sendto(header + chunk, (HOST_IP, VIDEO_PORT))

    # === Send IMU Data ===
    imu_data = {
        "timestamp": time.time(),
        "accel": mpu.readAccelerometerMaster(),
        "gyro": mpu.readGyroscopeMaster(),
        "mag": mpu.readMagnetometerMaster()
    }
    imu_json = json.dumps(imu_data).encode("utf-8")
    imu_sock.sendto(imu_json, (HOST_IP, IMU_PORT))

    time.sleep(0.03)  # ~30 FPS
