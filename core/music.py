import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFrame, QSlider
)
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from core.path import MUSIC_PATH, PLAYER_PATH, SETTINGS_JSON
from core.music_picker import MusicPickerDialog 

# JSON helpers
def load_settings():
    if SETTINGS_JSON.exists():
        try:
            return json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_settings(data):
    SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_JSON.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

# Music page
def create_music_page(stack, neon_enabled=True, neon_color="#00ffff"):
    page = QFrame()
    page.setObjectName("musicNeonFrame")
    layout = QVBoxLayout(page)

    # Neon border
    page.setStyleSheet(f"""
        QFrame#musicNeonFrame {{
            border: 2px solid {neon_color if neon_enabled else 'transparent'};
            border-radius: 15px;
            background-color: #1a1a1a;
        }}
    """)

    # Player backend
    audio = QAudioOutput()
    player = QMediaPlayer()
    player.setAudioOutput(audio)

    settings = load_settings()

    # Helper to style buttons
    def style_neon_button(btn):
        if neon_enabled:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {neon_color};
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 14px;
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
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)

    # Hint
    music_dir = Path.home() / "MiyaDesktop" / "Music"
    music_hint = QLabel(f"🎵 Add music files to:\n{music_dir}")
    music_hint.setStyleSheet("color: #888; font-size: 10px; padding-top: 4px;")
    music_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(music_hint)

    # Now playing
    now_playing = QLabel("No music selected")
    now_playing.setStyleSheet("color: white; font-size: 12px;")
    now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(now_playing)

    # Animation
    player_label = QLabel()
    player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    movie = QMovie(str(PLAYER_PATH))
    movie.setScaledSize(QSize(160, 160))
    player_label.setMovie(movie)
    layout.addWidget(player_label)

    # Controls
    play_btn = QPushButton("Play / Pause")
    style_neon_button(play_btn)

    volume_slider = QSlider(Qt.Orientation.Horizontal)
    volume_slider.setRange(0, 100)

    dots_btn = QPushButton("⋮")
    dots_btn.setFixedWidth(40)
    style_neon_button(dots_btn)

    layout.addWidget(play_btn)
    layout.addWidget(volume_slider)
    layout.addWidget(dots_btn)

    # Back button
    back_btn = QPushButton("Back")
    back_btn.setFixedSize(120, 50)
    style_neon_button(back_btn)
    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))

    layout.addStretch()
    layout.addWidget(back_btn)

    # Restore state
    last_music = settings.get("last_music")
    paused = settings.get("music_paused", True)
    volume = settings.get("music_volume", 60)

    audio.setVolume(volume / 100)
    volume_slider.setValue(volume)

    if last_music:
        path = MUSIC_PATH / last_music
        if path.exists():
            player.setSource(QUrl.fromLocalFile(str(path)))
            now_playing.setText(last_music)

    # Logic
    def toggle_play():
        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.pause()
            movie.stop()
            settings["music_paused"] = True
        else:
            player.play()
            movie.start()
            settings["music_paused"] = False
        save_settings(settings)

    play_btn.clicked.connect(toggle_play)

    def change_volume(v):
        audio.setVolume(v / 100)
        settings["music_volume"] = v
        save_settings(settings)

    volume_slider.valueChanged.connect(change_volume)

    def select_music(name):
        path = MUSIC_PATH / name
        if not path.exists():
            return
        player.setSource(QUrl.fromLocalFile(str(path)))
        player.play()
        movie.start()
        now_playing.setText(name)
        settings["last_music"] = name
        settings["music_paused"] = False
        save_settings(settings)

    def open_picker():
        dlg = MusicPickerDialog(current_music=settings.get("last_music"), parent=page)
        dlg.music_selected.connect(select_music)
        dlg.exec()

    dots_btn.clicked.connect(open_picker)

    return page, back_btn
