import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout,
    QFileDialog, QTabWidget, QSplitter, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QTextCursor


class SystemLogViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_log_path = self._generate_log_filename()

        self.setStyleSheet("""
            QWidget {
                background-color: #0c0c0d;
                color: #1e1e21;
                font-family: Adwaita Sans;
            }
            QTextEdit {
                background-color: #1e1e21;
                color: #f1f3f3;
                font-family: Adwaita Mono;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1e1e21;
                color: #f1f3f3;
                padding: 10px;
                font-weight: normal;
                border-radius: 5px;
                margin: 4px;
            }
            QTabBar::tab:selected {
                background: #7a63ff;
                color: white;
            }
            QPushButton {
                background-color: #1e1e21;
                color: #f1f3f3;
                padding: 5px 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #74e1ef;
                color: #0c0c0d;
            }
            QLabel#title {
                font-size: 24px;
                color: #f1f3f3;
            }
            QLabel#status {
                font-size: 12px;
                color: #888;
            }
            QLineEdit {
                background-color: #1e1e21;
                color: #f1f3f3;
                border: 1px solid #f1f3f3;
                padding: 6px;
                border-radius: 6px;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: #0c0c0d;
                border: 2px solid #1e1e21;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #7a63ff;
                min-height: 10px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #f1f3f3;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                background: #0c0c0d;
                border: 2px solid #1e1e21;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #7a63ff;
                min-height: 10px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #f1f3f3;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        # === TOP BAR ===
        top_layout = QHBoxLayout()
        self.title = QLabel("📄 System Logs \n– Current Session")
        #self.title.setWordWrap(True)
        self.title.setObjectName("title")

        self.status = QLabel()
        self.status.setObjectName("status")
        self._update_status_time()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_status_time)
        self._timer.start(1000)

        top_layout.addWidget(self.title)
        top_layout.addStretch()
        top_layout.addWidget(self.status)

        # === LEFT TAB BAR ===
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tab_editors = {}

        for tag in ["ALL", "INFO", "WARN", "ERROR", "DEBUG"]: # <--- TODO: FIX FOR MAIN APP
            editor = QTextEdit()
            editor.setReadOnly(True)
            editor.setLineWrapMode(QTextEdit.NoWrap)
            editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.tabs.addTab(editor, tag)
            self.tab_editors[tag] = editor

        # === CONTROL BUTTONS ===
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_logs)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_logs)

        self.load_btn = QPushButton("Load...")
        self.load_btn.clicked.connect(self.load_logs)

        controls = QHBoxLayout()
        controls.addStretch()
        controls.addWidget(self.clear_btn)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.load_btn)

        # === LAYOUT SPLITTER ===
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tabs)

        # Right panel with fixed max width
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 10, 20, 10)
        right_layout.setSpacing(10)
        right_layout.addLayout(top_layout)
        right_layout.addStretch()
        right_layout.addLayout(controls)
        # === Search Bar ===
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search logs...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.apply_search)
        right_layout.addWidget(self.search_bar)

        right_container.setMaximumWidth(800)  # Control stretch on wide screens <--- TODO: FIX FOR MAIN APP
        splitter.addWidget(right_container)
        splitter.setSizes([2000, 500])  # Sidebar, content area <--- TODO: FIX FOR MAIN APP

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)

        self.auto_scroll = True

    def _generate_log_filename(self):
        now = datetime.now().strftime("session_%Y-%m-%d_%H-%M-%S.log")
        return os.path.join(self.log_dir, now)

    def _update_status_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status.setText(f"🕒 {now}")

    def log(self, message, level="INFO"):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        entry = f"[{timestamp}] [{level.upper()}] {message}"

        color_map = {  # <--- TODO: FIX FOR MAIN APP
            "INFO": "#e0e0e0",
            "WARN": "#ffcc00",
            "ERROR": "#ff4444",
            "DEBUG": "#00c8ff"
        }
        color = color_map.get(level.upper(), "#e0e0e0") # <--- TODO: FIX FOR MAIN APP

        # HTML formatted line
        html_entry = f"<span style='color:{color}'>{entry}</span>"

        # Add to ALL tab and specific category
        self.tab_editors["ALL"].append(html_entry)
        if level.upper() in self.tab_editors:
            self.tab_editors[level.upper()].append(html_entry)

        """# Save raw entry to log file
        with open(self.session_log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")"""

        if self.auto_scroll:
            current_editor = self.tab_editors[self.tabs.tabText(self.tabs.currentIndex())]
            current_editor.moveCursor(QTextCursor.End)

    def clear_logs(self):
        for editor in self.tab_editors.values():
            editor.clear()

    def save_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs As", self.log_dir, "Log Files (*.log)")
        if file_path:
            content = self.tab_editors["ALL"].toPlainText()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def load_logs(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Log File", self.log_dir, "Log Files (*.log)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            self.clear_logs()   # # <--- TODO: FIX FOR MAIN APP
            for line in lines:
                level = "INFO"
                if "[ERROR]" in line:
                    level = "ERROR"
                elif "[WARN]" in line:
                    level = "WARN"
                elif "[DEBUG]" in line:
                    level = "DEBUG"
                self.log(line.strip(), level=level)
    
    def apply_search(self, text):
        current_tab = self.tabs.tabText(self.tabs.currentIndex())
        editor = self.tab_editors[current_tab]

        cursor = editor.textCursor()
        document = editor.document()

        # Reset formatting across the whole document
        #cursor.select(QTextCursor.Document)
        #cursor.setCharFormat(editor.currentCharFormat())

        if not text:
            return  # Nothing to highlight

        # Highlight matches
        #highlight_format = editor.currentCharFormat()
        #highlight_format.setBackground(Qt.yellow)

        # Start searching from the top
        cursor = document.find(text, 0)
        match_found = False

        while not cursor.isNull():
            #cursor.mergeCharFormat(highlight_format)
            if not match_found:
                editor.setTextCursor(cursor)  # Scroll to first match
                match_found = True
            cursor = document.find(text, cursor.position())


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    viewer = SystemLogViewer()
    viewer.setWindowTitle("DriveCore – System Log Dashboard")
    viewer.resize(1280, 720)
    viewer.show()

    # Simulated logs
    viewer.log("DriveCore boot sequence complete.", "INFO")
    viewer.log("Network handshake initialized.", "DEBUG")
    viewer.log("Brake command issued!", "WARN")
    viewer.log("ESC disconnected!", "ERROR")

    sys.exit(app.exec())