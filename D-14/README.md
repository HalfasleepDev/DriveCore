# WPL D-14 
![Modified WPL D-14 Host](D-14-Mod.jpg)

## Currently running Ver 1.0

## Features:
### Host:
- Can move forward, backwards, and any combonation with left or right
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

### UI Demo (Ver 1.0):
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

## Hardware requirements:
- Raspberry pi 4
- 8mp raspberry pi cam
- 20A esc
- battery pack
- wifi extender
- led kit (optional)

## Current issues:
- [ ] `Emergency Disconnect` does not work properly.
- [x] Sometimes multiple commands are sent at once.
- [ ] The servo needs to be re-calibrated.

## Planned Features:
- [ ] Parking brake **(Ver 1.1)**
- [x] Hardware modifications to cool the raspberry pi
- [x] Path detection (opencv) **(Ver 1.1)**
- [ ] Reduced input lag **(Ver 1.1)**
- [ ] Steering and max throttle tunning on the `settings` page
- [ ] Error popups for critical issues

## Client Tested on Arch Linux(Wayland)