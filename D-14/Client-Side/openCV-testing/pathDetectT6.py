import sys
import cv2
import torch
import numpy as np
import threading
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, QThread, Signal

import os
os.environ["QT_QPA_PLATFORM"] = "xcb" # For my Arch Linux environment
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# Torchvision transforms
from torchvision import transforms as T

# Add metric_depth to path
#sys.path.append("Depth-Anything-V2/metric_depth")
sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/Depth-Anything-V2/metric_depth')

from depth_anything_v2.dpt import DepthAnythingV2

class DepthWorker(QThread):
    depth_ready = Signal(np.ndarray)  # Emits processed depth image

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.running = True
        self.frame = None

    def run(self):
        while self.running:
            if self.frame is not None:
                depth_img = infer_depth_metric(self.frame, self.model)
                self.depth_ready.emit(depth_img)
                self.frame = None  # wait for next frame

    def submit_frame(self, frame):
        if self.frame is None:  # avoid queueing multiple frames
            self.frame = frame

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

# === Threaded MJPEG Reader ===
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

# --- Model Setup ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pretrained model (ViT-Small)
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

# === Inference ===
def infer_depth_metric(frame_bgr, model, size=210):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(frame_rgb, (size, size), interpolation=cv2.INTER_AREA)
    img = resized.astype(np.float32) / 255.0
    img = (img - 0.5) / 0.5
    tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0).to(device).float()

    with torch.no_grad():
        depth = model(tensor).squeeze().cpu().numpy()

    depth_resized = cv2.resize(depth, (frame_bgr.shape[1], frame_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
    depth_vis = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.applyColorMap(depth_vis, cv2.COLORMAP_MAGMA)


# --- Convert cv2 image to QImage ---
def convert_to_qimage(cv_img):
    h, w, ch = cv_img.shape
    return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()

# --- PySide6 GUI ---
class DepthViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("Depth Anything V2 - Metric Depth Viewer")

        self.video_label = QLabel("Loading Video...")
        self.depth_label = QLabel("Loading Depth...")

        layout = QHBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.depth_label)
        self.setLayout(layout)

        self.stream = MJPEGStreamReader(stream_url)

        # Launch depth estimation thread
        self.depth_worker = DepthWorker(model)
        self.depth_worker.depth_ready.connect(self.update_depth)
        self.depth_worker.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS GUI refresh

        self.last_depth = None
        self.frame_count = 0
        self.frame_skip = 5  # Inference only every 4 frames

    def update_frame(self):
        frame = self.stream.read()
        if frame is None:
            return

        self.frame_count += 1
        if self.frame_count % self.frame_skip == 0:
            self.depth_worker.submit_frame(frame)

        self.video_label.setPixmap(QPixmap.fromImage(convert_to_qimage(frame)))
    
    def update_depth(self, depth_img):
        self.depth_label.setPixmap(QPixmap.fromImage(convert_to_qimage(depth_img)))

    def closeEvent(self, event):
        self.stream.stop()
        self.depth_worker.stop()
        event.accept()

# --- Main Execution ---
if __name__ == "__main__":
    stream_url = "http://192.168.0.125:5000/video-feed" #! USE BACKUP FLASK STREAM FOR TESTING
    app = QApplication(sys.argv)
    viewer = DepthViewer(stream_url)
    viewer.resize(800, 600)
    viewer.show()
    sys.exit(app.exec())
