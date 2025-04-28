from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget, QPushButton, QMessageBox
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, Signal, QTimer
import time
import os
import json
import math

#from MainWindow import Ui_MainWindow

DEFAULT_SETTINGS = {
    "min_duty_servo": 900,
    "max_duty_servo": 2100,
    "neutral_duty_servo": 1500,
    "min_duty_esc": 1310,
    "max_duty_esc": 1750,
    "neutral_duty_esc": 1500,
    "brake_esc": 1470,
    "ramp_up": 0.05,
    "ramp_down": 0.05,
    "username": "",
    "password": "",
    "acceleration_curve": "linear",
    "broadcast_port": 9999
}

'''Keypress Page Class'''
# TODO: REFACTOR!!!!
class PageWithKeyEvents(QWidget):
    """A QWidget that only detects key presses when active in QStackedWidget"""
    commandSignal = Signal(str, float, float)

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)

        # For send interval tracking
        self.last_command_time = 0
        self.COMMAND_INTERVAL = 0.05        # seconds
        self.last_command_sent = None
        self.last_break_command_time = 0
        self.COMMAND_BRAKE_INTERVAL = 0.5   # seconds

        # === Throttle / Steering Tracking ===
        self.held_keys = set()
        self.command = None
        self.curveType = None
        self.servo_intensity = 0.0
        self.intensity = 0.0
        self.RAMP_UP = 0.05                 # create new servo ramp?
        self.RAMP_DOWN = 0.05               # create new servo ramp down?
        self.MAX_INTENSITY = 1.0

        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.send_ramping_command)
        self.control_timer.start(150) # check send speed?
    
    def setCurveType(self, val):
        self.curveType = val

    def send_ramping_command(self):
        # Calculate servo intensity
        if self.command in ['LEFTUP', 'RIGHTUP', 'LEFTDOWN', 'RIGHTDOWN', 'LEFT', 'RIGHT']:
            self.servo_intensity = min(self.MAX_INTENSITY, self.servo_intensity + self.RAMP_UP)

        # Calculate esc intensity
        if self.command in ['LEFTUP', 'RIGHTUP', 'LEFTDOWN', 'RIGHTDOWN', 'UP', 'DOWN', 'BRAKE']:
            self.intensity = min(self.MAX_INTENSITY, self.intensity + self.RAMP_UP)

        # Calculate the curves and emit the values of the COMMAND and intensity
        if self.command:
            curved_intensity_esc = curve(self.intensity, self.curveType)
            curved_intensity_servo = curve(self.servo_intensity, self.curveType)

            self.commandSignal.emit(self.command, round(curved_intensity_esc, 2), round(curved_intensity_servo, 2))
            #print(self.command)
        else:
            self.intensity = max(0.0, self.intensity - self.RAMP_DOWN)
            self.servo_intensity = max(0.0, self.servo_intensity - self.RAMP_DOWN)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        key = event.key()
        self.held_keys.add(key)

        self.command = self.get_command_from_keys()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        key = event.key()
        self.held_keys.discard(key)

        # If key is W or S
        if key == Qt.Key_W or key == Qt.Key_S:
            # Emit Neutral
            print("W or S release")
            self.held_keys.discard(key)
            
            self.commandSignal.emit("NEUTRAL", 0, 0)
            #self.intensity = self.intensity - (self.RAMP_DOWN * self.intensity)
        
        # Else if key is A or D
        elif key == Qt.Key_A or key == Qt.Key_D:
            # Emit Center
            print("A or D release")
            self.held_keys.discard(key)
            #self.servo_intensity = 0.0
            #self.commandSignal.emit("CENTER", 0, 0)
            #self.servo_intensity = self.servo_intensity - (self.RAMP_DOWN * self.servo_intensity)

        self.command = self.get_command_from_keys()

        # If no active keys, drop intensity
        if not self.command:
            self.servo_intensity = max(0.0, self.servo_intensity - (0.1 * self.servo_intensity))
            
            self.intensity = max(0.0, self.intensity - (0.1 * self.intensity))

            self.commandSignal.emit("NEUTRAL", 0, 0)
            self.commandSignal.emit("CENTER", 0, 0)
        '''self.pressed_keys.discard(event.key())

        if event.isAutoRepeat():
            return
        if event.key() in [Qt.Key_W, Qt.Key_S]:
            self.send_command("NEUTRAL")
            print("TEST NEUTRAL")
        elif event.key() in [Qt.Key_A, Qt.Key_D]:
            self.send_command("CENTER")
            print("TEST CENTER")'''
    
    '''def send_brake_burst(self, count, interval):
        """Send 'BRAKE' command `count` times every `interval` milliseconds"""
        now = time.monotonic()
        if (now - self.last_break_command_time) >= self.COMMAND_BRAKE_INTERVAL:
            self.last_command_time = now
            for i in range(count):
                QTimer.singleShot(i * interval, lambda: self.send_command("BRAKE"))
                print("TEST BRAKE CV")'''
    def get_command_from_keys(self):
        k = self.held_keys
        if Qt.Key_W in k and Qt.Key_A in k:
            return "LEFTUP"
        elif Qt.Key_W in k and Qt.Key_D in k:
            return "RIGHTUP"
        elif Qt.Key_S in k and Qt.Key_A in k:
            return "LEFTDOWN"
        elif Qt.Key_S in k and Qt.Key_D in k:
            return "RIGHTDOWN"
        elif Qt.Key_W in k:
            return "UP"
        elif Qt.Key_S in k:
            return "DOWN"
        elif Qt.Key_A in k:
            return "LEFT"
        elif Qt.Key_D in k:
            return "RIGHT"
        elif Qt.Key_Space in k:
            return "BRAKE"
        return None

'''Settings Page OpenCV Toggles'''

def toggleDebugCV(button, currentState, text):
    """Toggle visibility state, button text, and style."""
    newState = not currentState

    if newState:
        button.setText(text + "ON")
        button.setStyleSheet("background-color: #7a63ff;")
    else:
        button.setText(text + "OFF")
        button.setStyleSheet("background-color: #1e1e21;")

    return newState

'''Error popup'''
def showError(self, title: str, message: str):
    msg_box = QMessageBox(self)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()

def load_settings(SETTINGS_FILE):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                loaded = json.load(f)
                return {**DEFAULT_SETTINGS, **loaded}
            except json.JSONDecodeError:
                print("Invalid settings file. Loading defaults.")
    return DEFAULT_SETTINGS.copy()

def save_settings(new_settings, SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f, indent=4)

def curve(x, type="quadratic"):
    if type == "quadratic":
        return x * x
    elif type == "cubic":
        return x ** 3
    elif type == "expo":
        return 1 - math.exp(-5 * x)
    elif type == "sigmoid":
        k = 10
        return 1 / (1 + math.exp(-k * (x - 0.5)))
    return x  # linear fallback
