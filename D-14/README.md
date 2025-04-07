# WPL D-14 
![Modified WPL D-14 Host](D-14-Mod.jpg)

## Currently running Ver 1.1

---

## Features:
### Host:
- Can move forward, backward, and any combination with left or right
- Connection timeout safety stop
- Command queue for reducing input lag
- Ease of acceleration for servo and esc
- 720p video stream using a flask server

### Client:
- Uses pyside6 UI library
- Store recently connected IPs in history
- Video stream
- Inputs using `W` `A` `S` `D`
- On exit, the host "should" stop running
- OpenCV HUD & settings

### UI Demo (Ver 1.1):
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

---

## Hardware requirements:
- Raspberry pi 4
- 8mp raspberry pi cam
- 20A esc
- battery pack
- wifi extender
- led kit (optional)

---

## Current issues:
- [ ] `Emergency Disconnect` does not work properly.
- [x] Sometimes multiple commands are sent at once.
- [ ] The servo needs to be re-calibrated.
- [ ] The automatic brake creates an info backup

---

## Planned Features:

- [ ] Steering and max throttle tunning on the `settings` page
- [ ] Client-Host communication & verification
- [ ] Drive model *(HOST)*
- [ ] Acceleration curves *(CLIENT)*
- [ ] UI design consistency
- [ ] Upgrade `settings` page
- [ ] Application packaging
- [ ] Vehicle status info *(CLIENT)*

<details>

<summary>Completed Features</summary>

- [x] Parking brake **(Ver 1.1)**
- [x] Hardware modifications to cool the raspberry pi
- [X] Upgraded to Raspberry pi 4 (4gb)
- [x] Path detection (opencv) **(Ver 1.1)**
- [x] Reduced input lag **(Ver 1.1)**
- [x] Error popups for critical issues **(Ver 1.1)**

</details>

---

## Client Tested on Arch Linux(Wayland)