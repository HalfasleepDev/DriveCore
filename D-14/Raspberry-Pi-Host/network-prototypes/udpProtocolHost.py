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
def auth_status_packet(STATUS: str):
    return {
        "type": "auth_status",
        "status": STATUS
    }

def version_info_packet(VERSION: str):
    return {
        "type": "version_info",
        "version": VERSION
    }

def setup_info_packet(VEHICLE_MODEL: str, CONTROL_SCHEME: str):
    return {
        "type": "setup_info",
        "vehicle_model": VEHICLE_MODEL,
        "control_scheme": CONTROL_SCHEME
    }
