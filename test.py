# from pynput import keyboard

# ctrl_held = False

# def on_press(key):
#     global ctrl_held
#     try:
#         if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
#             ctrl_held = True
#         elif key.char.lower() == 'm' and ctrl_held:
#             print("Ctrl + M detected!")
#     except AttributeError:
#         pass

# def on_release(key):
#     global ctrl_held
#     if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
#         ctrl_held = False

# listener = keyboard.Listener(on_press=on_press, on_release=on_release)
# listener.start()

# # Keep the script alive
# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     print("Stopped by user")

# def on_press(key):
#     print(f"Pressed: {key}")

#note to myself : previous one failed xoxo
# import keyboard

# def listen_hotkey():
#     print("Listening for Ctrl + M...")

#     keyboard.add_hotkey('ctrl+m', lambda: print("Ctrl + M detected!"))

#     keyboard.wait('esc')  

# listen_hotkey()

# import winreg

# key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
# with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
#     desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
# print(desktop_path)  # this will be TrashDesk

# import os, winreg

# key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
# with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
#     desktop_path, _ = winreg.QueryValueEx(key, "Desktop")

# desktop_path = os.path.expandvars(desktop_path)  # resolves %USERPROFILE%
# print(desktop_path)  # C:\Users\Asahi\TrashDesk

# import winreg
# from pathlib import Path

# music_path = Path(r"C:\Users\Asahi\MyCustomMusic") 
# music_path_str = str(music_path)

# reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"

# with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
#     winreg.SetValueEx(key, "My Music", 0, winreg.REG_EXPAND_SZ, music_path_str)

# print(f"Windows Music folder updated to: {music_path_str}")


# import winreg
# from pathlib import Path
# import os

# # Default path for your Music folder
# default_music_path = str(Path(os.environ["USERPROFILE"]) / "Music")

# # Registry location
# reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"

# # Open and update the key
# with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
#     winreg.SetValueEx(key, "My Music", 0, winreg.REG_EXPAND_SZ, default_music_path)

# print(f"Music folder restored to: {default_music_path}")

# pyinstaller --noconfirm --onedir --windowed --name MiyaDesktop --icon assets/miya.ico --add-data "assets;assets" --add-data "models;models" --add-data "demon_runtime;demon_runtime" --collect-submodules core --collect-submodules models --collect-submodules ui --collect-all PyQt6 --collect-all vosk main.py

# pyinstaller --noconfirm --onedir --windowed --name MiyaDesktop  --icon assets/miya.ico --add-data "assets;assets" --add-data "demon_runtime;demon_runtime" --collect-submodules core --collect-submodules ui --collect-all PyQt6 main.py