from PySide6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsColorizeEffect
from PySide6.QtCore import QTimer, QPropertyAnimation, Qt, QEasingCurve, QRectF, QThread, QEvent
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QConicalGradient

import math

class AnimatedToolTip(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.ToolTip)
        self.setStyleSheet("""
            QLabel {
                background-color: #74e1ef;
                color: #0c0c0d;
                padding: 6px 10px;
                border-radius: 5px;
                font-size: 10pt;
                font-family: 'Adwaita Sans';
            }
        """)
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.opacity_effect = self.graphicsEffect()
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.finished.connect(self._handle_finished)
        self._fade_mode = None  # Track direction of animation

    def show_tooltip(self, pos, timeout=2000):
        self.move(pos)
        self.show()
        self.raise_()
        self._fade_mode = "in"
        self.animation.setDirection(QPropertyAnimation.Forward)
        self.animation.start()

    def hide_tooltip(self):
        if not self.isVisible():
            return
        self._fade_mode = "out"
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()

    def _handle_finished(self):
        if self._fade_mode == "out":
            self.hide()

class CircularProgress(QWidget):
    def __init__(self, diameter=60, thickness=5, color="#7a63ff"):
        super().__init__()
        self.diameter = diameter
        self.thickness = thickness
        self.color = color  # fallback color
        self.angle = 0
        self.setFixedSize(diameter, diameter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(20)

    def update_angle(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background (optional)
        painter.setBrush(QColor("#0c0c0d"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        rect = QRectF(
            self.thickness / 2,
            self.thickness / 2,
            self.diameter - self.thickness,
            self.diameter - self.thickness
        )

        # === Gradient Stroke ===
        gradient = QConicalGradient(self.rect().center(), -self.angle)
        gradient.setColorAt(0.0, QColor("#7a63ff"))   # violet
        gradient.setColorAt(0.5, QColor("#b19eff"))   # mid-tone
        gradient.setColorAt(1.0, QColor("#7a63ff"))   # loop back

        pen = QPen(gradient, self.thickness)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        painter.drawArc(rect, int(-self.angle * 16), int(90 * 16))

class LoadingScreen(QWidget):
    def __init__(self, on_finished_callback=None):
        super().__init__()
        self.setStyleSheet("")
        self.on_finished = on_finished_callback

        # === Appearance ===
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        # === Layout ===
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(30, 30, 30, 30)

        # === Logo / Image ===
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setPixmap(QPixmap("D-14/Client-Side/client-app/icons/DriveCoreAppLogo.png").scaledToWidth(120, Qt.SmoothTransformation))

        # === Title ===
        self.title = QLabel("DriveCore")
        self.title.setFont(QFont("Adwaita Sans", 24, QFont.Bold))
        self.title.setStyleSheet("color: #f1f3f3;")
        self.title.setAlignment(Qt.AlignCenter)

        # === Tagline or description ===
        self.tagline = QLabel("Autonomous RC Control Platform")
        self.tagline.setFont(QFont("Adwaita Sans", 11))
        self.tagline.setStyleSheet("color: #a0a0a0;")
        self.tagline.setAlignment(Qt.AlignCenter)

        # === Circular Progress Indicator ===
        self.spinner = CircularProgress(diameter=60, thickness=5)
        

        # === Loading status ===
        self.status = QLabel("Loading systems...")
        self.status.setFont(QFont("Adwaita Sans", 9))
        self.status.setStyleSheet("color: #888888; margin-top: 10px;")
        self.status.setAlignment(Qt.AlignCenter)

        # === Add widgets ===
        layout.addWidget(self.logo)
        layout.addSpacing(10)
        layout.addWidget(self.title)
        layout.addWidget(self.tagline)
        layout.addSpacing(10)

        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.status)

        # === Fade-in Animation ===
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.fade_in_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_in_anim.setDuration(700)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_in_anim.start()

        # === Timed Fade-out ===
        QTimer.singleShot(2500, self.fade_out)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#0c0c0d"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def fade_out(self):
        self.fade_out_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_out_anim.setDuration(600)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_anim.finished.connect(self.finish)
        self.fade_out_anim.start()

    def finish(self):
        self.close()
        if self.on_finished:
            self.on_finished()

def install_hover_animation(button: QPushButton):
    """Attach animated hover effect to a QPushButton."""
    effect = QGraphicsColorizeEffect(button)
    effect.setColor(QColor("#7a63ff"))
    effect.setStrength(0.0)
    button.setGraphicsEffect(effect)

    # Create animation objects
    anim_in = QPropertyAnimation(effect, b"strength", button)
    anim_in.setDuration(200)
    anim_in.setEndValue(0.5)
    anim_in.setEasingCurve(QEasingCurve.OutQuad)

    anim_out = QPropertyAnimation(effect, b"strength", button)
    anim_out.setDuration(200)
    anim_out.setEndValue(0.0)
    anim_out.setEasingCurve(QEasingCurve.InQuad)

    # Store in button so it's not garbage collected
    button._hover_anim_in = anim_in
    button._hover_anim_out = anim_out

    def on_enter(event):
        anim_out.stop()
        anim_in.start()
        return False

    def on_leave(event):
        anim_in.stop()
        anim_out.start()
        return False

    def event_filter(obj, event):
        if event.type() == QEvent.Enter:
            return on_enter(event)
        elif event.type() == QEvent.Leave:
            return on_leave(event)
        return False

    button.installEventFilter(button)
    button.eventFilter = event_filter  # Monkey-patch filter into button instance

