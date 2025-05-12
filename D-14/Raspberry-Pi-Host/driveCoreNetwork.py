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
import os

from threading import Event

from udpHostProtocols import (broadcast_packet, auth_status_packet, version_info_packet,
                             setup_info_packet, handshake_complete_packet, current_time, 
                             keyboard_command_ack_packet, frame_ack_packet, last_ack_packet)

from coreFunctions import load_settings, save_settings

class NetworkManager:
    #cwd = os.getcwd
    # ====== Settings Path ======
    SETTINGS_FILE =  "/home/halfdev/DriveCore/settings.json"

    # ====== NETWORK ======
    VIDEO_PORT = 5555
    CONTROL_PORT = 4444
    BROADCAST_PORT = 9999
    HEARTBEAT_PORT = 8888 #TODO: Finish heartbeat/pulse system

    CHUNK_SIZE = 1024 #1024
    
    HEARTBEAT_TIMEOUT = 6.0  # seconds
    TIMEOUT_MS = 200

    def __init__(self, core):
        self.core = core

        # === Settings ===
        self.settings = load_settings(self.SETTINGS_FILE)

        self.username = self.settings["username"]
        self.password = self.settings["password"]


        self.client_ip = None
        self.handshake_status = False

        # === Latency ===
        self.last_timestamp = None
        self.last_command_time = time.time()

        # === Heartbeat ===
        self.heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.heartbeat_socket.bind(("0.0.0.0", self.HEARTBEAT_PORT))
        self.heartbeat_socket.settimeout(2.0) #0.5

    # === ADVERTISE HOST IP ===
    def broadcast_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = json.dumps(broadcast_packet(self.VIDEO_PORT, self.CONTROL_PORT, self.HEARTBEAT_PORT))
        while not self.core.handshake_complete.is_set():
            sock.sendto(message.encode(), ('<broadcast>', self.BROADCAST_PORT))
            print("Broadcasting...")
            time.sleep(3)
        sock.close()
    
    # === HANDLE HANDSHAKE LOGIC ===
    def listen_for_handshake(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.CONTROL_PORT))
        print("Waiting for client handshake...")

        def send(payload, addr):
            sock.sendto(json.dumps(payload).encode(), addr)

        while (not self.core.handshake_complete.is_set()) and (not self.handshake_status):

            data, addr = sock.recvfrom(1024)
            payload = json.loads(data.decode())

            payloadType = payload.get("type")
            time.sleep(3)

            if payloadType == "credentials":
                print(f"[Handshake]: Credentials received from {addr}: {payload}")
                self.client_ip = addr[0]
                send(auth_status_packet(self.handle_client_response(payload)), addr)
                '''response = {"type": "auth_status", "status": "ok"}
                sock.sendto(json.dumps(response).encode(), addr)
                handshake_complete.set()
                break'''
            elif payloadType == "version_request":
                print(f"[Handshake]: Client version recieved from {addr}: {payload}")
                send(version_info_packet(self.core.HOST_VER, self.handle_client_response(payload)), addr)
            
            elif payloadType == "setup_request":
                print(f"[Handshake]: Setup request recieved from {addr}: {payload}")
                send(setup_info_packet(self.core.VEHICLE_MODEL, self.core.CONTROL_SCHEME), addr)
            
            elif payloadType == "handshake_tune_setup":
                print(f"[Handshake]: Applying tune setup from {addr}: {payload}")
                self.apply_tune(payload)
                send(handshake_complete_packet(True), addr)
                self.handshake_status = True
                self.core.client_online = True
                #sock.close()
                self.core.handshake_complete.set()

    # === Handle Client responces ===
    def handle_client_response(self, payload):
        if payload.get("type") == "credentials":
            if (payload.get("username") != self.username) and (payload.get("password") != self.password):
                print("[Handshake]: Invalid credentials.")
                self.handshake_status = False
                return False
            else:
                return True
        elif payload.get("type") == "version_request":
            if payload.get("client_ver") in self.core.SUPPORTED_VER:
                return True
            else:
                self.handshake_status = False
                print("[Handshake]: Incompatable client ver")
                return False

        elif payload.get("type") == "":
            return
        elif payload.get("type") == "":
            return
        elif payload.get("type") == "":
            return
    
    # === apply vehicle tune ===
    def apply_tune(self, payload):
        type = payload.get("type")

        if type == "handshake_tune_setup":
            
            self.core.min_duty_servo = payload.get("min_duty_servo")
            self.core.max_duty_servo = payload.get("max_duty_servo")
            self.core.neutral_servo = payload.get("neutral_duty_servo")
            self.core.min_duty_esc = payload.get("min_duty_esc")
            self.core.max_duty_esc = payload.get("max_duty_esc")
            self.core.neutral_duty_esc = payload.get("neutral_duty_esc")
            self.core.brake_esc = payload.get("brake_esc")

            self.settings["min_duty_servo"] = self.core.min_duty_servo
            self.settings["max_duty_servo"] = self.core.max_duty_servo
            self.settings["neutral_duty_servo"] = self.core.neutral_servo
            self.settings["min_duty_esc"] = self.core.min_duty_esc
            self.settings["max_duty_esc"] = self.core.max_duty_esc
            self.settings["neutral_duty_esc"] = self.core.neutral_duty_esc
            self.settings["brake_esc"] = self.core.brake_esc

            save_settings(self.settings, self.SETTINGS_FILE)
            self.settings = load_settings(self.SETTINGS_FILE)

            # Print The New Values Of The Duties
            print(f"Servo:\nMax Duty{self.core.max_duty_servo}\nMin Duty{self.core.min_duty_servo}\nNeutral Duty{self.core.neutral_servo}\n")
            print(f"Esc:\nMax Duty{self.core.max_duty_esc}\nMin Duty{self.core.min_duty_esc}\nNeutral Duty{self.core.neutral_duty_esc}\nBrake{self.core.brake_esc}")

            # Set Pi gpio
            self.core.setup_pigpio()
        
        
        elif type == "sent_tune":
            match payload.get("action"):
                # Test for midpoint of the servo
                case "servo_mid_cal":
                    print("sevo test")
                    servo_test = payload.get("servo")

                    # Set to desired point
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, servo_test)

                    time.sleep(0.01)

                    # Turn off servo for jitter
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, 0)

                case "save_mid_servo":
                    servo_mid = payload.get("servo")

                    # Set to desired point
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, servo_mid)

                    # Save everywhere
                    #self.settings["neutral_duty_servo"] = servo_mid
                    self.core.neutral_servo = servo_mid

                    # Save to Json
                    #TODO: Uncomment if it works
                    #save_settings(self.settings, self.SETTINGS_FILE)
                    #self.settings = load_settings(self.SETTINGS_FILE)

                case "test_servo":
                    servo_left = payload.get("left")
                    servo_center = payload.get("center")
                    servo_right = payload.get("right")

                    time.sleep(1)
                    # Set to the MIN pos
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, servo_left)
                    #Wait
                    time.sleep(1)
                    # Set to the CENTER pos
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, servo_center)
                    # Wait
                    time.sleep(1)
                    # Set to the MAX pos
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, servo_right)
                    time.sleep(1)
                    # Reset to center
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.neutral_servo)
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, 0)

                case "save_servo":
                    servo_left = payload.get("left")
                    servo_center = payload.get("center")
                    servo_right = payload.get("right")

                    # Save everywhere
                    self.core.neutral_servo = servo_center
                    self.core.min_duty_servo = servo_left
                    self.core.max_duty_servo = servo_right

                    self.settings["min_duty_servo"] = servo_left
                    self.settings["max_duty_servo"] = servo_right
                    self.settings["neutral_duty_servo"] = servo_center

                    # Save to Json
                    #TODO: Uncomment if it works
                    #save_settings(self.settings, self.SETTINGS_FILE)
                    #self.settings = load_settings(self.SETTINGS_FILE)

                case "test_esc":
                    esc_min = payload.get("min")
                    esc_neutral = payload.get("neutral")
                    esc_max = payload.get("max")
                    esc_brake = payload.get("brake")

                    print(payload)
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, 0)
                    # WAIT
                    time.sleep(1)
                    # TESTING REVERSE
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, esc_min)
                    # WAIT
                    time.sleep(2)
                    # RETURN TO NEUTRAL
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, esc_neutral)
                    # WAIT
                    time.sleep(1)
                    # TESTING MAX ACCELERATION
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, esc_max) 
                    # WAIT
                    time.sleep(2)
                    # TESTING BRAKE
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, esc_brake)
                    # WAIT
                    time.sleep(2)
                    # RETURN TO SELF NEUTRAL
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.neutral_duty_esc)

                case "save_esc":
                    esc_min = payload.get("min")
                    esc_neutral = payload.get("neutral")
                    esc_max = payload.get("max")
                    esc_brake = payload.get("brake")

                    # Save everywhere
                    self.core.min_duty_esc = esc_min
                    self.core.max_duty_esc = esc_max
                    self.core.neutral_duty_esc =esc_neutral
                    self.core.brake_esc = esc_brake

                    self.settings["min_duty_esc"] = esc_min
                    self.settings["max_duty_esc"] = esc_max
                    self.settings["neutral_duty_esc"] = esc_neutral
                    self.settings["brake_esc"] = esc_brake

                    # Save to Json
                    #TODO: Uncomment if it works
                    #save_settings(self.settings, self.SETTINGS_FILE)
                    #self.settings = load_settings(self.SETTINGS_FILE)

                case "":
                    pass
    
    # === COMMAND RECEIVER ===
    def command_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.CONTROL_PORT))
        print("Listening for control commands...")

        while True:
            data, addr = sock.recvfrom(1024)
            payload = json.loads(data.decode())
            payloadType = payload.get("type")

            if payloadType == "keyboard_command":
                self.handle_control(sock, addr, payload)
            elif payloadType == "drive_assist_command":
                self.handle_control(sock, addr, payload)
            elif payloadType == "sent_tune":
                self.apply_tune(payload)
            elif payloadType == "shutdown_systems":
                self.send_last_ack(sock, addr)
                self.core.shutdown()
            else:
                pass

    # === HANDLE KEYBOARD INPUTS ===
    def handle_control(self, sock, addr, payload):
        #global last_timestamp, last_command_time, current_esc_pw, current_servo_pw
        now = int(time.time() * 1000)
        incoming_time = payload.get("timestamp")
        command = payload.get("command")
        esc_intensity = payload.get("esc_intensity", 0.0)
        servo_intensity = payload.get("servo_intensity", 0.0)
        #last_command_time = time.time()

        if self.last_timestamp is not None:
            gap = now - self.last_timestamp
            if gap > self.TIMEOUT_MS:
                print(f"Delay > {self.TIMEOUT_MS}ms: {gap}ms since last packet")

                if self.core.current_esc_pw != self.core.neutral_duty_esc:
                    self.core.current_esc_pw = self.core.neutral_duty_esc
                    self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                    command = "NEUTRAL"

                if self.core.current_servo_pw != self.core.neutral_servo:
                    self.core.current_servo_pw = self.core.neutral_servo
                    self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)
                    command = "CENTER"
            time.sleep(0.01)
        
        elif self.core.emergency_active:
            if time.time() - self.core.emergency_trigger_time > 3.0:
                self.core.emergency_active = False
                print("Emergency cleared, ready for control.")
        
        if self.core.emergency_active and command  == "EMERGENCY_STOP":
            print("Ignored command during emergency:", command)
            ack = keyboard_command_ack_packet("Ignored command during emergency", self.core.current_esc_pw, self.core.current_servo_pw)
        
        #TODO match case
        else:
            if command == "UP":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=True)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.smooth_servo_center()

            elif command == "DOWN":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=False)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.smooth_servo_center()

            elif command == "LEFT":
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=True)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.neutral_duty_esc)

            elif command == "RIGHT":
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=False)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.neutral_duty_esc)

            elif command == "LEFTUP":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=True)
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=True)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)

            elif command == "LEFTDOWN":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=False)
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=True)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)

            elif command == "RIGHTUP":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=True)
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=False)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)

            elif command == "RIGHTDOWN":
                self.core.current_esc_pw = self.core.map_throttle(esc_intensity, forward=False)
                self.core.current_servo_pw = self.core.map_steering(servo_intensity, left=False)
                #self.core.current_servo_pw = self.core.map_steering(self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)

            elif command == "BRAKE":
                self.core.current_esc_pw = self.core.brake_esc
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)

            elif command == "NEUTRAL":
                self.core.current_esc_pw = self.core.neutral_duty_esc
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)

            elif command == "CENTER":
                self.core.current_servo_pw = self.core.neutral_servo
                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)

            elif command == "EMERGENCY_STOP":
                self.core.current_esc_pw = self.core.brake_esc
                self.core.current_servo_pw = self.core.neutral_servo

                self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                time.sleep(0.1)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                time.sleep(0.1)
                self.core.pi.set_servo_pulsewidth(self.core.ESC_PIN, self.core.current_esc_pw)
                
                
                self.core.emergency_active = True
                self.core.emergency_trigger_time = time.time()
            
            elif command == "CLEAR_EMERGENCY":
                self.core.emergency_active = False
                print("Emergency cleared manually.")
            
            print(f"Command: {command} | ESC: {self.core.current_esc_pw} | SERVO: {self.core.current_servo_pw} | From: {addr} | Time diff: {now - incoming_time}ms")
            ack = keyboard_command_ack_packet(command, self.core.current_esc_pw, self.core.current_servo_pw)

        self.last_timestamp = now
        sock.sendto(json.dumps(ack).encode(), addr)
    
    def send_last_ack(self, sock, addr):
        ack = last_ack_packet("Shutdown initiated")
        sock.sendto(json.dumps(ack).encode(), addr)
        sock.close()
    
    def smooth_servo_center(self, base_step=5, base_delay=0.005):
        """
        Gradually move the servo back to the neutral position.
        - step_size: PWM microseconds per adjustment
        - delay: seconds between each adjustment step
        """
        distance = abs(self.core.current_servo_pw - self.core.neutral_servo)
        steps = max(1, distance // base_step)

        for _ in range(int(steps)):
            if self.core.current_servo_pw < self.core.neutral_servo:
                self.core.current_servo_pw += base_step
                self.core.current_servo_pw = min(self.core.current_servo_pw, self.core.neutral_servo)
            else:
                self.core.current_servo_pw -= base_step
                self.core.current_servo_pw = max(self.core.current_servo_pw, self.core.neutral_servo)

            self.core.pi.set_servo_pulsewidth(self.core.SERVO_PIN, self.core.current_servo_pw)
            time.sleep(base_delay)
    
    def listen_for_heartbeats(self):
        while True:
            try:
                data, addr = self.heartbeat_socket.recvfrom(1024)
                payload = json.loads(data.decode())
                if payload.get("type") == "heartbeat":
                    self.core.last_seen_timestamp = time.time()

            except socket.timeout:
                continue

            except Exception as e:
                print(f"[Heartbeat] Error: {e}")

    def heartbeat_watchdog(self):
        while not self.core.restart_flag.is_set():
            self.core.restart_flag.wait(8.0)
            self.core.restart_flag.set()
            print("done")
            
        while self.core.restart_flag.is_set():
            now = time.time()

            if now - self.core.last_seen_timestamp > self.HEARTBEAT_TIMEOUT:
                if self.core.client_online:
                    print("Client disconnected. Restarting broadcast or handshake...")
                    self.core.client_online = False # Should break the run() loop

            else:
                if not self.core.client_online:
                    print("Client connection re-established.")
                    self.core.client_online = True

            time.sleep(2)

    def video_stream(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536) #65536

        picam2 = Picamera2()
        config = picam2.create_video_configuration(
            main={"format": "XRGB8888", "size": (1280, 720)}, 
            lores=None,    # no low-res stream
            raw=None,      # no raw output request
            controls={"FrameRate": 60.0}
        )
        picam2.configure(config)
        picam2.start(show_preview=False)

        print(f"Streaming video to {self.client_ip}:{self.VIDEO_PORT}")

        try:
            while True and self.core.client_online:
                frame = picam2.capture_array()
                _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
                data = buffer.tobytes()

                timestamp = int(time.time() * 1000)

                header = json.dumps({
                    "chunks": (len(data) + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
                    "timestamp": timestamp
                }).encode()

                sock.sendto(header, (self.client_ip, self.VIDEO_PORT))

                for i in range(0, len(data), self.CHUNK_SIZE):
                    sock.sendto(data[i:i + self.CHUNK_SIZE], (self.client_ip, self.VIDEO_PORT))


        except Exception as e:
            print(f"Video stream error: {e}")
        
        finally:
            picam2.stop()
            picam2.close()
            sock.close()
            print("Video stream stopped cleanly.")