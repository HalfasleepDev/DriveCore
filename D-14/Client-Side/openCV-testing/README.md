# Open-CV Testing

This folder contains experimental scripts and prototypes for testing various OpenCV-based vision techniques for the DriveCore Project.

The purpose of this directory is to iterate quickly on different ideas including:
- Floor detection
- Obstacle detection
- Simulated depth estimation
- Path planning
- Contour tracking
- Kalman filtering
- Other computer vision utilities

Each script is treated as a standalone experiment or iteration, with its purpose, techniques, and results noted below.

---

## Iteration Notes

### Iteration 01 - `pathDetectT1.py`
- **Goal:** Automatically isolate most driveable flat surfaces, and map a path(curve).
- **Technique:** Sampling using a predefined color array.
- **Result:** Subpar outlining of the floor/surface.
- **GUI Demo:**
![Iteration 01 GUI](T1_GUI.png)

### Iteration 02 - `pathDetectT2.py`
- **Goal:** Automatically isolate most driveable flat surfaces, map a path(curve), and sample the floor automatically. 
- **Technique:** Use a box on the lower portion of the screen to sample the HSV values of the floor. Applied Kalman Path Smoothing.
- **Result:** Clean, predictive path useful for motion planning, and addition of HSV sliders.
- **GUI Demo:**
![Iteration 02 GUI](T2_GUI.png)

### Iteration 03 - `pathDetectT3.py`
- **Goal:** Detect non-floor objects and estimate proximity.
- **Technique:** Canny edge + contour + ROI + color-coded bounding boxes.
- **Result:** Real-time obstacle alerting with depth-based coloring. Increased resolution to 1280 X 720.
- **GUI Demo:**
![Iteration 03 GUI](T3_GUI.png)

---

## Next Steps

### Iteration 04:
- Reduce the noice of the outlines.
- Increase the stability and reliablity of the object detection.
- Implement error popups.

---

## How to Run

- Make sure you are in a venv.
- Ensure that the camera or video stream is running

```bash
# Inside the Open-CV Testing folder
python pathDetectTXX.py
```

- **Required packages:**
```bash
pip install opencv-python numpy PySide6
```
