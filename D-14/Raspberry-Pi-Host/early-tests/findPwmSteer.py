import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
SERVO_PIN = 26  # Change this to the correct GPIO pin

# Servo PWM Configuration
#FREQ = 50  # Standard 50Hz PWM frequency for servos
FREQ = 100
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM
pwm = GPIO.PWM(SERVO_PIN, FREQ)
pwm.start(0)

# Function to test duty cycle
def set_duty_cycle(duty_cycle):
    """Set a specific duty cycle for testing."""
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Testing Duty Cycle: {duty_cycle:.2f}%")
    time.sleep(1)
    pwm.ChangeDutyCycle(0)  # Stop signal to prevent jitter

try:
    while True:
        print("\nEnter a duty cycle (0-100) to test, or 'exit' to quit:")
        user_input = input("Duty Cycle: ")

        if user_input.lower() == "exit":
            break

        try:
            duty_cycle = float(user_input)
            if 0 <= duty_cycle <= 100:
                set_duty_cycle(duty_cycle)
            else:
                print("Invalid input! Enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input! Please enter a number.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pwm.stop()
    GPIO.cleanup()
