import time

def current_time():
    return int(time.time() * 1000)

# ====== Send packets ======

# ------ Broadcast ------
def broadcast_packet(VIDEO_PORT, CONTROL_PORT):
    return {
        "type": "advertise",
        "video_port": VIDEO_PORT,
        "control_port": CONTROL_PORT
    }

# ------ Handshake ------
def auth_status_packet(STATUS: bool):
    return {
        "type": "auth_status",
        "status": STATUS
    }

def version_info_packet(VERSION: str, COMPATABLE: bool):
    return {
        "type": "version_info",
        "host-version": VERSION,
        "client_compatablity": COMPATABLE
    }

def setup_info_packet(VEHICLE_MODEL: str, CONTROL_SCHEME: str):
    return {
        "type": "setup_info",
        "vehicle_model": VEHICLE_MODEL,
        "control_scheme": CONTROL_SCHEME 
    }

def handshake_complete_packet(COMPLETE: bool):
    return {
        "type": "handshake_complete",
        "status": COMPLETE
    }

# ------ Keyboard Command ACK ------

def keyboard_command_ack_packet(cmd: str, current_esc_pw, current_servo_pw):
    return {
        "type": "command_ack",
        "command": cmd,
        "esc_pw": current_esc_pw,
        "servo_pw": current_servo_pw,
        "timestamp": current_time()
    }

# ------ Frame ------

def frame_ack_packet(n_chunks):
    return {
        "chunks": n_chunks,
        "timestamp": current_time()
    }