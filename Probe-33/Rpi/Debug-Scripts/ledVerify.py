import os
import sys
import termios
import tty
from colorama import Fore, Style, Back, init

import pigpio
import board
import neopixel

init(autoreset=True)

# Neopixel config
NEOPIXEL_PIN = board.D18
NEOPIXEL_COUNT = 40   

# --- ASCII CAR ART ---
car_ascii = [
    r"       `===@@@@@===`       ",
    r"     0//@@@@@@@@@@@\\0     ",
    r"   @//@@@@@@@@@@@@@@@\\@   ",
    r"  @@@@@@@@@@@@@@@@@@@@@@@  ",
    r"  @@@@@@@@@@@@@@@@@@@@@@@  ",
    r"  @@@@@@@@@@@@@@@@@@@@@@@  ",
    r"   @/*****************\@   ",
    r"   @|                 |@   ",
    r"   @\                 /@   ",
    r"(=>@@|               |@@<=)",
    r"   @^\               /^@   ",
    r"   @|\\____-----____//|@   ",
    r"   @| \@@@@@@@@@@@@@/ |@   ",
    r"   @|  |@@@@@@@@@@@|  |@   ",
    r"   @|  |@@@@@@@@@@@|  |@   ",
    r"   @|  |@@@@@@@@@@@|  |@   ",
    r"   @\  |@@@@@@@@@@@|  /@   ",
    r"  @@@| /@|       |@\ |@@@  ",
    r"  @@@| |@|       |@| |@@@  ",
    r"  @@@|/@/         \@\|@@@  ",
    r"  @@@⌄@|           |@⌄@@@  ",
    r"  @@@@@|           |@@@@@  ",
    r"   @\\@@@@@@@@@@@@@@@//@   ",
    r"    @\\@@@@@@@@@@@@@//@    ",
    r"      `==[=======]==`      "
]

# --- MODULE POSITIONS FOR HIGHLIGHTING (single and multi-col/row) ---
# Format: (row, col) or for multi-col: (row, start_col, end_col)
MODULES = [
    {"name": "Left Headlight",     "positions": [(0, 8, 11), (1, 6, 8), (2, 4, 6)]},
    {"name": "Right Headlight",    "positions": [(0, 16, 19), (1, 19, 21), (2, 21, 23)]},
    {"name": "Left Foglight",      "positions": [(1, 5)]},
    {"name": "Right Foglight",     "positions": [(1, 21)]},
    {"name": "Left Mirror",        "positions": [(9, 1)]},
    {"name": "Right Mirror",       "positions": [(9, 25)]},
    {"name": "Center Brake Bar",   "positions": [(24, 9, 18)]},
    {"name": "Left Brakelight",    "positions": [(22, 4, 6), (23, 5, 7), (24, 7, 9)]},
    {"name": "Right Brakelight",   "positions": [(22, 21, 23), (23, 20, 22), (24, 18, 20)]},
]

# --- GPIO PIN MAP ---
LED_GPIO_MAP = {
    "Left Foglight": 17,
    "Right Foglight": 27,
    "Left Mirror": 22,
    "Right Mirror": 23
}

# --- INIT ---
pi = pigpio.pi()
for name, gpio in LED_GPIO_MAP.items():
    pi.set_mode(gpio, pigpio.OUTPUT)
    pi.write(gpio, 0)  # Off

pixels = neopixel.NeoPixel(
    NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=0.4, auto_write=True, pixel_order=neopixel.GRB
)

NEOPIXEL_SEGMENTS = {
    "Left Headlight":      range(0, 8),    # Stick 1: LEDs 0-7
    "Right Headlight":     range(8, 16),   # Stick 2: LEDs 8-15
    "Right Brakelight":    range(16, 24),  # Stick 3: LEDs 16-23
    "Center Brake Bar":    range(24, 32),  # Stick 4: LEDs 24-31
    "Left Brakelight":     range(32, 40)   # Stick 5: LEDs 32-39
}

# --- HELPER: UPDATE HARDWARE STATE ---
def set_led_state(name, state):
    if name in LED_GPIO_MAP:
        pi.write(LED_GPIO_MAP[name], 1 if state else 0)
    elif name in NEOPIXEL_SEGMENTS:
        color = (255, 255, 255) if "Headlight" in name else (255, 0, 0) if "Brake" in name else (0, 0, 0)
        for idx in NEOPIXEL_SEGMENTS[name]:
            pixels[idx] = color if state else (0, 0, 0)
        pixels.show()
    else:
        # Unknown module, do nothing or log
        pass

def cleanup():
    for name, gpio in LED_GPIO_MAP.items():
        pi.write(gpio, 0)
    pixels.fill((0,0,0))
    pixels.show()
    pi.stop()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def getch():
    """Read a single keypress from stdin (no Enter required)."""
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

def render_car(led_states, selected_idx):
    # Copy lines so we can safely modify
    lines = car_ascii[:]
    lines = [list(line) for line in lines]  # List of char lists for easy mutation

    for idx, module in enumerate(MODULES):
        is_selected = (idx == selected_idx)
        on = led_states[module['name']]
        for pos in module['positions']:
            row = pos[0]
            if len(pos) == 2:  # Single symbol
                col = pos[1]
                orig_char = car_ascii[row][col]
                if is_selected:
                    color = Back.CYAN + Fore.BLACK + Style.BRIGHT
                elif "Mirror" in module['name'] or "Foglight" in module['name']:
                    color = Fore.YELLOW + (Style.BRIGHT if on else Style.NORMAL)
                else:
                    color = ""
                lines[row][col] = color + orig_char + Style.RESET_ALL
            elif len(pos) == 3:  # Multi-column (e.g., [===])
                start, end = pos[1], pos[2]
                orig_sub = car_ascii[row][start:end]
                if is_selected:
                    color = Back.CYAN + Fore.BLACK + Style.BRIGHT
                elif "Brake" in module['name']:
                    color = Fore.RED + (Style.BRIGHT if on else Style.NORMAL)
                elif "Headlight" in module['name']:
                    color = (
                        Back.CYAN + Fore.BLACK + Style.BRIGHT if is_selected else
                        Fore.WHITE + Style.BRIGHT if on else
                        Fore.LIGHTBLACK_EX
                    )
                else:
                    color = ""
                colored = color + "".join(orig_sub) + Style.RESET_ALL
                # Replace substring in line
                lines[row][start] = colored
                # Remove next n-1 original chars (because colored is one string)
                for i in range(start + 1, end):
                    lines[row][i] = ""
    # Recombine lines
    lines = ["".join(filter(None, l)) for l in lines]
    return "\n".join(lines)

def main():
    led_states = {mod["name"]: False for mod in MODULES}
    idx = 0
    while True:
        clear()
        print(f"{Fore.CYAN}{Style.DIM}DriveCore OS - LED Module Tester{Style.RESET_ALL}\n")
        print(render_car(led_states, idx))
        print(f"\n{Fore.LIGHTBLUE_EX}{Style.BRIGHT}Use ↑/↓ or W/S to select, SPACE/ENTER to toggle, Q to quit.\n{Style.RESET_ALL}")
        # Show list with status and highlight on selection
        for i, mod in enumerate(MODULES):
            sel = Fore.CYAN + Style.BRIGHT + "---> "if i == idx else ""
            name_fmt = (Fore.CYAN  + Style.BRIGHT if i == idx else "")
            name_end = (Style.RESET_ALL if i == idx else "")
            on = Fore.GREEN + " ON " + Style.RESET_ALL if led_states[mod["name"]] else Fore.RED + " OFF" + Style.RESET_ALL
            print(f"{sel}{name_fmt}[{mod['name']:^18}]{name_end} :{on}")
        key = getch()
        if key.lower() == 'q':
            break
        elif key in ['\x1b[A', 'w', 'W']:  # up arrow or w
            idx = (idx - 1) % len(MODULES)
        elif key in ['\x1b[B', 's', 'S']:  # down arrow or s
            idx = (idx + 1) % len(MODULES)
        elif key in [' ', '\r']:
            # Toggle selected LED
            name = MODULES[idx]['name']
            led_states[name] = not led_states[name]
            # GPIO logic would go here
            set_led_state(name, led_states[name])

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()