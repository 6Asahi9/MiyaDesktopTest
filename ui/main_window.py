from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QStackedLayout, QCheckBox, QFrame, QColorDialog, QSlider, QSpinBox,
    QSizePolicy, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QMovie, QFont, QColor
from core.startup import toggle_startup
from core.theme import toggle_theme, load_theme, save_theme
from core.avatar_toggle import toggle_avatar , load_settings, refresh_floating_miya
from core.demonMode import toggle_demon_mode
from core.fur import switch_fur
import keyboard
from PyQt6.QtWidgets import QDialog, QLineEdit
from core.page_switch import create_app_manager_page
from core.mic_handler import activate_miya_listener
from core.path import get_avatar_path, SETTINGS_JSON
from core.music import create_music_page
from PyQt6.QtGui import QKeySequence, QShortcut
from core.startup import load_startup_setting
from core.neon import load_neon_settings, save_neon_settings
from core.api_dialog import ApiDialog
from core.custom_path import CustomPathDialog
from PyQt6.QtCore import QTimer
import json

class ThemeLabel(QLabel):
    def __init__(self, text, main_window, red=False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.main_window = main_window
        self.red = red
        self.update_color()

    def update_color(self):
        if self.red:
            color = "red"  
        else:
            color = self.main_window.bg_colors["text"]
        self.setStyleSheet(f"color: {color}; font-weight: {'bold' if self.red else 'normal'};")

class ToggleAnimation(QPushButton):
    toggled = pyqtSignal(bool)

    def __init__(self, neon_color="#00ffff", parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(50, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.neon_color = neon_color

        self._circle = QLabel(self)
        self._circle.setFixedSize(20, 20)
        self._circle.move(2, 2)
        self._circle.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
        """)

        self._animation = QPropertyAnimation(self._circle, b"geometry")
        self._animation.setDuration(150)
        self.setStyleSheet("background-color: #444; border-radius: 12px;")
        self.clicked.connect(self.animate_toggle)

    def animate_toggle(self):
        if self.isChecked():
            self._animation.setStartValue(QRect(2, 2, 20, 20))
            self._animation.setEndValue(QRect(28, 2, 20, 20))
            self.setStyleSheet(f"background-color: {self.neon_color}; border-radius: 12px;")
        else:
            self._animation.setStartValue(QRect(28, 2, 20, 20))
            self._animation.setEndValue(QRect(2, 2, 20, 20))
            self.setStyleSheet("background-color: #444; border-radius: 12px;")
        self._animation.start()
        self.toggled.emit(self.isChecked())

    def update_neon_color(self, new_color):
        self.neon_color = new_color
        if self.isChecked():
            self.setStyleSheet(f"background-color: {self.neon_color}; border-radius: 12px;")

class GifSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("GIF Size")
        self.setFixedSize(220, 140)

        from core.avatar_toggle import load_settings
        settings = load_settings()
        size = settings.get("floating_miya_size", {"width": 350, "height": 200})
        current_w = size.get("width", 350)
        current_h = size.get("height", 200)

        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Width"))
        self.w = QLineEdit()
        self.w.setPlaceholderText(str(current_w))
        row1.addWidget(self.w)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Height"))
        self.h = QLineEdit()
        self.h.setPlaceholderText(str(current_h))
        row2.addWidget(self.h)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.validate_and_accept)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.apply_btn)

        self.setLayout(layout)

    def validate_and_accept(self):
        try:
            w = int(self.w.text() or self.w.placeholderText())
            h = int(self.h.text() or self.h.placeholderText())
            if w <= 0 or h <= 0:
                raise ValueError
        except ValueError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for both width and height!")
            return
        self.accept()

    def get_values(self):
        return int(self.w.text() or self.w.placeholderText()), int(self.h.text() or self.h.placeholderText())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miya Desktop")
        self.setFixedSize(700, 600)

        self.is_light_theme = load_theme()
        self.bg_colors = toggle_theme(self.is_light_theme) 
        self.neon_enabled, self.neon_color = load_neon_settings()
        self.toggle_refs = []
        self.toggle_labels = []
        self.stack = QStackedLayout()
        self.init_main_page()

        # --------------------------
        app_manager_page = create_app_manager_page(self.stack)
        self.stack.addWidget(app_manager_page)

        self.music_page, self.music_back_btn = create_music_page(self.stack, self.neon_enabled, self.neon_color)
        self.stack.addWidget(self.music_page)
        # --------------------------

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addLayout(self.stack)

        self.warning_bar = QLabel("⚠️ Warning: Miya Desktop is not liable for any damage, loss, or consequences arising from the launch or execution of unauthorized, harmful, or malicious applications launched through voice commands or user input. Use wisely.")
        self.warning_bar.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffaa00;
            font-size: 11px;
            font-weight: bold;
            border-top: 1px solid #ffaa00;
            padding: 6px;
        """)
        self.warning_bar.setWordWrap(True)
        self.warning_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.warning_bar.setFixedHeight(45)

        wrapper_layout.addWidget(self.warning_bar)

        self.init_hotkey_listener()

    def apply_theme_styles(self):
        font_size = self.font_size_input.value() if hasattr(self, "font_size_input") else 20
        self.setStyleSheet(f"background-color: {self.bg_colors['bg']}; color: {self.bg_colors['text']};")
        if hasattr(self, "left_panel"):
            self.left_panel.setStyleSheet(f"""
                * {{
                    color: {self.bg_colors['text']};
                    font-size: {font_size}px;
                    font-family: 'Segoe UI';
                }}
            """)
        self.apply_font_size()

    def open_gif_size_dialog(self):
        dialog = GifSizeDialog(self)
        if dialog.exec():
            w, h = dialog.get_values()
            from core.avatar_toggle import apply_floating_miya_size_now
            apply_floating_miya_size_now(w, h)

    def open_api_dialog(self):
        dialog = ApiDialog(self)
        dialog.exec()
    
    def open_custom_dialog(self):
        dialog = CustomPathDialog(self)
        dialog.exec()

    def on_theme_toggled(self, checked: bool):
        save_theme(checked)                  
        self.bg_colors = toggle_theme(checked)
        self.apply_theme_styles() 
        for label in self.toggle_labels:
            label.update_color()

    def init_hotkey_listener(self):
        print("🔉 Hotkey listener active for Ctrl + M")
        keyboard.add_hotkey('ctrl+m', self.on_ctrl_m_pressed)

    def on_ctrl_m_pressed(self):
        print("🎤 Ctrl + M detected — activating Miya listener...")
        activate_miya_listener()
    
    def reload_miya_gif(self):
        self.miya_movie.stop()
        self.miya_movie.setFileName(str(get_avatar_path()))
        self.miya_movie.start()

    def update_neon_styles(self):
        neon_style = f"""
            QFrame#neonFrame {{
                border: 2px solid {self.neon_color if self.neon_enabled else 'transparent'};
                border-radius: 15px;
                background-color: rgba(0, 0, 0, 0);
            }}
            QFrame#miyaFrame {{
                border: 2px solid {self.neon_color if self.neon_enabled else 'transparent'};
                border-radius: 15px;
                background-color: rgba(0, 0, 0, 0);
            }}
        """
        self.neon_frame.setStyleSheet(neon_style)
        self.miya_frame.setStyleSheet(neon_style)

    def style_neon_button(self, btn):
        size = self.font_size_input.value()

        if self.neon_enabled:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.neon_color};
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-family: 'Segoe UI';
                    font-size: {size}px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: white;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-family: 'Segoe UI';
                    font-size: {size}px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: #444444;
                }}
            """)
    
    def build_toggle_row(self, label_text, default_checked, slot_fn=None, red=False):
        toggle = ToggleAnimation(self.neon_color)
        toggle.setChecked(default_checked)
        toggle.animate_toggle()
        self.toggle_refs.append(toggle)
        label = ThemeLabel(label_text, self, red=red)
        self.toggle_labels.append(label)

        row = QHBoxLayout()
        row.addWidget(toggle)
        row.addWidget(label)
        row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        widget = QWidget()
        widget.setLayout(row)

        if slot_fn:
            toggle.toggled.connect(lambda checked: slot_fn(checked))

        return toggle, widget

    def init_main_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout()

        self.neon_frame = QFrame()
        self.neon_frame.setObjectName("neonFrame")
        neon_layout = QVBoxLayout()

        ui_container = QWidget()
        ui_layout = QHBoxLayout()
        ui_container.setStyleSheet("""
            * {
                font-family: 'DM Sans';
            }
        """)

        button_layout = QVBoxLayout()

        hotkey_hint = QLabel("🎤 She responds only to voice commands. Press Ctrl + M to begin speaking.")
        hotkey_hint.setStyleSheet("""
            color: #888;
            font-size: 10px;
            padding-top: 4px;
        """)
        hotkey_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(hotkey_hint)

        theme_toggle, theme_widget = self.build_toggle_row("Switch Theme", self.is_light_theme, self.on_theme_toggled)
        avatar_toggle , avatar_widget = self.build_toggle_row("Show Miya", True, toggle_avatar)
        startup_enabled = load_startup_setting()
        _, startup_widget = self.build_toggle_row("Run at Startup", startup_enabled, toggle_startup)
        neon_toggle, neon_widget = self.build_toggle_row("Enable Neon Glow",self.neon_enabled,self.toggle_neon)

        self._demon_resetting = False
        def on_demon_toggled(checked):
            if self._demon_resetting:
                return
            toggle_demon_mode(checked)
            if checked:
                def reset_toggle():
                    self._demon_resetting = True
                    demon_toggle.setChecked(False)
                    demon_toggle.animate_toggle()
                    self._demon_resetting = False

                QTimer.singleShot(5000, reset_toggle)
        demon_toggle, demon_widget = self.build_toggle_row("Override Mode",False,on_demon_toggled,red=True)

        self.settings = load_settings()
        avatar_enabled = self.settings.get("floating_miya_enabled", True)
        avatar_toggle.blockSignals(True)
        avatar_toggle.setChecked(avatar_enabled)
        avatar_toggle.animate_toggle()
        avatar_toggle.blockSignals(False)  
        toggle_avatar(avatar_enabled)

        demon_warning = QLabel("⚠️ Miya Desktop blocks critical paths by default.\nEnable this to override restricted paths, including system folders and protected apps. This action requires administrator privileges")
        demon_warning.setWordWrap(True)
        demon_warning.setStyleSheet("color: red; font-size: 10px;")

        self.app_btn = QPushButton("Add Application")
        self.app_btn.setFixedSize(300, 40)
        self.app_btn.setShortcut(QKeySequence("1"))
        self.app_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        font_row = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 26)
        self.font_size_input.setValue(20)
        self.font_size_input.setFixedWidth(60)
        self.font_size_input.setStyleSheet(f"""
            QSpinBox {{
                background: transparent;
                border: none;
            }}

            QSpinBox QLineEdit {{
                background: transparent;
                color: {self.bg_colors["text"]};
                font-size: 20px;
            }}

            QSpinBox::up-button,
            QSpinBox::down-button {{
                width: 0px;
                height: 0px;
            }}
        """)
        self.font_size_input.valueChanged.connect(self.apply_font_size)
        font_row.addWidget(font_size_label)
        font_row.addWidget(self.font_size_input)

        font_widget = QWidget()
        font_widget.setLayout(font_row)
        font_widget.setContentsMargins(0, 0, 0, 0)
        font_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        # --------------------------------
        self.music_btn = QPushButton("Music")
        self.music_btn.setFixedSize(300, 40)
        self.music_btn.setShortcut(QKeySequence("2"))
        self.music_btn.clicked.connect(lambda: print("Music button clicked"))
        self.music_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.custom_btn = QPushButton("Custom", ui_container)
        self.custom_btn.setFixedSize(150, 40)
        self.custom_btn.setShortcut(QKeySequence("4"))
        self.custom_btn.move(450, 270)
        self.custom_btn.clicked.connect(lambda: print("Custom clicked"))
        self.custom_btn.clicked.connect(self.open_custom_dialog)
        self.style_neon_button(self.custom_btn)
        self.custom_btn.show()

        self.gif_size_btn = QPushButton("Gif Size", ui_container)
        self.gif_size_btn.setFixedSize(150, 40)
        self.gif_size_btn.setShortcut(QKeySequence("5"))
        self.gif_size_btn.move(450, 330)
        self.gif_size_btn.clicked.connect(self.open_gif_size_dialog)
        self.style_neon_button(self.gif_size_btn)
        self.gif_size_btn.show()

        self.api_btn = QPushButton("API", ui_container)
        self.api_btn.setFixedSize(150, 40)
        self.api_btn.setShortcut(QKeySequence("6"))
        self.api_btn.move(450, 390)
        self.api_btn.clicked.connect(lambda: print("API clicked"))
        self.api_btn.clicked.connect(self.open_api_dialog)
        self.style_neon_button(self.api_btn)
        self.api_btn.show()
        # --------------------------------

        self.color_btn = QPushButton("Choose Neon Color")
        self.color_btn.setFixedSize(300, 40)
        self.color_btn.setShortcut(QKeySequence("3"))
        self.color_btn.clicked.connect(self.pick_neon_color)

        self.style_neon_button(self.app_btn)
        self.style_neon_button(self.music_btn)
        self.style_neon_button(self.color_btn)

        for widget in [theme_widget, avatar_widget, startup_widget, self.app_btn, font_widget, self.music_btn, neon_widget, self.color_btn, demon_widget, demon_warning]:
            button_layout.addWidget(widget)

        self.left_panel = QWidget()
        self.left_panel.setLayout(button_layout)
        self.apply_font_size()
        self.left_panel.setFixedWidth(350)
        ui_layout.addWidget(self.left_panel)

        miya_container = QVBoxLayout()
        self.miya_frame = QFrame()
        self.miya_frame.setObjectName("miyaFrame")
        self.miya_frame.setFixedWidth(200)
        miya_layout = QVBoxLayout()

        miya_image = QLabel()
        self.miya_movie = QMovie(str(get_avatar_path()))
        self.miya_movie.setScaledSize(QSize(200, 150))
        miya_image.setMovie(self.miya_movie)
        self.miya_movie.start()

        miya_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fur_row = QHBoxLayout()
        btn_color = self.bg_colors["text"] if hasattr(self, "bg_colors") else "#ffffff"
        left_btn = QPushButton("⯇")
        left_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: {btn_color};
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                color: {self.neon_color if self.neon_enabled else btn_color};
            }
        """)
        
        # Label for the Avatar name------------------------------
        try:
            data = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
            current_fur = data.get("current_fur", "White")
        except Exception:
                current_fur = "White"

        self.fur_label = QLabel(current_fur)
        self.fur_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_btn = QPushButton("⯈")
        right_btn.setStyleSheet(left_btn.styleSheet())

        left_btn.clicked.connect(
            lambda: (switch_fur("prev", self.fur_label), self.reload_miya_gif(), refresh_floating_miya())
        )

        right_btn.clicked.connect(
            lambda: (switch_fur("next", self.fur_label), self.reload_miya_gif(), refresh_floating_miya())
        )

        fur_row.addWidget(left_btn)
        fur_row.addWidget(self.fur_label)
        fur_row.addWidget(right_btn)

        miya_layout.addWidget(miya_image)
        miya_layout.addLayout(fur_row)
        self.miya_frame.setLayout(miya_layout)

        miya_container.addSpacing(40)
        miya_container.addWidget(self.miya_frame)

        # -------------------------------------
        miya_container.addStretch()

        ui_layout.addLayout(miya_container)
        ui_container.setLayout(ui_layout)
        neon_layout.addWidget(ui_container)
        self.neon_frame.setLayout(neon_layout)
        outer_layout.addWidget(self.neon_frame)
        page.setLayout(outer_layout)

        self.stack.addWidget(page)
        self.update_neon_styles()
        self.apply_theme_styles()
        for label in self.toggle_labels:
            label.update_color()

        self.apply_font_size()
        QShortcut(QKeySequence(Qt.Key.Key_Backspace), self, activated=self.showMinimized)

    def apply_font_size(self):
        size = self.font_size_input.value()
        self.font_size_input.setFont(QFont("Segoe UI", size))
        self.left_panel.setStyleSheet(f"""
            * {{
                font-size: {size}px;
                font-family: 'Segoe UI';
            }}
        """)

        if hasattr(self, "custom_btn"):
            self.style_neon_button(self.custom_btn)
        if hasattr(self, "gif_size_btn"):
            self.style_neon_button(self.gif_size_btn)
        if hasattr(self, "api_btn"):
            self.style_neon_button(self.api_btn)

        for btn in (self.app_btn, self.music_btn, self.color_btn):
            self.style_neon_button(btn)
            
        self.font_size_input.setStyleSheet(f"""
            QSpinBox {{
                background: transparent;
                border: none;
            }}

            QSpinBox QLineEdit {{
                background: transparent;
                color: {self.bg_colors["text"]};
                font-size: {size}px;
                font-family: 'Segoe UI';
            }}

            QSpinBox::up-button,
            QSpinBox::down-button {{
                width: 0px;
                height: 0px;
            }}
        """)

    def toggle_neon(self, checked):
        self.neon_enabled = checked
        save_neon_settings(enabled=checked)
        self.update_neon_styles()
        for btn in (self.app_btn, self.music_btn, self.color_btn, self.custom_btn, self.gif_size_btn, self.api_btn):
            self.style_neon_button(btn)
        for toggle in self.toggle_refs:
            toggle.update_neon_color(self.neon_color)
        self.style_neon_button(self.music_back_btn)
        self.update_music_page_neon()

    def pick_neon_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.neon_color = color.name()
            save_neon_settings(color=self.neon_color)
            for toggle in self.toggle_refs:
                toggle.update_neon_color(self.neon_color)
            self.update_neon_styles()
            for btn in (self.app_btn, self.music_btn, self.color_btn, self.custom_btn, self.gif_size_btn, self.api_btn):
                self.style_neon_button(btn)
            self.style_neon_button(self.music_back_btn)
            self.update_music_page_neon()

    def update_music_page_neon(self):
        if hasattr(self, "music_page"):
            border_color = self.neon_color if self.neon_enabled else "transparent"
            self.music_page.setStyleSheet(f"""
                QFrame#musicNeonFrame {{
                    border: 2px solid {border_color};
                    border-radius: 15px;
                    background-color: #1a1a1a;
                }}
            """)
       