import os
import json

DEFAULT_SETTINGS = {
    "min_duty_servo": 900,
    "max_duty_servo": 2100,
    "neutral_duty_servo": 1500,
    "min_duty_esc": 1310,
    "max_duty_esc": 1750,
    "neutral_duty_esc": 1500,
    "brake_esc": 1470,
    "username": "D-14",                 #* <--- Default username
    "password": "driveCore"             #* <--- Default password
}

def load_settings(SETTINGS_FILE):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                loaded = json.load(f)
                return {**DEFAULT_SETTINGS, **loaded}
            except json.JSONDecodeError:
                print("[DEBUG] Invalid settings file. Loading defaults.")
    return DEFAULT_SETTINGS.copy()
 
def save_settings(new_settings, SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f, indent=4)