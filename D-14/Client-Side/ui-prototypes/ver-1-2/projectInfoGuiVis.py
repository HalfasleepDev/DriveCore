import sys
import requests
from bs4 import BeautifulSoup
import webbrowser
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication,
    QScrollArea, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class GitHubInfoPanel(QWidget):
    def __init__(self, repo_url="https://github.com/HalfasleepDev/DriveCore"):
        super().__init__()
        self.repo_url = repo_url
        self.repo_owner, self.repo_name = self._parse_repo_url(repo_url)

        self.setMinimumWidth(400) 
        self.setStyleSheet("""
            QWidget {
                background-color: #74e1ef;  /* light cyan */
                border-radius: 14px;
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


# === DEMO ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = GitHubInfoPanel("https://github.com/HalfasleepDev/DriveCore")
    panel.resize(420, 500)
    panel.show()
    sys.exit(app.exec())
