# ui/settings_dialog.py
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QListWidget, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from utils.json_handler import load_json, save_json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORTCUTS_FILE = os.path.join(BASE_DIR, "config", "shortcuts.json")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(480, 360)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Shortcuts management list
        self.shortcuts_list = QListWidget()
        self.layout.addWidget(self.shortcuts_list)

        # Buttons row
        row = QHBoxLayout()
        add_btn = QPushButton("Add Shortcut")
        add_btn.clicked.connect(self.add_shortcut)
        row.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        row.addWidget(remove_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        row.addWidget(close_btn)

        self.layout.addLayout(row)

        self.load_shortcuts()

    def load_shortcuts(self):
        self.shortcuts_list.clear()
        shortcuts = load_json(SHORTCUTS_FILE)
        for name, url in shortcuts.items():
            self.shortcuts_list.addItem(f"{name} — {url}")

    def add_shortcut(self):
        name, ok = QInputDialog.getText(self, "New Shortcut", "Shortcut name:")
        if not ok or not name.strip():
            return
        url, ok = QInputDialog.getText(self, "New Shortcut", "URL (include https://):")
        if not ok or not url.strip():
            return
        # save
        shortcuts = load_json(SHORTCUTS_FILE)
        shortcuts[name.strip()] = url.strip()
        save_json(SHORTCUTS_FILE, shortcuts)
        self.load_shortcuts()

    def remove_selected(self):
        sel = self.shortcuts_list.currentItem()
        if not sel:
            return
        text = sel.text()
        # parse name — url
        name = text.split(" — ")[0].strip()
        shortcuts = load_json(SHORTCUTS_FILE)
        if name in shortcuts:
            del shortcuts[name]
            save_json(SHORTCUTS_FILE, shortcuts)
            self.load_shortcuts()
        else:
            QMessageBox.warning(self, "Remove Shortcut", "Could not find the selected shortcut.")