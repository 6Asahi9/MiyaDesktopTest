import speech_recognition as sr
import os
import json
import wave
import urllib.request

from core.chatgpt_api import send_to_chatgpt
from core.path import CONFIG_PATH, BASE_PATH
from core.avatar_toggle import show_chat_bubble

# --- VOSK (FULLY DISABLED) --------------------------------
# from vosk import Model, KaldiRecognizer
# VOSK_MODEL_PATH = BASE_PATH / "models" / "vosk"
# vosk_model = None
# if VOSK_MODEL_PATH.exists():
#     vosk_model = Model(str(VOSK_MODEL_PATH))
# else:
#     print("Vosk model not found:", VOSK_MODEL_PATH)
# -----------------------------------------------------------

SETTINGS_JSON = CONFIG_PATH / "settings.json"
recognizer = sr.Recognizer()

def internet_available():
    try:
        urllib.request.urlopen("http://google.com", timeout=2)
        return True
    except:
        return False

def load_settings():
    try:
        with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def normalize(text):
    return "".join(
        c for c in text.lower().strip()
        if c.isalnum() or c.isspace()
    )

def find_app_path(spoken_name):
    settings = load_settings()
    spoken_name = normalize(spoken_name)

    for app in settings.get("added_apps", []):
        if normalize(app.get("name", "")) == spoken_name:
            return app.get("path")

    return None

def open_path(path):
    os.startfile(path)

def activate_miya_listener():
    use_google = True
    model_name = "(Google)"

    print(f"Miya is now listening... {model_name}")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print(f"⏱️ Miya is ignoring you. {model_name}")
            show_chat_bubble("Miya is ignoring you :(")
            return

    try:
        user_text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print(f"Miya heard nothing understandable. {model_name}")
        show_chat_bubble("Miya heard nothing understandable")
        return
    except sr.RequestError:
        print(f"Miya is ignoring you. {model_name}")
        show_chat_bubble("Miya is ignoring you")
        return

    user_text = user_text.strip()
    print(f'You said: "{user_text}" {model_name}')

    if not user_text:
        print(f"Miya is ignoring you. {model_name}")
        show_chat_bubble("Miya is ignoring you")
        return

    if user_text.lower().startswith("open"):
        app_name = user_text[4:].strip()

        show_chat_bubble(f"meow opening {app_name} :3")

        path = find_app_path(app_name)
        if path:
            open_path(path)
        else:
            show_chat_bubble(f"I don't know {app_name} >:3")

        return   

    print(f"Conversation detected — sending to ChatGPT... {model_name}")
    response = send_to_chatgpt(user_text)
    show_chat_bubble(response)
