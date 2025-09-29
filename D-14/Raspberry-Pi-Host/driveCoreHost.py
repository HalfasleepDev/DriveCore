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
import pigpio
from threading import Event

from driveCoreNetwork import NetworkManager

from coreFunctions import load_settings, save_settings

# ====== NETWORK ======
VIDEO_PORT = 5555
CONTROL_PORT = 4444
BROADCAST_PORT = 9999
CHUNK_SIZE = 2048 #1024

# ------ NETWORK STATES ------
handshake_complete = threading.Event()
client_ip = None
handshake_status = True

# ------ LATENCY ------
TIMEOUT_MS = 500
last_timestamp = None

COMMAND_TIMEOUT = 0.5
DELAY = 0.02


class DriveCoreHost:
    # ====== Program Config ======
    HOST_VER = "1.3.0"
    SUPPORTED_VER = ["1.3.0"]

    # ====== Vehicle Config ======
    VEHICLE_MODEL = "D-14"
    CONTROL_SCHEME = "wasd"

    SERVO_PIN = 26          # GPIO pin for connected servo
    ESC_PIN = 19            # GPIO pin for connected ESC
    FLOOD_LIGHT_PIN = 12    # GPIO pin for connected Flood Light Leds

    FREQ_SERVO = 100  # Servo frequency (Standard for servos)
    FREQ_ESC = 100    # ESC frequency (Match your ESC calibration)

    # ====== Settings Path ======
    SETTINGS_FILE = "/home/halfdev/DriveCore/settings.json"

    def __init__(self):
        # === Settings ===
        self.settings = load_settings(self.SETTINGS_FILE)

        self.handshake_complete = threading.Event()

        self.pi = pigpio.pi()
        #self.setup_pigpio()

        self.network = NetworkManager(self)

        self.restart_flag = Event()

        # ====== PWM Duty Cycles ======
        self.min_duty_servo = self.settings["min_duty_servo"]
        self.max_duty_servo = self.settings["max_duty_servo"]
        self.neutral_servo = self.settings["neutral_duty_servo"]
        self.min_duty_esc = self.settings["min_duty_esc"]
        self.max_duty_esc = self.settings["max_duty_esc"]
        self.neutral_duty_esc = self.settings["neutral_duty_esc"]
        self.brake_esc = self.settings["brake_esc"]

        self.current_esc_pw = self.neutral_duty_esc
        self.current_servo_pw = self.neutral_servo

        # ====== Drive Assist ======
        self.emergency_active = False
        self.emergency_trigger_time = time.time()

        # ====== Heartbeat ======
        self.last_seen_timestamp = time.time()
        self.client_online = False


    def setup_pigpio(self, mode=None):
        if not self.pi.connected:
            print("ERROR: pigpio daemon is not running!")
            exit(1)
        if mode == "FLASH":
            self.pi.set_mode(self.FLOOD_LIGHT_PIN, pigpio.OUTPUT)               # Setup Flood lights
        else:
            # Set initial values for servo and ESC
            self.pi.set_servo_pulsewidth(self.SERVO_PIN, self.neutral_servo)    # Start at center
            self.pi.set_servo_pulsewidth(self.ESC_PIN, self.neutral_duty_esc)   # Start ESC at neutral
            self.pi.set_mode(self.FLOOD_LIGHT_PIN, pigpio.OUTPUT)               # Setup Flood lights
    
    def reset_pwm(self):
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, self.neutral_servo)    # Start at center
        self.pi.set_servo_pulsewidth(self.ESC_PIN, self.neutral_duty_esc)   # Start ESC at neutral
        self.pi.write(self.FLOOD_LIGHT_PIN, 0)                              # Turn of Flood Light

    # === Mapping Helpers ===
    def map_throttle(self, intensity, forward=True):
        if forward:
            return int(self.neutral_duty_esc + (self.max_duty_esc - self.neutral_duty_esc) * intensity)
        else:
            return int(self.neutral_duty_esc - (self.neutral_duty_esc - self.min_duty_esc) * intensity)

    '''
    def map_steering(self, current_esc_pwm, k_p=1.0):
        """
        Calculate steering PWM based on current ESC PWM.
        
        Assumes:
        - Neutral ESC = center point
        - Max/Min ESC = full motion extremes
        """
         # Calculate normalized "ESC error"
        if current_esc_pwm > self.neutral_duty_esc:
            # Moving forward
            max_range = self.max_duty_esc - self.neutral_duty_esc
            esc_error = (current_esc_pwm - self.neutral_duty_esc) / max_range
        else:
            # Moving backward or braking
            min_range = self.neutral_duty_esc - self.min_duty_esc
            esc_error = (current_esc_pwm - self.neutral_duty_esc) / min_range
        # Proportional control
        correction = -k_p * esc_error

        # Clamp correction
        correction = max(min(correction, 1.0), -1.0)

        if correction >= 0:
            # Steer right
            pwm = self.neutral_servo - (self.neutral_servo - self.min_duty_servo) * correction
        else:
            # Steer left
            pwm = self.neutral_servo + (self.max_duty_servo - self.neutral_servo) * abs(correction)

        return int(pwm)
    '''
    
    def map_steering(self, intensity, left=True):
        if left:
            return int(self.neutral_servo + (self.max_duty_servo - self.neutral_servo) * intensity)
        else:
            return int(self.neutral_servo - (self.neutral_servo - self.min_duty_servo) * intensity)
        
    def run(self):
        while True:
            print("Starting system...")
            self._start_system()

            while self.client_online:
                time.sleep(0.5)

            print("Client disconnected — restarting system...")
            self._stop_system()  # Clean shutdown
    
    def _start_system(self):
        #self.network.reset_connection_state()  # clear timestamps, flags

        # === Start broadcast ===
        threading.Thread(target=self.network.broadcast_ip, daemon=True).start()

        # === Start handshake ===
        self.network.listen_for_handshake()
        self.handshake_complete.wait()

        # === Start subsystems ===
        # Heartbeat thread
        threading.Thread(target=self.network.listen_for_heartbeats, daemon=True).start()
        threading.Thread(target=self.network.heartbeat_watchdog, daemon=True).start()

        # Command listener thread
        threading.Thread(target=self.network.command_listener, daemon=True).start()

        # Video stream thread
        threading.Thread(target=self.network.video_stream, daemon=True).start()

    def _stop_system(self):
        self.handshake_complete.clear()
        self.client_online = False
        self.network.handshake_status = False
        self.restart_flag.clear()
        time.sleep(1)
        # Close sockets, reset values, etc.

        
    '''def run(self):
        # Broadcast
        threading.Thread(target=self.network.broadcast_ip, daemon=True).start()

        # Handshake
        self.network.listen_for_handshake()
        self.handshake_complete.wait()

        # Start heartbeat thread
        threading.Thread(target=self.network.listen_for_heartbeats, daemon=True).start()
        threading.Thread(target=self.network.heartbeat_watchdog, daemon=True).start()

        # Start command listener thread
        threading.Thread(target=self.network.command_listener, daemon=True).start()

        # Start the video stream thread
        threading.Thread(target=self.network.video_stream(), daemon=True).start()'''
        
    def shutdown(self):
        self.reset_pwm()
        self.pi.stop()
        
if __name__ == "__main__":
    try:
        host = DriveCoreHost()
        host.run()
    except KeyboardInterrupt:
        host.shutdown()
