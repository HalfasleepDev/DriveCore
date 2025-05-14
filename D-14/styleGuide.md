# Python Codebase Style Guide

This guide defines the structure and standards for writing consistent, maintainable, and readable Python code in this project.

---

## 1. File Structure & Header

Each Python file should start with a module docstring:

```python
"""
file_name.py

Short description of the module's purpose.

Author: Your Name
Created: DD-MM-YYYY
"""
```

---

## 2. Section Headers & Organization

Use section headers to clearly mark logical code blocks:

```python
# === Imports ===
# === Constants ===
# === Class Definitions ===
# === Helper Functions ===
# === Main Execution ===
```

Optionally, use IDE-friendly region markers:

```python
# region Data Loading
# ... your code ...
# endregion
```

---

## 3. Function Style

Follow Google-style docstrings:

```python
def calculate_area(radius: float) -> float:
    """
    Calculates the area of a circle.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The area of the circle.
    """
```

**Best Practices:**

* Use full sentences.
* Leave a blank line before and after the function.
* Include types in parameters and return annotations.

---

## 4. Class Style

```python
class SensorManager:
    """
    Manages sensor data and hardware interfaces.

    Attributes:
        sensor_type (str): Type of the sensor.
    """

    def __init__(self, sensor_type: str):
        """
        Initializes the SensorManager.

        Args:
            sensor_type (str): The type of the sensor.
        """
        self.sensor_type = sensor_type
```

---

## 5. Commenting

### Inline Comments

Use to clarify non-obvious logic:

```python
velocity += 0.1  # Account for gravity
```

### Block Comments

Place above code sections to describe logic:

```python
# ------ User Authentication ------
# --- Check if the user is authenticated ---
if not user.is_authenticated:
    return redirect("/login")
```

### ERROR Logging Identification

Use to Identify Potential Error logs & popups

```python
#! --- Error Popup ---
```

---

## 6. TODOs and FIXMEs

```python
# TODO: Implement error recovery logic
# FIXME: Fails if config file is missing
```

---

## 7. Naming Conventions

| Element     | Style        | Example           |
| ----------- | ------------ | ----------------- |
| Variable    | snake\_case  | `image_data`      |
| Function    | camelCase    | `processInput()`  |
| Class       | PascalCase   | `DataLoader`      |
| Constant    | UPPER\_SNAKE | `MAX_BUFFER_SIZE` |
| Module/File | lowercase    | `utils.py`        |

---

## 8. Testing Format

```python
def testSum():
    """Tests the sum function."""
    assert sum([1, 2, 3]) == 6
```

* Use `pytest` format: functions prefixed with `test_`
* Isolate test files into a `tests/` folder when applicable

---

## 9. Main Entry Point

Files intended to be executed directly should include:

```python
if __name__ == "__main__":
    main()
```

---

## 10. Complete Example

```python
"""
motor_control.py

Controls ESC and servo via pigpio.

Author: HalfasleepDev
Created: 2025-05-12
"""

# === Imports ===
import pigpio

# === Constants ===
ESC_PIN = 17
NEUTRAL_PWM = 1500

# === Helper Functions ===
def initPwm(pi, pin, pwm=NEUTRAL_PWM):
    """
    Initializes PWM output on a pin.

    Args:
        pi (pigpio.pi): pigpio instance.
        pin (int): GPIO pin.
        pwm (int): Pulse width in microseconds.
    """
    pi.set_servo_pulsewidth(pin, pwm)

# === Main Execution ===
if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon not running.")
    initPwm(pi, ESC_PIN)
    print("PWM initialized.")
```

---

