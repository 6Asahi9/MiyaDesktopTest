from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QScrollArea, QDialog, QLineEdit,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
import json
from core.path import SETTINGS_JSON
import os
import win32com.client
import winreg
from PyQt6.QtGui import QKeySequence
import shutil

# JSON helpers -----------------------------------------
def load_settings():
    if SETTINGS_JSON.exists():
        with open(SETTINGS_JSON, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data.setdefault("added_apps", [])
    data.setdefault("folder_mode", False)

    return data

def prepare_miya_desktop():
    documents = get_documents_from_registry()
    miya_desktop = documents / "MiyaDesktop" / "Desktop"
    miya_desktop.mkdir(parents=True, exist_ok=True)
    return miya_desktop

def save_settings(settings):
    SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_JSON, "w") as f:
        json.dump(settings, f, indent=4)

def get_desktop_from_registry():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        ) as key:
            value, _ = winreg.QueryValueEx(key, "Desktop")
            return Path(os.path.expandvars(value))
    except Exception:
        return None
    
def get_documents_from_registry():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        ) as key:
            value, _ = winreg.QueryValueEx(key, "Personal")  
            return Path(os.path.expandvars(value))
    except Exception:
        return Path.home() / "Documents"  

def scan_desktop_shortcuts(existing_names):
    shell = win32com.client.Dispatch("WScript.Shell")

    desktop_paths = []

    user_desktop = get_desktop_from_registry()
    if user_desktop and user_desktop.exists():
        desktop_paths.append(user_desktop)

    public_desktop = Path("C:/Users/Public/Desktop")
    if public_desktop.exists():
        desktop_paths.append(public_desktop)

    found_apps = []

    for desktop in desktop_paths:
        for lnk in desktop.glob("*.lnk"):
            try:
                shortcut = shell.CreateShortcut(str(lnk))
                target = shortcut.Targetpath or str(lnk)

                name = lnk.stem

                if name in existing_names:
                    continue

                found_apps.append({
                    "name": name,
                    "path": target
                })

            except Exception:
                continue

    return found_apps

# Add App Dialog ---------------------
class AddAppDialog(QDialog):
    def __init__(self, parent=None, existing_names=None, app_data=None):
        super().__init__(parent)

        self.editing = app_data is not None
        self.setWindowTitle("Edit Application" if self.editing else "Add Application")
        self.setFixedSize(420, 160)

        self.existing_names = existing_names or set()
        self.original_name = app_data["name"] if app_data else None

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Application name")

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path to executable")

        if app_data:
            self.name_input.setText(app_data["name"])
            self.path_input.setText(app_data["path"])

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.name_input)
        layout.addLayout(path_layout)
        layout.addWidget(buttons)

        self.name_input.returnPressed.connect(self.validate_and_accept)
        self.path_input.returnPressed.connect(self.validate_and_accept)

        self._validating = False

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select EXE", "", "Executables (*.exe)"
        )
        if file:
            self.path_input.setText(file)


    def validate_and_accept(self):
        if self._validating:
            return
        self._validating = True
        try:
            name = self.name_input.text().strip()
            path = self.path_input.text().strip()

            if not name or not path:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please enter both a name and a path."
                )
                return

            if name in self.existing_names:
                if not self.editing or name != self.original_name:
                    QMessageBox.warning(
                        self,
                        "Duplicate Name",
                        "An application with this name already exists."
                    )
                    return

            self.accept()
        finally:
            self._validating = False

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "path": self.path_input.text().strip()
        }


# App Manager page --------------------------------------
def create_app_manager_page(stack):
    page = QWidget()
    page.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    layout = QVBoxLayout(page)

    # Top bar
    top_bar = QHBoxLayout()
    add_btn = QPushButton("Add")
    auto_btn = QPushButton("Auto")
    back_btn = QPushButton("Back")
    folder_btn = QPushButton("Folder")
    back_btn.setShortcut(QKeySequence(Qt.Key.Key_Escape))
    add_btn.setFixedSize(120, 50)
    add_btn.setShortcut(QKeySequence("1"))
    add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
    auto_btn.setFixedSize(120, 50)
    folder_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
    folder_btn.setFixedSize(120, 50)
    auto_btn.setShortcut(QKeySequence("2"))
    auto_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
    back_btn.setFixedSize(120, 50)
    back_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)

    top_bar.addWidget(add_btn)
    top_bar.addWidget(auto_btn)
    top_bar.addWidget(folder_btn)
    top_bar.addStretch()
    top_bar.addWidget(back_btn)
    layout.addLayout(top_bar)

    # Scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.addStretch()  

    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    settings = load_settings()
    saved_apps = settings.get("added_apps", [])
    def update_folder_button():
        if settings["folder_mode"]:
            folder_btn.setText("Folder ✅")
        else:
            folder_btn.setText("Folder ❌")

    update_folder_button()

    selected = {"widget": None, "app": None}

    # Row helper -------------------------------------------
    def add_app_row(app):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(6, 6, 6, 6)

        row.setStyleSheet(
            "QWidget { border: 1px solid white; font-size: 15px; border-radius: 8px;}"
        )

        name_lbl = QLabel(app["name"])
        path_lbl = QLabel(app["path"])

        row_layout.addWidget(name_lbl, stretch=3)
        row_layout.addWidget(path_lbl, stretch=1)

        def select_row():
            if selected["widget"]:
                selected["widget"].setStyleSheet(
                    "QWidget { border: 1px solid white; border-radius: 8px; font-size: 15px;}"
                )

            row.setStyleSheet(
                "QWidget { background-color: #00ffff; border: 1px solid black; color: black; font-size: 15px; border-radius: 8px;}"
            )
            selected["widget"] = row
            selected["app"] = app

        def mousePressEvent(event):
            if event.button() == Qt.MouseButton.LeftButton:
                if event.type() == event.Type.MouseButtonDblClick:
                    edit_app(app, row)
                else:
                    select_row()

        row.mousePressEvent = mousePressEvent

        content_layout.insertWidget(content_layout.count() - 1, row)

    # Load saved apps
    for app in saved_apps:
        add_app_row(app)

    # Add logic -------------------------------
    def add_file():
        existing_names = {app["name"] for app in saved_apps}
        dialog = AddAppDialog(page, existing_names=existing_names)

        if dialog.exec():
            data = dialog.get_data()

            saved_apps.append(data)
            settings["added_apps"] = saved_apps
            save_settings(settings)

            add_app_row(data)

    def toggle_folder_mode():
        settings["folder_mode"] = not settings["folder_mode"]
        save_settings(settings)
        update_folder_button()

    def auto_add_apps():
        existing_names = {app["name"] for app in saved_apps}
        new_apps = scan_desktop_shortcuts(existing_names)

        for app in new_apps:
            saved_apps.append(app)
            add_app_row(app)

        if settings.get("folder_mode", False):
            miya_desktop_path = prepare_miya_desktop()
            desktop_path = get_desktop_from_registry()
            if desktop_path and desktop_path.exists():
                for folder in desktop_path.iterdir():
                    if folder.is_dir() and folder.name not in existing_names:
                        target = miya_desktop_path / folder.name
                        try:
                            shutil.copytree(folder, target, dirs_exist_ok=True)
                            folder_app = {
                                "name": f"{folder.name}📁",
                                "path": str(target)
                            }
                            saved_apps.append(folder_app)
                            add_app_row(folder_app)
                            existing_names.add(folder.name) 
                        except Exception as e:
                            print(f"Failed to copy folder {folder}: {e}")

        settings["added_apps"] = saved_apps
        save_settings(settings)

    # Edit logic --------------------------------------------
    def edit_app(app, row_widget):
        existing_names = {a["name"] for a in saved_apps if a is not app}

        dialog = AddAppDialog(
            page,
            existing_names=existing_names,
            app_data=app
        )

        if dialog.exec():
            data = dialog.get_data()

            app["name"] = data["name"]
            app["path"] = data["path"]

            settings["added_apps"] = saved_apps
            save_settings(settings)

            labels = row_widget.findChildren(QLabel)
            labels[0].setText(data["name"])
            labels[1].setText(data["path"])
        
    add_btn.clicked.connect(add_file)
    auto_btn.clicked.connect(auto_add_apps)
    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))
    folder_btn.clicked.connect(toggle_folder_mode)

    # Delete key handling ------------------------------------------
    def keyPressEvent(event):
        if event.key() == Qt.Key.Key_Delete and selected["app"]:
            app = selected["app"]
            widget = selected["widget"]

            if "📁" in app["name"]:
                try:
                    folder_path = Path(app["path"])
                    if folder_path.exists() and folder_path.is_dir():
                        shutil.rmtree(folder_path)
                except Exception as e:
                    print(f"Failed to delete folder {app['name']}: {e}")

            saved_apps.remove(app)
            settings["added_apps"] = saved_apps
            save_settings(settings)

            widget.setParent(None)
            selected["widget"] = None
            selected["app"] = None

    page.keyPressEvent = keyPressEvent

    return page