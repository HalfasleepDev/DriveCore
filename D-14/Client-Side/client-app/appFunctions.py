"""
appFunctions.py

Background app functions and systems.

Author: HalfasleepDev
Created: 19-02-2025
"""

# === Imports ===
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget, QPushButton, QMessageBox
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, Signal, QTimer
import time
import os
import json
import math

from appUiAnimations import MsgPopup

# === Default Settings for Application ===
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

# === Keypress Page Class for Capturing Key Events ===
class PageWithKeyEvents(QWidget):
    """
    A QWidget that emits custom driving commands based on keyboard input.
    
    This widget supports ramping acceleration and handles keypress combinations
    for directional control. Intended to be used inside a QStackedWidget.
    """
    commandSignal = Signal(str, float, float)

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)

        # === Key Press Tracking ===
        self.last_command_time = 0
        self.last_command_sent = None
        self.last_break_command_time = 0

        # === Throttle / Steering Intensity States ===
        self.held_keys = set()
        self.command = None
        self.curveType = None
        self.servo_intensity = 0.0
        self.intensity = 0.0
        self.RAMP_UP = 0.05
        self.RAMP_DOWN = 0.05
        self.MAX_INTENSITY = 1.0

        # === Ramping Timer ===
        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.send_ramping_command)
        self.control_timer.start(100) # check send speed?
    
    def setCurveType(self, val):
        """Set the acceleration curve to use."""
        self.curveType = val

    def send_ramping_command(self):
        """Emit command with curved intensity based on key hold duration."""

        # Ramp up servo intensity
        if self.command in ['LEFTUP', 'RIGHTUP', 'LEFTDOWN', 'RIGHTDOWN', 'LEFT', 'RIGHT']:
            self.servo_intensity = min(self.MAX_INTENSITY, self.servo_intensity + self.RAMP_UP)

        # Ramp up ESC intensity
        if self.command in ['LEFTUP', 'RIGHTUP', 'LEFTDOWN', 'RIGHTDOWN', 'UP', 'DOWN', 'BRAKE']:
            self.intensity = min(self.MAX_INTENSITY, self.intensity + self.RAMP_UP)

        # Calculate the curves and emit the values of the COMMAND and intensity
        if self.command:
            curved_intensity_esc = curve(self.intensity, self.curveType)
            curved_intensity_servo = curve(self.servo_intensity, self.curveType)

            # Emit current ramped command
            self.commandSignal.emit(self.command, round(curved_intensity_esc, 2), round(curved_intensity_servo, 2))
        else:
            # Ramp down if no command
            self.intensity = max(0.0, self.intensity - self.RAMP_DOWN)
            self.servo_intensity = max(0.0, self.servo_intensity - self.RAMP_DOWN)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press and store active key in held_keys."""
        if event.isAutoRepeat():
            return
        key = event.key()
        self.held_keys.add(key)

        self.command = self.get_command_from_keys()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release and determine if system should neutralize."""
        if event.isAutoRepeat():
            return
        key = event.key()
        self.held_keys.discard(key)

        # If key is W or S
        if key == Qt.Key_W or key == Qt.Key_S:
            # Emit Neutral
            #print("W or S release")
            self.held_keys.discard(key)
            
            self.commandSignal.emit("NEUTRAL", 0, 0)
            #self.intensity = self.intensity - (self.RAMP_DOWN * self.intensity)
        
        # === ESC Direction Neutralization ===
        elif key == Qt.Key_A or key == Qt.Key_D:
            # Emit Center
            #print("A or D release")
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
            self.commandSignal.emit("CENTER", 0, 0)     #! Comment out for more realistic control
     
    def get_command_from_keys(self):
        """Return command string based on current held keys."""
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

# === Toggle Debug Visuals for OpenCV ===
def toggleDebugCV(button, currentState, text):
    """
    Toggle OpenCV visual state and update button label and color.

    Args:
        button (QPushButton): Button being toggled.
        currentState (bool): Current state before toggle.
        text (str): Label prefix for ON/OFF state.
    
    Returns:
        bool: The new toggled state.
    """
    newState = not currentState

    if newState:
        button.setText(text + "ON")
        button.setStyleSheet("background-color: #7a63ff;")
    else:
        button.setText(text + "OFF")
        button.setStyleSheet("background-color: #1e1e21;")

    return newState

# === Error Message Popup ===
def showError(window, title: str, message: str, severity: str, duration =0):
    """
    Display a styled popup message window.

    Args:
        window (QWidget): Parent widget.
        title (str): Popup title.
        message (str): Message body.
        severity (str): One of INFO, WARNING, ERROR, SUCCESS.
        duration (int, optional): How long the popup stays visible. Default is 0.
    """
    msg_box = MsgPopup(title, message, severity, window)
    msg_box.show_popup(duration, window)

# === Load Application Settings ===
def load_settings(SETTINGS_FILE):
    """
    Load settings from JSON, fallback to defaults if corrupted.

    Args:
        SETTINGS_FILE (str): Path to JSON config.

    Returns:
        dict: Merged settings with defaults applied.
    """
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                loaded = json.load(f)
                return {**DEFAULT_SETTINGS, **loaded}
            except json.JSONDecodeError:
                print("Invalid settings file. Loading defaults.")
    return DEFAULT_SETTINGS.copy()

# === Save Settings to File ===
def save_settings(new_settings, SETTINGS_FILE):
    """
    Save settings dictionary to a JSON file.

    Args:
        new_settings (dict): The dictionary of settings to save.
        SETTINGS_FILE (str): Path to JSON config.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f, indent=4)

# === Curve Mapping Function ===
def curve(x, type="quadratic"):
    """
    Apply a nonlinear mapping to control intensity.

    Args:
        x (float): Input value (0.0–1.0).
        type (str): One of 'quadratic', 'cubic', 'expo', 'sigmoid'.

    Returns:
        float: Transformed output value.
    """
    if type == "quadratic":
        return x * x
    elif type == "cubic":
        return x ** 3
    elif type == "expo":
        return 1 - math.exp(-5 * x)
    elif type == "sigmoid":
        k = 10
        return 1 / (1 + math.exp(-k * (x - 0.5)))
    return x  # fallback
