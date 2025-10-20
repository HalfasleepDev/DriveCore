![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![PySide6](https://img.shields.io/badge/GUI-PySide6-orange)
![Flask](https://img.shields.io/badge/Web-Flask-red)
![AI-Ready](https://img.shields.io/badge/AI-Ready-yellow)

# DriveCore – Modular RC Vehicle Control & AI Framework

DriveCore is a modular and scalable platform designed for controlling RC vehicles, with the potential for AI-powered autonomy. Built using Python, OpenCV, and a Raspberry Pi, DriveCore serves as the foundation for both manual and automated vehicle operation, integrating computer vision, sensor fusion, and remote control capabilities.

## Key Features

- Python-Based Framework – Simplifies development and customization.
- Raspberry Pi Integration – Acts as the central computing unit for real-time processing.
- OpenCV for Computer Vision – Enables object detection, lane tracking, and obstacle avoidance.
- Wireless Control – Supports remote driving via web interfaces or game controllers.
- AI & Machine Learning Ready – Designed to incorporate neural networks and autonomous decision-making in future updates.
- Scalable & Modular – Extendable with LiDAR, GPS, additional sensors for advanced navigation.
- Client Application – Built with PySide6 for a user-friendly interface.

## Future Enhancements

- Reinforcement Learning for self-driving AI
- Edge Computing with TensorFlow Lite
- Advanced SLAM (Simultaneous Localization and Mapping)

DriveCore is built for enthusiasts, researchers, and developers looking to expirement with AI-driven RC control. Whether experimenting with computer vision, autonomous navigation, or real-time control, DriveCore provides the flexibility to explore multiple concepts.

---

# Current Version: 1.3.0 - *"Control System & Communication Layer"* for D-14

![Ver 1.3.0 Demo](D-14/Diagrams-Concepts/Ver-1-3-0/DemoV1-3-0.gif)

- [D-14 Client and Host Section](D-14/README.md)

<details>

<summary>Important Notes</summary>

- The program becomes unstable after multiple disconnects and reconnects.

</details>

---

## Vehicles:

- [D-14](D-14/README.md)
- [Probe-33](Probe-33/README.md) *(New vehicle in progress..)*

---

## Getting Started

### Clone the Repository
`git clone https://github.com/HalfasleepDev/DriveCore.git cd DriveCore`


### Install Dependencies
`pip install -r requirements.txt`
- For host and client.


### Configure RC Car Control Server
- Create `DriveCore` folder on the Raspberry Pi.
- Create a python venv.
- Copy `drive-core-host.sh`, `driveCoreHost.py`, `driveCoreNetwork.py`,`coreFunctions.py`, `settings.json`, and `udpHostProtocols.py` to the raspberry pi's folder called DriveCore.

### Run the RC Car Control Server
`cd Drivecore`
`sudo ./drive-core-host.sh`
- Wait a minute or so for the system to start broadcasting.

### Launch the Client Application
`python3 DriveCore/D-14/Client-Side/client-app/main.py`
- Log into the Control Server using the configured credentials set in `DriveCore/settings.json` on the Raspberry pi.

---

## System Requirements

- Raspberry Pi 4 or later (2+ gb of ram)
- Python 3.7+
- PySide6 for the client application
- OpenCV for computer vision processing
- `pigpio` daemon running

---

## Tests

**To run unit tests for DriveCore:**
`DriveCore/D-14/pytest-tests/`  **TBD**

**OpenCV testing section:**
[OpenCv General Testing (D-14)](D-14/Client-Side/openCV-testing/README.md)

**GUI Prototype section:**
[GUI General Prototypes (D-14)](D-14/Client-Side/ui-prototypes/README.md)

---

## Next Big Feature - *"Mapping Engine"*

The next big feature for the DriveCore project will be a new mapping engine.
This system will convert monocular depth information into a system for calculating obstacles and provide:
- Navigation
- Advanced Cruise Control
- Object classification

## License

This project is licensed under the MIT License.

## Links

- Project Wiki: [DriveCore Docs](https://github.com/HalfasleepDev/DriveCore/wiki) **TBD**
- GitHub Repository: [DriveCore](https://github.com/HalfasleepDev/DriveCore)

DriveCore is designed to provide a scalable platform for remote-controlled and autonomous vehicle operation. Whether for research, experimentation, or hobbyist projects, DriveCore offers a solid foundation for developing intelligent RC vehicles.