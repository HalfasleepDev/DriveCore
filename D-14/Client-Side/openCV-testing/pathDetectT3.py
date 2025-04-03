import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QSlider, QHBoxLayout, QFormLayout, QGroupBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import os

os.environ["QT_QPA_PLATFORM"] = "xcb" # For my Arch Linux environment

VIDEO_URL = "http://192.168.0.123:5000/video-feed"  # Video Stream URL

class FloorDetector(QMainWindow):

    # Set Up UI window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore – Floor/Open Space Detection/Path Detection/object Detection V3")
        self.setGeometry(100, 100, 800, 600)

        self.init_kalman_filter()

        self.video_label = QLabel("Connecting to video stream...")
        self.video_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Margin sliders 
        self.h_margin_slider = QSlider(Qt.Horizontal)
        self.s_margin_slider = QSlider(Qt.Horizontal)
        self.v_margin_slider = QSlider(Qt.Horizontal)
        # Create labels to display values
        self.h_margin_value = QLabel(str(self.h_margin_slider.value()))
        self.s_margin_value = QLabel(str(self.s_margin_slider.value()))
        self.v_margin_value = QLabel(str(self.v_margin_slider.value()))

        # Set range for sensitivity tuning
        self.h_margin_slider.setRange(0, 50)
        self.s_margin_slider.setRange(0, 100)
        self.v_margin_slider.setRange(0, 100)

        # Set default values
        self.h_margin_slider.setValue(50)
        self.s_margin_slider.setValue(85)
        self.v_margin_slider.setValue(93)

        self.h_margin_slider.valueChanged.connect(lambda val: self.h_margin_value.setText(str(val)))
        self.s_margin_slider.valueChanged.connect(lambda val: self.s_margin_value.setText(str(val)))
        self.v_margin_slider.valueChanged.connect(lambda val: self.v_margin_value.setText(str(val)))

        # Layout for margin controls
        margin_layout = QFormLayout()
        h_row = QHBoxLayout()
        h_row.addWidget(self.h_margin_slider)
        h_row.addWidget(self.h_margin_value)
        margin_layout.addRow("H Margin", h_row)

        s_row = QHBoxLayout()
        s_row.addWidget(self.s_margin_slider)
        s_row.addWidget(self.s_margin_value)
        margin_layout.addRow("S Margin", s_row)

        v_row = QHBoxLayout()
        v_row.addWidget(self.v_margin_slider)
        v_row.addWidget(self.v_margin_value)
        margin_layout.addRow("V Margin", v_row)
        margin_group = QGroupBox("HSV Sensitivity Margins")
        margin_group.setLayout(margin_layout)

        layout.addWidget(margin_group)

        self.cap = cv2.VideoCapture(VIDEO_URL)
        if not self.cap.isOpened():
            self.show_error("Video Stream Error", "Failed to connect to the camera stream.")
            self.video_label.setText("Error: Unable to open video stream.")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.frame_counter = 0
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=100, detectShadows=False)
    
    # Error popup
    def show_error(self, title: str, message: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    # Update the frame
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (1280, 720))   # TODO: The frame needs to be resized for the main app
        processed = self.detect_floor_region(frame)
        qt_image = self.convert_cv_qt(processed)
        self.video_label.setPixmap(qt_image)
    
    def init_kalman_filter(self):
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                                [0, 1, 0, 1],
                                                [0, 0, 1, 0],
                                                [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.05

    def detect_floor_region(self, frame):
        self.frame_counter += 1

        # Detect object frame boundaries
        height, width = frame.shape[:2]
        roi = frame[int(height * 0.5):, :]  # bottom half

        fgmask = self.fgbg.apply(roi)
        kernel = np.ones((5, 5), np.uint8)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, kernel, iterations=5)

        edges = cv2.Canny(roi, 50, 150)     # TODO: Edit values for edge detection
        combined_mask = cv2.bitwise_or(fgmask, edges)
        mask2 = cv2.bitwise_not(combined_mask)
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw obstacles with simulated depth
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                depth_y = y + int(height * 0.5)
                depth_score = 0.95 - (depth_y / height)
                depth_color = (0, int(255 * depth_score), 255 - int(255 * depth_score))
                cv2.rectangle(frame, (x, depth_y), (x + w, depth_y + h), depth_color, 2)
                cv2.putText(frame, f"Obstacle", (x, depth_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, depth_color, 1)
                
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width = hsv.shape[:2]

        # Larger and blurred sampling region
        sample_w, sample_h = 300, 50
        x_start = width // 2 - sample_w // 2
        y_start = height - sample_h - 10  # Closer to the bottom
        sample_region = hsv[y_start:y_start + sample_h, x_start:x_start + sample_w]

        # Blur sample to reduce noise
        blurred_sample = cv2.GaussianBlur(sample_region, (5, 5), 0)
        avg_hsv = cv2.mean(blurred_sample)[:3]  # Average H, S, V

        h, s, v = avg_hsv
        #h_margin, s_margin, v_margin = 15, 70, 60  # Less sensitive (15,60,60)
        h_margin = self.h_margin_slider.value()
        s_margin = self.s_margin_slider.value()
        v_margin = self.v_margin_slider.value()
        lower_floor = np.array([max(h - h_margin, 0), max(s - s_margin, 0), max(v - v_margin, 0)], dtype=np.uint8)
        upper_floor = np.array([min(h + h_margin, 180), min(s + s_margin, 255), min(v + v_margin, 255)], dtype=np.uint8)

        # Create mask using relaxed bounds
        mask = cv2.inRange(hsv, lower_floor, upper_floor)

        # Visual sampling region (optional)
        cv2.rectangle(frame, (x_start, y_start), (x_start + sample_w, y_start + sample_h), (255, 255, 0), 2)
        cv2.putText(frame, "Sampling floor color", (x_start - 20, y_start - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Focus on bottom half
        roi = np.zeros_like(mask)
        roi[int(height / 2):, :] = 255
        floor_mask = cv2.bitwise_and(mask, roi, mask2)
        #floor_mask = cv2.bitwise_not(floor_mask1, mask2) 

        # Morphological cleanup
        kernel = np.ones((8, 8), np.uint8)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_DILATE, kernel)
                
        # Detect floor contour
        contours, _ = cv2.findContours(floor_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            cv2.drawContours(frame, [largest], -1, (0, 255, 0), 3)

            M = cv2.moments(largest)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Kalman update
                measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
                self.kalman.correct(measurement)
                prediction = self.kalman.predict()
                kx, ky = int(prediction[0]), int(prediction[1])

                # Draw predicted center
                cv2.circle(frame, (kx, ky), 5, (0, 255, 255), -1)
                cv2.putText(frame, "Kalman Center", (kx - 40, ky - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            self.draw_kalman_smoothed_curve(frame, largest, self.frame_counter)

        return frame
    
    def draw_kalman_smoothed_curve(self, frame, contour_points, frame_count):
        pts = np.array(contour_points).reshape(-1, 2)
        if len(pts) < 6:
            return

        # Frame size
        height, width = frame.shape[:2]
        bottom_center = (width // 2, height - 1)

        # Reduce frequency of updates
        if frame_count % 5 != 0 and hasattr(self, 'smoothed_curve'):
            # Just redraw last smoothed path
            for i in range(len(self.smoothed_curve) - 1):
                pt1 = self.smoothed_curve[i]
                pt2 = self.smoothed_curve[i + 1]
                cv2.line(frame, pt1, pt2, (255, 0, 0), 2)
            return

        # Centerline from contour
        pts = pts[np.argsort(pts[:, 1])]  # sort by y

        y_to_x = {}
        for x, y in pts:
            y = int(y)
            y_to_x.setdefault(y, []).append(x)

        y_vals = sorted(y_to_x.keys())
        centerline = []
        for y in y_vals:
            x_vals = y_to_x[y]
            if len(x_vals) >= 2:
                centerline.append((sum(x_vals) / len(x_vals), y))

        if len(centerline) < 6:
            return

        centerline = np.array(centerline)
        xs, ys = centerline[:, 0], centerline[:, 1]

        try:
            # Fit polynomial
            poly = np.polyfit(ys, xs, deg=2)
            smooth_y = np.linspace(ys[0], ys[-1], 50)
            smooth_x = np.polyval(poly, smooth_y)

            # Use midpoint as Kalman measurement
            mid_idx = len(smooth_y) // 2
            measurement = np.array([[np.float32(smooth_x[mid_idx])],
                                    [np.float32(smooth_y[mid_idx])]])
            self.kalman.correct(measurement)
            prediction = self.kalman.predict()
            dx = prediction[0] - smooth_x[mid_idx]
            dy = prediction[1] - smooth_y[mid_idx]

            # Apply Kalman offset
            path_points = []
            #path_points[0] = bottom_center
            for i in range(len(smooth_x)):
                x = int(smooth_x[i] + dx)
                y = int(smooth_y[i] + dy)
                path_points.append((x, y))

            # Anchor path to bottom center
            #path_points[0] = bottom_center

            # Store for future redraw
            self.smoothed_curve = path_points

            # Draw final path
            for i in range(len(path_points) - 1):
                if i == 0:
                    cv2.line(frame, path_points[i], path_points[i + 1], (255, 255, 0), 2)
                cv2.line(frame, path_points[i], path_points[i + 1], (255, 0, 0), 2)

            # Draw predicted center
            cv2.circle(frame, (int(prediction[0]), int(prediction[1])), 5, (0, 255, 255), -1)

        except Exception as e:
            print("Path fitting error:", e)

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