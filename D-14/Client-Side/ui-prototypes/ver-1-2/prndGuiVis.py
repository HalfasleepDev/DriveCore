import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QTimer, QRectF
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class PRNDWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 300) 
        self.setWindowTitle("PRND Gear Selector")

        self.gears = ["P", "R", "N", "D"]
        self.current_gear = "P"
        self.highlight_y = 0  # Animated Y position
        self.target_y = 0

        self.font = QFont("Segoe UI", 20, QFont.Bold)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

        # Demo cycling gears
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.cycle_gear)
        self.demo_timer.start(1500)

    def cycle_gear(self):
        idx = self.gears.index(self.current_gear)
        next_gear = self.gears[(idx + 1) % len(self.gears)]
        self.set_gear(next_gear)

    def set_gear(self, gear: str):
        if gear in self.gears:
            self.current_gear = gear
            index = self.gears.index(gear)
            gear_height = self.height() // len(self.gears)
            self.target_y = index * gear_height

    def animate(self):
        # Smooth transition to target highlight position
        if abs(self.highlight_y - self.target_y) > 1:
            self.highlight_y += (self.target_y - self.highlight_y) / 4
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        gear_height = h // len(self.gears)

        # Background
        painter.fillRect(self.rect(), QColor("#1e1e21"))

        # Highlight bar
        highlight_rect = QRectF(5, self.highlight_y + 5, w - 10, gear_height - 10)
        painter.setBrush(QColor("#74e1ef"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(highlight_rect, 8, 8)

        # Draw each gear letter
        for i, gear in enumerate(self.gears):
            y = i * gear_height
            rect = QRectF(0, y, w, gear_height)

            # Bold font for selected gear, regular for others
            font = QFont("Segoe UI", 20)
            if gear == self.current_gear:
                font.setBold(True)
                painter.setPen(QColor("#0c0c0d"))
            else:
                font.setBold(False)
                painter.setPen(QColor("#f1f3f3"))
                
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, gear)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PRNDWidget()
    widget.show()
    sys.exit(app.exec())
