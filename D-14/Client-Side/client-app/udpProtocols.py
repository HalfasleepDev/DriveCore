import time

def current_time():
    return int(time.time() * 1000)

# ====== Handshake Packets ======
# ------ Credentials ------
def credential_packet(username, password):
    return {
        "type": "credentials",
        "username": username,
        "password": password
    }

# ------ Host Version Request ------
def version_request_packet(CLIENT_VER: str):
    return {
        "type": "version_request",
        "client_ver": CLIENT_VER
    }

# ------ Host Setup Request ------
def setup_request_packet():
    return {
        "type": "setup_request"
    }

# ------ Apply Tune Settings ------ #! <--- Use this for applying tunes in setting page
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

# ====== Movement Packets ======
# ------ Keyboard Commands ------
def keyboard_command_packet(cmd: str, intensity):
    return {
        "type": "keyboard_command",
        "command": cmd,
        "intensity": intensity,
        "timestamp": current_time()
    }

# ------ Drive Assist Commands ------
def drive_assist_command_packet(cmd: str, intensity):
    return {
        "type": "drive_assist_command",
        "command": cmd,
        "intensity": intensity,
        "timestamp": current_time()
    }

# ------ Shutdown Command ------
def shutdown_host_packet():
    return {
        "type": "shutdown_systems"
    }
