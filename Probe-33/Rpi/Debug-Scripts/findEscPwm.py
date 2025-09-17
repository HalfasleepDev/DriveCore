import pigpio
import sys
import termios
import tty
import time
from colorama import Fore, Style, init

init(autoreset=True)

ESC_PIN = 19  # GPIO19 (BCM numbering)
# Spectrum Firma ESC typical calibration range:
MIN_US = 1000    # Minimum throttle (μs)
MAX_US = 2000    # Maximum throttle (μs)
NEUTRAL_US = 1500 # Usually neutral/stop for bidirectional ESCs

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print(Fore.RED + "Failed to connect to pigpio daemon. Is it running?" + Style.RESET_ALL)
    exit(1)

def set_pulsewidth(pw):
    pi.set_servo_pulsewidth(ESC_PIN, pw)
    print(Fore.CYAN + f"Pulse width set to {pw} μs" + Style.RESET_ALL)

def stop_esc():
    pi.set_servo_pulsewidth(ESC_PIN, 0)
    print(Fore.MAGENTA + "ESC signal stopped (pwm=0)." + Style.RESET_ALL)

def arm_esc():
    print(Fore.GREEN + "Sending NEUTRAL (1500μs) to arm ESC...")
    set_pulsewidth(NEUTRAL_US)
    time.sleep(2)

def esc_calibration():
    print(Fore.YELLOW + Style.BRIGHT + "\n=== ESC CALIBRATION ===" + Style.RESET_ALL)
    print(Fore.YELLOW + "1. UNPLUG the ESC power (if possible)!" + Style.RESET_ALL)
    input(Fore.YELLOW + "Press Enter when ready to begin calibration..." + Style.RESET_ALL)

    print(Fore.YELLOW + "2. Setting MAX throttle. (Keep ESC unpowered)" + Style.RESET_ALL)
    set_pulsewidth(MAX_US)
    input(Fore.YELLOW + "NOW PLUG IN ESC power and wait for beeps. Then press Enter..." + Style.RESET_ALL)

    print(Fore.YELLOW + "3. Setting MIN throttle..." + Style.RESET_ALL)
    set_pulsewidth(MIN_US)
    print(Fore.YELLOW + "Wait for confirmation beeps from ESC." + Style.RESET_ALL)
    time.sleep(3)

    print(Fore.GREEN + "Calibration complete! Returning to neutral." + Style.RESET_ALL)
    set_pulsewidth(NEUTRAL_US)
    time.sleep(2)
    stop_esc()

def manual_test():
    print(Fore.CYAN + "\n=== ESC MANUAL TEST ===")
    print("You can enter pulse width in μs (1000-2000), or type 'neutral', 'min', 'max', 'stop', or 'exit'.")
    while True:
        user = input(Fore.YELLOW + "Command or μs value: " + Style.RESET_ALL).strip().lower()
        if user == "exit":
            break
        elif user == "stop":
            stop_esc()
        elif user == "neutral":
            set_pulsewidth(NEUTRAL_US)
        elif user == "min":
            set_pulsewidth(MIN_US)
        elif user == "max":
            set_pulsewidth(MAX_US)
        else:
            try:
                val = int(float(user))
                if 800 <= val <= 2500:
                    set_pulsewidth(val)
                else:
                    print(Fore.RED + "Value out of safe range (800-2500μs)!" + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

def esc_menu():
    options = [
        "Arm ESC (send neutral signal)",
        "Calibrate ESC (full throttle range)",
        "Manual test (send custom PWM)",
        "Stop signal to ESC",
        "Exit"
    ]
    idx = 0
    while True:
        print(Fore.BLUE + Style.BRIGHT + "\n=== ESC DEBUG/CALIBRATION MENU ===" + Style.RESET_ALL)
        for i, opt in enumerate(options):
            prefix = Fore.CYAN + "---> " if i == idx else "  "
            highlight = Fore.YELLOW + Style.BRIGHT if i == idx else ""
            end = Style.RESET_ALL if i == idx else ""
            print(f"{prefix}{highlight}{opt}{end}")
        print(Fore.YELLOW + "\nUse ↑/↓ (or W/S) to move, Enter to select." + Style.RESET_ALL)
        key = getch()
        if key in ['\x1b[A', 'w', 'W']:  # Up arrow or W
            idx = (idx - 1) % len(options)
        elif key in ['\x1b[B', 's', 'S']:  # Down arrow or S
            idx = (idx + 1) % len(options)
        elif key in ['\r', '\n']:  # Enter
            if idx == 0:
                arm_esc()
            elif idx == 1:
                esc_calibration()
            elif idx == 2:
                manual_test()
            elif idx == 3:
                stop_esc()
            elif idx == 4:
                break
            input(Fore.YELLOW + "Press Enter to return to menu..." + Style.RESET_ALL)
        elif key.lower() == 'q':
            break
        # Clear screen for next draw
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    stop_esc()

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            # Arrow keys: read 2 more bytes
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    try:
        esc_menu()
    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted. Stopping ESC for safety." + Style.RESET_ALL)
    finally:
        stop_esc()
        pi.stop()
