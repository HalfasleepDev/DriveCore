import sys
import socket
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"
 
# Raspberry Pi IP address (update with actual IP)
RASPBERRY_PI_IP = '192.168.0.102'
PORT = 4444

class CarControlClient(QWidget):
    def __init__(self):
        super().__init__()

        # Setup UI
        self.setWindowTitle("RC Car Controller")
        self.setGeometry(100, 100, 400, 200)

        self.label = QLabel("Use W, A, S, D to control the car\nESC to exit", self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Setup socket connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((RASPBERRY_PI_IP, PORT))
            print("Connected to Raspberry Pi")
        except ConnectionRefusedError:
            print("Failed to connect to Raspberry Pi")
            sys.exit(1)

    def send_command(self, command):
        """Send command to Raspberry Pi"""
        try:
            self.client_socket.send(command.encode())
        except BrokenPipeError:
            print("Lost connection to Raspberry Pi")
            sys.exit(1)

    def keyPressEvent(self, event: QKeyEvent):
        """Detect keypress events and send commands"""
        key = event.key()
        if key == Qt.Key_W:
            self.send_command("UP")
        elif key == Qt.Key_S:
            self.send_command("DOWN")
            
        if key == Qt.Key_A:
            self.send_command("LEFT")
        elif key == Qt.Key_D:
            self.send_command("RIGHT")

        #TODO:ADD LEFT-FORWARD....etc
        elif key == Qt.Key_Escape:
            self.send_command("STOP")
            self.client_socket.close()
            QApplication.quit()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Detect key release events"""
        if event.isAutoRepeat():
            return  # Ignore repeated key release
        if event.key() in [Qt.Key_W, Qt.Key_S]:  # Only reset if W or S was released
            self.send_command("NEUTRAL")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarControlClient()
    window.show()
    sys.exit(app.exec())
