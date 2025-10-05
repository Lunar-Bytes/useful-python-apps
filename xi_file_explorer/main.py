import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QListView, QTextEdit,
    QToolBar, QWidget, QHBoxLayout, QLineEdit, QSizePolicy,
    QMenu, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QFileSystemModel, QIcon, QAction, QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QDir


TEXT_EXTENSIONS = ['.txt', '.py', '.go', '.c', '.cpp', '.json', '.md', '.html', '.css', '.js']


# ---------------- Syntax Highlighter ---------------- #
class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, file_extension):
        super().__init__(document)
        self.rules = []
        self.file_extension = file_extension.lower()

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#D69D85"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        if self.file_extension == ".py":
            python_keywords = [
                "def", "class", "if", "elif", "else", "while", "for", "in",
                "try", "except", "finally", "import", "from", "as", "with",
                "return", "break", "continue", "pass", "lambda", "True", "False", "None"
            ]
            for kw in python_keywords:
                self.rules.append((re.compile(rf"\b{kw}\b"), keyword_format))
            self.rules.append((re.compile(r"#.*"), comment_format))
            self.rules.append((re.compile(r"(\".*?\"|'.*?')"), string_format))
            self.rules.append((re.compile(r"\b\d+(\.\d+)?\b"), number_format))
        elif self.file_extension in ['.c', '.cpp', '.go', '.json', '.md', '.html', '.css', '.js']:
            # simple coloring rules for other files
            self.rules.append((re.compile(r"(\".*?\"|'.*?')"), string_format))
            self.rules.append((re.compile(r"\b\d+(\.\d+)?\b"), number_format))
            self.rules.append((re.compile(r"//.*"), comment_format))
            self.rules.append((re.compile(r"/\*.*?\*/", re.DOTALL), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                self.setFormat(start, end - start, fmt)


# ---------------- File Explorer ---------------- #
class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xi Explorer")
        self.setGeometry(200, 100, 1200, 650)

        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        # Tree view (folders)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.homePath()))
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.clicked.connect(self.on_tree_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)

        # List view (files)
        self.list_view = QListView()
        self.list_view.setModel(self.model)
        self.list_view.setRootIndex(self.model.index(QDir.homePath()))
        self.list_view.setIconSize(QSize(48, 48))
        self.list_view.setSpacing(8)
        self.list_view.doubleClicked.connect(self.on_file_double_clicked)
        self.list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.open_context_menu)

        # Right panel placeholder (either file list or QTextEdit)
        self.right_panel = self.list_view

        # Split layout
        self.container = QWidget()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.tree, 2)
        self.layout.addWidget(self.right_panel, 4)
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Navigation history
        self.history = [QDir.homePath()]
        self.history_index = 0

        # Toolbar
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        back_action = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_action.triggered.connect(self.go_back)
        toolbar.addAction(back_action)

        forward_action = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_action.triggered.connect(self.go_forward)
        toolbar.addAction(forward_action)

        up_action = QAction(QIcon.fromTheme("go-up"), "Up", self)
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)

        home_action = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_action.triggered.connect(self.go_home)
        toolbar.addAction(home_action)

        # Address bar
        self.address_bar = QLineEdit(QDir.homePath())
        self.address_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.address_bar.returnPressed.connect(self.go_to_path)
        toolbar.addWidget(self.address_bar)

    # ================= Navigation =================
    def update_path(self, path):
        index = self.model.index(path)
        self.tree.setRootIndex(index)
        if isinstance(self.right_panel, QListView):
            self.right_panel.setRootIndex(index)
        self.address_bar.setText(path)

        if not self.history or self.history[self.history_index] != path:
            self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index += 1

    def on_tree_clicked(self, index):
        path = self.model.filePath(index)
        self.update_path(path)

    def go_home(self):
        self.update_path(QDir.homePath())

    def go_up(self):
        current = self.model.filePath(self.list_view.rootIndex())
        parent = QDir(current).absolutePath() + "/.."
        self.update_path(QDir(parent).absolutePath())

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.update_path(self.history[self.history_index])

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.update_path(self.history[self.history_index])

    def go_to_path(self):
        path = self.address_bar.text()
        if QDir(path).exists():
            self.update_path(path)

    # ================= Right-Click Menu =================
    def open_context_menu(self, position: QPoint):
        widget = self.sender()
        index = widget.indexAt(position)
        if not index.isValid():
            return
        file_path = self.model.filePath(index)

        menu = QMenu()
        create_file_action = QAction("New File", self)
        create_folder_action = QAction("New Folder", self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)

        create_file_action.triggered.connect(lambda: self.create_file(file_path))
        create_folder_action.triggered.connect(lambda: self.create_folder(file_path))
        rename_action.triggered.connect(lambda: self.rename_item(file_path))
        delete_action.triggered.connect(lambda: self.delete_item(file_path))

        menu.addAction(create_file_action)
        menu.addAction(create_folder_action)
        menu.addSeparator()
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        menu.exec(widget.viewport().mapToGlobal(position))

    # ================= File Actions =================
    def create_file(self, base_path):
        if os.path.isfile(base_path):
            base_path = os.path.dirname(base_path)
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            new_file_path = os.path.join(base_path, name)
            if not os.path.exists(new_file_path):
                with open(new_file_path, "w"):
                    pass

    def create_folder(self, base_path):
        if os.path.isfile(base_path):
            base_path = os.path.dirname(base_path)
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            new_folder_path = os.path.join(base_path, name)
            if not os.path.exists(new_folder_path):
                os.mkdir(new_folder_path)

    def rename_item(self, file_path):
        base_path = os.path.dirname(file_path)
        current_name = os.path.basename(file_path)
        name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=current_name)
        if ok and name:
            new_path = os.path.join(base_path, name)
            if not os.path.exists(new_path):
                os.rename(file_path, new_path)

    def delete_item(self, file_path):
        reply = QMessageBox.question(
            self, "Delete", f"Are you sure you want to delete:\n{file_path}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    os.rmdir(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete:\n{e}")

    # ================= Text Editor =================
    def on_file_double_clicked(self, index):
        file_path = self.model.filePath(index)
        _, ext = os.path.splitext(file_path)
        if ext.lower() in TEXT_EXTENSIONS and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                content = ""

            # Replace right panel with QTextEdit
            if hasattr(self, 'text_editor'):
                self.layout.removeWidget(self.text_editor)
                self.text_editor.deleteLater()

            self.text_editor = QTextEdit()
            self.text_editor.setText(content)
            self.right_panel = self.text_editor
            self.layout.addWidget(self.right_panel, 4)

            # Apply syntax highlighting
            self.highlighter = CodeHighlighter(self.text_editor.document(), ext)

            # Save on focus out
            self.text_editor.focusOutEvent = lambda event, path=file_path: self.save_text(path, event)

        else:
            # If non-text file, restore list view
            if self.right_panel != self.list_view:
                self.layout.removeWidget(self.right_panel)
                self.right_panel.deleteLater()
                self.right_panel = self.list_view
                self.layout.addWidget(self.right_panel, 4)

    def save_text(self, path, event):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
        super(QTextEdit, self.text_editor).focusOutEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark theme
    from PyQt6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    window = FileExplorer()
    window.show()
    sys.exit(app.exec())
