from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, QThread, Signal, QEvent, Qt)
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

#from appFunctions import PageWithKeyEvents
from MainWindow import Ui_MainWindow

PORT = 4444 #TODO: move to settings

os.environ["QT_QPA_PLATFORM"] = "xcb"

# TODO: Add error popups

class VideoThread(QThread):
    frame_received = Signal(QImage)  # Signal to send new frame to UI

    def __init__(self, stream_url):
        super().__init__()
        self.stream_url = stream_url
        self.running = True  # Control flag for stopping thread

    def run(self):
        cap = cv2.VideoCapture(self.stream_url)

        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_received.emit(q_img)  # Emit the frame
            #else:
                #print("Failed to retrieve frame")
        
        cap.release()

    def stop(self):
        self.running = False
        self.wait()  # Ensure the thread is properly closed


class MainWindow(QMainWindow):
    IP_ADDR = ""
    STREAM_URL = ""
    VEHICLE_CONNECTION = False
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.inputIp.editingFinished.connect(self.setIp)
        self.ui.inputIp.editingFinished.connect(self.add_ip)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.recent_ips = self.load_recent_ips()
        self.ui.recentIpCombo.addItems(self.recent_ips)

        self.load_recent_ips()
        self.ui.ipComboBtn.clicked.connect(self.setIpCombo)
        
        '''###########################################Logic For Left Menu Buttons###########################################'''
        self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}")
        self.ui.homeBtn.clicked.connect(lambda: self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}"))
        self.ui.homeBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
        self.ui.homeBtn.clicked.connect(lambda: self.ui.driveBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))
        self.ui.homeBtn.clicked.connect(lambda: self.ui.settingsBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))
        self.ui.homeBtn.clicked.connect(lambda: self.thread.stop())

        self.ui.settingsBtn.clicked.connect(lambda: self.ui.settingsBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}"))
        self.ui.settingsBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.settingsPage))
        self.ui.settingsBtn.clicked.connect(lambda: self.ui.driveBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))
        self.ui.settingsBtn.clicked.connect(lambda: self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))
        self.ui.settingsBtn.clicked.connect(lambda: self.thread.stop())

        self.ui.driveBtn.clicked.connect(lambda: self.ui.driveBtn.setStyleSheet("QPushButton{background-color: #7a63ff;}"))
        self.ui.driveBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.drivePage))
        self.ui.driveBtn.clicked.connect(lambda: self.ui.homeBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))
        self.ui.driveBtn.clicked.connect(lambda: self.ui.settingsBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}"))

        self.ui.driveBtn.clicked.connect(lambda: self.iniDrivePage())
        #self.filter = KeyPressFilter()
        self.ui.emergencyDisconnectBtn.clicked.connect(lambda: self.emergencyDisconnect())
    

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

    def load_recent_ips(self):
        """ Loads recent IP addresses from a file. """
        filename = "recent_ips.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return [line.strip() for line in file.readlines()]
        return []
    
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

    def is_ip_address(self, s):
        try:
            ipaddress.ip_address(s)  # Try converting the string to an IP address
            return True
        except ValueError:
            print("ohno")
            return False  # Not a valid IP address
    
    def setIp(self):
        
        if self.is_ip_address(self.ui.inputIp.text()):
            self.IP_ADDR = self.ui.inputIp.text()
            self.STREAM_URL = "http://" + self.IP_ADDR + ":5000/video-feed"
            #self.STREAM_URL = self.IP_ADDR + ":5000/video_feed"
            print(self.STREAM_URL)
            try:
                self.client_socket.connect((self.IP_ADDR, PORT))
                print("Connected to Raspberry Pi")
                self.VEHICLE_CONNECTION = True
                self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")
                self.ui.vehicleTypeLabel.setText("RPI_D14")
                self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #32CD32;}")
            except ConnectionRefusedError:
                print("Failed to connect to Raspberry Pi")
                self.VEHICLE_CONNECTION = False
                self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #FFA500;}")
                
        else:
            self.ui.ipInputBox.setStyleSheet("QGroupBox::title{color: #FF0000;}")
    
    def setIpCombo(self):
        if self.is_ip_address(self.ui.recentIpCombo.currentText()):
            self.IP_ADDR = self.ui.recentIpCombo.currentText()
            self.STREAM_URL = "http://" + self.IP_ADDR + ":5000/video-feed"
            #self.STREAM_URL = self.IP_ADDR + ":5000/video_feed"
            print(self.STREAM_URL)
            try:
                self.client_socket.connect((self.IP_ADDR, PORT))
                print("Connected to Raspberry Pi")
                self.VEHICLE_CONNECTION = True
                self.ui.emergencyDisconnectBtn.setStyleSheet("QPushButton{background-color: #f1f3f3;}")
                self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #32CD32;}")
                self.ui.vehicleTypeLabel.setText("RPI_D14")
            except ConnectionRefusedError:
                print("Failed to connect to Raspberry Pi")
                self.VEHICLE_CONNECTION = False
                self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #FFA500;}")
        else:
            self.ui.recentIpBox.setStyleSheet("QGroupBox::title{color: #FF0000;}")
        

    def iniDrivePage(self):
        print('yay')
        print(self.STREAM_URL)
        if self.is_ip_address(self.IP_ADDR):
            self.thread = VideoThread(self.STREAM_URL)
            self.thread.frame_received.connect(self.update_frame)
            self.thread.start()
            #self.ui.drivePage.installEventFilter(self.filter)
            self.ui.videoStreamWidget.setStyleSheet("QWidget{background-color:  #0c0c0d;}")
            self.ui.drivePage.commandSignal.connect(self.changeKeyInfo)
            self.ui.drivePage.commandSignal.connect(self.send_command)
        else:
            self.ui.videoStreamLabel.setStyleSheet("QLabel{color: #1e1e21;}")

    def changeKeyInfo(self, command):
        if command == "UP":
            self.ui.wKeyLabel.setStyleSheet("QLabel{color: #7a63ff;}")
            self.ui.aKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.sKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.dKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
        elif command == "DOWN":
            self.ui.wKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.aKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;")
            self.ui.sKeyLabel.setStyleSheet("QLabel{color: #7a63ff;}")
            self.ui.dKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
        elif command == "LEFT":
            self.ui.wKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.aKeyLabel.setStyleSheet("QLabel{color: #7a63ff;}")
            self.ui.sKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.dKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
        elif command == "RIGHT":
            self.ui.wKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.aKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.sKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.dKeyLabel.setStyleSheet("QLabel{color: #7a63ff;}")
        elif command == "NEUTRAL":
            self.ui.wKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")
            self.ui.aKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;")
            self.ui.sKeyLabel.setStyleSheet("QLabel{color: #7a63ff;}")
            self.ui.dKeyLabel.setStyleSheet("QLabel{color: #f1f3f3;}")

    def send_command(self, command):
        """Send command to Raspberry Pi"""
        try:
            self.client_socket.send(command.encode())
            print(command + " sent!")
        except BrokenPipeError:
            print("Lost connection to Raspberry Pi")
            self.VEHICLE_CONNECTION = False

    
    def update_frame(self, q_img):
        """Update QLabel with new frame."""
        self.ui.videoStreamLabel.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        """Release resources when closing the window."""
        self.send_command("DISCONNECT")
        self.VEHICLE_CONNECTION = False
        self.client_socket.close()
        self.thread.stop()
        event.accept()
        self.client_socket.close()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.setWindowTitle("Drive Core Client Ver 1.0")

    sys.exit(app.exec())
