# ui/tab_browser.py
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtCore import QUrl

class XIWebEngine(QWebEngineView):
    def __init__(self, profile: QWebEngineProfile = None, url: str = "https://www.google.com"):
        super().__init__()
        if profile is None:
            profile = QWebEngineProfile.defaultProfile()
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        self.setUrl(QUrl(url))
