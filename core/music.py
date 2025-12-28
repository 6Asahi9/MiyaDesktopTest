import json
from pathlib import Path
from random import choice

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFrame, QSlider, QHBoxLayout
)
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.path import MUSIC_PATH, PLAYER_PATH, SETTINGS_JSON
from core.music_picker import MusicPickerDialog


# JSON helpers ----------------

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


# Music page ----------------

def create_music_page(stack, neon_enabled=True, neon_color="#00ffff"):
    page = QFrame()
    page.setObjectName("musicNeonFrame")
    page.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

    # helpers ----------

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

    def get_music_files():
        return sorted(f.name for f in MUSIC_PATH.iterdir() if f.is_file())

    def play_song(name):
        path = MUSIC_PATH / name
        if not path.exists():
            return
        settings["last_music"] = name
        save_settings(settings)
        now_playing.setText(name)
        player.setSource(QUrl.fromLocalFile(str(path)))
        player.play()
        movie.start()

    def play_next():
        music_files = get_music_files()
        current = settings.get("last_music")

        if not music_files:
            return

        if current not in music_files:
            play_song(music_files[0])
            return

        idx = music_files.index(current)
        play_song(music_files[(idx + 1) % len(music_files)])

    def play_previous():
        music_files = get_music_files()
        current = settings.get("last_music")

        if not music_files:
            return

        if current not in music_files:
            play_song(music_files[0])
            return

        idx = music_files.index(current)
        play_song(music_files[(idx - 1) % len(music_files)])

    # UI ----------

    music_dir = Path.home() / "MiyaDesktop" / "Music"
    music_hint = QLabel(f"🎵 Add music files to:\n{music_dir}")
    music_hint.setStyleSheet("color: #888; font-size: 10px; padding-top: 4px;")
    music_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(music_hint)

    now_playing = QLabel("No music selected")
    now_playing.setStyleSheet("color: white; font-size: 12px;")
    now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(now_playing)

    player_label = QLabel()
    player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    movie = QMovie(str(PLAYER_PATH))
    movie.setScaledSize(QSize(160, 160))
    player_label.setMovie(movie)
    layout.addWidget(player_label)

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

    # Playback modes ----------

    playback_mode = "repeat"

    mode_layout = QHBoxLayout()
    repeat_btn = QPushButton("Repeat")
    juggle_btn = QPushButton("Juggle")
    straight_btn = QPushButton("Straight")

    for btn in (repeat_btn, juggle_btn, straight_btn):
        style_neon_button(btn)
        btn.setFixedWidth(80)

    mode_layout.addWidget(repeat_btn)
    mode_layout.addWidget(juggle_btn)
    mode_layout.addWidget(straight_btn)
    layout.addLayout(mode_layout)

    def update_mode_buttons():
        repeat_btn.setStyleSheet(repeat_btn.styleSheet() + ("border:2px solid #ffff00;" if playback_mode == "repeat" else ""))
        juggle_btn.setStyleSheet(juggle_btn.styleSheet() + ("border:2px solid #ffff00;" if playback_mode == "juggle" else ""))
        straight_btn.setStyleSheet(straight_btn.styleSheet() + ("border:2px solid #ffff00;" if playback_mode == "straight" else ""))

    update_mode_buttons()

    def set_repeat():
        nonlocal playback_mode
        playback_mode = "repeat"
        print("clicked repeat")
        update_mode_buttons()

    def set_juggle():
        nonlocal playback_mode
        playback_mode = "juggle"
        print("clicked juggle")
        update_mode_buttons()

    def set_straight():
        nonlocal playback_mode
        playback_mode = "straight"
        print("clicked straight")
        update_mode_buttons()

    repeat_btn.clicked.connect(set_repeat)
    juggle_btn.clicked.connect(set_juggle)
    straight_btn.clicked.connect(set_straight)

    def handle_song_finished():
        last_music = settings.get("last_music")
        if not last_music:
            return

        music_files = get_music_files()

        if playback_mode == "repeat":
            play_song(last_music)

        elif playback_mode == "juggle":
            play_song(choice(music_files))

        elif playback_mode == "straight":
            idx = music_files.index(last_music)
            play_song(music_files[(idx + 1) % len(music_files)])

    player.mediaStatusChanged.connect(
        lambda status: handle_song_finished()
        if status == QMediaPlayer.MediaStatus.EndOfMedia else None
    )

    # Shortcuts ----------
    QShortcut(QKeySequence(Qt.Key.Key_Up), page).activated.connect(
    lambda: (
        print("Up arrow → volume up"),
        volume_slider.setValue(min(volume_slider.value() + 5, 100))
    )
    )

    QShortcut(QKeySequence(Qt.Key.Key_Down), page).activated.connect(
        lambda: (
            print("Down arrow → volume down"),
            volume_slider.setValue(max(volume_slider.value() - 5, 0))
        )
    )

    QShortcut(QKeySequence(Qt.Key.Key_Space), page).activated.connect(
    lambda: (print("Enter → Play/Pause"), toggle_play())
    )

    QShortcut(QKeySequence(Qt.Key.Key_Right), page).activated.connect(
        lambda: (print("Right arrow → next song"), play_next())
    )

    QShortcut(QKeySequence(Qt.Key.Key_Left), page).activated.connect(
        lambda: (print("Left arrow → previous song"), play_previous())
    )

    # Restore state ----------

    audio.setVolume(settings.get("music_volume", 60) / 100)
    volume_slider.setValue(settings.get("music_volume", 60))

    if settings.get("last_music"):
        play_song(settings["last_music"])
        if settings.get("music_paused", True):
            player.pause()
            movie.stop()

    # Controls ----------

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

    volume_slider.valueChanged.connect(
        lambda v: (audio.setVolume(v / 100),
                   settings.update({"music_volume": v}),
                   save_settings(settings))
    )

    def select_music(name):
        play_song(name)
        settings["music_paused"] = False
        save_settings(settings)

    dots_btn.clicked.connect(
        lambda: MusicPickerDialog(
            current_music=settings.get("last_music"),
            parent=page
        ).music_selected.connect(select_music)
    )

    back_btn = QPushButton("Back")
    back_btn.setFixedSize(120, 50)
    style_neon_button(back_btn)
    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))

    layout.addStretch()
    layout.addWidget(back_btn)
    def open_picker():
        dlg = MusicPickerDialog(
            current_music=settings.get("last_music"),
            parent=page
        )
        dlg.music_selected.connect(select_music)
        dlg.exec()

    dots_btn.clicked.connect(open_picker)

    return page, back_btn
