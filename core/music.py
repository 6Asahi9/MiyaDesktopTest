from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from pathlib import Path
from core.page_switch import switch_to_main
from core.path import MUSIC_PATH

def create_music_page(stack):
    page = QWidget()
    layout = QVBoxLayout(page)

    music_dir = Path.home() / "MiyaDesktop" / "Music"

    music_hint = QLabel(
        f"🎵 Add music files to:\n{music_dir}"
    )
    music_hint.setStyleSheet("""
        color: #888;
        font-size: 10px;
        padding-top: 4px;
    """)
    music_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(music_hint)


    back_btn = QPushButton("Back")
    back_btn.setFixedSize(120, 50)
    back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))
    layout.addWidget(back_btn)
    layout.addStretch()
    
    if MUSIC_PATH.exists():
        files = sorted(p.name for p in MUSIC_PATH.iterdir() if p.is_file())
        if files:
            for name in files:
                lbl = QLabel(f"• {name}")
                lbl.setStyleSheet("color: white; font-size: 11px;")
                layout.addWidget(lbl)
        else:
            layout.addWidget(QLabel("No music files found."))
    else:
        layout.addWidget(QLabel("Music folder does not exist."))

    return page
