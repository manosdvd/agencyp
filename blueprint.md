# **Project Blueprint: The Agency Case Builder**

**Official Repository:** [https://github.com/manosdvd/agencyp/](https://github.com/manosdvd/agencyp/)

## **1\. Core Vision & Philosophy**

### **Product**

"The Agency" is an integrated authoring tool that functions as a digital extension of a detective's mind. It's designed to be a sanctuary for creation, a space for constructing worlds, weaving plots, and stress-testing the very logic of a mystery. It anticipates the author's needs, helping to visualize connections, track narrative threads, and identify logical fallacies, freeing the author to focus on the creative spark, character depth, and atmospheric storytelling.

### **Core Philosophy**

The creative process is paramount. The software must be intuitive, powerful, and, most importantly, visually engaging. It will blend the psychological depth and high-contrast lighting of **neo-noir** with the elegant, clean geometry of **Art Deco** and the clarity of modern **speculative UI**. The experience should feel less like data entry and more like a detective in a near-future setting physically assembling clues on a holographic evidence board. Every interaction should feel tactile and meaningful, reinforcing the author's role as the master architect of their mystery.

## **2\. UI/UX Design: "Deco-Futurism"**

The user experience is central to this project. The goal is to create an interface that is not only efficient but also inspiring.

### **Core Navigation**

The user interface will be organized into two primary components, accessible via main tabs to manage cognitive load:

* **The World Builder:** This section is dedicated to creating the foundational elements of the story's universe. It is the library for managing **Districts, Locations, Factions, Characters, Items, and the Sleuth's profile**.  
* **The Case Builder:** This is the focused workspace for constructing a specific mystery using the assets defined in the World Builder. Here, authors will define the **Case Meta (victim, culprit, etc.), manage Key Suspects and Witnesses, write Interviews, and detail all Clues**.

### **Aesthetic & Design System**

* **Core Theme:** A fusion of four key influences: the moody atmosphere of **classic noir**; the stark, high-contrast lighting of **neo-noir**; the elegant, symmetrical geometry of **Art Deco**; and the clean, diegetic, holographic aesthetic of **modern sci-fi**.  
* **Color Palette:**  
  * **Base:** Deep, dark charcoal (\#10141a).  
  * **Primary Accent (Holographic):** Vibrant, electric cyan (\#00e5ff) for all interactive elements.  
  * **Secondary Accent (Art Deco):** Warm, elegant gold (\#D4AF37) for borders and major headers.  
* **Shape & Form:** The UI is built on a foundation of "cards" or elevated surfaces, framed with thin, gold, Art Deco-inspired borders. The layout prioritizes clean lines, symmetry, and elegant arrangements.  
* **Asset Presentation:** All world-building assets (Characters, Locations, etc.) will be presented in an attractive card-like or file-like format, with prominent imagery and clear, iconic metadata.  
* **Typography:** A clear sans-serif (like Inter or Roboto) for body text, paired with a stylized, geometric Art Deco font (like Poiret One) for major headers.

### **Animation & Interactivity Philosophy**

* **Information is Physical & Layered:** UI elements are treated as objects in a layered, holographic space. Detail views will animate in by **sliding and fading**.  
* **Motion with Purpose:** Clicks trigger a **Material ripple effect**, providing immediate tactile feedback.  
* **Responsive Feedback:** Interactive elements provide clear visual cues, such as "lifting" with a soft shadow on hover or a soft, pulsing **animated glow** on focused input fields.  
* **Subtle Ambiance:** The interface will feel constantly "online" through non-distracting ambient motion, like softly pulsing glows or faint, shimmering background grids.

## **3\. Core Features & Logic**

### **The Interactive Plot Graph**

This is the application's centerpiece: a dynamic, node-based plot graph. This will be the primary case-building interface, allowing for the visual construction and analysis of the narrative's logical flow.

### **The Validator: The Logical Co-Pilot**

The Validator is an ever-present, silent assistant that ensures the story is logically sound, solvable, and internally consistent. It runs automated checks in real-time and presents results in a clear, actionable report.

* **Core Principles:**  
  * **Persistent & Non-Intrusive:** Feedback is displayed in a dedicated panel, never in disruptive pop-ups.  
  * **Actionable Feedback:** Every validation message is clear and provides a "Go to Issue" button that navigates the user to the source of the error.  
* **Specific Validation Checks:**  
  * **Core Solvability Check:** Ensures the Means, Motive, and Opportunity clues are discoverable and that all critical hidden elements are eventually revealed.  
  * **Deception Integrity Check:** Verifies that every red herring and lie has a corresponding debunking clue, and that the logic is not circular.  
  * **Narrative Consistency Check:** Flags dependency cycles, logical inconsistencies between the culprit's profile and the crime, and contradictions in character relationships.  
  * **Uniqueness of Solution Check:** Attempts to "solve" the case to see if any other character besides the designated culprit fits the MMO profile, flagging ambiguity.

## **4\. Data Schema**

This section details the purpose and intent of every field within the application, serving as the single source of truth for the data model.

### **4.1 World Builder Fields**

* **Districts:** A macro-level container for tone and atmosphere.  
  * District\_ID, District, Description, Wealth Class, Atmosphere, Key Locations, Population Density, Notable Features, Dominant Faction  
* **Locations:** The stages upon which scenes unfold.  
  * location\_id, Name, Type, Description, District, Owning Faction, Danger level, Population, Image, Key Characters, Associated Items, Accessibility, Hidden, Clues, Internal\_Logic\_Notes  
* **Factions:** Organizations with their own goals that drive conflict.  
  * Faction\_ID, Name,, Archetype, Description, Ideology, Headquarters, Resources, Image, Ally Factions, Enemy Factions, Members, Influence, Public Perception\`  
* **Characters & Sleuth:** The heart of the story: victims, culprits, witnesses, and red herrings.  
  * Character\_ID, Full Name, Alias, Age, Gender, Employment, Biography, Image, Faction, Wealth Class, District, Allies/Relationships, Enemies/Nemesis, Items, Archetype, Personality, Values, Flaws\_Handicaps\_Limitations, Quirks, Characteristics, Alignment, Motivations, Secrets, Vulnerabilities, Voice Model, Dialogue\_Style, Expertise, Honesty, Victim Likelihood, Killer Likelihood, Portrayal\_Notes  
  * **Sleuth Specific:** City, Primary\_Arc  
* **Items:** Physical objects: clues, weapons, keys, etc.  
  * Item\_id, Item, Image, Type, Description, Use, Possible Means, Possible Motive, Possible Opportunity, Default Location, Default Owner, Significance, Clue Potential, Value, Condition, Unique Properties

### **4.2 Case Builder Fields**

* **Case Meta:** The absolute truth of the case.  
  * Victim, Culprit, Crime Scene, Murder Weapon, Murder Weapon hidden, Means Clue, Motive Clue, Opportunity Clue, Red Herring Clues, Narrative\_Viewpoint, Narrative Tense, Core\_Mystery\_Solution\_Details, Ultimate\_Reveal\_Scene\_Description, Opening\_Monologue, Successful\_Denouement, Failed Denouement  
* **Key Suspects & Witnesses:** The cast of the specific case.  
  * ADD Character/Witness, Interview Question, Interview Answer, Is Lie, Debunking Clue (for Lie), Is Clue, Clue ID (for Answer), Has Item  
* **Case Locations:** Relevant locations for this case.  
  * ADD Location, Location Clues  
* **Clues:** The lifeblood of the mystery.  
  * Clue\_ID, Critical Clue?, Character Implicated, Red Herring, Red\_Herring\_Type, Mechanism\_of\_Misdirection, Debunking Clue (for Red Herring), Source, Clue Summary, Discovery\_Path, Presentation\_Method, Knowledge\_Level, Dependencies, Required\_Actions\_For\_Discovery, Reveals\_Unlocks, Associated Item, Associated Location, Associated Character

## **5\. Strategic Roadmap & Future Enhancements**

### **Phased Rollout**

* **Phase I (V1 \- The Comprehensive Editor & Validator):** The initial focus is on building a flawless, stable foundation. This phase involves creating a robust manual editor for all world/case data coupled with the real-time logical validator.  
* **Phase II (V2 \- The Interactive Plot Graph):** This phase introduces the application's centerpiece: the dynamic, node-based plot graph as the primary case-building interface.  
* **Phase III (V3 \- The Generator):** With the core authoring tools perfected, this phase will introduce procedural generation and AI-assisted authoring to act as a creative co-pilot.

### **Potential Enhancements**

* **Human UI/UX:**  
  * **Contextual Actions:** Right-click menus on the Plot Graph for in-context editing.  
  * **Plot Graph Minimap:** For navigating large, complex case files.  
  * **Focus Mode:** The ability to select a node and dim all unconnected elements to trace a specific logical thread.  
  * **Templates:** Allow users to save characters, locations, or clue structures as reusable templates.  
* **Logical & Narrative Depth:**  
  * **Introduce a Timeline:** Add a temporal dimension to track events, clue discoveries, and interviews, allowing the Validator to check for paradoxes.  
  * **Model Character Knowledge:** Track what each character knows and when they learned it to prevent unintentional plot holes in dialogue.  
  * **Conditional Discovery Paths:** Implement more complex logic for clue discovery (e.g., (Clue A AND Clue B) OR Action C).  
* **Technical Architecture:**  
  * **Upgrade Data Storage:** Evolve from JSON files to a more robust and performant SQLite database for handling complex queries.  
  * **Adopt Model/View Architecture:** Decouple the data (model) from the UI (view) for a more scalable and maintainable codebase.  
  * **Asynchronous Validator:** Run the Validator in a background thread to ensure the UI remains responsive at all times.

\# This document serves as a technical guide for implementing "The Agency Case Builder" using PySide6.

\# It consolidates and organizes the technical strategies and code from the project blueprint.

\# \==================================================================================================

\# Part 1: Core Architecture & Data Management

\# \==================================================================================================

\# The foundation of the application relies on a solid data management strategy. While initial

\# prototypes can use JSON, a scalable application should use a more robust solution.

\# 1.1: Data Strategy: From JSON to SQLite

\# \------------------------------------------

\# For V1, JSON files are acceptable for portability. However, to handle complex relationships

\# and ensure performance, the architecture should be designed to use a SQLite database.

\# Pydantic models are highly recommended for data validation and structure.

\# Example data\_manager.py using the initial JSON approach:

import json

import os

class DataManager:

    """

    Abstracts all file I/O. Responsible for reading/writing case files.

    This would be replaced by a database interaction layer in a production build.

    """

    def \_\_init\_\_(self, data\_path="data"):

        self.data\_path \= data\_path

        if not os.path.exists(self.data\_path):

            os.makedirs(self.data\_path)

    def \_load\_json(self, filename):

        """Helper to load a JSON file from the data directory."""

        path \= os.path.join(self.data\_path, filename)

        try:

            with open(path, 'r', encoding='utf-8') as f:

                return json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):

            return {} \# Return empty dict on error

    def get\_case\_data(self, case\_id):

        """Load data for a specific case."""

        return self.\_load\_json(f"case\_{case\_id}.json")

    \# Recommendation: Evolve this class to use the \`sqlite3\` module to interact

    \# with a case-specific .db file. Use Pydantic models to validate data

    \# before insertion and after retrieval.

\# 1.2: Asynchronous Validator

\# \---------------------------

\# To prevent the UI from freezing during complex validation checks, the Validator logic

\# should run in a separate background thread (QThread) and communicate results back to the

\# main UI thread using Qt's signal/slot mechanism. This ensures a fluid user experience.

\# \==================================================================================================

\# Part 2: Application Entry & Styling

\# \==================================================================================================

\# 2.1: main.py (Application Entry Point)

\# \----------------------------------------

import sys

from PySide6.QtCore import Qt

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

\# In a full application, you would import your main window class

\# from main\_window import MainWindow

def main():

    """

    Initializes the Qt Application and the main window.

    """

    app \= QApplication(sys.argv)

    \# Load the global stylesheet (see Part 2.2)

    try:

        with open("style.qss", "r") as f:

            app.setStyleSheet(f.read())

        print("Stylesheet 'style.qss' loaded successfully.")

    except FileNotFoundError:

        print("Warning: style.qss not found. Using default styles.")

    \# In a real app, you would create and show your main window here

    \# main\_window \= MainWindow()

    \# main\_window.show()

    \# For demonstration purposes, we'll just show a simple window

    demo\_window \= QMainWindow()

    demo\_window.setWindowTitle("The Agency Case Builder")

    demo\_window.setCentralWidget(QLabel("Application Starting Point", alignment=Qt.AlignCenter))

    demo\_window.resize(800, 600\)

    demo\_window.show()

    sys.exit(app.exec())

\# To run the application, you would typically have:

\# if \_\_name\_\_ \== "\_\_main\_\_":

\#     main()

\# 2.2: style.qss (Global Stylesheet)

\# \-----------------------------------

\# This file defines the "Deco-Futurism" theme. It should be saved as \`style.qss\`

\# in the project's root directory.

"""

/\* style.qss \*/

/\* General Window and Widget Styling \*/

QWidget {

    background-color: \#10141a; /\* Base Charcoal \*/

    color: \#f0f0f0; /\* Off-white for readability \*/

    font-family: "Inter", sans-serif;

    font-size: 14px;

}

/\* Main Window Styling \*/

QMainWindow {

    background-color: \#10141a;

}

/\* Headers and Titles \*/

QLabel\#header {

    font-family: "Poiret One", sans-serif;

    color: \#D4AF37; /\* Gold \*/

    font-size: 28px;

    padding: 10px;

    border: none;

}

/\* Standard Buttons \*/

QPushButton {

    background-color: \#2a2f38;

    color: \#00e5ff; /\* Electric Cyan \*/

    border: 1px solid \#00e5ff;

    border-radius: 4px;

    padding: 8px 12px;

    font-weight: bold;

}

QPushButton:hover {

    background-color: \#00e5ff;

    color: \#10141a;

}

QPushButton:pressed {

    background-color: \#00b8d4; /\* A darker cyan for pressed state \*/

}

/\* Input Fields \*/

QLineEdit, QTextEdit, QSpinBox {

    background-color: \#1a1f25;

    border: 1px solid \#4a4f58;

    border-radius: 4px;

    padding: 8px;

    color: \#f0f0f0;

}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {

    border: 1px solid \#00e5ff; /\* Cyan glow on focus \*/

}

/\* Scrollbar Styling \*/

QScrollBar:vertical {

    border: none;

    background: \#1a1f25;

    width: 10px;

    margin: 0px 0px 0px 0px;

}

QScrollBar::handle:vertical {

    background: \#D4AF37; /\* Gold handle \*/

    min-height: 20px;

    border-radius: 5px;

}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {

    height: 0px;

}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {

    background: none;

}

"""

\# \==================================================================================================

\# Part 3: Reusable UI Components

\# \==================================================================================================

\# These custom widgets form the building blocks of the UI, ensuring a consistent look and feel.

\# 3.1: card\_widget.py (Core Reusable Component)

\# \----------------------------------------------

from PySide6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect, QLabel, QHBoxLayout

from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap

from PySide6.QtCore import QPoint, QPropertyAnimation, QEasingCurve, Property

class CardWidget(QFrame):

    """

    A custom widget that serves as the base for all 'card' elements in the UI.

    It includes the Art Deco border, shadow, and a Material-style ripple click effect.

    """

    def \_\_init\_\_(self, parent=None):

        super().\_\_init\_\_(parent)

        self.setLayout(QVBoxLayout())

        self.layout().setContentsMargins(20, 20, 20, 20\) \# Inner padding for content

        \# \--- Shadow Effect for a "lifted" look \---

        shadow \= QGraphicsDropShadowEffect(self)

        shadow.setBlurRadius(25)

        shadow.setColor(QColor(0, 0, 0, 150))

        shadow.setOffset(0, 3\)

        self.setGraphicsEffect(shadow)

        \# \--- Ripple Effect Properties \---

        self.\_ripple\_radius \= 0

        self.\_ripple\_opacity \= 0

        self.\_ripple\_pos \= QPoint()

        \# \--- Set base background color \---

        self.setAutoFillBackground(True)

        p \= self.palette()

        p.setColor(self.backgroundRole(), QColor("\#1a1f25"))

        self.setPalette(p)

    \# \--- Ripple Animation Properties (for QPropertyAnimation) \---

    @Property(float)

    def rippleRadius(self):

        return self.\_ripple\_radius

    @rippleRadius.setter

    def rippleRadius(self, value):

        self.\_ripple\_radius \= value

        self.update()  \# Trigger a repaint

    @Property(float)

    def rippleOpacity(self):

        return self.\_ripple\_opacity

    @rippleOpacity.setter

    def rippleOpacity(self, value):

        self.\_ripple\_opacity \= value

        self.update()  \# Trigger a repaint

    def mousePressEvent(self, event):

        \# Start the ripple animation on click

        self.\_ripple\_pos \= event.pos()

        

        radius\_anim \= QPropertyAnimation(self, b"rippleRadius")

        radius\_anim.setStartValue(0)

        radius\_anim.setEndValue(self.width() \* 0.8)

        radius\_anim.setDuration(400)

        radius\_anim.setEasingCurve(QEasingCurve.OutCubic)

        opacity\_anim \= QPropertyAnimation(self, b"rippleOpacity")

        opacity\_anim.setStartValue(0.4)

        opacity\_anim.setEndValue(0.0)

        opacity\_anim.setDuration(450)

        

        radius\_anim.start()

        opacity\_anim.start()

        super().mousePressEvent(event)

    def paintEvent(self, event):

        \# Let the base class paint its background first

        super().paintEvent(event)

        painter \= QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        \# \--- Draw Ripple Effect \---

        if self.\_ripple\_radius \> 0:

            painter.setPen(Qt.NoPen)

            color \= QColor("\#00e5ff")  \# Cyan ripple

            color.setAlphaF(self.\_ripple\_opacity)

            painter.setBrush(QBrush(color))

            painter.drawEllipse(self.\_ripple\_pos, self.\_ripple\_radius, self.\_ripple\_radius)

        \# \--- Draw Art Deco Border (on top of everything else) \---

        pen \= QPen(QColor("\#D4AF37"))  \# Gold color

        pen.setWidth(2)

        painter.setPen(pen)

        rect \= self.rect().adjusted(1, 1, \-1, \-1)

        painter.drawRect(rect)

        

        \# Draw geometric corners for the Art Deco feel

        corner\_size \= 10

        painter.drawLine(rect.topLeft(), rect.topLeft() \+ QPoint(corner\_size, 0))

        painter.drawLine(rect.topLeft(), rect.topLeft() \+ QPoint(0, corner\_size))

        painter.drawLine(rect.topRight(), rect.topRight() \- QPoint(corner\_size, 0))

        painter.drawLine(rect.topRight(), rect.topRight() \+ QPoint(0, corner\_size))

        painter.drawLine(rect.bottomLeft(), rect.bottomLeft() \+ QPoint(corner\_size, 0))

        painter.drawLine(rect.bottomLeft(), rect.bottomLeft() \- QPoint(0, corner\_size))

        painter.drawLine(rect.bottomRight(), rect.bottomRight() \- QPoint(corner\_size, 0))

        painter.drawLine(rect.bottomRight(), rect.bottomRight() \- QPoint(0, corner\_size))

\# 3.2: character\_card\_widget.py (Example Asset Card)

\# \---------------------------------------------------

class CharacterCard(CardWidget):

    """ An example of how to use the CardWidget to display a character's info. """

    def \_\_init\_\_(self, character\_name, character\_archetype, image\_path, parent=None):

        super().\_\_init\_\_(parent)

        

        main\_layout \= QHBoxLayout(self.layout()) \# Get the layout from the parent

        

        \# \--- Image Label (Left Side) \---

        self.image\_label \= QLabel()

        self.image\_label.setFixedSize(120, 120\)

        self.image\_label.setScaledContents(True)

        pixmap \= QPixmap(image\_path)

        if pixmap.isNull():

             \# Provide a fallback placeholder

             pixmap \= QPixmap(120, 120\)

             pixmap.fill(QColor("\#2a2f38"))

        self.image\_label.setPixmap(pixmap)

        self.image\_label.setStyleSheet("""

            QLabel {

                border: 2px solid \#D4AF37; /\* Gold border \*/

                border-radius: 60px; /\* Half of the size for a circle \*/

            }

        """)

        

        \# \--- Info Layout (Right Side) \---

        info\_layout \= QVBoxLayout()

        info\_layout.setSpacing(5)

        info\_layout.setAlignment(Qt.AlignVCenter)

        

        name\_label \= QLabel(character\_name)

        name\_label.setObjectName("header") \# Use the header style from QSS

        name\_label.setStyleSheet("font-size: 22px; padding: 0;")

        

        archetype\_label \= QLabel(character\_archetype)

        archetype\_label.setStyleSheet("color: \#8a8f98; font-style: italic; border: none;")

        

        info\_layout.addWidget(name\_label)

        info\_layout.addWidget(archetype\_label)

        info\_layout.addStretch()

        

        main\_layout.addWidget(self.image\_label)

        main\_layout.addLayout(info\_layout)

        

        self.setMinimumHeight(180)

\# \==================================================================================================

\# Part 4: The Interactive Plot Graph

\# \==================================================================================================

\# This is the centerpiece of the application. It uses a QGraphicsView to create a node-based

\# editor for visually constructing the narrative.

from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, 

                               QGraphicsProxyWidget, QGraphicsItem)

from PySide6.QtCore import QPointF

from PySide6.QtGui import QPainterPath

class ConnectionNode(QGraphicsItem):

    """Represents a single asset card as a movable node on the graph."""

    def \_\_init\_\_(self, card\_widget, parent=None):

        super().\_\_init\_\_(parent)

        self.proxy \= QGraphicsProxyWidget(self)

        self.proxy.setWidget(card\_widget)

        

        self.setFlags(QGraphicsItem.ItemIsMovable | 

                      QGraphicsItem.ItemIsSelectable | 

                      QGraphicsItem.ItemSendsGeometryChanges)

        

        self.sockets \= \[\]

        self.socket\_radius \= 6

        self.\_create\_sockets()

        self.lines \= \[\]

    def \_create\_sockets(self):

        card\_rect \= self.proxy.widget().rect()

        \# Sockets are positioned relative to the ConnectionNode's origin

        self.sockets.append(QPointF(0, card\_rect.height() / 2)) \# Left

        self.sockets.append(QPointF(card\_rect.width(), card\_rect.height() / 2)) \# Right

    def boundingRect(self):

        return self.proxy.boundingRect().adjusted(-self.socket\_radius, \-self.socket\_radius, self.socket\_radius, self.socket\_radius)

    def paint(self, painter, option, widget=None):

        painter.setPen(QPen(QColor("\#D4AF37"), 2))

        painter.setBrush(QBrush(QColor("\#10141a")))

        for pos in self.sockets:

            painter.drawEllipse(pos, self.socket\_radius, self.socket\_radius)

            

    def itemChange(self, change, value):

        if change \== QGraphicsItem.ItemPositionHasChanged:

            for line in self.lines:

                line.update\_path()

        return super().itemChange(change, value)

    def get\_socket\_scene\_pos(self, index):

        if 0 \<= index \< len(self.sockets):

            return self.mapToScene(self.sockets\[index\])

        return QPointF()

class ConnectionLine(QGraphicsItem):

    """A curved Bezier line to connect two nodes."""

    def \_\_init\_\_(self, start\_node, start\_socket\_idx, end\_node, end\_socket\_idx, parent=None):

        super().\_\_init\_\_(parent)

        self.start\_node \= start\_node

        self.start\_socket\_idx \= start\_socket\_idx

        self.end\_node \= end\_node

        self.end\_socket\_idx \= end\_socket\_idx

        

        self.pen \= QPen(QColor("\#00e5ff"), 2\)

        self.pen.setCapStyle(Qt.RoundCap)

        

        self.\_path \= QPainterPath()

        self.update\_path()

    def boundingRect(self):

        return self.\_path.boundingRect()

    def update\_path(self):

        self.prepareGeometryChange()

        start\_pos \= self.start\_node.get\_socket\_scene\_pos(self.start\_socket\_idx)

        end\_pos \= self.end\_node.get\_socket\_scene\_pos(self.end\_socket\_idx)

        

        path \= QPainterPath()

        path.moveTo(start\_pos)

        

        dx \= end\_pos.x() \- start\_pos.x()

        dy \= end\_pos.y() \- start\_pos.y()

        ctrl1 \= QPointF(start\_pos.x() \+ dx \* 0.5, start\_pos.y())

        ctrl2 \= QPointF(start\_pos.x() \+ dx \* 0.5, end\_pos.y())

        

        path.cubicTo(ctrl1, ctrl2, end\_pos)

        self.\_path \= path

    def paint(self, painter, option, widget=None):

        painter.setPen(self.pen)

        painter.setBrush(Qt.NoBrush)

        painter.drawPath(self.\_path)

class PlotGraphView(QGraphicsView):

    """The main view for displaying and interacting with the plot graph."""

    def \_\_init\_\_(self, parent=None):

        super().\_\_init\_\_(parent)

        self.scene \= QGraphicsScene(self)

        self.setScene(self.scene)

        

        self.setRenderHint(QPainter.Antialiasing)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.scene.setBackgroundBrush(QColor("\#10141a"))

    def add\_node(self, widget, pos=QPointF(0, 0)):

        node \= ConnectionNode(widget)

        node.setPos(pos)

        self.scene.addItem(node)

        return node

    def connect\_nodes(self, start\_node, end\_node):

        \# Default connection: right socket of start to left socket of end

        start\_socket\_idx, end\_socket\_idx \= 1, 0

        

        connection \= ConnectionLine(start\_node, start\_socket\_idx, end\_node, end\_socket\_idx)

        self.scene.addItem(connection)

        

        \# Register the line with the nodes so they can update it on move

        start\_node.lines.append(connection)

        end\_node.lines.append(connection)

        

        return connection

        

    def wheelEvent(self, event):

        zoom\_in\_factor \= 1.15

        zoom\_out\_factor \= 1 / zoom\_in\_factor

        

        if event.angleDelta().y() \> 0:

            self.scale(zoom\_in\_factor, zoom\_in\_factor)

        else:

            self.scale(zoom\_out\_factor, zoom\_out\_factor)

\# \--- Example Usage for Plot Graph \---

\# This demonstrates how to create the graph view and populate it with nodes.

def run\_plot\_graph\_demo():

    app \= QApplication.instance() or QApplication(sys.argv)

    

    try:

        with open("style.qss", "r") as f:

            app.setStyleSheet(f.read())

    except FileNotFoundError:

        print("Warning: style.qss not found.")

    view \= PlotGraphView()

    

    \# Create some asset cards

    \# NOTE: Provide a valid path to an image for the demo to work correctly.

    char\_card \= CharacterCard("Det. Harding", "Hard-boiled Detective", "path/to/image.png")

    

    clue\_card \= CardWidget()

    clue\_layout \= QVBoxLayout(clue\_card.layout())

    clue\_layout.addWidget(QLabel("Clue: Muddy Footprint"))

    

    location\_card \= CardWidget()

    loc\_layout \= QVBoxLayout(location\_card.layout())

    loc\_layout.addWidget(QLabel("Location: The Docks"))

    \# Add them to the scene as nodes

    node1 \= view.add\_node(char\_card, QPointF(-300, 0))

    node2 \= view.add\_node(clue\_card, QPointF(150, \-150))

    node3 \= view.add\_node(location\_card, QPointF(150, 150))

    

    \# Connect the nodes

    view.connect\_nodes(node1, node2) \# Det. Harding \-\> Clue

    view.connect\_nodes(node3, node2) \# Location \-\> Clue

    

    view.setWindowTitle("Interactive Plot Graph Demo")

    view.resize(1000, 800\)

    view.show()

    

    sys.exit(app.exec())

\# To run the demo, uncomment the following line in your main script:

\# run\_plot\_graph\_demo()
