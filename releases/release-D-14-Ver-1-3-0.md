# DriveCore v1.3.0 – "Control System & Communication Layer"

**Release Date:** 27-09-2025 *(Originally published on this repo)*
**Version:** `v1.3.0`  
**Components:** Client (PySide6 GUI) & Host (Raspberry Pi Controller)
**Tested Environment:** Arch Linux Wayland
**Download ZIP:** [D-14.zip](releases/D-14-Ver-1-3-0.zip)

---

## Overview

![Ver 1.3.0 Demo](D-14/Diagrams-Concepts/Ver-1-3-0/DemoV1-3-0.gif)


DriveCore is a modular platform designed to control and experiment with autonomous RC vehicles using Python, OpenCV, and a Raspberry Pi.

Version 1.3.0 introduces a new client-host communication layer, and full UI element implementation.

---

## What's Included

### Client (Desktop Application)
#### Ver 1.0
- Built with **PySide6** and **OpenCV**
- Store recently connected IPs in history
- Video stream
- Inputs using `W` `A` `S` `D`
- On exit, the host "should" stop running
#### Ver 1.1
- [openCV-testing iteration 04](D-14/Client-Side/openCV-testing/README.md) implemented & refactored.
- `SPACE BAR` input added for brake.
- OpenCv settings menu added with overlay toggles.
- Added rough obstacle collision warning/automatic brake.
- Added error popups.
- Added loading cursor for host connection.
- Removed *debug* print statements.
#### Ver 1.2
- Added multiple new UI Elements demonstrated in [ui-prototypes Ver 1.2](D-14/Client-Side/ui-prototypes/README.md).
    - `Project Info Widget`
    - `General Logs Widget`
    - `Speedometer Widget`
    - `Steer Angle Widget`
    - `PRND Selector Widget`
    - `DriveAssist Alert Widget`
    - `System Log Page`
    - `Vehicle Calibration Widget`
    - `Settings Description Widget`
- Added a new custom boot screen animation
- General UI Fixes and Tweaks for consistancy.
#### Ver 1.3.0
- Added a **new** communication layer & full UI implementation for the widgets from Ver 1.2.
- Acceleration curves.
- Vehicle status info display.
- Connection restart protocols
- **New** System Error messages and popups. 
- **New** System logs.
- **New** Username and password connection.
- App settings and calibration integration.
- Drive Mode framework. (Client based)
- UDP video stream integration.
- Command stream system.

### Host (Raspberry Pi)
#### Ver 1.0
- Servo and ESC control using **pigpio** for smoother PWM
- Socket server for remote throttle and steering commands
- Can move forward, backward, and any combination with left or right
- Connection timeout safety stop
- Command queue for reducing input lag
- Ease of acceleration for servo and ESC
- 720p video stream using a Flask server
- Safety features for input loss and runaway prevention
#### Ver 1.1
- Switched to UDP communication
- Added a `"BRAKE"` command
- Basic command spike detection algorithm 
- `"DISCONNECT"` command *potential fix*
#### Ver 1.3.0 
- **New** network manager system.
- **New** broadcast and verification for easier connection on wireless networks.
- **New** UDP video stream.
- **New** protocols.
- **New** Settings implementation. 
- **New** floodlight status implementation. 
---

## Setup Instructions

### Install Dependencies
```bash
pip install -r requirements.txt
```
- For host and client

### Configure RC Car Control Server
- Create `DriveCore` folder on the Raspberry Pi.
- Create a python venv.
- Copy `drive-core-host.sh`, `driveCoreHost.py`, `driveCoreNetwork.py`,`coreFunctions.py`, `settings.json`, and `udpHostProtocols.py` to the raspberry pi's folder called DriveCore.

### Run the RC Car Control Server
```bash
sudo pigpiod  # Start pigpio daemon
cd Drivecore
sudo ./drive-core-host.sh
```

### Launch the Client Application
```bash
python3 DriveCore/D-14/Client-Side/client-app/main.py
```

---

## System Requirements

- Raspberry Pi 4 or later (2+ GB of rRAM)
- Python 3.7+
- PySide6 for the client application
- OpenCV for computer vision processing
- `pigpio` daemon running
- For full setup and wiring, see the Follow the [D-14 Electronic Diagram](D-14/Diagrams-Concepts/D-14-Electronic-Diagram.pdf)

---

## Known Issues

- `Emergency Disconnect` does not work properly.
- The Re-Connect system is unreliable. 
- Floodlights do not work properly. 

---

## Roadmap (v1.4)

- [ ] Integrate monoculear depth estimation for floor & obstacle awareness.
- [ ] Use depth to improve obstacle detection & safety logic.
- [ ] Vehicle imu intergration.
- [ ] Map-manager system.