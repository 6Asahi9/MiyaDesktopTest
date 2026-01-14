import json
from pathlib import Path
from random import choice

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFrame, QSlider, QHBoxLayout
)
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from core.path import MUSIC_PATH, PLAYER_PATH, SETTINGS_JSON
from core.music_picker import MusicPickerDialog
from PyQt6.QtWidgets import QDialog, QLineEdit, QMessageBox
import subprocess, re
from PyQt6.QtCore import QThread, pyqtSignal

# JSON helpers --------------------------------
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

def open_add_music_dialog(parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Music")
    dialog.setFixedSize(400, 180)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(12)

    info_label = QLabel("Place yt-dlp, ffmpeg, and ffprobe in the Music folder.\n"
    "Remove '&list' from the link to avoid downloading FULL playlists.\n"
    "its frezzing during download is normal")
    info_label.setStyleSheet(""" color: yellow; font-size:15px; """)
    info_label.setWordWrap(True)
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info_label)

    url_input = QLineEdit()
    url_input.setPlaceholderText("Paste YT video URL here")
    layout.addWidget(url_input)

    btn_layout = QHBoxLayout()
    download_btn = QPushButton("Download")
    cancel_btn = QPushButton("Cancel")
    btn_layout.addWidget(download_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    cancel_btn.clicked.connect(dialog.reject)
    class YTDLPWorker(QThread):
        progress = pyqtSignal(int)
        finished = pyqtSignal()
        error = pyqtSignal(str)

        def __init__(self, yt_dlp_path, url, output_path):
            super().__init__()
            self.yt_dlp_path = yt_dlp_path
            self.url = url
            self.output_path = output_path

        def run(self):
            try:
                process = subprocess.Popen(
                    [
                        str(self.yt_dlp_path),
                        "-x",
                        "--audio-format", "mp3",
                        "-o", str(self.output_path / "%(title)s.%(ext)s"),
                        self.url
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                for line in process.stdout:
                    match = re.search(r"(\d{1,3}\.\d{1,2})%", line)
                    if match:
                        percent = float(match.group(1))
                        self.progress.emit(int(percent))

                process.wait()
                if process.returncode != 0:
                    self.error.emit(f"yt-dlp exited with code {process.returncode}")
                else:
                    self.finished.emit()

            except Exception as e:
                self.error.emit(str(e))
    # ----------------------------------------------------------------

    def start_download():
        url = url_input.text().strip()
        if not url:
            QMessageBox.warning(dialog, "Error", "Please paste a URL")
            return

        yt_dlp_path = MUSIC_PATH / "yt-dlp.exe"
        if not yt_dlp_path.exists():
            QMessageBox.warning(dialog, "Error", "yt-dlp.exe not found in Music folder")
            return

        try:
            subprocess.run([
                str(yt_dlp_path),
                "-x",
                "--audio-format", "mp3",
                "--no-playlist",
                "-o", f"{MUSIC_PATH}/%(title)s.%(ext)s",
                url
            ], check=True)
            QMessageBox.information(dialog, "Done", "Download finished!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Download failed:\n{e}")

    download_btn.clicked.connect(start_download)

    dialog.exec()

# Music page --------------------------------------------
def create_music_page(stack, neon_enabled=True, neon_color="#00ffff"):
    page = QFrame()
    page.setObjectName("musicNeonFrame")
    page.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    layout = QVBoxLayout(page)
    layout.setSpacing(15)
    layout.setContentsMargins(20, 20, 20, 20)

    # Neon border
    page.setStyleSheet(f""" 
        QFrame#musicNeonFrame {{ 
        margin: 10px; border: 2px solid {neon_color if neon_enabled else 'transparent'}; 
        border-radius: 15px; 
        background-color: #1a1a1a; }} 
    """)

    # Player backend
    audio = QAudioOutput()
    player = QMediaPlayer()
    player.setAudioOutput(audio)

    settings = load_settings()

    # helpers ----------------
    def style_neon_button(btn):
        if neon_enabled:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {neon_color};
                    color: black;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 15px;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: black;
                }}
            """)
        else:
            btn.setStyleSheet("""
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
    def grey_button(btn):
        btn.setStyleSheet("""
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

    def get_music_files():
        return sorted(
            f.name for f in MUSIC_PATH.iterdir()
            if f.is_file() and f.suffix.lower() == ".mp3" and not f.name.startswith(".")
        )

    def load_song(name):
        path = MUSIC_PATH / name
        if not path.exists():
            return
        settings["last_music"] = name
        save_settings(settings)
        now_playing.setText(name)
        player.setSource(QUrl.fromLocalFile(str(path)))

    def play_song(name):
        load_song(name)
        player.play()
        movie.start()
        settings["music_paused"] = False
        save_settings(settings)

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

    # UI -------------------------------------------
    music_dir = Path.home() / "Music"
    music_hint = QLabel(f"🎵 Add music files to: {music_dir}")
    music_hint.setStyleSheet("color: #aaaaaa; font-size: 11px; padding-top: 4px; background-color: #1a1a1a;")
    music_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(music_hint)

    now_playing = QLabel("No music selected")
    now_playing.setStyleSheet("color: #ffffff; font-size: 13px; background-color: #1a1a1a;")
    now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(now_playing)

    player_label = QLabel()
    player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    movie = QMovie(str(PLAYER_PATH))
    movie.setScaledSize(QSize(125, 125))
    player_label.setStyleSheet("background-color: #1a1a1a;")
    player_label.setMovie(movie)
    layout.addWidget(player_label)

    play_btn = QPushButton("Play / Pause")
    play_btn.setFixedWidth(220)
    grey_button(play_btn)

    # Music progress slider
    progress_slider = QSlider(Qt.Orientation.Horizontal)
    progress_slider.setRange(0, 1000)
    progress_slider.setFixedWidth(440)
    progress_slider.setStyleSheet("""
        QSlider {background-color: #1a1a1a;}
        QSlider::groove:horizontal {
            height: 8px;
            background: #444;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            width: 14px;
            background: #00ffff;
            border-radius: 6px;
            margin: -3px 0;
        }
    """)
    layout.addWidget(progress_slider, alignment=Qt.AlignmentFlag.AlignHCenter)

    # music progress logic -------------------------------------------
    is_user_seeking = False
    def update_progress(position):
        if player.duration() > 0 and not is_user_seeking:
            progress_slider.setValue(
                int(position / player.duration() * 1000)
            )

    player.positionChanged.connect(update_progress)

    def slider_moved(value):
        if player.duration() > 0:
            new_pos = int(value / 1000 * player.duration())
            player.setPosition(new_pos)

    def slider_pressed():
        nonlocal is_user_seeking
        is_user_seeking = True

    def slider_released():
        nonlocal is_user_seeking
        is_user_seeking = False
        slider_moved(progress_slider.value())

    progress_slider.sliderPressed.connect(slider_pressed)
    progress_slider.sliderReleased.connect(slider_released)
    progress_slider.sliderMoved.connect(slider_moved)

    progress_slider.setEnabled(False)
    player.durationChanged.connect(
        lambda d: progress_slider.setEnabled(d > 0)
    )
    # -------------------------------------------

    volume_slider = QSlider(Qt.Orientation.Horizontal)
    volume_slider.setRange(0, 100)
    volume_slider.setFixedWidth(220)
    volume_slider.setStyleSheet("""
        QSlider {background-color: #1a1a1a;}
        QSlider::groove:horizontal { height: 8px; background: #444; border-radius: 4px; }
        QSlider::handle:horizontal { width: 16px; background: #00ffff; border-radius: 8px; margin: -4px 0; }
    """)

    list_btn = QPushButton("List")
    list_btn.setShortcut(QKeySequence("4"))
    list_btn.setFixedSize(80, 40)
    grey_button(list_btn)

    add_music_btn = QPushButton("Add")
    add_music_btn.setShortcut(QKeySequence("5"))
    add_music_btn.setFixedSize(80, 40)
    grey_button(add_music_btn)

    # Playback modes ---------------------------
    playback_mode = "repeat"

    mode_layout = QHBoxLayout()
    repeat_btn = QPushButton("Repeat")
    repeat_btn.setShortcut(QKeySequence("1"))
    juggle_btn = QPushButton("Juggle")
    juggle_btn.setShortcut(QKeySequence("2"))
    straight_btn = QPushButton("Straight")
    straight_btn.setShortcut(QKeySequence("3"))

    for btn in (repeat_btn, juggle_btn, straight_btn):
        grey_button(btn)
        btn.setFixedWidth(90)
        btn.setFixedHeight(40)

    mode_layout.addWidget(repeat_btn)
    mode_layout.addWidget(juggle_btn)
    mode_layout.addWidget(straight_btn)

    layout.addWidget(play_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
    layout.addLayout(mode_layout)
    layout.addSpacing(12)
    layout.addWidget(volume_slider, alignment=Qt.AlignmentFlag.AlignHCenter)
    
    list_add_layout = QHBoxLayout()
    list_add_layout.setSpacing(15)
    list_add_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    list_add_layout.addWidget(list_btn)
    list_add_layout.addWidget(add_music_btn)
    layout.addLayout(list_add_layout)

    def update_mode_buttons():
        for btn, mode in zip((repeat_btn, juggle_btn, straight_btn),
                             ("repeat", "juggle", "straight")):
            btn.setStyleSheet(btn.styleSheet().split("border:2px solid")[0] +
                              ("border:2px solid #ffff00;" if playback_mode == mode else ""))

    update_mode_buttons()

    def set_repeat():
        nonlocal playback_mode
        playback_mode = "repeat"
        print("repeat")
        update_mode_buttons()

    def set_juggle():
        nonlocal playback_mode
        playback_mode = "juggle"
        print("juggle")
        update_mode_buttons()

    def set_straight():
        nonlocal playback_mode
        playback_mode = "straight"
        print("straight")
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

    # Shortcuts -------------------------------
    QShortcut(QKeySequence(Qt.Key.Key_Up), page).activated.connect(
        lambda: volume_slider.setValue(min(volume_slider.value() + 5, 100))
    )
    QShortcut(QKeySequence(Qt.Key.Key_Down), page).activated.connect(
        lambda: volume_slider.setValue(max(volume_slider.value() - 5, 0))
    )
    QShortcut(QKeySequence(Qt.Key.Key_Space), page).activated.connect(
        lambda: toggle_play()
    )
    QShortcut(QKeySequence(Qt.Key.Key_Right), page).activated.connect(play_next)
    QShortcut(QKeySequence(Qt.Key.Key_Left), page).activated.connect(play_previous)

    # Restore state -------------
    audio.setVolume(settings.get("music_volume", 60) / 100)
    volume_slider.setValue(settings.get("music_volume", 60))

    if settings.get("last_music"):
        load_song(settings["last_music"])
        if settings.get("music_paused", True):
            movie.stop()

    # Controls --------------------------------------
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

    list_btn.clicked.connect(
        lambda: MusicPickerDialog(
            current_music=settings.get("last_music"),
            parent=page
        ).music_selected.connect(select_music)
    )

    back_btn = QPushButton("Back")
    back_btn.setFixedSize(140, 50)
    style_neon_button(back_btn)
    back_btn.setShortcut(QKeySequence(Qt.Key.Key_Escape))
    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))
    add_music_btn.clicked.connect(lambda: open_add_music_dialog(parent=page))

    layout.addStretch()
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def open_picker():
        dlg = MusicPickerDialog(
            current_music=settings.get("last_music"),
            parent=page
        )
        dlg.music_selected.connect(select_music)
        dlg.exec()

    list_btn.clicked.connect(open_picker)

    return page, back_btn
