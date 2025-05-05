from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor
import sys


class StylishPopup(QWidget):
    def __init__(self, title="Notice", message="Something happened!", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360, 160)

        # === Styles ===
        self.setStyleSheet("""
            QWidget {
                background-color: #0c0c0d;
                border-radius: 15px;
            }
            QLabel#title {
                color: #f1f3f3;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#message {
                color: #f1f3f3;
                font-size: 16px;
            }
            QPushButton {
                background-color: #1e1e21;
                color: #f1f3f3;
                padding: 5px 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #74e1ef;
                color: #0c0c0d;
            }
        """)

        # === Layout ===
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)

        self.message_label = QLabel(message, self)
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.close_popup)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)

        # === Fade animation ===
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.anim = QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)

        # Auto-dismiss timer
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.close_popup)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#0c0c0d"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def show_popup(self, duration=0, near_widget=None):
        """Show popup near another widget or centered, with optional auto-dismiss."""
        if near_widget:
            pos = near_widget.mapToGlobal(near_widget.rect().center())
            self.move(pos.x() - self.width() // 2, pos.y() - self.height() - 20)
        else:
            self.move(100, 100)

        self.opacity.setOpacity(0.0)
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        self.show()

        if duration > 0:
            self.auto_close_timer.start(duration)

    def close_popup(self):
        """Close the popup with a fade-out animation."""
        self.anim.stop()
        self.anim.setStartValue(self.opacity.opacity())
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.close)
        self.anim.start()


# === Demo Run ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = StylishPopup("Invalid Credentials", "Username or password is incorrect.")
    #demo.show_popup(duration=6000)
    demo.show_popup()
    sys.exit(app.exec())
