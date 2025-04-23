import socket
import json
import time

from udpProtocolClient import (credential_packet, version_request_packet, 
                               setup_request_packet, send_tune_data_packet)

# ------ Network Settings ------
BROADCAST_PORT = 9999
CHUNK_SIZE = 1024
server_ip = None
video_port = None
control_port = None

# ------ Temp Variables ------
# --- Credentials --- 
username = "test"
password = "123"
# --- Version ---
client_ver = "1.3"
supported_ver = ["1.3"]
# --- PWM Tune Settings ---
MIN_DUTY_SERVO = 900   # Leftmost position in µs
MAX_DUTY_SERVO = 2100  # Rightmost position in µs 
NEUTRAL_SERVO = 1500   # Center position in µs

MIN_DUTY_ESC = 1310    # Minimum throttle
MAX_DUTY_ESC = 1750    # Maximum throttle
NEUTRAL_DUTY_ESC = 1500  # Neutral position
BRAKE_ESC = 1470     # Should trigger the brake in the esc
# --- Vehicle Setup ---
control_scheme = str
vehicle_model = str

def listen_for_broadcast():
    global server_ip, video_port, control_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    print("Listening for broadcast...")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            payload = json.loads(data.decode())

            if payload.get("type") == "advertise":
                server_ip = addr[0]
                video_port = payload["video_port"]
                control_port = payload["control_port"]
                print(f"Found host: {server_ip}, Video: {video_port}, Control: {control_port}")
                break
        except Exception as e:
            pass
    sock.close()

def send_handshake():
    handshake_status = True

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    
    def send(payload):
        sock.sendto(json.dumps(payload).encode(), (server_ip, control_port))

    pending_action = "send_credentials"

    while handshake_status:
        if pending_action == "send_credentials":
            send(credential_packet(username, password))
            pending_action = None

        elif pending_action == "auth_failed":
            #! Error message
            print("[Handshake][Error]: authentication failed")
            handshake_status = False
            pending_action = None
        
        elif pending_action == "version_request":
            send(version_request_packet(client_ver))
            pending_action = None
        
        elif pending_action == "version_request_failed":
            #! Error message
            print("[Handshake][Error]: Incompatable Host Ver")
            handshake_status = False
            pending_action = None

        elif pending_action == "send_client_version_failed":
            #! Error message
            print("[Handshake][Error]: Incompatable Client Ver")
            handshake_status = False
            pending_action = None
        
        elif pending_action == "setup_request":
            send(setup_request_packet())
            pending_action = None

        elif pending_action == "send_tune_data":
            send(send_tune_data_packet("handshake", MIN_DUTY_SERVO, MAX_DUTY_SERVO, NEUTRAL_SERVO, 
                                       MIN_DUTY_ESC, MAX_DUTY_ESC, NEUTRAL_DUTY_ESC, BRAKE_ESC))
            pending_action = None

        elif pending_action == "handshake_complete":
            #* Done message
            print("[Handshake]: handshake is complete")
            print(f"[Status]: Successfully connected to {vehicle_model}")
            print(f"[Status]: Using {control_scheme} control scheme")
            pending_action = None
            handshake_status = False

        # === Inbound messages ===
        try:
            data, _ = sock.recvfrom(2048)
            payload = json.loads(data.decode())
            pending_action = handle_server_response(payload)

        except socket.timeout:
            print("Waiting for server...")
            continue
    '''try:
        data, _ = sock.recvfrom(1024)
        payload = json.loads(data.decode())
        if payload.get("type") == "auth_status" and payload.get("status") == "ok":
            print("🤝 Handshake accepted.")
        else:
            print("❌ Handshake failed.")
    except socket.timeout:
        print("❌ No response from host.")'''

def handle_server_response(payload):
    global vehicle_model, control_scheme
    # ------ Authentication ------
    if payload.get("type") == "auth_status":
        if payload.get("status"):
            #* Done message
            print("[Handshake]: Authentication succsessful")
            return "version_request"                                #* <--- pass
        else:
            return "auth_failed"
    
    # ------ Check Version Compatability ------
    elif payload.get("type") == "version_info":
        if payload.get("client_compatablity"):
            # grab host ver here
            #* Done message
            print("[Handshake]: Client is compatable")
            if payload.get("host-version") in supported_ver:
                #* Done message
                print("[Handshake]: Host is compatable")
                return "setup_request"                              #* <--- pass
            else:
                return "version_request_failed"
        else:
            return "send_client_version_failed"
    # ------ Gather Vehicle Setup Info ------
    elif payload.get("type") == "setup_info":
        vehicle_model = payload.get("vehicle_model")
        control_scheme = payload.get("control_scheme")
        #* Done message
        print("[Handshake]: Gathered vehicle setup info")
        return "send_tune_data"                                     #* <--- pass
    
    elif payload.get("type") == "handshake_complete":
        if payload.get("status"):
            return "handshake_complete"                             #* <--- pass
        
    elif payload.get("type") == "":
        return

if __name__ == "__main__":
    listen_for_broadcast()
    send_handshake()
