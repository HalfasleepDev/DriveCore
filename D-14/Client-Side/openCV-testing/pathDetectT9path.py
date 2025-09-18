import sys
import os
import cv2
import torch
import numpy as np
import threading
import time
from collections import deque
import math
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

# Pathfinding configuration
class PathConfig:
    VEHICLE_WIDTH = 12  # Vehicle width in grid cells (3)
    LOOKAHEAD_DISTANCE = 10  # How far ahead to plan (8)
    SMOOTHING_FACTOR = 0.3  # Path smoothing strength (0.3)
    SAFETY_MARGIN = 1  # Additional safety margin around obstacles
    TARGET_HORIZON = 0.6  # Target point as fraction of image height from bottom

def convert_to_qimage(cv_img):
    h, w, ch = cv_img.shape
    return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888).rgbSwapped()

def generate_perspective_y_lines(h, num_lines=12, power=1.8, top_fraction=5/8, bottom_fraction=0.9):
    y0 = int(h * top_fraction)
    y1 = int(h * bottom_fraction)
    return [int(y0 + (y1 - y0) * (i / num_lines) ** power) for i in range(1, num_lines + 1)]

def get_grid_lines(w, h, spacing=SPACING, num_lines=NUM_LINES):
    grid_lines_y = generate_perspective_y_lines(h, spacing)
    step = w // num_lines
    grid_lines_x = list(range(0, w + step, step))
    return grid_lines_x, grid_lines_y

def create_occupancy_grid(alert_cells, grid_x, grid_y, image_shape):
    """
    Create a 2D occupancy grid from detected obstacle cells
    Returns: 2D numpy array where 1 = obstacle, 0 = free space
    """
    grid_height = len(grid_y) - 1
    grid_width = len(grid_x) - 1
    
    occupancy = np.zeros((grid_height, grid_width), dtype=np.uint8)
    
    # Mark obstacle cells
    for (x1, x2, y1, y2) in alert_cells:
        # Find grid indices
        grid_col = -1
        grid_row = -1
        
        # Find column
        for i in range(len(grid_x) - 1):
            if grid_x[i] <= x1 < grid_x[i + 1]:
                grid_col = i
                break
        
        # Find row
        for i in range(len(grid_y) - 1):
            if grid_y[i] <= y1 < grid_y[i + 1]:
                grid_row = i
                break
        
        if 0 <= grid_row < grid_height and 0 <= grid_col < grid_width:
            occupancy[grid_row, grid_col] = 1
    
    return occupancy

def expand_obstacles(occupancy_grid, safety_margin=1):
    """Expand obstacles by safety margin"""
    if safety_margin <= 0:
        return occupancy_grid
    
    kernel = np.ones((2*safety_margin + 1, 2*safety_margin + 1), np.uint8)
    expanded = cv2.dilate(occupancy_grid, kernel, iterations=1)
    return expanded

def calculate_openness_map(occupancy_grid, window_size=5):
    """
    Calculate openness score for each cell based on surrounding free space
    Higher values = more open space
    """
    h, w = occupancy_grid.shape
    openness = np.zeros((h, w), dtype=np.float32)
    
    half_window = window_size // 2
    
    for r in range(h):
        for c in range(w):
            if occupancy_grid[r, c] == 1:  # Obstacle cell
                openness[r, c] = 0
                continue
            
            # Calculate free space in surrounding window
            r_min = max(0, r - half_window)
            r_max = min(h, r + half_window + 1)
            c_min = max(0, c - half_window)
            c_max = min(w, c + half_window + 1)
            
            window = occupancy_grid[r_min:r_max, c_min:c_max]
            free_cells = np.sum(window == 0)
            total_cells = window.size
            
            openness[r, c] = free_cells / total_cells
    
    return openness

def find_best_path_potential_field(occupancy_grid, start_col, target_row, vehicle_width=3):
    """
    Use potential field method to find path toward most open space
    """
    h, w = occupancy_grid.shape
    
    # Create potential field
    potential = np.ones((h, w), dtype=np.float32) * 1000  # High potential = bad
    
    # Set goal attraction (lower potential toward target)
    for c in range(w):
        for r in range(h):
            if occupancy_grid[r, c] == 0:  # Free space
                # Distance to target row
                target_distance = abs(r - target_row)
                # Prefer center columns slightly
                center_distance = abs(c - w//2) * 0.1
                potential[r, c] = target_distance + center_distance
    
    # Add obstacle repulsion
    obstacle_potential = expand_obstacles(occupancy_grid, safety_margin=2).astype(np.float32) * 1000
    potential += obstacle_potential
    
    # Calculate openness and subtract to prefer open areas
    openness = calculate_openness_map(occupancy_grid, window_size=5)
    potential -= openness * 50  # Bias toward open areas
    
    # Generate path using gradient descent
    path = []
    current_row = h - 1  # Start from bottom
    current_col = start_col
    
    for step in range(h):
        if current_row <= target_row:
            break
            
        path.append((current_row, current_col))
        
        # Find next step with lowest potential
        best_potential = float('inf')
        best_row, best_col = current_row, current_col
        
        # Check surrounding cells (prioritize forward movement)
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1)]  # Prioritize forward
        for dr, dc in moves:
            new_row = current_row + dr
            new_col = current_col + dc
            
            if (0 <= new_row < h and 0 <= new_col < w and 
                new_col >= vehicle_width//2 and new_col < w - vehicle_width//2):
                
                # Check if vehicle width can fit
                can_fit = True
                for offset in range(-vehicle_width//2, vehicle_width//2 + 1):
                    check_col = new_col + offset
                    if (check_col < 0 or check_col >= w or 
                        occupancy_grid[new_row, check_col] == 1):
                        can_fit = False
                        break
                
                if can_fit and potential[new_row, new_col] < best_potential:
                    best_potential = potential[new_row, new_col]
                    best_row, best_col = new_row, new_col
        
        current_row, current_col = best_row, best_col
        
        # Avoid infinite loops
        if len(path) > 1 and (current_row, current_col) == path[-2]:
            break
    
    return path, potential, openness

def find_best_path_astar(occupancy_grid, start_col, target_row, vehicle_width=3):
    """
    A* pathfinding toward most open space
    """
    h, w = occupancy_grid.shape
    start = (h - 1, start_col)  # Bottom of grid
    
    # Define heuristic function first
    def heuristic(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(pos):
        r, c = pos
        neighbors = []
        # Prioritize forward and diagonal-forward movement
        moves = [(-1, 0), (-1, -1), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in moves:
            new_r, new_c = r + dr, c + dc
            
            if (0 <= new_r < h and 0 <= new_c < w and
                new_c >= vehicle_width//2 and new_c < w - vehicle_width//2):
                
                # Check if vehicle can fit
                can_fit = True
                for offset in range(-vehicle_width//2, vehicle_width//2 + 1):
                    check_col = new_c + offset
                    if (check_col < 0 or check_col >= w or 
                        occupancy_grid[new_r, check_col] == 1):
                        can_fit = False
                        break
                
                if can_fit:
                    neighbors.append((new_r, new_c))
        
        return neighbors
    
    # Calculate openness for goal selection
    openness = calculate_openness_map(occupancy_grid, window_size=5)
    
    # Find best goal position in target row
    best_goal_col = start_col
    best_openness = 0
    
    for c in range(vehicle_width//2, w - vehicle_width//2):
        if target_row < h and occupancy_grid[target_row, c] == 0:
            local_openness = openness[target_row, c]
            if local_openness > best_openness:
                best_openness = local_openness
                best_goal_col = c
    
    goal = (target_row, best_goal_col)
    
    # A* algorithm
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        open_set.sort(key=lambda x: x[0])
        current_f, current = open_set.pop(0)
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return list(reversed(path)), openness
        
        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + 1
            
            # Add openness bias to cost
            neighbor_openness = openness[neighbor[0], neighbor[1]] if neighbor[0] < h and neighbor[1] < w else 0
            openness_cost = (1.0 - neighbor_openness) * 2  # Prefer open areas
            tentative_g += openness_cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                
                if (f_score[neighbor], neighbor) not in open_set:
                    open_set.append((f_score[neighbor], neighbor))
    
    # No path found, return straight line
    return [(h-1, start_col), (target_row, start_col)], openness

def smooth_path(path, smoothing_factor=0.3):
    """Apply smoothing to path for more natural vehicle movement"""
    if len(path) < 3:
        return path
    
    smoothed = [path[0]]  # Keep start point
    
    for i in range(1, len(path) - 1):
        prev_point = np.array(path[i-1])
        current_point = np.array(path[i])
        next_point = np.array(path[i+1])
        
        # Moving average smoothing
        smoothed_point = (prev_point + current_point + next_point) / 3
        smoothed_point = current_point + smoothing_factor * (smoothed_point - current_point)
        smoothed.append(tuple(smoothed_point.astype(int)))
    
    smoothed.append(path[-1])  # Keep end point
    return smoothed

def grid_to_image_coordinates(path, grid_x, grid_y):
    """Convert grid coordinates to image pixel coordinates"""
    image_path = []
    for grid_row, grid_col in path:
        if (0 <= grid_row < len(grid_y) - 1 and 
            0 <= grid_col < len(grid_x) - 1):
            # Center of grid cell
            x = (grid_x[grid_col] + grid_x[grid_col + 1]) // 2
            y = (grid_y[grid_row] + grid_y[grid_row + 1]) // 2
            image_path.append((x, y))
    return image_path

def calculate_steering_angle(path, lookahead_points=3):
    """
    Calculate steering angle for vehicle control based on path
    Returns angle in degrees (-90 to 90, where 0 is straight)
    """
    if len(path) < lookahead_points + 1:
        return 0.0
    
    # Use lookahead point for steering calculation
    current_point = np.array(path[0])
    lookahead_point = np.array(path[min(lookahead_points, len(path)-1)])
    
    # Calculate direction vector
    direction = lookahead_point - current_point
    
    if direction[1] == 0:  # Avoid division by zero
        return 0.0
    
    # Calculate angle (negative because image y increases downward)
    angle_rad = math.atan2(direction[0], -direction[1])
    angle_deg = math.degrees(angle_rad)
    
    # Clamp to reasonable steering range
    return max(-45, min(45, angle_deg))

# Previous functions from pathDetectT9o

def detect_objects_by_vertical_blobs_accurate(color_map, grid_x, grid_y, hue_diff_thresh=2, min_vertical=3, slope_thresh=2):
    hsv_map = cv2.cvtColor(color_map, cv2.COLOR_BGR2HSV)
    hsv_blurred = cv2.GaussianBlur(hsv_map, (5, 5), 0)
    alert_cells = []
    max_cells = len(grid_y) - 1
    vertical_hues = [(0, 0.0)] * max_cells
    
    for j in range(len(grid_x) - 1):
        x1, x2 = grid_x[j], grid_x[j + 1]
        actual_count = 0
        for i in range(len(grid_y) - 1):
            y1, y2 = grid_y[i], grid_y[i + 1]
            if y1 >= hsv_blurred.shape[0] or y2 >= hsv_blurred.shape[0] or x1 >= hsv_blurred.shape[1] or x2 >= hsv_blurred.shape[1]:
                continue
            cell = hsv_blurred[y1:y2, x1:x2]
            if cell.size == 0:
                continue
            mean_hue = np.mean(cell[:, :, 0])
            vertical_hues[actual_count] = (i, mean_hue)
            actual_count += 1
        
        if actual_count < 2:
            continue
        
        run = []
        for idx in range(actual_count - 1):
            i1, h1 = vertical_hues[idx]
            i2, h2 = vertical_hues[idx + 1]
            delta = abs(h2 - h1)

            if delta < hue_diff_thresh:
                run.append(i1)
                if idx + 1 == actual_count - 1:
                    run.append(i2)
            else:
                if len(run) >= min_vertical:
                    hues = [vertical_hues[k][1] for k in range(len(vertical_hues)) if vertical_hues[k][0] in run]
                    if len(hues) > 1 and np.std(np.diff(hues)) < slope_thresh:
                        for k in run:
                            if k < len(grid_y) - 1:
                                y1, y2 = grid_y[k], grid_y[k + 1]
                                alert_cells.append((x1, x2, y1, y2))
                run = []

        if len(run) >= min_vertical:
            hues = [vertical_hues[k][1] for k in range(len(vertical_hues)) if vertical_hues[k][0] in run]
            if len(hues) > 1 and np.std(np.diff(hues)) < slope_thresh:
                for k in run:
                    if k < len(grid_y) - 1:
                        y1, y2 = grid_y[k], grid_y[k + 1]
                        alert_cells.append((x1, x2, y1, y2))
    
    filtered_cells = filter_alert_cells_optimized(alert_cells, image_shape=color_map.shape[:2])
    return filtered_cells

def filter_alert_cells_optimized(alert_cells, min_neighbors=6, min_vertical_span=2, image_shape=(720, 1280)):
    if not alert_cells:
        return []
    h, w = image_shape
    cell_map = np.zeros((h, w), dtype=np.uint8)
    for (x1, x2, y1, y2) in alert_cells:
        x1_c, x2_c = max(0, min(x1, w)), max(0, min(x2, w))
        y1_c, y2_c = max(0, min(y1, h)), max(0, min(y2, h))
        if x1_c < x2_c and y1_c < y2_c:
            cell_map[y1_c:y2_c, x1_c:x2_c] = 255
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cell_map, connectivity=8)
    if num_labels <= 1:
        return []
    if alert_cells:
        avg_cell_height = np.mean([y2 - y1 for _, _, y1, y2 in alert_cells])
    else:
        avg_cell_height = 1
    filtered_cells = []
    valid_labels = set()
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        vertical_blocks = max(1, int(h_box / avg_cell_height))
        if vertical_blocks >= min_vertical_span and area >= min_neighbors * 50:
            valid_labels.add(i)
    if valid_labels:
        for (x1, x2, y1, y2) in alert_cells:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if 0 <= cy < h and 0 <= cx < w and labels[cy, cx] in valid_labels:
                filtered_cells.append((x1, x2, y1, y2))
    return filtered_cells

def draw_perspective_grid_with_path(frame, spacing=SPACING, num_lines=NUM_LINES, highlight_zones=None, path=None, occupancy_grid=None, openness_map=None):
    """Enhanced grid drawing with path visualization and error handling"""
    try:
        # Ensure frame is valid
        if not isinstance(frame, np.ndarray) or frame.size == 0:
            return frame
            
        h, w = frame.shape[:2]
        vanish_x = w // 2
        vanish_y = int(h / 3)
        
        # Make a proper copy
        output = frame.copy()
        if output.dtype != np.uint8:
            output = output.astype(np.uint8)
        output = np.ascontiguousarray(output)
        
        grid_y = generate_perspective_y_lines(h, spacing)
        
        # Draw base grid
        try:
            for y in grid_y:
                cv2.line(output, (0, y), (w, y), (0, 255, 0), 1)
            
            step = w // num_lines
            for x in range(0, w + step, step):
                cv2.line(output, (x, h), (vanish_x, vanish_y), (0, 255, 0), 1)
        except Exception as e:
            print(f"Error drawing grid lines: {e}")
        
        # Draw openness visualization (optional)
        if openness_map is not None:
            try:
                grid_x = list(range(0, w + step, step))
                for r in range(openness_map.shape[0]):
                    for c in range(openness_map.shape[1]):
                        if r < len(grid_y) - 1 and c < len(grid_x) - 1:
                            openness_val = openness_map[r, c]
                            if openness_val > 0.3:  # Only show relatively open areas
                                x1, x2 = grid_x[c], grid_x[c + 1]
                                y1, y2 = grid_y[r], grid_y[r + 1]
                                # Green tint for open areas
                                overlay = output.copy()
                                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
                                cv2.addWeighted(output, 1 - openness_val * 0.3, overlay, openness_val * 0.3, 0, output)
            except Exception as e:
                print(f"Error drawing openness map: {e}")
        
        # Draw obstacle cells
        if highlight_zones:
            try:
                for (x1, x2, y1, y2) in highlight_zones:
                    # Bounds checking
                    x1, x2 = max(0, min(x1, w)), max(0, min(x2, w))
                    y1, y2 = max(0, min(y1, h)), max(0, min(y2, h))
                    if x1 < x2 and y1 < y2:
                        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), -1)  # Red fill
                        cv2.rectangle(output, (x1, y1), (x2, y2), (200, 200, 50), 2)  # Yellow border
            except Exception as e:
                print(f"Error drawing obstacle zones: {e}")
        
        # Draw path
        if path and len(path) > 1:
            try:
                # Draw path line
                for i in range(len(path) - 1):
                    pt1 = (int(path[i][0]), int(path[i][1]))
                    pt2 = (int(path[i + 1][0]), int(path[i + 1][1]))
                    # Bounds checking
                    if (0 <= pt1[0] < w and 0 <= pt1[1] < h and 
                        0 <= pt2[0] < w and 0 <= pt2[1] < h):
                        cv2.line(output, pt1, pt2, (255, 255, 0), 3)  # Cyan path
                
                # Draw path points
                for i, point in enumerate(path):
                    pt = (int(point[0]), int(point[1]))
                    if 0 <= pt[0] < w and 0 <= pt[1] < h:
                        color = (0, 255, 255) if i == 0 else (255, 255, 0)  # Start point red, others cyan
                        radius = 8 if i == 0 else 5
                        cv2.circle(output, pt, radius, color, -1)
                
                # Draw vehicle position and direction
                if len(path) > 1:
                    start = (int(path[0][0]), int(path[0][1]))
                    direction = np.array([path[1][0] - path[0][0], path[1][1] - path[0][1]])
                    if np.linalg.norm(direction) > 0:
                        direction = direction / np.linalg.norm(direction) * 30
                        end_point = (int(start[0] + direction[0]), int(start[1] + direction[1]))
                        # Bounds checking
                        if (0 <= start[0] < w and 0 <= start[1] < h and 
                            0 <= end_point[0] < w and 0 <= end_point[1] < h):
                            cv2.arrowedLine(output, start, end_point, (0, 255, 255), 3, tipLength=0.3)
            except Exception as e:
                print(f"Error drawing path: {e}")
        
        return output, vanish_x, vanish_y
        
    except Exception as e:
        print(f"Error in draw_perspective_grid_with_path: {e}")
        return frame, w//2, int(h/3) if h > 0 else 100

def classify_clusters(clusters, depth_map, image_shape):
    """Original classification preserved for accuracy"""
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

# [Include the previous DepthWorker and MJPEGStreamReaderThread classes here - they remain unchanged]
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
                self.msleep(1)

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
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True
        self.frame_count = 0
        self.last_time = time.time()

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_received.emit(frame)
                self.frame_count += 1
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

class PathfindingViewer(QWidget):
    def __init__(self, stream_url):
        super().__init__()
        self.setWindowTitle("DriveCore - Advanced Pathfinding System")
        self.setFixedSize(1280, 720)

        self.video_label = QLabel("Loading...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Initialize components
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
        self.timer.start(16)

        # Pathfinding state
        self.depth_result = None
        self.depth_vis = None
        self.frame_skip = 2
        self.frame_count = 0
        self.grid_cache = None
        self.grid_cache_size = None
        
        # Pathfinding parameters
        self.config = PathConfig()
        self.current_path = None
        self.steering_angle = 0.0
        self.pathfinding_method = "potential_field"  # or "astar"

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
            # Cache grid lines
            current_size = (frame.shape[1], frame.shape[0])
            if self.grid_cache is None or self.grid_cache_size != current_size:
                self.grid_cache = get_grid_lines(frame.shape[1], frame.shape[0])
                self.grid_cache_size = current_size
            
            grid_x, grid_y = self.grid_cache
            
            # Detect obstacles
            alert_cells = detect_objects_by_vertical_blobs_accurate(
                self.depth_vis, grid_x, grid_y)
            
            # Create occupancy grid for pathfinding
            occupancy_grid = create_occupancy_grid(alert_cells, grid_x, grid_y, frame.shape[:2])
            
            # Expand obstacles for safety
            safe_occupancy = expand_obstacles(occupancy_grid, self.config.SAFETY_MARGIN)
            
            # Calculate target position
            target_row = int(len(grid_y) * (1 - self.config.TARGET_HORIZON))
            start_col = len(grid_x) // 2  # Start from center
            
            # Generate path
            try:
                if self.pathfinding_method == "potential_field":
                    path, potential_map, openness_map = find_best_path_potential_field(
                        safe_occupancy, start_col, target_row, self.config.VEHICLE_WIDTH)
                else:  # A*
                    path, openness_map = find_best_path_astar(
                        safe_occupancy, start_col, target_row, self.config.VEHICLE_WIDTH)
                    potential_map = None
                
                # Smooth path for natural movement
                if len(path) > 2:
                    path = smooth_path(path, self.config.SMOOTHING_FACTOR)
                
                # Convert to image coordinates
                image_path = grid_to_image_coordinates(path, grid_x, grid_y)
                self.current_path = image_path
                
                # Calculate steering angle for vehicle control
                if len(image_path) > 1:
                    self.steering_angle = calculate_steering_angle(image_path, self.config.LOOKAHEAD_DISTANCE)
                
            except Exception as e:
                print(f"Pathfinding error: {e}")
                self.current_path = None
                openness_map = None
            
            # Start with depth blended frame for better visibility
            output = cv2.addWeighted(frame, 0.7, self.depth_vis, 0.3, 0)
            
            # Draw grid and obstacles
            output = self.draw_enhanced_visualization(output, alert_cells, grid_x, grid_y, safe_occupancy, openness_map)
            
            # Draw path on top with high visibility
            if self.current_path and len(self.current_path) > 1:
                self.draw_path_overlay(output, self.current_path)
            
            # Add status information
            self.draw_status_overlay(output, alert_cells)
            
            # Draw steering indicator
            self.draw_steering_indicator(output)
            
        else:
            # Show original frame with basic grid when no depth is available
            output = frame.copy()
            h, w = output.shape[:2]
            
            # Draw basic grid
            grid_y_lines = generate_perspective_y_lines(h, SPACING)
            vanish_x = w // 2
            vanish_y = int(h / 3)
            
            for y in grid_y_lines:
                cv2.line(output, (0, y), (w, y), (0, 255, 0), 1)
            
            step = w // NUM_LINES
            for x in range(0, w + step, step):
                cv2.line(output, (x, h), (vanish_x, vanish_y), (0, 255, 0), 1)
            
            # Show waiting message
            cv2.putText(output, "Waiting for depth data...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
            cv2.putText(output, "Waiting for depth data...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

        # Display
        qimage = convert_to_qimage(output)
        self.video_label.setPixmap(QPixmap.fromImage(qimage))

    def draw_enhanced_visualization(self, frame, alert_cells, grid_x, grid_y, occupancy_grid, openness_map):
        """Draw grid, obstacles, and openness visualization"""
        output = frame.copy()
        h, w = output.shape[:2]
        
        # Draw perspective grid (lighter)
        grid_y_lines = generate_perspective_y_lines(h, SPACING)
        vanish_x = w // 2
        vanish_y = int(h / 3)
        
        # Draw grid lines (more transparent)
        for y in grid_y_lines:
            cv2.line(output, (0, y), (w, y), (0, 150, 0), 1)
        
        step = w // NUM_LINES
        for x in range(0, w + step, step):
            cv2.line(output, (x, h), (vanish_x, vanish_y), (0, 150, 0), 1)
        
        # Draw openness areas (green tint)
        if openness_map is not None:
            for r in range(openness_map.shape[0]):
                for c in range(openness_map.shape[1]):
                    if r < len(grid_y) - 1 and c < len(grid_x) - 1:
                        openness_val = openness_map[r, c]
                        if openness_val > 0.4:
                            x1, x2 = grid_x[c], grid_x[c + 1]
                            y1, y2 = grid_y[r], grid_y[r + 1]
                            # Bright green for very open areas
                            overlay = output.copy()
                            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
                            cv2.addWeighted(output, 1 - openness_val * 0.4, overlay, openness_val * 0.4, 0, output)
        
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

        #Draw individual alert cells (crucial for pathfinding)
            for (x1, x2, y1, y2) in alert_cells:
                cv2.rectangle(output, (x1, y1), (x2, y2), (200, 200, 50), 2)  # light yellow cells

        # Draw classification results
            for (x1, y1, x2, y2, label) in classified:
                region = self.depth_result[y1:y2, x1:x2]
                avg_depth = np.mean(region) if region.size > 0 else 0
                color = {"obstacle": (255, 0, 255), "wall": (0, 255, 255), "dip": (0, 100, 255)}[label]
                cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
                cv2.putText(output, f"{label} ({avg_depth:.2f}m)", (x1, y2 + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
        '''# Draw obstacle cells with high visibility
        for (x1, x2, y1, y2) in alert_cells:
            # Bright red fill
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), -1)
            # Bright yellow border
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 255), 2)'''
        
        return output
    
    def draw_path_overlay(self, image, path):
        """Draw path with high visibility"""
        if not path or len(path) < 2:
            return
            
        h, w = image.shape[:2]
        
        # Draw thick path line with shadow effect
        for i in range(len(path) - 1):
            pt1 = (int(path[i][0]), int(path[i][1]))
            pt2 = (int(path[i + 1][0]), int(path[i + 1][1]))
            
            # Bounds check
            if (0 <= pt1[0] < w and 0 <= pt1[1] < h and 
                0 <= pt2[0] < w and 0 <= pt2[1] < h):
                # Draw shadow (black, thick)
                cv2.line(image, pt1, pt2, (0, 0, 0), 8)
                # Draw main path (bright cyan)
                cv2.line(image, pt1, pt2, (255, 255, 0), 4)
        
        # Draw path waypoints
        for i, point in enumerate(path):
            pt = (int(point[0]), int(point[1]))
            if 0 <= pt[0] < w and 0 <= pt[1] < h:
                if i == 0:  # Start point (current position)
                    cv2.circle(image, pt, 12, (0, 0, 0), -1)  # Black shadow
                    cv2.circle(image, pt, 10, (0, 255, 0), -1)  # Green center
                    cv2.circle(image, pt, 10, (255, 255, 255), 2)  # White border
                else:  # Path points
                    cv2.circle(image, pt, 6, (0, 0, 0), -1)  # Black shadow
                    cv2.circle(image, pt, 4, (255, 255, 0), -1)  # Cyan center
        
        # Draw vehicle direction arrow from start
        if len(path) > 1:
            start = (int(path[0][0]), int(path[0][1]))
            next_pt = (int(path[1][0]), int(path[1][1]))
            
            direction = np.array([next_pt[0] - start[0], next_pt[1] - start[1]])
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction) * 40
                end_point = (int(start[0] + direction[0]), int(start[1] + direction[1]))
                
                if (0 <= start[0] < w and 0 <= start[1] < h and 
                    0 <= end_point[0] < w and 0 <= end_point[1] < h):
                    # Draw direction arrow with shadow
                    cv2.arrowedLine(image, start, end_point, (0, 0, 0), 6, tipLength=0.4)  # Shadow
                    cv2.arrowedLine(image, start, end_point, (255, 255, 255), 3, tipLength=0.4)  # Arrow
    
    def draw_steering_indicator(self, image):
        """Draw steering wheel indicator with error handling"""
        try:
            # Ensure image is valid
            if not isinstance(image, np.ndarray) or image.size == 0:
                return
                
            h, w = image.shape[:2]
            center_x, center_y = w - 100, 80
            radius = 50
            
            # Draw steering wheel background
            cv2.circle(image, (center_x, center_y), radius, (100, 100, 100), 3)
            cv2.circle(image, (center_x, center_y), radius - 10, (50, 50, 50), 1)
            
            # Draw steering direction
            angle_rad = math.radians(self.steering_angle)
            end_x = center_x + int((radius - 15) * math.sin(angle_rad))
            end_y = center_y - int((radius - 15) * math.cos(angle_rad))
            
            color = (0, 255, 0) if abs(self.steering_angle) < 10 else (0, 255, 255)
            cv2.arrowedLine(image, (center_x, center_y), (end_x, end_y), color, 3, tipLength=0.3)
            
            # Draw angle text with error handling
            angle_text = f"{self.steering_angle:.1f}°"
            cv2.putText(image, angle_text, 
                       (center_x - 30, center_y + radius + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        except Exception as e:
            print(f"Error drawing steering indicator: {e}")
            pass

    def draw_status_overlay(self, image, alert_cells):
        """Draw status information with enhanced visibility"""
        # Create semi-transparent background
        overlay = image.copy()
        cv2.rectangle(overlay, (5, 5), (300, 120), (0, 0, 0), -1)
        cv2.addWeighted(image, 0.7, overlay, 0.3, 0, image)
        
        status_text = [
            f"Method: {self.pathfinding_method.replace('_', ' ').title()}",
            f"Obstacles: {len(alert_cells)} cells",
            f"Steering: {self.steering_angle:.1f}°",
            f"Path Points: {len(self.current_path) if self.current_path else 0}"
        ]
        
        y_offset = 25
        for text in status_text:
            # Draw text with outline for better visibility
            cv2.putText(image, str(text), (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)  # Black outline
            cv2.putText(image, str(text), (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)  # White text
            y_offset += 22
        """Draw steering wheel indicator with error handling"""
        try:
            # Ensure image is valid
            if not isinstance(image, np.ndarray) or image.size == 0:
                return
                
            h, w = image.shape[:2]
            center_x, center_y = w - 100, 80
            radius = 50
            
            # Draw steering wheel background
            cv2.circle(image, (center_x, center_y), radius, (100, 100, 100), 3)
            cv2.circle(image, (center_x, center_y), radius - 10, (50, 50, 50), 1)
            
            # Draw steering direction
            angle_rad = math.radians(self.steering_angle)
            end_x = center_x + int((radius - 15) * math.sin(angle_rad))
            end_y = center_y - int((radius - 15) * math.cos(angle_rad))
            
            color = (0, 255, 0) if abs(self.steering_angle) < 10 else (0, 255, 255)
            cv2.arrowedLine(image, (center_x, center_y), (end_x, end_y), color, 3, tipLength=0.3)
            
            # Draw angle text with error handling
            angle_text = f"{self.steering_angle:.1f}°"
            cv2.putText(image, angle_text, 
                       (center_x - 30, center_y + radius + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        except Exception as e:
            print(f"Error drawing steering indicator: {e}")
            pass

    def on_depth_ready(self, depth_map, vis_img):
        self.depth_result = depth_map
        self.depth_vis = vis_img

    def on_stream_fps(self, fps):
        method_display = self.pathfinding_method.replace("_", " ").title()
        self.status_label.setText(f"Stream FPS: {fps:.1f} | Method: {method_display} | Steering: {self.steering_angle:.1f}°")

    def keyPressEvent(self, event):
        """Handle keyboard input for switching pathfinding methods"""
        if event.key() == Qt.Key_1:
            self.pathfinding_method = "potential_field"
            print("Switched to Potential Field pathfinding")
        elif event.key() == Qt.Key_2:
            self.pathfinding_method = "astar"
            print("Switched to A* pathfinding")
        elif event.key() == Qt.Key_Space:
            # Toggle safety margin
            self.config.SAFETY_MARGIN = 2 if self.config.SAFETY_MARGIN == 1 else 1
            print(f"Safety margin: {self.config.SAFETY_MARGIN}")
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            # Increase vehicle width
            self.config.VEHICLE_WIDTH = min(7, self.config.VEHICLE_WIDTH + 1)
            print(f"Vehicle width: {self.config.VEHICLE_WIDTH}")
        elif event.key() == Qt.Key_Minus:
            # Decrease vehicle width
            self.config.VEHICLE_WIDTH = max(1, self.config.VEHICLE_WIDTH - 1)
            print(f"Vehicle width: {self.config.VEHICLE_WIDTH}")

    def get_vehicle_control_data(self):
        """
        Get data for vehicle control system
        Returns dict with steering angle, path confidence, and obstacle info
        """
        if not self.current_path:
            return {
                'steering_angle': 0.0,
                'path_confidence': 0.0,
                'obstacle_distance': float('inf'),
                'path_length': 0,
                'has_clear_path': False
            }
        
        # Calculate path confidence based on length and smoothness
        path_confidence = min(1.0, len(self.current_path) / 10.0)
        
        # Estimate obstacle distance (simplified)
        obstacle_distance = len(self.current_path) * 0.5  # Rough estimate
        
        return {
            'steering_angle': self.steering_angle,
            'path_confidence': path_confidence,
            'obstacle_distance': obstacle_distance,
            'path_length': len(self.current_path),
            'has_clear_path': True
        }

    def closeEvent(self, event):
        self.stream_thread.stop()
        self.depth_worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PathfindingViewer(VIDEO_URL)
    viewer.show()
    
    # Print controls
    print("\n=== PATHFINDING CONTROLS ===")
    print("Key 1: Switch to Potential Field pathfinding")
    print("Key 2: Switch to A* pathfinding")
    print("Space: Toggle safety margin (1-2)")
    print("+/-: Adjust vehicle width")
    print("============================\n")
    
    sys.exit(app.exec())