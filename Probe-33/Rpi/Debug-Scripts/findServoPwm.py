import pigpio
import time
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

# GPIO Pin Configuration
SERVO_PIN = 26  # BCM numbering (gpio37)

# Servo pulse width range (microseconds)
MIN_PW = 1600     # Full left
CENTER_PW = 1850  # Center
MAX_PW = 2100     # Full right

# Named positions for easy menu
POSITIONS = [
    ("Full Left",   MIN_PW, 0),
    ("Center",      CENTER_PW, 50),
    ("Full Right",  MAX_PW, 100),
    ("Custom (enter duty %)", None, None),
    ("Exit",        None, None)
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pulsewidth_to_duty(pw):
    # Map pulse width back to duty cycle % for info
    return (pw - MIN_PW) * 100.0 / (MAX_PW - MIN_PW)

def set_servo(pi, pulsewidth):
    pi.set_servo_pulsewidth(SERVO_PIN, pulsewidth)
    print(f"{Fore.YELLOW}Set Pulse Width: {pulsewidth}μs {Fore.WHITE}(Duty Cycle: {pulsewidth_to_duty(pulsewidth):.1f}%)")
    time.sleep(1)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Stop signal to prevent jitter

def main():
    # Connect to pigpio daemon
    pi = pigpio.pi()
    if not pi.connected:
        print(f"{Fore.RED}Failed to connect to pigpio daemon. Is it running?{Style.RESET_ALL}")
        sys.exit(1)

    try:
        idx = 0
        while True:
            clear()
            print(f"{Fore.CYAN}{Style.BRIGHT}=== DriveCore Servo/Steering Tester ==={Style.RESET_ALL}\n")
            for i, (name, _, _) in enumerate(POSITIONS):
                if i == idx:
                    print(f"{Fore.CYAN}{Style.BRIGHT}→ [{name}]{Style.RESET_ALL}")
                else:
                    print(f"  [{name}]")
            print(f"\n{Fore.GREEN}Use ↑/↓ or W/S to select, Enter to choose.{Style.RESET_ALL}")

            # Read keyboard input (arrow keys and enter)
            ch = getch()
            if ch in ['\x1b[A', 'w', 'W']:
                idx = (idx - 1) % len(POSITIONS)
            elif ch in ['\x1b[B', 's', 'S']:
                idx = (idx + 1) % len(POSITIONS)
            elif ch == '\r':
                name, pulsewidth, duty = POSITIONS[idx]
                if name == "Exit":
                    break
                elif name == "Custom (enter duty %)":
                    duty_input = input(f"\n{Fore.CYAN}Enter duty cycle (0-100), or 'exit' to go back:{Style.RESET_ALL} ")
                    if duty_input.lower() == "exit":
                        continue
                    try:
                        duty_val = float(duty_input)
                        if not (0 <= duty_val <= 100):
                            print(f"{Fore.RED}Duty cycle out of range!{Style.RESET_ALL}")
                            time.sleep(1)
                            continue
                        pulsewidth = int(MIN_PW + duty_val/100.0*(MAX_PW - MIN_PW))
                        set_servo(pi, pulsewidth)
                        input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                        time.sleep(1)
                    continue
                else:
                    set_servo(pi, pulsewidth)
                    input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()

def getch():
    """Read a single keypress from stdin (no Enter required)."""
    import tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

if __name__ == "__main__":
    main()
