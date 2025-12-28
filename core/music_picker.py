from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton,
    QScrollArea, QWidget
)
from PyQt6.QtCore import pyqtSignal
from core.path import MUSIC_PATH

class MusicPickerDialog(QDialog):
    music_selected = pyqtSignal(str)

    def __init__(self, parent=None, current_music=None):
        super().__init__(parent)
        self.setWindowTitle("Select Music")
        self.setFixedSize(600, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        list_layout = QVBoxLayout(container)
        list_layout.setContentsMargins(4, 4, 4, 4)
        list_layout.setSpacing(4)

        if MUSIC_PATH.exists():
            files = sorted(p.name for p in MUSIC_PATH.iterdir() if p.is_file())
            if files:
                for name in files:
                    btn = QPushButton(name)
                    btn.setFixedHeight(28)
                    if current_music and name == current_music:
                        btn.setStyleSheet("background-color: #00ffff; color: black;")
                    btn.clicked.connect(lambda _, n=name: self.select(n))
                    list_layout.addWidget(btn)
            else:
                list_layout.addWidget(QPushButton("No music files found."))
        else:
            list_layout.addWidget(QPushButton("Music folder does not exist."))

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def select(self, filename):
        self.music_selected.emit(filename)
        self.close()
