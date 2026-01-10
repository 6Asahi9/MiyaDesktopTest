import json
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QSize, QPoint, QTimer
from PyQt6.QtGui import QMovie
from core.path import SETTINGS_JSON, get_avatar_path
from PyQt6.QtCore import QTimer, QPropertyAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect

# ROOT OVERLAY---------------------------------------------------------
class MiyaOverlay(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 300)

        # children
        self.text_overlay = TextOverlay(self)
        self.miya = FloatingMiya(self)

        self.text_overlay.move(0, 10)
        
        self.miya.move(
            (self.width() - self.miya.width()) // 2 + 100,
            self.height() - self.miya.height() - 10
        )

        self._drag_offset: QPoint | None = None

    # Drag whole overlay 
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

    # Visibility---------------------------- 
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

# Floating Miya------------------------------------------------------------
class FloatingMiya(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 150)

        self.label = QLabel(self)
        self.label.setFixedSize(self.size())
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.movie = QMovie(str(get_avatar_path()))
        self.movie.setScaledSize(self.size())
        self.label.setMovie(self.movie)
        self.movie.start()

    def reload_avatar(self):
        self.movie.stop()
        self.movie.setFileName(str(get_avatar_path()))
        self.movie.setScaledSize(self.size())
        self.movie.start()

# Text overlay-----------------------------------
class TextOverlay(QWidget):
    AUTO_HIDE_MS = 6000

    def fade_out(self):
        self.fade_anim.stop()
        try:
            self.fade_anim.finished.disconnect()
        except TypeError:
            pass
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

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 120)

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet("""
            QLabel {
                color: #00ff9c;
                background: black;
                font-size: 11px;
                padding: 10px;
                border-radius: 8px;
                font-family: Consolas, monospace;
            }
        """)
        self.label.setGeometry(0, 0, 380, 120)
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1)
        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(600)

        # auto-hide timer 
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        self.hide()

# Settings helpers-----------------------------
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

# Toggle logic---------------------------------------------
_overlay: MiyaOverlay | None = None
def toggle_avatar(show_avatar: bool):
    global _overlay
    settings = load_settings()

    if show_avatar:
        if _overlay is None:
            _overlay = MiyaOverlay()
        _overlay.show_at_corner()
    else:
        if _overlay is not None:
            _overlay.hide_all()

    settings["floating_miya_enabled"] = show_avatar
    save_settings(settings)

def show_chat_bubble(text: str):
    if _overlay is None:
        return
    _overlay.text_overlay.show_text(text)

def hide_chat_bubble():
    if _overlay is None:
        return
    _overlay.text_overlay.hide_now()

def refresh_floating_miya():
    if _overlay and _overlay.miya:
        _overlay.miya.reload_avatar()
