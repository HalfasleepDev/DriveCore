import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QProgressBar, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class InfotainmentStyleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore Infotainment Display")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #121212; color: white;")

        self.init_ui()

        # Simulated values for testing UI animation
        self.fake_throttle = 0
        self.fake_steering = 0
        self.fake_brake = False
        self.fake_neutral = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fake_status)
        self.timer.start(300)

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Vehicle Status Vis")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00adb5;")
        layout.addWidget(title)

        # Main Grid
        grid = QGridLayout()
        grid.setSpacing(20)

        # Throttle Meter
        self.throttle_bar = QProgressBar()
        self.throttle_bar.setRange(-100, 100)
        self.throttle_bar.setTextVisible(True)
        self.throttle_bar.setFormat("Throttle: %v%")
        self.throttle_bar.setStyleSheet(self.progress_style("#00ff99"))
        grid.addWidget(self.throttle_bar, 0, 0)

        # Steering Meter (centered around 0)
        self.steering_bar = QProgressBar()
        self.steering_bar.setRange(-100, 100)
        self.steering_bar.setTextVisible(True)
        self.steering_bar.setFormat("Steering: %v%")
        self.steering_bar.setStyleSheet(self.progress_style("#ffaa00"))
        grid.addWidget(self.steering_bar, 0, 1)

        # Brake and Neutral Display
        self.brake_label = self.build_status_box("Brake", active=False, color="#ff4444")
        self.neutral_label = self.build_status_box("Neutral", active=True, color="#44ff44")

        # PRND Display
        self.prnd_display = QLabel("P  R  N  D")
        self.prnd_display.setAlignment(Qt.AlignCenter)
        self.prnd_display.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.prnd_display.setStyleSheet("color: #00adb5; margin-top: 10px;")
        layout.addWidget(self.prnd_display)

        # Alert display
        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.alert_label.setStyleSheet("color: yellow; background-color: #333; padding: 10px; border-radius: 8px;")
        layout.addWidget(self.alert_label)
        grid.addWidget(self.brake_label, 1, 0)
        grid.addWidget(self.neutral_label, 1, 1)

        layout.addLayout(grid)
        self.setLayout(layout)

    def progress_style(self, color):
        return f"""
            QProgressBar {{
                border: 2px solid #2d2d2d;
                border-radius: 5px;
                background-color: #1e1e1e;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """

    def build_status_box(self, label, active=False, color="#ffffff"):
        box = QLabel()
        box.setAlignment(Qt.AlignCenter)
        box.setFont(QFont("Segoe UI", 14, QFont.Bold))
        box.setText(f"{label}: {'YES' if active else 'NO'}")
        box.setStyleSheet(f"""
            background-color: {color if active else '#2d2d2d'};
            color: {'white' if active else '#888888'};
            padding: 20px;
            border-radius: 10px;
        """)
        return box

    # DEMO only!
    def update_fake_status(self):
        prnd_states = ['P', 'R', 'N', 'D']
        self.current_prnd_index = getattr(self, 'current_prnd_index', 0)
        self.current_prnd_index = (self.current_prnd_index + 1) % len(prnd_states)
        self.update_prnd_display(prnd_states[self.current_prnd_index])

        self.fake_throttle = (self.fake_throttle + 15) % 220 - 100
        self.fake_steering = (self.fake_steering + 20) % 200 - 100
        self.fake_brake = not self.fake_brake
        self.fake_neutral = not self.fake_neutral

        self.show_alert(f"Gear: {prnd_states[self.current_prnd_index]}")

        self.set_status(
            throttle=self.fake_throttle,
            steering=self.fake_steering,
            brake=self.fake_brake,
            neutral=self.fake_neutral
        )

    def set_status(self, throttle, steering, brake, neutral):
        if throttle < 0:
            self.throttle_bar.setStyleSheet(self.progress_style("#ff4444")) # Red
        else:
            self.throttle_bar.setStyleSheet(self.progress_style("#00ff99")) # Green
        
        self.throttle_bar.setValue(throttle)
        self.steering_bar.setValue(steering)

        # Update Brake Label
        self.brake_label.setText(f"Brake: {'YES' if brake else 'NO'}")
        self.brake_label.setStyleSheet(f"""
            background-color: {'#ff4444' if brake else '#2d2d2d'};
            color: {'white' if brake else '#888888'};
            padding: 20px;
            border-radius: 10px;
        """)

        # Update Neutral Label
        self.neutral_label.setText(f"Neutral: {'YES' if neutral else 'NO'}")
        self.neutral_label.setStyleSheet(f"""
            background-color: {'#44ff44' if neutral else '#2d2d2d'};
            color: {'white' if neutral else '#888888'};
            padding: 20px;
            border-radius: 10px;
        """)

    def show_alert(self, message):
        self.alert_label.setText(message)

    def update_prnd_display(self, active_gear):
        styled = "  ".join([
            f"<span style='color:#00adb5;font-weight:bold;'>{g}</span>" if g == active_gear else f"<span style='color:#444;'>{g}</span>"
            for g in ['P', 'R', 'N', 'D']
        ])
        self.prnd_display.setText(f"<html><div style='letter-spacing:15px'>{styled}</div></html>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InfotainmentStyleUI()
    window.show()
    sys.exit(app.exec())
