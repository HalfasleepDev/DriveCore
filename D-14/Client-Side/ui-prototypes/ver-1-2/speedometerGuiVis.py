import sys
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QConicalGradient, QFont, QColor, QPen
from PySide6.QtCore import Qt, QTimer, QRectF
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class SpeedometerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore Speedometer")
        self.setGeometry(100, 100, 300, 300) # Maybe use fixed size

        # Customizable µs range
        self.min_us = 1310
        self.neutral_us = 1500
        self.max_us = 1750

        self.current_us = self.neutral_us
        self.target_us = self.neutral_us

        # Smooth animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_us)
        self.timer.start(20)

        # Simulate throttle input
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self.simulate_input)
        self.sim_timer.start(1000)

    def simulate_input(self):
        import random
        # Simulate forward, reverse, or neutral randomly
        choices = [self.max_us, self.min_us, self.neutral_us, 1650]
        self.target_us = random.choice(choices)

    def animate_us(self):
        if self.current_us < self.target_us:
            self.current_us = min(self.current_us + 10, self.target_us)
        elif self.current_us > self.target_us:
            self.current_us = max(self.current_us - 10, self.target_us)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = min(self.width(), self.height())
        center = self.rect().center()
        radius = size * 0.4

        # Draw background circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#222"))
        painter.drawEllipse(center, radius, radius)

        # Full arc span
        arc_span = 270  # degrees
        arc_start_angle = -135  # starting from bottom center

        # Calculate normalized value from neutral (range: -1 to 1)
        value_range = self.max_us - self.min_us
        offset = self.current_us - self.neutral_us
        norm_value = offset / (value_range / 2)  # -1 to 1

        # Clamp and convert to arc span
        norm_value = max(-1, min(1, norm_value))
        span_angle = int(norm_value * arc_span * 16)

        # Gradient setup
        if self.current_us >= 1650:
            gradient = QConicalGradient(center, arc_start_angle)
            gradient.setColorAt(0.0, QColor("#ffaa00"))
            gradient.setColorAt(0.5, QColor("#ff4444"))
            gradient.setColorAt(1.0, QColor("#ffaa00"))
        elif self.current_us < self.neutral_us:
            gradient = QConicalGradient(center, -90)
            gradient.setColorAt(0.0, QColor("#d97bff"))
            gradient.setColorAt(0.5, QColor("#b033ff"))
            gradient.setColorAt(1.0, QColor("#d97bff"))
        else:
            gradient = QConicalGradient(center, arc_start_angle)
            gradient.setColorAt(0.0, QColor("#74e1ef"))
            gradient.setColorAt(0.5, QColor("#33aaff"))
            gradient.setColorAt(1.0, QColor("#74e1ef"))

        # Draw background arc
        painter.setPen(QPen(QColor("#333"), 18, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(
            QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
            arc_start_angle * 16,
            -arc_span * 16
        )

        # Draw filled arc
        painter.setPen(QPen(gradient, 18, Qt.SolidLine, Qt.RoundCap))

        if self.current_us < self.neutral_us:
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                315 * 16,
                -span_angle
            )

        else:
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                arc_start_angle * 16,
                -span_angle
            )

        # Draw µs value
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 28, QFont.Bold)) # TODO: Change font and size for main build
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.current_us} µs")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SpeedometerWidget()
    widget.show()
    sys.exit(app.exec())
