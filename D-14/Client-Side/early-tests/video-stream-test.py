import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QThread, Signal, Qt
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"
STREAM_URL = "http://192.168.0.102:5000/video_feed"

class VideoThread(QThread):
    frame_received = Signal(QImage)  # Signal to send new frame to UI

    def __init__(self, stream_url):
        super().__init__()
        self.stream_url = stream_url
        self.running = True  # Control flag for stopping thread

    def run(self):
        cap = cv2.VideoCapture(self.stream_url)

        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_received.emit(q_img)  # Emit the frame
            else:
                print("Failed to retrieve frame")
        
        cap.release()

    def stop(self):
        self.running = False
        self.wait()  # Ensure the thread is properly closed


class StreamViewer(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI
        self.setWindowTitle("Live Stream Viewer")
        self.setGeometry(100, 100, 1280, 720)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)  # Ensure the video scales properly
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Start the video thread
        self.thread = VideoThread(STREAM_URL)
        self.thread.frame_received.connect(self.update_frame)  # Connect signal
        self.thread.start()

    def update_frame(self, q_img):
        """Update QLabel with new frame."""
        self.label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        """Release resources when closing the window."""
        self.thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = StreamViewer()
    viewer.show()
    sys.exit(app.exec())
