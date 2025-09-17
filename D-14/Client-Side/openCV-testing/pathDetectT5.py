import sys
import cv2
import torch
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import QTimer

import os
'''
Using MiDaS depth estimation within raspberry pi hardware constraints
RESULTS: Fuzzy and laggy video stream. Hard to tell what is a floor
'''
os.environ["QT_QPA_PLATFORM"] = "xcb" # For my Arch Linux environment

sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/MiDaS/')

# MiDaS setup
from midas.dpt_depth import DPTDepthModel
from midas.midas_net_custom import MidasNet_small
from midas.transforms import Resize, NormalizeImage, PrepareForNet
from torchvision.transforms import Compose

# --- Load MiDaS model ---
model_path = "/home/halfdev/Documents/Projects/DriveCore/MiDaS/weights/midas_v21_small_256.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#model = DPTDepthModel(path=model_path, backbone="vitl16_384", non_negative=True)
model = MidasNet_small(model_path, features=64, non_negative=True).to(device)
model.eval().to(device)


transform = Compose([
    Resize(
        width=256,
        height=256,
        resize_target=None,
        keep_aspect_ratio=False,
        ensure_multiple_of=32,
        resize_method="minimal"
    ),
    NormalizeImage(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
    PrepareForNet()
])


# --- Helper functions ---
def convert_cv_to_qt(cv_img):
    """Convert BGR or RGB OpenCV image to QImage."""
    h, w, ch = cv_img.shape
    return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()

def infer_depth(frame):
    """Run MiDaS depth inference on a single RGB frame."""
    input_small = cv2.resize(frame, (256, 192), interpolation=cv2.INTER_AREA)  # ↓↓↓ downscale frame before MiDaS
    input_data = transform({"image": input_small})["image"]
    input_tensor = torch.from_numpy(input_data).unsqueeze(0).to(device)
    with torch.no_grad():
        prediction = model.forward(input_tensor)
        depth_map = prediction.squeeze().cpu().numpy()
        depth_map = cv2.resize(depth_map, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)
        depth_vis = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        depth_vis = cv2.equalizeHist(depth_vis)
        depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_MAGMA)
        return depth_colored

# --- PySide6 GUI ---
class MidasViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("MiDaS Webstream Depth Viewer (Fast Mode)")
        self.video_label = QLabel("Loading video...")
        self.depth_label = QLabel("Loading depth map...")

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.depth_label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(stream_url)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.frame_count = 0
        self.frame_skip = 3  # Only run depth on every 3rd frame
        self.last_depth = None

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.frame_count += 1
        if self.frame_count % self.frame_skip == 0:
            self.last_depth = infer_depth(frame_rgb)

        self.video_label.setPixmap(QPixmap.fromImage(convert_cv_to_qt(frame_rgb).rgbSwapped()))
        if self.last_depth is not None:
            self.depth_label.setPixmap(QPixmap.fromImage(convert_cv_to_qt(self.last_depth)))

# --- Run the application ---
if __name__ == "__main__":
    stream_url = "http://192.168.0.125:5000/video-feed" #! USE BACKUP FLASK STREAM FOR TESTING
    app = QApplication(sys.argv)
    viewer = MidasViewer(stream_url)
    viewer.resize(600, 400)
    viewer.show()
    sys.exit(app.exec())