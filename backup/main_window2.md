from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QStackedLayout, QCheckBox, QFrame, QColorDialog, QSlider, QSpinBox,
    QSizePolicy, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QMovie, QFont, QColor
from core.startup import toggle_startup
from core.theme import toggle_theme
from core.avatar_toggle import toggle_avatar , load_settings
from core.demonMode import toggle_demon_mode
from core.fur import switch_fur
from core.page_switch import switch_to_main, create_app_manager_page
from core.mic_handler import activate_miya_listener
import keyboard

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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miya Desktop")
        self.setFixedSize(700, 560)

        self.neon_enabled = True
        self.neon_color = "#00ffff"
        self.toggle_refs = []
        self.toggle_labels = []
        self.stack = QStackedLayout()
        self.init_main_page()
        # self.init_app_manager_page()
        app_manager_page = create_app_manager_page(self.stack)
        self.stack.addWidget(app_manager_page)
        # app_manager_page = create_app_manager_page(self.stack)
        # self.stack.addWidget(app_manager_page)

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
    
    def init_hotkey_listener(self):
        print("🔉 Hotkey listener active for Ctrl + M")
        keyboard.add_hotkey('ctrl+m', self.on_ctrl_m_pressed)

    def on_ctrl_m_pressed(self):
        print("🎤 Ctrl + M detected — activating Miya listener...")
        activate_miya_listener()


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
        if self.neon_enabled:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.neon_color};
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background-color: white;
                }}
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)

    def apply_font_size(self):
        size = self.font_size_input.value()
        font = QFont("Segoe UI", size)
        self.font_size_input.setFont(QFont("Segoe UI", size))

        self.left_panel.setStyleSheet(f"""
            * {{
                font-size: {size}px;
                font-family: 'Segoe UI';
            }}
        """)

        for label in self.toggle_labels:
            label.setFont(font)

    def build_toggle_row(self, label_text, default_checked, slot_fn=None, red=False):
        toggle = ToggleAnimation(self.neon_color)
        toggle.setChecked(default_checked)
        toggle.animate_toggle()
        self.toggle_refs.append(toggle)

        label = QLabel(label_text)
        self.toggle_labels.append(label)
        label.setStyleSheet(f"color: {'red' if red else 'white'}; font-weight: {'bold' if red else 'normal'};")

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

        _, theme_widget = self.build_toggle_row("Switch Theme", False, toggle_theme)
        avatar_toggle , avatar_widget = self.build_toggle_row("Show Miya", True, toggle_avatar)
        _, startup_widget = self.build_toggle_row("Run at Startup", False, toggle_startup)
        _, neon_widget = self.build_toggle_row("Enable Neon Glow", True, self.toggle_neon)
        _, demon_widget = self.build_toggle_row("Override Mode", False, toggle_demon_mode, red=True)

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
        self.app_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        font_row = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 26)
        self.font_size_input.setValue(20)
        self.font_size_input.setFixedWidth(60)
        self.font_size_input.setStyleSheet("""
            QSpinBox {
                background: transparent;
                color: white;
                border: none;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                height: 0px;
            }
        """)
        self.font_size_input.valueChanged.connect(self.apply_font_size)
        font_row.addWidget(font_size_label)
        font_row.addWidget(self.font_size_input)

        font_widget = QWidget()
        font_widget.setLayout(font_row)
        font_widget.setContentsMargins(0, 0, 0, 0)
        font_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        self.color_btn = QPushButton("Choose Neon Color")
        self.color_btn.setFixedSize(300, 40)
        self.color_btn.clicked.connect(self.pick_neon_color)

        self.style_neon_button(self.app_btn)
        self.style_neon_button(self.color_btn)

        for widget in [theme_widget, avatar_widget, startup_widget, self.app_btn, font_widget, neon_widget, self.color_btn, demon_widget, demon_warning]:
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
        movie = QMovie("assets/placeholder_miya.gif")
        movie.setScaledSize(QSize(200, 150))
        miya_image.setMovie(movie)
        movie.start()
        miya_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fur_row = QHBoxLayout()
        left_btn = QPushButton("⯇")
        left_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: #00ffff;
            }
        """)
        self.fur_label = QLabel("White")
        self.fur_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_btn = QPushButton("⯈")
        right_btn.setStyleSheet(left_btn.styleSheet())

        left_btn.clicked.connect(lambda: switch_fur("prev", self.fur_label))
        right_btn.clicked.connect(lambda: switch_fur("next", self.fur_label))

        fur_row.addWidget(left_btn)
        fur_row.addWidget(self.fur_label)
        fur_row.addWidget(right_btn)

        miya_layout.addWidget(miya_image)
        miya_layout.addLayout(fur_row)
        self.miya_frame.setLayout(miya_layout)

        miya_container.addWidget(self.miya_frame)
        miya_container.addStretch()

        ui_layout.addLayout(miya_container)
        ui_container.setLayout(ui_layout)
        neon_layout.addWidget(ui_container)
        self.neon_frame.setLayout(neon_layout)
        outer_layout.addWidget(self.neon_frame)
        page.setLayout(outer_layout)

        self.stack.addWidget(page)
        self.update_neon_styles()

    # def init_app_manager_page(self):
    #     page = QWidget()
    #     layout = QVBoxLayout()
    #     label = QLabel("App Manager (Placeholder)")
    #     # back_btn = QPushButton("⬅ Back")
    #     # back_btn.clicked.connect(lambda: switch_to_main(self.stack))

    #     layout.addWidget(label)
    #     # layout.addWidget(back_btn)
    #     layout.addStretch()
    #     page.setLayout(layout)

    #     scroll_area = QScrollArea()
    #     scroll_area.setWidgetResizable(True)
    #     scroll_area.setWidget(page)
    #     scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    #     self.stack.addWidget(scroll_area)

    def toggle_neon(self, checked):
        self.neon_enabled = checked
        self.update_neon_styles()
        self.style_neon_button(self.app_btn)
        self.style_neon_button(self.color_btn)
        for toggle in self.toggle_refs:
            toggle.update_neon_color(self.neon_color)

    def pick_neon_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.neon_color = color.name()
            for toggle in self.toggle_refs:
                toggle.update_neon_color(self.neon_color)
            self.update_neon_styles()
            self.style_neon_button(self.app_btn)
            self.style_neon_button(self.color_btn)
