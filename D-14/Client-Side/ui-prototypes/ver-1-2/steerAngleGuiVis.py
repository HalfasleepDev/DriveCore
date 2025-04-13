import sys
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QFont
from PySide6.QtCore import Qt, QTimer
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class SteeringPathWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.setWindowTitle("Steering Path PWM")

        # === µs PWM Limits ===
        self.min_us = 900
        self.center_us = 1500
        self.max_us = 2100

        # Internal angle (0 = center)
        self._current_us = self.center_us
        self._target_us = self.center_us
        self._smoothing_speed = 2

        # Timer for smooth animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

        # Simulate input (for testing)
        self.demo = QTimer(self)
        self.demo.timeout.connect(self.simulate_input)
        self.demo.start(1000)

    def simulate_input(self):
        import random
        self.set_steering_us(random.choice([900, 1100, 1500, 1800, 2100]))

    def set_steering_us(self, us_val: int):
        self._target_us = max(self.min_us, min(self.max_us, us_val))

    def animate(self):
        if abs(self._target_us - self._current_us) > 1:
            self._current_us += (self._target_us - self._current_us) / self._smoothing_speed
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center_x = w // 2
        bottom_y = h - 50

        # === Background ===
        painter.setBrush(QColor("#1a1a1a"))
        painter.setPen(QColor("#444"))
        painter.drawRoundedRect(5, 5, w - 10, h - 10, 15, 15)

        # === Normalize PWM to curve ratio ===
        us_range = self.max_us - self.min_us
        curve_ratio = (self._current_us - self.center_us) / (us_range / 2)
        curve_ratio = max(-1.0, min(1.0, curve_ratio))

        # === Build curved path ===
        curve_amount = curve_ratio * (w * 0.9)
        path = QPainterPath()
        path.moveTo(center_x, bottom_y)
        control_x = center_x + curve_amount
        control_y = h * 0.4
        end_y = 40  # Adjust this to move the tip downward (default was 25)
        path.quadTo(control_x, control_y, center_x, end_y)

        # === Curve Color ===
        if curve_ratio < 0:
            color = "#ff55aa"  # Left
        elif curve_ratio > 0:
            color = "#00ffaa"  # Right
        else:
            color = "#888888"  # Center

        # Draw the arc
        pen = QPen(QColor(color), 4)
        painter.setPen(pen)
        painter.drawPath(path)

        # === Draw tip marker ===
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 4, end_y - 4, 8, 8)

        # === Draw arc labels ===
        painter.setPen(QColor("#aaaaaa"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(20, h - 25, "L")           # Left
        painter.drawText(center_x - 5, h - 25, "C")  # Center
        painter.drawText(w - 30, h - 25, "R")        # Right

        # === µs + Percentage Display ===
        painter.setPen(QColor("#ffffff"))
        steering_percent = curve_ratio * 100
        painter.setFont(QFont("Segoe UI", 14))
        painter.drawText(self.rect().adjusted(0, 5, 0, -10), Qt.AlignTop | Qt.AlignHCenter,
                         f"{int(self._current_us)} µs ({steering_percent:+.0f}%)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SteeringPathWidget()
    widget.show()
    sys.exit(app.exec())
