from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QDoubleSpinBox, QPushButton, QFormLayout, QSlider
)
from PySide6.QtCore import Qt , QSize
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class ServoCenterTuner(QGroupBox):
    def __init__(self, on_send_callback=None):
        super().__init__("Fine Tune Servo Center")
        self.on_send = on_send_callback

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(900, 2100)
        self.slider.setValue(1500)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self._slider_moved)

        self.display = QLabel("Current µs: 1500")
        self.display.setAlignment(Qt.AlignCenter)

        btns = QHBoxLayout()
        self.set_btn = QPushButton("Set as Mid")
        self.set_btn.setMinimumSize(QSize(0, 25))
        self.reset_btn = QPushButton("Reset to 1500")
        self.reset_btn.setMinimumSize(QSize(0, 25))
        btns.addWidget(self.set_btn)
        btns.addWidget(self.reset_btn)

        self.set_btn.clicked.connect(self._save_mid)
        self.reset_btn.clicked.connect(lambda: self._update(1500))

        layout.addWidget(self.slider)
        layout.addWidget(self.display)
        layout.addLayout(btns)

        self._saved_mid = 1500

    def _slider_moved(self, val):
        self._update(val)

    def _update(self, val):
        self.slider.setValue(val)
        self.display.setText(f"Current µs: {val}")
        if self.on_send:
            self.on_send(val)

    def _save_mid(self):
        self._saved_mid = self.slider.value()
        print(f"[Servo Cal] Midpoint saved as: {self._saved_mid} µs")

    def get_mid_value(self):
        return self._saved_mid


class CalibrationWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QDoubleSpinBox {
                font-family: 'Adwaita Sans';
                font-size: 11px;
                padding: 4px;
                padding-left: 5px;
                border-width: 3px;
                background: #f1f3f3;
                color: #1e1e21;
                border-radius: 5px;
                border: none;
            }
            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                background: #1e1e21;
                border: none;
                border-radius: 5px;
                margin: 1px;
            }
            QDoubleSpinBox::up-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 2px solid #f1f3f3;
                margin: 1px;
            }

            QDoubleSpinBox::down-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 2px solid #f1f3f3;
                margin: 1px;
            }
            /* Hover effects (optional) */
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: #7a63ff;
            }
                              
            QSlider::handle:horizontal{
                background: #7a63ff;
                width: 10px;
                margin: -5px -1px;
                border-radius: 5px;
            }
            QSlider::add-page:horizontal{
                background: #f1f3f3;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal{
                background: #7a63ff;
                border-radius: 2px;
            }
            QLabel {
                font-family: 'Adwaita Sans';
                font-size: 11px;
                color: #f1f3f3;
            }
            QGroupBox {
                background-color: #1e1e21;
                border-radius: 5px;
                color: #f1f3f3;
                font-family: 'Adwaita Sans';
                font-size: 11px;
                margin-top: 20px;
            }
            QPushButton {
                font-family: 'Adwaita Sans';
                background-color: #f1f3f3;
                color: #0c0c0d;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            
        """)

        main_layout = QVBoxLayout(self)

        # === Servo Calibration ===
        servo_group = QGroupBox("Servo Calibration (µs)")
        servo_layout = QVBoxLayout()
        servo_form = QFormLayout()

        self.servo_min = QDoubleSpinBox()
        self.servo_min.setRange(500, 2500)
        self.servo_min.setValue(900)

        self.servo_max = QDoubleSpinBox()
        self.servo_max.setRange(500, 2500)
        self.servo_max.setValue(2100)

        servo_form.addRow("Min:", self.servo_min)
        servo_form.addRow("Max:", self.servo_max)

        self.servo_mid_tuner = ServoCenterTuner(self.preview_servo)
        servo_layout.addLayout(servo_form)
        servo_layout.addWidget(self.servo_mid_tuner)

        servo_test_btn = QPushButton("Test Servo")
        servo_test_btn.setMinimumSize(QSize(0, 25))
        servo_test_btn.clicked.connect(self.test_servo)
        servo_layout.addWidget(servo_test_btn)

        servo_group.setLayout(servo_layout)
        main_layout.addWidget(servo_group)

        # === ESC Calibration ===
        esc_group = QGroupBox("ESC Calibration (µs)")
        esc_form = QFormLayout()

        self.esc_min = QDoubleSpinBox()
        self.esc_min.setRange(500, 2500)
        self.esc_min.setValue(1310)

        self.esc_mid = QDoubleSpinBox()
        self.esc_mid.setRange(500, 2500)
        self.esc_mid.setValue(1500)

        self.esc_max = QDoubleSpinBox()
        self.esc_max.setRange(500, 2500)
        self.esc_max.setValue(1750)

        esc_form.addRow("Min:", self.esc_min)
        esc_form.addRow("Mid:", self.esc_mid)
        esc_form.addRow("Max:", self.esc_max)

        esc_test_btn = QPushButton("Test ESC")
        esc_test_btn.setMinimumSize(QSize(0, 25))
        esc_test_btn.clicked.connect(self.test_esc)
        esc_form.addRow(esc_test_btn)

        esc_group.setLayout(esc_form)
        main_layout.addWidget(esc_group)

        # === Future Curve Configuration ===
        curve_group = QGroupBox("Acceleration / Deceleration Curves")
        curve_layout = QVBoxLayout()
        curve_note = QLabel("Curve shaping will allow smooth acceleration profiles (coming soon).")
        curve_note.setWordWrap(True)
        curve_layout.addWidget(curve_note)
        curve_group.setLayout(curve_layout)

        main_layout.addWidget(curve_group)
        main_layout.addStretch()

    # === Preview callbacks ===
    def preview_servo(self, value):
        print(f"[Preview] Sending servo test µs: {value}")
        # TODO: Send live µs to servo

    def test_servo(self):
        print("[TEST] Servo Calibration:")
        print(f"Min: {self.servo_min.value()} µs")
        print(f"Mid: {self.servo_mid_tuner.get_mid_value()} µs")
        print(f"Max: {self.servo_max.value()} µs")

    def test_esc(self):
        print("[TEST] ESC Calibration:")
        print(f"Min: {self.esc_min.value()} µs")
        print(f"Mid: {self.esc_mid.value()} µs")
        print(f"Max: {self.esc_max.value()} µs")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = CalibrationWidget()
    
    window.setWindowTitle("Calibration Settings")
    window.resize(789, 600)
    
    window.show()
    sys.exit(app.exec())
