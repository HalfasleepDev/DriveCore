import socket
import RPi.GPIO as GPIO
import time

# GPIO Configuration
SERVO_PIN = 26  # Change this to your GPIO pin
ESC_PIN = 19
FREQ = 100  # 50Hz is standard for servos

# Servo PWM Duty Cycle Range
MIN_DUTY_SERVO = 9  # Leftmost position
MAX_DUTY_SERVO = 21  # Rightmost position
STEP = 0.1  # Step size for duty cycle changes
DELAY = 0.05  # Small delay for smooth movement

# ESC PWM Duty Cycle Range (Adjust based on ESC specs)
MIN_DUTY_ESC = 14.1    # Minimum throttle
MAX_DUTY_ESC = 17.5   # Maximum throttle
NEUTRAL_DUTY = 14.9  # Neutral position

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(ESC_PIN, GPIO.OUT)

# Initialize PWM
pwmServo = GPIO.PWM(SERVO_PIN, FREQ)
pwmServo.start(15)  # Start at center (15%)
pwmEsc = GPIO.PWM(ESC_PIN, FREQ)
pwmEsc.start(NEUTRAL_DUTY)  # Start in neutral

# Socket Configuration
HOST = '192.168.0.102'  # Listen on all available interfaces
PORT = 4444  # Choose a port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servo Server Listening on {HOST}:{PORT}")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# Store current duty cycle
current_duty_servo = 15  # Start in center position
current_duty_esc = NEUTRAL_DUTY

def adjust_throttle(command):
    global current_duty_esc

    if command == "UP" and current_duty_esc < MAX_DUTY_ESC:
        current_duty_esc +=STEP
    elif command == "DOWN" and current_duty_esc > MIN_DUTY_ESC:
        current_duty_esc -= STEP
    elif command == "NEUTRAL":
        current_duty_esc = NEUTRAL_DUTY
    
    pwmEsc.ChangeDutyCycle(current_duty_esc)
    print(f"ESC Throttle set to Duty Cycle: {current_duty_esc:.2f}%")

def move_servo(command):
    global current_duty_servo

    if command == "RIGHT" and current_duty_servo < MAX_DUTY_SERVO:
        current_duty_servo += STEP
    elif command == "LEFT" and current_duty_servo > MIN_DUTY_SERVO:
        current_duty_servo -= STEP
    else:
        print("Unknown Command:", command)

    pwmServo.ChangeDutyCycle(current_duty_servo)
    print(f"Servo moved to Duty Cycle: {current_duty_servo:.2f}%")



try:
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        move_servo(data)
        adjust_throttle(data)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pwmEsc.ChangeDutyCycle(NEUTRAL_DUTY)
    time.sleep(1)
    pwmEsc.stop()
    pwmServo.stop()
    GPIO.cleanup()
    conn.close()
    server_socket.close()
