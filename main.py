# main.py
# The Agency: A Detective Story Authoring Tool
# Fusing Holo-Noir aesthetic with Material Design 3 principles and animations.

import sys
import logging
import uuid
import json
import os
import shutil
from dataclasses import asdict, is_dataclass, fields
from typing import get_args, List, Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QSplitter, QStackedWidget, QFormLayout,
    QGraphicsOpacityEffect, QFileDialog, QInputDialog, QStyledItemDelegate,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QRadialGradient
from PySide6.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent, Property, Signal, 
    QTimer, QPoint, QParallelAnimationGroup
)

# --- Schema Imports ---
import schemas

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# --- Enhanced JSON Encoder for Dataclasses ---
class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

# --- Data Reconstruction Helper ---
def from_dict_to_dataclass(cls, data):
    if not isinstance(data, dict): return data
    field_types = {f.name: f.type for f in fields(cls)}
    kwargs = {}
    for f_name, f_type in field_types.items():
        if f_name in data:
            val = data[f_name]
            origin = getattr(f_type, '__origin__', None)
            if origin is list and val is not None:
                item_type = get_args(f_type)[0]
                kwargs[f_name] = [from_dict_to_dataclass(item_type, i) for i in val] if is_dataclass(item_type) else val
            elif is_dataclass(f_type) and val is not None:
                kwargs[f_name] = from_dict_to_dataclass(f_type, val)
            else:
                kwargs[f_name] = val
    return cls(**kwargs)

# --- Data Management ---
class DataManager:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.case_files = {}
        self.load_all_cases()

    def load_all_cases(self):
        os.makedirs(self.base_path, exist_ok=True)
        self.case_files.clear()
        for filename in os.listdir(self.base_path):
            if filename.endswith(".json"):
                try:
                    path = os.path.join(self.base_path, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        case_obj = from_dict_to_dataclass(schemas.CaseFile, data)
                        self.case_files[case_obj.caseId] = case_obj
                except Exception as e:
                    logger.error(f"Failed to load case file {filename}: {e}")

    def get_case(self, case_id):
        return self.case_files.get(case_id)

    def save_case(self, case_obj):
        path = os.path.join(self.base_path, f"{case_obj.caseId}.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(case_obj, f, indent=4, cls=DataclassJSONEncoder)
            self.case_files[case_obj.caseId] = case_obj
        except Exception as e:
            logger.error(f"Failed to save case {case_obj.caseId}: {e}")

    def create_new_case(self, title):
        new_case = schemas.CaseFile(
            caseId=f"case_{uuid.uuid4().hex[:8]}", title=title, synopsis="A new mystery is afoot.",
            status="unsolved", difficulty=1,
            groundTruth=schemas.GroundTruth(victimId="", perpetratorId="", motiveClueId="", meansClueId="", opportunityClueId=""),
            locations=[], characters=[], clues=[], eventChain=[]
        )
        self.save_case(new_case)
        return new_case
    
    def import_case_file(self, source_path):
        try:
            with open(source_path, 'r') as f:
                data = json.load(f)
                case_obj = from_dict_to_dataclass(schemas.CaseFile, data)
            destination_path = os.path.join(self.base_path, os.path.basename(source_path))
            shutil.copy(source_path, destination_path)
            self.case_files[case_obj.caseId] = case_obj
            return True
        except Exception as e:
            logger.error(f"Failed to import case file from {source_path}: {e}")
            return False

    def add_asset_to_case(self, case_obj, asset_type):
        if asset_type == "characters":
            new_char = schemas.Character(
                characterId=f"char_{uuid.uuid4().hex[:8]}",
                coreIdentity=schemas.CoreIdentity(fullName="New Character", age=30, employment=""),
                psychologicalProfile=schemas.PsychologicalProfile(personalityArchetype="", motivations=[]),
                systemFacing=schemas.SystemFacing(voiceModelArchetype="", knowledgeAreas=[])
            )
            case_obj.characters.append(new_char)
        elif asset_type == "locations":
            new_loc = schemas.Location(
                locationId=f"loc_{uuid.uuid4().hex[:8]}",
                coreDetails=schemas.LocationCoreDetails(name="New Location", description="", type=""),
                geographic=schemas.Geographic(district=""),
                systemic=schemas.Systemic(securityLevel=1, factionOwner="", informationValue=1)
            )
            case_obj.locations.append(new_loc)
        self.save_case(case_obj)

# --- Animated UI Components ---

class MaterialButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ripple_radius = 0
        self.ripple_pos = QPoint()
        self.animation = QPropertyAnimation(self, b"ripple_radius", self)
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        self.ripple_pos = event.position().toPoint()
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.width() * 1.5)
        self.animation.start()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.animation.state() == QPropertyAnimation.Running:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            end_val = self.animation.endValue()
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

class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_direction = Qt.Horizontal
        self.m_speed = 500
        self.m_animation_type = QEasingCurve.OutCubic
        self.m_now = 0
        self.m_next = 0
        self.m_wrap = False
        self.m_pnow = QPoint(0, 0)
        self.m_active = False

    def slideInNext(self):
        now_widget = self.widget(self.m_now)
        next_widget = self.widget(self.m_next)
        
        anim_group = QParallelAnimationGroup(self)

        # Animate current widget out
        pos_anim_now = QPropertyAnimation(now_widget, b"pos")
        pos_anim_now.setDuration(self.m_speed)
        pos_anim_now.setEasingCurve(self.m_animation_type)
        pos_anim_now.setStartValue(QPoint(0,0))
        pos_anim_now.setEndValue(QPoint(-self.width(), 0))
        anim_group.addAnimation(pos_anim_now)

        # Animate next widget in
        next_widget.move(self.width(), 0)
        next_widget.show()
        next_widget.raise_()
        
        pos_anim_next = QPropertyAnimation(next_widget, b"pos")
        pos_anim_next.setDuration(self.m_speed)
        pos_anim_next.setEasingCurve(self.m_animation_type)
        pos_anim_next.setStartValue(QPoint(self.width(), 0))
        pos_anim_next.setEndValue(QPoint(0, 0))
        anim_group.addAnimation(pos_anim_next)

        anim_group.finished.connect(self.animationDone)
        self.m_active = True
        anim_group.start(QPropertyAnimation.DeleteWhenStopped)

    def setCurrentWidget(self, widget):
        if self.m_active: return
        self.m_now = self.currentIndex()
        self.m_next = self.indexOf(widget)
        if self.m_now == self.m_next: return
        self.slideInNext()

    def animationDone(self):
        self.setCurrentIndex(self.m_next)
        self.widget(self.m_now).hide()
        self.widget(self.m_now).move(self.m_pnow)
        self.m_active = False

class WelcomeWidget(QWidget):
    create_new_case = Signal()
    browse_for_case = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title_label = QLabel("The Agency")
        title_label.setObjectName("welcomeTitle")
        title_label.setAlignment(Qt.AlignCenter)
        prompt_label = QLabel("Case Synthesis Terminal")
        prompt_label.setObjectName("welcomePrompt")
        prompt_label.setAlignment(Qt.AlignCenter)
        button_layout = QHBoxLayout()
        self.create_button = MaterialButton("Create New Case")
        self.create_button.setObjectName("welcomeButton")
        self.create_button.clicked.connect(self.create_new_case.emit)
        self.browse_button = MaterialButton("Browse for Case...")
        self.browse_button.setObjectName("welcomeButton")
        self.browse_button.clicked.connect(self.browse_for_case.emit)
        button_layout.addStretch()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.browse_button)
        button_layout.addStretch()
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(prompt_label)
        layout.addLayout(button_layout)
        layout.addStretch()

class CaseListView(QWidget):
    case_selected = Signal(str)
    create_new_case = Signal()
    browse_for_case = Signal()

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20,20,20,20)
        self.stack = QStackedWidget()
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.create_new_case.connect(self.create_new_case.emit)
        self.welcome_widget.browse_for_case.connect(self.browse_for_case.emit)
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.stack.addWidget(self.welcome_widget)
        self.stack.addWidget(self.list_widget)
        self.main_layout.addWidget(self.stack)
        self.refresh_list()

    def refresh_list(self):
        self.data_manager.load_all_cases()
        self.list_widget.clear()
        if not self.data_manager.case_files:
            self.stack.setCurrentWidget(self.welcome_widget)
        else:
            self.stack.setCurrentWidget(self.list_widget)
            for case_id, case_obj in self.data_manager.case_files.items():
                item = QListWidgetItem(case_obj.title)
                item.setData(Qt.UserRole, case_id)
                self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        self.case_selected.emit(item.data(Qt.UserRole))

class DetailView(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("detailCard")

class CharacterDetailView(DetailView):
    def __init__(self, character_obj, on_save):
        super().__init__()
        self.character = character_obj
        self.on_save = on_save
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(20,20,20,20)
        self.name_field = QLineEdit(self.character.coreIdentity.fullName)
        self.age_field = QLineEdit(str(self.character.coreIdentity.age))
        self.employment_field = QLineEdit(self.character.coreIdentity.employment)
        self.archetype_field = QLineEdit(self.character.psychologicalProfile.personalityArchetype)
        self.layout.addRow("Full Name:", self.name_field)
        self.layout.addRow("Age:", self.age_field)
        self.layout.addRow("Employment:", self.employment_field)
        self.layout.addRow("Archetype:", self.archetype_field)
        self.save_button = MaterialButton("Save Character")
        self.save_button.clicked.connect(self.save)
        self.layout.addRow(self.save_button)

    def save(self):
        self.character.coreIdentity.fullName = self.name_field.text()
        self.character.coreIdentity.age = int(self.age_field.text()) if self.age_field.text().isdigit() else 0
        self.character.coreIdentity.employment = self.employment_field.text()
        self.character.psychologicalProfile.personalityArchetype = self.archetype_field.text()
        self.on_save()

class LocationDetailView(DetailView):
    def __init__(self, location_obj, on_save):
        super().__init__()
        self.location = location_obj
        self.on_save = on_save
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(20,20,20,20)
        self.name_field = QLineEdit(self.location.coreDetails.name)
        self.desc_field = QTextEdit(self.location.coreDetails.description)
        self.type_field = QLineEdit(self.location.coreDetails.type)
        self.layout.addRow("Name:", self.name_field)
        self.layout.addRow("Description:", self.desc_field)
        self.layout.addRow("Type:", self.type_field)
        self.save_button = MaterialButton("Save Location")
        self.save_button.clicked.connect(self.save)
        self.layout.addRow(self.save_button)

    def save(self):
        self.location.coreDetails.name = self.name_field.text()
        self.location.coreDetails.description = self.desc_field.toPlainText()
        self.location.coreDetails.type = self.type_field.text()
        self.on_save()

class CaseDetailView(QWidget):
    case_updated = Signal()
    back_to_menu = Signal()

    def __init__(self, case_obj, data_manager):
        super().__init__()
        self.case = case_obj
        self.data_manager = data_manager
        self.current_asset_type = "characters"
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.splitter = QSplitter(Qt.Horizontal)
        self.left_pane = QFrame()
        self.left_pane.setObjectName("leftPane")
        self.left_layout = QVBoxLayout(self.left_pane)
        self.top_bar = QHBoxLayout()
        self.back_button = MaterialButton("< Back")
        self.back_button.clicked.connect(self.back_to_menu.emit)
        self.case_title_label = QLabel(case_obj.title)
        self.case_title_label.setObjectName("caseTitleLabel")
        self.top_bar.addWidget(self.back_button)
        self.top_bar.addWidget(self.case_title_label)
        self.top_bar.addStretch()
        self.left_layout.addLayout(self.top_bar)
        self.asset_nav_bar = QHBoxLayout()
        self.asset_buttons = { "Characters": "characters", "Locations": "locations", "Clues": "clues" }
        for name, key in self.asset_buttons.items():
            button = MaterialButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, at=key: self.set_asset_view(at))
            self.asset_nav_bar.addWidget(button)
        self.left_layout.addLayout(self.asset_nav_bar)
        self.add_asset_button = MaterialButton("+ Add Character")
        self.add_asset_button.setObjectName("addButton")
        self.add_asset_button.clicked.connect(self.add_new_asset)
        self.left_layout.addWidget(self.add_asset_button)
        self.asset_list_widget = QListWidget()
        self.asset_list_widget.itemClicked.connect(self.on_asset_selected)
        self.left_layout.addWidget(self.asset_list_widget)
        self.detail_stack = AnimatedStackedWidget() # Use animated stack
        self.placeholder_view = QLabel("Select an asset to edit")
        self.placeholder_view.setAlignment(Qt.AlignCenter)
        self.placeholder_view.setObjectName("placeholderLabel")
        self.detail_stack.addWidget(self.placeholder_view)
        self.splitter.addWidget(self.left_pane)
        self.splitter.addWidget(self.detail_stack)
        self.splitter.setSizes([400, 800])
        self.main_layout.addWidget(self.splitter)
        self.asset_nav_bar.itemAt(0).widget().setChecked(True)
        self.set_asset_view("characters")

    def set_asset_view(self, asset_type):
        for i in range(self.asset_nav_bar.count()):
            btn = self.asset_nav_bar.itemAt(i).widget()
            btn.setChecked(btn.text().lower() == asset_type)
        self.current_asset_type = asset_type
        self.add_asset_button.setText(f"+ Add {asset_type.capitalize()[:-1]}")
        self.populate_asset_list()
        self.detail_stack.setCurrentWidget(self.placeholder_view)

    def populate_asset_list(self):
        self.asset_list_widget.clear()
        assets = getattr(self.case, self.current_asset_type, [])
        for i, asset in enumerate(assets):
            name, id_val = "", ""
            if self.current_asset_type == "characters": name, id_val = asset.coreIdentity.fullName, asset.characterId
            elif self.current_asset_type == "locations": name, id_val = asset.coreDetails.name, asset.locationId
            elif self.current_asset_type == "clues": name, id_val = asset.name, asset.clueId
            if name and id_val:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, id_val)
                self.asset_list_widget.addItem(item)

    def add_new_asset(self):
        self.data_manager.add_asset_to_case(self.case, self.current_asset_type)
        self.populate_asset_list()

    def on_asset_selected(self, item):
        asset_id = item.data(Qt.UserRole)
        assets = getattr(self.case, self.current_asset_type)
        id_field = f"{self.current_asset_type[:-1]}Id"
        asset = next((a for a in assets if getattr(a, id_field) == asset_id), None)
        if asset:
            if self.detail_stack.widget(1):
                self.detail_stack.removeWidget(self.detail_stack.widget(1))

            editor = None
            if self.current_asset_type == "characters": editor = CharacterDetailView(asset, self.on_asset_save)
            elif self.current_asset_type == "locations": editor = LocationDetailView(asset, self.on_asset_save)
            if editor:
                self.detail_stack.addWidget(editor)
                self.detail_stack.setCurrentWidget(editor)

    def on_asset_save(self):
        self.data_manager.save_case(self.case)
        self.populate_asset_list()
        self.case_updated.emit()

class NoiseOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.noise_pixmap = self._create_noise_texture(512, 512)

    def _create_noise_texture(self, width, height):
        image = QPixmap(width, height)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255, 5))
        for _ in range(10000):
            painter.drawPoint(uuid.uuid4().int % width, uuid.uuid4().int % height)
        painter.end()
        return image

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawTiledPixmap(self.rect(), self.noise_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Agency")
        self.setGeometry(100, 100, 1200, 800)
        self.data_manager = DataManager()
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        self.case_list_view = CaseListView(self.data_manager)
        self.case_list_view.case_selected.connect(self.open_case_view)
        self.case_list_view.create_new_case.connect(self.create_new_case)
        self.case_list_view.browse_for_case.connect(self.browse_for_case)
        self.main_stack.addWidget(self.case_list_view)
        self.noise_overlay = NoiseOverlay(self.centralWidget())
        self.apply_holo_noir_style()

    def resizeEvent(self, event):
        self.noise_overlay.resize(event.size())
        super().resizeEvent(event)

    def create_new_case(self):
        text, ok = QInputDialog.getText(self, 'Create New Case', 'Enter case title:')
        if ok and text:
            self.data_manager.create_new_case(title=text)
            self.case_list_view.refresh_list()

    def browse_for_case(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Browse for Case File", "", "JSON Files (*.json)")
        if file_path and self.data_manager.import_case_file(file_path):
            self.case_list_view.refresh_list()

    def open_case_view(self, case_id):
        case_obj = self.data_manager.get_case(case_id)
        if case_obj:
            case_detail_view = CaseDetailView(case_obj, self.data_manager)
            case_detail_view.case_updated.connect(self.case_list_view.refresh_list)
            case_detail_view.back_to_menu.connect(self.show_case_list)
            self.main_stack.addWidget(case_detail_view)
            self.main_stack.setCurrentWidget(case_detail_view)
    
    def show_case_list(self):
        if self.main_stack.count() > 1:
            old = self.main_stack.currentWidget()
            self.main_stack.removeWidget(old)
            old.deleteLater()
        self.main_stack.setCurrentWidget(self.case_list_view)

    def apply_holo_noir_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #10141a; }
            QWidget { color: #e0e0e0; font-family: 'Roboto', sans-serif; font-size: 14px; }
            
            #welcomeTitle { font-size: 48px; font-weight: bold; color: #ffffff; }
            #welcomePrompt { font-size: 18px; color: #a0a0a0; }
            #welcomeButton, #addButton { 
                padding: 12px 24px; font-size: 14px; font-weight: bold;
                background-color: #00e5ff; color: #10141a; border: none; border-radius: 8px;
            }
            #welcomeButton:hover, #addButton:hover { background-color: #81ffff; }

            #leftPane { background-color: #1c222b; border-right: 1px solid #2c333d; }
            #caseTitleLabel { font-size: 24px; font-weight: bold; color: #ffffff; }
            
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 12px; border-radius: 8px; }
            QListWidget::item:hover { background-color: #2c333d; }
            QListWidget::item:selected { background-color: #00e5ff; color: #10141a; font-weight: bold; }
            
            QPushButton {
                background-color: transparent; border: 1px solid #2c333d;
                padding: 8px 16px; font-size: 14px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #2c333d; }
            QPushButton:pressed { background-color: #00e5ff; color: #10141a; }
            QPushButton:checked { background-color: #00e5ff; color: #10141a; border: 1px solid #00e5ff; }

            QLineEdit, QTextEdit, QComboBox {
                background-color: #2c333d; border: none; border-radius: 8px;
                padding: 12px; font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { background-color: #3c444d; }
            
            #detailCard {
                background-color: #1c222b;
                border-radius: 12px;
                margin: 20px;
            }
            
            #placeholderLabel { font-size: 20px; color: #5c636d; }
            QSplitter::handle { background-color: #2c333d; }
            QSplitter::handle:horizontal { width: 1px; }

            QScrollBar:vertical {
                border: none; background: #1c222b; width: 10px; margin: 0px;
            }
            QScrollBar::handle:vertical { background: #3c444d; border-radius: 5px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
