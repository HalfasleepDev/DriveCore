import time
import sys
import termios
import tty
from colorama import Fore, Style, init

try:
    from DFRobot_GNSS import DFRobot_GNSS_I2C
except ImportError:
    print("You need to pip3 install DFRobot_GNSS or place the driver in your PYTHONPATH.")
    sys.exit(1)

init(autoreset=True)

def clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main():
    GNSS_ADDR = 0x20
    BUS = 1

    gnss = DFRobot_GNSS_I2C(BUS, GNSS_ADDR)
    print("Initializing GNSS module...")
    if not gnss.begin():
        print(Fore.RED + "Could not find GNSS device at address 0x20. Check wiring and try again." + Style.RESET_ALL)
        sys.exit(1)
    print(Fore.GREEN + "GNSS module found. Starting data stream..." + Style.RESET_ALL)
    time.sleep(1)

    try:
        while True:
            clear()
            print(Fore.BLUE + Style.BRIGHT + "=== DFROBOT GNSS (I2C) TEST MENU ===\n" + Style.RESET_ALL)

            # Date and Time
            utc_date = gnss.get_date()
            utc_time = gnss.get_utc()
            print(Fore.CYAN + f"UTC Date: {utc_date.year}-{utc_date.month:02d}-{utc_date.date:02d}   Time: {utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}" + Style.RESET_ALL)

            # Lat/Lon
            lat = gnss.get_lat()
            lon = gnss.get_lon()
            lat_str = f"{lat.lat_dd}° {lat.lat_mm}' {lat.lat_mmmmm}'' {lat.lat_direction}"
            lon_str = f"{lon.lon_ddd}° {lon.lon_mm}' {lon.lon_mmmmm}'' {lon.lon_direction}"
            print(Fore.YELLOW + f"Latitude:  {lat_str}   ({lat.latitude_degree:.6f})" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Longitude: {lon_str}   ({lon.lonitude_degree:.6f})" + Style.RESET_ALL)

            # Altitude
            alt = gnss.get_alt()
            print(Fore.GREEN + f"Altitude:  {alt:.2f} m" + Style.RESET_ALL)

            # Satellite count and GNSS mode
            sat = gnss.get_num_sta_used()
            mode = gnss.get_gnss_mode()
            mode_str = {1: "GPS", 2: "BeiDou", 3: "GPS+BeiDou", 4: "GLONASS", 5: "GPS+GLONASS", 6: "BeiDou+GLONASS", 7: "GPS+BeiDou+GLONASS"}.get(mode, "Unknown")
            sat_color = Fore.GREEN if sat >= 4 else (Fore.YELLOW if sat > 0 else Fore.RED)
            print(f"Satellites Used: {sat_color}{sat}{Style.RESET_ALL}    GNSS Mode: {mode_str}")

            # SOG, COG
            sog = gnss.get_sog()
            cog = gnss.get_cog()
            print(f"Speed Over Ground: {Fore.MAGENTA}{sog:.2f} knots{Style.RESET_ALL}   Course Over Ground: {Fore.CYAN}{cog:.2f}°{Style.RESET_ALL}")

            # Fix Status
            if sat == 0:
                print(Fore.RED + Style.BRIGHT + "\nSearching for satellites..." + Style.RESET_ALL)
            elif sat < 4:
                print(Fore.YELLOW + Style.BRIGHT + "\nNo 3D Fix (need >=4 satellites for 3D position)" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + Style.BRIGHT + "\n3D Fix Acquired!" + Style.RESET_ALL)

            print(Fore.BLUE + "\nPress Q to quit, Enter to refresh.\n" + Style.RESET_ALL)
            ch = getch()
            if ch.lower() == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting GNSS CLI.")

if __name__ == "__main__":
    main()
