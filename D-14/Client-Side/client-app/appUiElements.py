import sys
import requests
from bs4 import BeautifulSoup
import webbrowser
import math

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication,
    QScrollArea, QFrame, QHBoxLayout,QTextEdit,QFileDialog, 
    QTabWidget, QSplitter, QSizePolicy, QLineEdit,QGroupBox,
    QDoubleSpinBox, QFormLayout, QSlider, QSpinBox, QSpacerItem,
    QTextBrowser)

from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, QRectF

from PySide6.QtGui import (QFont, QTextCursor, QPainter, QColor,
    QConicalGradient, QPen, QPainterPath)

import os

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_SCALE_FACTOR"] = "0.95"

#! IMPORTANT:
'''
- All of these Widgets do not have interactive signals yet
- Everything is held together with duct tape
- Ver 1.3 is needed for Client to Host communication
'''

class GitHubInfoPanel(QWidget):
    """
    A widget that displays GitHub repository information including a description and latest release.
    
    @param repo_url: URL to the GitHub repository.
    """
    def __init__(self, repo_url="https://github.com/HalfasleepDev/DriveCore"):
        
        super().__init__()
        self.repo_url = repo_url
        self.repo_owner, self.repo_name = self._parse_repo_url(repo_url)
        self.setObjectName(u"projectInfoCard")

        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QWidget {
                background-color: #74e1ef;  /* light cyan */
            }
            QLabel {
                color: #0c0c0d;
                font-family: 'Adwaita Sans';
            }
            QScrollArea {
                border: none;
            }
            QFrame#line {
                background-color: #f1f3f3;
                height: 1px;
                margin-top: 4px;
                margin-bottom: 8px;
            }
            QPushButton {
                background-color: #1e1e21;
                color: #f1f3f3;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # === About ===
        layout.addWidget(self._section_title("About"))
        layout.addWidget(self._divider())

        self.about_scroll = self._create_scrollable_label()
        layout.addWidget(self.about_scroll, 3)

        # === Releases ===
        layout.addWidget(self._section_title("Latest Release"))
        layout.addWidget(self._divider())

        self.release_scroll = self._create_scrollable_label()
        layout.addWidget(self.release_scroll, 1)

        # === Button to open GitHub
        self.button = QPushButton("View on GitHub")
        self.button.clicked.connect(lambda: webbrowser.open(self.repo_url))
        layout.addWidget(self.button, alignment=Qt.AlignRight)

        # Load data on delay
        QTimer.singleShot(100, self.load_github_info)

    def _section_title(self, text):
        label = QLabel(text)
        label.setFont(QFont("Adwaita Sans", 15))
        return label

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("line")
        return line

    def _create_scrollable_label(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        label = QLabel("Loading...")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        label.setContentsMargins(5, 5, 5, 5)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.addWidget(label)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(wrapper)
        scroll.text_label = label  # attach for external access
        return scroll

    def _parse_repo_url(self, url):
        parts = url.rstrip("/").split("/")
        return parts[-2], parts[-1]

    def load_github_info(self):
        try:
            # --- Description via Open Graph ---
            metadata = self.fetch_preview_metadata(self.repo_url)
            aboutStr = metadata["title"].replace("GitHub - HalfasleepDev/DriveCore: ", "").strip()
            self.about_scroll.text_label.setText(aboutStr)

            # --- Release Info ---
            release = self.fetch_latest_release()
            if release:
                published = release["published_at"]
                if "T" in published:
                    published = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
                release_text = f"• <b>{release['tag_name']}</b> – {release['name']}<br><i>Published: {published}</i>"
            else:
                release_text = "No public releases found."
            
            '''if metadata["image"]:
                image_data = requests.get(metadata["image"]).content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.width(), self.image_label.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))'''

            self.release_scroll.text_label.setText(release_text)

        except Exception as e:
            self.about_scroll.text_label.setText("Failed to load repository info.")
            self.release_scroll.text_label.setText(str(e))
            print("GitHubInfoPanel Error:", e)

    def fetch_preview_metadata(self, repo_url):
        response = requests.get(repo_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        def get_meta(prop):
            tag = soup.find("meta", property=prop)
            return tag["content"] if tag else ""

        return {
            "title": get_meta("og:title"),
            "description": get_meta("og:description"),
            'image': get_meta('og:image'),
            "url": get_meta("og:url")
        }

    def fetch_latest_release(self):
        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return {
                "tag_name": data.get("tag_name", "v?"),
                "name": data.get("name", "Untitled"),
                "published_at": data.get("published_at", "")
            }
        return None

class SystemLogViewer(QWidget):
    """
    A tabbed system log viewer for categorized logging during a session.
    Includes searching, saving, and loading logs.
    """
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
        self.status.setFixedWidth(150)
        self._update_status_time()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_status_time)
        self._timer.start(1000)

        top_layout.addWidget(self.title)
        top_layout.addStretch()
        top_layout.addWidget(self.status,0, Qt.AlignmentFlag.AlignCenter)

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
        right_layout.setContentsMargins(20, 5, 10, 5)
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
        splitter.setSizes([2000, 400])  # Sidebar, content area <--- TODO: FIX FOR MAIN APP

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)

        self.auto_scroll = True

    def _generate_log_filename(self):
        """
        Generates a timestamped filename for the current log session.
        """
        now = datetime.now().strftime("session_%d-%m-%Y_%H-%M-%S.log")
        return os.path.join(self.log_dir, now)

    def _update_status_time(self):
        """
        Updates the timestamp in the UI to reflect the current system time.
        """
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.status.setText(f"🕒 {now}")

    def log(self, message, level="INFO"):
        """
        Logs a message with a specific severity level to the UI.
        
        @param message: The log message text.
        @param level: Log level (INFO, WARN, ERROR, DEBUG).
        """
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
        """
        Clears all logs from the UI.
        """
        for editor in self.tab_editors.values():
            editor.clear()

    def save_logs(self):
        """
        Saves the current session logs to a file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs As", self.log_dir, "Log Files (*.log)")
        if file_path:
            content = self.tab_editors["ALL"].toPlainText()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def load_logs(self):
        """
        Loads logs from a selected file and displays them in the log viewer.
        """
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
        """
        Filters and highlights matching text in the log viewer.
        
        @param text: Search string to highlight in logs.
        """
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

class ServoCenterTuner(QGroupBox):
    """
    A UI component for fine-tuning the servo center pulse width (µs).
    
    @param on_send_callback: Optional callback for live servo updates.
    """
    def __init__(self, on_send_callback=None):
        super().__init__("Fine Tune Servo Center")
        self.on_send = on_send_callback

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(900, 2100)
        self.slider.setValue(1500)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self._slider_moved)

        self.display = QLabel("Current µs: 1500")
        self.display.setAlignment(Qt.AlignCenter)

        btns = QHBoxLayout()
        self.set_btn = QPushButton("Set as Mid")
        self.set_btn.setMinimumSize(QSize(0, 25))
        self.reset_btn = QPushButton("Reset to 1500")
        self.reset_btn.setMinimumSize(QSize(0, 25))
        btns.addWidget(self.set_btn)
        btns.addWidget(self.reset_btn)

        self.set_btn.clicked.connect(self._save_mid)
        self.reset_btn.clicked.connect(lambda: self._update(1500))

        layout.addWidget(self.slider)
        layout.addWidget(self.display)
        layout.addLayout(btns)

        self._saved_mid = 1500

    def _slider_moved(self, val):
        """
        Updates the servo value when the slider is moved.
        
        @param val: Current slider value.
        """
        self._update(val)

    def _update(self, val):
        """
        Updates the display and emits the on_send callback.

        @param val: µs value to set.
        """
        self.slider.setValue(val)
        self.display.setText(f"Current µs: {val}")
        if self.on_send:
            self.on_send(val)

    def _save_mid(self):
        """
        Saves the current slider value as the servo midpoint.
        """
        self._saved_mid = self.slider.value()
        print(f"[Servo Cal] Midpoint saved as: {self._saved_mid} µs")

    def get_mid_value(self):
        """
        Returns the currently saved midpoint value.
        """
        return self._saved_mid

class CalibrationWidget(QWidget):
    """
    Main widget for calibrating servo and ESC settings.
    Also includes port configuration and curve placeholders.
    """
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QSpinBox {
                font-family: 'Adwaita Sans';
                font-size: 15px;
                padding: 4px;
                padding-left: 5px;
                border-width: 3px;
                background: #f1f3f3;
                color: #1e1e21;
                border-radius: 5px;
                border: none;
            }
            QSpinBox::up-button,
            QSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                background: #1e1e21;
                border: none;
                border-radius: 5px;
                margin: 1px;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 2px solid #f1f3f3;
                margin: 1px;
            }

            QSpinBox::down-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 2px solid #f1f3f3;
                margin: 1px;
            }
            /* Hover effects (optional) */
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #7a63ff;
            }
                           
            QDoubleSpinBox {
                font-family: 'Adwaita Sans';
                font-size: 15px;
                padding: 4px;
                padding-left: 5px;
                border-width: 3px;
                background: #f1f3f3;
                color: #1e1e21;
                border-radius: 5px;
                border: none;
            }
            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                background: #1e1e21;
                border: none;
                border-radius: 5px;
                margin: 1px;
            }
            QDoubleSpinBox::up-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 2px solid #f1f3f3;
                margin: 1px;
            }

            QDoubleSpinBox::down-arrow {
                width: 0;
                height: 3;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 2px solid #f1f3f3;
                margin: 1px;
            }
            /* Hover effects (optional) */
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: #7a63ff;
            }
                              
            QSlider::handle:horizontal{
                background: #7a63ff;
                width: 10px;
                margin: -5px -1px;
                border-radius: 5px;
            }
            QSlider::add-page:horizontal{
                background: #f1f3f3;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal{
                background: #7a63ff;
                border-radius: 2px;
            }
            QLabel {
                font-family: 'Adwaita Sans';
                font-size: 15px;
                color: #f1f3f3;
            }
            QLabel#headerTitle {
                font-family: 'Adwaita Sans';
                font-size: 20px;
                color: #f1f3f3;
            }             
            QGroupBox {
                background-color: #1e1e21;
                border-radius: 5px;
                color: #f1f3f3;
                font-family: 'Adwaita Sans';
                font-size: 15px;
                margin-top: 30px;
            }
            QGroupBox::title {
                font-size: 15px;
                color: #f1f3f3;
                font-family: 'Adwaita Sans';
            }
            QPushButton {
                font-family: 'Adwaita Sans';
                background-color: #f1f3f3;
                color: #0c0c0d;
                border-radius: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            
        """)

        main_layout = QVBoxLayout(self)
        self.headerTitle = QLabel("Vehicle Tuning")
        self.headerTitle.setObjectName("headerTitle")
        self.headerTitle.setMinimumSize(QSize(0, 30))
        self.headerTitle.setMaximumSize(QSize(16777215, 35))
        font1 = QFont()
        font1.setPointSize(15)
        self.headerTitle.setFont(font1)
        main_layout.addWidget(self.headerTitle)

        self.headerLine = QFrame()
        self.headerLine.setFrameShape(QFrame.Shape.HLine)
        self.headerLine.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(self.headerLine, 0 , Qt.AlignmentFlag.AlignVCenter)

        # === Servo Calibration ===
        servo_group = QGroupBox("Servo Calibration (µs):")
        font2 = QFont()
        font2.setPointSize(15)
        servo_group.setFont(font2)
        servo_layout = QVBoxLayout()
        servo_form = QFormLayout()

        self.servo_min = QDoubleSpinBox()
        self.servo_min.setRange(500, 2500)
        self.servo_min.setValue(900)

        self.servo_max = QDoubleSpinBox()
        self.servo_max.setRange(500, 2500)
        self.servo_max.setValue(2100)

        servo_form.addRow("Min:", self.servo_min)
        servo_form.addRow("Max:", self.servo_max)

        self.servo_mid_tuner = ServoCenterTuner(self.preview_servo)
        servo_layout.addLayout(servo_form)
        servo_layout.addWidget(self.servo_mid_tuner)

        servo_test_btn = QPushButton("Test Servo")
        servo_test_btn.setMinimumSize(QSize(0, 25))
        servo_test_btn.clicked.connect(self.test_servo)
        servo_layout.addWidget(servo_test_btn)

        servo_group.setLayout(servo_layout)
        main_layout.addWidget(servo_group, 0, Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer1 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self.verticalSpacer1)

        # === ESC Calibration ===
        esc_group = QGroupBox("ESC Calibration (µs):")
        esc_form = QFormLayout()

        self.esc_min = QDoubleSpinBox()
        self.esc_min.setRange(500, 2500)
        self.esc_min.setValue(1310)

        self.esc_mid = QDoubleSpinBox()
        self.esc_mid.setRange(500, 2500)
        self.esc_mid.setValue(1500)

        self.esc_max = QDoubleSpinBox()
        self.esc_max.setRange(500, 2500)
        self.esc_max.setValue(1750)

        esc_form.addRow("Min:", self.esc_min)
        esc_form.addRow("Mid:", self.esc_mid)
        esc_form.addRow("Max:", self.esc_max)

        esc_test_btn = QPushButton("Test ESC")
        esc_test_btn.setMinimumSize(QSize(0, 25))
        esc_test_btn.clicked.connect(self.test_esc)
        esc_form.addRow(esc_test_btn)

        esc_group.setLayout(esc_form)
        main_layout.addWidget(esc_group, 0, Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self.verticalSpacer2)

        # === Network Port Settings ===
        port_group = QGroupBox("Network Port Configuration:")
        port_layout = QFormLayout()

        font3 = QFont()
        font3.setPointSize(8)
        font3.setItalic(True)
        font3.setWeight(QFont.Weight.Thin)

        self.comm_port = QSpinBox()
        self.comm_port.setRange(1024, 65535)
        self.comm_port.setValue(4444)  # Default or current communication port

        self.cam_port = QSpinBox()
        self.cam_port.setRange(1024, 65535)
        self.cam_port.setValue(5000)  # Default or current camera stream port

        self.comm_label = QLabel(f"Current: {self.comm_port.value()}")
        self.comm_label.setFont(font3)
        self.cam_label = QLabel(f"Current: {self.cam_port.value()}")
        self.cam_label.setFont(font3)

        # Apply button
        apply_btn = QPushButton("Apply Port Settings")
        apply_btn.setMinimumSize(QSize(0, 25))
        apply_btn.clicked.connect(self.apply_port_settings)

        port_layout.addRow("Comm Port:", self.comm_port)
        port_layout.addRow(self.comm_label)
        port_layout.addRow("Webcam Port:", self.cam_port)
        port_layout.addRow(self.cam_label)
        port_layout.addRow(apply_btn)

        port_group.setLayout(port_layout)
        main_layout.addWidget(port_group, 0, Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer3 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self.verticalSpacer3)

        # === Future Curve Configuration ===
        curve_group = QGroupBox("Acceleration / Deceleration Curves:")
        curve_layout = QVBoxLayout()
        curve_note = QLabel("Curve shaping will allow smooth acceleration profiles (coming soon).")
        curve_note.setWordWrap(True)
        curve_layout.addWidget(curve_note)
        curve_group.setLayout(curve_layout)

        main_layout.addWidget(curve_group, 0, Qt.AlignmentFlag.AlignVCenter)

        main_layout.addStretch()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(9, 0, 9, 0)

    # === Preview callbacks ===
    def preview_servo(self, value):
        """
        Placeholder for previewing live servo values.

        @param value: µs value for live servo preview.
        """
        print(f"[Preview] Sending servo test µs: {value}")
        # TODO: Send live µs to servo

    def test_servo(self):
        """
        Prints out the current servo min, mid, and max values for testing.
        """
        print("[TEST] Servo Calibration:")
        print(f"Min: {self.servo_min.value()} µs")
        print(f"Mid: {self.servo_mid_tuner.get_mid_value()} µs")
        print(f"Max: {self.servo_max.value()} µs")

    def test_esc(self):
        """
        Prints out the current ESC min, mid, and max values for testing.
        """
        print("[TEST] ESC Calibration:")
        print(f"Min: {self.esc_min.value()} µs")
        print(f"Mid: {self.esc_mid.value()} µs")
        print(f"Max: {self.esc_max.value()} µs")
    
    def apply_port_settings(self):
        """
        Applies the communication and camera port settings from the UI.
        """
        comm = self.comm_port.value()
        cam = self.cam_port.value()
        self.comm_label.setText(f"Current: {comm}")
        self.cam_label.setText(f"Current: {cam}")
        print(f"[PORT] Comm: {comm} | Webcam: {cam}")
        # TODO: Send updated config to networking system

class DescriptionWidget(QWidget):
    """
    Displays a markdown-based description from a file using QTextBrowser.
    
    @param markdown_text_filepath: Path to the markdown file.
    """
    def __init__(self, markdown_text_filepath="D-14/Client-Side/client-app/markdown-descriptions/file.md"):
        super().__init__()
        self.setObjectName("descriptionCard")

        # === Markdown Display ===
        markdown_text = self.load_markdown(markdown_text_filepath)
        self.markdown_view = QTextBrowser()
        self.markdown_view.setOpenExternalLinks(True)
        self.markdown_view.setMarkdown(markdown_text)
        self.markdown_view.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                color: #0c0c0d;
                font-family: 'Adwaita Sans';
                font-size: 11pt;
                border: none;
            }
            QScrollBar:vertical {
                background: #1e1e21;
                width: 8px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #7a63ff;
                min-height: 20px;
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
        """)
        self.markdown_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # === Layout ===
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        layout.addWidget(self.markdown_view)

    def load_markdown(self, filepath: str) -> str:
        """
        Loads markdown text from a file.

        @param filepath: Path to the .md file.
        @return: Raw markdown string.
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()

class LogConsoleWidget(QWidget):
    """
    A compact log viewer widget with scrollable text output and a clear button.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.setMaximumSize(620, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e21;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(6)

        # === Scrollable log viewer ===
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Adwaita Mono", 10)) # TODO: Fix fornt for Ver 1.2
        # TODO: Fix the border-radius for Ver 1.2
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0d;
                color: #f1f3f3;
                border: 1px solid #0c0c0d;
                border-radius: 10px;
                padding: 10px;
            }
            QScrollBar:vertical {
                background: #1e1e21;
                width: 8px;
                margin: 4px 2px 4px 2px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #7a63ff;
                min-height: 20px;
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
        """)

        # === Clear button with modern style ===
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f3;
                color: #0c0c0d;
                padding: 8px 14px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            QPushButton:pressed {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
        """)

        layout.addWidget(self.log_output)
        layout.addWidget(self.clear_button, alignment=Qt.AlignCenter)

    def add_log(self, message: str):
        """
        Append a log message to the console output.

        @param message: Text to display in the log console.
        """
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        """
        Clears all log text from the console.
        """
        self.log_output.clear()

class DriveAssistWidget(QWidget):
    """
    A widget that toggles Drive Assist mode and displays high-priority warnings with flashing animation.
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e21;
                border-radius: 15px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # === Assist Toggle Section ===
        self.toggle_button = QPushButton("Drive Assist: OFF")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f3;
                color: #0c0c0d;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
            QPushButton:checked {
                background-color: #7a63ff;
                color: #f1f3f3;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_assist)

        # === Warning Section ===
        self.warning_label = QLabel("No active warnings")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #0c0c0d;
                color: #f1f3f3;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        main_layout.addWidget(self.toggle_button)
        main_layout.addSpacing(5)
        main_layout.addWidget(self.warning_label)

        # === Flashing warning animation timer ===
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._flash_warning)
        self._flash_state = False
        self._alert_active = False

    def toggle_assist(self):
        """
        Toggles the state of the drive assist system.
        """
        if self.toggle_button.isChecked():
            self.toggle_button.setText("Drive Assist: ON")
        else:
            self.toggle_button.setText("Drive Assist: OFF")
        # TODO: Emit signal or call control logic here

    def show_warning(self, message: str):
        """
        Displays a flashing warning message in the UI.

        @param message: Warning text to display.
        """
        self.warning_label.setText(message)
        self._alert_active = True
        self._flash_state = False
        self.flash_timer.start(500)

    def clear_warning(self):
        """
        Resets the warning label to default and stops flashing.
        """
        self.warning_label.setText("No active warnings")
        self._alert_active = False
        self.flash_timer.stop()
        self._reset_warning_style()

    def _flash_warning(self):
        """
        Flashes the warning label to get the user's attention.
        """
        if not self._alert_active:
            return

        self._flash_state = not self._flash_state
        if self._flash_state:
            self.warning_label.setStyleSheet("""
                QLabel {
                    background-color: #ff4444;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        else:
            self._reset_warning_style()

    def _reset_warning_style(self):
        """
        Applies default style to the warning label.
        """
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #0c0c0d;
                color: #f1f3f3;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

class PRNDWidget(QWidget):
    """
    A vertical gear indicator widget for PRND with smooth animation and visual highlighting.
    """
    def __init__(self):
        super().__init__()
        self.gears = ["P", "R", "N", "D"]
        self.current_gear = "P"
        self.highlight_y = 0  # Animated Y position
        self.target_y = 0

        self.font = QFont("Adwaita Sans", 20, QFont.Bold)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    # TODO: THIS FUNCTION is the logic to set different gears
    def set_gear(self, gear: str):
        """
        Sets the currently selected gear and triggers animation.
        
        @param gear: Gear to select (P, R, N, D).
        """
        if gear in self.gears:
            self.current_gear = gear
            index = self.gears.index(gear)
            gear_height = self.height() // len(self.gears)
            self.target_y = index * gear_height

    def animate(self):
        """
        Smoothly animates the highlight bar to the target gear.
        """
        if abs(self.highlight_y - self.target_y) > 1:
            self.highlight_y += (self.target_y - self.highlight_y) / 4
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        gear_height = h // len(self.gears)

        # Highlight bar
        highlight_rect = QRectF(5, self.highlight_y + 5, w - 10, gear_height - 10)
        painter.setBrush(QColor("#74e1ef"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(highlight_rect, 10, 10)

        # Draw each gear letter
        for i, gear in enumerate(self.gears):
            y = i * gear_height
            rect = QRectF(0, y, w, gear_height)

            # Bold font for selected gear, regular for others
            font = QFont("Adwaita Sans", 20)
            if gear == self.current_gear:
                font.setBold(True)
                painter.setPen(QColor("#0c0c0d"))
            else:
                font.setBold(False)
                painter.setPen(QColor("#f1f3f3"))
                
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, gear)

class SpeedometerWidget(QWidget):
    """
    A smooth animated speedometer with gradient feedback based on ESC pulse width.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(290, 290)
        # Customizable µs range
        self.min_us = 1310
        self.neutral_us = 1500
        self.max_us = 1750

        # Check if the vehicle is connected
        self.vehicleConnect = False

        
        self.current_us = self.neutral_us

        #* IMPORTANT: self.target_us is the value needed to be changed to affect the speedometer value
        self.target_us = self.neutral_us

        # Smooth animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_us)
        self.timer.start(20)

    # TODO: Maybe add a new function to change the self.target_us value?
    def animate_us(self):
        """
        Smooth animation of current_us toward target_us.
        """
        if self.current_us < self.target_us:
            self.current_us = min(self.current_us + 10, self.target_us)
        elif self.current_us > self.target_us:
            self.current_us = max(self.current_us - 10, self.target_us)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = min(self.width(), self.height())
        center = self.rect().center()
        radius = size * 0.46

        # Draw background circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#0c0c0d"))
        painter.drawEllipse(center, radius, radius)

        # Full arc span
        arc_span = 270  # degrees
        arc_start_angle = -135  # starting from bottom center

        # Calculate normalized value from neutral (range: -1 to 1)
        value_range = self.max_us - self.min_us
        offset = self.current_us - self.neutral_us
        norm_value = offset / (value_range / 2)  # -1 to 1

        # Clamp and convert to arc span
        norm_value = max(-1, min(1, norm_value))
        span_angle = int(norm_value * arc_span * 16)

        # Gradient setup
        if self.current_us >= 1650:
            gradient = QConicalGradient(center, arc_start_angle)
            gradient.setColorAt(0.0, QColor("#ffaa00"))
            gradient.setColorAt(0.5, QColor("#ff4444"))
            gradient.setColorAt(1.0, QColor("#ffaa00"))
        elif self.current_us < self.neutral_us:
            gradient = QConicalGradient(center, -90)
            gradient.setColorAt(0.0, QColor("#d97bff"))
            gradient.setColorAt(0.5, QColor("#b033ff"))
            gradient.setColorAt(1.0, QColor("#d97bff"))
        else:
            gradient = QConicalGradient(center, arc_start_angle)
            gradient.setColorAt(0.0, QColor("#7a63ff"))
            gradient.setColorAt(0.5, QColor("#33aaff"))
            gradient.setColorAt(1.0, QColor("#7a63ff"))

        # Draw background arc
        painter.setPen(QPen(QColor("#1e1e21"), 18, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(
            QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
            arc_start_angle * 16,
            -arc_span * 16
        )

        # Draw filled arc
        painter.setPen(QPen(gradient, 18, Qt.SolidLine, Qt.RoundCap))

        if self.current_us < self.neutral_us:
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                315 * 16,
                -span_angle
            )

        else:
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                arc_start_angle * 16,
                -span_angle
            )

        # Draw µs value
        if self.vehicleConnect:
            painter.setPen(QColor("#f1f3f3"))
            painter.setFont(QFont("Adwaita Sans", 26, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, f"{self.current_us} µs")
        else:
            painter.setPen(QColor("#ff4444"))
            font1 = QFont("Adwaita Mono", 26, QFont.Thin)
            font1.setItalic(True)
            painter.setFont(font1)
            painter.drawText(self.rect(), Qt.AlignCenter, "NULL µs")

class SteeringPathWidget(QWidget):
    """
    A visual widget that shows the current steering angle as a curved path based on PWM µs.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(290, 290)
        # === µs PWM Limits ===
        self.min_us = 900
        self.center_us = 1500
        self.max_us = 2100

        # Internal angle (0 = center)
        self._current_us = self.center_us
        self._target_us = self.center_us
        self._smoothing_speed = 2

        # Timer for smooth animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def set_steering_us(self, us_val: int):
        """
        Sets the target µs steering value for animation.
        
        @param us_val: PWM value to target.
        """
        self._target_us = max(self.min_us, min(self.max_us, us_val))

    def animate(self):
        """
        Smoothly animates the path to the target steering value.
        """
        if abs(self._target_us - self._current_us) > 1:
            self._current_us += (self._target_us - self._current_us) / self._smoothing_speed
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center_x = w // 2
        bottom_y = h - 50

        # === Background ===
        painter.setBrush(QColor("#1e1e21"))

        # === Normalize PWM to curve ratio ===
        us_range = self.max_us - self.min_us
        curve_ratio = (self._current_us - self.center_us) / (us_range / 2)
        curve_ratio = max(-1.0, min(1.0, curve_ratio))

        # === Build curved path ===
        curve_amount = curve_ratio * (w * 0.9)
        path = QPainterPath()
        path.moveTo(center_x, bottom_y)
        control_x = center_x + curve_amount
        control_y = h * 0.4
        end_y = 40  # Adjust this to move the tip downward (default was 25)
        path.quadTo(control_x, control_y, center_x, end_y)

        # === Curve Color ===
        if curve_ratio < 0:
            color = "#ff55aa"  # Left
        elif curve_ratio > 0:
            color = "#00ffaa"  # Right
        else:
            color = "#888888"  # Center

        # Draw the arc
        pen = QPen(QColor(color), 4)
        painter.setPen(pen)
        painter.drawPath(path)

        # === Draw tip marker ===
        painter.setBrush(QColor("#f1f3f3"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 4, end_y - 4, 8, 8)

        # === Draw arc labels ===
        painter.setPen(QColor("#aaaaaa"))
        painter.setFont(QFont("Adwaita Sans", 12, QFont.Bold))
        painter.drawText(20, h - 15, "L")           # Left
        painter.drawText(center_x - 5, h - 15, "C")  # Center
        painter.drawText(w - 30, h - 15, "R")        # Right

        # === µs + Percentage Display ===
        painter.setPen(QColor("#f1f3f3"))
        steering_percent = curve_ratio * 100
        painter.setFont(QFont("Adwaita Sans", 14))
        painter.drawText(self.rect().adjusted(0, 5, 0, -10), Qt.AlignTop | Qt.AlignHCenter,
                         f"{int(self._current_us)} µs ({steering_percent:+.0f}%)")