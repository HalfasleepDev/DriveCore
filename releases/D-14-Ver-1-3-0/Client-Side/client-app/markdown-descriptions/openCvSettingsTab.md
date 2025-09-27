## OpenCV Settings Overview

The **OpenCV Settings Tab** provides advanced control and visualization tools for debugging and tuning the computer vision pipeline used in the DriveCore system. It offers real-time toggle options for visual overlays and HSV sensitivity configuration.

---

### Debug Options

Toggle visibility of OpenCV overlays for better understanding and debugging of the pathfinding and object detection systems:

| Option               | Description                                                   |
|----------------------|---------------------------------------------------------------|
| **Object Vis**       | Highlights detected objects and bounding boxes                |
| **Floor Vis**        | Outlines the estimated drivable floor region                  |
| **Kalman Center Vis**| Displays the predicted path center from the Kalman filter     |
| **Ambient Vis**      | Shows the ambient light sampling zone                         |
| **FloorSample Vis**  | Highlights the area used for adaptive HSV floor detection     |
| **Path Vis**         | Visualizes the calculated trajectory or planned path          |

---

### Min HSV Sensitivity Margins

Adjust the **minimum HSV margin thresholds** to fine-tune floor detection stability under different lighting conditions. These values influence the tolerance range when identifying floor-like surfaces:

- **H Margin**: Hue sensitivity  
- **S Margin**: Saturation sensitivity  
- **V Margin**: Value (brightness) sensitivity  

Lower margins = more strict matching.  
Higher margins = more leniency for dynamic environments.

---

### Collision Assist

The **Collision Assist** feature provides intelligent protection against frontal obstacles:

- When enabled, DriveCore monitors obstacle proximity.
- If an object crosses a predefined **tripwire distance**, the system automatically issues a `"BRAKE"` command.
- A **visual alert** is shown on the HUD when this zone is breached.

Toggle this feature using the **OFF/ON** button at the bottom.

---

### Use Case

This page is ideal for developers and testers needing:
- Immediate feedback from vision processing  
- Parameter tuning without restarting the application  
- Enhanced safety in autonomous or semi-autonomous modes