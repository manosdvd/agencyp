# main.py
# A UI/UX Demonstration of the "Deco-Futurism" Aesthetic

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFrame, QStackedWidget, QFormLayout,
    QGraphicsDropShadowEffect, QComboBox
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
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
            painter.setBrush(QColor(255, 255, 255, int(opacity * 60)))
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
        self.animation_speed = 400
        self.animation_curve = QEasingCurve.OutCubic
        self.current_index = 0
        self.is_animating = False

    def setCurrentWidget(self, widget):
        if self.is_animating: return
        
        new_index = self.indexOf(widget)
        if self.currentIndex() == new_index: return

        self.is_animating = True
        
        current_widget = self.currentWidget()
        next_widget = widget
        
        self.current_index = new_index
        
        offset_x = self.width()
        
        next_widget.setGeometry(offset_x, 0, self.width(), self.height())
        
        anim_group = QParallelAnimationGroup(self)

        # Animate current widget out
        anim_current = QPropertyAnimation(current_widget, b"pos")
        anim_current.setEndValue(QPoint(-offset_x, 0))
        anim_current.setDuration(self.animation_speed)
        anim_current.setEasingCurve(self.animation_curve)
        anim_group.addAnimation(anim_current)

        # Animate next widget in
        anim_next = QPropertyAnimation(next_widget, b"pos")
        anim_next.setEndValue(QPoint(0, 0))
        anim_next.setDuration(self.animation_speed)
        anim_next.setEasingCurve(self.animation_curve)
        anim_group.addAnimation(anim_next)
        
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
    def background_color(self):
        return self.bg_color

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
        
        # Draw Gold Border
        pen = QPen(QColor("#D4AF37"), 2)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        
        # Draw Cyan Inner Glow
        pen.setColor(QColor(0, 229, 255, 50))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 11, 11)

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deco-Futurism UI/UX Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Left Navigation Pane
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
        
        # Populate with mock data
        mock_items = ["The Crimson Canary", "Case of the Glass Dagger", "Shadows over Neo-Kyoto", "The Archimedes Paradox"]
        for text in mock_items:
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(QSize(100, 60))
            item_widget = AnimatedListItem(text)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
            
        left_layout.addWidget(self.list_widget)

        # Right Detail Pane
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

    def on_item_selected(self, item):
        self.detail_stack.setCurrentWidget(self.detail_card)

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #10141a; }
            QWidget { color: #e0e0e0; font-family: 'Roboto', sans-serif; }
            
            #leftPane { background-color: transparent; border: none; }
            #paneTitle { font-size: 24px; font-weight: bold; color: #D4AF37; padding-bottom: 10px; }
            
            #detailCard { background-color: rgba(28, 34, 43, 0.8); border: none; }
            #cardTitle { font-size: 20px; font-weight: bold; color: #ffffff; padding-bottom: 10px; }
            
            QListWidget { background-color: transparent; border: none; }
            
            QPushButton, MaterialButton {
                background-color: #1c222b; border: 1px solid #2c333d;
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
