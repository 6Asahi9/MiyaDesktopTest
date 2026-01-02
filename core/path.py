import json
from pathlib import Path
import sys
import winreg
import os

def get_windows_documents_folder():
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
        documents_path, _ = winreg.QueryValueEx(key, "Personal")
    documents_path = os.path.expandvars(documents_path)
    return Path(documents_path)

DOCUMENTS_PATH = get_windows_documents_folder()
MIYA_DESKTOP_PATH = DOCUMENTS_PATH / "MiyaDesktop"
MIYA_CONFIG_PATH = MIYA_DESKTOP_PATH / "config"
MIYA_CONFIG_PATH.mkdir(parents=True, exist_ok=True)

def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]

BASE_PATH = get_base_path()
# CONFIG_PATH = BASE_PATH / "config"
CONFIG_PATH = MIYA_CONFIG_PATH
ASSETS_PATH = BASE_PATH / "assets"
SETTINGS_JSON = CONFIG_PATH / "settings.json"

if not SETTINGS_JSON.exists():
    SETTINGS_JSON.write_text("{}", encoding="utf-8")
# MUSIC_PATH = BASE_PATH / "music"
DEFAULT_AVATAR = ASSETS_PATH / "gif/placeholder_miya.gif"
PLAYER_PATH = ASSETS_PATH / "gif/SimpsonsSticker.gif"


def get_avatar_path():
    if SETTINGS_JSON.exists():
        try:
            data = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
            custom = data.get("custom_avatar_path")
            if custom and Path(custom).exists():
                return Path(custom)
        except Exception:
            pass
    return DEFAULT_AVATAR

def get_windows_music_folder():
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
        music_path, _ = winreg.QueryValueEx(key, "My Music")
    music_path = os.path.expandvars(music_path)
    return Path(music_path)
MUSIC_PATH = get_windows_music_folder()