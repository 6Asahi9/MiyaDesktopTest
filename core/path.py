import json
from pathlib import Path
import sys

def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]

BASE_PATH = get_base_path()

CONFIG_PATH = BASE_PATH / "config"
ASSETS_PATH = BASE_PATH / "assets"
SETTINGS_JSON = CONFIG_PATH / "settings.json"
MUSIC_PATH = BASE_PATH / "music"
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
