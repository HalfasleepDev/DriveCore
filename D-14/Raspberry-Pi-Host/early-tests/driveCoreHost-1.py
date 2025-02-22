import socket
import RPi.GPIO as GPIO
import time
import threading
from getIpAddr import get_local_ip

# GPIO Configuration
SERVO_PIN = 26  # GPIO pin for connected servo
ESC_PIN = 19    # GPIO pin for connected esc (WARNING!! CALIBRATE ESC FIRST)
FREQ = 100  # Adjust as needed

# Servo PWM Duty Cycle Range
MIN_DUTY_SERVO = 9  # Leftmost position
MAX_DUTY_SERVO = 21  # Rightmost position

STEP = 0.1  # Step size for duty cycle changes
DELAY = 0.05  # Small delay for smooth movement

# ESC PWM Duty Cycle Range
MIN_DUTY_ESC = 13.1  # Minimum throttle
MAX_DUTY_ESC = 17.5  # Maximum throttle
NEUTRAL_DUTY = 15  # Neutral position

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(ESC_PIN, GPIO.OUT)

# Initialize PWM
pwmServo = GPIO.PWM(SERVO_PIN, FREQ)
pwmServo.start(15)  # Start at center (15%)
pwmEsc = GPIO.PWM(ESC_PIN, FREQ)
pwmEsc.start(NEUTRAL_DUTY)  # Start in neutral

# Command Filter

# Socket Configuration
HOST = get_local_ip()
PORT = 4444

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servo Server Listening on {HOST}:{PORT}")

# Store current duty cycles
current_duty_servo = 15  # Start in center position
current_duty_esc = NEUTRAL_DUTY  # Start the ESC in neutral

# ESC Control Function
def adjust_throttle(command):
    global current_duty_esc

    if command == "UP" and current_duty_esc < MAX_DUTY_ESC:
        current_duty_esc += STEP
    elif command == "DOWN" and current_duty_esc > MIN_DUTY_ESC:
        current_duty_esc -= STEP
    elif command == "NEUTRAL":
        current_duty_esc = NEUTRAL_DUTY

    pwmEsc.ChangeDutyCycle(current_duty_esc)
    print(f"ESC Throttle set to Duty Cycle: {current_duty_esc:.2f}%")

# Servo Control Function
def move_servo(command):
    global current_duty_servo

    if command == "LEFT" and current_duty_servo < MAX_DUTY_SERVO:
        current_duty_servo += STEP * 2
    elif command == "RIGHT" and current_duty_servo > MIN_DUTY_SERVO:
        current_duty_servo -= STEP * 2

    pwmServo.ChangeDutyCycle(current_duty_servo)
    print(f"Servo moved to Duty Cycle: {current_duty_servo:.2f}%")

# Handle client connection
def handle_client(conn):
    """ Handles a single client connection """
    global pwmEsc, pwmServo
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

# Accept connections in a separate thread
def start_server():
    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.daemon = True  # Closes thread when main program exits
        client_thread.start()

# Run the socket server in a separate thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the main thread alive

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pwmEsc.ChangeDutyCycle(NEUTRAL_DUTY)
    time.sleep(2)
    pwmEsc.stop()
    pwmServo.stop()
    GPIO.cleanup()
    time.sleep(2)
    server_socket.close()
