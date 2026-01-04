from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout, QMessageBox
from core.avatar_toggle import load_settings, save_settings

class CustomPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Custom GIF")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout(self)
        label = QLabel("Select a GIF file (empty to clear):")
        layout.addWidget(label)

        h_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        h_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        h_layout.addWidget(browse_btn)
        layout.addLayout(h_layout)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.save_and_close)
        layout.addWidget(ok_btn)

        self.load_existing_path()
        self.path_edit.returnPressed.connect(self.save_and_close)

    def load_existing_path(self):
        settings = load_settings()
        self.path_edit.setText(settings.get("custom", ""))

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GIF",
            "",
            "GIF Files (*.gif)"
        )
        if file_path:
            self.path_edit.setText(file_path)

    def save_and_close(self):
        path = self.path_edit.text().strip()
        settings = load_settings()

        if not path:
            if "custom" in settings:
                del settings["custom"]
            save_settings(settings)
            self.accept()
            return

        if not path.lower().endswith(".gif"):
            QMessageBox.warning(self, "Invalid file", "Only GIF files are allowed, darling!")
            return

        settings["custom"] = path
        save_settings(settings)
        self.accept()
