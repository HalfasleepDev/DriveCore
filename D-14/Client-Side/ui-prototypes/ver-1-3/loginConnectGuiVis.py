from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sys
import os
import json

class CarConnectWidget(QWidget):
    """
    A login-style widget for connecting to the car using username and password.
    """

    #SETTINGS_PATH = "D-14/Client-Side/client-app/settings.json" #!DO NOT MODIFY THE SETTINGS HERE!!!

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QWidget {
                background-color: #7a63ff;
                border-radius: 15px;
            }
            QLabel {
                color: #f1f3f3;
                font-family: 'Adwaita Sans';
            }
            QLineEdit {
                background-color: #f1f3f3;
                color: #0c0c0d;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'Adwaita Sans';
            }
            QPushButton {
                background-color: #1e1e21;
                color: #f1f3f3;
                padding: 10px;
                border-radius: 15px;
                font-size: 11pt;
                font-family: 'Adwaita Sans';
            }
            QPushButton:hover {
                background-color: #74e1ef;
                color: #0c0c0d;
            }
        """)

        # === UI Elements ===
        self.title = QLabel("Connect to Host")
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setFont(QFont("Adwaita Sans", 15, QFont.Bold))

        self.subtitle = QLabel("Please enter your credentials to connect to the vehicle.")
        self.subtitle.setAlignment(Qt.AlignHCenter)
        self.subtitle.setWordWrap(True)

        self.username_title = QLabel("Username")
        self.username_title.setAlignment(Qt.AlignLeft)
        self.username_title.setFont(QFont("Adwaita Sans", 15)) 

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_title = QLabel("Password")
        self.password_title.setAlignment(Qt.AlignLeft)
        self.password_title.setFont(QFont("Adwaita Sans", 15)) 

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.attempt_connection)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ffaaaa; font-size: 11pt;")
        self.error_label.setAlignment(Qt.AlignHCenter)
        self.error_label.hide()

        # === Layout ===
        layout = QVBoxLayout(self)
        #layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 10, 0)

        layout.addWidget(self.title, 0)
        layout.addSpacing(15)
        layout.addWidget(self.subtitle, 0)
        layout.addSpacing(30)
        layout.addWidget(self.username_title)
        layout.addWidget(self.username_input, 0)
        layout.addSpacing(15)
        layout.addWidget(self.password_title)
        layout.addWidget(self.password_input, 0)
        layout.addSpacing(10)
        layout.addWidget(self.error_label)
        layout.addSpacing(10)
        layout.addWidget(self.connect_btn, 0)
        
        #! Fix with the actual settings def
        self.load_credentials()  # Autofill on startup
    #! Fix with the actual settings def
    def load_credentials(self):
        """Load saved credentials from disk and autofill the fields."""
        if os.path.exists(self.SETTINGS_PATH):
            with open(self.SETTINGS_PATH, "r") as f:
                try:
                    data = json.load(f)
                    self.username_input.setText(data.get("username", ""))
                    self.password_input.setText(data.get("password", ""))
                except Exception as e:
                    print(f"[ERROR] Failed to load credentials: {e}")
    #! Fix with the actual settings def
    def save_credentials(self, username, password):
        """Save credentials to disk (password optional)."""
        os.makedirs(os.path.dirname(self.SETTINGS_PATH), exist_ok=True)
        data = {
            "username": username,
            "password": password  # Or leave blank
        }
        with open(self.SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=2)
        
    def attempt_connection(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please enter both username and password.")
        elif username != "test" or password != "123":
            self.show_error("Invalid credentials. Please try again.")
        else:
            self.save_credentials(username, password)
            print(f"[INFO] Connecting to car as '{username}'...")
            self.error_label.hide()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setStyleSheet("""
        QWidget {
                background-color: #7a63ff;
                border-radius: 15px;
            }

    """)
    layout = QVBoxLayout(window)
    login_widget = CarConnectWidget()
    layout.addWidget(login_widget, alignment=Qt.AlignHCenter)
    window.setFixedSize(410, 400)
    window.setWindowTitle("DriveCore Car Connect")
    window.show()
    sys.exit(app.exec())
