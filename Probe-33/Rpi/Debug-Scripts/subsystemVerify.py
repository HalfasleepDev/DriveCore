import serial
import time
import json
import sys
import threading
from colorama import Back, Fore, Style, init

init(autoreset=True)

SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 115200

SUPPORTED_COMMANDS = [
    "WIPER_ON",
    "WIPER_OFF",
    "STATUS",
    "PAGE_STATUS",
    "PAGE_MESSAGES",
    "MSG:Test message",
    "TEMP_THRESH:30"
]

def clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def serial_reader(ser, lines, stop_event, lock):
    while not stop_event.is_set():
        try:
            if ser.in_waiting:
                raw = ser.readline().decode('utf-8', errors='ignore').strip()
                if raw:
                    if raw.startswith("{") and raw.endswith("}"):
                        try:
                            msg = json.loads(raw.replace("'", '"'))
                            text = Fore.GREEN + f"ESP32 STATUS: {msg}" + Style.RESET_ALL
                        except Exception:
                            text = Fore.YELLOW + f"ESP32 (bad JSON): {raw}" + Style.RESET_ALL
                    else:
                        text = Fore.CYAN + f"ESP32: {raw}" + Style.RESET_ALL
                    with lock:
                        lines.append(text)
        except Exception as e:
            with lock:
                lines.append(Fore.RED + f"Serial error: {e}" + Style.RESET_ALL)
        time.sleep(0.02)

def getch():
    import termios, tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # For arrow keys or ESC
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def menu_select():
    idx = 0
    while True:
        clear()
        print(Fore.BLUE + Style.BRIGHT + "=== SUPPORTED ESP32 COMMANDS ===" + Style.RESET_ALL)
        for i, cmd in enumerate(SUPPORTED_COMMANDS):
            pointer = Fore.CYAN + "→ " if i == idx else "  "
            highlight = Back.CYAN + Fore.BLACK + Style.BRIGHT if i == idx else ""
            end = Style.RESET_ALL if i == idx else ""
            print(f"{pointer}{highlight}{cmd}{end}")
        print(Fore.YELLOW + "\n↑/↓: select, Enter: send, Q: cancel" + Style.RESET_ALL)
        key = getch()
        if key in ['\x1b[A', 'w', 'W']:
            idx = (idx - 1) % len(SUPPORTED_COMMANDS)
        elif key in ['\x1b[B', 's', 'S']:
            idx = (idx + 1) % len(SUPPORTED_COMMANDS)
        elif key in ['\r', '\n']:
            return SUPPORTED_COMMANDS[idx]
        elif key.lower() == 'q':
            return None

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(Fore.RED + f"Could not open serial port {SERIAL_PORT}: {e}" + Style.RESET_ALL)
        return

    print(Fore.CYAN + f"Serial port {SERIAL_PORT} opened. Type to send, Tab for commands, Ctrl+C/ESC to exit." + Style.RESET_ALL)
    lines = []
    stop_event = threading.Event()
    lock = threading.Lock()
    reader = threading.Thread(target=serial_reader, args=(ser, lines, stop_event, lock), daemon=True)
    reader.start()

    try:
        while True:
            clear()
            print(Fore.BLUE + Style.BRIGHT + "=== ESP32 SERIAL LIVE CHAT ===" + Style.RESET_ALL)
            print(Fore.YELLOW + "Type or use Tab for commands. Type 'exit' to quit.\n" + Style.RESET_ALL)
            with lock:
                for l in lines[-20:]:
                    print(l)
            print(Fore.MAGENTA + "\n[Tab = menu | Enter = send | exit = quit]" + Style.RESET_ALL)
            print(Fore.CYAN + "Supported: " + ', '.join(SUPPORTED_COMMANDS) + Style.RESET_ALL)
            print()
            # Prompt for input
            sys.stdout.write(Fore.YELLOW + ">>> " + Style.RESET_ALL)
            sys.stdout.flush()
            user_input = ""
            while True:
                c = getch()
                # Tab key to open menu
                if c == '\t':
                    cmd = menu_select()
                    if cmd:
                        user_input = cmd
                        print(cmd)
                        break
                    else:
                        # Redraw prompt after cancel
                        clear()
                        with lock:
                            for l in lines[-20:]:
                                print(l)
                        print(Fore.YELLOW + ">>> " + Style.RESET_ALL, end='')
                        sys.stdout.flush()
                        continue
                # Enter key to send
                elif c in ['\r', '\n']:
                    break
                # Ctrl+C or ESC to exit
                elif c == '\x03' or c.startswith('\x1b'):
                    user_input = "exit"
                    print()
                    break
                # Backspace
                elif c in ['\x7f', '\b']:
                    user_input = user_input[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                else:
                    user_input += c
                    sys.stdout.write(c)
                    sys.stdout.flush()
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if user_input.strip():
                ser.write((user_input.strip() + "\n").encode('utf-8'))
                with lock:
                    lines.append(Fore.MAGENTA + f"Sent: {user_input.strip()}" + Style.RESET_ALL)
            time.sleep(0.05)
    except (KeyboardInterrupt, EOFError):
        print(Fore.YELLOW + "\nExiting..." + Style.RESET_ALL)
    finally:
        stop_event.set()
        ser.close()
        time.sleep(0.2)
        clear()
        print(Fore.MAGENTA + "Serial port closed." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
