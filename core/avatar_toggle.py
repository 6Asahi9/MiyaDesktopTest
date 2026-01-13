from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
import json
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from core.path import SETTINGS_JSON, get_avatar_path, CHAT_BUBBLE
from PyQt6.QtCore import QPropertyAnimation

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

class MiyaOverlay(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 500)

        self.miya = None
        self.text_overlay = TextOverlay(self)
        self.miya = FloatingMiya(self)
        self.text_overlay.move(0, 10)
        self.center_miya()
        self._drag_offset: QPoint | None = None

    def center_miya(self):
        if not self.miya:
            return
        self.miya.move(
            (self.width() - self.miya.width()) // 2 + 100,
            self.height() - self.miya.height() - 10
        )

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

    def hide_all(self):
        self.text_overlay.hide_now()
        self.hide()


class FloatingMiya(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie(str(get_avatar_path()))
        self.label.setMovie(self.movie)
        self.apply_size_from_settings()
        self.movie.start()

    def apply_size_from_settings(self):
        settings = load_settings()

        size = settings.get("floating_miya_size")
        if not size:
            size = {"width": 350, "height": 200}
            settings["floating_miya_size"] = size
            save_settings(settings)

        w = size.get("width", 350)
        h = size.get("height", 200)

        self.setFixedSize(w, h)
        self.label.setFixedSize(w, h)
        self.movie.setScaledSize(self.size())

        if self.parent():
            self.parent().center_miya()

    def reload_avatar(self):
        self.movie.stop()
        self.movie.setFileName(str(get_avatar_path()))
        self.apply_size_from_settings()
        self.movie.start()

class TextOverlay(QWidget):
    AUTO_HIDE_MS = 6000

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 120)

        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, 380, 120)
        pixmap = QPixmap(str(CHAT_BUBBLE))
        pixmap = pixmap.scaled(
            self.bg.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.bg.setPixmap(pixmap)

        self.label = QLabel(self.bg)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setGeometry(10, 10, 360, 100)
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1)
        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(600)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        self.hide()

    def fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.finished.connect(self.hide)
        self.fade_anim.start()

    def show_text(self, text: str):
        self.fade_anim.stop()
        self.label.setText(text)
        self.show()
        self.opacity.setOpacity(1)
        QTimer.singleShot(self.AUTO_HIDE_MS, self.fade_out)
        self.raise_()

    def hide_now(self):
        self.hide_timer.stop()
        self.hide()

_overlay: MiyaOverlay | None = None

def toggle_avatar(show_avatar: bool):
    global _overlay
    settings = load_settings()

    if show_avatar:
        if _overlay is None:
            _overlay = MiyaOverlay()
        _overlay.show_at_corner()
    else:
        if _overlay:
            _overlay.hide_all()

    settings["floating_miya_enabled"] = show_avatar
    save_settings(settings)

def refresh_floating_miya():
    if _overlay and _overlay.miya:
        _overlay.miya.reload_avatar()

def apply_floating_miya_size_now(width: int, height: int):
    settings = load_settings()
    settings["floating_miya_size"] = {"width": width, "height": height}
    save_settings(settings)

    if _overlay and _overlay.miya:
        _overlay.miya.apply_size_from_settings()


def show_chat_bubble(text: str):
    if _overlay:
        _overlay.text_overlay.show_text(text)


def hide_chat_bubble():
    if _overlay:
        _overlay.text_overlay.hide_now()
