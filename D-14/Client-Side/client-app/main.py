"""
main.py

The main file for the Client App and system hooks.

Author: HalfasleepDev
Created: 19-02-2025
"""

# === Imports ===
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QTimer, Signal, QSize, QTime, 
    QUrl, QThread, Signal, QEvent, Qt, QThreadPool, QRunnable, Slot)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,QImage, QKeySequence, 
    QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, 
    QTransform, QKeyEvent)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout, QLineEdit, QMainWindow, 
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout, 
    QWidget)

import os
import sys
import cv2
import numpy as np
import ipaddress
import socket
import time
import json
import threading

from appFunctions import toggleDebugCV, showError, load_settings, save_settings
from appClientNetwork import NetworkManager
from appUiAnimations import AnimatedToolTip, LoadingScreen, install_hover_animation
from openCVFunctions import FrameProcessor
from MainWindow import Ui_MainWindow

# === Environment Variables ===
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_SCALE_FACTOR"] = "0.95"

# === Heartbeat Worker ===
class HeartbeatWorker(QObject):
    """
    A QObject-based worker class that periodically sends heartbeat packets to a server via UDP.

    This class is designed to run in a separate QThread and use QTimer to emit heartbeat signals
    at regular intervals.

    Attributes:
        finished (Signal): Emitted when the worker is stopped and cleaned up.
        server_ip (str): The IP address of the server to send heartbeat packets to.
        heartbeat_port (int): The port on the server to send heartbeat packets to.
        sock (socket.socket): The UDP socket used to send heartbeat messages.
        timer (QTimer): The timer used to schedule periodic heartbeat emissions.
        running (bool): Indicates whether the worker is actively sending heartbeats.
    """

    # === Signals ===
    finished = Signal()
    heartbeat_log_signal = Signal(str,str)

    def __init__(self, server_ip, heartbeat_port):
        """
        Initializes the HeartbeatWorker with server information.

        Args:
            server_ip (str): IP address of the heartbeat server.
            heartbeat_port (int): UDP port for sending heartbeat messages.
        """
        super().__init__()
        self.server_ip = server_ip
        self.heartbeat_port = heartbeat_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timer = None
        self.running = False

    def start(self):
        """
        Starts the QTimer to emit heartbeat signals at fixed intervals.
        This function should be called after moving the worker to a QThread.
        """
        # TODO: Move to log
        print("Pulse Start")
        #self.heartbeat_log_signal(f"[Heartbeat] Info: Pulse Start", "INFO")

        self.timer = QTimer(self)  # Create timer with self as parent (safe post-moveToThread)
        self.timer.setInterval(4000)  # Emit heartbeat every 4 seconds
        self.timer.timeout.connect(self.sendHeartbeat)

        self.running = True
        self.timer.start()

    def sendHeartbeat(self):
        """
        Sends a heartbeat packet to the server via UDP.

        The packet includes a type identifier and the current timestamp in milliseconds.
        """
        if not self.running:
            return

        packet = {
            "type": "heartbeat",
            "timestamp": int(time.time() * 1000)
        }

        try:
            self.sock.sendto(json.dumps(packet).encode(), (self.server_ip, self.heartbeat_port))

        except Exception as e:
            self.heartbeat_log_signal(f"[Heartbeat] Error: {e}", "ERROR")
            

    @Slot()
    def stop(self):
        """
        Stops the timer and socket, performs cleanup, and emits the `finished` signal.
        This is safe to call from another thread.
        """
        #self.heartbeat_log_signal("[Heartbeat] Stopping HeartbeatWorker", "ERROR")
        self.running = False

        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()

        self.sock.close()
        self.finished.emit()

# === Generic QRunnable Worker ===
class Worker(QRunnable):
    """
    A QRunnable-based worker that executes a given function with provided arguments.

    This class is meant to be submitted to a QThreadPool for concurrent execution. It 
    is useful for offloading work without blocking the GUI thread.

    Args:
        fn (Callable): The function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    """

    def __init__(self, fn, *args, **kwargs):
        """
        Initializes the Worker with the target function and arguments.

        Args:
            fn (Callable): The function to run in the background.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        """
        Executes the target function with the provided arguments.
        This method is automatically called when the QRunnable is executed.
        """
        self.fn(*self.args, **self.kwargs)

# === Video Thread (UDP Video Receiver) ===
class VideoThread(QThread):
    """
    A threaded UDP video receiver that reconstructs JPEG frames from chunked packets.

    This class listens on a specified UDP port, handles header metadata to reassemble
    frames, decodes them, and emits QImage frames for GUI display. If the connection
    times out, it emits a heartbeat signal to indicate disconnection.

    Signals:
        frame_received (QImage): Emitted when a new video frame is reconstructed.
        heartbeat_signal (bool): Emitted with False when server disconnect is detected.

    Attributes:
        server_ip (str): IP of the video stream server.
        video_port (int): Port to listen on for video data.
        processor (Optional): A processing pipeline for image enhancement or AI.
        fps (float): Current frame rate (frames per second).
        last_video_latency_ms (int): Time in ms between sending and receiving frame.
    """

    frame_received = Signal(QImage)
    heartbeat_signal = Signal(bool)  # Sends a flag that the Host has been disconnected

    def __init__(self, server_ip, video_port):
        """
        Initializes the UDP socket and sets up receiver state.

        Args:
            server_ip (str): IP address of the server.
            video_port (int): UDP port to bind and receive video frames.
        """
        super().__init__()
        self.server_ip = server_ip
        self.video_port = video_port
        self.running = True
        self.processor = None

        self.disconnect = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.settimeout(8.0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.video_port))

        self.total_chunks = 0
        self.current_chunks = 0
        self.frame_chunks = []
        self.last_frame_timestamp = 0

        self.last_frame_time = time.time()
        self.frame_counter = 0
        self.fps = 0
        self.last_video_latency_ms = 0

    def set_processor(self, processor):
        """
        Sets the processor instance used for frame enhancement or AI processing.

        Args:
            processor: A class with a method `detect_floor_region(frame)` that processes frames.
        """
        self.processor = processor

    def run(self):
        """
        Main thread loop: receives packets, assembles frames, processes them, and emits the result.

        Handles JSON headers, collects JPEG frame chunks, and manages timeout-triggered disconnects.
        """
        BUFFER_SIZE = 65536

        while self.running:
            try:
                data, _ = self.sock.recvfrom(BUFFER_SIZE)

                # Try decoding a JSON header packet
                '''try:
                    header = json.loads(data.decode())
                    self.total_chunks = header["chunks"]
                    self.last_frame_timestamp = header["timestamp"]
                    self.frame_chunks = [None] * self.total_chunks  # Preallocate
                    self.current_chunks = 0
                    continue
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                # Collect JPEG chunks
                self.frame_chunks.append(data)
                self.current_chunks += 1'''
                try:
                    header = json.loads(data.decode())
                    self.total_chunks = header["chunks"]
                    self.last_frame_timestamp = header["timestamp"]
                    self.frame_chunks = [None] * self.total_chunks  # Preallocated
                    self.current_chunks = 0
                    continue
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                # Only accept chunk if frame is initialized
                if self.frame_chunks and 0 <= self.current_chunks < self.total_chunks:
                    self.frame_chunks[self.current_chunks] = data
                    self.current_chunks += 1
                else:
                    # Desync or uninitialized — reset
                    #print("Dropped chunk due to out-of-range or uninitialized state")
                    self.frame_chunks = []
                    self.current_chunks = 0
                    #self.total_chunks = 0

                # Drop the frame if too many chunks are received
                if self.current_chunks > self.total_chunks:
                    self.frame_chunks.clear()
                    self.current_chunks = 0
                    continue

                # Reassemble and display complete frame
                if self.current_chunks == self.total_chunks:
                    frame_data = b''.join(self.frame_chunks)
                    now = int(time.time() * 1000)
                    self.last_video_latency_ms = now - self.last_frame_timestamp

                    # Decode JPEG to OpenCV frame
                    nparr = np.frombuffer(frame_data, np.uint8)
                    try:
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    except cv2.error:
                        frame = None
                    if frame is None:
                        self.frame_chunks = []
                        self.current_chunks = 0
                        continue
                    #frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # --- Update FPS ---
                        self.frame_counter += 1
                        now = time.time()
                        elapsed = now - self.last_frame_time
                        if elapsed >= 1.0:
                            self.fps = self.frame_counter / elapsed
                            self.frame_counter = 0
                            self.last_frame_time = now

                        # --- Overlay FPS and latency ---
                        overlay = f"FPS: {self.fps:.1f} | Latency: {self.last_video_latency_ms} ms"
                        cv2.putText(frame, overlay, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 255, 0), 1, cv2.LINE_AA)

                        # --- Optional Frame Processing (AI/Floor Detection) ---
                        if self.processor:
                            frame = self.processor.detect_floor_region(frame)

                        # Convert to QImage and emit
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = frame.shape
                        bytes_per_line = ch * w
                        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        self.frame_received.emit(q_img)

                    # Reset state for next frame
                    self.frame_chunks = []
                    self.current_chunks = 0

            except BlockingIOError:
                # No data yet — non-blocking mode
                pass

            except socket.timeout:
                # Server likely disconnected
                self.running = False
                self.heartbeat_signal.emit(False)
                self.sock.close()

    def stop(self):
        """
        Stops the video thread and closes the UDP socket.
        """
        self.running = False
        self.wait()
        self.sock.close()

# === Main Application Window ===
class MainWindow(QMainWindow):
    """
    The primary application window for the client GUI.

    Manages the full lifecycle of the client-side application, including:
    - Loading and saving settings from a JSON file
    - Managing vehicle connection and authentication
    - Displaying video streams and telemetry from the host vehicle
    - Configuring OpenCV debug overlays and drive assist features
    - Controlling navigation and layout of UI pages
    - Handling threaded background operations (heartbeat, handshake, tuning)

    Attributes:
        SETTINGS_FILE (str): Path to the settings JSON file.
        VEHICLE_CONNECTION (bool): Whether the vehicle is currently connected.
        OPENED_DRIVE_PAGE (bool): Flag indicating if the drive page has been opened.
        THREAD_RUNNING (bool): Flag for thread activity.
        OBJECT_VIS_ENABLED, FLOOR_VIS_ENABLED, ... (bool): OpenCV visual debug flags.
        IS_DRIVE_ASSIST_ENABLED (bool): State of Drive Assist mode.
        logSignal (Signal): Emits log messages to system log widgets.
        displayVehicleMovementSignal (Signal): Updates vehicle movement UI.
        showErrorSignal (Signal): Triggers global error popups.
    """
    # === Configuration Paths ===
    SETTINGS_FILE = "D-14/Client-Side/client-app/settings.json"

    # === Status Flags ===
    VEHICLE_CONNECTION = False
    OPENED_DRIVE_PAGE = False
    THREAD_RUNNING = False

    # === OpenCV Debug Visuals ===
    OBJECT_VIS_ENABLED = False
    FLOOR_VIS_ENABLED = False
    KALMAN_CENTER_VIS_ENABLED = False
    AMBIENT_VIS_ENABLED = False
    FLOOR_SAMPLE_VIS_ENABLED = False
    PATH_VIS_ENABLED = False
    COLLISION_ASSIST_ENABLED = False
    alert_triggered = False
    alert_cooldown = False

    # === Drive Assist State ===
    IS_DRIVE_ASSIST_ENABLED = False

    # === UI Signals ===
    logSignal = Signal(str, str)
    displayVehicleMovementSignal = Signal(str, int, int)
    showErrorSignal = Signal(str, str, str, int) # Title, Message, Severity, Duration

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.threadpool = QThreadPool.globalInstance()

        # === App Version Info ===
        self.client_ver = "1.3.0"
        self.supported_ver = ["1.3.0"]  # Supported Host Versions

        # === Load Configuration ===
        self.settings = load_settings(self.SETTINGS_FILE)

        # === Host Info Placeholders ===
        self.vehicle_model = str
        self.control_scheme = str
        self.curveType = str    # Accel curve

        # === Button Animations ===
        animButtons = [self.ui.homeBtn, self.ui.settingsBtn, self.ui.driveBtn, self.ui.logBtn, self.ui.openCVSettingsBtn,
            self.ui.vehicleTuningBtn, self.ui.ObjectVisBtn, self.ui.FloorVisBtn, self.ui.KalmanCenterVisBtn, 
            self.ui.AmbientVisBtn, self.ui.FloorSampleVisBtn, self.ui.PathVisBtn, self.ui.CollisionAssistBtn,
            self.ui.emergencyDisconnectBtn
            ]
        
        for btn in animButtons:
            install_hover_animation(btn)

        # === Networking Setup ===
        self.handshake_done = threading.Event()
        self.network = NetworkManager(self)

        # === Load Saved Credentials ===
        self.load_credentials() # Load Credentials On Startup

        # === Signal & UI Connections ===
        self.ui.carConnectLoginWidget.connect_btn.clicked.connect(self.attempt_connection)  # Car Login Button
        self.logSignal.connect(self.logToSystem)    # Log to all systems
        self.ui.projectInfoWidgetCustom.logErrorSignal.connect(self.logToSystem)    # Car Login Error to system
        self.showErrorSignal.connect(self.showGlobalError)  # Global popup
        
        # === Main Left Menu Navigation ===
        self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
        self.ui.homeBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.homeBtn, self.ui.homePage))
        self.ui.settingsBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.settingsBtn, self.ui.settingsPage))
        self.ui.settingsBtn.clicked.connect(lambda: self.iniSettingsPage())
        self.ui.driveBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.driveBtn, self.ui.drivePage))
        self.ui.driveBtn.clicked.connect(lambda: self.iniDrivePage())
        self.ui.logBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.logBtn, self.ui.systemLogPage))

        # === Settings Page Navigation === 
        self.ui.openCVSettingsBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
        self.ui.openCVSettingsBtn.clicked.connect(lambda: self.handleSettingsNav(self.ui.openCVSettingsBtn, self.ui.OpenCVSettingsPage, 2))
        self.ui.vehicleTuningBtn.clicked.connect(lambda: self.handleSettingsNav(self.ui.vehicleTuningBtn, self.ui.VehicleTuningSettingsPage, 3))
        
        # === OpenCV Toggle Buttons ===
        self.ui.ObjectVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(1))
        self.ui.FloorVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(2))
        self.ui.KalmanCenterVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(3))
        self.ui.AmbientVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(4))
        self.ui.FloorSampleVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(5))
        self.ui.PathVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(6))
        self.ui.CollisionAssistBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(7))

        # === HSV Sliders (OpenCV) ===
        # --- Set range for sensitivity tuning ---
        self.ui.HRowSlider.setRange(0, 50)
        self.ui.SRowSlider.setRange(0, 100)
        self.ui.VRowSlider.setRange(0, 100)

        self.ui.HRowSlider.valueChanged.connect(lambda val: self.ui.HRowValueLabel.setText(str(val)))
        self.ui.SRowSlider.valueChanged.connect(lambda val: self.ui.SRowValueLabel.setText(str(val)))
        self.ui.VRowSlider.valueChanged.connect(lambda val: self.ui.VRowValueLabel.setText(str(val)))

        # --- Set default values ---
        self.ui.HRowSlider.setValue(35)
        self.ui.SRowSlider.setValue(40)
        self.ui.VRowSlider.setValue(50)

        # === Vehicle Tuning Page Setup ===
        self.ui.VehicleTuningSettingsPage.set_curve_selection(self.settings["acceleration_curve"])
        self.ui.VehicleTuningSettingsPage.previewServoSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.servo_mid_tuner.saveServoMidpointSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.accelCurveSignal.connect(self.setSaveCurveType) #* DONE
        self.ui.VehicleTuningSettingsPage.servoTuneSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.escTuneSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.set_default_tune_page(
            self.settings["min_duty_esc"], self.settings["neutral_duty_esc"], 
            self.settings["max_duty_esc"], self.settings["brake_esc"], 
            self.settings["min_duty_servo"], self.settings["neutral_duty_servo"], 
            self.settings["max_duty_servo"], self.settings["broadcast_port"]
        )
        self.ui.VehicleTuningSettingsPage.updateBroadcastPortSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.logToSystemSignal.connect(self.logToSystem) #* DONE

        # === Emergency Disconnect Button ===
        self.ui.emergencyDisconnectBtn.clicked.connect(lambda: self.emergencyDisconnect())

        # === OpenCV Runtime Variables ===
        self.timer = QTimer()
        self.timer.start(30)
        self.frame_counter = 0
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=100, detectShadows=False)
        self.last_floor_contour = None
        self.alert_line_y = 680 # Trigger line for object detection

        # === Drive Assist Widget ===
        self.tooltip = AnimatedToolTip("", self)
        self.ui.alertAssistWidget.installEventFilter(self)
        self.ui.alertAssistWidget.setToolTip("Turn On/Off collision braking")
        self.ui.driveAssistWidget.toggle_button.clicked.connect(lambda: self.toggleSettingOpenCvBtns(8))

        # === Alert Cooldown Timer ===
        self.alert_cooldown_timer = QTimer()
        self.alert_cooldown_timer.setSingleShot(True)
        self.alert_cooldown_timer.timeout.connect(self.reset_alert_cooldown)

    # === Startup Logging ===
    def onStartup(self):
        """
        Logs the available thread count on startup.
    
        Used to verify multithreading capabilities on client launch.
        """
        thread_count = self.threadpool.maxThreadCount()
        self.logToSystem(f"Multithreading with maximum {thread_count} threads", "DEBUG")
    
    # === Tooltip Event Filter for Custom Hover Popups ===
    def eventFilter(self, watched, event):
        """
        Custom tooltip event filter for UI widgets.

        Args:
            watched (QObject): The object being observed.
            event (QEvent): The event that occurred.

        Returns:
            bool: True if custom tooltip was shown, False otherwise.
        """
        if event.type() == QEvent.ToolTip:
            if isinstance(watched, QWidget):
                tooltip_text = watched.toolTip()
                self.tooltip.setText(tooltip_text)

                # Show beside the widget
                pos = watched.mapToGlobal(watched.rect().topRight())
                self.tooltip.show_tooltip(pos)
                return True  # Override default tooltip behavior

        elif event.type() == QEvent.Leave:
            self.tooltip.hide_tooltip()

        return super().eventFilter(watched, event)
    
    # === Settings Page Navigation ===
    def handleSettingsNav(self, active_btn, target_page, infoIndex: int):
        """
        Handles switching between settings sub-pages and their corresponding info views.

        Args:
            active_btn (QPushButton): The button that triggered the change.
            target_page (QWidget): The target stacked page widget.
            infoIndex (int): Index of the information view in the side panel.
        """
        # Reset all button styles
        for btn in [self.ui.openCVSettingsBtn, self.ui.vehicleTuningBtn]:
            btn.setStyleSheet("QPushButton{background-color: #1e1e21;}")

            # Highlight active button
            active_btn.setStyleSheet("QPushButton{background-color: #7a63ff;}")

            # Switch stacked widget page
            self.ui.settingsStackedWidget.setCurrentWidget(target_page)

            # Adjust spacing based on index
            self.ui.settingsInfoStackedWidget.setCurrentIndex(infoIndex)
            if infoIndex == 3:
                self.ui.verticalLayout_15.removeItem(self.ui.verticalSpacer_8)
                self.ui.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                self.ui.verticalLayout_15.insertItem(3, self.ui.verticalSpacer_8)
            else:
                self.ui.verticalLayout_15.removeItem(self.ui.verticalSpacer_8)
                self.ui.verticalSpacer_8 = QSpacerItem(20, 431, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                self.ui.verticalLayout_15.insertItem(3, self.ui.verticalSpacer_8)
    
    # === Main Page Navigation ===
    def handleLeftMenuNav(self, active_btn, target_page):
        """
        Handles navigation from the left-side main menu.

        Args:
            active_btn (QPushButton): The button clicked.
            target_page (QWidget): The page to display.
        """
        for btn in [self.ui.homeBtn, self.ui.settingsBtn, self.ui.driveBtn, self.ui.logBtn]:
            btn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")

            # Highlight active button
            active_btn.setStyleSheet("QPushButton{background-color: #7a63ff;}")

            # Switch page
            self.ui.stackedWidget.setCurrentWidget(target_page)
    
    # === Toggle OpenCV Debug Modes ===
    def toggleSettingOpenCvBtns(self, select):
        """
        Toggles visualization/debug settings for OpenCV modes.
        Works as a pseudo Drive Assist Enable

        Args:
            select (int): Identifier for the selected OpenCV mode.
        """
        #self.IS_DRIVE_ASSIST_ENABLED = True
        if self.VEHICLE_CONNECTION:
            match select:
                case 1:
                    self.OBJECT_VIS_ENABLED = toggleDebugCV(self.ui.ObjectVisBtn, self.OBJECT_VIS_ENABLED, "Object Vis: ")
                case 2:
                    self.FLOOR_VIS_ENABLED = toggleDebugCV(self.ui.FloorVisBtn, self.FLOOR_VIS_ENABLED, "Floor Vis: ")
                case 3:
                    self.KALMAN_CENTER_VIS_ENABLED = toggleDebugCV(self.ui.KalmanCenterVisBtn, self.KALMAN_CENTER_VIS_ENABLED, "Kalman Center Vis: ")
                case 4:
                    self.AMBIENT_VIS_ENABLED = toggleDebugCV(self.ui.AmbientVisBtn, self.AMBIENT_VIS_ENABLED, "Ambient Vis: ")
                case 5:
                    self.FLOOR_SAMPLE_VIS_ENABLED = toggleDebugCV(self.ui.FloorSampleVisBtn, self.FLOOR_SAMPLE_VIS_ENABLED, "Floor Sample Vis: ")
                case 6:
                    self.PATH_VIS_ENABLED = toggleDebugCV(self.ui.PathVisBtn, self.PATH_VIS_ENABLED, "Path Vis: ")
                case 7 | 8:
                    self.COLLISION_ASSIST_ENABLED = toggleDebugCV(self.ui.CollisionAssistBtn, self.COLLISION_ASSIST_ENABLED, "")
                    self.COLLISION_ASSIST_ENABLED = self.ui.driveAssistWidget.toggle_assist()
                    self.IS_DRIVE_ASSIST_ENABLED = self.ui.driveAssistWidget.toggle_assist()
                    if self.IS_DRIVE_ASSIST_ENABLED:
                        self.network.send_drive_assist_command("ENABLE_DRIVE_ASSIST")
                    else:
                        self.network.send_drive_assist_command("DISABLE_DRIVE_ASSIST")

    
    # === Central Logging Handler ===
    def logToSystem(self, message: str, type: str): #? FIXME: Vehicle control logs could slow down the thread
        """
        Logs a message to the system and auxiliary log widgets.

        Args:
            message (str): The message to log.
            type (str): Log type (e.g., INFO, WARN, BROADCAST).
        """
        self.ui.systemLogPage.log(message, type)
        match type:
            case "BROADCAST" | "HANDSHAKE":
                self.ui.networkConnectionLogWidget.add_log(f"[{type}] {message}")
            case "INFO" | "WARN":
                self.ui.vehicleSystemAlertLogWidget.add_log(f"[{type}] {message}")
                #QCoreApplication.processEvents()
        QCoreApplication.processEvents()

    # === Show Error Dialog Globally ===
    def showGlobalError(self, title: str, message: str, severity: str, duration =0):
        """
        Displays a global error popup over the central widget.

        Args:
            title (str): Title of the error.
            message (str): Body of the error.
            severity (str): Type of error (INFO, ERROR, etc).
            duration (int, optional): Duration in milliseconds to show the popup. Defaults to 0.
        """
        showError(self.ui.centralwidget, title, message, severity, duration)

    # === Save Selected Curve Type ===
    def setSaveCurveType(self, curve: str):
        """
        Sets the curve type and saves it to the settings file.

        Args:
            curve (str): Name of the selected acceleration curve.
        """
        self.ui.drivePage.setCurveType = curve
        self.settings["acceleration_curve"] = curve
        save_settings(self.settings, self.SETTINGS_FILE)

    # === Auto-fill Credentials on Startup ===
    def load_credentials(self):
        """
        Loads saved credentials from settings and fills in the login form.
        """
        self.ui.carConnectLoginWidget.username_input.setText(self.settings["username"])
        self.ui.carConnectLoginWidget.password_input.setText(self.settings["password"])

    # === Begin Connection Sequence ===
    def attempt_connection(self):
        """
        Validates login fields and begins vehicle discovery and handshake.
        """
        # --- Get username and password from the input fields ---
        username = self.ui.carConnectLoginWidget.username_input.text().strip()
        password = self.ui.carConnectLoginWidget.password_input.text().strip()

        # --- Check that username and/or password is not empty ---
        if not username or not password:
            self.ui.carConnectLoginWidget.show_error("Please enter both username and password.")
            showError(self.ui.centralwidget, "Login Error", "Please enter both username and password.", "INFO", 6000)
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)


            self.threadpool.start(Worker(self.network.discover_host))
            #self.threadpool.waitForDone()
            self.network.discovery_done_signal.connect(lambda: self.threadpool.start(Worker(lambda: self.network.perform_handshake(username, password))))
            #self.threadpool.waitForDone()
            self.network.handshake_done_signal.connect(lambda: self.connection_done(username, password))
            
            #QApplication.restoreOverrideCursor()

    # === Finalize Connection ===
    def connection_done(self, username, password):
       """
        Called after successful connection; sets up heartbeat thread and saves credentials.

        Args:
            username (str): The username entered by the user.
            password (str): The password entered by the user.
        """
       QApplication.restoreOverrideCursor()
       #QCoreApplication.processEvents()
       if self.VEHICLE_CONNECTION:
                self.heartbeat_thread = QThread()
                self.heartbeat_worker = HeartbeatWorker(self.network.server_ip, self.network.heartbeat_port)
                self.heartbeat_worker.moveToThread(self.heartbeat_thread)

                self.heartbeat_thread.started.connect(self.heartbeat_worker.start)
                

                self.heartbeat_worker.finished.connect(self.heartbeat_thread.quit)
                self.heartbeat_worker.finished.connect(self.heartbeat_worker.deleteLater)
                self.heartbeat_thread.finished.connect(self.heartbeat_thread.deleteLater)

                self.heartbeat_thread.start()

                #TODO: Fix the log signal for heartbeat
                #self.heartbeat_worker.heartbeat_log_signal.connect(self.logToSystem)

                self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = True
                self.settings["username"] = username
                self.settings["password"] = password
                save_settings(self.settings, self.SETTINGS_FILE)

                showError(self.ui.centralwidget, "Connection Succes!", f"Established and secured connection to vehicle {self.vehicle_model}", "SUCCESS", 3000)
                
                try:
                    self.threadpool.clear()
                except AttributeError:
                    pass
                self.threadpool.waitForDone()

    # === Initialize Drive Page ===
    def iniDrivePage(self):
        """
        Initializes and starts the video stream, processor, and drive UI.

        Checks for vehicle connection and hardware readiness before launching the
        drive view. Starts the video thread and connects signals to update the UI.
        """
        if self.VEHICLE_CONNECTION and self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY:
            print(self.network.server_ip)
            print(self.network.video_port)

            '''self.thread = VideoThread(self.network.server_ip, self.network.video_port)
            self.processor = FrameProcessor(self, self.thread)
            self.processor.initKalmanFilter()
            self.thread.set_processor(self.processor)'''
            '''self.thread.frame_received.connect(self.update_frame)
            self.thread.heartbeat_signal.connect(self.checkHeartBeat)'''

            if not self.OPENED_DRIVE_PAGE:
                self.thread = VideoThread(self.network.server_ip, self.network.video_port)
                self.processor = FrameProcessor(self, self.thread)
                self.processor.initKalmanFilter()
                self.thread.set_processor(self.processor)
                self.thread.start()
                self.THREAD_RUNNING = True
                self.OPENED_DRIVE_PAGE = True
            
            self.thread.frame_received.connect(self.update_frame)
            self.thread.heartbeat_signal.connect(self.checkHeartBeat)
            self.updateVehicleMovement("SET")
            self.ui.videoStreamWidget.setStyleSheet("QWidget{background-color:  #0c0c0d;}")
            self.ui.drivePage.commandSignal.connect(self.changeKeyInfo)
            #? Maybe hindering performance because it is running on the same main thread?
            self.ui.drivePage.commandSignal.connect(self.network.send_keyboard_command)
            
        else:
            self.ui.videoStreamLabel.setStyleSheet("QLabel{color: #1e1e21;}")

    # === Update Directional Button States ===
    def changeKeyInfo(self, command, intensity):
        """
        Updates the UI to highlight the active directional control based on command.

        Args:
            command (str): The driving command (e.g., 'UP', 'LEFT', 'BRAKE').
            intensity (int): The intensity of the command (currently unused).
        """
        if command == "UP":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #7a63ff;}")
            #print('t')
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
        elif command == "DOWN":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #7a63ff;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
        elif command == "LEFT":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #7a63ff;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
        elif command == "RIGHT":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #7a63ff;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
        elif command == "NEUTRAL":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #7a63ff;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
        elif command == "BRAKE":
            self.ui.accelerateBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnLeftBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.reverseBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.turnRightBtn.setStyleSheet("QPushButton{color: #f1f3f3;}")
            self.ui.brakeBtn.setStyleSheet("QPushButton{color: #7a63ff;}") 

    # === Update or Reset Vehicle Display Widgets ===
    def updateVehicleMovement(self, mode: str, esc_pw=None, servo_pw=None):
        """
        Updates vehicle telemetry widgets (speedometer, steering, gear selector).

        Args:
            mode (str): One of 'SET', 'UPDATE', or 'RESET' to determine update type.
            esc_pw (int, optional): ESC pulse width, used in 'UPDATE' mode.
            servo_pw (int, optional): Servo pulse width, used in 'UPDATE' mode.
        """
        match mode:
            case "SET":
                # Update Settings to get current
                self.settings = load_settings(self.SETTINGS_FILE)
                # Speedometer
                self.ui.vehicleSpeedometerWidget.min_us = self.settings["min_duty_esc"]
                self.ui.vehicleSpeedometerWidget.max_us = self.settings["max_duty_esc"]
                self.ui.vehicleSpeedometerWidget.neutral_us = self.settings["neutral_duty_esc"]
                self.ui.vehicleSpeedometerWidget.vehicleConnect = True
                # Steer angle
                self.ui.steerPathWidget.min_us = self.settings["min_duty_servo"]
                self.ui.steerPathWidget.max_us = self.settings["max_duty_servo"]
                self.ui.steerPathWidget.center_us = self.settings["neutral_duty_servo"]
                # PRND
                self.ui.PRNDWidget.set_gear("N")
            
            case "UPDATE":
                # Speedometer
                self.ui.vehicleSpeedometerWidget.target_us = esc_pw # <--- ESC US
                # Steer angle
                self.ui.steerPathWidget.set_steering_us(servo_pw)
                # PRND
                if esc_pw > self.ui.vehicleSpeedometerWidget.neutral_us:
                    self.ui.PRNDWidget.set_gear("D")
                elif esc_pw == self.ui.vehicleSpeedometerWidget.neutral_us:
                    self.ui.PRNDWidget.set_gear("N")
                elif esc_pw < self.ui.vehicleSpeedometerWidget.neutral_us:
                    if esc_pw == self.settings["brake_esc"]:
                        self.ui.PRNDWidget.set_gear("P")
                    else:
                        self.ui.PRNDWidget.set_gear("R")
            
            case "RESET":
                self.ui.vehicleSpeedometerWidget.vehicleConnect = False

    # === Prepare Settings Page ===
    def iniSettingsPage(self):
        """
        Initializes the settings page if the vehicle is connected.

        Currently enables vehicle tuning settings if the heartbeat is alive.
        """
        if self.VEHICLE_CONNECTION:
            #? Check if vehicle heartbeat is alive --> send a command such as "heartbeat"
            self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = True

    # === Tune Vehicle Parameters ===
    def tuneVehicle(self, mode: str, min=0, mid=0, max=0, brake=0, port=0):
        """
        Sends tuning commands to the vehicle and updates settings.

        Args:
            mode (str): Type of tuning operation (e.g., 'test_servo', 'save_esc').
            min (int): Minimum PWM value.
            mid (int): Midpoint PWM value.
            max (int): Maximum PWM value.
            brake (int): Brake PWM value.
            port (int): Broadcast port (used in 'update_port').
        """
        if self.VEHICLE_CONNECTION:
            match mode:
                case "servo_mid_cal":
                    self.network.tune_vehicle_command(mode, min)
                    self.logToSystem(f"[SERVO] Servo tested at {min} µs", "DEBUG")
                
                case "save_mid_servo":
                    self.network.tune_vehicle_command(mode, min)
                    #? Comment if it fails
                    self.settings["neutral_duty_servo"] = min
                    save_settings(self.settings, self.SETTINGS_FILE)
                    #? --- END ---

                    self.logToSystem(f"[SERVO] New servo midpoint is set to {min} µs", "DEBUG")

                case "test_servo":
                    self.network.tune_vehicle_command(mode, min, max, mid)
                    # SEND TEST COMMAND ---> Send via WAIT and Send command, ACK should re enable the button

                case "save_servo":
                    #? Comment if it fails
                    self.network.tune_vehicle_command(mode, min, max, mid)
                    self.settings["neutral_duty_servo"] = mid
                    self.settings["max_duty_servo"] = max
                    self.settings["min_duty_servo"] = min
                    save_settings(self.settings, self.SETTINGS_FILE)
                    #? --- END ---

                    self.logToSystem(f"[SERVO] New servo is set to {min}µs, {mid}µs, {max}µs", "DEBUG") 

                case "test_esc":
                    self.network.tune_vehicle_command(mode, 0,0,0, min, mid, max, brake)

                case "save_esc":
                    #? Comment if it fails
                    self.network.tune_vehicle_command(mode, 0,0,0, min, mid, max, brake)
                    self.settings["min_duty_esc"] = min
                    self.settings["max_duty_esc"] = max
                    self.settings["neutral_duty_esc"] = mid
                    self.settings["brake_esc"] = brake
                    save_settings(self.settings, self.SETTINGS_FILE)
                    #? --- END ---

                    self.logToSystem(f"[ESC] New esc is set to {min}µs, {mid}µs, {max}µs, {brake}µs", "DEBUG")

        elif mode == "update_port":
            #? Comment if it fails
            self.settings["broadcast_port"] = port
            save_settings(self.settings, self.SETTINGS_FILE)
            #? --- END ---
                    
            self.logToSystem(f"[NETWORK] Updated broadcast port on client to {port}", "DEBUG")
        #? Comment if it fails
        self.settings = load_settings(self.SETTINGS_FILE)
        #? --- END ---
    
    # === General Settings Update ===
    def updateGeneralSettings(self, mode:str, value):
        """
        Updates a general settings key in memory and saves to file.

        Args:
            mode (str): The settings key to update.
            value (Any): The new value to assign.
        """
        self.settings[mode] = value
        save_settings(self.settings, self.SETTINGS_FILE)

    # === Enable Drive Assist Mode ===
    def enableDriveAssist(self):
        """
        Placeholder method to enable drive assist.

        (Not yet implemented.)
        """
        pass
    
    # === Handle Lost Heartbeat ===
    def checkHeartBeat(self, online:bool):
        """
        Handles loss of heartbeat signal from the vehicle.

        Cleans up threads, resets UI elements, and displays a disconnection popup.

        Args:
            online (bool): False if the heartbeat is lost.
        """
        if not online:
            #! RESET SYSTEMS, CALL ERROR, POPUP
            # Vehicle Status
            self.VEHICLE_CONNECTION = False
            self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = False
            self.logToSystem("Vehicle disconnected", "ERROR")
            self.ui.vehicleTypeLabel.setText("Unknown")
            QMetaObject.invokeMethod(self.heartbeat_worker, "stop", Qt.QueuedConnection)
            
            # Video stream
            if self.THREAD_RUNNING == True:
                self.thread.stop()
                self.ui.videoStreamLabel.setText("No Conncection")
                self.ui.videoStreamWidget.setStyleSheet("QWidget{background-color: #f1f3f3;}")
            
            # Popup
            showError(self.ui.centralwidget, "Vehicle Error", "Vehicle disconnected or connection timeout", "ERROR")
        #TODO: Temp fix for heartbeat log signal?
        else:
            self.heartbeat_worker.heartbeat_log_signal.connect(self.logToSystem)
    
    # === Emergency Disconnect Logic ===
    def emergencyDisconnect(self):
        """
        Manually triggers a disconnect routine for the vehicle.

        Highlights the emergency button and sends shutdown commands.
        """
        if self.VEHICLE_CONNECTION == True:
            self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
            #TODO: RESET ALL SYSTEMS, SEND A DISCONNECT/Shutdown Command to Host

            # Vehicle Status
            self.VEHICLE_CONNECTION = False
            self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = False
            self.logToSystem("Vehicle forcefully disconnected", "ERROR")
            self.ui.vehicleTypeLabel.setText("Unknown")
            QMetaObject.invokeMethod(self.heartbeat_worker, "stop", Qt.QueuedConnection)

            # Video stream
            if self.THREAD_RUNNING == True:
                self.thread.stop()
                self.ui.videoStreamLabel.setText("No Conncection")
                self.ui.videoStreamWidget.setStyleSheet("QWidget{background-color: #f1f3f3;}")

            # Popup 
            showError(self.ui.centralwidget, "Vehicle Error", "Vehicle forcefully disconnected", "ERROR")

            #self.send_command("DISCONNECT")
            #VEHICLE_CONNECTION = False
    
    # === Frame Display and Emergency Stop Check ===
    def update_frame(self, q_img):
        """
        Receives a new frame and updates the video label with it.

        Also triggers emergency stop logic if Drive Assist is enabled.

        Args:
            q_img (QImage): Frame to display.
        """
        #pixmap = QPixmap.fromImage(q_img)
        self.ui.videoStreamLabel.setPixmap(QPixmap.fromImage(q_img))
        
        if self.alert_triggered and not self.alert_cooldown:
            self.network.send_drive_assist_command("EMERGENCY_STOP")
            self.ui.driveAssistWidget.show_warning("OBJECT DETECTED")
            self.alert_cooldown = True
            self.alert_cooldown_timer.start(3000) # 3 seconds
            self.logToSystem("Object detected! Applying command: EMERGENCY_STOP", "WARN")
    
    # === Reset Emergency Stop Timer ===
    def reset_alert_cooldown(self):
        """
        Resets the alert cooldown after an emergency stop has been triggered.

        Clears the Drive Assist warning and logs the event.
        """
        self.alert_cooldown = False
        self.ui.driveAssistWidget.clear_warning()
        self.logToSystem("Object Alert has been reset on client", "WARN")

    # === On Window Close Event ===
    def closeEvent(self, event):    #! FIXME: Fix for Ver 1.3.0
        """
        Handles graceful shutdown when the window is closed.

        Stops background threads, heartbeat, and any remaining processes.

        Args:
            event (QCloseEvent): The close event passed from Qt.
        """
        if self.VEHICLE_CONNECTION:
            #self.send_command("DISCONNECT")
            QMetaObject.invokeMethod(self.heartbeat_worker, "stop", Qt.QueuedConnection)
        self.VEHICLE_CONNECTION = False
        #self.client_socket.close()
        if self.THREAD_RUNNING == True:
            self.thread.stop()

        event.accept()
        #self.client_socket.close()
        
# === Main Execution ===
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    def launch_main():
        window = MainWindow()
        window.setWindowTitle(f"Drive Core Client Ver {window.client_ver}")
        window.show()
        window.onStartup()

    loading = LoadingScreen(on_finished_callback=launch_main)
    loading.show()

    sys.exit(app.exec())
