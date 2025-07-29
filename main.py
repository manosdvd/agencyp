# main.py
# The Agency: A Detective Story Authoring Tool
# Refactored to PySide6 with "Holo-Noir" animations and effects.

import sys
import logging
import uuid
import json
import os
from dataclasses import asdict
from typing import get_args

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QSplitter, QStackedWidget, QFormLayout
)
from PySide6.QtGui import QIcon, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent

# --- Schema Imports ---
from schemas import (
    Character, Alignment, Gender, WealthClass, Location, District, Faction,
    ValidationResult, CaseMeta, Item, TimelineEvent, Clue
)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# --- Data Management (UNMODIFIED) ---
class DataManager:
    """Handles loading, saving, and indexing all project data."""
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.images_path = os.path.join(self.base_path, "images")
        self.asset_map = {
            "characters": {"class": Character, "list": [], "dict": {}},
            "locations": {"class": Location, "list": [], "dict": {}},
            "factions": {"class": Faction, "list": [], "dict": {}},
            "districts": {"class": District, "list": [], "dict": {}},
            "items": {"class": Item, "list": [], "dict": {}},
            "clues": {"class": Clue, "list": [], "dict": {}},
            "timeline_events": {"class": TimelineEvent, "list": [], "dict": {}},
        }
        self.case_meta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="")
        self.load_all()

    def get_asset_list(self, asset_type):
        return self.asset_map.get(asset_type, {}).get("list", [])

    def get_asset_dict(self, asset_type):
        return self.asset_map.get(asset_type, {}).get("dict", {})

    def load_all(self):
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.images_path, exist_ok=True)
        for asset_type, data in self.asset_map.items():
            self._load_json(asset_type, data["class"])
        case_meta_path = os.path.join(self.base_path, "case_meta.json")
        if os.path.exists(case_meta_path):
            try:
                with open(case_meta_path, "r") as f:
                    self.case_meta = CaseMeta(**json.load(f))
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Could not load or parse {case_meta_path}: {e}")

    def _load_json(self, asset_type, data_class):
        path = os.path.join(self.base_path, f"{asset_type}.json")
        asset_list = self.get_asset_list(asset_type)
        asset_dict = self.get_asset_dict(asset_type)
        asset_list.clear()
        asset_dict.clear()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for item_data in data:
                        try:
                            valid_fields = {f.name for f in data_class.__dataclass_fields__.values()}
                            filtered_data = {k: v for k, v in item_data.items() if k in valid_fields}
                            asset = data_class(**filtered_data)
                            asset_list.append(asset)
                            asset_dict[asset.id] = asset
                        except (TypeError, KeyError) as te:
                            logger.warning(f"Skipping invalid item in {path}: {te} - Data: {item_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Could not parse {path}: {e}")

    def save_asset(self, asset_type):
        path = os.path.join(self.base_path, f"{asset_type}.json")
        asset_list = self.get_asset_list(asset_type)
        try:
            with open(path, "w") as f:
                json.dump([asdict(c) for c in asset_list], f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save {asset_type} to {path}: {e}")

    def add_asset(self, asset_type, **kwargs):
        if asset_type not in self.asset_map: return None
        asset_class = self.asset_map[asset_type]["class"]
        new_id = str(uuid.uuid4())
        if 'name' not in kwargs and 'fullName' not in kwargs:
             kwargs['name'] = "Unnamed"
        if asset_type == "characters":
            kwargs.setdefault('biography', "")
            kwargs.setdefault('personality', "")
            kwargs.setdefault('alignment', "True Neutral")
            kwargs.setdefault('honesty', 50)
            kwargs.setdefault('victimLikelihood', 50)
            kwargs.setdefault('killerLikelihood', 50)
        new_asset = asset_class(id=new_id, **kwargs)
        self.get_asset_list(asset_type).append(new_asset)
        self.get_asset_dict(asset_type)[new_id] = new_asset
        self.save_asset(asset_type)
        return new_asset

    def delete_asset(self, asset_type, asset_id):
        asset_list = self.get_asset_list(asset_type)
        asset_dict = self.get_asset_dict(asset_type)
        asset_to_delete = asset_dict.get(asset_id)
        if asset_to_delete:
            asset_list.remove(asset_to_delete)
            del asset_dict[asset_id]
            self.save_asset(asset_type)
            return True
        return False

# --- Animated UI Components ---

class AnimatedLineEdit(QLineEdit):
    """A QLineEdit with an animated border color for focus effects."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = QPropertyAnimation(self, b"styleSheet")
        self.animation.setDuration(200) # milliseconds
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def event(self, event):
        if event.type() == QEvent.FocusIn:
            self.animation.setStartValue(self.styleSheet())
            self.animation.setEndValue("""
                QLineEdit {
                    border: 1px solid #82B1FF;
                    background-color: #374151;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            self.animation.start()
        elif event.type() == QEvent.FocusOut:
            self.animation.setStartValue(self.styleSheet())
            self.animation.setEndValue("""
                QLineEdit {
                    border: 1px solid #374151;
                    background-color: #1F2937;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            self.animation.start()
        return super().event(event)

# --- Standard UI Components (PySide6) ---

class AssetListView(QWidget):
    """A reusable list view for displaying assets."""
    def __init__(self, data_manager, on_select):
        super().__init__()
        self.data_manager = data_manager
        self.on_select = on_select
        self.current_asset_type = "characters"

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.add_button = QPushButton("Add Character")
        self.add_button.clicked.connect(self.add_asset)
        self.layout.addWidget(self.add_button)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._handle_item_clicked)
        self.layout.addWidget(self.list_widget)

        self.update_list()

    def set_asset_type(self, asset_type):
        self.current_asset_type = asset_type
        self.add_button.setText(f"Add {asset_type.replace('_', ' ').capitalize()[:-1]}")
        self.update_list()

    def update_list(self):
        self.list_widget.clear()
        assets = self.data_manager.get_asset_list(self.current_asset_type)
        for asset in assets:
            display_name = getattr(asset, 'fullName', getattr(asset, 'name', 'Unnamed'))
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, asset) # Store the whole object
            self.list_widget.addItem(item)

    def add_asset(self):
        if self.current_asset_type == "characters":
            self.data_manager.add_asset(self.current_asset_type, fullName="New Character")
        else:
            self.data_manager.add_asset(self.current_asset_type, name=f"New {self.current_asset_type.capitalize()[:-1]}")
        self.update_list()

    def _handle_item_clicked(self, item):
        asset = item.data(Qt.UserRole)
        self.on_select(asset)

class CharacterDetailView(QWidget):
    """A detail view for editing a Character."""
    def __init__(self, character, data_manager, on_save, on_delete):
        super().__init__()
        self.character = character
        self.data_manager = data_manager
        self.on_save = on_save
        self.on_delete = on_delete

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # Use the new animated line edit
        self.name_field = AnimatedLineEdit(self.character.fullName)
        self.bio_field = QTextEdit(self.character.biography)
        self.personality_field = QTextEdit(self.character.personality)
        self.alignment_dropdown = QComboBox()
        self.alignment_dropdown.addItems(get_args(Alignment))
        self.alignment_dropdown.setCurrentText(self.character.alignment)

        self.form_layout.addRow("Full Name:", self.name_field)
        self.form_layout.addRow("Alignment:", self.alignment_dropdown)
        self.form_layout.addRow("Biography:", self.bio_field)
        self.form_layout.addRow("Personality:", self.personality_field)

        self.layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_clicked)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_clicked)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)

    def save_clicked(self):
        self.character.fullName = self.name_field.text()
        self.character.biography = self.bio_field.toPlainText()
        self.character.personality = self.personality_field.toPlainText()
        self.character.alignment = self.alignment_dropdown.currentText()
        self.data_manager.save_asset("characters")
        self.on_save(self.character)

    def delete_clicked(self):
        self.data_manager.delete_asset("characters", self.character.id)
        self.on_delete()

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Agency")
        self.setGeometry(100, 100, 1200, 800)

        self.data_manager = DataManager()
        
        # --- Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Navigation Rail ---
        self.nav_rail = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_rail)
        self.nav_rail.setFixedWidth(150)

        self.nav_buttons = {
            "Characters": "characters",
            "Locations": "locations",
            "Factions": "factions",
            "Districts": "districts",
            "Items": "items",
            "Plot Graph": "plot_graph",
        }

        for name, asset_type in self.nav_buttons.items():
            button = QPushButton(name)
            button.clicked.connect(lambda checked, at=asset_type: self.change_view(at))
            self.nav_layout.addWidget(button)
        self.nav_layout.addStretch()

        # --- List Pane ---
        self.list_pane = AssetListView(self.data_manager, self.on_asset_select)

        # --- Detail Pane ---
        self.detail_stack = QStackedWidget()
        self.placeholder_view = QLabel("Select an item to see details.")
        self.placeholder_view.setAlignment(Qt.AlignCenter)
        self.detail_stack.addWidget(self.placeholder_view)

        # --- Splitter to manage panes ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.list_pane)
        self.splitter.addWidget(self.detail_stack)
        self.splitter.setSizes([300, 900])

        self.main_layout.addWidget(self.nav_rail)
        self.main_layout.addWidget(self.splitter)

        self.apply_holo_noir_style()

    def apply_holo_noir_style(self):
        """Applies the 'Holo-Noir' theme using QSS."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #111827;
                color: #E0E0E0;
                font-family: Inter, sans-serif;
            }
            QListWidget {
                background-color: #1F2937;
                border: 1px solid #374151;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #374151; /* Holographic Card effect */
            }
            QListWidget::item:selected {
                background-color: #82B1FF;
                color: #111827;
            }
            QPushButton {
                background-color: #374151;
                border: 1px solid #4B5563;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
            QPushButton:pressed {
                background-color: #82B1FF;
                color: #111827;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1F2937;
                border: 1px solid #374151;
                padding: 5px;
                border-radius: 3px;
            }
            /* We remove the focus state from QSS to let the animation handle it */
            QTextEdit, QComboBox {
                 border: 1px solid #374151;
            }
            QTextEdit:focus, QComboBox:focus {
                 border: 1px solid #82B1FF;
            }
            QLabel {
                font-size: 14px;
            }
            QSplitter::handle {
                background-color: #374151;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """)

    def change_view(self, asset_type):
        """Changes the asset type displayed in the list view."""
        if asset_type == "plot_graph":
            self.list_pane.setVisible(False)
            plot_graph_view = QLabel("Interactive Plot Graph (Coming Soon!)")
            plot_graph_view.setAlignment(Qt.AlignCenter)
            self.set_detail_view(plot_graph_view)
        else:
            self.list_pane.setVisible(True)
            self.list_pane.set_asset_type(asset_type)
            self.set_detail_view(self.placeholder_view)

    def on_asset_select(self, asset):
        """Callback to display the detail view for a selected asset."""
        asset_type = self.list_pane.current_asset_type
        if asset_type == "characters":
            view = CharacterDetailView(
                asset,
                self.data_manager,
                on_save=lambda updated_asset: self.list_pane.update_list(),
                on_delete=lambda: (
                    self.set_detail_view(self.placeholder_view),
                    self.list_pane.update_list()
                )
            )
            self.set_detail_view(view)
        else:
            # Placeholder for other asset types
            view = QLabel(f"Detail view for {asset_type} not implemented.")
            view.setAlignment(Qt.AlignCenter)
            self.set_detail_view(view)

    def set_detail_view(self, widget):
        """Clears the detail stack and adds a new widget."""
        # Clear previous widgets
        while self.detail_stack.count() > 0:
            w = self.detail_stack.widget(0)
            self.detail_stack.removeWidget(w)
            w.deleteLater()
        self.detail_stack.addWidget(widget)
        self.detail_stack.setCurrentWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
