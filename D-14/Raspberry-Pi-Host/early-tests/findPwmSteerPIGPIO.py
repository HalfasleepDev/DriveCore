import pigpio
import time

# GPIO Pin Configuration
SERVO_PIN = 26  # BCM numbering

# Servo pulse width range (microseconds)
MIN_PW = 500     # Typically 500μs = full left
MAX_PW = 2500    # Typically 2500μs = full right

# Connect to pigpio daemon
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon. Is it running?")
    exit(1)

# Function to convert duty cycle % (0-100) to pulse width (μs)
def duty_to_pulsewidth(duty_percent):
    return int(500 + (duty_percent / 100.0) * 2000)

# Function to test duty cycle
def set_duty_cycle(duty_cycle):
    pulsewidth = duty_to_pulsewidth(duty_cycle)
    pi.set_servo_pulsewidth(SERVO_PIN, pulsewidth)
    print(f"Testing Duty Cycle: {duty_cycle:.2f}% (Pulse Width: {pulsewidth}μs)")
    time.sleep(1)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Stop signal to prevent jitter

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
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Always stop the servo
    pi.stop()
