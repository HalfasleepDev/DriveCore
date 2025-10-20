# WPL D-14 
![Modified WPL D-14 Host](D-14-Mod.jpg)

## Currently running Ver 1.3.0 - *"Control System & Communication Layer"*

---

![Ver 1.3.0 Demo](Diagrams-Concepts/Ver-1-3-0/DemoV1-3-0.gif)

---
## Features:
### Host:
- Can move forward, backward, and any combination with left or right.
- Connection timeout safety stop/disconnecct.
- Command ack for latency tracking.
- Acceleration curves for esc.
- Servo return to center for natural drive control. 
- 720p video stream using a UDP protocol.
- Network broadcast system.
- Client communication.
- Vehicle settings.

### Client:
- Uses pyside6 UI library.
- Store most recent vehicle username and password in history.
- App settings
- Video stream.
- Inputs using `W` `A` `S` `D`.
- On exit, the host "should" stop running.
- OpenCV HUD & settings.
- Vehicle inspired UI.
- Vehicle tunning system. 
- System logging for debugging.

### UI Demo (Ver 1.3.0):
<details>

<summary>Home Page</summary>

![Home Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/HomePageV1-3-0.gif)

</details>

<details>

<summary>Drive Page</summary>

![Drive Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/DrivePageV1-3-0.gif)

</details>

<details>

<summary>Log Page</summary>

![Log Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/LogPageV1-3-0.gif)

</details>

<details>

<summary>Settings Page</summary>

![Settings Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/SettingsPageV1-3-0.gif)

</details>

<details>

<summary>OpenCV Overlay</summary>

![OpenCV Overlay Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/CvOverlayV1-3-0.gif)

</details>

---

### Change Log

<details>

<summary>Ver 1.0</summary>

#### Ver 1.0

##### Host:
- Can move forward, backward, and any combination with left or right.
- Connection timeout safety stop.
- Command queue for reducing input lag.
- Ease of acceleration for servo and esc.
- 720p video stream using a flask server.

##### Client
- Uses pyside6 UI library.
- Store recently connected IPs in history.
- Video stream.
- Inputs using `W` `A` `S` `D` `SPACE BAR`.
- On exit, the host "should" stop running.

##### UI Demo (Ver 1.0):
<details>

<summary>Home Page</summary>

![Home Page Ver 1.0](Diagrams-Concepts/Ver-1-0/HomePageV1-0.png)

</details>

<details>

<summary>Drive Page</summary>

![Drive Page Ver 1.0](Diagrams-Concepts/Ver-1-0/DrivePageV1-0.png)

</details>

<details>

<summary>Settings Page</summary>

![Settings Page Ver 1.0](Diagrams-Concepts/Ver-1-0/SettingsPageV1-0.png)

</details>


---

</details>

<details>

<summary>Ver 1.1</summary>

#### Ver 1.1

##### Host:
- Switched to UDP communication.
- Added a `"BRAKE"` command.
- Basic command spike detection algorithm .
- `"DISCONNECT"` command *potential fix*.

##### Client
- `SPACE BAR` input added for brake.
- [openCV-testing iteration 04](Client-Side/openCV-testing/README.md) implemented & refactored.
- OpenCv settings menu added with overlay toggles.
- Added rough obstacle collision warning/automatic brake.
- Added error popups.
- Added loading cursor for host connection.
- Removed *debug* print statements.

##### UI Demo (Ver 1.1):
<details>

<summary>Home Page</summary>

![Home Page Ver 1.1](Diagrams-Concepts/Ver-1-1/HomePageV1-1.png)

</details>

<details>

<summary>Drive Page</summary>

![Drive Page Ver 1.1](Diagrams-Concepts/Ver-1-1/DrivePageV1-1.png)

</details>

<details>

<summary>Settings Page</summary>

![Settings Page Ver 1.1](Diagrams-Concepts/Ver-1-1/SettingsPageV1-1.png)

</details>

<details>

<summary>OpenCV Overlay</summary>

![OpenCV Overlay Ver 1.1](Diagrams-Concepts/Ver-1-1/CvOverlayV1-1.png)

</details>

---

</details>

<details>

<summary>Ver 1.2</summary>

#### Ver 1.2 - "Control Tuning & UI Foundations"

##### Host:
- No new changes.

##### Client
- Added multiple new UI Elements demonstrated in [ui-prototypes Ver 1.2](Client-Side/ui-prototypes/README.md).
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

##### UI Demo (Ver 1.2):
<details>

<summary>Home Page</summary>

![Home Page Ver 1.2](Diagrams-Concepts/Ver-1-2/HomePageV1-2.gif)

</details>

<details>

<summary>Drive Page</summary>

![Drive Page Ver 1.2](Diagrams-Concepts/Ver-1-2/DrivePageV1-2.gif)

</details>

<details>

<summary>Log Page</summary>

![Log Page Ver 1.2](Diagrams-Concepts/Ver-1-2/LogPageV1-2.gif)

</details>

<details>

<summary>Settings Page</summary>

![Settings Page Ver 1.2](Diagrams-Concepts/Ver-1-2/SettingsPageV1-2.gif)

</details>

<details>

<summary>OpenCV Overlay</summary>

![OpenCV Overlay Ver 1.2](Diagrams-Concepts/Ver-1-2/CvOverlayV1-2.gif)

</details>

---

</details>

<details>

<summary>Ver 1.3.0</summary>

#### Ver 1.3.0 - "Control System & Communication Layer"

##### Host:
- **New** network manager system.
- **New** broadcast and verification for easier connection on wireless networks.
- **New** UDP video stream.
- **New** protocols.
- **New** Settings implementation. 
- **New** floodlight status implementation.

##### Client
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

##### UI Demo (Ver 1.3.0):
<details>

<summary>Home Page</summary>

![Home Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/HomePageV1-3-0.gif)

</details>

<details>

<summary>Drive Page</summary>

![Drive Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/DrivePageV1-3-0.gif)

</details>

<details>

<summary>Log Page</summary>

![Log Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/LogPageV1-3-0.gif)

</details>

<details>

<summary>Settings Page</summary>

![Settings Page Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/SettingsPageV1-3-0.gif)

</details>

<details>

<summary>OpenCV Overlay</summary>

![OpenCV Overlay Ver 1.3.0](Diagrams-Concepts/Ver-1-3-0/CvOverlayV1-3-0.gif)

</details>

---

</details>

---

## Hardware requirements:
- WPL D14 Suzuki Carry - RTR
- Raspberry pi 4
- 8mp raspberry pi cam
- 30A esc
- battery pack
- wifi extender
- led kit (optional)
- Follow the [Electronic Diagram](Diagrams-Concepts/D-14-Electronic-Diagram.pdf)
    - *Flood light guide comming soon*

---

## Current issues:
- [ ] `Emergency Disconnect` does not work properly.
    - Should send a disconnect command to vehicle.
- [ ] The Re-Connect system is unreliable.
    - Threading issue.
- [x] Floodlights are faulty
    - Wiring issue.

---

## Version Roadmap **(Upcomming)**:
<details>

<summary>Version 1.3.5</summary>

### Version 1.3.1 - 1.3.5 – “UI Tune-up”
 - [ ] Refresh the UI colours
 - [ ] Alter the widget positions
 ...

 </details>

<details>

<summary>Version 1.4.0</summary>

### Version 1.4 – “Intelligent Perception Update”
 - [ ] Integrate monoculear depth estimation for floor & obstacle awareness.
 - [ ] Use depth to improve obstacle detection & safety logic.
 - [ ] Mapping Engine
 - [ ] Vehicle imu intergration.
 - [x] Vehicle flood light upgrade.
 - [ ] Steering input via Mapping Engine
 - [ ] DriveCore OS
 ...

 </details>

<details>

<summary>Version 1.5</summary>

### Version 1.5 – “Autonomy Foundations”
- [ ] Add Kalman-filtered path following (auto-drive down a detected path/auto cruise control)
- [ ] Add basic AI behavior tree or rule-based autonomy modes
...

</details>

### Stretch Features(v1.5+) *(TBD)*
- [ ] UI overhall *(Post v1.5)*
- [ ] Raspberry pi based autonomy <-- *If the raspberry pi is too weak, I'll make a new vehicle*
    - [ ] Map tracking
    - [ ] Route mapping
    - [ ] Waypoint Navagation *(TBD)*
    - [ ] Return to Home

<details>

<summary>Completed Features</summary>

- [x] Parking brake **(Ver 1.1)**
- [x] Hardware modifications to cool the raspberry pi
- [X] Upgraded to Raspberry pi 4 (4gb)
- [x] Path detection (opencv) **(Ver 1.1)**
- [x] Reduced input lag **(Ver 1.1)**
- [x] Error popups for critical issues **(Ver 1.1)**

- [x] Framework for steering and max throttle tuning on the `settings` page **(Ver 1.2)**
- [X] UI design consistency **(Ver 1.2)**
- [x] Add UI element foundations for *Ver 1.3* **(Ver 1.2)**
- [x] Upgrade `settings` page **(Ver 1.2)**
- [x] Created the front-end for the `log` page **(Ver 1.2)**

- [x] Drive model *(HOST)* **(Ver 1.3.0)**
- [x] Client-Host communication & verification **(Ver 1.3.0)**
- [x] Acceleration curves *(CLIENT)* **(Ver 1.3.0)**
- [x] Vehicle status info *(CLIENT)* **(Ver 1.3.0)**
- [x] Restarting connection **(Ver 1.3.0)**
- [x] Error messages **(Ver 1.3.0)**
- [x] Client-Host logging **(Ver 1.3.0)**
</details>

---

<details>

<summary>UI Concepts</summary>

- [UI Preview V 1.0](Diagrams-Concepts/DriveCore-Ver-1-1.pdf)
- [UI Preview V1.2](Diagrams-Concepts/DriveCore-Ver-1-2.pdf)

</details>

---

## Client Tested on Arch Linux(Wayland)