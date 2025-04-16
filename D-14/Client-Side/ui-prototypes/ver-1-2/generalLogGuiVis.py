import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"


class LogConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore Logs")
        self.setMinimumSize(420, 260)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e21;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # === Scrollable log viewer ===
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Adwaita Mono", 10)) # TODO: Fix fornt for Ver 1.2
        # TODO: Fix the border-radius for Ver 1.2
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0d;
                color: #f1f3f3;
                border: 1px solid #0c0c0d;
                border-radius: 8px;
                padding: 8px;
            }
            QScrollBar:vertical {
                background: #1e1e21;
                width: 8px;
                margin: 4px 2px 4px 2px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #7a63ff;
                min-height: 20px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #f1f3f3;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # === Clear button with modern style ===
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f3;
                color: #0c0c0d;
                padding: 8px 14px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            QPushButton:pressed {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
        """)

        layout.addWidget(self.log_output)
        layout.addWidget(self.clear_button, alignment=Qt.AlignCenter)

    def add_log(self, message: str):
        """Append a log message to the console"""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        """Clear all log output"""
        self.log_output.clear()


# === DEMO ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = LogConsoleWidget()
    widget.show()

    # Simulated log generator
    from PySide6.QtCore import QTimer
    import random
    sample_msgs = [
        "[INFO] Vehicle initialized",
        "[WARNING] Brake pulse delay detected",
        "[DEBUG] Path update triggered",
        "[ERROR] UDP timeout",
        "[INFO] Object detection toggle: ON"
    ]
    timer = QTimer()
    timer.timeout.connect(lambda: widget.add_log(random.choice(sample_msgs)))
    timer.start(1000)

    sys.exit(app.exec())
