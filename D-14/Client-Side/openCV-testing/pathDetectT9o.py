import sys
import os
import cv2
import torch
import numpy as np
import threading
import time
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer, QThread, Signal, Qt

sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/Depth-Anything-V2/metric_depth')
from depth_anything_v2.dpt import DepthAnythingV2

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
VIDEO_URL = "http://192.168.0.125:5000/video-feed"

#=== Grid Spacing Variables ===
SPACING = 12
NUM_LINES = 40

def convert_to_qimage(cv_img):
    h, w, ch = cv_img.shape
    return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()

def generate_perspective_y_lines(h, num_lines=12, power=1.8, top_fraction=5/8, bottom_fraction=0.9):
    """
    Generates y positions for horizontal lines where:
    - Top of image: dense lines (far)
    - Bottom: sparse lines (close/floor)
    """
    y0 = int(h * top_fraction)
    y1 = int(h * bottom_fraction)
    return [int(y0 + (y1 - y0) * (i / num_lines) ** power) for i in range(1, num_lines + 1)]

def draw_perspective_grid_optimized(frame, spacing=SPACING, num_lines=NUM_LINES, highlight_zones=None, draw_full_grid=True):
    """Optimized grid drawing with optional full grid rendering"""
    h, w = frame.shape[:2]
    vanish_x = w // 2
    vanish_y = int(h / 3)
    output = frame.copy()

    if draw_full_grid:
        grid_y = generate_perspective_y_lines(h, spacing)
        
        # Horizontal lines - vectorized (optimization)
        for y in grid_y:
            cv2.line(output, (0, y), (w, y), (0, 255, 0), 1)

        # Vertical converging lines
        step = w // num_lines
        for x in range(0, w + step, step):
            cv2.line(output, (x, h), (vanish_x, vanish_y), (0, 255, 0), 1)

    # Draw highlighted cells efficiently
    if highlight_zones:
        # Group rectangles by color for batch drawing
        for (x1, x2, y1, y2) in highlight_zones:
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return output, vanish_x, vanish_y

def get_grid_lines(w, h, spacing=SPACING, num_lines=NUM_LINES):
    grid_lines_y = generate_perspective_y_lines(h, spacing)
    step = w // num_lines
    grid_lines_x = list(range(0, w + step, step))
    return grid_lines_x, grid_lines_y

def detect_objects_by_vertical_blobs_accurate(color_map, grid_x, grid_y, hue_diff_thresh=2, min_vertical=3, slope_thresh=2):
    """
    Optimized version improving performance through:
    1. Memory management
    2. Reduced redundant calculations
    3. Preserved original algorithm
    """
    # Single conversion and blur operation
    hsv_map = cv2.cvtColor(color_map, cv2.COLOR_BGR2HSV)
    hsv_blurred = cv2.GaussianBlur(hsv_map, (5, 5), 0)
    
    alert_cells = []
    
    # Pre-allocate arrays to reduce memory allocation overhead
    max_cells = len(grid_y) - 1
    vertical_hues = [(0, 0.0)] * max_cells  # Pre-allocate list
    
    for j in range(len(grid_x) - 1):
        x1, x2 = grid_x[j], grid_x[j + 1]
        
        # Reset and fill the pre-allocated list
        actual_count = 0
        for i in range(len(grid_y) - 1):
            y1, y2 = grid_y[i], grid_y[i + 1]
            
            # Bounds checking
            if y1 >= hsv_blurred.shape[0] or y2 >= hsv_blurred.shape[0] or x1 >= hsv_blurred.shape[1] or x2 >= hsv_blurred.shape[1]:
                continue
                
            cell = hsv_blurred[y1:y2, x1:x2]
            if cell.size == 0:
                continue
                
            mean_hue = np.mean(cell[:, :, 0])
            vertical_hues[actual_count] = (i, mean_hue)
            actual_count += 1
        
        # Process only the actual data
        if actual_count < 2:
            continue
            
        # Original algorithm preserved
        run = []
        for idx in range(actual_count - 1):
            i1, h1 = vertical_hues[idx]
            i2, h2 = vertical_hues[idx + 1]
            delta = abs(h2 - h1)

            if delta < hue_diff_thresh:
                run.append(i1)
                if idx + 1 == actual_count - 1:  # Last iteration
                    run.append(i2)
            else:
                if len(run) >= min_vertical:
                    # Calculate total gradient across run
                    hues = [vertical_hues[k][1] for k in range(len(vertical_hues)) if vertical_hues[k][0] in run]
                    if len(hues) > 1 and np.std(np.diff(hues)) < slope_thresh:
                        for k in run:
                            if k < len(grid_y) - 1:
                                y1, y2 = grid_y[k], grid_y[k + 1]
                                alert_cells.append((x1, x2, y1, y2))
                run = []

        # Handle final run
        if len(run) >= min_vertical:
            hues = [vertical_hues[k][1] for k in range(len(vertical_hues)) if vertical_hues[k][0] in run]
            if len(hues) > 1 and np.std(np.diff(hues)) < slope_thresh:
                for k in run:
                    if k < len(grid_y) - 1:
                        y1, y2 = grid_y[k], grid_y[k + 1]
                        alert_cells.append((x1, x2, y1, y2))
    
    # Apply filtering with preserved accuracy
    filtered_cells = filter_alert_cells_optimized(alert_cells, image_shape=color_map.shape[:2])
    return filtered_cells

def filter_alert_cells_optimized(alert_cells, min_neighbors=6, min_vertical_span=2, image_shape=(720, 1280)):
    """
    Optimized filtering maintaining original accuracy while improving performance
    """
    if not alert_cells:
        return []
    
    h, w = image_shape
    cell_map = np.zeros((h, w), dtype=np.uint8)

    # Batch rectangle drawing with bounds checking
    for (x1, x2, y1, y2) in alert_cells:
        # Clamp coordinates to image bounds
        x1_c, x2_c = max(0, min(x1, w)), max(0, min(x2, w))
        y1_c, y2_c = max(0, min(y1, h)), max(0, min(y2, h))
        
        if x1_c < x2_c and y1_c < y2_c:
            cell_map[y1_c:y2_c, x1_c:x2_c] = 255

    # Connected components analysis
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cell_map, connectivity=8)

    if num_labels <= 1:
        return []

    # Calculate average cell height for scaling
    if alert_cells:
        avg_cell_height = np.mean([y2 - y1 for _, _, y1, y2 in alert_cells])
    else:
        avg_cell_height = 1

    filtered_cells = []
    
    # Create lookup for valid labels first (optimization)
    valid_labels = set()
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        vertical_blocks = max(1, int(h_box / avg_cell_height))
        
        if vertical_blocks >= min_vertical_span and area >= min_neighbors * 50:
            valid_labels.add(i)

    # Only process cells that belong to valid components
    if valid_labels:
        for (x1, x2, y1, y2) in alert_cells:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # Bounds check for label lookup
            if 0 <= cy < h and 0 <= cx < w and labels[cy, cx] in valid_labels:
                filtered_cells.append((x1, x2, y1, y2))

    return filtered_cells

def classify_clusters(clusters, depth_map, image_shape):
    """Original classification"""
    classified = []
    h, w = image_shape

    for (x1, y1, x2, y2) in clusters:
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = width / max(height, 1)
        
        # Bounds checking
        x1_c, x2_c = max(0, min(x1, w)), max(0, min(x2, w))
        y1_c, y2_c = max(0, min(y1, h)), max(0, min(y2, h))
        
        if x1_c < x2_c and y1_c < y2_c:
            region = depth_map[y1_c:y2_c, x1_c:x2_c]
            avg_depth = np.mean(region) if region.size > 0 else 1.0
        else:
            avg_depth = 1.0

        if aspect_ratio > 3 or x1 <= 5 or x2 >= w - 5:
            label = "wall"
        elif avg_depth < 0.05:
            label = "dip"
        else:
            label = "obstacle"

        classified.append((x1, y1, x2, y2, label))
    return classified

def overlay_depth_blend(rgb, depth_vis, alpha=0.5):
    return cv2.addWeighted(rgb, 1 - alpha, depth_vis, alpha, 0)

class DepthWorker(QThread):
    depth_ready = Signal(np.ndarray, np.ndarray)

    def __init__(self, model, device):
        super().__init__()
        self.model = model
        self.device = device
        self.running = True
        self.frame = None
        self.processing = False

    def run(self):
        while self.running:
            if self.frame is not None and not self.processing:
                frame = self.frame
                self.frame = None
                self.processing = True
                try:
                    depth_map, vis = self.infer_depth_map(frame)
                    self.depth_ready.emit(depth_map, vis)
                finally:
                    self.processing = False
            else:
                self.msleep(1)  # Small sleep to prevent busy waiting

    def submit_frame(self, frame):
        if not self.processing:
            self.frame = frame

    def infer_depth_map(self, frame_bgr, size=210):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(frame_rgb, (size, size), interpolation=cv2.INTER_AREA)
        img = resized.astype(np.float32) / 255.0
        img = (img - 0.4) / 0.4
        tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0).to(self.device).float()

        with torch.no_grad():
            depth = self.model(tensor).squeeze().cpu().numpy()

        depth_resized = cv2.resize(depth, (frame_bgr.shape[1], frame_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
        vis = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        vis_color = cv2.applyColorMap(vis, cv2.COLORMAP_TURBO)
        return depth_resized, vis_color

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class MJPEGStreamReaderThread(QThread):
    frame_received = Signal(np.ndarray)
    fps_updated = Signal(float)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.cap = None
        self.running = False
        self.last_time = time.time()
        self.frame_count = 0

    def run(self):
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            print(f"Failed to open stream: {self.url}")
            return

        # Buffer optimization
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.running = True
        self.frame_count = 0
        self.last_time = time.time()

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_received.emit(frame)
                self.frame_count += 1

                # Calculate FPS every second
                now = time.time()
                if now - self.last_time >= 1.0:
                    fps = self.frame_count / (now - self.last_time)
                    self.fps_updated.emit(fps)
                    self.frame_count = 0
                    self.last_time = now
            else:
                self.msleep(1)

        self.cap.release()

    def stop(self):
        print("Stopping MJPEG stream thread...")
        self.running = False
        self.wait()

class DepthGridViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("DriveCore - Grid + Depth Blob Classification (Accurate + Optimized)")
        self.setFixedSize(1280, 720)

        self.video_label = QLabel("Loading...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.stream_fps_label = QLabel("FPS: ...")
        self.stream_fps_label.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.stream_fps_label)
        self.setLayout(layout)

        self.stream_thread = MJPEGStreamReaderThread(VIDEO_URL)
        self.stream_thread.frame_received.connect(self.on_new_frame)
        self.stream_thread.start()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = DepthAnythingV2(
            encoder="vits",
            features=64,
            out_channels=[48, 96, 192, 384],
            max_depth=1
        )
        ckpt = torch.load("Depth-Anything-V2/checkpoints/depth_anything_v2_metric_hypersim_vits.pth", map_location=self.device)
        model.load_state_dict(ckpt, strict=True)
        model.eval().to(self.device)

        self.depth_worker = DepthWorker(model, self.device)
        self.depth_worker.depth_ready.connect(self.on_depth_ready)
        self.stream_thread.fps_updated.connect(self.on_stream_fps)
        self.depth_worker.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # ~60 FPS

        self.depth_result = None
        self.depth_vis = None
        self.frame_skip = 2  # Balanced for accuracy vs performance
        self.frame_count = 0
        
        # Cache for grid lines
        self.grid_cache = None
        self.grid_cache_size = None
        
        # Performance monitoring
        self.show_grid = True  # Toggle for performance testing

    def on_new_frame(self, frame):
        self.latest_frame = frame.copy()

    def update_frame(self):
        frame = getattr(self, 'latest_frame', None)
        if frame is None:
            return

        frame = cv2.resize(frame, (1280, 720))
        self.frame_count += 1
        
        if self.frame_count % self.frame_skip == 0:
            self.depth_worker.submit_frame(frame)

        if self.depth_result is not None:
            # Use cached grid lines
            current_size = (frame.shape[1], frame.shape[0])
            if self.grid_cache is None or self.grid_cache_size != current_size:
                self.grid_cache = get_grid_lines(frame.shape[1], frame.shape[0])
                self.grid_cache_size = current_size
            
            grid_x, grid_y = self.grid_cache
            
            # Use accurate detection algorithm
            alert_cells = detect_objects_by_vertical_blobs_accurate(
                self.depth_vis, grid_x, grid_y)

            # Create mask for clustering (keep original approach for accuracy)
            mask = np.zeros((720, 1280), dtype=np.uint8)
            for (x1, x2, y1, y2) in alert_cells:
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)
            
            # Cluster connected blobs
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            clusters = [cv2.boundingRect(cnt) for cnt in contours if cv2.contourArea(cnt) >= 150]
            clusters = [(x, y, x + w, y + h) for (x, y, w, h) in clusters]

            # Classify clusters
            classified = classify_clusters(clusters, self.depth_result, frame.shape[:2])

            # Draw results
            blend = overlay_depth_blend(frame, self.depth_vis)

            # Draw perspective grid with highlighted cells
            blend, vanish_x, vanish_y = draw_perspective_grid_optimized(
                blend, highlight_zones=alert_cells, draw_full_grid=self.show_grid)
            
            # Draw individual alert cells (for pathfinding)
            for (x1, x2, y1, y2) in alert_cells:
                cv2.rectangle(blend, (x1, y1), (x2, y2), (200, 200, 50), 1)  # light yellow cells

            # Draw classification results
            for (x1, y1, x2, y2, label) in classified:
                region = self.depth_result[y1:y2, x1:x2]
                avg_depth = np.mean(region) if region.size > 0 else 0
                color = {"obstacle": (255, 0, 255), "wall": (0, 255, 255), "dip": (0, 100, 255)}[label]
                cv2.rectangle(blend, (x1, y1), (x2, y2), color, 2)
                cv2.putText(blend, f"{label} ({avg_depth:.2f}m)", (x1, y2 + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

            output = blend
        else:
            output = frame

        # Display
        qimage = convert_to_qimage(output)
        self.video_label.setPixmap(QPixmap.fromImage(qimage))

    def on_depth_ready(self, depth_map, vis_img):
        self.depth_result = depth_map
        self.depth_vis = vis_img

    def on_stream_fps(self, fps):
        self.stream_fps_label.setText(f"Stream FPS: {fps:.1f}")

    def closeEvent(self, event):
        self.stream_thread.stop()
        self.depth_worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DepthGridViewer(VIDEO_URL)
    viewer.show()
    sys.exit(app.exec())