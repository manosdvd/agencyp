# main.py
# An advanced UI/UX Demonstration of the "Deco-Futurism" Aesthetic
# with a procedural rainy cityscape background and refined Art Deco motifs.

import sys
import random
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFrame, QStackedWidget, QFormLayout,
    QGraphicsDropShadowEffect, QComboBox, QGraphicsOpacityEffect
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient, QCursor
)
from PySide6.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent, Property, Signal, 
    QTimer, QPoint, QParallelAnimationGroup, QRectF
)

# --- Custom Animated Widgets ---

class MaterialButton(QPushButton):
    """A QPushButton with a Material Design ripple effect and hover animation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self._ripple_radius = 0
        self.ripple_pos = QPoint()
        
        self.ripple_anim = QPropertyAnimation(self, b"ripple_radius", self)
        self.ripple_anim.setDuration(400)
        self.ripple_anim.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        self.ripple_pos = event.position().toPoint()
        self.ripple_anim.setStartValue(0)
        self.ripple_anim.setEndValue(self.width() * 1.5)
        self.ripple_anim.start()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.ripple_anim.state() == QPropertyAnimation.Running:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            end_val = self.ripple_anim.endValue()
            opacity = 1.0 - (self._ripple_radius / end_val) if end_val > 0 else 0.0
            painter.setBrush(QColor(0, 229, 255, int(opacity * 80)))
            painter.drawEllipse(self.ripple_pos, self._ripple_radius, self._ripple_radius)

    @Property(float)
    def ripple_radius(self):
        return self._ripple_radius

    @ripple_radius.setter
    def ripple_radius(self, value):
        self._ripple_radius = value
        self.update()

class AnimatedLineEdit(QLineEdit):
    """A QLineEdit with an animated glow effect on focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor("#00e5ff"))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
        self.animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self.animation.setDuration(200)

    def focusInEvent(self, event):
        self.animation.setStartValue(self.shadow.blurRadius())
        self.animation.setEndValue(15)
        self.animation.start()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.animation.setStartValue(self.shadow.blurRadius())
        self.animation.setEndValue(0)
        self.animation.start()
        super().focusOutEvent(event)

class AnimatedStackedWidget(QStackedWidget):
    """A QStackedWidget that slides and fades in new widgets."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_speed = 500
        self.animation_curve = QEasingCurve.OutExpo
        self.is_animating = False

    def setCurrentWidget(self, widget):
        if self.is_animating or self.currentWidget() == widget:
            return

        self.is_animating = True
        current_widget = self.currentWidget()
        next_widget = widget
        
        offset_x = self.width()
        
        next_widget.setGeometry(0, 0, self.width(), self.height())
        
        opacity_effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(opacity_effect)
        
        anim_group = QParallelAnimationGroup(self)

        anim_pos = QPropertyAnimation(next_widget, b"pos")
        anim_pos.setStartValue(QPoint(offset_x / 4, 0))
        anim_pos.setEndValue(QPoint(0, 0))
        anim_pos.setDuration(self.animation_speed)
        anim_pos.setEasingCurve(self.animation_curve)
        anim_group.addAnimation(anim_pos)

        anim_opacity = QPropertyAnimation(opacity_effect, b"opacity")
        anim_opacity.setStartValue(0.0)
        anim_opacity.setEndValue(1.0)
        anim_opacity.setDuration(self.animation_speed / 2)
        anim_group.addAnimation(anim_opacity)
        
        anim_group.finished.connect(self.animation_finished)
        super().setCurrentWidget(widget)
        anim_group.start(QPropertyAnimation.DeleteWhenStopped)

    def animation_finished(self):
        self.is_animating = False

class AnimatedListItem(QWidget):
    """A custom widget for list items with hover animations."""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.bg_color = QColor("#1c222b")
        self.setCursor(Qt.PointingHandCursor)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

        self.anim_group = QParallelAnimationGroup(self)
        
        self.color_anim = QPropertyAnimation(self, b"background_color")
        self.color_anim.setDuration(200)
        self.anim_group.addAnimation(self.color_anim)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.shadow_anim.setDuration(200)
        self.anim_group.addAnimation(self.shadow_anim)
        
        self.offset_anim = QPropertyAnimation(self.shadow, b"offset")
        self.offset_anim.setDuration(200)
        self.anim_group.addAnimation(self.offset_anim)

    def enterEvent(self, event):
        self.color_anim.setEndValue(QColor("#2c333d"))
        self.shadow_anim.setEndValue(20)
        self.offset_anim.setEndValue(QPoint(0, 5))
        self.anim_group.start()

    def leaveEvent(self, event):
        self.color_anim.setEndValue(QColor("#1c222b"))
        self.shadow_anim.setEndValue(0)
        self.offset_anim.setEndValue(QPoint(0, 0))
        self.anim_group.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 8, 8)
        painter.fillPath(path, self.bg_color)
        painter.setPen(QColor("#e0e0e0"))
        font = QFont("Roboto", 11)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(15, 0, 0, 0), Qt.AlignVCenter, self.text)

    @Property(QColor)
    def background_color(self): return self.bg_color
    @background_color.setter
    def background_color(self, color):
        self.bg_color = color
        self.update()

class DecoFrame(QFrame):
    """A QFrame with a custom Art Deco / futuristic border."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor("#D4AF37"), 1)
        painter.setPen(pen)
        
        # Main border
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

        # Corner Details
        corner_size = 20
        for i in range(4):
            path = QPainterPath()
            if i == 0: # Top-left
                path.moveTo(1, corner_size)
                path.lineTo(1, 1)
                path.lineTo(corner_size, 1)
            elif i == 1: # Top-right
                path.moveTo(self.width() - 1, corner_size)
                path.lineTo(self.width() - 1, 1)
                path.lineTo(self.width() - corner_size, 1)
            elif i == 2: # Bottom-right
                path.moveTo(self.width() - 1, self.height() - corner_size)
                path.lineTo(self.width() - 1, self.height() - 1)
                path.lineTo(self.width() - corner_size, self.height() - 1)
            elif i == 3: # Bottom-left
                path.moveTo(1, self.height() - corner_size)
                path.lineTo(1, self.height() - 1)
                path.lineTo(corner_size, self.height() - 1)
            painter.drawPath(path)

# --- Main Application Widgets ---

class DetailCard(DecoFrame):
    """A demonstration detail card."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("detailCard")
        layout = QFormLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        layout.addRow(title_label)
        layout.addRow("Name:", AnimatedLineEdit("John 'The Ghost' Doe"))
        layout.addRow("Status:", QComboBox())
        layout.addRow("Description:", QTextEdit("A mysterious figure with no past..."))
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(MaterialButton("Save Changes"))
        layout.addRow(button_layout)

class RainyGlassWidget(QWidget):
    """A widget that draws an animated, rainy cityscape background."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_drops)
        self.timer.start(16) # ~60 FPS
        self.drops = []

    def update_drops(self):
        # Add new drops
        if random.randint(0, 5) == 0:
            self.drops.append({
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'radius': random.uniform(1, 3),
                'life': random.randint(100, 300),
                'streak_len': 0,
                'streaking': False
            })

        for drop in self.drops[:]:
            drop['life'] -= 1
            if drop['life'] <= 0 and not drop['streaking']:
                drop['streaking'] = True
            
            if drop['streaking']:
                drop['y'] += 5
                drop['streak_len'] += 5
                if drop['y'] - drop['streak_len'] > self.height():
                    self.drops.remove(drop)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background Cityscape Gradient
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#05080d"))
        grad.setColorAt(0.7, QColor("#10141a"))
        grad.setColorAt(1, QColor("#1c222b"))
        painter.fillRect(self.rect(), grad)

        # Raindrops and Streaks
        for drop in self.drops:
            alpha = min(255, drop['life'])
            if drop['streaking']:
                pen = QPen(QColor(0, 229, 255, alpha // 4), 1)
                painter.setPen(pen)
                painter.drawLine(drop['x'], drop['y'] - drop['streak_len'], drop['x'], drop['y'])
            else:
                brush = QBrush(QColor(0, 229, 255, alpha // 5))
                painter.setBrush(brush)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(drop['x'], drop['y']), drop['radius'], drop['radius'])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deco-Futurism UI/UX Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.rain_bg = RainyGlassWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        left_pane = DecoFrame()
        left_pane.setFixedWidth(350)
        left_pane.setObjectName("leftPane")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(20, 20, 20, 20)
        title_label = QLabel("CASE FILES")
        title_label.setObjectName("paneTitle")
        left_layout.addWidget(title_label)
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(10)
        self.list_widget.itemClicked.connect(self.on_item_selected)
        mock_items = ["The Crimson Canary", "Case of the Glass Dagger", "Shadows over Neo-Kyoto", "The Archimedes Paradox"]
        for text in mock_items:
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(QSize(100, 60))
            item_widget = AnimatedListItem(text)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
        left_layout.addWidget(self.list_widget)

        self.detail_stack = AnimatedStackedWidget()
        self.placeholder = QLabel("SELECT A CASE FILE")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setObjectName("placeholderLabel")
        self.detail_card = DetailCard("The Crimson Canary")
        self.detail_stack.addWidget(self.placeholder)
        self.detail_stack.addWidget(self.detail_card)

        main_layout.addWidget(left_pane)
        main_layout.addWidget(self.detail_stack)

        self.apply_stylesheet()

    def resizeEvent(self, event):
        self.rain_bg.resize(event.size())
        super().resizeEvent(event)

    def on_item_selected(self, item):
        self.detail_stack.setCurrentWidget(self.detail_card)

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #10141a; }
            QWidget { color: #e0e0e0; font-family: 'Roboto', sans-serif; }
            
            #leftPane, #detailCard { background-color: rgba(16, 20, 26, 0.85); border: none; }
            #paneTitle { font-size: 24px; font-weight: bold; color: #D4AF37; padding-bottom: 10px; }
            #cardTitle { font-size: 20px; font-weight: bold; color: #ffffff; padding-bottom: 10px; }
            
            QListWidget { background-color: transparent; border: none; }
            
            QPushButton, MaterialButton {
                background-color: transparent; border: 1px solid #2c333d;
                padding: 12px 24px; font-size: 14px; font-weight: bold; border-radius: 8px;
            }
            QPushButton:hover, MaterialButton:hover { background-color: #2c333d; }
            
            QLineEdit, QTextEdit, QComboBox {
                background-color: #10141a; border: 1px solid #2c333d;
                border-radius: 8px; padding: 12px; font-size: 14px;
            }
            
            #placeholderLabel { font-size: 24px; color: #5c636d; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
