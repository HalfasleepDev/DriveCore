from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QTimer,
    QSize, QTime, QUrl, QThread, Signal, QEvent, Qt, QThreadPool,QRunnable, Slot)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QKeyEvent)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

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

#PORT = 4444 #move to settings

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_SCALE_FACTOR"] = "0.95"
""" 
This Codebase sucks and I hate sockets
Time wasted here since 26-04-2025: 30Hrs
"""
# TODO: Style error popups
class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        """Initialise the runner function with passed args, kwargs."""
        self.fn(*self.args, **self.kwargs)

class VideoThread(QThread):
    frame_received = Signal(QImage)

    def __init__(self, server_ip, video_port):
        super().__init__()
        self.server_ip = server_ip
        self.video_port = video_port
        self.running = True
        self.processor = None  # Optional processor

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(('', self.video_port))

        self.total_chunks = 0
        self.current_chunks = 0
        self.frame_chunks = []
        self.last_frame_timestamp = 0

        self.last_frame_time = time.time()
        self.frame_counter = 0
        self.fps = 0
        self.last_video_latency_ms = 0
        self.last_frame_timestamp = 0

    def set_processor(self, processor):
        self.processor = processor

    def run(self):
        BUFFER_SIZE = 65536

        while self.running:
            try:
                data, _ = self.sock.recvfrom(BUFFER_SIZE)

                # Header packet (first packet = JSON info)
                try:
                    header = json.loads(data.decode())
                    self.total_chunks = header["chunks"]
                    self.last_frame_timestamp = header["timestamp"]
                    self.frame_chunks = []
                    self.current_chunks = 0
                    continue
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                # Accumulate frame chunks
                self.frame_chunks.append(data)
                self.current_chunks += 1

                # === Drop frame if excessive chunks ===
                if self.current_chunks > self.total_chunks:
                    self.frame_chunks.clear()
                    self.current_chunks = 0
                    continue

                # Frame complete
                if self.current_chunks == self.total_chunks:
                    frame_data = b''.join(self.frame_chunks)

                    # Decode JPEG
                    now = int(time.time() * 1000)
                    self.last_video_latency_ms = now - self.last_frame_timestamp

                    ###! self.display_frame(frame_data)
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # === FPS calculation ===
                        self.frame_counter += 1
                        now = time.time()
                        elapsed = now - self.last_frame_time
                        if elapsed >= 1.0:
                            self.fps = self.frame_counter / elapsed
                            self.frame_counter = 0
                            self.last_frame_time = now

                        # === Overlay text ===
                        overlay = f"FPS: {self.fps:.1f} | Latency: {self.last_video_latency_ms} ms"
                        cv2.putText(frame, overlay, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 255, 0), 1, cv2.LINE_AA) 
                           
                        #AI or floor detection
                        if self.processor:
                            # IF DriveAssist Enabled
                            frame = self.processor.detect_floor_region(frame)

                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        h, w, ch = frame.shape
                        bytes_per_line = ch * w
                        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                        self.frame_received.emit(q_img)
                    ###! end

                    # Reset for next frame
                    self.frame_chunks = []
                    self.current_chunks = 0

            except BlockingIOError:
                pass  # No data received; socket is non-blocking

    def stop(self):
        self.running = False
        self.wait()
        self.sock.close()

'''
class VideoThread(QThread):
    frame_received = Signal(QImage)  # Signal to send new frame to UI

    def __init__(self, stream_url):
        super().__init__() 
        self.stream_url = stream_url
        self.running = True  # Control flag for stopping thread

    def set_processor(self, processor):
        self.processor = processor

    def run(self):
        cap = cv2.VideoCapture(self.stream_url)

        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = self.processor.detect_floor_region(frame)   #OpenCV processes
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_received.emit(q_img)  # Emit the frame
            #else:
                #print("Failed to retrieve frame")
        
        cap.release()
    
    def try_video_stream(self, streamURL):
        cap = cv2.VideoCapture(streamURL)
        
        ret, frame = cap.read()
        if ret:
            cap.release() 
        else:
            cap.release()
            raise ConnectionRefusedError

    def stop(self):
        self.running = False
        self.wait()  # Ensure the thread is properly closed
'''
class MainWindow(QMainWindow):
    # Load Settings
    SETTINGS_FILE = "D-14/Client-Side/client-app/settings.json"
    #client_ver = "1.3"
    #supported_ver = ["1.3"]

    # Network Variables
    #server_ip = None
    #video_port = None
    #control_port = None
    #handshake_done = threading.Event()


    # Vehicle Status
    VEHICLE_CONNECTION = False
    OPENED_DRIVE_PAGE = False

    # Vehicle Info
    #control_scheme = str
    #vehicle_model = str

    # Thread Status
    THREAD_RUNNING = False

    # OpenCV Settings Variables
    OBJECT_VIS_ENABLED = False
    FLOOR_VIS_ENABLED = False
    KALMAN_CENTER_VIS_ENABLED = False
    AMBIENT_VIS_ENABLED = False
    FLOOR_SAMPLE_VIS_ENABLED = False
    PATH_VIS_ENABLED = False
    COLLISION_ASSIST_ENABLED = False
    alert_triggered = False
    alert_cooldown = False

    # Drive Assist
    IS_DRIVE_ASSIST_ENABLED = False

    logSignal = Signal(str, str)
    displayVehicleMovementSignal = Signal(str, int, int)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.threadpool = QThreadPool.globalInstance()

        ''' ====== App Details ======'''
        # Current Client App Version
        self.client_ver = "1.3"
        # Supported Host Versions
        self.supported_ver = ["1.3"]

        # Load Settings From Json
        self.settings = load_settings(self.SETTINGS_FILE)

        ''' ====== Host Details ======'''
        self.vehicle_model = str
        self.control_scheme = str

        self.curveType = str

        ''' ====== Animated Button Setup ======'''
        animButtons = [self.ui.homeBtn, self.ui.settingsBtn, self.ui.driveBtn, self.ui.logBtn, self.ui.openCVSettingsBtn,
            self.ui.vehicleTuningBtn, self.ui.ObjectVisBtn, self.ui.FloorVisBtn, self.ui.KalmanCenterVisBtn, 
            self.ui.AmbientVisBtn, self.ui.FloorSampleVisBtn, self.ui.PathVisBtn, self.ui.CollisionAssistBtn,
            self.ui.emergencyDisconnectBtn
            ]
        
        for btn in animButtons:
            install_hover_animation(btn)

        ''' ====== Network Setup ======'''
        self.handshake_done = threading.Event()

        self.network = NetworkManager(self)

        # TODO: if network doesnt update use these 
        '''
        self.server_ip = None
        self.video_port = None
        '''
        
        #! Depreciated for Ver1.3
        #self.ui.inputIp.editingFinished.connect(self.setIp)
        #self.ui.inputIp.editingFinished.connect(self.add_ip)
        #self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)       # Use UDP communication

        #self.recent_ips = self.load_recent_ips()
        #self.ui.recentIpCombo.addItems(self.recent_ips)

        #self.load_recent_ips()
        #self.ui.ipComboBtn.clicked.connect(self.setIpCombo)

        ''' ====== Home Page ======'''
        # Load Credentials On Startup
        self.load_credentials()

        self.ui.carConnectLoginWidget.connect_btn.clicked.connect(self.attempt_connection)
        self.logSignal.connect(self.logToSystem)

        self.ui.projectInfoWidgetCustom.logErrorSignal.connect(self.logToSystem)
        #self.discoverHostSignal.connect(self.network.discover_host)
        #self.performHandshakeSignal.connect(self.network.perform_handshake)
        
        ''' ====== Logic For Left Menu Buttons ====== '''
        self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
        self.ui.homeBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.homeBtn, self.ui.homePage))
        self.ui.settingsBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.settingsBtn, self.ui.settingsPage))
        self.ui.settingsBtn.clicked.connect(lambda: self.iniSettingsPage())
        self.ui.driveBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.driveBtn, self.ui.drivePage))
        self.ui.driveBtn.clicked.connect(lambda: self.iniDrivePage())
        self.ui.logBtn.clicked.connect(lambda: self.handleLeftMenuNav(self.ui.logBtn, self.ui.systemLogPage))

        ''' ====== Settings Page ====== '''
        # ------ Top Nav Buttons ------ 
        self.ui.openCVSettingsBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
        self.ui.openCVSettingsBtn.clicked.connect(lambda: self.handleSettingsNav(self.ui.openCVSettingsBtn, self.ui.OpenCVSettingsPage, 2))
        self.ui.vehicleTuningBtn.clicked.connect(lambda: self.handleSettingsNav(self.ui.vehicleTuningBtn, self.ui.VehicleTuningSettingsPage, 3))
        
        # ------ OpenCV ------
        # OpenCV Setting Buttons
        self.ui.ObjectVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(1))
        self.ui.FloorVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(2))
        self.ui.KalmanCenterVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(3))
        self.ui.AmbientVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(4))
        self.ui.FloorSampleVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(5))
        self.ui.PathVisBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(6))
        self.ui.CollisionAssistBtn.clicked.connect(lambda: self.toggleSettingOpenCvBtns(7))

        # HSV Sliders
        # - Set range for sensitivity tuning
        self.ui.HRowSlider.setRange(0, 50)
        self.ui.SRowSlider.setRange(0, 100)
        self.ui.VRowSlider.setRange(0, 100)

        self.ui.HRowSlider.valueChanged.connect(lambda val: self.ui.HRowValueLabel.setText(str(val)))
        self.ui.SRowSlider.valueChanged.connect(lambda val: self.ui.SRowValueLabel.setText(str(val)))
        self.ui.VRowSlider.valueChanged.connect(lambda val: self.ui.VRowValueLabel.setText(str(val)))

        # - Set default values
        self.ui.HRowSlider.setValue(35)
        self.ui.SRowSlider.setValue(40)
        self.ui.VRowSlider.setValue(50)

        # ------ Vehicle Tuning ------
        self.ui.VehicleTuningSettingsPage.set_curve_selection(self.settings["acceleration_curve"])
        self.ui.VehicleTuningSettingsPage.previewServoSignal.connect(self.tuneVehicle)

        self.ui.VehicleTuningSettingsPage.servo_mid_tuner.saveServoMidpointSignal.connect(self.tuneVehicle)

        self.ui.VehicleTuningSettingsPage.accelCurveSignal.connect(self.setSaveCurveType) #* DONE

        self.ui.VehicleTuningSettingsPage.servoTuneSignal.connect(self.tuneVehicle)
        self.ui.VehicleTuningSettingsPage.escTuneSignal.connect(self.tuneVehicle)

        self.ui.VehicleTuningSettingsPage.set_default_tune_page(self.settings["min_duty_esc"], self.settings["neutral_duty_esc"], 
                                                                self.settings["max_duty_esc"], self.settings["brake_esc"], 
                                                                self.settings["min_duty_servo"], self.settings["neutral_duty_servo"], 
                                                                self.settings["max_duty_servo"], self.settings["broadcast_port"])

        self.ui.VehicleTuningSettingsPage.updateBroadcastPortSignal.connect(self.tuneVehicle)

        self.ui.VehicleTuningSettingsPage.logToSystemSignal.connect(self.logToSystem) #* DONE

        # ------ Emergency Dissconnect ------
        self.ui.emergencyDisconnectBtn.clicked.connect(lambda: self.emergencyDisconnect())

        ''' ====== OpenCV Variables & Functions ====== '''
        self.timer = QTimer()
        
        self.timer.start(30)

        self.frame_counter = 0
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=100, detectShadows=False)
        self.last_floor_contour = None

        self.alert_line_y = 680 # Set where an object enters it stops the vehicle, could move to settings?

        ''' ====== Drive Page ====== '''
        # ------ tooltip ------
        self.tooltip = AnimatedToolTip("", self)
        self.ui.alertAssistWidget.installEventFilter(self)
        self.ui.alertAssistWidget.setToolTip("Turn On/Off collision braking")
        self.ui.driveAssistWidget.toggle_button.clicked.connect(lambda: self.toggleSettingOpenCvBtns(8))

        # ------ Drive Assist Widget ------
        self.ui.driveAssistWidget.toggle_button.clicked.connect(lambda: self.toggleSettingOpenCvBtns(8))
        self.alert_cooldown_timer = QTimer()
        self.alert_cooldown_timer.setSingleShot(True)
        self.alert_cooldown_timer.timeout.connect(self.reset_alert_cooldown)

    def onStartup(self):
        thread_count = self.threadpool.maxThreadCount()
        self.logToSystem(f"Multithreading with maximum {thread_count} threads", "DEBUG")
        
    def eventFilter(self, watched, event):
        if event.type() == QEvent.ToolTip:
            if isinstance(watched, QWidget):
                tooltip_text = watched.toolTip()
                self.tooltip.setText(tooltip_text)

                # Show beside the widget
                pos = watched.mapToGlobal(watched.rect().topRight())
                self.tooltip.show_tooltip(pos)
                return True  # prevent default tooltip from showing

        elif event.type() == QEvent.Leave:
            self.tooltip.hide_tooltip()

        return super().eventFilter(watched, event)
    
    def handleSettingsNav(self, active_btn, target_page, infoIndex: int):
        for btn in [self.ui.openCVSettingsBtn, self.ui.vehicleTuningBtn]:
            btn.setStyleSheet("QPushButton{background-color: #1e1e21;}")

            # Highlight active button
            active_btn.setStyleSheet("QPushButton{background-color: #7a63ff;}")

            # Switch page
            self.ui.settingsStackedWidget.setCurrentWidget(target_page)

            # Switch to info page (1) is no page
            self.ui.settingsInfoStackedWidget.setCurrentIndex(infoIndex)
            if infoIndex == 3:
                self.ui.verticalLayout_15.removeItem(self.ui.verticalSpacer_8)
                self.ui.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                self.ui.verticalLayout_15.insertItem(3, self.ui.verticalSpacer_8)
            else:
                self.ui.verticalLayout_15.removeItem(self.ui.verticalSpacer_8)
                self.ui.verticalSpacer_8 = QSpacerItem(20, 431, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                self.ui.verticalLayout_15.insertItem(3, self.ui.verticalSpacer_8)
        
    def handleLeftMenuNav(self, active_btn, target_page):
        for btn in [self.ui.homeBtn, self.ui.settingsBtn, self.ui.driveBtn, self.ui.logBtn]:
            btn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")

            # Highlight active button
            active_btn.setStyleSheet("QPushButton{background-color: #7a63ff;}")

            # Switch page
            self.ui.stackedWidget.setCurrentWidget(target_page)

    def stop_thread_safely(self):
        if self.THREAD_RUNNING:
            try:
                self.thread.stop()
            except Exception as e:
                showError(self, "Program Error!", f"Error stopping thread: {e}")
                #print(f"Error stopping thread: {e}")
    
    def toggleSettingOpenCvBtns(self, select):
        self.IS_DRIVE_ASSIST_ENABLED = True
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
            case 7:
                self.COLLISION_ASSIST_ENABLED = toggleDebugCV(self.ui.CollisionAssistBtn, self.COLLISION_ASSIST_ENABLED, "")
            case 8:
                self.COLLISION_ASSIST_ENABLED = toggleDebugCV(self.ui.CollisionAssistBtn, self.COLLISION_ASSIST_ENABLED, "")
                self.COLLISION_ASSIST_ENABLED = self.ui.driveAssistWidget.toggle_assist()
                self.IS_DRIVE_ASSIST_ENABLED = self.ui.driveAssistWidget.toggle_assist()

    def logToSystem(self, message: str, type: str):
        self.ui.systemLogPage.log(message, type)
        match type:
            case "BROADCAST":
                self.ui.networkConnectionLogWidget.add_log(f"[{type}] {message}")
            case "HANDSHAKE":
                self.ui.networkConnectionLogWidget.add_log(f"[{type}] {message}")
            case "INFO":
                self.ui.vehicleSystemAlertLogWidget.add_log(f"[{type}] {message}")
            case "WARN":
                self.ui.vehicleSystemAlertLogWidget.add_log(f"[{type}] {message}")
        QCoreApplication.processEvents()

    # Set and save the selected curve from the settings page
    def setSaveCurveType(self, curve: str):
        self.ui.drivePage.setCurveType = curve
        self.settings["acceleration_curve"] = curve
        save_settings(self.settings, self.SETTINGS_FILE)

    # Automatically load the previously used credentials from settings.json
    def load_credentials(self):
        self.ui.carConnectLoginWidget.username_input.setText(self.settings["username"])
        self.ui.carConnectLoginWidget.password_input.setText(self.settings["password"])

    # Attempt a connection to the vehicle
    def attempt_connection(self):
        # Get username and password from the input fields
        username = self.ui.carConnectLoginWidget.username_input.text().strip()
        password = self.ui.carConnectLoginWidget.password_input.text().strip()

        # Check that username and/or password is not empty
        if not username or not password:
            self.ui.carConnectLoginWidget.show_error("Please enter both username and password.")
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            self.threadpool.start(Worker(self.network.discover_host))
            #self.threadpool.waitForDone()
            self.network.discovery_done_signal.connect(lambda: self.threadpool.start(Worker(lambda: self.network.perform_handshake(username, password))))

            self.threadpool.waitForDone()
            QApplication.restoreOverrideCursor()

            if self.VEHICLE_CONNECTION:
                
                self.settings["username"] = username
                self.settings["password"] = password
                save_settings(self.settings, self.SETTINGS_FILE)
        
    #! Depreciated for Ver1.3

    '''
    def add_ip(self):
        """ Adds the entered IP to the combo box and saves it. """
        ip = self.ui.inputIp.text().strip()
        if self.is_ip_address(ip):
            if ip and ip not in self.recent_ips:
                self.recent_ips.insert(0, ip)  # Add to the top of the list
                self.ui.recentIpCombo.insertItem(0, ip)  # Add to QComboBox
                self.save_recent_ips()

        # Clear input field
        self.ui.inputIp.clear()

    #! Depreciated for Ver1.3
    def load_recent_ips(self):
        """ Loads recent IP addresses from a file. """
        filename = "D-14/Client-Side/client-app/recent_ips.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return [line.strip() for line in file.readlines()]
        return []
    
    #! Depreciated for Ver1.3
    def save_recent_ips(self):
        """ Saves recent IP addresses to a file. """
        with open("D-14/Client-Side/client-app/recent_ips.txt", "w") as file:
            for ip in self.recent_ips[:10]:  # Keep only the last 10 entries
                file.write(ip + "\n")
        
    def emergencyDisconnect(self):
        if self.VEHICLE_CONNECTION == True:
            self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
            self.send_command("DISCONNECT")
            VEHICLE_CONNECTION = False

    #! Depreciated for Ver1.3
    def is_ip_address(self, s):
        try:
            ipaddress.ip_address(s)  # Try converting the string to an IP address
            return True
        except ValueError:
            showError(self, "CONNECTION ERROR", "Not a valid IP address")
            return False  # Not a valid IP address
    
    #! Depreciated for Ver1.3
    def setIp(self):
        
        if self.is_ip_address(self.ui.inputIp.text()):
            self.IP_ADDR = self.ui.inputIp.text()
            self.STREAM_URL = "http://" + self.IP_ADDR + ":5000/video-feed"
            #self.STREAM_URL = self.IP_ADDR + ":5000/video_feed"
            print(self.STREAM_URL)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                VideoThread.try_video_stream(self, self.STREAM_URL)
                self.client_socket.connect((self.IP_ADDR, PORT))
                print("Connected to Raspberry Pi")
                self.VEHICLE_CONNECTION = True
                self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")
                self.ui.vehicleTypeLabel.setText("RPI_D14")
                self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #32CD32;}")
            except ConnectionRefusedError:
                QApplication.restoreOverrideCursor()
                showError(self, "CONNECTION ERROR", "Failed to connect to Raspberry Pi")
                self.VEHICLE_CONNECTION = False
                self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #FFA500;}")
            QApplication.restoreOverrideCursor()

        else:
            self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #FF0000;}")
            
    #! Depreciated for Ver1.3
    def setIpCombo(self):
        if self.is_ip_address(self.ui.recentIpCombo.currentText()):
            self.IP_ADDR = self.ui.recentIpCombo.currentText()
            self.STREAM_URL = "http://" + self.IP_ADDR + ":5000/video-feed"
            #self.STREAM_URL = self.IP_ADDR + ":5000/video_feed"
            print(self.STREAM_URL)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                VideoThread.try_video_stream(self, self.STREAM_URL)
                self.client_socket.connect((self.IP_ADDR, PORT))
                print("Connected to Raspberry Pi")
                self.VEHICLE_CONNECTION = True
                self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")
                self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #32CD32;}")
                self.ui.vehicleTypeLabel.setText("RPI_D14")
            except ConnectionRefusedError:
                QApplication.restoreOverrideCursor()
                showError(self, "CONNECTION ERROR", "Failed to connect to Raspberry Pi")
                self.VEHICLE_CONNECTION = False
                self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #FFA500;}")
            QApplication.restoreOverrideCursor()
                
        else:
            self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #FF0000;}")'''
        

    def iniDrivePage(self):
        if self.VEHICLE_CONNECTION and self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY:
            print(self.network.server_ip)
            print(self.network.video_port)
            self.thread = VideoThread(self.network.server_ip, self.network.video_port)
            self.processor = FrameProcessor(self, self.thread)
            self.processor.initKalmanFilter()
            self.thread.set_processor(self.processor)
            self.thread.frame_received.connect(self.update_frame)

            if not self.OPENED_DRIVE_PAGE:
                self.thread.start()
                self.THREAD_RUNNING = True
                self.OPENED_DRIVE_PAGE = True
            
            self.updateVehicleMovement("SET")
            self.ui.videoStreamWidget.setStyleSheet("QWidget{background-color:  #0c0c0d;}")
            self.ui.drivePage.commandSignal.connect(self.changeKeyInfo)
            self.ui.drivePage.commandSignal.connect(self.network.send_keyboard_command)
            
        else:
            self.ui.videoStreamLabel.setStyleSheet("QLabel{color: #1e1e21;}")

    def changeKeyInfo(self, command, intensity):
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

    def updateVehicleMovement(self, mode: str, esc_pw=None, servo_pw=None):

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
    
    def iniSettingsPage(self):
        if self.VEHICLE_CONNECTION:
            self.ui.VehicleTuningSettingsPage.IS_VEHICLE_READY = True

    def tuneVehicle(self, mode: str, min=0, mid=0, max=0, brake=0, port=0):
        if self.VEHICLE_CONNECTION:
            match mode:
                case "servo_mid_cal":
                    self.network.tune_vehicle_command(mode, min)
                    self.logToSystem(f"[SERVO] Servo tested at {min} µs", "DEBUG")
                    #TEST PRINT
                    #print(min)
                
                case "save_mid_servo":
                    self.network.tune_vehicle_command(mode, min)
                    # TODO: Uncomment if it works
                    #self.settings["neutral_duty_servo"] = min
                    #save_settings(self.settings, self.SETTINGS_FILE)

                    self.logToSystem(f"[SERVO] New servo midpoint is set to {min} µs", "DEBUG")
                        
                    #TEST PRINT
                    #print(f"TEST save servo mid {min}")

                case "test_servo":
                    self.network.tune_vehicle_command(mode, min, max, mid)
                    # SEND TEST COMMAND ---> Send via WAIT and Send command, ACK should re enable the button
                    
                    # TEST PRINT
                    #print(f"SERVO:\nMin: {min} µs\nMid: {mid} µs\nMax: {max} µs")

                case "save_servo":
                    # TODO: Uncomment if it works
                    #self.network.tune_vehicle_command(mode, min, max, mid)
                    #self.settings["neutral_duty_servo"] = mid
                    #self.settings["max_duty_servo"] = max
                    #self.settings["min_duty_servo"] = min
                    #save_settings(self.settings, self.SETTINGS_FILE)

                    self.logToSystem(f"[SERVO] New servo is set to {min}µs, {mid}µs, {max}µs", "DEBUG") 


                
                case "test_esc":
                    self.network.tune_vehicle_command(mode, 0,0,0, min, mid, max, brake)
                        
                    # TEST PRINT
                    #print(f"ESC:\nMin: {min} µs\nMid: {mid} µs\nMax: {max} µs\nBRAKE {brake} µs")

                case "save_esc":
                    # TODO: Uncomment if it works
                    #self.network.tune_vehicle_command(mode, 0,0,0, min, mid, max, brake)
                    #self.settings["min_duty_esc"] = min
                    #self.settings["max_duty_esc"] = max
                    #self.settings["neutral_duty_esc"] = mid
                    #self.settings["brake_esc"] = brake
                    #save_settings(self.settings, self.SETTINGS_FILE)

                    self.logToSystem(f"[ESC] New esc is set to {min}µs, {mid}µs, {max}µs, {brake}µs", "DEBUG")

        elif mode == "update_port":
            # TODO: Uncomment if it works
            #self.settings["broadcast_port"] = port
            #save_settings(self.settings, self.SETTINGS_FILE)
                    
            self.logToSystem(f"[NETWORK] Updated broadcast port on client to {port}", "DEBUG")

        #self.settings = load_settings(self.SETTINGS_FILE)
    
    def updateGeneralSettings(self, mode:str, value):
        self.settings[mode] = value
        save_settings(self.settings, self.SETTINGS_FILE)

    def enableDriveAssist(self):
        pass


    #! Depreciated for Ver1.3
    def send_command(self, command):
        """Send command to Raspberry Pi"""
        # Check For MODE
        # IF keyboard
            # calculate intensity
            # send command
        # IF driveassist
            # send driveAssist Command
        pass
    
    #! FIX DRIVE ASSIST Functions
    def update_frame(self, q_img):
        """Update QLabel with new frame."""
        #pixmap = QPixmap.fromImage(q_img)
        self.ui.videoStreamLabel.setPixmap(QPixmap.fromImage(q_img))
        
        if self.alert_triggered and not self.alert_cooldown:
            self.network.send_drive_assist_command("EMERGENCY_STOP")
            self.ui.driveAssistWidget.show_warning("OBJECT DETECTED")
            self.alert_cooldown = True
            self.alert_cooldown_timer.start(3000) # 3 seconds
            self.logToSystem("Object detected! Applying command: EMERGENCY_STOP", "WARN")
        
    def reset_alert_cooldown(self):
        self.alert_cooldown = False
        self.ui.driveAssistWidget.clear_warning()
        self.logToSystem("Object Alert has been reset on client", "WARN")

    #! Depreciated for Ver1.3
    def closeEvent(self, event):
        """Release resources when closing the window."""
        if self.VEHICLE_CONNECTION:
            self.send_command("DISCONNECT")
        self.VEHICLE_CONNECTION = False
        self.client_socket.close()
        if self.THREAD_RUNNING == True:
            self.thread.stop()
        event.accept()
        #self.client_socket.close()
        

if __name__ == '__main__':
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    #!ENABLE FOR RELEASE
    def launch_main():
        window = MainWindow()
        window.setWindowTitle(f"Drive Core Client Ver {window.client_ver}")
        window.show()
        window.onStartup()

    loading = LoadingScreen(on_finished_callback=launch_main)
    loading.show()

    #!ENABLE FOR TESTING ONLY
    #window = MainWindow()
    #window.setWindowTitle("Drive Core Client Ver 1.2")
    #window.show()

    sys.exit(app.exec())
