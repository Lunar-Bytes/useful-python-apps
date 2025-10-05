# ui/start_page.py
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from utils.json_handler import load_json, save_json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORTCUTS_FILE = os.path.join(BASE_DIR, "config", "shortcuts.json")

# default shortcuts if none present
DEFAULT_SHORTCUTS = {
    "Google": "https://www.google.com",
    "YouTube": "https://www.youtube.com",
    "GitHub": "https://github.com",
    "Reddit": "https://www.reddit.com",
    "StackOverflow": "https://stackoverflow.com",
}

class XIStartPage(QWidget):
    def __init__(self, parent_browser=None):  # <-- FIX: allow parent_browser argument
        super().__init__()
        self.parent_browser = parent_browser
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        title = QLabel("XI Browser")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; color: #E6E6E6;")
        self.layout.addWidget(title)

        # Sub-title / instructions
        sub = QLabel("Click a shortcut to open it in a new tab. You can add/remove shortcuts via Settings.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #a9a9a9; margin-bottom: 24px;")
        self.layout.addWidget(sub)

        # Grid area for shortcuts (centered)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_container.setLayout(self.grid_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.grid_container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch()

        self.load_shortcuts()

    def load_shortcuts(self):
        # Load json, fallback to defaults if empty
        shortcuts = load_json(SHORTCUTS_FILE)
        if not shortcuts:
            shortcuts = DEFAULT_SHORTCUTS.copy()
            save_json(SHORTCUTS_FILE, shortcuts)

        # Clear existing grid widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Create up-to-9 shortcut buttons in 3x3
        positions = [(i, j) for i in range(3) for j in range(3)]
        items = list(shortcuts.items())
        for pos, entry in zip(positions, items):
            name, url = entry
            btn = QPushButton(name)
            btn.setFixedSize(QSize(100, 100))
            btn.setStyleSheet("""
                background-color: #00c853;
                font-weight: bold;
                border-radius: 8px;
                color: #081013;
            """)
            if self.parent_browser:  # <-- only if browser exists
                btn.clicked.connect(lambda checked=False, url=url: self.parent_browser.add_tab(url=url))
            self.grid_layout.addWidget(btn, *pos)

        # Fill remaining slots with empty placeholders
        used = len(items)
        for pos in positions[used:]:
            ph = QLabel("")
            ph.setFixedSize(QSize(100, 100))
            ph.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.grid_layout.addWidget(ph, *pos)