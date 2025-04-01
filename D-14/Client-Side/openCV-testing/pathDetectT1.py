import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

VIDEO_URL = "http://192.168.0.123:5000/video-feed"  # Video Stream URL

class FloorDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore – Floor/Open Space Detection")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel("Connecting to video stream...")
        self.video_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.cap = cv2.VideoCapture(VIDEO_URL)
        if not self.cap.isOpened():
            self.video_label.setText("Error: Unable to open video stream.")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (640, 480))
        processed = self.detect_floor_region(frame)
        qt_image = self.convert_cv_qt(processed)
        self.video_label.setPixmap(qt_image)

    def detect_floor_region(self, frame):
        # Convert to HSV for more stable color filtering
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define color range for floor (light gray / beige / off-white)
        lower_floor = np.array([0, 0, 160])    # adjust to match your floor color
        # TODO: Add an auto detect floor color
        
        upper_floor = np.array([180, 50, 255]) # light colors, low saturation

        # Mask floor-colored regions
        mask = cv2.inRange(hsv, lower_floor, upper_floor)

        # Define a region of interest (bottom half of the image)
        height, width = mask.shape
        roi = np.zeros_like(mask)
        roi[int(height / 2):, :] = 255
        floor_mask = cv2.bitwise_and(mask, roi)

        # Morphological ops to clean mask
        kernel = np.ones((5, 5), np.uint8)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_DILATE, kernel)

        # Find contours of detected floor
        contours, _ = cv2.findContours(floor_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            cv2.drawContours(frame, [largest], -1, (0, 255, 0), 3)

            # Optional: draw center of floor region
            M = cv2.moments(largest)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, "Floor Center", (cx - 40, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
            # Path tracing
            pts = np.array(largest).reshape(-1, 2)
            if len(pts) > 5:
                try:
                    poly = np.polyfit(pts[:, 1], pts[:, 0], 2)
                    y_vals = np.linspace(min(pts[:, 1]), max(pts[:, 1]), 50)
                    x_vals = np.polyval(poly, y_vals)
                    for i in range(len(x_vals) - 1):
                        pt1 = (int(x_vals[i]), int(y_vals[i]))
                        pt2 = (int(x_vals[i + 1]), int(y_vals[i + 1]))
                        cv2.line(frame, pt1, pt2, (255, 0, 0), 2)
                except Exception as e:
                    print(f"Curve fitting error: {e}")

        return frame

    def convert_cv_qt(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        return QPixmap.fromImage(QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888))

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloorDetector()
    window.show()
    sys.exit(app.exec())