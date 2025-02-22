from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget, QPushButton
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, Signal
'''TODO:
- create LEFTUP, LEFTDOWN, RIGHTUP, RIGHTDOWN
'''

class PageWithKeyEvents(QWidget):
    """A QWidget that only detects key presses when active in QStackedWidget"""
    commandSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.pressed_keys = set()  # Store currently pressed keys
        # Ensure this widget can receive key events
        self.setFocusPolicy(Qt.StrongFocus)

        

    def keyPressEvent(self, event: QKeyEvent):
        """Detect keypress events and send commands"""
        self.pressed_keys.add(event.key())

        if Qt.Key_W in self.pressed_keys and Qt.Key_A in self.pressed_keys:
            self.commandSignal.emit("LEFTUP")
            print("TEST LU")
        elif Qt.Key_W in self.pressed_keys and Qt.Key_D in self.pressed_keys:
            self.commandSignal.emit("RIGHTUP")
            print("TEST RU")
        elif Qt.Key_S in self.pressed_keys and Qt.Key_A in self.pressed_keys:
            self.commandSignal.emit("LEFTDOWN")
            print("TEST LD")
        elif Qt.Key_S in self.pressed_keys and Qt.Key_D in self.pressed_keys:
             self.commandSignal.emit("RIGHTDOWN")
             print("TEST RD")
        elif Qt.Key_W in self.pressed_keys:
            self.commandSignal.emit("UP")
            print("TEST UP")
        elif Qt.Key_S in self.pressed_keys:
            self.commandSignal.emit("DOWN")
            print("TEST DOWN")
        elif Qt.Key_A in self.pressed_keys:
            self.commandSignal.emit("LEFT")
            print("TEST LEFT")
        elif Qt.Key_D in self.pressed_keys:
            self.commandSignal.emit("RIGHT")
            print("TEST RIGHT")
        else:
            pass
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """Detect key release events"""
        self.pressed_keys.discard(event.key()) #Remove released key from set

        if event.isAutoRepeat():
            return  # Ignore repeated key release
        if event.key() in [Qt.Key_W, Qt.Key_S]:  # Only reset if W or S was released
            self.commandSignal.emit("NEUTRAL")
            print("TEST NEUTRAL")
        elif event.key() in [Qt.Key_A, Qt.Key_D]:
            self.commandSignal.emit("CENTER")
            print("TEST CENTER")