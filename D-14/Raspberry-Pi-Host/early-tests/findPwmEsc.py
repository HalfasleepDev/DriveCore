import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
ESC_PIN = 19  # Change this to the correct GPIO pin

# ESC PWM Configuration
FREQ = 100  # Standard 50Hz PWM frequency for ESCs

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_PIN, GPIO.OUT)

# Initialize PWM
pwm = GPIO.PWM(ESC_PIN, FREQ)
pwm.start(0)

# Function to test duty cycle
def set_duty_cycle(duty_cycle):
    """Set a specific duty cycle for testing ESC throttle."""
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Testing Duty Cycle: {duty_cycle:.2f}%")
    time.sleep(1)

try:
    print("ESC Calibration Process")
    print("1. Disconnect power from the ESC.")
    print("2. Enter the highest throttle (e.g., 10-12% duty cycle).")
    print("3. Power up the ESC while running the script at max throttle.")
    print("4. Wait for beeps, then enter the lowest throttle (e.g., 5%).")
    
    input("\nPress Enter to continue with testing...")

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
