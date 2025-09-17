import sys
import time
import termios
import tty
from smbus2 import SMBus
from colorama import Fore, Back, Style, init

init(autoreset=True)

BH1750_ADDRESS = 0x23  # Default I2C address for BH1750
CONT_H_RES_MODE = 0x10  # Continuous high-res mode
ONE_TIME_H_RES_MODE = 0x20  # One-time high-res mode

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

def lux_color(lux):
    if lux < 20:
        return Fore.BLUE
    elif lux < 200:
        return Fore.CYAN
    elif lux < 1000:
        return Fore.GREEN
    elif lux < 10000:
        return Fore.YELLOW
    else:
        return Fore.RED

class BH1750:
    def __init__(self, bus_num=1, addr=BH1750_ADDRESS):
        self.bus = SMBus(bus_num)
        self.addr = addr

    def read_lux(self, mode=CONT_H_RES_MODE):
        self.bus.write_byte(self.addr, mode)
        time.sleep(0.18)  # Wait for measurement (per datasheet: 120-180ms)
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 2)
        raw = (data[0] << 8) | data[1]
        return raw / 1.2  # Convert to lux

    def one_shot_lux(self):
        return self.read_lux(ONE_TIME_H_RES_MODE)

def main():
    try:
        sensor = BH1750()
    except Exception as e:
        print(Fore.RED + f"Could not initialize BH1750 on I2C bus: {e}" + Style.RESET_ALL)
        sys.exit(1)

    menu = ["Live Lux Readout", "One-Shot Read", "Exit"]
    idx = 0

    try:
        while True:
            clear()
            print(Fore.BLUE + Style.BRIGHT + "=== BH1750 LIGHT SENSOR CLI TEST ===" + Style.RESET_ALL)
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
                        try:
                            lux = sensor.read_lux()
                            color = lux_color(lux)
                            print(Fore.BLUE + Style.BRIGHT + "--- LIVE LUX READOUT ---\n" + Style.RESET_ALL)
                            print(color + f"Lux: {lux:.2f} lx" + Style.RESET_ALL)
                        except Exception as e:
                            print(Fore.RED + f"Read error: {e}" + Style.RESET_ALL)
                        print(Fore.GREEN + "\nPress Enter/Menu to return..." + Style.RESET_ALL)
                        # Wait 0.5s or until Enter/menu
                        import select
                        fd = sys.stdin.fileno()
                        r, _, _ = select.select([fd], [], [], 0.5)
                        if r:
                            ch = sys.stdin.read(1)
                            if ch in ['\r', '\n']:
                                break
                elif idx == 1:  # One-Shot Read
                    clear()
                    try:
                        lux = sensor.one_shot_lux()
                        color = lux_color(lux)
                        print(Fore.BLUE + Style.BRIGHT + "--- ONE-SHOT LUX READ ---\n" + Style.RESET_ALL)
                        print(color + f"Lux: {lux:.2f} lx" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Read error: {e}" + Style.RESET_ALL)
                    input("\nPress Enter to return...")
                elif idx == 2:  # Exit
                    break
            elif key.lower() == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        clear()
        print(Fore.MAGENTA + "Exiting BH1750 test CLI." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
