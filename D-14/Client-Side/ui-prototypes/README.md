# General GUI Prototypes 

## GUI (v1.2)
---
### Home Page
<details>

<summary>General Logs GUI (Connection Logs)</summary>

#### Features
- A General Logs Widget that can be used to display specific logs
- Scrollable widget
- Clear Button for clearing logs

#### How will this be applied?
- It will be added to the Home Page Next to the Ip input feilds.

![General Logs Vis](ver-1-2/generalLogGuiVis.png)

[General Logs Code](ver-1-2/generalLogGuiVis.py)


</details>

<details>

<summary>Project Info GUI</summary>

#### Features
- Provides:
    - A project description
    - A button that links to the github
    - Shows the most recent release

#### How will this be applied?
- It will be added to the Home Page to replace the about section.

![Project Info Vis](ver-1-2/projectInfoGuiVis.png)

[Project Info Code](ver-1-2/projectInfoGuiVis.py)


</details>

### Drive Page
<details>

<summary>Infotainment GUI</summary>

#### Features
- 'P' 'R' 'N' 'D' Visualization
- Alert-Info Widget
- Throttle, Steering, Brake, and Neutral Visualization

#### How will this be applied?
- Widgets will be moved and oriented where the `Keybindings` are.
- `Keybindings` will be moved and minimized vertically to the bottom.

![Vehicle Control Vis](ver-1-2/vehicleControlGuiVis.png)

[Vehicle Control Code](ver-1-2/vehicleControlGuiVis.py)

</details>

<details>

<summary>Speedometer GUI</summary>

#### Features
- Customizable µs range
- Smooth animation
- Forward and Reverse value Visualization

#### How will this be applied?
- It will replace the Throttle Visualization from [Infotainment GUI](ver-1-2/vehicleControlGuiVis.py)

![Speedometer Vis](ver-1-2/speedometerGuiVis.png)

[Speedometer Code](ver-1-2/speedometerGuiVis.py)


</details>

<details>

<summary>Steer Angle GUI</summary>

#### Features
- Customizable µs range
- Smooth animation
- Curve Path Visualization

#### How will this be applied?
- It will replace the Steering Visualization from [Infotainment GUI](ver-1-2/vehicleControlGuiVis.py)

![Steer Angle Vis](ver-1-2/steerAngleGuiVis.png)

[Steer Angle Code](ver-1-2/steerAngleGuiVis.py)


</details>

<details>

<summary>PRND Selector GUI</summary>

#### Features
- An animated PRND selector
- Dynamic animation

#### How will this be applied?
- It will replace the PRND Visualization from [Infotainment GUI](ver-1-2/vehicleControlGuiVis.py)

![PRND Selector Vis](ver-1-2/prndGuiVis.png)

[PRND Selector Code](ver-1-2/prndGuiVis.py)


</details>

<details>

<summary>General Logs GUI (Alert Logs)</summary>

#### Features
- A General Logs Widget that can be used to display specific logs
- Scrollable widget
- Clear Button for clearing logs

#### How will this be applied?
- It will replace the Alert-Info widget from [Infotainment GUI](ver-1-2/vehicleControlGuiVis.py)

![General Logs Vis](ver-1-2/generalLogGuiVis.png)

[General Logs Code](ver-1-2/generalLogGuiVis.py)


</details>

<details>

<summary>Alert Assist GUI</summary>

#### Features
- A red flashing alert to notify an issue
- A button toggle for drive assist (obstacle avoidance)

#### How will this be applied?
- It will be on the bottom right of the Infotainment widgets.

![Alert Assist Vis](ver-1-2/alertAssistGuiVis.png)

[Alert Assist Code](ver-1-2/alertAssistGuiVis.py)


</details>

### Log Page

<details>

<summary>System Log Page GUI</summary>

#### Features
- Shows system logs of the current session
- Different tags for each log 
- Save, clear, or load different logs
- Keyword search area

#### How will this be applied?
- It will be added as a new Log page.

![System Log Page Vis](ver-1-2/systemLogPageGuiVis.png)

[System Log Page Code](ver-1-2/systemLogPageGuiVis.py)


</details>

### Settings Page

<details>

<summary>Vehicle Calibration GUI</summary>

#### Features
- A settings section to set and tune esc and servo µs values.
- Servo values can be adjusted continuously to find the center alignment
- Adjust port values

#### How will this be applied?
- It will be a new settings page section.

![Vehicle Calibration Vis](ver-1-2/vehicleCalibrationGuiVis.png)

[Vehicle Calibration Code](ver-1-2/vehicleCalibrationGuiVis.py)


</details>

<details>

<summary>Settings Description</summary>

#### Features
- A settings section that describes the current settings page.
- Text is in markdown format

#### How will this be applied?
- It will be a new settings page section on the right.

![Settings Description Vis](ver-1-2/settingsDescriptionGuiVis.png)

[Settings Description Code](ver-1-2/settingsDescriptionGuiVis.py)


</details>