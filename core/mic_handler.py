import speech_recognition as sr
import os
from core.chatgpt_api import send_to_chatgpt
from vosk import Model, KaldiRecognizer
import json
import sys
import wave
import urllib.request
from core.path import CONFIG_PATH

# UI hook (chat bubble)
from core.avatar_toggle import show_chat_bubble

SETTINGS_JSON = CONFIG_PATH / "settings.json"
recognizer = sr.Recognizer()

def internet_available():
    try:
        urllib.request.urlopen("http://google.com", timeout=2)
        return True
    except:
        return False

VOSK_MODEL_PATH = os.path.join("models", "vosk")
vosk_model = None
if os.path.exists(VOSK_MODEL_PATH):
    vosk_model = Model(VOSK_MODEL_PATH)

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
    use_google = False
    model_name = "(Vosk)"
    print(f"Miya is now listening... {model_name}")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print(f"⏱️ Miya is ignoring you. {model_name}")
            show_chat_bubble("Miya is ignoring you 😿")
            return

    # if use_google:
    #     try:
    #         user_text = recognizer.recognize_google(audio)
    #     except sr.UnknownValueError:
    #         print(f"Miya heard nothing understandable. {model_name}")
    #         show_chat_bubble("Miya heard nothing understandable")
    #         return
    #     except sr.RequestError:
    #         print(f"Miya is ignoring you. {model_name}")
    #         show_chat_bubble("Miya is ignoring you")
    #         return
    #
    #     user_text = user_text.strip()
    #     print(f"You said: \"{user_text}\" {model_name}")
    #
    #     if not user_text:
    #         print(f"Miya is ignoring you. {model_name}")
    #         show_chat_bubble("Miya is ignoring you")
    #         return
    #
    #     if user_text.lower().startswith("open"):
    #         print(f"Command detected! {model_name}")
    #         print(f"Handling OPEN command: {user_text} {model_name}")
    #         show_chat_bubble(user_text)
    #     else:
    #         print(f"Conversation detected — sending to ChatGPT... {model_name}")
    #         response = send_to_chatgpt(user_text)
    #         show_chat_bubble(response)

    try:
        wav_path = "temp_audio.wav"
        with open(wav_path, "wb") as f:
            f.write(audio.get_wav_data())

        wf = wave.open(wav_path, "rb")
        rec = KaldiRecognizer(vosk_model, wf.getframerate())
        rec.SetWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                results.append(res.get("text", ""))

        results.append(json.loads(rec.FinalResult()).get("text", ""))
        user_text = " ".join(results).strip()
        wf.close()
        os.remove(wav_path)

    except Exception as e:
        print(f"Miya flicked her tail at you. (Vosk error: {e}) {model_name}")
        show_chat_bubble("Miya flicked her tail at you 😾")
        return

    if not user_text:
        print(f"Miya flicked her tail at you. {model_name}")
        show_chat_bubble("Miya flicked her tail at you 😾")
        return

    print(f"You said (offline): \"{user_text}\" {model_name}")
    if user_text.lower().startswith("open"):
        app_name = user_text[4:].strip()  
        show_chat_bubble(f"meow opening {app_name} 😼")

        path = find_app_path(app_name)
        if path:
            open_path(path)
        else:
            show_chat_bubble(f"I don't know {app_name} 🙄")

    else:
        response = send_to_chatgpt(user_text)
        show_chat_bubble(response)
