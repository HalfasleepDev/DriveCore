## Vehicle Tuning Settings Overview

The **Vehicle Tuning Settings Tab** provides configuration tools for calibrating the RC vehicle’s servo, ESC, and networking settings. It also lays the groundwork for future tuning of acceleration and deceleration behavior.

---

### Servo Calibration (µs)

Calibrate the steering servo's behavior with precision:

- **Min / Max**: Define the mechanical limits for the servo (e.g., 900–2100 µs).
- **Fine Tune Slider**: Adjust and preview the center position of the servo manually.
- **Set as Mid**: Locks in the currently selected value as the servo’s midpoint.
- **Reset to 1500**: Quickly restores the servo to its default center.

> Use the **Test Servo** button to preview the settings live on the hardware.

---

### ESC Calibration (µs)

Fine-tune the throttle ESC (Electronic Speed Controller) behavior:

- **Min**: Idle or minimum throttle PWM value (e.g., 1310 µs).
- **Mid**: Neutral throttle pulse width (typically 1500 µs).
- **Max**: Maximum throttle output (e.g., 1750 µs).

> Use the **Test ESC** button to validate the throttle response in real time.

---

### Network Port Configuration

Set or review the port numbers used for communication between the DriveCore host and client:

- **Comm Port**: Port used for UDP or socket-based command transmission.
- **Webcam Port**: Port used for video stream (Flask or HTTP-based).

> Click **Apply Port Settings** to update active socket configurations.

---

### Acceleration / Deceleration Curves *(coming soon)*

Future updates will introduce curve shaping to control:

- Smooth ramp-up when accelerating
- Controlled roll-off when slowing down

This will help simulate realistic vehicle dynamics and reduce jerkiness during control.

---

These tuning tools are essential for adapting DriveCore to various RC platforms and driving environments. They allow for real-time testing, safer limits, and precise control feedback.