import socket
import pigpio
import time
import threading
import queue  # Queue to handle input lag and prevent runaway actions
from getIpAddr import get_local_ip
import sys

# =================== GPIO Configuration ===================
SERVO_PIN = 26  # GPIO pin for connected servo
ESC_PIN = 19    # GPIO pin for connected ESC

FREQ_SERVO = 100  # Servo frequency (Standard for servos)
FREQ_ESC = 100    # ESC frequency (Match your ESC calibration)

# Servo PWM Duty Cycle Range (Microseconds)TODO: find true center
MIN_DUTY_SERVO = 900   # Leftmost position in µs
MAX_DUTY_SERVO = 2100  # Rightmost position in µs 
NEUTRAL_SERVO = 1500   # Center position in µs

# ESC PWM Duty Cycle Range (Microseconds)
MIN_DUTY_ESC = 1310    # Minimum throttle
MAX_DUTY_ESC = 1750    # Maximum throttle
NEUTRAL_DUTY_ESC = 1500  # Neutral position

STEP_SERVO = 30  # Step size for smoother servo movement (µs)
STEP_ESC = 10    # Step size for smoother ESC control (µs)

COMMAND_TIMEOUT = 0.5  # If no command received for 500 ms, stop the car
DELAY = 0.02  # Small delay for smooth movement

# =================== Initialize pigpio ===================
pi = pigpio.pi()
if not pi.connected:
    print("ERROR: pigpio daemon is not running!")
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

print(f"INFO: Servo & ESC Server Listening on {HOST}:{PORT}")

# Store current pulse width values
current_servo_pw = NEUTRAL_SERVO
current_esc_pw = NEUTRAL_DUTY_ESC

# Command queue to resolve input lag and runaway actions
command_queue = queue.Queue()

# Timestamp of last received command
last_command_time = time.time()

# =================== Control Vehicle Using match-case ===================
def control_vehicle(command):
    """ Adjusts both the throttle and steering based on the command """
    global current_servo_pw, current_esc_pw, last_command_time

    last_command_time = time.time()  # Update timestamp on valid command

    target_esc_pw = current_esc_pw
    target_servo_pw = current_servo_pw

    match command:
        # ESC (Throttle) Control
        case "UP":
            target_esc_pw = min(MAX_DUTY_ESC, current_esc_pw + STEP_ESC)
        case "DOWN":
            target_esc_pw = max(MIN_DUTY_ESC, current_esc_pw - STEP_ESC)
        case "NEUTRAL":
            target_esc_pw = NEUTRAL_DUTY_ESC

        # Servo (Steering) Control
        case "LEFT":
            target_servo_pw = min(MAX_DUTY_SERVO, current_servo_pw + STEP_SERVO)
        case "RIGHT":
            target_servo_pw = max(MIN_DUTY_SERVO, current_servo_pw - STEP_SERVO)
        case "CENTER":
            target_servo_pw = NEUTRAL_SERVO  # Reset servo to center

        # Handle simultaneous servo & throttle movements
        case "LEFTUP":
            target_servo_pw = min(MAX_DUTY_SERVO, current_servo_pw + STEP_SERVO)
            target_esc_pw = min(MAX_DUTY_ESC, current_esc_pw + STEP_ESC)
        case "LEFTDOWN":
            target_servo_pw = min(MAX_DUTY_SERVO, current_servo_pw + STEP_SERVO)
            target_esc_pw = max(MIN_DUTY_ESC, current_esc_pw - STEP_ESC)
        case "RIGHTUP":
            target_servo_pw = max(MIN_DUTY_SERVO, current_servo_pw - STEP_SERVO)
            target_esc_pw = min(MAX_DUTY_ESC, current_esc_pw + STEP_ESC)
        case "RIGHTDOWN":
            target_servo_pw = max(MIN_DUTY_SERVO, current_servo_pw - STEP_SERVO)
            target_esc_pw = max(MIN_DUTY_ESC, current_esc_pw - STEP_ESC)

        # Unknown Commands
        case _:
            print(f"WARNING: Unrecognized command '{command}'. Ignoring...")
            return  # Ignore invalid commands

    # Smooth transition for both ESC and Servo
    while abs(current_esc_pw - target_esc_pw) > 1 or abs(current_servo_pw - target_servo_pw) > 1:
        if current_esc_pw < target_esc_pw:
            current_esc_pw += STEP_ESC
        elif current_esc_pw > target_esc_pw:
            current_esc_pw -= STEP_ESC

        if current_servo_pw < target_servo_pw:
            current_servo_pw += STEP_SERVO
        elif current_servo_pw > target_servo_pw:
            current_servo_pw -= STEP_SERVO

        # **Update both ESC and Servo at the same time**
        pi.set_servo_pulsewidth(ESC_PIN, current_esc_pw)
        pi.set_servo_pulsewidth(SERVO_PIN, current_servo_pw)

        print(f"INFO: ESC: {current_esc_pw} µs | Servo: {current_servo_pw} µs")

        time.sleep(DELAY)  # Smooth movement

# =================== Handle Client Connection ===================
def handle_client(conn):
    """ Handles a single client connection """
    try:
        while True:
            data = conn.recv(1024).decode('utf8').strip()

            # Handle disconnection
            if not data:
                print("INFO: Client disconnected.")
                break

            print(f"INFO: Received Command: {data}")

            # Add to queue to process in main loop (fixes input lag)
            command_queue.put(data)

            # Handle DISCONNECT command
            if data == "DISCONNECT":
                print("INFO: Client requested disconnection. Shutting down server.")
                server_socket.close()
                pi.set_servo_pulsewidth(ESC_PIN, NEUTRAL_DUTY_ESC)
                pi.set_servo_pulsewidth(SERVO_PIN, NEUTRAL_SERVO)
                pi.stop()
                sys.exit()
                exit(1)

    except Exception as e:
        print(f"ERROR: Client connection error: {e}")
    finally:
        conn.close()

# =================== Start Server in a Thread ===================
def start_server():
    while True:
        conn, addr = server_socket.accept()
        print(f"INFO: Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.daemon = True  # Closes thread when the main program exits
        client_thread.start()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# =================== Process Input Queue & Prevent Runaway Actions ===================
try:
    while True:
        # Process commands from the queue
        while not command_queue.empty():
            command = command_queue.get()
            control_vehicle(command)

        # If no command is received within `COMMAND_TIMEOUT`, reset to neutral
        if time.time() - last_command_time > COMMAND_TIMEOUT:
            if current_esc_pw != NEUTRAL_DUTY_ESC or current_servo_pw != NEUTRAL_SERVO:
                print("WARNING: No input received. Resetting to NEUTRAL for safety.")
                pi.set_servo_pulsewidth(ESC_PIN, NEUTRAL_DUTY_ESC)
                pi.set_servo_pulsewidth(SERVO_PIN, NEUTRAL_SERVO)
                current_esc_pw = NEUTRAL_DUTY_ESC
                current_servo_pw = NEUTRAL_SERVO

        time.sleep(0.01)  # Prevent CPU overload while polling

except KeyboardInterrupt:
    print("\nINFO: Exiting...")

finally:
    pi.set_servo_pulsewidth(ESC_PIN, NEUTRAL_DUTY_ESC)
    pi.set_servo_pulsewidth(SERVO_PIN, NEUTRAL_SERVO)
    time.sleep(2)
    pi.stop()  # Close pigpio connection
    server_socket.close()
    sys.exit()
