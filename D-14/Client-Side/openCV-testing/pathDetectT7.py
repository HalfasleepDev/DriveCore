import sys
import cv2
import torch
import numpy as np
import threading
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, QThread, Signal

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"  # For Arch Linux
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from torchvision import transforms as T

# Depth model
sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/Depth-Anything-V2/metric_depth')
from depth_anything_v2.dpt import DepthAnythingV2

# === Inference Model Setup ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DepthAnythingV2(
    encoder="vits",
    features=64,
    out_channels=[48, 96, 192, 384],
    max_depth=1
)
ckpt = torch.load("Depth-Anything-V2/checkpoints/depth_anything_v2_metric_hypersim_vits.pth", map_location=device)
model.load_state_dict(ckpt, strict=True)
model.eval().to(device)
print(torch.cuda.get_device_name(0))

# === Depth Inference Function ===
def infer_depth_and_raw(frame_bgr, model, size=210):
    """Run depth model on input frame and return raw + visualized maps"""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(frame_rgb, (size, size), interpolation=cv2.INTER_AREA)
    img = resized.astype(np.float32) / 255.0
    img = (img - 0.5) / 0.5
    tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0).to(device).float()

    with torch.no_grad():
        depth = model(tensor).squeeze().cpu().numpy()  # raw depth

    # Resize back to original frame size
    depth_resized = cv2.resize(depth, (frame_bgr.shape[1], frame_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)

    # Normalize for visualization
    depth_vis = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    depth_colormap = cv2.applyColorMap(depth_vis, cv2.COLORMAP_INFERNO) #cv2.COLORMAP_MAGMA

    return depth_resized, depth_colormap

# === MJPEG Video Stream ===
class MJPEGStreamReader:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        self.cap.release()

# === Depth Worker ===
class DepthWorker(QThread):
    depth_ready = Signal(np.ndarray, np.ndarray)  # raw_depth, heatmap

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.running = True
        self.frame = None

    def run(self):
        while self.running:
            if self.frame is not None:
                raw_depth, depth_vis = infer_depth_and_raw(self.frame, self.model)
                self.depth_ready.emit(raw_depth, depth_vis)
                self.frame = None

    def submit_frame(self, frame):
        if self.frame is None:
            self.frame = frame

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

# === Convert OpenCV frame to Qt image ===
def convert_to_qimage(cv_img):
    h, w, ch = cv_img.shape
    return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()

# === Main UI Widget ===
class DepthViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("Depth + Occupancy Map Viewer")

        self.video_label = QLabel("Video")
        self.depth_label = QLabel("Depth")
        self.map_label = QLabel("Occupancy Map")

        layout = QHBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.depth_label)
        layout.addWidget(self.map_label)
        self.setLayout(layout)

        # MJPEG stream from Pi
        self.stream = MJPEGStreamReader(stream_url)

        # Depth inference thread
        self.depth_worker = DepthWorker(model)
        self.depth_worker.depth_ready.connect(self.update_depth)
        self.depth_worker.start()

        # Refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 FPS UI refresh

        self.frame_count = 0
        self.frame_skip = 4

    def update_frame(self):
        frame = self.stream.read()
        if frame is None:
            return

        self.frame_count += 1
        if self.frame_count % self.frame_skip == 0:
            self.depth_worker.submit_frame(frame)

        self.video_label.setPixmap(QPixmap.fromImage(convert_to_qimage(frame)))

    def update_depth(self, raw_depth, depth_vis):
        """Triggered when depth model is finished"""
        self.depth_label.setPixmap(QPixmap.fromImage(convert_to_qimage(depth_vis)))
        grid_img = self.generate_occupancy_map(raw_depth)
        self.map_label.setPixmap(QPixmap.fromImage(convert_to_qimage(grid_img)))

    def generate_occupancy_map(self, depth_map):
        """Process depth map into 2D grid map showing free vs. obstacle zones"""
        h, w = depth_map.shape
        roi = depth_map[h//2:, :]  # Use bottom half

        # Compute gradient (floor is smooth, obstacles are sharp)
        sobel = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=5)
        grad_mag = np.abs(sobel)

        # Threshold gradient to extract obstacles
        _, binary = cv2.threshold(grad_mag, 0.1, 1.0, cv2.THRESH_BINARY)

        # Resize to 40x40 occupancy grid
        grid = cv2.resize(binary, (40, 40), interpolation=cv2.INTER_AREA)
        grid = (grid > 0.2).astype(np.uint8) * 255  # Binary mask

        # Visualize grid as image (white = obstacle, black = floor)
        vis = cv2.cvtColor(grid, cv2.COLOR_GRAY2BGR)
        return cv2.resize(vis, (200, 200), interpolation=cv2.INTER_NEAREST)

    def closeEvent(self, event):
        self.stream.stop()
        self.depth_worker.stop()
        event.accept()

# === Launch UI ===
if __name__ == "__main__":
    stream_url = "http://192.168.0.125:5000/video-feed"
    app = QApplication(sys.argv)
    viewer = DepthViewer(stream_url)
    viewer.resize(1024, 480)
    viewer.show()
    sys.exit(app.exec())
