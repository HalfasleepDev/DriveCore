import sys
import time
import threading
import termios
import tty
from colorama import Fore, Back, Style, init

init(autoreset=True)

# === MPU-9250 Library ===
try:
    from mpu9250_jmdev.registers import *
    from mpu9250_jmdev.mpu_9250 import MPU9250
except ImportError:
    print(Fore.RED + "mpu9250-jmdev library not found! Install with pip3 install mpu9250-jmdev" + Style.RESET_ALL)
    sys.exit(1)

# === Helper Functions ===
def clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def getch():
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

# === IMU Reader Thread ===
class IMUReader(threading.Thread):
    def __init__(self, imu):
        super().__init__()
        self.imu = imu
        self.running = threading.Event()
        self.running.set()
        self.lines = []
        self.lock = threading.Lock()

    def run(self):
        while self.running.is_set():
            try:
                accel = self.imu.readAccelerometerMaster()
                gyro = self.imu.readGyroscopeMaster()
                mag = self.imu.readMagnetometerMaster()
                temp = self.imu.readTemperatureMaster()
                line = (f"{Fore.CYAN}ACC [g]: {accel}\n"
                        f"{Fore.YELLOW}GYRO [°/s]: {gyro}\n"
                        f"{Fore.MAGENTA}MAG [μT]: {mag}\n"
                        f"{Fore.RED}TEMP [°C]: {temp:.2f}{Style.RESET_ALL}")
                with self.lock:
                    self.lines.append(line)
                    if len(self.lines) > 15:
                        self.lines = self.lines[-15:]
            except Exception as e:
                with self.lock:
                    self.lines.append(Fore.RED + f"Read error: {e}" + Style.RESET_ALL)
            time.sleep(0.15)

    def stop(self):
        self.running.clear()

    def get_lines(self):
        with self.lock:
            return list(self.lines)

def main():
    # === Setup IMU ===
    try:
        imu = MPU9250(
            address_ak=AK8963_ADDRESS,
            address_mpu_master=MPU9050_ADDRESS_68,
            address_mpu_slave=None,
            bus=1, # Default I2C bus on Raspberry Pi
            gfs=GFS_1000, afs=AFS_8G, mfs=AK8963_BIT_16, mode=AK8963_MODE_C100HZ)
        imu.calibrateMPU6500()
        imu.configure()
    except Exception as e:
        print(Fore.RED + f"Failed to initialize MPU-9250: {e}" + Style.RESET_ALL)
        sys.exit(1)

    reader = IMUReader(imu)
    reader.start()
    menu = ["Live Readout", "Calibrate Gyro/Accel", "Exit"]
    idx = 0

    try:
        while True:
            clear()
            print(Fore.BLUE + Style.BRIGHT + "=== MPU-9250 IMU CLI TEST ===" + Style.RESET_ALL)
            for i, item in enumerate(menu):
                sel = Fore.CYAN + "→ " if i == idx else "  "
                highlight = Back.CYAN + Fore.BLACK + Style.BRIGHT if i == idx else ""
                end = Style.RESET_ALL if i == idx else ""
                print(f"{sel}{highlight}{item}{end}")
            print(Fore.YELLOW + "\nUse ↑/↓ (or W/S) to select, Enter to run, Q to exit." + Style.RESET_ALL)

            key = getch()
            if key in ['\x1b[A', 'w', 'W']:
                idx = (idx - 1) % len(menu)
            elif key in ['\x1b[B', 's', 'S']:
                idx = (idx + 1) % len(menu)
            elif key in ['\r', '\n']:
                if idx == 0:  # Live Readout
                    while True:
                        clear()
                        print(Fore.BLUE + Style.BRIGHT + "--- LIVE IMU DATA ---" + Style.RESET_ALL)
                        for l in reader.get_lines():
                            print(l)
                        print(Fore.GREEN + "\nPress Enter/Menu to return..." + Style.RESET_ALL)
                        # Wait for Enter or menu key
                        k = getch()
                        if k in ['\r', '\n']:
                            break
                elif idx == 1:  # Calibrate Gyro/Accel
                    clear()
                    print(Fore.YELLOW + "Place IMU still, calibrating gyro/accel..." + Style.RESET_ALL)
                    imu.calibrateMPU6500()
                    imu.configure()
                    print(Fore.GREEN + "Calibration complete!" + Style.RESET_ALL)
                    input("Press Enter to return...")
                elif idx == 2:  # Exit
                    break
            elif key.lower() == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        reader.stop()
        reader.join()
        clear()
        print(Fore.MAGENTA + "Exiting MPU-9250 test CLI. Bye!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
