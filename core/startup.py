import os
import sys
import winreg  
import json
from core.path import SETTINGS_JSON

APP_NAME = "MiyaDesktop"
def load_startup_setting() -> bool:
    if not SETTINGS_JSON.exists():
        return False

    with open(SETTINGS_JSON, "r") as f:
        data = json.load(f)

    return data.get("run_at_startup", False)

def toggle_startup(is_on: bool):
    save_startup_setting(is_on)
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = os.path.abspath(sys.argv[0])

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_WRITE
    )

    if is_on:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
        print("Startup on")
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
            print("Startup off")
        except FileNotFoundError:
            pass

    winreg.CloseKey(key)

def save_startup_setting(is_on: bool):
    data = {}

    if SETTINGS_JSON.exists():
        with open(SETTINGS_JSON, "r") as f:
            data = json.load(f)

    data["run_at_startup"] = is_on

    with open(SETTINGS_JSON, "w") as f:
        json.dump(data, f, indent=2)
