"""
appClientNetwork.py

Client Host Communication system and operations (APP).

Author: HalfasleepDev
Created: 25-04-2025
"""

# === Imports ===
import socket
import json
import threading
import time
import asyncio

from PySide6.QtCore import QObject, Signal,QCoreApplication, Qt
from PySide6.QtWidgets import QApplication

from udpProtocols import (credential_packet, version_request_packet, 
                               setup_request_packet, send_tune_data_packet,
                               current_time, keyboard_command_packet)

from appFunctions import save_settings, load_settings, showError

# === Network Manager for Client-Host Communication ===
class NetworkManager(QObject):
    """
    Handles all network operations for the client app, including:
    - Broadcast discovery
    - Authentication and handshake with vehicle host
    - Sending control and tuning commands
    - Listening for acknowledgments and status

    Attributes:
        discovery_done_signal (Signal): Emitted after host is discovered.
        handshake_done_signal (Signal): Emitted after handshake succeeds.
    """

    SETTINGS_FILE = "D-14/Client-Side/client-app/settings.json"
    CHUNK_SIZE = 1024 #1024
    BUFFER_SIZE = 65536 #65536

    discovery_done_signal = Signal()
    handshake_done_signal = Signal()

    def __init__(self, main_app_reference):
        """
        Initialize network manager with app reference and loaded settings.

        Args:
            main_app_reference main.py: Reference to the main application.
        """
        super().__init__()
        self.app = main_app_reference

        # === Settings ===
        self.settings = load_settings(self.SETTINGS_FILE)

        # === Network Configuration ===
        self.BROADCAST_PORT = self.settings["broadcast_port"]
        self.server_ip = None
        self.video_port = None
        self.control_port = None
        self.heartbeat_port = None
        #self.app.handshake_done = threading.Event()
        self.discovery_done = threading.Event()

    # === Step 1: Discover Vehicle Host Over UDP Broadcast ===
    def discover_host(self):
        """
        Listens for UDP broadcast packets to detect the host vehicle.
        Emits discovery_done_signal upon successful connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20.0)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.BROADCAST_PORT)) #'<broadcast>'
        
        self.app.logSignal.emit("Listening for broadcast. Please wait...", "BROADCAST")

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    payload = json.loads(data.decode())
                    if payload.get("type") == "advertise":
                        self.server_ip = addr[0]
                        self.video_port = payload.get("video_port")
                        self.control_port = payload.get("control_port")
                        self.heartbeat_port = payload.get("heartbeat_port")
                        self.app.logSignal.emit(f"Found host: {self.server_ip}, Video: {self.video_port}, Control: {self.control_port}, HeartBeat: {self.heartbeat_port}", "BROADCAST")
                        
                        QCoreApplication.processEvents()
                        self.discovery_done_signal.emit()
                        break
                except ConnectionRefusedError:
                    ##! Connection refused by server
                    self.app.logSignal.emit("ConnectionRefusedError", "BROADCAST")
                    self.app.logSignal.emit("[BROADCAST] ConnectionRefusedError", "ERROR")
                    self.app.showErrorSignal.emit("CONNECTION ERROR", "ConnectionRefusedError. Could not connect to host.", "ERROR", 6000)
                    QApplication.restoreOverrideCursor()
                    break
                except Exception as e:
                    continue

            except socket.timeout:
                #! Broadcast timeout
                QCoreApplication.processEvents()
                self.app.logSignal.emit("Socket Timeout. 20s", "BROADCAST")
                self.app.logSignal.emit("[BROADCAST] Socket Timeout. 20s", "ERROR")
                self.app.showErrorSignal.emit("Broadcast Timeout", "Unable to locate broadcast from vehicle. Please make sure vehicle is online.", "WARNING", 8000)
                QApplication.restoreOverrideCursor()
                break
            
        sock.close()
        return     

    # === Step 2: Perform Handshake With Server ===
    def perform_handshake(self, username, password):
        """
        Sends authentication and configuration packets to the host in sequence.

        Args:
            username (str): Login username.
            password (str): Login password.
        """
        handshake_status = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        print(self.server_ip)

        def send(payload):
            sock.sendto(json.dumps(payload).encode(), (self.server_ip, self.control_port))

        pending_action = "send_credentials"

        while handshake_status:
            # === Outbound Client Commands ===
            if pending_action == "send_credentials":
                send(credential_packet(username, password))
                self.app.logSignal.emit("Sent credentials to host", "HANDSHAKE")
                pending_action = None
                QCoreApplication.processEvents()

            elif pending_action == "auth_failed":
                #! Invalid credential
                self.app.logSignal.emit("Authentication failed", "HANDSHAKE")
                self.app.logSignal.emit("[HANDSHAKE] Authentication failed", "ERROR")
                self.app.ui.carConnectLoginWidget.show_error("Invalid credentials. Please try again.")
                self.app.ui.showError(self, "AUTHENTICATION ERROR", "Invalid credentials. Please try again.")
                
                handshake_status = False
                pending_action = None
                QCoreApplication.processEvents()
            
            elif pending_action == "version_request":
                send(version_request_packet(self.app.client_ver))
                self.app.logSignal.emit("Sent a version request", "HANDSHAKE")
                self.app.logSignal.emit("Checking compatability...", "HANDSHAKE")
                pending_action = None
                QCoreApplication.processEvents()
            
            elif pending_action == "version_request_failed":
                #! Host version incompatibility
                self.app.logSignal.emit("Incompatable host version", "HANDSHAKE")
                self.app.logSignal.emit("[HANDSHAKE] Incompatable host version", "ERROR")
                self.app.ui.showError("COMPATABILITY ERROR", "Incompatable host version.")
                handshake_status = False
                pending_action = None
                QCoreApplication.processEvents()

            elif pending_action == "send_client_version_failed":
                #! Client version rejected
                self.app.logSignal.emit("Incompatable client version", "HANDSHAKE")
                self.app.logSignal.emit("[HANDSHAKE] Incompatable client version", "ERROR")
                self.app.ui.showError("COMPATABILITY ERROR", "Incompatable client version.")
                handshake_status = False
                pending_action = None
                QCoreApplication.processEvents()
            
            elif pending_action == "setup_request":
                send(setup_request_packet())
                self.app.logSignal.emit("Sent a setup request", "HANDSHAKE")
                self.app.logSignal.emit("Waiting for vehicle details...", "HANDSHAKE")
                pending_action = None
                QCoreApplication.processEvents()

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
                
                self.app.logSignal.emit("Sent vehicle tune data", "HANDSHAKE")
                pending_action = None
                QCoreApplication.processEvents()

            elif pending_action == "handshake_complete":
                #* Finalize handshake
                self.app.logSignal.emit("Handshake is complete", "HANDSHAKE")
                self.app.logSignal.emit(f"Successfully connected to {self.app.vehicle_model}", "DEBUG")
                self.app.logSignal.emit(f"Using {self.app.control_scheme} control scheme", "DEBUG")
                
                pending_action = None
                handshake_status = False
                self.app.VEHICLE_CONNECTION = True

                # FOR TUNE SETUP
                self.app.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = True

                self.handshake_done_signal.emit()
                QCoreApplication.processEvents()
                #self.app.handshake_done.set()
                

            '''elif pending_action == "":
                pending_action = None'''
            
            # TODO: add other actions
            
            # === Incoming Server Payloads ===
            try:
                data, _ = sock.recvfrom(1048)
                payload = json.loads(data.decode())
                pending_action = self.handle_server_response(payload)
                QCoreApplication.processEvents()

            except socket.timeout:
                if handshake_status:
                    self.app.logSignal.emit("Waiting for server...", "HANDSHAKE")
                    QCoreApplication.processEvents()
                continue

            finally:
                continue

        sock.close()
        QApplication.restoreOverrideCursor()
        return

    # === Step 2.5: Parse Server Payloads ===
    def handle_server_response(self, payload):
        """
        Interprets server responses and determines next action in handshake.

        Args:
            payload (dict): JSON-decoded response from server.

        Returns:
            str | None: Next action keyword for handshake loop.
        """

        # ------ Authentication ------
        if payload.get("type") == "auth_status":
            if payload.get("status"):
                #* Done message
                self.app.logSignal.emit("Authentication succsessful", "HANDSHAKE")

                self.app.ui.carConnectLoginWidget.error_label.hide()
                QCoreApplication.processEvents()
                return "version_request"                                #* <--- pass
            else:

                return "auth_failed"
        
        # ------ Check Version Compatability ------
        elif payload.get("type") == "version_info":
            if payload.get("client_compatablity"):
                #* Done message
                self.app.logSignal.emit("Client version is compatable", "HANDSHAKE")
                QCoreApplication.processEvents()

                if payload.get("host-version") in self.app.supported_ver:
                    #* Done message
                    self.app.logSignal.emit("Host version is compatable", "HANDSHAKE")
                    QCoreApplication.processEvents()

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
            self.app.logSignal.emit("Gathered vehicle setup info", "HANDSHAKE")
            QCoreApplication.processEvents()
            return "send_tune_data"                                     #* <--- pass
        
        elif payload.get("type") == "handshake_complete":
            if payload.get("status"):
                self.app.logSignal.emit("Applied vehicle tune data", "HANDSHAKE")
                QCoreApplication.processEvents()

                return "handshake_complete"                             #* <--- pass
            
        elif payload.get("type") == "":
            return

    # === Step 3: Send Keyboard Command ===
    def send_keyboard_command(self, cmd: str, esc_intensity, servo_intensity):
        """
        Sends keyboard control packet and updates local vehicle movement UI.

        Args:
            cmd (str): Movement command name.
            esc_intensity (float): ESC power value.
            servo_intensity (float): Steering power value.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        packet = keyboard_command_packet(cmd, esc_intensity, servo_intensity)
        now = int(time.time() * 1000)
        sock.sendto(json.dumps(packet).encode(), (self.server_ip, self.control_port))

        try:
            data, _ = sock.recvfrom(1024)
            
            ack = json.loads(data.decode())

            if ack.get("type") == "command_ack":
                if ack.get("command") == "Ignored command during emergency":
                    self.app.logSignal.emit(f"[ACK] DriveAssist: {ack.get("command")}", "WARN")
                
                if ack.get("command") == "ENABLE_DRIVE_ASSIST":
                    self.app.logSignal.emit("[ACK] DriveAssist: DriveAssist Enabled", "WARN")

                if ack.get("command") == "DISABLE_DRIVE_ASSIST":
                    self.app.logSignal.emit("[ACK] DriveAssist: DriveAssist Disabled", "WARN")
                #now = time.time()
                delay = ack["timestamp"] - now
                esc_pw = ack["esc_pw"]
                servo_pw = ack["servo_pw"]
                # If servo pwm is == to center
                if servo_pw == self.settings["neutral_duty_servo"]:
                    # change the intensity of servo to 0.0
                    self.app.ui.drivePage.servo_intensity = 0.0

                # UPDATE UI ELEMENTS
                self.app.updateVehicleMovement("UPDATE", esc_pw, servo_pw)
                self.app.logSignal.emit(f"[ACK] Command: {ack['command']} | ESC: {esc_pw} | SERVO: {servo_pw} | RTT: {delay}ms", "INFO")

            # EMERGENCY STOP FEATURES
            #elif ack.get("type") == "":

        except socket.timeout:
            self.app.logSignal.emit(f"No ACK for command: {cmd}", "INFO")
            self.app.logSignal.emit(f"No ACK for command: {cmd}", "ERROR")
        sock.close()
        return

    # === Step 4: Send Drive Assist Control ===
    def send_drive_assist_command(self, cmd: str):
        """
        Dispatches control signals related to Drive Assist mode.

        Args:
            cmd (str): Drive assist command like 'EMERGENCY_STOP'.
        """
        if cmd == "EMERGENCY_STOP":
            self.send_keyboard_command(cmd, None, None)
            # Todo: Add more triggers for UI?
        elif cmd == "CLEAR_EMERGENCY":
            pass
        elif cmd == "ENABLE_DRIVE_ASSIST":
            self.send_keyboard_command(cmd, None, None)
        elif cmd == "DISABLE_DRIVE_ASSIST":
            self.send_keyboard_command(cmd, None, None)

    # === Step 5: Apply Tune Parameters ===
    def tune_vehicle_command(self, mode:str, min_duty_servo=0, max_duty_servo=0, neutral_servo=0, 
                            min_duty_esc=0, neutral_duty_esc=0, max_duty_esc=0, brake_esc=0):
        """
        Sends tuning values for servo or ESC to the host vehicle.

        Args:
            mode (str): The mode (e.g., 'test_servo', 'save_esc').
            min_duty_servo (int): Min servo PWM.
            ...
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        packet = send_tune_data_packet(mode, min_duty_servo, max_duty_servo, neutral_servo, 
                                        min_duty_esc, max_duty_esc, neutral_duty_esc, brake_esc)
        sock.sendto(json.dumps(packet).encode(), (self.server_ip, self.control_port))
        self.settings = load_settings(self.SETTINGS_FILE)

        async def waitForTest():
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.app.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = False
            await asyncio.sleep(6)  
            self.app.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = True
            QApplication.restoreOverrideCursor()

        if mode == "test_servo":
            asyncio.run(waitForTest())
            self.app.logSignal.emit(f"[SERVO] Tested with {min_duty_servo}µs, {neutral_servo}µs, {max_duty_servo}µs", "DEBUG")
        
        elif mode == "test_esc":
            asyncio.run(waitForTest())
            self.app.logSignal.emit(f"[ESC] Tested with {min_duty_esc}µs, {neutral_duty_esc}µs, {max_duty_servo}µs, {brake_esc}µs", "DEBUG") 