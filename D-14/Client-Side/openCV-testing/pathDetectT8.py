import sys
import os
import cv2
import torch
import numpy as np
import threading
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer, QThread, Signal, Qt

sys.path.insert(1, '/home/halfdev/Documents/Projects/DriveCore/Depth-Anything-V2/metric_depth')
from depth_anything_v2.dpt import DepthAnythingV2

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
VIDEO_URL = "http://192.168.0.125:5000/video-feed"

# TODO: Documentation for this code
# [x] Script works as intended!! 
# [x] Do not change anything!!!!

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
    
    Args:
        h: Image height
        num_lines: Number of horizontal lines
        power: Controls the non-linearity. Higher = more compression at top
        top_fraction: Vertical start ratio (e.g. 0.4 = 40% down)
        bottom_fraction: End of grid (usually 1.0 = bottom of image)

    Returns:
        List of y-coordinates for horizontal grid lines
    """
    y0 = int(h * top_fraction)
    y1 = int(h * bottom_fraction)

    return [int(y0 + (y1 - y0) * (i / num_lines) ** power) for i in range(1, num_lines + 1)]

def draw_perspective_grid(frame, spacing=SPACING, num_lines=NUM_LINES, highlight_zones=None):
    h, w = frame.shape[:2]
    vanish_x = w // 2
    #lower_y = int(h * 2 / 3)
    grid_y = generate_perspective_y_lines(h, spacing)
    output = frame.copy()

    # Horizontal lines from bottom third only
    for y in grid_y:
        cv2.line(output, (0, y), (w, y), (0, 255, 0), 1)

    # Vertical converging lines
    step = w // num_lines
    for x in range(0, w + step, step):
        cv2.line(output, (x, h), (vanish_x, int(h / 3)), (0, 255, 0), 1)

    if highlight_zones:
        for (x1, x2, y1, y2) in highlight_zones:
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return output, vanish_x, int(h / 3)

def get_grid_lines(w, h, spacing=SPACING, num_lines=NUM_LINES):
    grid_lines_y = generate_perspective_y_lines(h, spacing)
    step = w // num_lines
    grid_lines_x = list(range(0, w + step, step))
    return grid_lines_x, grid_lines_y

def filter_alert_cells(alert_cells, min_neighbors=3, min_vertical_span=2, image_shape=(720, 1280)):
    """
    Filters raw alert cells to remove noise/anomalies based on:
    - Spatial neighbor count
    - Minimum vertical continuity
    - Optional mask-based analysis

    Parameters:
        alert_cells: list of tuples (x1, x2, y1, y2)
        min_neighbors: minimum adjacent neighbors in the 8-connected sense
        min_vertical_span: minimum number of vertically stacked cells
        image_shape: (height, width) of original image for map bounds

    Returns:
        List of filtered alert cells
    """
    h, w = image_shape
    cell_map = np.zeros((h, w), dtype=np.uint8)

    # Step 1: Draw alert regions on mask
    for (x1, x2, y1, y2) in alert_cells:
        cv2.rectangle(cell_map, (x1, y1), (x2, y2), 255, thickness=-1)

    # Step 2: Connected components (8-connected)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cell_map, connectivity=8)

    # Step 3: Keep only components that meet size and shape criteria
    filtered_cells = []
    for i in range(1, num_labels):  # label 0 is background
        x, y, w_box, h_box, area = stats[i]
        vertical_blocks = int(h_box / ((alert_cells[0][3] - alert_cells[0][2]) + 1)) if alert_cells else 1
        if vertical_blocks >= min_vertical_span and area >= min_neighbors * 50:
            # Add all matching cells that intersect with this component
            for (x1, x2, y1, y2) in alert_cells:
                if labels[(y1 + y2) // 2, (x1 + x2) // 2] == i:
                    filtered_cells.append((x1, x2, y1, y2))

    return filtered_cells

def detect_objects_by_vertical_blobs(color_map, grid_x, grid_y, hue_diff_thresh=2, min_vertical=3, slope_thresh=2):
    """
    Identify objects by finding vertical columns where hue remains constant across stacked cells.
    Floor is excluded by measuring linear hue gradient.

    Args:
    color_map:          The depth colormap image (e.g. output from cv2.applyColorMap). 
                        Used for visual similarity instead of raw depth. Usually shape (H, W, 3) in BGR.

    grid_x:             X-axis boundaries of vertical grid columns (e.g. [0, 80, 160, ...]). 
                        Created from the perspective grid. Each pair (x1, x2) defines one vertical slice.

    grid_y:             Y-axis boundaries of horizontal grid rows (from bottom 1/3 of the image). 
                        Each pair (y1, y2) defines one cell height. Combined with grid_x, it defines each cell.
                        
    hue_diff_thresh:   	The maximum allowed difference in hue between adjacent grid cells in a vertical stack. 
                        If two cells have a hue difference smaller than this, they’re considered part of the same object.

    min_vertical:       The minimum number of vertically adjacent grid cells that must have similar hues to count as an object. 
                        Prevents detecting small noise blobs.

    slope_thresh:       Controls whether the hue gradient is flat enough to count as an object (low slope = object; high slope = floor). 
                        A low standard deviation in hue deltas means the hue is steady, and accept it.

    """
    hsv_map = cv2.cvtColor(color_map, cv2.COLOR_BGR2HSV)
    alert_cells = []

    for j in range(len(grid_x) - 1):
        x1, x2 = grid_x[j], grid_x[j + 1]
        vertical_hues = []

        for i in range(len(grid_y) - 1):
            y1, y2 = grid_y[i], grid_y[i + 1]
            cell = hsv_map[y1:y2, x1:x2]
            mean_hue = np.mean(cell[:, :, 0])
            vertical_hues.append((i, mean_hue))

        # Measure hue differences across the column
        run = []
        for i in range(len(vertical_hues) - 1):
            idx1, h1 = vertical_hues[i]
            idx2, h2 = vertical_hues[i + 1]
            delta = abs(h2 - h1)

            if delta < hue_diff_thresh:
                run.append(idx1)
                if i + 1 == len(vertical_hues) - 1:
                    run.append(idx2)
            else:
                if len(run) >= min_vertical:
                    # Calculate total gradient across run
                    hues = [vertical_hues[k][1] for k in run]
                    if np.std(np.diff(hues)) < slope_thresh:
                        for k in run:
                            y1, y2 = grid_y[k], grid_y[k + 1]
                            alert_cells.append((x1, x2, y1, y2))
                run = []

        # Catch leftover run
        if len(run) >= min_vertical:
            hues = [vertical_hues[k][1] for k in run]
            if np.std(np.diff(hues)) < slope_thresh:
                for k in run:
                    y1, y2 = grid_y[k], grid_y[k + 1]
                    alert_cells.append((x1, x2, y1, y2))
    
    # Filter the Cells to avoid false positives
    filtered_cells = filter_alert_cells(alert_cells)

    return filtered_cells
    #return alert_cells

def filter_alert_cells(alert_cells, min_neighbors=6, min_vertical_span=2, image_shape=(720, 1280)):
    """
    Filters raw alert cells to remove noise/anomalies based on:
    - Spatial neighbor count
    - Minimum vertical continuity
    - Optional mask-based analysis

    Parameters:
        alert_cells: list of tuples (x1, x2, y1, y2)
        min_neighbors: minimum adjacent neighbors in the 8-connected sense
        min_vertical_span: minimum number of vertically stacked cells
        image_shape: (height, width) of original image for map bounds

    Returns:
        List of filtered alert cells
    """
    h, w = image_shape
    cell_map = np.zeros((h, w), dtype=np.uint8)

    # Step 1: Draw alert regions on mask
    for (x1, x2, y1, y2) in alert_cells:
        cv2.rectangle(cell_map, (x1, y1), (x2, y2), 255, thickness=-1)

    # Step 2: Connected components (8-connected)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cell_map, connectivity=8)

    # Step 3: Keep only components that meet size and shape criteria
    filtered_cells = []
    for i in range(1, num_labels):  # label 0 is background
        x, y, w_box, h_box, area = stats[i]
        vertical_blocks = int(h_box / ((alert_cells[0][3] - alert_cells[0][2]) + 1)) if alert_cells else 1
        if vertical_blocks >= min_vertical_span and area >= min_neighbors * 50:
            # Add all matching cells that intersect with this component
            for (x1, x2, y1, y2) in alert_cells:
                if labels[(y1 + y2) // 2, (x1 + x2) // 2] == i:
                    filtered_cells.append((x1, x2, y1, y2))

    return filtered_cells

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

    def run(self):
        while self.running:
            if self.frame is not None:
                frame = self.frame
                self.frame = None
                depth_map, vis = self.infer_depth_map(frame)
                self.depth_ready.emit(depth_map, vis)

    def submit_frame(self, frame):
        if self.frame is None:
            self.frame = frame

    def infer_depth_map(self, frame_bgr, size=210):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(frame_rgb, (size, size), interpolation=cv2.INTER_AREA)
        img = resized.astype(np.float32) / 255.0
        img = (img - 0.4) / 0.4 # <--- Change
        tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0).to(self.device).float()

        with torch.no_grad():
            depth = self.model(tensor).squeeze().cpu().numpy()

        depth_resized = cv2.resize(depth, (frame_bgr.shape[1], frame_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
        vis = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        '''depth_clipped = np.clip(depth_resized, 0.1, 0.5)  # [min_depth, max_depth]
        vis = ((depth_clipped - 0.1) / (0.5 - 0.1) * 255.0).astype(np.uint8)'''
        vis_color = cv2.applyColorMap(vis, cv2.COLORMAP_TURBO) #MAGMA, TURBO, 
        return depth_resized, vis_color

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
        print("exit")
        self.running = False
        self.cap.release()
        self.thread.join()
        

class DepthGridViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("DriveCore – Grid + Depth Blob Detection")
        self.setFixedSize(1280, 720)

        self.video_label = QLabel("Loading...")
        self.video_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        self.setLayout(layout)

        self.stream = MJPEGStreamReader(stream_url)
        '''if not self.stream.isOpened():
            raise RuntimeError("Failed to open video stream")'''

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
        self.depth_worker.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

        self.depth_result = None
        self.depth_vis = None
        self.frame_skip = 2
        self.frame_count = 0

    def update_frame(self):
        frame = self.stream.read()
        if frame is None:
            return
        
        '''ret, frame = self.stream.read()
        if not ret:
            return'''

        frame = cv2.resize(frame, (1280, 720))
        self.frame_count += 1
        if self.frame_count % self.frame_skip == 0:
            self.depth_worker.submit_frame(frame)

        if self.depth_vis is not None:
            grid_x, grid_y = get_grid_lines(frame.shape[1], frame.shape[0])
            alert_cells = detect_objects_by_vertical_blobs(self.depth_vis, grid_x, grid_y)
            blend = overlay_depth_blend(frame, self.depth_vis)
            frame, _, _ = draw_perspective_grid(blend, highlight_zones=alert_cells)

        self.video_label.setPixmap(QPixmap.fromImage(convert_to_qimage(frame)))

    def on_depth_ready(self, depth_map, vis_img):
        self.depth_result = depth_map
        self.depth_vis = vis_img

    def closeEvent(self, event):
        '''if self.stream.isOpened():
            self.stream.release()'''
        self.stream.stop()
        self.depth_worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DepthGridViewer(VIDEO_URL)
    viewer.show()
    sys.exit(app.exec())