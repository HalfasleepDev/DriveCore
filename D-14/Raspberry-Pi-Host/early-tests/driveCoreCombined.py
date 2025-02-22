import socket
import RPi.GPIO as GPIO
import time
import multiprocessing
from flask import Flask, Response
from picamera2 import Picamera2
import cv2

# ====================== GPIO Configuration ======================
SERVO_PIN = 26  # GPIO pin for connected servo
ESC_PIN = 19    # GPIO pin for connected ESC
FREQ = 100  # Change to 2000Hz if needed

# Servo PWM Duty Cycle Range
MIN_DUTY_SERVO = 9  # Leftmost position
MAX_DUTY_SERVO = 21  # Rightmost position

STEP_SERVO = 0.1  # Step size for servo movement
STEP_ESC = 0.05  # Smaller step for smoother ESC transitions
DELAY = 0.02  # Delay for smooth transitions

# ESC PWM Duty Cycle Range
MIN_DUTY_ESC = 13.1    # Minimum throttle
MAX_DUTY_ESC = 17.5   # Maximum throttle
NEUTRAL_DUTY = 15  # Neutral position

# ====================== Flask Camera Stream ======================
app = Flask(__name__)
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))
camera.start()

def generate_frames():
    """ Continuously capture frames from the camera and send as MJPEG stream """
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video-feed')
def video_feed():
    """ Flask route for live video feed """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    """ Runs Flask video streaming server """
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ====================== ESC & Servo Control via Socket ======================
def run_socket_server():
    """ Runs the socket server for ESC & Servo control """

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
    HOST = '192.168.0.102'
    PORT = 4444

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"🚗 Servo & ESC Server Listening on {HOST}:{PORT}")
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    # Store current duty cycles
    current_duty_servo = 15  # Start in center position
    current_duty_esc = NEUTRAL_DUTY  # Start ESC in neutral

    # Function for smooth ESC throttle adjustment
    def adjust_throttle(command):
        """ Smoothly adjusts ESC throttle """
        nonlocal current_duty_esc
        target_duty = current_duty_esc

        if command == "UP" and current_duty_esc < MAX_DUTY_ESC:
            target_duty = min(MAX_DUTY_ESC, current_duty_esc + STEP_ESC)
        elif command == "DOWN" and current_duty_esc > MIN_DUTY_ESC:
            target_duty = max(MIN_DUTY_ESC, current_duty_esc - STEP_ESC)
        elif command == "NEUTRAL":
            target_duty = NEUTRAL_DUTY
            pwmEsc.ChangeDutyCycle(target_duty)
            time.sleep(0.1)
            pwmEsc.ChangeDutyCycle(0)  # Stop PWM to prevent jitter
            return

        # Smoothly transition to target duty cycle
        while abs(current_duty_esc - target_duty) > 0.01:
            if current_duty_esc < target_duty:
                current_duty_esc += STEP_ESC
            elif current_duty_esc > target_duty:
                current_duty_esc -= STEP_ESC
            pwmEsc.ChangeDutyCycle(current_duty_esc)
            print(f"ESC Throttle set to Duty Cycle: {current_duty_esc:.2f}%")
            time.sleep(DELAY)

    # Function for smooth servo movement
    def move_servo(command):
        """ Moves the servo smoothly """
        nonlocal current_duty_servo

        if command == "LEFT" and current_duty_servo < MAX_DUTY_SERVO:
            current_duty_servo += STEP_SERVO * 2
        elif command == "RIGHT" and current_duty_servo > MIN_DUTY_SERVO:
            current_duty_servo -= STEP_SERVO * 2

        pwmServo.ChangeDutyCycle(current_duty_servo)
        print(f"Servo moved to Duty Cycle: {current_duty_servo:.2f}%")

    try:
        while True:
            data = conn.recv(1024).decode('utf8').strip()
            if not data:
                break
            print(f"Received Command: {data}")
            move_servo(data)
            adjust_throttle(data)

    except KeyboardInterrupt:
        print("\nStopping Servo & ESC Server...")

    finally:
        pwmEsc.ChangeDutyCycle(NEUTRAL_DUTY)
        time.sleep(2)
        pwmEsc.stop()
        pwmServo.stop()
        GPIO.cleanup()
        time.sleep(2)
        conn.close()
        server_socket.close()

# ====================== Main Execution (Multiprocessing) ======================
if __name__ == '__main__':
    # Start Flask video stream in a separate process
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.start()

    # Start Socket server for ESC & Servo control
    socket_process = multiprocessing.Process(target=run_socket_server)
    socket_process.start()

    # Wait for both processes to finish
    flask_process.join()
    socket_process.join()
