import pigpio
import time

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    exit("pigpio daemon not running")

# Define the GPIO pin (BCM numbering)
LED_GPIO = 13  # GPIO13 = physical pin 33

# Set pin as output
pi.set_mode(LED_GPIO, pigpio.OUTPUT)

try:
    while True:
        print("LED ON")
        pi.write(LED_GPIO, 1)  # Set GPIO HIGH = LED ON
        time.sleep(1)

        print("LED OFF")
        pi.write(LED_GPIO, 0)  # Set GPIO LOW = LED OFF
        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted")

finally:
    pi.write(LED_GPIO, 0)  # Turn LED off
    pi.stop()
