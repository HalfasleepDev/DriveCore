import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QSlider, QHBoxLayout, QFormLayout, QGroupBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import os
import torch
from torchvision import transforms
os.environ["QT_QPA_PLATFORM"] = "xcb" # For my Arch Linux environment
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# Depth model
sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/Depth-Anything-V2/metric_depth')
from depth_anything_v2.dpt import DepthAnythingV2

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
depth_model = DepthAnythingV2(encoder="vits", features=64,
                              out_channels=[48, 96, 192, 384], max_depth=1)
ckpt = torch.load("Depth-Anything-V2/checkpoints/depth_anything_v2_metric_hypersim_vits.pth", map_location=device)
depth_model.load_state_dict(ckpt, strict=True)
depth_model.eval().to(device)

def infer_depth_colormap(frame_bgr, model, size=210):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(frame_rgb, (size, size), interpolation=cv2.INTER_AREA)
    img = resized.astype(np.float32) / 255.0
    img = (img - 0.5) / 0.5
    tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0).to(device).float()

    with torch.no_grad():
        depth = model(tensor).squeeze().cpu().numpy()

    # Resize and colormap
    depth_resized = cv2.resize(depth, (frame_bgr.shape[1], frame_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
    norm = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.applyColorMap(norm, cv2.COLORMAP_MAGMA)

VIDEO_URL = "http://10.0.0.11:5000/video-feed"  # Video Stream URL

class FloorDetector(QMainWindow):

    # Set Up UI window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DriveCore – Floor/Open Space Detection/Path Detection/Object Detection/Collision warning/Sample Adjust  V4")
        self.setGeometry(100, 100, 800, 600)

        self.init_kalman_filter()

        self.video_label = QLabel("Connecting to video stream...")
        self.video_label.setAlignment(Qt.AlignCenter)

        

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.hsv_debug = QLabel("Auto HSV: h=-- s=-- v=--")
        layout.addWidget(self.hsv_debug)

        self.ambient_debug = QLabel("Ambient Shift – Hue:-- Value:--")
        layout.addWidget(self.ambient_debug)

        self.alert_zone_debug = QLabel("Safe")
        layout.addWidget(self.alert_zone_debug)

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
        self.h_margin_slider.setValue(35)
        self.s_margin_slider.setValue(40)
        self.v_margin_slider.setValue(50)

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
        margin_group = QGroupBox("Min HSV Sensitivity Margins")
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
        self.last_floor_contour = None

        self.alert_line_y = 680  # e.g. bottom quarter of 480p frame
        self.alert_triggered = False
    
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

        
        frame = cv2.resize(frame, (1280, 720))
        depth_overlay = infer_depth_colormap(frame, depth_model)
        processed = self.detect_floor_region(depth_overlay)
        qt_image = self.convert_cv_qt(processed)
        self.video_label.setPixmap(qt_image)
        self.hsv_debug.setText(f"Auto HSV Margin: H={self.auto_h_margin} S={self.auto_s_margin} V={self.auto_v_margin}")
    
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
        self.alert_triggered = False  # reset each frame

        # Detect object frame boundaries
        height, width = frame.shape[:2]
        roi = frame[int(height * 0.5):, :]  # bottom half

        gray_bottom = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        fgmask = self.fgbg.apply(roi)
        kernel = np.ones((5, 5), np.uint8)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)

        edges = cv2.Canny(gray_bottom, 50, 200)
        #edges = cv2.Canny(roi, 50, 200)     # TODO: Edit values for edge detection
        combined_mask = cv2.bitwise_or(fgmask, edges)
        mask2 = cv2.bitwise_not(combined_mask)

        # Better obstacle contours
        min_obstacle_area = 1000  # Ignore tiny noise

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_obstacle_area:
                x, y, w, h = cv2.boundingRect(cnt)
                depth_y = y + int(height * 0.5)

                # Check if the box crosses the alert line
                if depth_y + h > self.alert_line_y:
                    self.alert_triggered = True

                depth_score = 0.95 - (depth_y / height)
                depth_color = (0, int(255 * depth_score), 255 - int(255 * depth_score))

                # Draw smoothed bounding box
                cv2.rectangle(frame, (x, depth_y), (x + w, depth_y + h), depth_color, 2)
                cv2.putText(frame, "Obstacle", (x, depth_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, depth_color, 1)


        # Larger and blurred sampling region
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width = hsv.shape[:2]

        # === Ambient Light Sampling ===
        ambient_w, ambient_h = 600, 30
        x_a = width // 2 - ambient_w // 2
        y_a = 90
        ambient_sample = hsv[y_a:y_a + ambient_h, x_a:x_a + ambient_w]
        ambient_blurred = cv2.GaussianBlur(ambient_sample, (5, 5), 0)
        ambient_hsv = ambient_blurred.reshape(-1, 3).astype(np.float32)
        ambient_mean = np.mean(ambient_hsv, axis=0)  # [h, s, v]
        ambient_hue_shift = int(ambient_mean[0] - 90)   # 90 is neutral (greenish)
        ambient_val_shift = int(ambient_mean[2] - 128)  # midpoint of brightness

        cv2.rectangle(frame, (x_a, y_a), (x_a + ambient_w, y_a + ambient_h), (255, 100, 0), 1)
        cv2.putText(frame, "Ambient", (x_a - 10, y_a - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 100, 0), 1)

        # === Obstacle-Aware Smart Floor Sampling ===
        sample_w, sample_h = 300, 50
        y_start = height - sample_h - 100
        x_center = width // 2

        # Generate obstacle mask using edges
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        obstacle_mask = cv2.dilate(edges, kernel, iterations=2)

        # Try center, then slide left/right
        clean_sample_found = False
        for dx in range(0, width // 2, 10):
            for direction in [-1, 1]:
                x_start = x_center + dx * direction - sample_w // 2
                if x_start < 0 or x_start + sample_w > width:
                    continue

                roi = obstacle_mask[y_start:y_start + sample_h, x_start:x_start + sample_w]
                if np.mean(roi) < 10:
                    clean_sample_found = True
                    break
            if clean_sample_found:
                break

        if not clean_sample_found and hasattr(self, 'last_sample_x'):
            x_start = self.last_sample_x
        elif not clean_sample_found:
            x_start = width // 2 - sample_w // 2

        self.last_sample_x = x_start

        # === Final Floor HSV Sampling (with blur) ===
        sample_region = hsv[y_start:y_start + sample_h, x_start:x_start + sample_w]
        blurred_sample = cv2.GaussianBlur(sample_region, (7, 7), 0)
        sample_hsv = blurred_sample.reshape(-1, 3).astype(np.float32)
        mean = np.mean(sample_hsv, axis=0)
        std = np.std(sample_hsv, axis=0)
        h, s, v = mean
        h_std, s_std, v_std = std

        sl_H_margin = self.h_margin_slider.value()
        sl_S_margin = self.s_margin_slider.value()
        Sl_V_margin = self.v_margin_slider.value()

        # Set adaptive margins based on stddev (clipped to safe limits)
        h_margin = int(np.clip(h_std * 1.5, sl_H_margin, 50))
        s_margin = int(np.clip(s_std * 1.5, sl_S_margin, 100))
        v_margin = int(np.clip(v_std * 1.5, Sl_V_margin, 100))

        # Apply ambient corrections
        corrected_h = np.clip(h - ambient_hue_shift * 0.4, 0, 180)
        corrected_v = np.clip(v - ambient_val_shift * 0.3, 0, 255)

        # Store values for optional display
        self.auto_h_margin = h_margin
        self.auto_s_margin = s_margin
        self.auto_v_margin = v_margin

        self.ambient_debug.setText(
            f"Ambient Shift – Hue: {ambient_hue_shift:+.0f}, Value: {ambient_val_shift:+.0f}")

        # Calculate dynamic HSV bounds
        lower_floor = np.array([max(corrected_h - h_margin, 0), max(s - s_margin, 0), max(corrected_v - v_margin, 0)], dtype=np.uint8)

        upper_floor = np.array([min(corrected_h + h_margin, 180), min(s + s_margin, 255), min(corrected_v + v_margin, 255)], dtype=np.uint8)

        # === Visualize sampling box
        cv2.rectangle(frame, (x_start, y_start), (x_start + sample_w, y_start + sample_h), (255, 255, 0), 2)
        cv2.putText(frame, "Floor Sample", (x_start - 10, y_start - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Draw alert line
        line_color = (0, 0, 255) if self.alert_triggered else (200, 200, 200)
        # Shortened alert line in the center
        line_length = 800  # total width in pixels
        frame_width = frame.shape[1]
        x_start = frame_width // 2 - line_length // 2
        x_end = frame_width // 2 + line_length // 2

        line_color = (0, 0, 255) if self.alert_triggered else (200, 200, 200)

        cv2.line(frame, (x_start, self.alert_line_y), (x_end, self.alert_line_y), line_color, 2)
        cv2.putText(frame, "ALERT ZONE", (x_start, self.alert_line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, line_color, 1)
        
        # === Popup Alert if Triggered ===
        if self.alert_triggered and not getattr(self, 'alert_shown', False):
            self.alert_shown = True
            self.alert_zone_debug.setText("NOTICE: Collision Zone Entered")
        elif not self.alert_triggered:
            self.alert_shown = False
            self.alert_zone_debug.setText("SAFE")

        # Create mask using relaxed bounds
        mask = cv2.inRange(hsv, lower_floor, upper_floor)

        # Focus on bottom half
        roi = np.zeros_like(mask)
        roi[int(height / 2):, :] = 255
        floor_mask = cv2.bitwise_and(mask, roi, mask2)
        #floor_mask = cv2.bitwise_not(floor_mask1, mask2) 

        # Morphological cleanup
        kernel = np.ones((5, 5), np.uint8)

        # Add closing to fill gaps
        #floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel)
        #floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_DILATE, kernel)
        floor_mask = cv2.dilate(floor_mask, kernel, iterations=2)

        min_floor_area = 5000 # Filter small/noisy contours
                
        # Detect floor contour
        contours, _ = cv2.findContours(floor_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > min_floor_area:
                self.last_floor_contour = largest
            elif self.last_floor_contour is not None:
                largest = self.last_floor_contour
            else:
                largest = None
        else:
            if self.last_floor_contour is not None:
                largest = self.last_floor_contour
            else:
                largest = None

        if largest is not None:
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