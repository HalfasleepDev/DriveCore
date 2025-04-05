# DriveCore v1.0 – Initial Release

**Release Date:** 21-02-2025 *(Originally published on this repo)*
**Version:** `v1.0`  
**Components:** Client (PySide6 GUI) & Host (Raspberry Pi Controller)
**Tested Environment:** Arch Linux Wayland
**Download ZIP:** [D-14.zip](https://github.com/user-attachments/files/19610983/D-14.zip)

---

## Overview

![Modified WPL D-14 Host](D-14/D-14-Mod.jpg)

DriveCore is a modular platform designed to control and experiment with autonomous RC vehicles using Python, OpenCV, and a Raspberry Pi.

Version 1.0 introduces the foundational features required for real-time remote control and a GUI-based client interface.

---

## What's Included

### Client (Desktop Application)
- Built with **PySide6** and **OpenCV**
- Store recently connected IPs in history
- Video stream
- Inputs using `W` `A` `S` `D`
- On exit, the host "should" stop running

### Host (Raspberry Pi)
- Servo and ESC control using **pigpio** for smoother PWM
- Socket server for remote throttle and steering commands
- Can move forward, backward, and any combination with left or right
- Connection timeout safety stop
- Command queue for reducing input lag
- Ease of acceleration for servo and ESC
- 720p video stream using a Flask server
- Safety features for input loss and runaway prevention

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
For full setup and wiring, see the [D-14 Client and Host Diagram Section](D-14/Diagrams-Concepts)  *(Coming soon)*

---

## Known Issues

- `Emergency Disconnect` does not work properly.
- Sometimes multiple commands are sent at once.
- The servo needs to be recalibrated.

---

## Roadmap (v1.1 and Beyond)

- [ ] Parking brake **(Ver 1.1)**
- [x] Hardware modifications to cool the Raspberry Pi
- [x] Path detection (opencv) **(Ver 1.1)**
- [ ] Reduced input lag **(Ver 1.1)**
- [ ] Steering and max throttle tuning on the `settings` page
- [ ] Error popups for critical issues