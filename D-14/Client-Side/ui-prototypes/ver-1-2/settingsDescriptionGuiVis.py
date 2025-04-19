import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget


class DescriptionWidget(QWidget):
    def __init__(self, title="Title", markdown_text="**This** _is_ `markdown`..."):
        super().__init__()
        self.setObjectName("descriptionCard")

        # === Title Label ===
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Adwaita Sans", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #ffffff;")
        self.title_label.setAlignment(Qt.AlignLeft)

        # === Markdown Display ===
        self.markdown_view = QTextBrowser()
        self.markdown_view.setOpenExternalLinks(True)
        self.markdown_view.setMarkdown(markdown_text)
        self.markdown_view.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                color: #f1f3f3;
                font-family: 'Adwaita Sans';
                font-size: 11pt;
                border: none;
            }
        """)
        self.markdown_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # === Layout ===
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.markdown_view)

        # === Card Styling ===
        self.setStyleSheet("""
            QWidget#descriptionCard {
                background-color: #1e1e21;
                border-radius: 15px;
            }
        """)

    def update_markdown(self, markdown_text):
        self.markdown_view.setMarkdown(markdown_text)

    def update_title(self, title):
        self.title_label.setText(title)


# === Demo Window ===
class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Description Widget Demo")
        self.resize(500, 400)
        layout = QVBoxLayout(self)

        markdown_text = """
### HEADER  
Text text text text
- Point
- Point
- Point

Text text text text

---

**Text** text  
*Text* text
"""

        desc_widget = DescriptionWidget("TITLE", markdown_text)
        layout.addWidget(desc_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
