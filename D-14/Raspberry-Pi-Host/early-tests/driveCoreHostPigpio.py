import socket
import pigpio  # Replaces RPi.GPIO
import time
import threading
from getIpAddr import get_local_ip

# =================== GPIO Configuration ===================
SERVO_PIN = 26  # GPIO pin for connected servo
ESC_PIN = 19    # GPIO pin for connected ESC

FREQ_SERVO = 100  # Servo frequency (Standard for servos)
FREQ_ESC = 100    # ESC frequency (Match your ESC calibration)

# Servo PWM Duty Cycle Range (Microseconds)
MIN_DUTY_SERVO = 900   # Leftmost position in µs
MAX_DUTY_SERVO = 2100  # Rightmost position in µs
NEUTRAL_SERVO = 1500   # Center position in µs

# ESC PWM Duty Cycle Range (Microseconds)
MIN_DUTY_ESC = 1310    # Minimum throttle
MAX_DUTY_ESC = 1750    # Maximum throttle
NEUTRAL_DUTY_ESC = 1500  # Neutral position

STEP_SERVO = 10  # Step size for smoother servo movement (µs)
STEP_ESC = 10    # Step size for smoother ESC control (µs)

DELAY = 0.02  # Small delay for smooth movement

# =================== Initialize pigpio ===================
pi = pigpio.pi()
if not pi.connected:
    print("pigpio daemon is not running!")
    exit(1)

# Set initial values for servo and ESC
pi.set_servo_pulsewidth(SERVO_PIN, NEUTRAL_SERVO)  # Start at center
pi.set_servo_pulsewidth(ESC_PIN, NEUTRAL_DUTY_ESC)  # Start ESC at neutral

# =================== Socket Configuration ===================
HOST = get_local_ip()
PORT = 4444

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servo & ESC Server Listening on {HOST}:{PORT}")

# Store current pulse width values
current_servo_pw = NEUTRAL_SERVO
current_esc_pw = NEUTRAL_DUTY_ESC

# =================== ESC Control Function ===================
def adjust_throttle(command):
    global current_esc_pw

    target_pw = current_esc_pw

    if command == "UP" and current_esc_pw < MAX_DUTY_ESC:
        target_pw = min(MAX_DUTY_ESC, current_esc_pw + STEP_ESC)
    elif command == "DOWN" and current_esc_pw > MIN_DUTY_ESC:
        target_pw = max(MIN_DUTY_ESC, current_esc_pw - STEP_ESC)
    elif command == "NEUTRAL":
        target_pw = NEUTRAL_DUTY_ESC

    # Smooth transition
    while abs(current_esc_pw - target_pw) > 1:
        if current_esc_pw < target_pw:
            current_esc_pw += STEP_ESC
        elif current_esc_pw > target_pw:
            current_esc_pw -= STEP_ESC
        pi.set_servo_pulsewidth(ESC_PIN, current_esc_pw)
        print(f"ESC Throttle set to {current_esc_pw} µs")
        time.sleep(DELAY)

# =================== Servo Control Function ===================
def move_servo(command):
    global current_servo_pw

    if command == "LEFT" and current_servo_pw > MIN_DUTY_SERVO:
        current_servo_pw -= STEP_SERVO
    elif command == "RIGHT" and current_servo_pw < MAX_DUTY_SERVO:
        current_servo_pw += STEP_SERVO

    pi.set_servo_pulsewidth(SERVO_PIN, current_servo_pw)
    print(f"Servo moved to {current_servo_pw} µs")

# =================== Handle Client Connection ===================
def handle_client(conn):
    """ Handles a single client connection """
    try:
        while True:
            data = conn.recv(1024).decode('utf8').strip()
            if not data:
                break
            print(f"Received: {data}")
            move_servo(data)
            adjust_throttle(data)
    except Exception as e:
        print(f"Client connection error: {e}")
    finally:
        conn.close()

# =================== Start Server in a Thread ===================
def start_server():
    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.daemon = True  # Closes thread when the main program exits
        client_thread.start()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the main thread alive

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pi.set_servo_pulsewidth(ESC_PIN, NEUTRAL_DUTY_ESC)
    pi.set_servo_pulsewidth(SERVO_PIN, NEUTRAL_SERVO)
    time.sleep(2)
    pi.stop()  # Close pigpio connection
    server_socket.close()
