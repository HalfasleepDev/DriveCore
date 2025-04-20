from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget, QPushButton, QMessageBox
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, Signal, QTimer
import time

'''Keypress Page Class'''
class PageWithKeyEvents(QWidget):
    """A QWidget that only detects key presses when active in QStackedWidget"""
    commandSignal = Signal(str)

    def __init__(self):
        super().__init__()
        self.pressed_keys = set()
        self.setFocusPolicy(Qt.StrongFocus)

        # For send interval tracking
        self.last_command_time = 0
        self.COMMAND_INTERVAL = 0.05  # seconds
        self.last_command_sent = None
        self.last_break_command_time = 0
        self.COMMAND_BRAKE_INTERVAL = 0.5   # seconds


        

    def send_command(self, command: str):
        """Throttle and emit command if interval has passed"""
        now = time.monotonic()
        if (now - self.last_command_time) >= self.COMMAND_INTERVAL or command != self.last_command_sent:
            self.commandSignal.emit(command)
            self.last_command_time = now
            self.last_command_sent = command

    def keyPressEvent(self, event: QKeyEvent):
        self.pressed_keys.add(event.key())

        if Qt.Key_W in self.pressed_keys and Qt.Key_A in self.pressed_keys:
            self.send_command("LEFTUP")
            print("TEST LU")
        elif Qt.Key_W in self.pressed_keys and Qt.Key_D in self.pressed_keys:
            self.send_command("RIGHTUP")
            print("TEST RU")
        elif Qt.Key_S in self.pressed_keys and Qt.Key_A in self.pressed_keys:
            self.send_command("LEFTDOWN")
            print("TEST LD")
        elif Qt.Key_S in self.pressed_keys and Qt.Key_D in self.pressed_keys:
            self.send_command("RIGHTDOWN")
            print("TEST RD")
        elif Qt.Key_W in self.pressed_keys:
            self.send_command("UP")
            print("TEST UP")
        elif Qt.Key_S in self.pressed_keys:
            self.send_command("DOWN")
            print("TEST DOWN")
        elif Qt.Key_A in self.pressed_keys:
            self.send_command("LEFT")
            print("TEST LEFT")
        elif Qt.Key_D in self.pressed_keys:
            self.send_command("RIGHT")
            print("TEST RIGHT")
        elif Qt.Key_Space in self.pressed_keys:
            print ("TEST BRAKE")
            self.send_command("BRAKE")

    def keyReleaseEvent(self, event: QKeyEvent):
        self.pressed_keys.discard(event.key())

        if event.isAutoRepeat():
            return
        if event.key() in [Qt.Key_W, Qt.Key_S]:
            self.send_command("NEUTRAL")
            print("TEST NEUTRAL")
        elif event.key() in [Qt.Key_A, Qt.Key_D]:
            self.send_command("CENTER")
            print("TEST CENTER")
    
    def send_brake_burst(self, count, interval):
        """Send 'BRAKE' command `count` times every `interval` milliseconds"""
        now = time.monotonic()
        if (now - self.last_break_command_time) >= self.COMMAND_BRAKE_INTERVAL:
            self.last_command_time = now
            for i in range(count):
                QTimer.singleShot(i * interval, lambda: self.send_command("BRAKE"))
                print("TEST BRAKE CV")

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

#def logToSystem()

