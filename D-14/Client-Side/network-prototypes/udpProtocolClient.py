import time

def current_time():
    return int(time.time() * 1000)

# ====== Send packets ======
# ------ Handshake ------
def credential_packet(username, password):
    return {
        "type": "credentials",
        "username": username,
        "password": password
    }

def version_request_packet(CLIENT_VER: str):
    return {
        "type": "version_request",
        "client_ver": CLIENT_VER
    }

def setup_request_packet():
    return {
        "type": "setup_request"
    }

def send_tune_data_packet(PHASE: str, MIN_DUTY_SERVO, MAX_DUTY_SERVO, NEUTRAL_SERVO, 
                          MIN_DUTY_ESC, MAX_DUTY_ESC, NEUTRAL_DUTY_ESC, BRAKE_ESC):
    if PHASE == "handshake":
        return {
            "type": "handshake_tune_setup",
            "min_duty_servo": MIN_DUTY_SERVO,
            "max_duty_servo": MAX_DUTY_SERVO,
            "neutral_duty_servo": NEUTRAL_SERVO,
            "min_duty_esc": MIN_DUTY_ESC,
            "max_duty_esc": MAX_DUTY_ESC,
            "neutral_duty_esc": NEUTRAL_DUTY_ESC,
            "brake_esc": BRAKE_ESC
            # Add more ltr
        }

# ------ Keyboard Commands ------
def keyboard_command_packet(cmd: str, intensity: float):
    return {
        "type": "keyboard_command",
        "command": cmd,
        "intensity": intensity,
        "timestamp": current_time()
    }
