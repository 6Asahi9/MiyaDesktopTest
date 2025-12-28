from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QScrollArea
)
from pathlib import Path
import json
from core.path import SETTINGS_JSON

# ----------------- JSON helpers -----------------
def load_settings():
    if SETTINGS_JSON.exists():
        with open(SETTINGS_JSON, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_JSON, "w") as f:
        json.dump(settings, f, indent=4)

# ----------------- App Manager page -----------------
def create_app_manager_page(stack):
    page = QWidget()
    layout = QVBoxLayout(page)

    # Top bar with Add button
    top_bar = QHBoxLayout()
    add_btn = QPushButton("Add")
    back_btn = QPushButton("Back")
    add_btn.setFixedSize(120, 50)
    back_btn.setFixedSize(120, 50)

    top_bar.addWidget(add_btn)
    top_bar.addStretch()
    top_bar.addWidget(back_btn)
    layout.addLayout(top_bar)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    settings = load_settings()
    saved_apps = settings.get("added_apps", [])
    for path in saved_apps:
        lbl = QLabel(path)
        content_layout.addWidget(lbl)

    def add_file():
        files, _ = QFileDialog.getOpenFileNames(page, "Select EXE files", "", "Executables (*.exe)")
        for f in files:
            if "Windows" in f or "Program Files" in f:
                continue
            if f not in saved_apps:
                saved_apps.append(f)
                lbl = QLabel(f)
                content_layout.addWidget(lbl)
        settings["added_apps"] = saved_apps
        save_settings(settings)

    add_btn.clicked.connect(add_file)

    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))

    return page

# ----------------- Legacy helpers -----------------
def switch_to_app_manager(stack):
    print("Opening App Manager...")
    stack.setCurrentIndex(1)

def switch_to_main(stack):
    print("Returning to Main Page")
    stack.setCurrentIndex(0)

# -------------------------------------------------------------------------------------------------------------