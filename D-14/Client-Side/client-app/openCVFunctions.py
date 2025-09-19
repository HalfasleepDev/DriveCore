"""
openCVFunctions.py

OpenCv functions implementation from pathDetectT4.py

Author: HalfasleepDev
Created: 04-04-2025
"""

import sys
import cv2
import numpy as np
import os

class FrameProcessor:
    def __init__(self, mainWindow, videoThread):
        self.mainWindow = mainWindow
        self.videoThread = videoThread

    '''Initialize the Kalman Filter'''
    def initKalmanFilter(self):
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                [0, 1, 0, 0]], np.float32)
        
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                                [0, 1, 0, 1],
                                                [0, 0, 1, 0],
                                                [0, 0, 0, 1]], np.float32)
        
        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.05

    '''Main function to detect the floor region, obstacles, and update tracking'''
    def detect_floor_region(self, frame):
        # If openCV is enabled
        if self.mainWindow.IS_DRIVE_ASSIST_ENABLED:
            self.mainWindow.frame_counter += 1
            self.mainWindow.alert_triggered = False

            height, width = frame.shape[:2]

            # Step 1: Detect obstacles in bottom half
            self.detect_obstacles(frame, height)

            # Step 2: Sample ambient light for color correction
            hsv, ambient_hue_shift, ambient_val_shift = self.sample_ambient_light(frame)

            # Step 3: Sample floor color and compute adaptive HSV thresholds
            lower_floor, upper_floor, sample_box_coords = self.sample_floor_color(frame, hsv, ambient_hue_shift, ambient_val_shift)

            # Step 4: Draw sample region on frame for debugging
            
            self.draw_floor_sampling_box(frame, sample_box_coords)

            # Step 5: Draw alert line if obstacles are near
            if self.mainWindow.COLLISION_ASSIST_ENABLED:
                self.draw_alert_line(frame, width)

            # Step 6: Display alert zone GUI message
            self.check_alert_popup(frame)

            # Step 7: Create mask to isolate floor area
            floor_mask = self.create_floor_mask(hsv, lower_floor, upper_floor, height)

            # Step 8: Find and track largest floor contour
            largest = self.get_largest_floor_contour(floor_mask)

            if largest is not None:
                self.update_kalman_path(frame, largest)

            return frame
        
        else:
            return frame

    '''Detect obstacles using background subtraction and edge detection'''
    def detect_obstacles(self, frame, height):
        roi = frame[int(height * 0.5):, :]
        gray_bottom = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Foreground mask from background subtractor
        fgmask = self.mainWindow.fgbg.apply(roi)
        kernel = np.ones((5, 5), np.uint8)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)

        # Edge detection
        edges = cv2.Canny(gray_bottom, 50, 200)
        combined_mask = cv2.bitwise_or(fgmask, edges)

        # Detect obstacle contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                x, y, w, h = cv2.boundingRect(cnt)
                depth_y = y + int(height * 0.5)

                if depth_y + h > self.mainWindow.alert_line_y:
                    self.mainWindow.alert_triggered = True

                # Simulated depth color
                depth_score = 0.95 - (depth_y / height)
                color = (0, int(255 * depth_score), 255 - int(255 * depth_score))

                # Draw box
                if self.mainWindow.OBJECT_VIS_ENABLED:
                    cv2.rectangle(frame, (x, depth_y), (x + w, depth_y + h), color, 2)
                    cv2.putText(frame, "Obstacle", (x, depth_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    '''Sample ambient color for HSV correction'''
    def sample_ambient_light(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width = hsv.shape[:2]

        x_a = width // 2 - 300
        y_a = 90
        sample = hsv[y_a:y_a + 30, x_a:x_a + 600]
        blurred = cv2.GaussianBlur(sample, (5, 5), 0)
        mean = np.mean(blurred.reshape(-1, 3).astype(np.float32), axis=0)
        h_shift = int(mean[0] - 90)
        v_shift = int(mean[2] - 128)

        # Draw ambient sample box
        if self.mainWindow.AMBIENT_VIS_ENABLED:
            cv2.rectangle(frame, (x_a, y_a), (x_a + 600, y_a + 30), (255, 100, 0), 1)
            cv2.putText(frame, "Ambient", (x_a - 10, y_a - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 100, 0), 1)

        return hsv, h_shift, v_shift

    '''Smart floor color sampling and adaptive HSV margin calculation'''
    def sample_floor_color(self, frame, hsv, h_shift, v_shift):
        height, width = hsv.shape[:2]
        sample_w, sample_h = 300, 50
        y_start = height - sample_h - 100
        x_center = width // 2

        # Edge-based mask to avoid obstacle regions
        obstacle_mask = cv2.dilate(cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 50, 150),
                                np.ones((5, 5), np.uint8), iterations=2)

        # Smart horizontal search
        '''x_start = self.find_clean_sample_x(obstacle_mask, y_start, sample_w, sample_h, width, x_center)
        self.last_sample_x = x_start'''
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

        region = hsv[y_start:y_start + sample_h, x_start:x_start + sample_w]
        blurred = cv2.GaussianBlur(region, (7, 7), 0)
        mean = np.mean(blurred.reshape(-1, 3).astype(np.float32), axis=0)
        std = np.std(blurred.reshape(-1, 3).astype(np.float32), axis=0)

        h, s, v = mean
        h_std, s_std, v_std = std

        # Adaptive margins based on standard deviation
        h_margin = int(np.clip(h_std * 1.5, self.mainWindow.ui.HRowSlider.value(), 50))
        s_margin = int(np.clip(s_std * 1.5, self.mainWindow.ui.SRowSlider.value(), 100))
        v_margin = int(np.clip(v_std * 1.5, self.mainWindow.ui.VRowSlider.value(), 100))

        self.auto_h_margin = h_margin
        self.auto_s_margin = s_margin
        self.auto_v_margin = v_margin
        cv2.putText(frame, f"Auto HSV Margin: H={h_margin} S={s_margin} V={v_margin}", (frame.shape[1] - 340, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Ambient Shift – Hue: {h_shift:+.0f}, Value: {v_shift:+.0f}", (frame.shape[1] - 340, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        #self.ambient_debug.setText(f"Ambient Shift – Hue: {h_shift:+.0f}, Value: {v_shift:+.0f}")

        corrected_h = np.clip(h - h_shift * 0.4, 0, 180)
        corrected_v = np.clip(v - v_shift * 0.3, 0, 255)

        lower = np.array([max(corrected_h - h_margin, 0), max(s - s_margin, 0), max(corrected_v - v_margin, 0)], dtype=np.uint8)
        upper = np.array([min(corrected_h + h_margin, 180), min(s + s_margin, 255), min(corrected_v + v_margin, 255)], dtype=np.uint8)

        return lower, upper, (x_start, y_start, sample_w, sample_h)

    '''Search left/right for obstacle-free area to sample floor color'''
    '''def find_clean_sample_x(self, mask, y, w, h, width, center):
        for dx in range(0, width // 2, 10):
            for direction in [-1, 1]:
                x = center + dx * direction - w // 2
                if not (x <0 or x + w > width):
                    if np.mean(mask[y:y + h, x:x + w]) < 10:
                        return x
        return getattr(self, 'last_sample_x', center - w // 2)'''

    '''Draw the yellow box used to sample floor HSV color'''
    def draw_floor_sampling_box(self, frame, coords):
        x, y, w, h = coords
        if self.mainWindow.FLOOR_SAMPLE_VIS_ENABLED:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(frame, "Floor Sample", (x - 10, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    '''Draw a horizontal alert line across screen center'''
    def draw_alert_line(self, frame, width):
        x_start = width // 2 - 400
        x_end = width // 2 + 400
        color = (0, 0, 255) if self.mainWindow.alert_triggered else (200, 200, 200)
        cv2.line(frame, (x_start, self.mainWindow.alert_line_y), (x_end, self.mainWindow.alert_line_y), color, 2)
        cv2.putText(frame, "ALERT ZONE", (x_start, self.mainWindow.alert_line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    '''Update GUI alert zone message based on object detection'''
    def check_alert_popup(self, frame):
        if self.mainWindow.alert_triggered and not getattr(self, 'alert_shown', False):
            self.alert_shown = True
            cv2.putText(frame, "NOTICE: Collision Zone Entered", (frame.shape[1] - 310, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            #self.alert_zone_debug.setText("NOTICE: Collision Zone Entered")
        elif not self.mainWindow.alert_triggered:
            self.alert_shown = False
            cv2.putText(frame, "SAFE", (frame.shape[1] - 310, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            #self.alert_zone_debug.setText("SAFE")

    '''Create binary mask for floor using HSV range and region-of-interest'''
    def create_floor_mask(self, hsv, lower, upper, height):
        mask = cv2.inRange(hsv, lower, upper)
        roi = np.zeros_like(mask)
        roi[int(height / 2):, :] = 255
        floor_mask = cv2.bitwise_and(mask, roi)

        kernel = np.ones((5, 5), np.uint8)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_DILATE, kernel)
        floor_mask = cv2.dilate(floor_mask, kernel, iterations=2)

        return floor_mask

    '''Select the largest valid floor contour (with fallback)'''
    def get_largest_floor_contour(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 5000:
                self.mainWindow.last_floor_contour = largest
            elif self.mainWindow.last_floor_contour is not None:
                largest = self.mainWindow.last_floor_contour
            else:
                largest = None
        else:
            largest = getattr(self, 'last_floor_contour', None)
        return largest

    '''Draw the tracked contour and Kalman filtered center point'''
    def update_kalman_path(self, frame, contour):
        if self.mainWindow.KALMAN_CENTER_VIS_ENABLED:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
            self.kalman.correct(measurement)
            prediction = self.kalman.predict()
            kx, ky = int(prediction[0]), int(prediction[1])
            if self.mainWindow.KALMAN_CENTER_VIS_ENABLED:
                cv2.circle(frame, (kx, ky), 5, (0, 255, 255), -1)
                cv2.putText(frame, "Kalman Center", (kx - 40, ky - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        self.draw_kalman_smoothed_curve(frame, contour, self.mainWindow.frame_counter)


    '''Draw the predicted path'''
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
                if self.mainWindow.KALMAN_CENTER_VIS_ENABLED:
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
            if self.mainWindow.PATH_VIS_ENABLED:
                for i in range(len(path_points) - 1):
                    if i == 0:
                        cv2.line(frame, path_points[i], path_points[i + 1], (255, 255, 0), 2)
                    cv2.line(frame, path_points[i], path_points[i + 1], (255, 0, 0), 2)

                # Draw predicted center
                cv2.circle(frame, (int(prediction[0]), int(prediction[1])), 5, (0, 255, 255), -1)

        except Exception as e:
            print("Path fitting error:", e)

