from PyQt6.QtWebEngineWidgets import QWebEngineView  # only the view
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile  # page & profile
from PyQt6.QtCore import QUrl
import os
import json

# Paths inside cookie_manager, no import from main.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
COOKIES_FILE = os.path.join(CONFIG_DIR, "cookies.json")
USER_DATA_DIR = os.path.join(CONFIG_DIR, "user_data")
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Keep your CookieManager class as-is (for JSON backup/export)
class CookieManager:
    def __init__(self, profile: QWebEngineProfile):
        self.profile = profile
        self.store = self.profile.cookieStore()
        # existing code to hook cookieAdded signal, etc.

    def load_cookies(self):
        # your existing JSON loading logic (best-effort)
        pass

    def save_cookies_now(self):
        # your existing save logic
        pass


# Optional helper to create a persistent profile
def create_persistent_profile(name="XIProfile"):
    profile = QWebEngineProfile(name)
    profile.setPersistentStoragePath(USER_DATA_DIR)
    profile.setCachePath(USER_DATA_DIR)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    return profile
