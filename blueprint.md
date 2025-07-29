# **Project Blueprint: The Agency Case Builder**

**Official Repository:** [https://github.com/manosdvd/agencyp/](https://github.com/manosdvd/agencyp/)

**Objective:** Develop a standalone desktop application, "The Agency," for authoring intricate and logically sound detective stories. This application will serve as an intelligent and immersive workspace, translating the complex web of a mystery into a clear, manageable, and inspiring digital format.

## **1\. Core Vision & Philosophy**

* **Product:** "The Agency" is an integrated authoring tool that functions as a digital extension of a detective's mind. It's a space for constructing worlds, weaving plots, and stress-testing the logic of a mystery.  
* **Core Philosophy:** The creative process is paramount. The software must be intuitive, powerful, and visually engaging. It will blend the psychological depth and atmospheric tension of **neo-noir** with the elegant geometry of Art Deco and the clarity of modern speculative UI. It should feel less like data entry and more like assembling clues on a futuristic evidence board.  
* **Strategic Phases:**  
  * **Phase I (V1 \- The Comprehensive Editor & Validator):** Build a robust manual editor for all world and case data, coupled with integrated real-time logical validation. The focus is on a flawless, stable foundation with a fully realized UI/UX.  
  * **Phase II (V2 \- The Interactive Plot Graph):** Introduce the dynamic, node-based plot graph as the primary case-building interface, allowing for visual construction and analysis of the narrative's logical flow.  
  * **Phase III (V3 \- The Generator):** Introduce procedural generation and AI-assisted authoring to help scaffold case skeletons, characters, and dialogue, acting as a creative co-pilot.

## **2\. UI/UX Design: The Digital Detective's Mind**

The user experience is central to this project. The goal is to create an interface that is not only efficient but also inspiring, making the author feel like a brilliant detective piecing together a complex puzzle.

* **Aesthetic & Design System: "Deco-Futurism"**  
  * **Core Theme:** A fusion of four key influences: the moody atmosphere of **classic noir**, the psychological depth and high-contrast lighting of **neo-noir**, the elegant geometry of **Art Deco** (inspired by *Poirot*), and the clean, holographic aesthetic of **modern sci-fi** (inspired by *Star Trek: Picard*).  
  * **Color Palette:**  
    * **Base:** A deep, dark charcoal (\#10141a), representing the pervasive shadows of the noir genre.  
    * **Primary Accent (Holographic):** A vibrant, **electric cyan** (\#00e5ff) for all interactive elements. This acts as the "neon in the rain," providing a stark, modern contrast to the dark background.  
    * **Secondary Accent (Art Deco):** A warm, elegant **gold** (\#D4AF37) for borders, major headers, and decorative geometric motifs, grounding the futuristic elements with a touch of classic sophistication.  
  * **Shape & Form:** The UI is built on a foundation of "cards" or elevated surfaces. These cards will be framed with thin, gold, Art Deco-inspired borders. The overall layout will prioritize clean lines, symmetry, and elegant geometric arrangements.  
  * **Typography:** A primary sans-serif font (like Roboto) for body text and UI elements to ensure clarity. A stylized, geometric Art Deco font will be used for major headers to provide thematic flair.  
* **Animation & Interactivity Philosophy**  
  * **Information is Physical & Layered:** UI elements are treated as objects in a layered, holographic space. Detail views will animate in by **sliding and fading**, giving the impression of coming forward to the user for focus. This creates a sense of depth and parallax.  
  * **Motion with Purpose:** Every animation is a direct and intuitive response to user input. Clicks trigger a **Material ripple effect**, providing immediate tactile feedback.  
  * **Responsive Feedback:** Interactive elements provide clear visual cues. List items will **"lift"** with a shadow and highlight on hover. Buttons will have smooth color transitions, and focused input fields will feature a soft **animated glow**.  
  * **Subtle Ambiance:** The interface will feel constantly "online" through non-distracting ambient motion, such as softly pulsing glows on key UI elements, reinforcing the high-tech aesthetic.

## **3\. Authoring Tools: The Workspace**

These are the primary interfaces where the author will spend their time. They must be powerful, intuitive, and align with our "Deco-Futurism" design philosophy.

* **The Interactive Plot Graph (The Evidence Board):**  
  * **Concept:** This is the author's main workspace for structuring the case. It will be built using **PySide6's Graphics View Framework**, a highly capable system for creating zoomable, pannable canvases with interactive items. Every piece of case data (clues, characters, locations, items) can be placed as a node.  
  * **Functionality:**  
    * Authors can visually link nodes to define the logical flow of the investigation.  
    * Connections are not static lines but animated **"glowing threads of logic"** that are drawn in real-time to visually reinforce the deductive process.  
    * **Live Validation Feedback:** If the Validator detects an issue (e.g., a clue that doesn't lead anywhere), the corresponding node or thread on the graph will **flicker with a red glow**, providing immediate, visual feedback in the exact location of the problem.  
* **The Gamified Timeline Editor (Chronological Reconstruction):**  
  * **Concept:** Authoring the ground-truth timeline of events should feel like a puzzle. The UI will guide the author backward from the crime.  
  * **Functionality:**  
    * The editor will present a clear, linear track.  
    * Chronological or causal impossibilities (e.g., a character being in two places at once) will be flagged in real-time directly on the timeline, highlighting the conflicting events in red.

## **4\. The Validator: The Logical Co-Pilot**

The Validator is the application's brain. It's an ever-present assistant that ensures the story is logically sound and solvable.

* **Persistent & Non-Intrusive:** The Validator's feedback will be displayed in a dedicated panel, updating in real-time as the author works. It will not use disruptive pop-ups.  
* **Actionable Feedback:** Every validation message will be clear, concise, and provide a "Go to Issue" button that instantly navigates the user to the exact field or node on the Plot Graph that contains the error.

## **5\. Data & Performance Architecture**

The application must feel instantaneous. The architecture is designed to support a highly responsive and interconnected UI.

* **Data Storage Model: File-Based JSON**  
  * The primary storage method is a directory of human-readable .json files, organized by CaseFile. This ensures maximum portability and simplifies version control.  
* **Performance Strategy: In-Memory Reconstruction**  
  * On application start, all data from the JSON files is loaded into memory and fully reconstructed into their proper Python dataclass objects. This allows for fast, type-safe data manipulation.

## **6\. Development Methodology**

* **UI Framework:** The project uses **PySide6 (the official Python bindings for Qt)**. This framework was chosen for its stability, maturity, and powerful animation system (QPropertyAnimation) and styling engine (QSS), which are essential for realizing our hybrid aesthetic.  
* **Component-Based UI:** The PySide6 UI is built using reusable custom QWidget classes to keep the code clean, maintainable, and scalable.  
* **Iterative Implementation:** We will build and test one feature at a time, ensuring each piece is polished and aligns with the design philosophy before moving to the next.