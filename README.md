# The Agency: A Detective Story Authoring Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)

This repository contains the source code for "The Agency," a standalone desktop application for authoring intricate and logically sound detective stories. It provides a comprehensive, intuitive environment for creating, managing, and rigorously validating all game data, from individual CaseFile mysteries to the global lore and assets of the game world.

## Core Features

*   **World Builder:** A suite of specialized visual tools for creating and managing characters, locations, factions, and lore.
*   **Case Builder:** A powerful workspace for structuring the case, including an interactive bulletin board (Plot Graph) and a gamified timeline editor (eventChain).
*   **The Validator:** An intelligent "story editor" that provides real-time, actionable feedback on the logical consistency and playability of the story.
*   **Data-driven:** The application uses a human-readable JSON file-based data storage model, making it easy to version control and use with other tools.
*   **Noir-themed UI:** A visually engaging interface with a classic noir aesthetic and modern usability.

## Getting Started

### Prerequisites

*   Python 3.10+ is required.

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/manosdvd/agencyp.git
    cd agencyp
    ```

2.  **Create and activate a virtual environment:**

    *This is a required step.*

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the following command from the project root directory:

```bash
python3 main.py
```

## Project Structure

```
.agencyp/
├── .gitignore
├── blueprint.md
├── data/
│   ├── characters.json
│   ├── districts.json
│   └── images/
├── main.py
├── README.md
├── requirements.txt
├── schemas.py
└── venv/
```

*   `main.py`: The main entry point for the application.
*   `schemas.py`: Defines the Pydantic models for the data schemas.
*   `data/`: Contains the JSON data files for the world and case assets.
*   `blueprint.md`: The project's master plan and single source of truth.
*   `requirements.txt`: A list of the Python dependencies for the project.
*   `venv/`: The Python virtual environment directory.

## Development Notes

*   **Virtual Environment:** All development and execution *must* be done within the project's `venv`. Activate it with `source venv/bin/activate`.
*   **PySide6 UI Framework:**
    *   **Styling:** PySide6 uses Qt Style Sheets (QSS) for styling, similar to CSS.
    *   **Event Handling:** Signals and slots are used for event handling.
    *   **Layouts:** Widgets are arranged using layout managers (e.g., `QVBoxLayout`, `QHBoxLayout`, `QFormLayout`).

## Technology Stack

*   **Python:** The core programming language.
*   **PySide6:** The UI framework for building the desktop application.
*   **Pydantic:** Used for data validation and schema definition.

## Roadmap

The project is divided into three strategic phases:

*   **Phase I (V1 - The Comprehensive Editor & Validator):** Build a robust manual editor for creating all world and case data, coupled with integrated real-time and pre-export logical validation.
*   **Phase II (V2 - The World-Builder & Plot Graph):** Expand the tool to manage global game world data more dynamically and introduce advanced creative assistance tools, including the fully interactive plot graph.
*   **Phase III (V3 - The Generator):** Introduce procedural generation capabilities to assist in the rapid creation of case skeletons and characters.

For more details, please refer to the [project blueprint](blueprint.md).