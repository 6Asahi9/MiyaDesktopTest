import json
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QMovie

from core.path import SETTINGS_JSON, ASSETS_PATH
from core.path import get_avatar_path

class FloatingMiya(QWidget):
    # def __init__(self, gif_path=None):
    #     super().__init__(
    #         None,
    #         Qt.WindowType.FramelessWindowHint |
    #         Qt.WindowType.WindowStaysOnTopHint |
    #         Qt.WindowType.Tool
    #     )
    #     if gif_path is None:
    #         gif_path = ASSETS_PATH / "placeholder_miya.gif"
    #     self.movie = QMovie(str(gif_path))

    #     self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    #     self.setFixedSize(200, 150)

    #     self.label = QLabel(self)
    #     self.label.setFixedSize(self.size())
    #     self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    #     # self.movie = QMovie(gif_path)
    #     self.movie.setScaledSize(self.size())
    #     self.label.setMovie(self.movie)
    #     self.movie.start()

    #     self._drag_offset: QPoint | None = None
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

    # ---- Drag handling ----
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        event.accept()

    # ---- Initial placement ----
    def show_at_corner(self):
        screen = QApplication.primaryScreen()
        if not screen:
            self.show()
            return

        geo = screen.availableGeometry()
        x = geo.right() - self.width() - 20
        y = geo.bottom() - self.height() - 20

        self.move(x, y)
        self.show()


# ---------- Settings helpers ----------
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

# ---------- Toggle logic ----------
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
            _floating_miya.hide()

    settings["floating_miya_enabled"] = show_avatar
    save_settings(settings)

    print("Avatar", "shown" if show_avatar else "hidden")
