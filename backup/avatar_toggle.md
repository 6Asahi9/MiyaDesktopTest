import json
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QMovie
from core.path import SETTINGS_JSON, ASSETS_PATH
from core.path import get_avatar_path, CHAT_BUBBLE

class FloatingMiya(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 150)

        self.label = QLabel(self)
        self.label.setFixedSize(self.size())
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.movie = QMovie(str(get_avatar_path()))
        self.movie.setScaledSize(self.size())
        self.label.setMovie(self.movie)
        self.movie.start()

        # Drag state
        self._drag_offset = None

        # Chat bubble overlay
        self.chat_bubble = ChatBubble()
        self.chat_bubble.move_above(self.pos(), self.size())

    # Drag handling 
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            self.move(new_pos)
            self.chat_bubble.move_above(new_pos, self.size())
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        event.accept()

    # Initial placement 
    def show_at_corner(self):
        screen = QApplication.primaryScreen()
        if not screen:
            self.show()
            self.chat_bubble.show()
            return

        geo = screen.availableGeometry()
        x = geo.right() - self.width() - 20
        y = geo.bottom() - self.height() - 20

        self.move(x, y)
        self.show()
        self.chat_bubble.move_above(QPoint(x, y), self.size())
        self.chat_bubble.show()

    def hide_all(self):
        self.chat_bubble.hide()
        self.hide()

class ChatBubble(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 250)

        self.gif_label = QLabel(self)
        self.gif_label.setFixedSize(self.size())
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.movie = QMovie(str(CHAT_BUBBLE))
        self.movie.setScaledSize(self.size())
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        # Text overlay
        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10px;
                background: transparent;
            }
        """)
        self.text_label.setGeometry(10, 10, 100, 60)

        self.hide()

    def move_above(self, avatar_pos: QPoint, avatar_size: QSize):
        x = avatar_pos.x() + (avatar_size.width() - self.width()) // 2 - 70
        y = avatar_pos.y() - self.height() + 10
        self.move(x, y)

    def show_text(self, text: str):
        self.text_label.setText(text)
        self.show()

    def clear_and_hide(self):
        self.text_label.clear()
        self.hide()

# Settings helpers ----------------------
def load_settings():
    if SETTINGS_JSON.exists():
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_settings(settings: dict):
    SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_JSON, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

# Toggle logic --------------------------------------------
_floating_miya: FloatingMiya | None = None

def toggle_avatar(show_avatar: bool):
    global _floating_miya
    settings = load_settings()
    if show_avatar:
        if _floating_miya is None:
            _floating_miya = FloatingMiya()
        _floating_miya.show_at_corner()
    else:
        if _floating_miya is not None:
            _floating_miya.hide_all()
    settings["floating_miya_enabled"] = show_avatar
    save_settings(settings)
    print("Avatar", "shown" if show_avatar else "hidden")

def show_chat_bubble(text: str):
    if _floating_miya is None:
        return

    pos = _floating_miya.pos()
    size = _floating_miya.size()

    _floating_miya.chat_bubble.move_above(pos, size)
    _floating_miya.chat_bubble.show_text(text)


def hide_chat_bubble():
    if _floating_miya is None:
        return

    _floating_miya.chat_bubble.clear_and_hide()
