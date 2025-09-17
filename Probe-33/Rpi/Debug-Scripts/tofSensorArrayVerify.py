import time
import board
import busio
import digitalio
from adafruit_vl53l0x import VL53L0X

# Color output (optional)
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class FakeColor:  # fallback if colorama isn't installed
        def __getattr__(self, _): return ""
    Fore = Style = FakeColor()

# ===== Sensor configuration =====
SENSORS = [
    {'name': 'Front Left',  'xshut': 24, 'key': 'FL'},
    {'name': 'Front Right', 'xshut': 25, 'key': 'FR'},
    {'name': 'Rear Left',   'xshut': 5,  'key': 'RL'},
    {'name': 'Rear Right',  'xshut': 6,  'key': 'RR'},
]

# Helper for board pin name (D24, D25, etc)
def get_board_pin(num):
    return getattr(board, f"D{num}")

def setup_xshut_pins():
    pins = {}
    for s in SENSORS:
        pin = digitalio.DigitalInOut(get_board_pin(s['xshut']))
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False  # all sensors OFF initially
        pins[s['xshut']] = pin
    return pins

def power_up_sensor(xshut_pin, pins):
    for pin in pins.values():
        pin.value = False  # power off all
    time.sleep(0.02)
    pins[xshut_pin].value = True  # power on one
    time.sleep(0.20)  # sensor boot time

def distance_color(mm):
    if mm is None:
        return Fore.MAGENTA
    if mm < 100:
        return Fore.RED
    elif mm < 400:
        return Fore.YELLOW
    elif mm < 1200:
        return Fore.GREEN
    else:
        return Fore.CYAN

def clear():
    import os
    os.system("cls" if os.name == "nt" else "clear")

def get_map_ascii(dists):
    FL, FR, RL, RR = dists.get('FL'), dists.get('FR'), dists.get('RL'), dists.get('RR')
    def dist_str(val):
        return f"{val:4d}" if isinstance(val, int) else " ---"
    return f"""
   {distance_color(FL)}FL {dist_str(FL)} mm{Style.RESET_ALL}       {distance_color(FR)}FR {dist_str(FR)} mm{Style.RESET_ALL}
      ╭─────────────╮
      │             │
{distance_color(RL)}RL {dist_str(RL)} mm{Style.RESET_ALL} │   [  CAR  ]   │ {distance_color(RR)}RR {dist_str(RR)} mm{Style.RESET_ALL}
      │             │
      ╰─────────────╯
"""

def read_sensor(i2c, xshut_pin, pins):
    power_up_sensor(xshut_pin, pins)
    try:
        sensor = VL53L0X(i2c)
        distance = sensor.range
        del sensor
        return distance
    except Exception as e:
        return None

def main():
    pins = setup_xshut_pins()
    i2c = busio.I2C(board.SCL, board.SDA)
    print(Fore.CYAN + "VL53L0X Multi-Sensor CLI (Adafruit CircuitPython version)" + Style.RESET_ALL)
    time.sleep(1)
    keymap = {s['name']: s['key'] for s in SENSORS}

    try:
        while True:
            dists = {}
            for s in SENSORS:
                dist = read_sensor(i2c, s['xshut'], pins)
                dists[s['key']] = dist
            clear()
            print(Fore.BLUE + "=== TOF SENSOR ARRAY MAP ===\n" + Style.RESET_ALL)
            print(get_map_ascii(dists))
            print(Fore.GREEN + "Press Ctrl+C to exit, script updates every 1s." + Style.RESET_ALL)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        for pin in pins.values():
            pin.value = False  # power down all sensors

if __name__ == "__main__":
    main()
