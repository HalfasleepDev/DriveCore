import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QPalette


class DriveAssistWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(130, 300)
        self.setWindowTitle("Drive Assist")

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e21;
                border-radius: 15px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # === Assist Toggle Section ===
        self.toggle_button = QPushButton("Drive Assist: OFF")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f3;
                color: #0c0c0d;
                padding: 10px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            QPushButton:checked {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_assist)

        # === Warning Section ===
        self.warning_label = QLabel("No active warnings")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #0c0c0d;
                color: #f1f3f3;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        main_layout.addWidget(self.toggle_button)
        main_layout.addSpacing(5)
        main_layout.addWidget(self.warning_label)

        # === Flashing warning animation timer ===
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._flash_warning)
        self._flash_state = False
        self._alert_active = False

    def toggle_assist(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("Drive Assist: ON")
        else:
            self.toggle_button.setText("Drive Assist: OFF")
        # TODO: Emit signal or call control logic here

    def show_warning(self, message: str):
        """Show a high-priority warning and start flashing"""
        self.warning_label.setText(message)
        self._alert_active = True
        self._flash_state = False
        self.flash_timer.start(500)

    def clear_warning(self):
        """Clear any warning and stop animation"""
        self.warning_label.setText("No active warnings")
        self._alert_active = False
        self.flash_timer.stop()
        self._reset_warning_style()

    def _flash_warning(self):
        if not self._alert_active:
            return

        self._flash_state = not self._flash_state
        if self._flash_state:
            self.warning_label.setStyleSheet("""
                QLabel {
                    background-color: #ff4444;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        else:
            self._reset_warning_style()

    def _reset_warning_style(self):
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #0c0c0d;
                color: #f1f3f3;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)


# === Demo App ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DriveAssistWidget()
    widget.show()

    # Simulate a warning
    from PySide6.QtCore import QTimer
    QTimer.singleShot(2000, lambda: widget.show_warning("Obstacle Detected!"))
    QTimer.singleShot(6000, lambda: widget.clear_warning())

    sys.exit(app.exec())
