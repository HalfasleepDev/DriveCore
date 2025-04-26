import socket
import json
import threading
import time

from udpProtocols import (credential_packet, version_request_packet, 
                               setup_request_packet, send_tune_data_packet,
                               current_time, keyboard_command_packet)

from appFunctions import save_settings, load_settings

#SETTINGS_FILE = "D-14/Client-Side/client-app/settings.json"

class NetworkManager:

    SETTINGS_FILE = "D-14/Client-Side/client-app/settings.json"
    CHUNK_SIZE = 1024 #1024
    BUFFER_SIZE = 65536 #65536

    def __init__(self, main_app_reference):
        self.app = main_app_reference

        # === Settings ===
        self.settings = load_settings(self.SETTINGS_FILE)

        # --- Network ---
        self.BROADCAST_PORT = self.settings["broadcast_port"]
        self.server_ip = None
        self.video_port = None
        self.control_port = None
        #self.app.handshake_done = threading.Event()

        # --- App Settings ---


    #self.app.logToSystem()
    # Step 1: Discover Broadcast
    def discover_host(self):
        #global server_ip, video_port, control_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.BROADCAST_PORT)) #'<broadcast>'
        self.app.logToSystem("Listening for broadcast. Please wait...", "BROADCAST")

        while True:
            data, addr = sock.recvfrom(1024)
            try:
                #causes a decode error
                payload = json.loads(data.decode())
                if payload.get("type") == "advertise":
                    self.server_ip = addr[0]
                    self.video_port = payload.get("video_port")
                    self.control_port = payload.get("control_port")
                    self.app.logToSystem(f"Found host: {self.server_ip}, Video: {self.video_port}, Control: {self.control_port}", "BROADCAST")
                    break
            except ConnectionRefusedError:
                #! Error message
                self.app.logToSystem("ConnectionRefusedError", "BROADCAST")
                self.app.logToSystem("[BROADCAST] ConnectionRefusedError", "ERROR")
                self.app.ui.showError(self, "CONNECTION ERROR", "ConnectionRefusedError. Could not connect to host.")
            '''
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            '''
        sock.close()

    # Step 2: Preform Handshake ---> pass the json settings
    def perform_handshake(self, username, password):
        handshake_status = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)

        def send(payload):
            sock.sendto(json.dumps(payload).encode(), (self.server_ip, self.control_port))

        pending_action = "send_credentials"

        while (not self.app.handshake_done.is_set()) & handshake_status:

            if pending_action == "send_credentials":
                send(credential_packet(username, password))
                self.app.logToSystem("Sent credentials to host", "HANDSHAKE")
                pending_action = None

            elif pending_action == "auth_failed":
                #! Error message
                self.app.logToSystem("Authentication failed", "HANDSHAKE")
                self.app.logToSystem("[HANDSHAKE] Authentication failed", "ERROR")
                self.app.ui.carConnectLoginWidget.show_error("Invalid credentials. Please try again.")
                self.app.ui.showError(self, "AUTHENTICATION ERROR", "Invalid credentials. Please try again.")
                
                handshake_status = False
                pending_action = None
            
            elif pending_action == "version_request":
                send(version_request_packet(self.app.client_ver))
                self.app.logToSystem("Sent a version request", "HANDSHAKE")
                self.app.logToSystem("Checking compatability...", "HANDSHAKE")
                pending_action = None
            
            elif pending_action == "version_request_failed":
                #! Error message
                self.app.logToSystem("Incompatable host version", "HANDSHAKE")
                self.app.logToSystem("[HANDSHAKE] Incompatable host version", "ERROR")
                self.app.ui.showError("COMPATABILITY ERROR", "Incompatable host version.")
                handshake_status = False
                pending_action = None

            elif pending_action == "send_client_version_failed":
                #! Error message
                self.app.logToSystem("Incompatable client version", "HANDSHAKE")
                self.app.logToSystem("[HANDSHAKE] Incompatable client version", "ERROR")
                self.app.ui.showError("COMPATABILITY ERROR", "Incompatable client version.")
                handshake_status = False
                pending_action = None
            
            elif pending_action == "setup_request":
                send(setup_request_packet())
                self.app.logToSystem("Sent a setup request", "HANDSHAKE")
                self.app.logToSystem("Waiting for vehicle details...", "HANDSHAKE")
                pending_action = None

            elif pending_action == "send_tune_data":
                # Servo & ESC
                min_duty_servo = self.settings["min_duty_servo"]
                max_duty_servo = self.settings["max_duty_servo"]
                neutral_servo = self.settings["neutral_duty_servo"]
                min_duty_esc = self.settings["min_duty_esc"]
                max_duty_esc = self.settings["max_duty_esc"]
                neutral_duty_esc = self.settings["neutral_duty_esc"]
                brake_esc = self.settings["brake_esc"]

                send(send_tune_data_packet("handshake", min_duty_servo, max_duty_servo, neutral_servo, 
                                        min_duty_esc, max_duty_esc, neutral_duty_esc, brake_esc))
                
                self.app.logToSystem("Sent vehicle tune data", "HANDSHAKE")
                pending_action = None

            elif pending_action == "handshake_complete":
                #* Done message
                self.app.logToSystem("Handshake is complete", "HANDSHAKE")
                self.app.logToSystem(f"Successfully connected to {self.app.vehicle_model}", "DEBUG")
                self.app.logToSystem(f"Using {self.app.control_scheme} control scheme", "DEBUG")
                
                pending_action = None
                handshake_status = False
                self.app.handshake_done.set()
                

            '''elif pending_action == "":
                pending_action = None'''
            
            # TODO: add other actions
            
            # === Inbound messages ===
            try:
                data, _ = sock.recvfrom(2048)
                payload = json.loads(data.decode())
                pending_action = self.handle_server_response(payload)

            except socket.timeout:
                self.app.logToSystem("Waiting for server...", "HANDSHAKE")
                continue

        sock.close()

    # Step 2.5: Handle Server Response From Handshake
    def handle_server_response(self, payload):
        # ------ Authentication ------
        if payload.get("type") == "auth_status":
            if payload.get("status"):
                #* Done message
                self.app.logToSystem("Authentication succsessful", "HANDSHAKE")

                self.app.ui.carConnectLoginWidget.error_label.hide()
                return "version_request"                                #* <--- pass
            else:

                return "auth_failed"
        
        # ------ Check Version Compatability ------
        elif payload.get("type") == "version_info":
            if payload.get("client_compatablity"):
                #* Done message
                self.app.logToSystem("Client version is compatable", "HANDSHAKE")

                if payload.get("host-version") in self.app.supported_ver:
                    #* Done message
                    self.app.logToSystem("Host version is compatable", "HANDSHAKE")

                    return "setup_request"                              #* <--- pass
                else:
                    return "version_request_failed"
            else:
                return "send_client_version_failed"
        # ------ Gather Vehicle Setup Info ------
        elif payload.get("type") == "setup_info":
            self.app.vehicle_model = payload.get("vehicle_model")
            self.app.control_scheme = payload.get("control_scheme")

            # Update label for vehicle
            self.app.ui.vehicleTypeLabel.setText(self.app.vehicle_model)

            #* Done message
            self.app.logToSystem("Gathered vehicle setup info", "HANDSHAKE")
            return "send_tune_data"                                     #* <--- pass
        
        elif payload.get("type") == "handshake_complete":
            if payload.get("status"):
                self.app.logToSystem("Applied vehicle tune data", "HANDSHAKE")

                return "handshake_complete"                             #* <--- pass
            
        elif payload.get("type") == "":
            return

    # Step 3: Send Different Types of Commands

    # Step 4: Send Keyboard Commands
    def send_keyboard_command(self, cmd: str, intensity):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        packet = keyboard_command_packet(cmd, intensity)
        now = int(time.time() * 1000)                                   # TODO: Maybe replace with 'current_time()'
        sock.sendto(json.dumps(packet).encode(), (self.server_ip, self.control_port))

        try:
            data, _ = sock.recvfrom(1024)
            
            ack = json.loads(data.decode())

            if ack.get("type") == "command_ack":
                #now = time.time()
                delay = now - ack["timestamp"]
                self.app.logToSystem(f"[ACK] Command: {ack['command']} | ESC: {ack["esc_pw"]} | SERVO: {ack["servo_pw"]} | RTT: {delay}ms", "INFO")
                #print(f"[ACK]: Command: {ack['command']} | ESC: {ack["esc_pw"]} | SERVO: {ack["servo_pw"]} | RTT: {delay}ms")
            
            #elif ack.get("type") == ""

        except socket.timeout:
            self.app.logToSystem(f"No ACK for command: {cmd}", "INFO")
            self.app.logToSystem(f"No ACK for command: {cmd}", "ERROR")
            #print("No ACK for command:", cmd)
        sock.close()

    # Step 5: Send Drive Assist Commands
    def send_drive_assist_command(self, cmd: str):
        if cmd == "emergency_stop":
            self.send_keyboard_command(cmd, None)
            # Todo: Add more triggers for UI?

    # Step 6: Applying Tune Data
    def tune_vehicle_command():
        pass

    # Step 7: 