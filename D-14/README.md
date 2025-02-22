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

## Hardware requirements:
- Raspberry pi A+
- 8mp raspberry pi cam
- 20A esc
- battery pack
- wifi extender
- led kit (optional)

## Current issues:
- Raspberry pi stutters due to hardware limitations
- `Emergency Disconnect` does not work properly
- Sometimes multiple commands are sent at once
- The servo needs to be re-calibrated

## Planned Features:
- Parking brake
- Hardware modifications to cool the raspberry pi

## Client Tested on Arch Linux(Wayland)