import sys
import logging
import uuid
import json
import os
from dataclasses import asdict, is_dataclass, fields
from typing import get_args, List, Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QSplitter, QStackedWidget, QFormLayout,
    QGraphicsDropShadowEffect, QTabWidget, QCheckBox, QGraphicsView,
    QGraphicsScene, QGraphicsProxyWidget, QGraphicsItem
)
from PySide6.QtGui import (
    QColor, QPixmap, QPainter, QBrush, QPen, QPainterPath
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, Property, QPoint, QPointF, QThread, Signal
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
            elif origin is dict and val is not None:
                key_type, value_type = get_args(f_type)
                kwargs[f_name] = {key_type(k): from_dict_to_dataclass(value_type, v) for k, v in val.items()} if is_dataclass(value_type) else val
            elif is_dataclass(f_type) and val is not None:
                kwargs[f_name] = from_dict_to_dataclass(f_type, val)
            else:
                kwargs[f_name] = val
    return cls(**kwargs)

# --- Data Management ---
class DataManager:
    """
    Abstracts all file I/O. Responsible for reading/writing case files.
    This would be replaced by a database interaction layer in a production build.
    """
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.world_data_path = os.path.join(self.base_path, "world.json")
        self.cases_path = os.path.join(self.base_path, "cases")
        self.world_data = self.load_world_data()
        self.case_files = self.load_all_cases()

    def load_world_data(self):
        os.makedirs(self.base_path, exist_ok=True)
        if os.path.exists(self.world_data_path):
            try:
                with open(self.world_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return from_dict_to_dataclass(schemas.WorldData, data)
            except Exception as e:
                logger.error(f"Failed to load world data: {e}")
        return schemas.WorldData()

    def save_world_data(self):
        try:
            with open(self.world_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.world_data, f, indent=4, cls=DataclassJSONEncoder)
        except Exception as e:
            logger.error(f"Failed to save world data: {e}")

    def load_all_cases(self):
        os.makedirs(self.cases_path, exist_ok=True)
        cases = {}
        for filename in os.listdir(self.cases_path):
            if filename.endswith(".json"):
                try:
                    path = os.path.join(self.cases_path, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        case_obj = from_dict_to_dataclass(schemas.CaseFile, data)
                        cases[case_obj.case_meta.victim] = case_obj
                except Exception as e:
                    logger.error(f"Failed to load case file {filename}: {e}")
        return cases

    def save_case(self, case_obj):
        case_id = case_obj.case_meta.victim or f"case_{uuid.uuid4().hex[:8]}"
        path = os.path.join(self.cases_path, f"{case_id}.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(case_obj, f, indent=4, cls=DataclassJSONEncoder)
            self.case_files[case_id] = case_obj
        except Exception as e:
            logger.error(f"Failed to save case {case_id}: {e}")

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

class DynamicHeightTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.update_height)
        self.update_height() # Initial size update

    def update_height(self):
        doc_height = self.document().size().height()
        self.setFixedHeight(int(doc_height) + self.contentsMargins().top() + self.contentsMargins().bottom())


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

class MultiSelectComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._selected_ids = []

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.update_text()

    def setItems(self, item_dict, selected_ids):
        self.clear()
        self._selected_ids = selected_ids if selected_ids is not None else []
        for item_id, item_obj in item_dict.items():
            name = getattr(item_obj, "name", getattr(item_obj, "full_name", getattr(item_obj, "district_name", getattr(item_obj, "item", ""))))
            self.addItem(name, item_id)
            item = self.model().item(self.count() - 1)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if item_id in self._selected_ids else Qt.Unchecked)
        self.update_text()

    def update_text(self):
        texts = []
        for i in range(self.count()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.itemText(i))
        self.lineEdit().setText(", ".join(texts))

    def getSelectedIds(self):
        ids = []
        for i in range(self.count()):
            if self.model().item(i).checkState() == Qt.Checked:
                ids.append(self.itemData(i))
        return ids

# --- Reusable UI Components ---
class CardWidget(QFrame):
    """
    A custom widget that serves as the base for all 'card' elements in the UI.
    It includes the Art Deco border, shadow, and a Material-style ripple click effect.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 20, 20, 20) # Inner padding for content

        # --- Shadow Effect for a "lifted" look ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # --- Ripple Effect Properties ---
        self._ripple_radius = 0
        self._ripple_opacity = 0
        self._ripple_pos = QPoint()

        # --- Set base background color ---
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#1a1f25"))
        self.setPalette(p)

    # --- Ripple Animation Properties (for QPropertyAnimation) ----
    @Property(float)
    def rippleRadius(self):
        return self._ripple_radius

    @rippleRadius.setter
    def rippleRadius(self, value):
        self._ripple_radius = value
        self.update()  # Trigger a repaint

    @Property(float)
    def rippleOpacity(self):
        return self._ripple_opacity

    @rippleOpacity.setter
    def rippleOpacity(self, value):
        self._ripple_opacity = value
        self.update()  # Trigger a repaint

    def mousePressEvent(self, event):
        # Start the ripple animation on click
        self._ripple_pos = event.pos()
        
        radius_anim = QPropertyAnimation(self, b"rippleRadius")
        radius_anim.setStartValue(0)
        radius_anim.setEndValue(self.width() * 0.8)
        radius_anim.setDuration(400)
        radius_anim.setEasingCurve(QEasingCurve.OutCubic)

        opacity_anim = QPropertyAnimation(self, b"rippleOpacity")
        opacity_anim.setStartValue(0.4)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setDuration(450)
        
        radius_anim.start()
        opacity_anim.start()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        # Let the base class paint its background first
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Draw Ripple Effect ---
        if self._ripple_radius > 0:
            painter.setPen(Qt.NoPen)
            color = QColor("#00e5ff")  # Cyan ripple
            color.setAlphaF(self._ripple_opacity)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(self._ripple_pos, self._ripple_radius, self._ripple_radius)

        # --- Draw Art Deco Border (on top of everything else) ---
        pen = QPen(QColor("#D4AF37"))  # Gold color
        pen.setWidth(2)
        painter.setPen(pen)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRect(rect)
        
        # Draw geometric corners for the Art Deco feel
        corner_size = 10
        painter.drawLine(rect.topLeft(), rect.topLeft() + QPoint(corner_size, 0))
        painter.drawLine(rect.topLeft(), rect.topLeft() + QPoint(0, corner_size))
        painter.drawLine(rect.topRight(), rect.topRight() - QPoint(corner_size, 0))
        painter.drawLine(rect.topRight(), rect.topRight() + QPoint(0, corner_size))
        painter.drawLine(rect.bottomLeft(), rect.bottomLeft() + QPoint(corner_size, 0))
        painter.drawLine(rect.bottomLeft(), rect.bottomLeft() - QPoint(0, corner_size))
        painter.drawLine(rect.bottomRight(), rect.bottomRight() - QPoint(corner_size, 0))
        painter.drawLine(rect.bottomRight(), rect.bottomRight() - QPoint(0, corner_size))

class CharacterCard(CardWidget):
    """ An example of how to use the CardWidget to display a character's info. """
    def __init__(self, character_name, character_archetype, image_path, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self.layout()) # Get the layout from the parent
        
        # --- Image Label (Left Side) ---
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 120)
        self.image_label.setScaledContents(True)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
             # Provide a fallback placeholder
             pixmap = QPixmap(120, 120)
             pixmap.fill(QColor("#2a2f38"))
        self.image_label.setPixmap(pixmap)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #D4AF37; /* Gold border */
                border-radius: 60px; /* Half of the size for a circle */
            }
        """)
        
        # --- Info Layout (Right Side) ---
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        name_label = QLabel(character_name)
        name_label.setObjectName("header") # Use the header style from QSS
        name_label.setStyleSheet("font-size: 22px; padding: 0;")
        
        archetype_label = QLabel(character_archetype)
        archetype_label.setStyleSheet("color: #8a8f98; font-style: italic; border: none;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(archetype_label)
        info_layout.addStretch()
        
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(info_layout)
        
        self.setMinimumHeight(180)

class CaseMetaCard(CardWidget):
    def __init__(self, case_meta_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Victim: {case_meta_obj.victim}"))
        layout.addWidget(QLabel(f"Culprit: {case_meta_obj.culprit}"))
        layout.addWidget(QLabel(f"Crime Scene: {case_meta_obj.crime_scene}"))

class SuspectCard(CardWidget):
    def __init__(self, character_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Suspect: {character_obj.full_name}"))
        layout.addWidget(QLabel(f"Archetype: {character_obj.archetype}"))

class WitnessCard(CardWidget):
    def __init__(self, character_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Witness: {character_obj.full_name}"))
        layout.addWidget(QLabel(f"Honesty: {character_obj.honesty}"))

class ClueCard(CardWidget):
    def __init__(self, clue_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Clue: {clue_obj.clue_summary}"))
        layout.addWidget(QLabel(f"Source: {clue_obj.source}"))

class CaseLocationCard(CardWidget):
    def __init__(self, location_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Location: {location_obj.name}"))
        layout.addWidget(QLabel(f"District: {location_obj.district}"))


# --- The Interactive Plot Graph ---
class ConnectionNode(QGraphicsItem):
    """Represents a single asset card as a movable node on the graph."""
    def __init__(self, card_widget, parent=None):
        super().__init__(parent)
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(card_widget)
        
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.sockets = []
        self.socket_radius = 6
        self._create_sockets()
        self.lines = []

    def _create_sockets(self):
        card_rect = self.proxy.widget().rect()
        # Sockets are positioned relative to the ConnectionNode's origin
        self.sockets.append(QPointF(0, card_rect.height() / 2)) # Left
        self.sockets.append(QPointF(card_rect.width(), card_rect.height() / 2)) # Right

    def boundingRect(self):
        return self.proxy.boundingRect().adjusted(-self.socket_radius, -self.socket_radius, self.socket_radius, self.socket_radius)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(QColor("#D4AF37"), 2))
        painter.setBrush(QBrush(QColor("#10141a")))
        for pos in self.sockets:
            painter.drawEllipse(pos, self.socket_radius, self.socket_radius)
            
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for line in self.lines:
                line.update_path()
        return super().itemChange(change, value)

    def get_socket_scene_pos(self, index):
        if 0 <= index < len(self.sockets):
            return self.mapToScene(self.sockets[index])
        return QPointF()

class ConnectionLine(QGraphicsItem):
    """A curved Bezier line to connect two nodes."""
    def __init__(self, start_node, start_socket_idx, end_node, end_socket_idx, parent=None):
        super().__init__(parent)
        self.start_node = start_node
        self.start_socket_idx = start_socket_idx
        self.end_node = end_node
        self.end_socket_idx = end_socket_idx
        
        self.pen = QPen(QColor("#00e5ff"), 2)
        self.pen.setCapStyle(Qt.RoundCap)
        
        self._path = QPainterPath()
        self.update_path()

    def boundingRect(self):
        return self._path.boundingRect()

    def update_path(self):
        self.prepareGeometryChange()
        start_pos = self.start_node.get_socket_scene_pos(self.start_socket_idx)
        end_pos = self.end_node.get_socket_scene_pos(self.end_socket_idx)
        
        path = QPainterPath()
        path.moveTo(start_pos)
        
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(start_pos.x() + dx * 0.5, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        self._path = path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._path)

class PlotGraphView(QGraphicsView):
    """The main view for displaying and interacting with the plot graph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.scene.setBackgroundBrush(QColor("#10141a"))

    def add_node(self, widget, pos=QPointF(0, 0)):
        node = ConnectionNode(widget)
        node.setPos(pos)
        self.scene.addItem(node)
        return node

    def connect_nodes(self, start_node, end_node):
        # Default connection: right socket of start to left socket of end
        start_socket_idx, end_socket_idx = 1, 0
        
        connection = ConnectionLine(start_node, start_socket_idx, end_node, end_socket_idx)
        self.scene.addItem(connection)
        
        # Register the line with the nodes so they can update it on move
        start_node.lines.append(connection)
        end_node.lines.append(connection)
        
        return connection
        
    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

# --- Validator Components ---
class ValidatorWorker(QThread):
    validation_finished = Signal(list) # Signal to emit validation results

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager

    def run(self):
        results = []

        # --- World Data Validations ---
        # Check for characters with empty full names
        for char_id, character in self.data_manager.world_data.characters.items():
            if not character.full_name:
                results.append({'message': f"Warning: Character with ID {char_id} has no full name.", 'asset_type': 'characters', 'asset_id': char_id})

        # Check for locations with empty names
        for loc_id, location in self.data_manager.world_data.locations.items():
            if not location.name:
                results.append({'message': f"Warning: Location with ID {loc_id} has no name.", 'asset_type': 'locations', 'asset_id': loc_id})

        # Check for factions with empty names
        for faction_id, faction in self.data_manager.world_data.factions.items():
            if not faction.name:
                results.append({'message': f"Warning: Faction with ID {faction_id} has no name.", 'asset_type': 'factions', 'asset_id': faction_id})

        # Check for items with empty names
        for item_id, item in self.data_manager.world_data.items.items():
            if not item.item:
                results.append({'message': f"Warning: Item with ID {item_id} has no name.", 'asset_type': 'items', 'asset_id': item_id})

        # Check for districts with empty names
        for district_id, district in self.data_manager.world_data.districts.items():
            if not district.district_name:
                results.append({'message': f"Warning: District with ID {district_id} has no name.", 'asset_type': 'districts', 'asset_id': district_id})

        # --- Case Data Validations (Basic Solvability and Deception Integrity) ---
        for case_id, case_file in self.data_manager.case_files.items():
            if not case_file.case_meta.victim:
                results.append({'message': f"Error: Case '{case_id}' has no victim defined.", 'asset_type': 'cases', 'asset_id': case_id})
            if not case_file.case_meta.culprit:
                results.append({'message': f"Error: Case '{case_id}' has no culprit defined.", 'asset_type': 'cases', 'asset_id': case_id})
            if not case_file.case_meta.crime_scene:
                results.append({'message': f"Warning: Case '{case_id}' has no crime scene defined.", 'asset_type': 'cases', 'asset_id': case_id})

            # Check if Means, Motive, Opportunity clues exist
            for clue_type in ["means_clue", "motive_clue", "opportunity_clue"]:
                clue_id = getattr(case_file.case_meta, clue_type)
                if clue_id and not any(c.clue_id == clue_id for c in case_file.clues):
                    results.append({'message': f"Error: Case '{case_id}' references a non-existent {clue_type} '{clue_id}'.", 'asset_type': 'clues', 'asset_id': clue_id})

            # Deception Integrity Check
            for suspect in case_file.key_suspects:
                for interview in suspect.interviews:
                    if interview.answer.is_lie and not interview.answer.debunking_clue:
                        results.append({'message': f"Warning: Suspect '{suspect.character_id}' has a lie without a debunking clue in case '{case_id}'.", 'asset_type': 'characters', 'asset_id': suspect.character_id})
                    if interview.answer.is_lie and interview.answer.debunking_clue and not any(c.clue_id == interview.answer.debunking_clue for c in case_file.clues):
                        results.append({'message': f"Error: Suspect '{suspect.character_id}' references a non-existent debunking clue '{interview.answer.debunking_clue}' in case '{case_id}'.", 'asset_type': 'clues', 'asset_id': interview.answer.debunking_clue})

            for location in case_file.locations:
                for witness in location.witnesses:
                    for interview in witness.interviews:
                        if interview.answer.is_lie and not interview.answer.debunking_clue:
                            results.append({'message': f"Warning: Witness '{witness.character_id}' has a lie without a debunking clue in case '{case_id}'.", 'asset_type': 'characters', 'asset_id': witness.character_id})
                        if interview.answer.is_lie and interview.answer.debunking_clue and not any(c.clue_id == interview.answer.debunking_clue for c in case_file.clues):
                            results.append({'message': f"Error: Witness '{witness.character_id}' references a non-existent debunking clue '{interview.answer.debunking_clue}' in case '{case_id}'.", 'asset_type': 'clues', 'asset_id': interview.answer.debunking_clue})

        # Simulate some work to show asynchronicity
        import time
        time.sleep(0.5)

        self.validation_finished.emit(results)

class ValidatorPanel(QWidget):
    issue_selected = Signal(str, str) # asset_type, asset_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        self.title_label = QLabel("Validation Results")
        self.title_label.setObjectName("header") # Use QSS header style
        self.title_label.setStyleSheet("font-size: 18px; padding-bottom: 5px; border-bottom: 1px solid #D4AF37;")
        self.layout.addWidget(self.title_label)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("background-color: #1a1f25; border: 1px solid #4a4f58; border-radius: 4px;")
        self.layout.addWidget(self.results_list)

    def update_results(self, results):
        self.results_list.clear()
        if not results:
            self.results_list.addItem("No issues found. All clear!")
            self.results_list.setStyleSheet("color: #00e5ff; background-color: #1a1f25; border: 1px solid #4a4f58; border-radius: 4px;")
        else:
            for result in results:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0,0,0,0)
                
                message_label = QLabel(result['message'])
                message_label.setStyleSheet("border: none;")
                item_layout.addWidget(message_label)

                if result.get('asset_type') and result.get('asset_id'):
                    go_to_button = QPushButton("Go to Issue")
                    go_to_button.setStyleSheet("padding: 2px 5px; font-size: 12px; border-radius: 4px; background-color: #2a2f38; color: #00e5ff;")
                    go_to_button.clicked.connect(lambda checked, at=result['asset_type'], aid=result['asset_id']: self.issue_selected.emit(at, aid))
                    item_layout.addWidget(go_to_button)

                list_item = QListWidgetItem(self.results_list)
                list_item.setSizeHint(item_widget.sizeHint())
                self.results_list.addItem(list_item)
                self.results_list.setItemWidget(list_item, item_widget)
                list_item.setForeground(QColor("#FF6B6B")) # Red color for warnings/errors
            self.results_list.setStyleSheet("color: #FF6B6B; background-color: #1a1f25; border: 1px solid #4a4f58; border-radius: 4px;")

# --- World Builder ---

class WorldBuilder(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        # --- Navigation Sidebar ---
        self.nav_bar = QFrame()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedWidth(250)
        self.nav_layout = QVBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(10,10,10,10)
        self.nav_layout.setSpacing(10)

        self.asset_buttons = {
            "Characters": "characters",
            "Locations": "locations",
            "Factions": "factions",
            "Items": "items",
            "Districts": "districts",
            "Sleuth": "sleuth"
        }

        for name, key in self.asset_buttons.items():
            button = MaterialButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, at=key: self.set_asset_view(at))
            self.nav_layout.addWidget(button)

        self.main_layout.addWidget(self.nav_bar)

        # --- Detail View ---
        self.detail_stack = QStackedWidget()
        self.main_layout.addWidget(self.detail_stack)

        self.placeholder_view = QLabel("Select an asset type to begin")
        self.placeholder_view.setAlignment(Qt.AlignCenter)
        self.detail_stack.addWidget(self.placeholder_view)

        self.asset_views = {}

        self.nav_layout.itemAt(0).widget().setChecked(True)
        self.set_asset_view("characters")

    def set_asset_view(self, asset_type):
        if asset_type not in self.asset_views:
            view = None
            if asset_type == "characters":
                view = AssetListView(asset_type, self.data_manager.world_data.characters, CharacterDetailView, self.data_manager)
            elif asset_type == "locations":
                view = AssetListView(asset_type, self.data_manager.world_data.locations, LocationDetailView, self.data_manager)
            elif asset_type == "factions":
                view = AssetListView(asset_type, self.data_manager.world_data.factions, FactionDetailView, self.data_manager)
            elif asset_type == "items":
                view = AssetListView(asset_type, self.data_manager.world_data.items, ItemDetailView, self.data_manager)
            elif asset_type == "districts":
                view = AssetListView(asset_type, self.data_manager.world_data.districts, DistrictDetailView, self.data_manager)
            elif asset_type == "sleuth":
                view = SleuthDetailView(self.data_manager.world_data.sleuth, self.data_manager.save_world_data, self.data_manager)

            if view:
                self.asset_views[asset_type] = view
                self.detail_stack.addWidget(view)

        for i in range(self.nav_layout.count()):
            btn = self.nav_layout.itemAt(i).widget()
            btn.setChecked(btn.text().lower().replace(" ", "_") == asset_type)

        if asset_type in self.asset_views:
            self.detail_stack.setCurrentWidget(self.asset_views[asset_type])
        else:
            self.detail_stack.setCurrentWidget(self.placeholder_view)

class AssetListView(QWidget):
    def __init__(self, asset_type, asset_dict, detail_view_class, data_manager):
        super().__init__()
        self.asset_type = asset_type
        self.asset_dict = asset_dict
        self.detail_view_class = detail_view_class
        self.data_manager = data_manager

        self.main_layout = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # --- List Pane ---
        self.list_pane = QFrame()
        self.list_layout = QVBoxLayout(self.list_pane)
        self.add_button = MaterialButton(f"+ Add {self.asset_type.capitalize()[:-1]}")
        self.add_button.clicked.connect(self.add_new_asset)
        self.list_layout.addWidget(self.add_button)
        self.asset_list_widget = QListWidget()
        self.asset_list_widget.itemClicked.connect(self.on_asset_selected)
        self.list_layout.addWidget(self.asset_list_widget)
        self.splitter.addWidget(self.list_pane)

        # --- Detail Pane ---
        self.detail_stack = AnimatedStackedWidget()
        self.placeholder_view = QLabel("Select an asset to edit")
        self.placeholder_view.setAlignment(Qt.AlignCenter)
        self.detail_stack.addWidget(self.placeholder_view)
        self.splitter.addWidget(self.detail_stack)

        self.splitter.setSizes([300, 700])
        self.populate_asset_list()

    def populate_asset_list(self):
        self.asset_list_widget.clear()
        for asset_id, asset in self.asset_dict.items():
            name = getattr(asset, "name", getattr(asset, "full_name", getattr(asset, "district_name", getattr(asset, "item", ""))))
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, asset_id)
            self.asset_list_widget.addItem(item)

    def select_asset_by_id(self, asset_id):
        for i in range(self.asset_list_widget.count()):
            item = self.asset_list_widget.item(i)
            if item.data(Qt.UserRole) == asset_id:
                self.asset_list_widget.setCurrentItem(item)
                self.on_asset_selected(item)
                break

    def add_new_asset(self):
        singular_asset_type = self.asset_type[:-1]
        new_id = f"{singular_asset_type}_{uuid.uuid4().hex[:8]}"
        
        schema_class_name = ""
        for name, cls in schemas.__dict__.items():
            if name.lower() == singular_asset_type:
                schema_class_name = name
                break
        
        if schema_class_name:
            asset_class = getattr(schemas, schema_class_name)
            new_asset = asset_class()
            id_field = f"{singular_asset_type}_id"
            if not hasattr(new_asset, id_field):
                id_field = "id" # fallback for sleuth
            setattr(new_asset, id_field, new_id)
            
            # Set a default name
            if hasattr(new_asset, "name"):
                new_asset.name = f"New {singular_asset_type.capitalize()}"
            elif hasattr(new_asset, "full_name"):
                new_asset.full_name = f"New {singular_asset_type.capitalize()}"
            elif hasattr(new_asset, "district_name"):
                new_asset.district_name = f"New {singular_asset_type.capitalize()}"
            elif hasattr(new_asset, "item"):
                new_asset.item = f"New {singular_asset_type.capitalize()}"

            self.asset_dict[new_id] = new_asset
            self.data_manager.save_world_data()
            self.populate_asset_list()


    def on_asset_selected(self, item):
        asset_id = item.data(Qt.UserRole)
        asset = self.asset_dict.get(asset_id)
        if asset:
            # Remove old editor if it exists
            if self.detail_stack.count() > 1:
                old_editor = self.detail_stack.widget(1)
                if old_editor is not self.placeholder_view:
                    self.detail_stack.removeWidget(old_editor)
                    old_editor.setParent(None)

            editor = self.detail_view_class(asset, self.on_asset_save, self.data_manager)
            self.detail_stack.addWidget(editor)
            self.detail_stack.setCurrentWidget(editor)

    def on_asset_save(self):
        self.data_manager.save_world_data()
        self.populate_asset_list()

class CharacterDetailView(QFrame):
    def __init__(self, character_obj, on_save, data_manager):
        super().__init__()
        self.character = character_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # --- Core Info Tab ---
        self.core_tab = QWidget()
        self.core_layout = QFormLayout(self.core_tab)
        self.full_name_field = QLineEdit(self.character.full_name)
        self.alias_field = QLineEdit(self.character.alias)
        self.age_field = QLineEdit(str(self.character.age) if self.character.age is not None else "")
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["_"] + list(get_args(schemas.Gender)))
        self.gender_combo.setCurrentText(self.character.gender or "_")
        self.employment_field = QLineEdit(self.character.employment)
        self.biography_field = DynamicHeightTextEdit(self.character.biography)
        self.image_field = QLineEdit(self.character.image)
        self.core_layout.addRow("Full Name:", self.full_name_field)
        self.core_layout.addRow("Alias:", self.alias_field)
        self.core_layout.addRow("Age:", self.age_field)
        self.core_layout.addRow("Gender:", self.gender_combo)
        self.core_layout.addRow("Employment:", self.employment_field)
        self.core_layout.addRow("Biography:", self.biography_field)
        self.core_layout.addRow("Image URL:", self.image_field)
        self.tabs.addTab(self.core_tab, "Core Info")

        # --- Associations Tab ---
        self.assoc_tab = QWidget()
        self.assoc_layout = QFormLayout(self.assoc_tab)
        self.faction_combo = QComboBox()
        self.wealth_combo = QComboBox()
        self.district_combo = QComboBox()
        self.allies_combo = MultiSelectComboBox()
        self.enemies_combo = MultiSelectComboBox()
        self.items_combo = MultiSelectComboBox()
        self.populate_association_combos()
        self.assoc_layout.addRow("Faction:", self.faction_combo)
        self.assoc_layout.addRow("Wealth Class:", self.wealth_combo)
        self.assoc_layout.addRow("District:", self.district_combo)
        self.assoc_layout.addRow("Allies:", self.allies_combo)
        self.assoc_layout.addRow("Enemies:", self.enemies_combo)
        self.assoc_layout.addRow("Items:", self.items_combo)
        self.tabs.addTab(self.assoc_tab, "Associations")

        # --- Profile Tab ---
        self.profile_tab = QWidget()
        self.profile_layout = QFormLayout(self.profile_tab)
        self.archetype_field = QLineEdit(self.character.archetype)
        self.personality_field = DynamicHeightTextEdit(self.character.personality)
        self.values_field = DynamicHeightTextEdit("\n".join(self.character.values or []))
        self.flaws_field = DynamicHeightTextEdit("\n".join(self.character.flaws_handicaps_limitations or []))
        self.quirks_field = DynamicHeightTextEdit("\n".join(self.character.quirks or []))
        self.characteristics_field = DynamicHeightTextEdit("\n".join(self.character.characteristics or []))
        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["_"] + list(get_args(schemas.Alignment)))
        self.alignment_combo.setCurrentText(self.character.alignment or "_")
        self.motivations_field = DynamicHeightTextEdit("\n".join(self.character.motivations or []))
        self.secrets_field = DynamicHeightTextEdit("\n".join(self.character.secrets or []))
        self.vulnerabilities_field = DynamicHeightTextEdit("\n".join(self.character.vulnerabilities or []))
        self.profile_layout.addRow("Archetype:", self.archetype_field)
        self.profile_layout.addRow("Personality:", self.personality_field)
        self.profile_layout.addRow("Values:", self.values_field)
        self.profile_layout.addRow("Flaws/Handicaps:", self.flaws_field)
        self.profile_layout.addRow("Quirks:", self.quirks_field)
        self.profile_layout.addRow("Characteristics:", self.characteristics_field)
        self.profile_layout.addRow("Alignment:", self.alignment_combo)
        self.profile_layout.addRow("Motivations:", self.motivations_field)
        self.profile_layout.addRow("Secrets:", self.secrets_field)
        self.profile_layout.addRow("Vulnerabilities:", self.vulnerabilities_field)
        self.tabs.addTab(self.profile_tab, "Profile")

        # --- Dialogue Tab ---
        self.dialogue_tab = QWidget()
        self.dialogue_layout = QFormLayout(self.dialogue_tab)
        self.voice_model_field = QLineEdit(self.character.voice_model)
        self.dialogue_style_field = DynamicHeightTextEdit(self.character.dialogue_style)
        self.expertise_field = DynamicHeightTextEdit("\n".join(self.character.expertise or []))
        self.dialogue_layout.addRow("Voice Model:", self.voice_model_field)
        self.dialogue_layout.addRow("Dialogue Style:", self.dialogue_style_field)
        self.dialogue_layout.addRow("Expertise:", self.expertise_field)
        self.tabs.addTab(self.dialogue_tab, "Dialogue")

        # --- Meta Tab ---
        self.meta_tab = QWidget()
        self.meta_layout = QFormLayout(self.meta_tab)
        self.honesty_field = QLineEdit(str(self.character.honesty))
        self.victim_likelihood_field = QLineEdit(str(self.character.victim_likelihood))
        self.killer_likelihood_field = QLineEdit(str(self.character.killer_likelihood))
        self.portrayal_notes_field = DynamicHeightTextEdit(self.character.portrayal_notes)
        self.meta_layout.addRow("Honesty (0-1):", self.honesty_field)
        self.meta_layout.addRow("Victim Likelihood (0-1):", self.victim_likelihood_field)
        self.meta_layout.addRow("Killer Likelihood (0-1):", self.killer_likelihood_field)
        self.meta_layout.addRow("Portrayal Notes:", self.portrayal_notes_field)
        self.tabs.addTab(self.meta_tab, "Meta")

        self.save_button = MaterialButton("Save Character")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def populate_association_combos(self):
        # Faction
        self.faction_combo.addItem("None", None)
        for faction_id, faction in self.data_manager.world_data.factions.items():
            self.faction_combo.addItem(faction.name, faction_id)
        if self.character.faction:
            self.faction_combo.setCurrentIndex(self.faction_combo.findData(self.character.faction))

        # Wealth Class
        self.wealth_combo.addItems(["_"] + list(get_args(schemas.WealthClass)))
        self.wealth_combo.setCurrentText(self.character.wealth_class or "_")

        # District
        self.district_combo.addItem("None", None)
        for district_id, district in self.data_manager.world_data.districts.items():
            self.district_combo.addItem(district.district_name, district_id)
        if self.character.district:
            self.district_combo.setCurrentIndex(self.district_combo.findData(self.character.district))

        # Allies, Enemies, Items
        self.allies_combo.setItems(self.data_manager.world_data.characters, self.character.allies)
        self.enemies_combo.setItems(self.data_manager.world_data.characters, self.character.enemies)
        self.items_combo.setItems(self.data_manager.world_data.items, self.character.items)

    def save(self):
        # Core Info
        self.character.full_name = self.full_name_field.text()
        self.character.alias = self.alias_field.text()
        self.character.age = int(self.age_field.text()) if self.age_field.text().isdigit() else None
        self.character.gender = self.gender_combo.currentText() if self.gender_combo.currentText() != "_" else None
        self.character.employment = self.employment_field.text()
        self.character.biography = self.biography_field.toPlainText()
        self.character.image = self.image_field.text()

        # Associations
        self.character.faction = self.faction_combo.currentData()
        self.character.wealth_class = self.wealth_combo.currentText() if self.wealth_combo.currentText() != "_" else None
        self.character.district = self.district_combo.currentData()
        self.character.allies = self.allies_combo.getSelectedIds()
        self.character.enemies = self.enemies_combo.getSelectedIds()
        self.character.items = self.items_combo.getSelectedIds()

        # Profile
        self.character.archetype = self.archetype_field.text()
        self.character.personality = self.personality_field.toPlainText()
        self.character.values = [v for v in self.values_field.toPlainText().splitlines() if v]
        self.character.flaws_handicaps_limitations = [v for v in self.flaws_field.toPlainText().splitlines() if v]
        self.character.quirks = [v for v in self.quirks_field.toPlainText().splitlines() if v]
        self.character.characteristics = [v for v in self.characteristics_field.toPlainText().splitlines() if v]
        self.character.alignment = self.alignment_combo.currentText() if self.alignment_combo.currentText() != "_" else None
        self.character.motivations = [v for v in self.motivations_field.toPlainText().splitlines() if v]
        self.character.secrets = [v for v in self.secrets_field.toPlainText().splitlines() if v]
        self.character.vulnerabilities = [v for v in self.vulnerabilities_field.toPlainText().splitlines() if v]

        # Dialogue
        self.character.voice_model = self.voice_model_field.text()
        self.character.dialogue_style = self.dialogue_style_field.toPlainText()
        self.character.expertise = [v for v in self.expertise_field.toPlainText().splitlines() if v]

        # Meta
        try: self.character.honesty = float(self.honesty_field.text())
        except (ValueError, TypeError): self.character.honesty = 0.5
        try: self.character.victim_likelihood = float(self.victim_likelihood_field.text())
        except (ValueError, TypeError): self.character.victim_likelihood = 0.5
        try: self.character.killer_likelihood = float(self.killer_likelihood_field.text())
        except (ValueError, TypeError): self.character.killer_likelihood = 0.5
        self.character.portrayal_notes = self.portrayal_notes_field.toPlainText()

        self.on_save()

class LocationDetailView(QFrame):
    def __init__(self, location_obj, on_save, data_manager):
        super().__init__()
        self.location = location_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # --- Core Info Tab ---
        self.core_tab = QWidget()
        self.core_layout = QFormLayout(self.core_tab)
        self.name_field = QLineEdit(self.location.name)
        self.type_field = QLineEdit(self.location.type)
        self.description_field = DynamicHeightTextEdit(self.location.description)
        self.image_field = QLineEdit(self.location.image)
        self.core_layout.addRow("Name:", self.name_field)
        self.core_layout.addRow("Type:", self.type_field)
        self.core_layout.addRow("Description:", self.description_field)
        self.core_layout.addRow("Image URL:", self.image_field)
        self.tabs.addTab(self.core_tab, "Core Info")

        # --- Associations Tab ---
        self.assoc_tab = QWidget()
        self.assoc_layout = QFormLayout(self.assoc_tab)
        self.district_combo = QComboBox()
        self.owning_faction_combo = QComboBox()
        self.key_characters_combo = MultiSelectComboBox()
        self.associated_items_combo = MultiSelectComboBox()
        self.clues_combo = MultiSelectComboBox()
        self.populate_association_combos()
        self.assoc_layout.addRow("District:", self.district_combo)
        self.assoc_layout.addRow("Owning Faction:", self.owning_faction_combo)
        self.assoc_layout.addRow("Key Characters:", self.key_characters_combo)
        self.assoc_layout.addRow("Associated Items:", self.associated_items_combo)
        self.assoc_layout.addRow("Clues:", self.clues_combo)
        self.tabs.addTab(self.assoc_tab, "Associations")

        # --- Details Tab ---
        self.details_tab = QWidget()
        self.details_layout = QFormLayout(self.details_tab)
        self.danger_level_combo = QComboBox()
        self.danger_level_combo.addItems(["_"] + [str(i) for i in range(1, 11)])
        self.danger_level_combo.setCurrentText(str(self.location.danger_level) if self.location.danger_level is not None else "_")
        self.population_field = QLineEdit(str(self.location.population) if self.location.population is not None else "")
        self.accessibility_combo = QComboBox()
        self.accessibility_combo.addItems(["_"] + list(get_args(schemas.AccessibilityLevel)))
        self.accessibility_combo.setCurrentText(self.location.accessibility or "_")
        self.hidden_checkbox = QCheckBox("Hidden")
        self.hidden_checkbox.setChecked(self.location.hidden or False)
        self.internal_logic_notes_field = DynamicHeightTextEdit(self.location.internal_logic_notes)
        self.details_layout.addRow("Danger Level:", self.danger_level_combo)
        self.details_layout.addRow("Population:", self.population_field)
        self.details_layout.addRow("Accessibility:", self.accessibility_combo)
        self.details_layout.addRow(self.hidden_checkbox)
        self.details_layout.addRow("Internal Logic Notes:", self.internal_logic_notes_field)
        self.tabs.addTab(self.details_tab, "Details")

        self.save_button = MaterialButton("Save Location")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def populate_association_combos(self):
        # District
        self.district_combo.addItem("None", None)
        for district_id, district in self.data_manager.world_data.districts.items():
            self.district_combo.addItem(district.district_name, district_id)
        if self.location.district:
            self.district_combo.setCurrentIndex(self.district_combo.findData(self.location.district))

        # Owning Faction
        self.owning_faction_combo.addItem("None", None)
        for faction_id, faction in self.data_manager.world_data.factions.items():
            self.owning_faction_combo.addItem(faction.name, faction_id)
        if self.location.owning_faction:
            self.owning_faction_combo.setCurrentIndex(self.owning_faction_combo.findData(self.location.owning_faction))

        # Key Characters, Associated Items, Clues
        self.key_characters_combo.setItems(self.data_manager.world_data.characters, self.location.key_characters)
        self.associated_items_combo.setItems(self.data_manager.world_data.items, self.location.associated_items)
        # self.clues_combo.setItems(self.data_manager.case_files, self.location.clues) # This will need to be updated when case files are handled

    def save(self):
        # Core Info
        self.location.name = self.name_field.text()
        self.location.type = self.type_field.text()
        self.location.description = self.description_field.toPlainText()
        self.location.image = self.image_field.text()

        # Associations
        self.location.district = self.district_combo.currentData()
        self.location.owning_faction = self.owning_faction_combo.currentData()
        self.location.key_characters = self.key_characters_combo.getSelectedIds()
        self.location.associated_items = self.associated_items_combo.getSelectedIds()
        # self.location.clues = self.clues_combo.getSelectedIds()

        # Details
        self.location.danger_level = int(self.danger_level_combo.currentText()) if self.danger_level_combo.currentText().isdigit() else None
        self.location.population = int(self.population_field.text()) if self.population_field.text().isdigit() else None
        self.location.accessibility = self.accessibility_combo.currentText() if self.accessibility_combo.currentText() != "_" else None
        self.location.hidden = self.hidden_checkbox.isChecked()
        self.location.internal_logic_notes = self.internal_logic_notes_field.toPlainText()

        self.on_save()

class FactionDetailView(QFrame):
    def __init__(self, faction_obj, on_save, data_manager):
        super().__init__()
        self.faction = faction_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.name_field = QLineEdit(self.faction.name)
        self.archetype_field = QLineEdit(self.faction.archetype)
        self.description_field = DynamicHeightTextEdit(self.faction.description)
        self.ideology_field = QLineEdit(self.faction.ideology)
        self.headquarters_combo = QComboBox()
        self.resources_field = DynamicHeightTextEdit("\n".join(self.faction.resources or []))
        self.image_field = QLineEdit(self.faction.image)
        self.ally_factions_combo = MultiSelectComboBox()
        self.enemy_factions_combo = MultiSelectComboBox()
        self.members_combo = MultiSelectComboBox()
        self.influence_combo = QComboBox()
        self.public_perception_field = QLineEdit(self.faction.public_perception)

        self.form_layout.addRow("Name:", self.name_field)
        self.form_layout.addRow("Archetype:", self.archetype_field)
        self.form_layout.addRow("Description:", self.description_field)
        self.form_layout.addRow("Ideology:", self.ideology_field)
        self.form_layout.addRow("Headquarters:", self.headquarters_combo)
        self.form_layout.addRow("Resources:", self.resources_field)
        self.form_layout.addRow("Image URL:", self.image_field)
        self.form_layout.addRow("Ally Factions:", self.ally_factions_combo)
        self.form_layout.addRow("Enemy Factions:", self.enemy_factions_combo)
        self.form_layout.addRow("Members:", self.members_combo)
        self.form_layout.addRow("Influence:", self.influence_combo)
        self.form_layout.addRow("Public Perception:", self.public_perception_field)

        self.populate_combos()

        self.save_button = MaterialButton("Save Faction")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def populate_combos(self):
        # Headquarters
        self.headquarters_combo.addItem("None", None)
        for loc_id, loc in self.data_manager.world_data.locations.items():
            self.headquarters_combo.addItem(loc.name, loc_id)
        if self.faction.headquarters:
            self.headquarters_combo.setCurrentIndex(self.headquarters_combo.findData(self.faction.headquarters))
        
        # Ally/Enemy Factions
        self.ally_factions_combo.setItems(self.data_manager.world_data.factions, self.faction.ally_factions)
        self.enemy_factions_combo.setItems(self.data_manager.world_data.factions, self.faction.enemy_factions)

        # Members
        self.members_combo.setItems(self.data_manager.world_data.characters, self.faction.members)

        # Influence
        self.influence_combo.addItems(["_"] + list(get_args(schemas.InfluenceScope)))
        self.influence_combo.setCurrentText(self.faction.influence or "_")

    def save(self):
        self.faction.name = self.name_field.text()
        self.faction.archetype = self.archetype_field.text()
        self.faction.description = self.description_field.toPlainText()
        self.faction.ideology = self.ideology_field.text()
        self.faction.headquarters = self.headquarters_combo.currentData()
        self.faction.resources = [r for r in self.resources_field.toPlainText().splitlines() if r]
        self.faction.image = self.image_field.text()
        self.faction.ally_factions = self.ally_factions_combo.getSelectedIds()
        self.faction.enemy_factions = self.enemy_factions_combo.getSelectedIds()
        self.faction.members = self.members_combo.getSelectedIds()
        self.faction.influence = self.influence_combo.currentText() if self.influence_combo.currentText() != "_" else None
        self.faction.public_perception = self.public_perception_field.text()
        self.on_save()

class ItemDetailView(QFrame):
    def __init__(self, item_obj, on_save, data_manager):
        super().__init__()
        self.item = item_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.item_name_field = QLineEdit(self.item.item)
        self.image_field = QLineEdit(self.item.image)
        self.type_field = QLineEdit(self.item.type)
        self.description_field = DynamicHeightTextEdit(self.item.description)
        self.use_field = DynamicHeightTextEdit("\n".join(self.item.use or []))
        self.possible_means_check = QCheckBox("Possible Means")
        self.possible_means_check.setChecked(self.item.possible_means or False)
        self.possible_motive_check = QCheckBox("Possible Motive")
        self.possible_motive_check.setChecked(self.item.possible_motive or False)
        self.possible_opportunity_check = QCheckBox("Possible Opportunity")
        self.possible_opportunity_check.setChecked(self.item.possible_opportunity or False)
        self.default_location_combo = QComboBox()
        self.default_owner_combo = QComboBox()
        self.significance_field = QLineEdit(self.item.significance)
        self.clue_potential_combo = QComboBox()
        self.value_field = QLineEdit(self.item.value)
        self.condition_combo = QComboBox()
        self.unique_properties_field = DynamicHeightTextEdit("\n".join(self.item.unique_properties or []))

        self.form_layout.addRow("Item Name:", self.item_name_field)
        self.form_layout.addRow("Image URL:", self.image_field)
        self.form_layout.addRow("Type:", self.type_field)
        self.form_layout.addRow("Description:", self.description_field)
        self.form_layout.addRow("Use:", self.use_field)
        self.form_layout.addRow(self.possible_means_check)
        self.form_layout.addRow(self.possible_motive_check)
        self.form_layout.addRow(self.possible_opportunity_check)
        self.form_layout.addRow("Default Location:", self.default_location_combo)
        self.form_layout.addRow("Default Owner:", self.default_owner_combo)
        self.form_layout.addRow("Significance:", self.significance_field)
        self.form_layout.addRow("Clue Potential:", self.clue_potential_combo)
        self.form_layout.addRow("Value:", self.value_field)
        self.form_layout.addRow("Condition:", self.condition_combo)
        self.form_layout.addRow("Unique Properties:", self.unique_properties_field)

        self.populate_combos()

        self.save_button = MaterialButton("Save Item")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def populate_combos(self):
        # Default Location
        self.default_location_combo.addItem("None", None)
        for loc_id, loc in self.data_manager.world_data.locations.items():
            self.default_location_combo.addItem(loc.name, loc_id)
        if self.item.default_location:
            self.default_location_combo.setCurrentIndex(self.default_location_combo.findData(self.item.default_location))

        # Default Owner
        self.default_owner_combo.addItem("None", None)
        for char_id, char in self.data_manager.world_data.characters.items():
            self.default_owner_combo.addItem(char.full_name, char_id)
        if self.item.default_owner:
            self.default_owner_combo.setCurrentIndex(self.default_owner_combo.findData(self.item.default_owner))

        # Clue Potential
        self.clue_potential_combo.addItems(["_"] + list(get_args(schemas.CluePotential)))
        self.clue_potential_combo.setCurrentText(self.item.clue_potential or "_")

        # Condition
        self.condition_combo.addItems(["_"] + list(get_args(schemas.ItemCondition)))
        self.condition_combo.setCurrentText(self.item.condition or "_")

    def save(self):
        self.item.item = self.item_name_field.text()
        self.item.image = self.image_field.text()
        self.item.type = self.type_field.text()
        self.item.description = self.description_field.toPlainText()
        self.item.use = [u for u in self.use_field.toPlainText().splitlines() if u]
        self.item.possible_means = self.possible_means_check.isChecked()
        self.item.possible_motive = self.possible_motive_check.isChecked()
        self.item.possible_opportunity = self.possible_opportunity_check.isChecked()
        self.item.default_location = self.default_location_combo.currentData()
        self.item.default_owner = self.default_owner_combo.currentData()
        self.item.significance = self.significance_field.text()
        self.item.clue_potential = self.clue_potential_combo.currentText() if self.clue_potential_combo.currentText() != "_" else None
        self.item.value = self.value_field.text()
        self.item.condition = self.condition_combo.currentText() if self.condition_combo.currentText() != "_" else None
        self.item.unique_properties = [p for p in self.unique_properties_field.toPlainText().splitlines() if p]
        self.on_save()

class DistrictDetailView(QFrame):
    def __init__(self, district_obj, on_save, data_manager):
        super().__init__()
        self.district = district_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.district_name_field = QLineEdit(self.district.district_name)
        self.description_field = DynamicHeightTextEdit(self.district.description)
        self.wealth_class_combo = QComboBox()
        self.atmosphere_field = QLineEdit(self.district.atmosphere)
        self.key_locations_combo = MultiSelectComboBox()
        self.population_density_combo = QComboBox()
        self.notable_features_field = DynamicHeightTextEdit("\n".join(self.district.notable_features or []))
        self.dominant_faction_combo = QComboBox()

        self.form_layout.addRow("District Name:", self.district_name_field)
        self.form_layout.addRow("Description:", self.description_field)
        self.form_layout.addRow("Wealth Class:", self.wealth_class_combo)
        self.form_layout.addRow("Atmosphere:", self.atmosphere_field)
        self.form_layout.addRow("Key Locations:", self.key_locations_combo)
        self.form_layout.addRow("Population Density:", self.population_density_combo)
        self.form_layout.addRow("Notable Features:", self.notable_features_field)
        self.form_layout.addRow("Dominant Faction:", self.dominant_faction_combo)

        self.populate_combos()

        self.save_button = MaterialButton("Save District")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def populate_combos(self):
        # Wealth Class
        self.wealth_class_combo.addItems(["_"] + list(get_args(schemas.WealthClass)))
        self.wealth_class_combo.setCurrentText(self.district.wealth_class or "_")

        # Key Locations
        self.key_locations_combo.setItems(self.data_manager.world_data.locations, self.district.key_locations)

        # Population Density
        self.population_density_combo.addItems(["_"] + list(get_args(schemas.PopulationDensity)))
        self.population_density_combo.setCurrentText(self.district.population_density or "_")

        # Dominant Faction
        self.dominant_faction_combo.addItem("None", None)
        for faction_id, faction in self.data_manager.world_data.factions.items():
            self.dominant_faction_combo.addItem(faction.name, faction_id)
        if self.district.dominant_faction:
            self.dominant_faction_combo.setCurrentIndex(self.dominant_faction_combo.findData(self.district.dominant_faction))

    def save(self):
        self.district.district_name = self.district_name_field.text()
        self.district.description = self.description_field.toPlainText()
        self.district.wealth_class = self.wealth_class_combo.currentText() if self.wealth_class_combo.currentText() != "_" else None
        self.district.atmosphere = self.atmosphere_field.text()
        self.district.key_locations = self.key_locations_combo.getSelectedIds()
        self.district.population_density = self.population_density_combo.currentText() if self.population_density_combo.currentText() != "_" else None
        self.district.notable_features = [f for f in self.notable_features_field.toPlainText().splitlines() if f]
        self.district.dominant_faction = self.dominant_faction_combo.currentData()
        self.on_save()

class SleuthDetailView(QFrame):
    def __init__(self, sleuth_obj, on_save, data_manager):
        super().__init__()
        self.sleuth = sleuth_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.full_name_field = QLineEdit(self.sleuth.full_name)
        self.city_field = QLineEdit(self.sleuth.city)
        self.primary_arc_field = DynamicHeightTextEdit(self.sleuth.primary_arc)

        self.form_layout.addRow("Full Name:", self.full_name_field)
        self.form_layout.addRow("City:", self.city_field)
        self.form_layout.addRow("Primary Arc:", self.primary_arc_field)

        self.save_button = MaterialButton("Save Sleuth")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def save(self):
        self.sleuth.full_name = self.full_name_field.text()
        self.sleuth.city = self.city_field.text()
        self.sleuth.primary_arc = self.primary_arc_field.toPlainText()
        self.on_save()

class CaseBuilder(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.main_layout = QVBoxLayout(self)

        self.case_selector = QComboBox()
        self.case_selector.addItem("Select a Case", None)
        self.case_selector.currentIndexChanged.connect(self.load_selected_case)
        self.main_layout.addWidget(self.case_selector)

        self.new_case_button = MaterialButton("+ New Case")
        self.new_case_button.clicked.connect(self.create_new_case)
        self.main_layout.addWidget(self.new_case_button)

        self.plot_graph_view = PlotGraphView()
        self.main_layout.addWidget(self.plot_graph_view)

        self.populate_case_selector()

    def create_new_case(self):
        case_name, ok = QInputDialog.getText(self, "New Case", "Enter a name for the new case (e.g., Victim's Name):")
        if ok and case_name:
            new_case = schemas.CaseFile()
            new_case.case_meta.victim = case_name # Use victim as the case ID for now
            self.data_manager.save_case(new_case)
            self.populate_case_selector()
            # Select the newly created case
            index = self.case_selector.findData(case_name)
            if index != -1:
                self.case_selector.setCurrentIndex(index)

    def populate_case_selector(self):
        self.case_selector.blockSignals(True) # Block signals to prevent load_selected_case from firing during population
        self.case_selector.clear()
        self.case_selector.addItem("Select a Case", None)
        for case_id, case_obj in self.data_manager.case_files.items():
            self.case_selector.addItem(case_obj.case_meta.victim or case_id, case_id)
        self.case_selector.blockSignals(False)

    def load_selected_case(self, index):
        case_id = self.case_selector.itemData(index)
        self.plot_graph_view.scene.clear() # Clear existing nodes

        if case_id:
            case_file = self.data_manager.case_files.get(case_id)
            if case_file:
                # Add Case Meta Node
                case_meta_card = CaseMetaCard(case_file.case_meta)
                self.plot_graph_view.add_node(case_meta_card, QPointF(0, 0))

                # Add Suspects
                x_offset = -300
                y_offset = 100
                for suspect_id in case_file.key_suspects:
                    character = self.data_manager.world_data.characters.get(suspect_id)
                    if character:
                        suspect_card = SuspectCard(character)
                        self.plot_graph_view.add_node(suspect_card, QPointF(x_offset, y_offset))
                        y_offset += 150

                # Add Witnesses
                x_offset = 300
                y_offset = 100
                for witness_id in case_file.key_witnesses:
                    character = self.data_manager.world_data.characters.get(witness_id)
                    if character:
                        witness_card = WitnessCard(character)
                        self.plot_graph_view.add_node(witness_card, QPointF(x_offset, y_offset))
                        y_offset += 150

                # Add Clues
                x_offset = 0
                y_offset = -200
                for clue_obj in case_file.clues:
                    clue_card = ClueCard(clue_obj)
                    self.plot_graph_view.add_node(clue_card, QPointF(x_offset, y_offset))
                    x_offset += 200

                # Add Case Locations
                x_offset = -200
                y_offset = -300
                for loc_id in case_file.case_locations:
                    location = self.data_manager.world_data.locations.get(loc_id)
                    if location:
                        loc_card = CaseLocationCard(location)
                        self.plot_graph_view.add_node(loc_card, QPointF(x_offset, y_offset))
                        x_offset += 200

class CaseLocationCard(CardWidget):
    def __init__(self, location_obj, parent=None):
        super().__init__(parent)
        layout = self.layout()
        layout.addWidget(QLabel(f"Location: {location_obj.name}"))
        layout.addWidget(QLabel(f"District: {location_obj.district}"))

class CaseMetaDetailView(QFrame):
    def __init__(self, case_meta_obj, on_save, data_manager):
        super().__init__()
        self.case_meta = case_meta_obj
        self.on_save = on_save
        self.data_manager = data_manager

        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.victim_field = QLineEdit(self.case_meta.victim)
        self.culprit_field = QLineEdit(self.case_meta.culprit)
        self.crime_scene_field = QLineEdit(self.case_meta.crime_scene)
        self.murder_weapon_field = QLineEdit(self.case_meta.murder_weapon)
        self.murder_weapon_hidden_checkbox = QCheckBox("Murder Weapon Hidden")
        self.murder_weapon_hidden_checkbox.setChecked(self.case_meta.murder_weapon_hidden)
        self.means_clue_field = QLineEdit(self.case_meta.means_clue)
        self.motive_clue_field = QLineEdit(self.case_meta.motive_clue)
        self.opportunity_clue_field = QLineEdit(self.case_meta.opportunity_clue)
        self.red_herring_clues_field = DynamicHeightTextEdit("\n".join(self.case_meta.red_herring_clues or []))
        self.narrative_viewpoint_combo = QComboBox()
        self.narrative_viewpoint_combo.addItems(["_"] + list(get_args(schemas.NarrativeViewpoint)))
        self.narrative_viewpoint_combo.setCurrentText(self.case_meta.narrative_viewpoint or "_")
        self.narrative_tense_combo = QComboBox()
        self.narrative_tense_combo.addItems(["_"] + list(get_args(schemas.NarrativeTense)))
        self.narrative_tense_combo.setCurrentText(self.case_meta.narrative_tense or "_")
        self.core_mystery_solution_details_field = DynamicHeightTextEdit(self.case_meta.core_mystery_solution_details)
        self.ultimate_reveal_scene_description_field = DynamicHeightTextEdit(self.case_meta.ultimate_reveal_scene_description)
        self.opening_monologue_field = DynamicHeightTextEdit(self.case_meta.opening_monologue)
        self.successful_denouement_field = DynamicHeightTextEdit(self.case_meta.successful_denouement)
        self.failed_denouement_field = DynamicHeightTextEdit(self.case_meta.failed_denouement)

        self.layout.addRow("Victim:", self.victim_field)
        self.layout.addRow("Culprit:", self.culprit_field)
        self.layout.addRow("Crime Scene:", self.crime_scene_field)
        self.layout.addRow("Murder Weapon:", self.murder_weapon_field)
        self.layout.addRow(self.murder_weapon_hidden_checkbox)
        self.layout.addRow("Means Clue:", self.means_clue_field)
        self.layout.addRow("Motive Clue:", self.motive_clue_field)
        self.layout.addRow("Opportunity Clue:", self.opportunity_clue_field)
        self.layout.addRow("Red Herring Clues:", self.red_herring_clues_field)
        self.layout.addRow("Narrative Viewpoint:", self.narrative_viewpoint_combo)
        self.layout.addRow("Narrative Tense:", self.narrative_tense_combo)
        self.layout.addRow("Core Mystery Solution Details:", self.core_mystery_solution_details_field)
        self.layout.addRow("Ultimate Reveal Scene Description:", self.ultimate_reveal_scene_description_field)
        self.layout.addRow("Opening Monologue:", self.opening_monologue_field)
        self.layout.addRow("Successful Denouement:", self.successful_denouement_field)
        self.layout.addRow("Failed Denouement:", self.failed_denouement_field)

        self.save_button = MaterialButton("Save Case Meta")
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignRight)

    def save(self):
        self.case_meta.victim = self.victim_field.text()
        self.case_meta.culprit = self.culprit_field.text()
        self.case_meta.crime_scene = self.crime_scene_field.text()
        self.case_meta.murder_weapon = self.murder_weapon_field.text()
        self.case_meta.murder_weapon_hidden = self.murder_weapon_hidden_checkbox.isChecked()
        self.case_meta.means_clue = self.means_clue_field.text()
        self.case_meta.motive_clue = self.motive_clue_field.text()
        self.case_meta.opportunity_clue = self.opportunity_clue_field.text()
        self.case_meta.red_herring_clues = [c for c in self.red_herring_clues_field.toPlainText().splitlines() if c]
        self.case_meta.narrative_viewpoint = self.narrative_viewpoint_combo.currentText() if self.narrative_viewpoint_combo.currentText() != "_" else None
        self.case_meta.narrative_tense = self.narrative_tense_combo.currentText() if self.narrative_tense_combo.currentText() != "_" else None
        self.case_meta.core_mystery_solution_details = self.core_mystery_solution_details_field.toPlainText()
        self.case_meta.ultimate_reveal_scene_description = self.ultimate_reveal_scene_description_field.toPlainText()
        self.case_meta.opening_monologue = self.opening_monologue_field.toPlainText()
        self.case_meta.successful_denouement = self.successful_denouement_field.toPlainText()
        self.case_meta.failed_denouement = self.failed_denouement_field.toPlainText()
        self.on_save()


# --- The Interactive Plot Graph ---
class ConnectionNode(QGraphicsItem):
    """Represents a single asset card as a movable node on the graph."""
    def __init__(self, card_widget, parent=None):
        super().__init__(parent)
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(card_widget)
        
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.sockets = []
        self.socket_radius = 6
        self._create_sockets()
        self.lines = []

    def _create_sockets(self):
        card_rect = self.proxy.widget().rect()
        # Sockets are positioned relative to the ConnectionNode's origin
        self.sockets.append(QPointF(0, card_rect.height() / 2)) # Left
        self.sockets.append(QPointF(card_rect.width(), card_rect.height() / 2)) # Right

    def boundingRect(self):
        return self.proxy.boundingRect().adjusted(-self.socket_radius, -self.socket_radius, self.socket_radius, self.socket_radius)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(QColor("#D4AF37"), 2))
        painter.setBrush(QBrush(QColor("#10141a")))
        for pos in self.sockets:
            painter.drawEllipse(pos, self.socket_radius, self.socket_radius)
            
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for line in self.lines:
                line.update_path()
        return super().itemChange(change, value)

    def get_socket_scene_pos(self, index):
        if 0 <= index < len(self.sockets):
            return self.mapToScene(self.sockets[index])
        return QPointF()

class ConnectionLine(QGraphicsItem):
    """A curved Bezier line to connect two nodes."""
    def __init__(self, start_node, start_socket_idx, end_node, end_socket_idx, parent=None):
        super().__init__(parent)
        self.start_node = start_node
        self.start_socket_idx = start_socket_idx
        self.end_node = end_node
        self.end_socket_idx = end_socket_idx
        
        self.pen = QPen(QColor("#00e5ff"), 2)
        self.pen.setCapStyle(Qt.RoundCap)
        
        self._path = QPainterPath()
        self.update_path()

    def boundingRect(self):
        return self._path.boundingRect()

    def update_path(self):
        self.prepareGeometryChange()
        start_pos = self.start_node.get_socket_scene_pos(self.start_socket_idx)
        end_pos = self.end_node.get_socket_scene_pos(self.end_socket_idx)
        
        path = QPainterPath()
        path.moveTo(start_pos)
        
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(start_pos.x() + dx * 0.5, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        self._path = path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._path)

class PlotGraphView(QGraphicsView):
    """The main view for displaying and interacting with the plot graph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.scene.setBackgroundBrush(QColor("#10141a"))

    def add_node(self, widget, pos=QPointF(0, 0)):
        node = ConnectionNode(widget)
        node.setPos(pos)
        self.scene.addItem(node)
        return node

    def connect_nodes(self, start_node, end_node):
        # Default connection: right socket of start to left socket of end
        start_socket_idx, end_socket_idx = 1, 0
        
        connection = ConnectionLine(start_node, start_socket_idx, end_node, end_socket_idx)
        self.scene.addItem(connection)
        
        # Register the line with the nodes so they can update it on move
        start_node.lines.append(connection)
        end_node.lines.append(connection)
        
        return connection
        
    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

# --- Validator Components ---
class ValidatorWorker(QThread):
    validation_finished = Signal(list) # Signal to emit validation results

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager

    def run(self):
        results = []

        # --- World Data Validations ---
        # Check for characters with empty full names
        for char_id, character in self.data_manager.world_data.characters.items():
            if not character.full_name:
                results.append({'message': f"Warning: Character with ID {char_id} has no full name. (World Data)", 'asset_type': 'characters', 'asset_id': char_id})

        # Check for locations with empty names
        for loc_id, location in self.data_manager.world_data.locations.items():
            if not location.name:
                results.append({'message': f"Warning: Location with ID {loc_id} has no name. (World Data)", 'asset_type': 'locations', 'asset_id': loc_id})

        # Check for factions with empty names
        for faction_id, faction in self.data_manager.world_data.factions.items():
            if not faction.name:
                results.append({'message': f"Warning: Faction with ID {faction_id} has no name. (World Data)", 'asset_type': 'factions', 'asset_id': faction_id})

        # Check for items with empty names
        for item_id, item in self.data_manager.world_data.items.items():
            if not item.item:
                results.append({'message': f"Warning: Item with ID {item_id} has no name. (World Data)", 'asset_type': 'items', 'asset_id': item_id})

        # Check for districts with empty names
        for district_id, district in self.data_manager.world_data.districts.items():
            if not district.district_name:
                results.append({'message': f"Warning: District with ID {district_id} has no name. (World Data)", 'asset_type': 'districts', 'asset_id': district_id})

        # --- Case Data Validations (Basic Solvability and Deception Integrity) ---
        for case_id, case_file in self.data_manager.case_files.items():
            # Core Solvability Check
            if not case_file.case_meta.victim:
                results.append({'message': f"Error: Case '{case_id}' has no victim defined.", 'asset_type': 'cases', 'asset_id': case_id})
            if not case_file.case_meta.culprit:
                results.append({'message': f"Error: Case '{case_id}' has no culprit defined.", 'asset_type': 'cases', 'asset_id': case_id})
            if not case_file.case_meta.crime_scene:
                results.append({'message': f"Warning: Case '{case_id}' has no crime scene defined.", 'asset_type': 'cases', 'asset_id': case_id})

            # Check if Means, Motive, Opportunity clues exist
            for clue_type in ["means_clue", "motive_clue", "opportunity_clue"]:
                clue_id = getattr(case_file.case_meta, clue_type)
                if clue_id and not any(c.clue_id == clue_id for c in case_file.clues):
                    results.append({'message': f"Error: Case '{case_id}' references a non-existent {clue_type} '{clue_id}'.", 'asset_type': 'clues', 'asset_id': clue_id})

            # Deception Integrity Check
            for suspect in case_file.key_suspects:
                for interview in suspect.interviews:
                    if interview.answer.is_lie and not interview.answer.debunking_clue:
                        results.append({'message': f"Warning: Suspect '{suspect.character_id}' has a lie without a debunking clue in case '{case_id}'.", 'asset_type': 'characters', 'asset_id': suspect.character_id})
                    if interview.answer.is_lie and interview.answer.debunking_clue and not any(c.clue_id == interview.answer.debunking_clue for c in case_file.clues):
                        results.append({'message': f"Error: Suspect '{suspect.character_id}' references a non-existent debunking clue '{interview.answer.debunking_clue}' in case '{case_id}'.", 'asset_type': 'clues', 'asset_id': interview.answer.debunking_clue})

            for location in case_file.locations:
                for witness in location.witnesses:
                    for interview in witness.interviews:
                        if interview.answer.is_lie and not interview.answer.debunking_clue:
                            results.append({'message': f"Warning: Witness '{witness.character_id}' has a lie without a debunking clue in case '{case_id}'.", 'asset_type': 'characters', 'asset_id': witness.character_id})
                        if interview.answer.is_lie and interview.answer.debunking_clue and not any(c.clue_id == interview.answer.debunking_clue for c in case_file.clues):
                            results.append({'message': f"Error: Witness '{witness.character_id}' references a non-existent debunking clue '{interview.answer.debunking_clue}' in case '{case_id}'.", 'asset_type': 'clues', 'asset_id': interview.answer.debunking_clue})

        # Simulate some work to show asynchronicity
        import time
        time.sleep(0.5)

        self.validation_finished.emit(results)

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Agency Case Builder")
        self.data_manager = DataManager()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.world_builder = WorldBuilder(self.data_manager)
        self.case_builder = CaseBuilder(self.data_manager)

        self.main_tabs.addTab(self.world_builder, "World Builder")
        self.main_tabs.addTab(self.case_builder, "Case Builder")

        # Validator Panel
        self.validator_panel = ValidatorPanel()
        self.main_layout.addWidget(self.validator_panel)

        # Validator Worker
        self.validator_worker = ValidatorWorker(self.data_manager)
        self.validator_worker.validation_finished.connect(self.validator_panel.update_results)
        self.validator_panel.issue_selected.connect(self.go_to_asset)
        self.validator_worker.start() # Start validation on app launch

    def go_to_asset(self, asset_type, asset_id):
        # Switch to World Builder tab
        self.main_tabs.setCurrentWidget(self.world_builder)

        # Set the correct asset view in WorldBuilder
        self.world_builder.set_asset_view(asset_type)

        # Select the specific asset in the AssetListView
        if asset_type in self.world_builder.asset_views:
            asset_list_view = self.world_builder.asset_views[asset_type]
            asset_list_view.select_asset_by_id(asset_id)

def main():
    """
    Initializes the Qt Application and the main window.
    """
    app = QApplication(sys.argv)

    # Load the global stylesheet
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
        print("Stylesheet 'style.qss' loaded successfully.")
    except FileNotFoundError:
        print("Warning: style.qss not found. Using default styles.")

    main_window = MainWindow()
    main_window.resize(1200, 800)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

def main():
    """
    Initializes the Qt Application and the main window.
    """
    app = QApplication(sys.argv)

    # Load the global stylesheet
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
        print("Stylesheet 'style.qss' loaded successfully.")
    except FileNotFoundError:
        print("Warning: style.qss not found. Using default styles.")

    main_window = MainWindow()
    main_window.resize(1200, 800)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
