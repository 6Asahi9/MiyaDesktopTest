from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QStackedLayout, QCheckBox, QFrame, QColorDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie
from core.startup import toggle_startup
from PyQt6.QtWidgets import QSlider, QSpinBox
from PyQt6.QtWidgets import QSizePolicy
from core.theme import toggle_theme
from core.avatar_toggle import toggle_avatar
from core.demonMode import toggle_demon_mode
from PyQt6.QtGui import QFont
from core.fur import switch_fur
from core.page_switch import switch_to_app_manager, switch_to_main

from PyQt6.QtCore import pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

# class ToggleAnimation(QPushButton):
#     toggled = pyqtSignal(bool)

#     def __init__(self, neon_color="#00ffff", parent=None):
#         super().__init__(parent)
#         self.setCheckable(True)
#         self.setFixedSize(50, 24)
#         self.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.neon_color = neon_color

#         self._circle = QLabel(self)
#         self._circle.setFixedSize(20, 20)
#         self._circle.move(2, 2)
#         self._circle.setStyleSheet("""
#             background-color: white;
#             border-radius: 10px;
#         """)

#         self._animation = QPropertyAnimation(self._circle, b"geometry")
#         self._animation.setDuration(150)
#         self.setStyleSheet("background-color: #444; border-radius: 12px;")
#         self.clicked.connect(self.animate_toggle)

#     def animate_toggle(self):
#         if self.isChecked():
#             self._animation.setStartValue(QRect(2, 2, 20, 20))
#             self._animation.setEndValue(QRect(28, 2, 20, 20))
#             self.setStyleSheet(f"background-color: {self.neon_color}; border-radius: 12px;")
#         else:
#             self._animation.setStartValue(QRect(28, 2, 20, 20))
#             self._animation.setEndValue(QRect(2, 2, 20, 20))
#             self.setStyleSheet("background-color: #444; border-radius: 12px;")
#         self._animation.start()

#     def update_neon_color(self, new_color):
#         self.neon_color = new_color
#         if self.isChecked():
#             self.setStyleSheet(f"background-color: {self.neon_color}; border-radius: 12px;")
  

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miya Desktop")
        self.setFixedSize(600, 450)

        self.neon_enabled = True
        self.neon_color = "#00ffff"

        self.stack = QStackedLayout()
        self.init_main_page()
        self.init_app_manager_page()

        self.setLayout(self.stack)

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
        self.left_panel.setStyleSheet(f"""
            * {{
                font-size: {size}px;
                font-family: 'Segoe UI';
            }}
        """)    

# --------------------------------------------------------------

    def init_main_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout()
        # Neon border frame (Box1)
        self.neon_frame = QFrame()
        self.neon_frame.setObjectName("neonFrame")
        neon_layout = QVBoxLayout()

        # Inner UI container
        ui_container = QWidget()
        ui_layout = QHBoxLayout()

        ui_container = QWidget()
        ui_layout = QHBoxLayout()
        ui_container.setStyleSheet("""
            * {
                font-size: 16px;
                font-family: 'DM Sans';
            }
        """)
        # Left side buttons
        button_layout = QVBoxLayout()

        # Toggle checkboxes
        theme_checkbox = QCheckBox("Light Theme")
        avatar_checkbox = QCheckBox("Show Floating Miya")
        avatar_checkbox.setChecked(True)
        startup_checkbox = QCheckBox("Run at Startup")
        neon_checkbox = QCheckBox("Enable Neon Glow")
        neon_checkbox.setChecked(True)

        # Buttons
        self.app_btn = QPushButton("Add Application")
        self.app_btn.setFixedSize(300, 40)
        self.app_btn.clicked.connect(lambda: switch_to_app_manager(self.stack))

        demon_checkbox = QCheckBox("Enable Demon Mode")
        demon_checkbox.setStyleSheet("color: red; font-weight: bold;")

        demon_warning = QLabel("⚠️ Requires administrator privileges.\nEnables full access, including system folders and unrestricted apps.")
        demon_warning.setWordWrap(True)
        demon_warning.setStyleSheet("color: red; font-size: 11px;")
        demon_checkbox.stateChanged.connect(lambda state: toggle_demon_mode(state == 2))

# --------------------------------------------------------------
      
        # Font size controls
        font_row = QHBoxLayout()

        font_size_label = QLabel("Font Size:")
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 30)
        self.font_size_input.setValue(16)
        
        self.font_size_input.setFixedWidth(60)
        self.font_size_input.setStyleSheet("""
            QSpinBox {
                background: transparent;
                color: white;
                border: none;
                font-size: 14px;
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

        # Style them initially
        self.style_neon_button(self.app_btn)
        self.style_neon_button(self.color_btn)

# --------------------------------------------------------------

        # Add widgets to layout
        button_layout.addWidget(theme_checkbox)
        button_layout.addWidget(avatar_checkbox)
        button_layout.addWidget(startup_checkbox)
        button_layout.addWidget(self.app_btn)
        button_layout.addWidget(font_widget)
        button_layout.addWidget(neon_checkbox)
        button_layout.addWidget(self.color_btn)
        button_layout.addWidget(demon_checkbox)
        button_layout.addWidget(demon_warning)

        # self.animated_toggle = ToggleAnimation(self.neon_color)
        # animated_label = QLabel("Test Toggle (no function)")
        # animated_label.setStyleSheet("color: white; font-size: 14px;")

        # preview_row = QHBoxLayout()
        # preview_row.addWidget(animated_label)
        # preview_row.addWidget(self.animated_toggle)

        # preview_widget = QWidget()
        # preview_widget.setLayout(preview_row)
        # button_layout.addWidget(preview_widget)


        button_layout.addStretch()

# --------------------------------------------------------------

        # 🔹 Wrap it in a container so styles don't leak
        self.left_panel = QWidget()
        self.left_panel.setLayout(button_layout)

        # Now add this panel to the left of the main UI
        ui_layout.addWidget(self.left_panel)


        # Right side Miya image
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

        # Fur switcher row (moved below image)
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
        right_btn.setStyleSheet("""
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

        left_btn.clicked.connect(lambda: switch_fur("prev", self.fur_label))
        right_btn.clicked.connect(lambda: switch_fur("next", self.fur_label))

# --------------------------------------------------------------
      
        fur_row.addWidget(left_btn)
        fur_row.addWidget(self.fur_label)
        fur_row.addWidget(right_btn)

        miya_layout.addWidget(miya_image)
        miya_layout.addLayout(fur_row)
        self.miya_frame.setLayout(miya_layout)

        miya_container.addWidget(self.miya_frame)
        miya_container.addStretch()

        # Assemble UI
        ui_layout.addLayout(miya_container)
        ui_container.setLayout(ui_layout)
        neon_layout.addWidget(ui_container)
        self.neon_frame.setLayout(neon_layout)
        outer_layout.addWidget(self.neon_frame)
        page.setLayout(outer_layout)

        self.stack.addWidget(page)
        self.update_neon_styles()

# --------------------------------------------------------------
      
    def init_app_manager_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel("App Manager (Placeholder)")
        back_btn = QPushButton("⬅ Back")
        back_btn.clicked.connect(lambda: switch_to_main(self.stack))

        layout.addWidget(label)
        layout.addWidget(back_btn)
        page.setLayout(layout)

        self.stack.addWidget(page)

    def toggle_neon(self, checked):
        self.neon_enabled = checked
        self.update_neon_styles()
        self.style_neon_button(self.app_btn)
        self.style_neon_button(self.color_btn)

    def pick_neon_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.neon_color = color.name()
            # self.animated_toggle.update_neon_color(self.neon_color)

            self.update_neon_styles()
            self.style_neon_button(self.app_btn)
            self.style_neon_button(self.color_btn)
