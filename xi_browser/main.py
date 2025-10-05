# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineCore import QWebEngineProfile

from ui.start_page import XIStartPage
from ui.tab_browser import XIWebEngine
from ui.settings_dialog import SettingsDialog
from utils.json_handler import load_json, save_json
from utils.cookie_manager import create_persistent_profile, CookieManager

# Config paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SHORTCUTS_FILE = os.path.join(CONFIG_DIR, "shortcuts.json")
COOKIES_FILE = os.path.join(CONFIG_DIR, "cookies.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
USER_DATA_DIR = os.path.join(CONFIG_DIR, "user_data")  # for persistent profile
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Ensure config files exist
for p in [SHORTCUTS_FILE, COOKIES_FILE, SETTINGS_FILE]:
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        save_json(p, {})


class XIBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XI Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #111214; color: #E6E6E6; }
            QToolBar { background-color: #18191a; spacing: 6px; padding: 6px; }
            QLineEdit { background-color: #222; color: #fff; border-radius: 6px; padding: 6px; min-width: 300px; }
            QPushButton { border-radius: 6px; }
        """)

        # Shared persistent profile for all tabs
        self.profile = create_persistent_profile("XIProfile")
        self.cookie_manager = CookieManager(self.profile)
        self.cookie_manager.load_cookies()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        # Top navigation bar
        self.nav_bar = QToolBar()
        self.addToolBar(self.nav_bar)
        self._setup_topbar()

        # Start page as first tab
        self.add_tab(start_page=True)

    def _setup_topbar(self):
        back_action = QAction("◀", self)
        back_action.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.nav_bar.addAction(back_action)

        forward_action = QAction("▶", self)
        forward_action.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.nav_bar.addAction(forward_action)

        reload_action = QAction("↻", self)
        reload_action.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.nav_bar.addAction(reload_action)

        # URL / Search bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.addWidget(self.url_bar)

        new_tab_action = QAction("＋", self)
        new_tab_action.triggered.connect(lambda: self.add_tab())
        self.nav_bar.addAction(new_tab_action)

        settings_action = QAction("⚙", self)
        settings_action.triggered.connect(self.open_settings)
        self.nav_bar.addAction(settings_action)

    def current_browser(self) -> XIWebEngine | None:
        widget = self.tabs.currentWidget()
        if isinstance(widget, XIWebEngine):
            return widget
        return None

    def add_tab(self, url: str = "https://www.google.com", start_page: bool = False):
        if start_page:
            page = XIStartPage(parent_browser=self)
            self.tabs.addTab(page, "Start")
            self.tabs.setCurrentWidget(page)
        else:
            browser = XIWebEngine(profile=self.profile)
            browser.setUrl(QUrl(url))
            browser.urlChanged.connect(lambda qurl: self.on_url_changed(qurl))
            self.tabs.addTab(browser, "New Tab")
            self.tabs.setCurrentWidget(browser)

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text and not text.startswith("http"):
            url = "https://" + text
        elif text.startswith("http"):
            url = text
        else:
            from urllib.parse import quote_plus
            url = f"https://www.google.com/search?q={quote_plus(text)}"
        cb = self.current_browser()
        if cb:
            cb.setUrl(QUrl(url))
        else:
            self.add_tab(url=url)

    def on_url_changed(self, qurl):
        if isinstance(self.tabs.currentWidget(), XIWebEngine):
            self.url_bar.setText(qurl.toString())

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        widget = self.tabs.currentWidget()
        if widget and widget.__class__.__name__ == "XIStartPage":
            widget.load_shortcuts()

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if isinstance(widget, XIWebEngine):
            self.url_bar.setText(widget.url().toString())
        else:
            self.url_bar.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XIBrowser()
    window.show()
    sys.exit(app.exec())
