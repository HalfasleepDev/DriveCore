import sys
import os
import time
import numpy as np
from colorama import Fore, Style, Back, init

init(autoreset=True)

# Optional: Try to import OpenCV (for standard video feeds)
try:
    import cv2
    has_cv2 = True
except ImportError:
    has_cv2 = False

# Optional: Try to import ArducamDepthCamera (for TOF/Depth feed)
try:
    import ArducamDepthCamera as ac
    has_tof = True
except ImportError:
    has_tof = False

# Camera feed definitions: (name, device_id, aspect, mode)
CAMERA_FEEDS = [
    ("Front Camera", 0, "16:9", "opencv"),
    ("Rear Camera", 2, "16:9", "opencv"),
    ("TOF Camera", 0, "default", "tof"),
]

ASCII_CHARS = " .:-=+*#%@"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def getch():
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

def frame_to_ascii(frame, width=80, aspect="default"):
    h, w = frame.shape
    if aspect == "16:9":
        new_w = width
        new_h = int(new_w * 9 / 16 * 0.55)
    else:
        aspect_ratio = h / w
        new_w = width
        new_h = int(aspect_ratio * new_w * 0.55)
    import cv2
    resized = cv2.resize(frame, (new_w, max(1, new_h)))
    result = ""
    for row in resized:
        for pixel in row:
            result += ASCII_CHARS[int(pixel / 256 * len(ASCII_CHARS))]
        result += "\n"
    return result

def depth_to_color(val):
    # Map depth (0-255) to color: red->yellow->green->cyan->blue
    if val < 51:    return Fore.RED + Style.BRIGHT
    if val < 102:   return Fore.YELLOW + Style.BRIGHT
    if val < 153:   return Fore.GREEN + Style.BRIGHT
    if val < 204:   return Fore.CYAN + Style.BRIGHT
    return Fore.BLUE + Style.BRIGHT

def frame_to_colored_ascii(frame, width=80, aspect="default"):
    h, w = frame.shape
    aspect_ratio = h / w
    new_w = width
    new_h = int(aspect_ratio * new_w * 0.55) if aspect == "default" else int(new_w * 9 / 16 * 0.55)
    import cv2
    resized = cv2.resize(frame, (new_w, max(1, new_h)))
    result = ""
    for row in resized:
        for pixel in row:
            color = depth_to_color(pixel)
            char = ASCII_CHARS[int(pixel / 256 * len(ASCII_CHARS))]
            result += color + char + Style.RESET_ALL
        result += "\n"
    return result

def show_menu():
    idx = 0
    while True:
        clear()
        print(f"{Fore.CYAN}{Style.BRIGHT}=== DriveCore Camera Menu ==={Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Select a feed (←/→ or A/D), Enter to preview, Q to quit.{Style.RESET_ALL}\n")
        for i, (name, _, _, mode) in enumerate(CAMERA_FEEDS):
            disabled = ""
            if (mode == "tof" and not has_tof):
                disabled = Fore.LIGHTBLACK_EX + " (SDK Not Found)"
            if (mode == "opencv" and not has_cv2):
                disabled = Fore.LIGHTBLACK_EX + " (OpenCV Not Found)"
            arrow = (Fore.CYAN + "--->" if i == idx else " ")
            selected = (Back.CYAN + Fore.BLACK + Style.BRIGHT if i == idx else "")
            endsel = (Style.RESET_ALL if i == idx else "")
            print(f"{arrow} {selected}{name}{endsel}{disabled}")
        key = getch()
        if key and key.lower() == 'q':
            clear()
            print("Exited camera menu.")
            return None
        elif key in ['\x1b[C', 'd', 'D']:
            idx = (idx + 1) % len(CAMERA_FEEDS)
        elif key in ['\x1b[D', 'a', 'A']:
            idx = (idx - 1) % len(CAMERA_FEEDS)
        elif key in ['\r', '\n']:
            # Don't allow selection if required module is missing
            mode = CAMERA_FEEDS[idx][3]
            if (mode == "tof" and not has_tof) or (mode == "opencv" and not has_cv2):
                print(Fore.RED + "This camera mode is not available." + Style.RESET_ALL)
                time.sleep(1.5)
                continue
            clear()
            print(f"{Fore.YELLOW}Loading {CAMERA_FEEDS[idx][0]}...{Style.RESET_ALL}")
            time.sleep(0.4)
            return idx

def extract_scalar(val):
    while isinstance(val, (list, tuple)):
        if not val:
            return None
        val = val[0]
    return val

def show_camera_preview(idx):
    cam_name, cam_id, aspect, mode = CAMERA_FEEDS[idx]
    if mode == "opencv":
        if not has_cv2:
            print(f"{Fore.RED}OpenCV not found! Cannot open camera.{Style.RESET_ALL}")
            time.sleep(1.5)
            return
        cap = cv2.VideoCapture(cam_id)
        if not cap.isOpened():
            print(f"\n{Fore.RED}Could not open {cam_name} (index {cam_id})!{Style.RESET_ALL}")
            time.sleep(1.5)
            return
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print(f"{Fore.RED}Frame capture failed.{Style.RESET_ALL}")
                    time.sleep(0.5)
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ascii_frame = frame_to_ascii(gray, width=80, aspect=aspect)
                clear()
                print(f"{Fore.CYAN}{Style.BRIGHT}=== DriveCore Camera Preview ==={Style.RESET_ALL}\n")
                print(f"{Fore.YELLOW}[{cam_name} - {aspect}]{Style.RESET_ALL}\n")
                print(ascii_frame)
                print(f"{Fore.GREEN}[Q to quit preview, Enter/Menu to return]{Style.RESET_ALL}")

                # Handle key press for preview navigation
                import select, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    import tty
                    tty.setcbreak(fd)
                    r, _, _ = select.select([fd], [], [], 0.05)
                    if r:
                        ch = sys.stdin.read(1)
                        if ch.lower() == 'q':
                            break
                        elif ch in ['\r', '\n']:
                            break
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            clear()

    elif mode == "tof":
        if not has_tof:
            print(f"{Fore.RED}TOF SDK not found!{Style.RESET_ALL}")
            time.sleep(1.5)
            return

        width = 80
        max_distance = 4000  # or 2000, as appropriate

        print("Arducam Depth Camera Demo (CLI ASCII Heatmap Mode)")
        print("  SDK version:", ac.__version__)

        cam = ac.ArducamCamera()
        print("Attempting to open TOF camera...")
        ret = cam.open(ac.Connection.CSI, 4)
        print(f"cam.open() returned: {ret}")
        if ret != 0:
            print("Failed to open TOF camera. Error code:", ret)
            time.sleep(2)
            return

        print("Attempting to start TOF camera...")
        ret = cam.start(ac.FrameType.DEPTH)
        print(f"cam.start() returned: {ret}")
        if ret != 0:
            print("Failed to start TOF camera. Error code:", ret)
            cam.close()
            time.sleep(2)
            return

        print("Setting TOF RANGE control...")
        cam.setControl(ac.Control.RANGE, max_distance)
        r = cam.getControl(ac.Control.RANGE)

        info = cam.getCameraInfo()
        print(f"Camera resolution: {info.width}x{info.height}")

        # --- Helper function ---
        def extract_scalar(val):
            while isinstance(val, (list, tuple)):
                if not val:
                    return None
                val = val[0]
            return val

        try:
            framecount = 0
            while True:
                #print("Requesting TOF frame...")
                frame = cam.requestFrame(2000)
                #print("Frame:", type(frame))
                if frame is not None and isinstance(frame, ac.DepthData):
                    depth_buf = frame.depth_data
                    depth_buf = np.array(depth_buf)

                    # Always extract and check r immediately before scaling!
                    r_val = extract_scalar(r)
                    #print("DEBUG FINAL r before scale:", r_val, type(r_val))
                    if r_val is None or not isinstance(r_val, (int, float)):
                        print("ERROR: Camera range (r) is invalid. Exiting TOF preview.")
                        time.sleep(2)
                        break
                    scale = 255.0 / float(r_val)

                    result_image = (depth_buf * scale).astype(np.uint8)
                    mean_distance = np.mean(depth_buf)

                    ascii_frame = frame_to_colored_ascii(result_image, width=width)
                    clear()
                    print(f"{Fore.CYAN}{Style.BRIGHT}=== DriveCore TOF Camera ASCII Heatmap ==={Style.RESET_ALL}\n")
                    print(ascii_frame)
                    print(f"{Fore.CYAN}Mean distance: {mean_distance:.1f} mm{Style.RESET_ALL}\n")
                    print("[Q to quit preview, Enter/Menu to return]")
                    cam.releaseFrame(frame)
                    framecount += 1

                    # Key handling
                    import select, termios
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        import tty
                        tty.setcbreak(fd)
                        r_event, _, _ = select.select([fd], [], [], 0.05)
                        if r_event:
                            ch = sys.stdin.read(1)
                            if ch.lower() == 'q':
                                break
                            elif ch in ['\r', '\n']:
                                break
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                else:
                    print("Did not receive a valid ac.DepthData frame.")
                    time.sleep(1)
                    break
        except KeyboardInterrupt:
            pass
        finally:
            cam.stop()
            cam.close()
            clear()


def main():
    while True:
        idx = show_menu()
        if idx is None:
            break
        show_camera_preview(idx)

if __name__ == "__main__":
    main()
