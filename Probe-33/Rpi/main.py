import os
import sys
import colorama
import termios
import tty
import subprocess
import time

colorama.init(autoreset=True)
from colorama import Fore, Style

# ========= LOGO ASCII ==========
DRIVECORE_ASCII = f"""
{Style.DIM}{Fore.WHITE}+=========================================================================================+
{Fore.CYAN}| ____                              ____                               _____   ____       |
|/\  _`\          __               /\  _`\                            /\  __`\/\  _`\     |
|{Fore.LIGHTCYAN_EX}\\ \\ \\/\\ \\  _ __ /\\_\\  __  __    __\\ \\ \\/\\_\\    ___   _ __    __      \\ \\ \\/\\ \\ \\,\\L\\_\\   |
|{Fore.LIGHTBLUE_EX} \\ \\ \\ \\ \\/\\`'__\\/\\ \\/\\ \\/\\ \\ /'__`\\ \\ \\/_/_  / __`\\/\\`'__\\/'__`\\     \\ \\ \\ \\ \\/_\\__ \\   |
|  \\ \\ \\_\\ \\ \\ \\/ \\ \\ \\ \\ \\_/ /\\  __/\\ \\ \\L\\ \\/\\ \\L\\ \\ \\ \\//\\  __/      \\ \\ \\_\\ \\/\\ \\L\\ \\ |
|   \\ \\____/\\ \\_\\  \\ \\_\\ \\___/\\ \\____\\\\ \\____/\\ \\____/\\ \\_\\\\ \\____\\      \\ \\_____\\ `\\____\\|
|    \\/___/  \\/_/   \\/_/\\/__/  \\/____/ \\/___/  \\/___/  \\/_/ \\/____/       \\/_____/\\/_____/|
{Style.DIM}{Fore.WHITE}+=========================================================================================+{Style.RESET_ALL}
"""

# ========== MENU LOGIC ===========

MENU_OPTIONS = [
    "Calibration Tools",
    "Debugging Tools",
    "Start Autonomous Mode",
    "System Info",
    "Shut Down"
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_drivecore_logo():
    print(DRIVECORE_ASCII)

def get_key():
    """Read single char from stdin (arrow key or w/s navigation)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def custom_menu(options):
    idx = 0
    while True:
        clear()
        print_drivecore_logo()
        print(f"{Fore.LIGHTBLUE_EX}{Style.BRIGHT}Use ↑/↓ or W/S, [Enter] to select:{Style.RESET_ALL}\n")
        for i, opt in enumerate(options):
            if i == idx:
                print(f"{Fore.CYAN}{Style.BRIGHT}---> [{opt}]{Style.RESET_ALL}")
            else:
                print(f"     [{opt}]")
        print(f"\n{Style.DIM}{Fore.WHITE}DriveCore OS {Fore.MAGENTA}v1.0.0\n{Fore.WHITE}Vehicle: {Fore.MAGENTA}Probe-33 {Style.RESET_ALL}")
        key = get_key()
        if key in ['\x1b[A', 'w', 'W']:  # up arrow or w
            idx = (idx - 1) % len(options)
        elif key in ['\x1b[B', 's', 'S']:  # down arrow or s
            idx = (idx + 1) % len(options)
        elif key == '\r':  # Enter
            return idx

def boot_sequence():
    clear()
    #TODO: Replace with actual module startup msgs
    boot_msgs = [
        f"{Fore.CYAN}DriveCore OS Initializing...",
        f"{Fore.LIGHTCYAN_EX}{Style.DIM} > Verifying neural modules...{Style.RESET_ALL}",
        f"{Fore.MAGENTA}{Style.DIM} > Checking sensor suite...{Style.RESET_ALL}",
        f"{Fore.CYAN}{Style.DIM} > Power system stable...{Style.RESET_ALL}",
        f"{Fore.LIGHTCYAN_EX}{Style.DIM} > Engaging DriveCore kernel...{Style.RESET_ALL}",
        f"{Style.BRIGHT}{Fore.CYAN}SYSTEM ONLINE{Style.RESET_ALL}",
        f"{Fore.WHITE}--- Press Enter to access DriveCore Console ---{Style.RESET_ALL}"
    ]
    for msg in boot_msgs[:-1]:
        print(msg)
        time.sleep(0.5)
    print(boot_msgs[-1])
    input()

def launch_script(script_path, display_name):
    clear()
    print_drivecore_logo()
    print(f"{Fore.CYAN}[{display_name}] {Fore.WHITE}Launching {script_path}...\n{Style.RESET_ALL}")
    try:
        # You can use subprocess.run or os.system. subprocess is preferred for safety and control.
        result = subprocess.run(['python3', script_path], check=True)
        print(f"{Fore.GREEN}✔ {display_name} finished successfully.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✖ Error: {display_name} exited with code {e.returncode}.{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}✖ Script not found: {script_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✖ Unexpected error: {e}{Style.RESET_ALL}")
    input(f"\n{Fore.LIGHTBLUE_EX}Press Enter to return to main menu...{Style.RESET_ALL}")

def script_selection_menu(scripts, menu_title="Select Script"):
    """
    scripts: list of (display_name, script_path) tuples
    Returns the index of the selected script, or None if the user cancels.
    """
    idx = 0
    while True:
        clear()
        print_drivecore_logo()
        print(f"{Fore.LIGHTBLUE_EX}{Style.BRIGHT}{menu_title}:{Style.RESET_ALL}\n")
        for i, (display_name, _) in enumerate(scripts):
            if i == idx:
                print(f"{Fore.MAGENTA}{Style.BRIGHT}---> [{display_name}]{Style.RESET_ALL}")
            else:
                print(f"     [{display_name}]")
        print(f"\n{Fore.LIGHTBLACK_EX}Press Q to go back to the previous menu.{Style.RESET_ALL}")
        key = get_key()
        if key in ['\x1b[A', 'w', 'W']:  # up
            idx = (idx - 1) % len(scripts)
        elif key in ['\x1b[B', 's', 'S']:  # down
            idx = (idx + 1) % len(scripts)
        elif key == '\r':  # Enter
            return idx
        elif key.lower() == 'q':
            return None

def calibration_menu():
    # Add sub-menu or script launching logic here
    clear()
    print_drivecore_logo()
    print(f"{Fore.CYAN}{Style.BRIGHT}CALIBRATION TOOLS{Style.RESET_ALL}\n")
    input(f"{Fore.LIGHTBLUE_EX}Press Enter to return to main menu...{Style.RESET_ALL}")

def debugging_menu():
    '''scripts = [
        ("Live Camera Feed", "./debug_camera.py"),
        ("Sensor Status", "./debug_sensors.py"),
        ("IMU Monitor", "./debug_imu.py")
    ]'''
    scripts = [
        #("Servo Test", "Probe-33/Rpi/Debug-Scripts/findServoPwm.py"),
        #("Verify Light Modules", "Probe-33/Rpi/Debug-Scripts/ledVerify.py")
        ("Servo Test", "Debug-Scripts/findServoPwm.py"),
        ("ESC Test", "Debug-Scripts/findEscPwm.py"), #TODO: maybe move to calibration?
        ("Verify Light Modules", "Debug-Scripts/ledVerify.py"),
        ("Verify Camera Views", "Debug-Scripts/cameraVerify.py"),
        ("Verify Connection to Subsystem", "Debug-Scripts/subsystemVerify.py"),
        ("Verify TOF Sensor Array", "Debug-Scripts/tofSensorArrayVerify.py"),
        ("Verify IMU", "Debug-Scripts/imuVerify.py"),
        ("Verify Light Sensor", "Debug-Scripts/lightSensorVerify.py"),
        ("Verify GPS/GNSS", "Debug-Scripts/gnssVerify.py")
    ]
    selected = script_selection_menu(scripts, menu_title="Debugging Tools")
    if selected is not None:
        display_name, script_path = scripts[selected]
        launch_script(script_path, display_name)

def start_autonomous_mode():
    clear()
    print_drivecore_logo()
    print(f"{Fore.CYAN}{Style.BRIGHT}Starting Autonomous Mode...{Style.RESET_ALL}")
    # Example: launch_script('./main_system.py', 'Autonomous Mode')
    input(f"{Fore.LIGHTBLUE_EX}Press Enter to return to main menu...{Style.RESET_ALL}")

def system_info():
    clear()
    print_drivecore_logo()
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}== SYSTEM INFORMATION =={Style.RESET_ALL}")
    os.system('uname -a')
    os.system('free -h')
    input(f"\n{Fore.LIGHTBLUE_EX}Press Enter to return to DriveCore OS...{Style.RESET_ALL}")

def main_menu():
    boot_sequence()
    while True:
        selection = custom_menu(MENU_OPTIONS)
        if selection == 0:
            calibration_menu()
        elif selection == 1:
            debugging_menu()
        elif selection == 2:
            start_autonomous_mode()
        elif selection == 3:
            system_info()
        elif selection == 4:
            clear()
            print_drivecore_logo()
            print(f"{Fore.RED}{Style.BRIGHT}DriveCore OS shutting down...{Style.RESET_ALL}")
            sys.exit(0)

if __name__ == "__main__":
    main_menu()
