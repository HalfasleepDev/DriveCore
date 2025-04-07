# DriveCore v1.1 – Initial Release

**Release Date:** 7-04-2025 *(Originally published on this repo)*
**Version:** `v1.1`  
**Components:** Client (PySide6 GUI) & Host (Raspberry Pi Controller)
**Tested Environment:** Arch Linux Wayland
**Download ZIP:** [D-14.zip](releases/D-14-Ver-1-1.zip)

---

## Overview

![OpenCV Overlay Ver 1.1](D-14/Diagrams-Concepts/Ver-1-1/CvOverlayV1-1.png)


DriveCore is a modular platform designed to control and experiment with autonomous RC vehicles using Python, OpenCV, and a Raspberry Pi.

Version 1.1 introduces OpenCv path detection, a new settings page, and a Heads-Up-Display.

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
- [openCV-testing iteration 04](Client-Side/openCV-testing/README.md) implemented & refactored.
- `SPACE BAR` input added for brake.
- OpenCv settings menu added with overlay toggles.
- Added rough obstacle collision warning/automatic brake.
- Added error popups.
- Added loading cursor for host connection.
- Removed *debug* print statements.

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

---

## Setup Instructions

### Install Dependencies
```bash
pip install -r requirements.txt
```
- For host and client

### Configure RC Car Control Server
- Create `DriveCore` folder on the Raspberry Pi
- Copy `drive-core-host.sh`, `driveCoreHost.py`, `getIpAddr.py`, and `webStream.py` to the Raspberry Pi's folder called DriveCore

### Run the RC Car Control Server
```bash
sudo pigpiod  # Start pigpio daemon
cd Drivecore
sudo ./drive-core-host.sh
```
- Wait a minute or so for the Flask server to start streaming

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
For full setup and wiring, see the [D-14 Client and Host Diagram Section](D-14/Diagrams-Concepts/README.md)  *(Coming soon)*

---

## Known Issues

- `Emergency Disconnect` does not work properly.
- Sometimes multiple commands are sent at once.
- The servo needs to be recalibrated.
- The automatic brake creates an info backup

---

## Roadmap (v1.1 and Beyond)

- [ ] Steering and max throttle tunning on the `settings` page
- [ ] Client-Host communication & verification
- [ ] Drive model *(HOST)*
- [ ] Acceleration curves *(CLIENT)*
- [ ] UI design consistency
- [ ] Upgrade `settings` page
- [ ] Application packaging
- [ ] Vehicle status info *(CLIENT)*