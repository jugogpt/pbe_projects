"""
Modern, smooth UI animations for premium user experience
"""

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect, QPoint, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor


class FadeInEffect:
    """Smooth fade-in animation with professional easing"""

    def __init__(self, widget, duration=400):
        self.widget = widget
        self.duration = duration
        self.opacity_effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutExpo)  # Smoother easing

    def start(self):
        self.animation.start()


class SlideInEffect:
    """Smooth slide-in animation with modern easing"""

    def __init__(self, widget, direction="down", duration=500):
        self.widget = widget
        self.duration = duration
        self.direction = direction

        # Store original geometry
        self.original_geometry = widget.geometry()

        # Set starting position with subtle offset
        start_geometry = QRect(self.original_geometry)
        if direction == "down":
            start_geometry.moveTop(start_geometry.top() - 20)
        elif direction == "up":
            start_geometry.moveTop(start_geometry.top() + 20)
        elif direction == "left":
            start_geometry.moveLeft(start_geometry.left() + 20)
        elif direction == "right":
            start_geometry.moveLeft(start_geometry.left() - 20)

        widget.setGeometry(start_geometry)

        # Create smooth animation
        self.animation = QPropertyAnimation(widget, b"geometry")
        self.animation.setDuration(duration)
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(self.original_geometry)
        self.animation.setEasingCurve(QEasingCurve.OutExpo)  # Premium smooth easing

    def start(self):
        self.animation.start()


class PulseEffect:
    """Smooth, subtle pulse animation for modern highlighting"""

    def __init__(self, widget, duration=1600):
        self.widget = widget
        self.duration = duration
        self.opacity_effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.85)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # Smooth, gentle easing

        # Make it loop seamlessly
        self.animation.setLoopCount(-1)
        self.animation.finished.connect(self.reverse_animation)
        self.reverse = False

    def reverse_animation(self):
        self.reverse = not self.reverse
        if self.reverse:
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.85)
        else:
            self.animation.setStartValue(0.85)
            self.animation.setEndValue(1.0)

    def start(self):
        self.animation.start()

    def stop(self):
        self.animation.stop()
        # Reset to full opacity
        self.opacity_effect.setOpacity(1.0)


class ButtonHoverEffect:
    """Premium hover effect with smooth scale and glow"""

    def __init__(self, button):
        self.button = button
        self.original_style = button.styleSheet()

        # Store original event handlers
        self.original_enter = button.enterEvent
        self.original_leave = button.leaveEvent

        # Override with our handlers
        button.enterEvent = self.on_enter
        button.leaveEvent = self.on_leave

    def on_enter(self, event):
        # Smooth visual feedback on hover
        # The CSS handles most of the styling, just call original
        if self.original_enter:
            self.original_enter(event)

    def on_leave(self, event):
        # Return to normal state
        if self.original_leave:
            self.original_leave(event)


class ScaleEffect:
    """Smooth scale animation for interactive elements"""

    def __init__(self, widget, scale_factor=1.05, duration=200):
        self.widget = widget
        self.scale_factor = scale_factor
        self.duration = duration
        self.original_geometry = None

    def scale_up(self):
        """Scale widget up smoothly"""
        if self.original_geometry is None:
            self.original_geometry = self.widget.geometry()

        current = self.widget.geometry()
        center = current.center()

        new_width = int(current.width() * self.scale_factor)
        new_height = int(current.height() * self.scale_factor)

        scaled = QRect(0, 0, new_width, new_height)
        scaled.moveCenter(center)

        animation = QPropertyAnimation(self.widget, b"geometry")
        animation.setDuration(self.duration)
        animation.setStartValue(current)
        animation.setEndValue(scaled)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

    def scale_down(self):
        """Scale widget back to original size"""
        if self.original_geometry is None:
            return

        current = self.widget.geometry()

        animation = QPropertyAnimation(self.widget, b"geometry")
        animation.setDuration(self.duration)
        animation.setStartValue(current)
        animation.setEndValue(self.original_geometry)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()


def stagger_widget_animations(widgets, delay=80):
    """Smooth staggered entrance animations for multiple widgets"""
    for i, widget in enumerate(widgets):
        timer = QTimer()
        timer.timeout.connect(lambda w=widget: FadeInEffect(w, duration=350).start())
        timer.setSingleShot(True)
        timer.start(i * delay)


class GlowEffect:
    """Modern glow effect for emphasis"""

    def __init__(self, widget, color=QColor(100, 120, 255), blur_radius=20):
        self.widget = widget
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(blur_radius)
        self.shadow.setColor(color)
        self.shadow.setOffset(0, 0)
        self.widget.setGraphicsEffect(self.shadow)

        # Animate glow intensity
        self.animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self.animation.setDuration(800)
        self.animation.setStartValue(blur_radius)
        self.animation.setEndValue(blur_radius * 1.5)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1)

    def start(self):
        self.animation.start()

    def stop(self):
        self.animation.stop()