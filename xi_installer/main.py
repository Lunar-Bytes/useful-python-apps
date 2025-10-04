import sys, os, shutil, json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel,
    QMessageBox, QHBoxLayout, QFileDialog, QDialog, QCheckBox, QDialogButtonBox,
    QFormLayout, QLineEdit, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import win32com.client  # pip install pywin32

# ---------------- Resource path helper ----------------
def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller --onefile."""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- Custom Install Dialog ----------------
class CustomInstallDialog(QDialog):
    def __init__(self, app_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Xi Installer")
        self.setFixedSize(1280, 720)

        layout = QFormLayout()

        self.folder_input = QLineEdit()
        self.folder_input.setText(os.path.expanduser("~\\AppData\\Local\\XiApps"))
        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(120)
        browse_btn.clicked.connect(self.browse_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        layout.addRow("Install Location:", folder_layout)

        self.desktop_shortcut = QCheckBox("Create Desktop Shortcut")
        self.startmenu_shortcut = QCheckBox("Create Start Menu Shortcut")
        layout.addRow(self.desktop_shortcut)
        layout.addRow(self.startmenu_shortcut)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Install Location")
        if folder:
            self.folder_input.setText(folder)

    def get_options(self):
        return {
            "install_folder": self.folder_input.text(),
            "desktop_shortcut": self.desktop_shortcut.isChecked(),
            "startmenu_shortcut": self.startmenu_shortcut.isChecked()
        }

# ---------------- Xi Installer ----------------
class XiInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xi Installer")
        self.setGeometry(100, 100, 1280, 720)

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left panel
        left_panel = QVBoxLayout()
        title = QLabel("Available Programs")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.list = QListWidget()
        self.list.setFont(QFont("Arial", 14))
        self.list.setSpacing(5)
        self.list.setMinimumWidth(400)
        left_panel.addWidget(title)
        left_panel.addWidget(self.list)
        layout.addLayout(left_panel)

        # Right panel
        right_panel = QVBoxLayout()
        self.detail_title = QLabel("Select an app to see details")
        self.detail_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.detail_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setFixedSize(300, 300)
        self.preview_label = QLabel("App Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 12))
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_label)
        self.preview_frame.setLayout(preview_layout)

        self.detail_text = QLabel("")
        self.detail_text.setWordWrap(True)
        self.detail_text.setFont(QFont("Arial", 14))

        self.install_btn = QPushButton("Install Selected App")
        self.install_btn.setFont(QFont("Arial", 16))
        self.install_btn.setMinimumHeight(50)
        self.install_btn.setEnabled(False)

        right_panel.addWidget(self.detail_title)
        right_panel.addWidget(self.preview_frame)
        right_panel.addWidget(self.detail_text)
        right_panel.addStretch()
        right_panel.addWidget(self.install_btn)
        layout.addLayout(right_panel)

        # Load apps
        self.programs_dir = resource_path("programs")
        self.apps = self.scan_programs()
        for app in self.apps:
            self.list.addItem(app)

        self.installed_file = "installed.json"
        self.installed = self.load_installed()

        self.list.itemSelectionChanged.connect(self.show_details)
        self.install_btn.clicked.connect(self.install_app)

    # Scan embedded programs
    def scan_programs(self):
        apps = {}
        if not os.path.exists(self.programs_dir):
            os.makedirs(self.programs_dir)
        for file in os.listdir(self.programs_dir):
            if file.endswith(".exe"):
                path = os.path.join(self.programs_dir, file)
                apps[file] = path
        return apps

    def load_installed(self):
        if os.path.exists(self.installed_file):
            with open(self.installed_file, "r") as f:
                return json.load(f)
        return {}

    def save_installed(self):
        with open(self.installed_file, "w") as f:
            json.dump(self.installed, f, indent=4)

    def show_details(self):
        app_name = self.list.currentItem().text()
        status = "Installed" if app_name in self.installed else "Not Installed"
        self.detail_title.setText(app_name)
        self.detail_text.setText(f"Status: {status}\n\nLocation: {self.installed.get(app_name, 'Not installed yet')}")
        self.install_btn.setEnabled(True)

        preview_image_path = resource_path(os.path.join("programs", app_name.replace(".exe", ".png")))
        if os.path.exists(preview_image_path):
            pixmap = QPixmap(preview_image_path).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("App Preview")

    def install_app(self):
        app_name = self.list.currentItem().text()
        src_path = self.apps[app_name]

        dialog = CustomInstallDialog(app_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_options()
            target_dir = os.path.join(options["install_folder"], app_name.replace(".exe", ""))
            target_path = os.path.join(target_dir, app_name)

            try:
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy(src_path, target_path)

                self.installed[app_name] = target_path
                self.save_installed()

                if options["desktop_shortcut"]:
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    self.create_shortcut(target_path, os.path.join(desktop, app_name))

                if options["startmenu_shortcut"]:
                    self.create_start_menu_shortcut(target_path, app_name.replace(".exe", ""))

                QMessageBox.information(self, "Success", f"{app_name} installed to {target_dir}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to install {app_name}: {e}")

    def create_shortcut(self, target, shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path + ".lnk")
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.save()

    def create_start_menu_shortcut(self, target, app_name):
        shell = win32com.client.Dispatch("WScript.Shell")
        start_menu = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs")
        shortcut_path = os.path.join(start_menu, app_name + ".lnk")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.save()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XiInstaller()
    window.show()
    sys.exit(app.exec())
