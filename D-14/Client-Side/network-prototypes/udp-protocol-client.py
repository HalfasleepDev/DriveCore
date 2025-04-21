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


# ====== Response packets ======
