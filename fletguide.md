# **A Developer's Comprehensive Guide to Building Multi-Platform Applications with Flet**

## **Introduction: The Flet Philosophy and Architecture**

Flet is a Python framework designed to empower developers to build interactive, real-time web, mobile, and desktop applications without requiring prior frontend development experience.1 Its guiding philosophy is to enable the rapid transition from "idea to app in minutes," catering to a wide array of projects, from internal team dashboards and data entry forms to high-fidelity prototypes.2

### **Core Architecture**

At its heart, Flet employs a Server-Driven UI (SDUI) architecture.4 Unlike traditional web development where the client-side (browser) handles much of the UI logic, in Flet, the Python application runs as a persistent process that manages all application state and control flow. This Python backend communicates with an out-of-process Flet server, known as

Fletd, through a WebSocket-based protocol. The Fletd server then drives a client built with Flutter, Google's UI toolkit, which is responsible for rendering the user interface on the target platform.4 This unique architecture is what allows a single Python codebase to be deployed across the web, desktop (Windows, macOS, Linux), and mobile devices.2

### **The Monolith Advantage**

Flet champions a simplified architectural model that stands in contrast to the often complex stacks of modern web development which can involve a JavaScript frontend, a REST API backend, databases, and caching layers.2 Instead, Flet promotes the development of a stateful, monolithic application where the entire UI and business logic reside within a single Python program. This approach significantly reduces complexity, allowing developers to focus on application features rather than on managing a distributed system.3

The framework's design represents a deliberate and opinionated approach to GUI development, rather than a simple 1:1 binding for Flutter. While it leverages Flutter's powerful rendering engine to ensure applications look professional and polished, Flet intentionally abstracts away many of Flutter's complexities.1 It achieves this by combining smaller Flutter "widgets" into ready-to-use "controls" with sensible defaults, and most notably, by implementing an imperative programming model (

page.update()) which is philosophically distinct from Flutter's declarative nature.1 This design choice, coupled with its "batteries-included" distribution that bundles a web server and desktop clients, makes Flet a distinct paradigm tailored for Python developers, not just a port of Flutter to Python.2 This distinction is crucial for developers, especially those with a Flutter background, as it sets clear expectations about the development experience Flet provides.

## **Part I: Foundations of Flet Development**

### **Section 1: Environment Setup and Project Initialization**

Before building an application, a proper development environment must be configured. Flet has specific prerequisites and offers flexible project setup options.

#### **Prerequisites**

Flet requires Python 3.9 or a later version to be installed on the system. It officially supports the following operating systems 8:

* macOS 11 (Big Sur) or later.  
* 64-bit versions of Windows 10 or later.  
* Debian Linux 11 or later, and Ubuntu Linux 20.04 LTS or later.

For Linux users, developing and running Flet apps may require additional dependencies, particularly for multimedia support. For instance, if an application needs audio or video capabilities, GStreamer libraries must be installed to avoid runtime errors.8

#### **Virtual Environments**

It is a strongly recommended best practice to use a virtual environment for every Flet project. This isolates project dependencies and avoids conflicts with other Python projects on the same machine. Flet supports several popular tools for managing virtual environments.8

* **Using** venv: Python's built-in module.  
  1. Create and navigate to a project directory: mkdir first-flet-app && cd first-flet-app  
  2. Create the virtual environment: python \-m venv.venv  
  3. Activate it:  
     * Windows: .venv\\Scripts\\activate  
     * macOS/Linux: source.venv/bin/activate  
* **Using Poetry**: A popular dependency management tool.  
  1. Create a project directory and initialize Poetry: mkdir my-app && cd my-app  
  2. Run poetry init to create a pyproject.toml file.  
  3. Add Flet: poetry add 'flet\[all\]'  
* **Using** uv: An extremely fast, modern package manager.  
  1. Create a project directory and initialize uv: mkdir my-app && cd my-app  
  2. Run uv init to create a pyproject.toml file.  
  3. Add Flet: uv add 'flet\[all\]'

#### **Installation**

Once the virtual environment is activated, install Flet using pip. The command pip install flet installs the core package. However, for access to all features, including packaging for desktop, the \[all\] extra is recommended 1:

Bash

pip install 'flet\[all\]'

To verify that Flet has been installed correctly, run flet \--version in the terminal.8

#### **Running Your First App**

Flet applications can be executed in two primary modes from the same codebase.

* **As a Desktop App**: This launches the application in a native OS window. This can be done using the Flet CLI or by running the Python script directly.1  
  * Using Flet CLI: flet run my\_app.py  
  * Using Python interpreter: python my\_app.py (requires the app to end with ft.app(target=main))  
* **As a Web App**: This runs the application in a web browser.  
  * Using Flet CLI: flet run \--web my\_app.py 1  
  * Programmatically: Modify the last line of the script to ft.app(target=main, view=ft.AppView.WEB\_BROWSER).3

#### **Troubleshooting**

Some common issues can arise during setup 9:

* **Naming Collision**: Never name your project file flet.py, as this will conflict with the installed Flet library itself. Use a name like app.py or main.py.  
* **Environment Issues**: Ensure the correct virtual environment is activated before running your script.  
* **Python Version**: Verify that the Python interpreter being used meets the minimum version requirement (3.9+).

### **Section 2: The Anatomy of a Flet Application**

Understanding the fundamental structure of a Flet app is key to effective development. The official "Counter" example serves as an excellent case study for dissecting its core components.1

Python

import flet as ft

def main(page: ft.Page):  
    page.title \= "Flet counter example"  
    page.vertical\_alignment \= ft.MainAxisAlignment.CENTER

    txt\_number \= ft.TextField(value="0", text\_align=ft.TextAlign.RIGHT, width=100)

    def minus\_click(e):  
        txt\_number.value \= str(int(txt\_number.value) \- 1)  
        page.update()

    def plus\_click(e):  
        txt\_number.value \= str(int(txt\_number.value) \+ 1)  
        page.update()

    page.add(  
        ft.Row(  
           ,  
            alignment=ft.MainAxisAlignment.CENTER,  
        )  
    )

ft.app(target=main)

* import flet as ft: This is the standard convention for importing the Flet library.1  
* def main(page: ft.Page):: This function serves as the entry point for the application. For every new user session (e.g., a new browser tab or a new desktop app instance), Flet starts a new thread and calls this main function.9  
* The page: ft.Page Argument: The Page object is the root container, or "canvas," for all UI elements in a session. All other controls must be added to the Page or to one of its descendants to be visible.6 Properties like  
   page.title and page.vertical\_alignment configure the top-level window or browser page.  
* ft.app(target=main): This function call initializes the Flet app, starts the background web server, and runs the main function for new user connections. It is a blocking call that keeps the application alive to handle UI events.9

#### **Flet Coding Conventions: A Guide to Capitalization and Naming**

A key aspect of Flet's design is its seamless integration with Python's idiomatic coding styles. By adhering to the standard PEP 8 conventions, Flet lowers the cognitive load for Python developers, making the framework feel immediately familiar. This is not an accident but a deliberate design choice to ensure developers do not need to learn a new stylistic "dialect." The conventions are consistent across all official examples and documentation.1

| Element Type | Convention | Example | Notes |
| :---- | :---- | :---- | :---- |
| **Control Classes** | PascalCase | ft.ElevatedButton, ft.Column | Standard Python convention for class names. |
| **Functions/Methods** | snake\_case | main(), page.update() | Standard for Python functions and methods. |
| **Variables/Instances** | snake\_case | txt\_number, new\_task | Standard for Python variables. |
| **Properties/Attributes** | snake\_case | .value, .on\_click, .controls | Used for all control properties and event handlers. |
| **Constants/Enums** | UPPER\_SNAKE\_CASE | ft.MainAxisAlignment.CENTER, ft.colors.BLUE | Standard for constants and enumeration members. |

### **Section 3: Core Concepts: Controls and the Imperative UI Model**

The user interface in a Flet application is constructed from a set of building blocks called **Controls** (also referred to as widgets).6 These are simply regular Python classes that are instantiated to create UI elements.

#### **The Control Hierarchy**

All controls in a Flet app are organized into a tree-like structure with the Page object at its root. Controls that can contain other controls, such as Row, Column, or Stack, are known as container controls. They typically have a controls property, which is a list that holds their child controls.6

#### **The Imperative Workflow**

Flet employs an imperative UI model, which is a core tenet of its design. This model is straightforward and follows a clear, three-step process 6:

1. **Instantiation**: You create instances of control classes to define UI elements. For example: t \= ft.Text(value="Hello").  
2. **Mutation**: You modify the properties of these instances directly in your Python code to change their state or appearance. For example: t.value \= "Goodbye".  
3. **Update**: You explicitly command Flet to render these changes to the frontend by calling page.update(). Flet is efficient and will only send the delta of changes made since the last update to the client.1

A convenient shortcut, page.add(control), combines adding a control to the page's controls list and calling page.update() in a single step.6

#### **Common Control Properties**

Most Flet controls share a set of common properties that allow for consistent manipulation of the UI.

* visible: A boolean that determines whether a control (and all of its children) is rendered on the page. When visible is False, the control is completely removed from the render tree and cannot be interacted with or emit events.6  
* disabled: A boolean that controls the interactive state of a control. A key feature is that this property propagates downward through the control tree. Setting disabled=True on a container control, like a Column containing a form, will disable every input field and button within it, simplifying state management for entire UI sections.6  
* expand: When a control is placed inside a Row or Column, this property can be used to make it fill the available space. It can be a boolean (True) or an integer representing a flex factor for creating proportional layouts.12  
* data: This property allows you to attach arbitrary custom data to any control. This is particularly useful for passing information to event handlers without relying on global variables.12

## **Part II: Building the User Interface**

### **Section 4: A Deep Dive into Flet Controls**

Flet comes "batteries-included" with a comprehensive library of over 100 pre-built controls that are based on Google's Flutter widgets.2 These controls are organized into logical categories, and the official interactive Controls Gallery is an indispensable resource for exploring them with live code samples.15

| Category | Description | Example Controls |
| :---- | :---- | :---- |
| **Layout** | Controls for arranging other controls on the page. | Row, Column, Container, Stack, Card 13 |
| **Navigation** | Controls for app structure and moving between views. | View, Tabs, NavigationBar 12 |
| **Information Displays** | Controls for presenting static information. | Text, Markdown, Icon, Image, DataTable 12 |
| **Buttons** | Controls that trigger actions when clicked. | ElevatedButton, IconButton, FloatingActionButton 16 |
| **Input & Selections** | Controls for user input and choices. | TextField, Checkbox, Dropdown, Slider, Switch 12 |
| **Dialogs, Alerts & Panels** | Controls for displaying transient pop-up messages. | AlertDialog, Banner, SnackBar 12 |

#### **Detailed Control Examples**

Below are code snippets and explanations for some of the most frequently used controls.

##### **Information Displays**

* ft.Text: The most basic control for displaying text. It can be styled with properties like color, size, weight, and can even display complex, multi-styled text using the spans property.6  
* Python

page.add(  
    ft.Text("Simple text"),  
    ft.Text("Styled text", size=20, color="blue", italic=True),  
    ft.Text(  
        spans=  
    )  
)

*   
*   
* ft.Markdown: Renders text formatted with Markdown syntax. It supports extensions, such as ft.MarkdownExtensionSet.GITHUB\_WEB, and can handle link clicks via the on\_tap\_link event handler.18  
* Python

def open\_link(e):  
    page.launch\_url(e.data)

markdown\_content \= """  
\# This is a header

This is a link to \[Google\](https://google.com).

\* Item 1  
\* Item 2  
"""

page.add(  
    ft.Markdown(  
        markdown\_content,  
        extension\_set=ft.MarkdownExtensionSet.GITHUB\_WEB,  
        on\_tap\_link=open\_link  
    )  
)

*   
*   
* ft.Icon: Displays an icon from the Material Icons library. The specific icon is chosen from the ft.icons collection.1  
* Python

page.add(ft.Icon(name=ft.icons.FAVORITE, color=ft.colors.PINK))

*   
*   
* ft.Image: Displays an image from a URL or a local asset path. It also supports transformations like rotate and scale.12  
* Python

page.add(  
    ft.Image(  
        src="https://flet.dev/img/flet-logo.png",  
        width=100,  
        height=100,  
        fit=ft.ImageFit.CONTAIN,  
    )  
)

*   
* 

##### **Input and Selections**

* ft.TextField: A versatile control for text input. Key properties include label, hint\_text, password (to obscure text), can\_reveal\_password, and error\_text for validation feedback.1  
* Python

user\_name \= ft.TextField(label="Username", autofocus=True)  
password \= ft.TextField(label="Password", password=True, can\_reveal\_password=True)  
page.add(user\_name, password)

*   
*   
* ft.Checkbox: A standard checkbox for boolean input. It uses the on\_change event to report state changes.6  
* Python

def checkbox\_changed(e):  
    print(f"Checkbox value: {e.control.value}")

page.add(ft.Checkbox(label="I agree to the terms", on\_change=checkbox\_changed))

*   
*   
* ft.Dropdown: A dropdown menu for selecting from a list of options. The options are provided as a list of ft.dropdown.Option objects.6  
* Python

page.add(  
    ft.Dropdown(  
        label="Color",  
        options=  
    )  
)

*   
* 

##### **Buttons**

* ft.ElevatedButton: A standard Material Design button with a raised appearance. Its primary event is on\_click.6  
* Python

def button\_clicked(e):  
    page.add(ft.Text("Button was clicked\!"))

page.add(ft.ElevatedButton(text="Click me", on\_click=button\_clicked))

*   
*   
* ft.IconButton: A button that consists solely of an icon, making it ideal for toolbars or compact UIs.1  
* Python

page.add(  
    ft.IconButton(  
        icon=ft.icons.ADD\_CIRCLE,  
        icon\_color="green",  
        tooltip="Add item",  
        on\_click=button\_clicked  
    )  
)

*   
*   
* ft.FloatingActionButton: A circular icon button that is typically used for a primary, or most common, action on a screen. It appears to "float" above the other UI elements.22  
* Python

page.add(  
    ft.FloatingActionButton(  
        icon=ft.icons.ADD,  
        on\_click=button\_clicked  
    )  
)

*   
* 

### **Section 5: Mastering Layout and Structure**

Arranging controls effectively is fundamental to creating a well-organized and visually appealing application. Flet provides several powerful layout controls for this purpose.

#### **Row and Column**

Row and Column are the workhorses of Flet layouts. Row arranges its child controls in a horizontal array, while Column arranges them vertically.13

Key properties for alignment and spacing include 13:

* alignment: Controls the distribution of children along the main axis (horizontal for Row, vertical for Column). It takes a ft.MainAxisAlignment value (e.g., START, CENTER, END, SPACE\_BETWEEN).  
* vertical\_alignment (for Row) and horizontal\_alignment (for Column): Controls alignment along the cross axis. They take a ft.CrossAxisAlignment value (e.g., START, CENTER, END, STRETCH).  
* spacing: Defines the space in virtual pixels between each child control.

A crucial concept for building responsive UIs is the expand property. When a child of a Row or Column has expand=True, it will stretch to fill all available space along the main axis. If multiple children have integer expand values (e.g., expand=1, expand=3), they will divide the available space proportionally.12

If the content of a Row or Column exceeds the available screen space, you can enable scrolling by setting the scroll property to a ft.ScrollMode value, such as ft.ScrollMode.AUTO.13

Python

page.add(  
    ft.Row(  
        controls=,  
        spacing=10,  
        height=100  
    )  
)

#### **Container**

The Container control is a highly versatile layout tool that acts as a decorator for a single child control. It can be used to add background colors, borders, padding, margins, and more.13 Its key properties include

width, height, padding, margin, bgcolor, border, and border\_radius. Furthermore, a Container can be made interactive by assigning a handler to its on\_click event, effectively turning any area of the UI into a clickable button.13

Python

page.add(  
    ft.Container(  
        content=ft.Text("Clickable Container"),  
        width=200,  
        height=100,  
        bgcolor="blue",  
        border\_radius=10,  
        padding=20,  
        on\_click=lambda e: print("Container clicked\!"),  
        alignment=ft.alignment.center  
    )  
)

#### **Stack**

The Stack control allows you to layer children on top of one another. This is useful for creating overlapping UI elements, such as placing a text label over an image. Child controls within a Stack can be positioned precisely using properties like top, left, right, and bottom.12

### **Section 6: Handling User Interaction with Events**

Flet's event model is straightforward: user actions on the client (like a button click) generate an event that is sent via WebSocket to the Python script. The script then executes a corresponding event handler function that you have defined.6

* on\_click: This is the most common event, fired by buttons (ElevatedButton, IconButton, etc.) and other clickable controls like Container. You define a Python function and assign its name to the on\_click property of the control.1  
* on\_change: This event is used by input controls whose value can be changed by the user, such as TextField, Checkbox, Dropdown, Slider, and Switch. It fires whenever the control's value is modified.6

#### **The Event Object (**e**)**

The event handler function always receives a single argument, conventionally named e. This object contains information about the event. A particularly useful attribute is e.control, which is a reference to the control instance that fired the event. This allows you to read or modify the properties of the source control within the handler. Other data, such as a link's URL in a Markdown control, can be accessed via e.data.18

Python

def textbox\_changed(e):  
    \# e.control is the TextField that fired the event  
    print(f"TextField value changed to: {e.control.value}")

my\_textfield \= ft.TextField(on\_change=textbox\_changed)

#### **Passing Custom Data to Handlers**

A common requirement in dynamic UIs is to pass extra information to an event handler, such as the ID of an item in a list that was clicked. Since event handlers like on\_click expect a function that takes only one argument (e), a standard Python technique is required. The lambda function provides an elegant solution. It allows you to create a small, anonymous function that captures variables from its surrounding scope and then calls your main handler with the required arguments. This pattern is essential for building interactive lists or grids where each item needs to trigger an action with its specific data.26

Python

def delete\_item(e, item\_id):  
    print(f"Request to delete item with ID: {item\_id}")  
    \#... logic to delete the item...

items\_to\_display \= \["item\_1", "item\_2", "item\_3"\]

for item\_id in items\_to\_display:  
    page.add(  
        ft.Row()  
    )

An alternative approach is to store the necessary information in the control's data property and retrieve it inside the handler via e.control.data.14

## **Part III: Advanced Flet Techniques**

### **Section 7: Creating Reusable Components with Custom Controls**

To build large, scalable, and maintainable applications, it is crucial to break down the UI into smaller, self-contained, and reusable components. Flet fully supports this through object-oriented programming, allowing you to create your own custom controls.22

#### **Styled Controls**

The simplest form of a custom control is a "styled control." This involves creating a new class that inherits from a base Flet control (e.g., ft.ElevatedButton) and then setting default properties in its constructor (\_\_init\_\_). This is an excellent way to create a consistent design system for your application, ensuring all buttons or text fields share the same look and feel.27

Python

class PrimaryButton(ft.ElevatedButton):  
    def \_\_init\_\_(self, text, on\_click):  
        super().\_\_init\_\_()  
        self.text \= text  
        self.on\_click \= on\_click  
        self.bgcolor \= ft.colors.BLUE\_700  
        self.color \= ft.colors.WHITE

\# Usage  
page.add(PrimaryButton(text="Submit", on\_click=submit\_handler))

#### **Composite Controls**

A more powerful technique is to create "composite controls." This is done by inheriting from a layout control like ft.Row or ft.Column (or the more generic ft.UserControl, which is designed for this purpose) and assembling multiple standard controls into a single, cohesive component. The Task class from the official To-Do app tutorial is a perfect example: it encapsulates a Checkbox, Text, and IconButtons to represent a single to-do item, along with all the logic for editing and deleting itself.22

#### **State and Isolation**

When a custom control manages its own internal state (e.g., a Task control toggling between view and edit modes), calling page.update() from within one of its methods would be inefficient, as it could trigger an update of the entire page. Flet provides a more targeted solution to this problem through the concept of "isolation."

An isolated control can update its own UI without triggering a redraw of its parent or siblings. This is achieved by calling self.update() from within the control's methods. For this to work efficiently, the control must be marked as isolated. This can be done in two ways: by inheriting from ft.UserControl (which is isolated by default) or by setting self.is\_isolated \= True in the constructor of a control that inherits from a standard layout control.23 This pattern is a critical performance optimization that arises directly from Flet's imperative update model, allowing developers to manually scope UI updates to specific components.

Python

class CounterControl(ft.UserControl):  
    def build(self):  
        self.counter \= 0  
        self.text \= ft.Text(str(self.counter))  
        return ft.Row()

    def minus\_click(self, e):  
        self.counter \-= 1  
        self.text.value \= str(self.counter)  
        self.update() \# Only updates this CounterControl instance

    def plus\_click(self, e):  
        self.counter \+= 1  
        self.text.value \= str(self.counter)  
        self.update() \# Only updates this CounterControl instance

### **Section 8: State Management Strategies**

#### **The Default Imperative Model**

Flet's default approach to state management is explicit and imperative. The "state" of the application is held in standard Python variables and the properties of your control instances. The developer is fully responsible for mutating this state and then calling page.update() (or self.update() within an isolated control) to synchronize the UI with the new state.6

* **Strengths**: This model is simple to grasp, especially for those with a background in traditional object-oriented or procedural programming. For small to medium-sized applications, its directness is a significant advantage.6  
* **Weaknesses**: As applications grow in complexity, with many interdependent pieces of state, manually tracking every necessary UI update can become cumbersome and error-prone. This can lead to code that is difficult to maintain and debug, a problem that modern declarative frameworks were designed to solve.7

#### **Introduction to Reactive Solutions**

The limitations of the imperative model for large-scale applications have not gone unnoticed by the Flet community. This has led to the development of third-party libraries that introduce more advanced state management patterns. The emergence of libraries like **FletX** and **NeoState** is a clear indicator of a maturing framework ecosystem.29 It demonstrates that the core framework is robust enough to be used for complex projects that push beyond its initial design, prompting the community to build solutions for these advanced use cases.

These libraries, often inspired by solutions from other ecosystems like GetX in the Flutter world, bring concepts like reactive state management, dependency injection, and modular routing to Flet.29 With a reactive approach, UI elements can automatically "listen" to state variables and update themselves whenever the state changes, removing the need for manual

update() calls.

For example, using a library like FletX, state management might look conceptually like this 29:

Python

\# Conceptual example  
self.query \= RxStr("") \# A reactive string variable  
self.results \= RxList() \# A reactive list

\# The UI automatically updates when self.query changes  
\# without an explicit update() call.  
def search(query\_value):  
    \#... fetch results...  
    self.results.value \= new\_results

self.query.listen(search)

This evolution signifies a healthy, growing community that is actively extending Flet's capabilities, providing developers with more options as their application needs evolve.

## **Part IV: A Practical Case Study: Building a To-Do Application**

This section synthesizes the concepts discussed into a complete, practical example by walking through the implementation of the classic To-Do application. This case study closely follows the official Flet tutorial, providing additional commentary to connect the code back to the core principles of the framework.22

### **Section 9: Step-by-Step Implementation of a To-Do App**

#### **Step 1: Application Structure (**TodoApp **Class)**

First, the main application component, TodoApp, is created. It inherits from ft.Column to act as the root container for the app's UI. The layout is defined with a Row at the top for the input TextField and "Add" FloatingActionButton, followed by another Column that will hold the list of tasks.10

#### **Step 2: The Reusable** Task **Component**

The Task class is a composite control that represents a single to-do item. It encapsulates its own layout and logic. It contains two main views: display\_view (a Row with a Checkbox and IconButtons for edit/delete) and edit\_view (a Row with a TextField and a "Save" button). The visible property is used to toggle between these two states, demonstrating internal state management within a component.10

#### **Step 3: Implementing Event Handlers**

Event handlers connect the UI to the application logic.

* In TodoApp, the add\_clicked handler creates a new instance of the Task component and adds it to the list of tasks.  
* In the Task class, handlers like edit\_clicked, save\_clicked, and delete\_clicked manage the component's view state.  
* A key pattern for communication between components is demonstrated here: callback functions (task\_delete, task\_status\_change) are passed from the parent TodoApp into the child Task instances during their creation. When a Task's delete button is clicked, it calls the task\_delete function that was passed to it, telling the parent TodoApp to remove it from the list.10

#### **Step 4: Filtering and State Updates**

To handle task filtering ("all", "active", "completed"), an ft.Tabs control is added to the TodoApp. The logic for filtering is implemented in the before\_update lifecycle method. Before the UI is redrawn, this method iterates through all Task controls and sets their visible property based on the currently selected tab and the task's completed status. This is a perfect example of Flet's imperative state synchronization in action.10

#### **Final Annotated Code**

The following is the complete, annotated source code for the To-Do application, showcasing all the concepts discussed.10

Python

import flet as ft

class Task(ft.UserControl):  
    def \_\_init\_\_(self, task\_name, task\_status\_change, task\_delete):  
        super().\_\_init\_\_()  
        self.completed \= False  
        self.task\_name \= task\_name  
        self.task\_status\_change \= task\_status\_change  
        self.task\_delete \= task\_delete

    def build(self):  
        self.display\_task \= ft.Checkbox(  
            value=False, label=self.task\_name, on\_change=self.status\_changed  
        )  
        self.edit\_name \= ft.TextField(expand=1)

        self.display\_view \= ft.Row(  
            alignment=ft.MainAxisAlignment.SPACE\_BETWEEN,  
            vertical\_alignment=ft.CrossAxisAlignment.CENTER,  
            controls=,  
                ),  
            \],  
        )

        self.edit\_view \= ft.Row(  
            visible=False,  
            alignment=ft.MainAxisAlignment.SPACE\_BETWEEN,  
            vertical\_alignment=ft.CrossAxisAlignment.CENTER,  
            controls=,  
        )  
        return ft.Column(controls=\[self.display\_view, self.edit\_view\])

    def edit\_clicked(self, e):  
        self.edit\_name.value \= self.display\_task.label  
        self.display\_view.visible \= False  
        self.edit\_view.visible \= True  
        self.update()

    def save\_clicked(self, e):  
        self.display\_task.label \= self.edit\_name.value  
        self.display\_view.visible \= True  
        self.edit\_view.visible \= False  
        self.update()

    def status\_changed(self, e):  
        self.completed \= self.display\_task.value  
        self.task\_status\_change(self)

    def delete\_clicked(self, e):  
        self.task\_delete(self)

class TodoApp(ft.UserControl):  
    def build(self):  
        self.new\_task \= ft.TextField(hint\_text="What needs to be done?", expand=True)  
        self.tasks \= ft.Column()

        self.filter \= ft.Tabs(  
            selected\_index=0,  
            on\_change=self.tabs\_changed,  
            tabs=,  
        )

        return ft.Column(  
            width=600,  
            controls=,  
                ),  
                ft.Column(  
                    spacing=25,  
                    controls=\[  
                        self.filter,  
                        self.tasks,  
                    \],  
                ),  
            \],  
        )

    def add\_clicked(self, e):  
        if self.new\_task.value:  
            task \= Task(self.new\_task.value, self.task\_status\_change, self.task\_delete)  
            self.tasks.controls.append(task)  
            self.new\_task.value \= ""  
            self.new\_task.focus()  
            self.update()

    def task\_status\_change(self, task):  
        self.update()

    def task\_delete(self, task):  
        self.tasks.controls.remove(task)  
        self.update()

    def tabs\_changed(self, e):  
        self.update()

    def update(self):  
        status \= self.filter.tabs\[self.filter.selected\_index\].text  
        for task in self.tasks.controls:  
            task.visible \= (  
                status \== "all"  
                or (status \== "active" and not task.completed)  
                or (status \== "completed" and task.completed)  
            )  
        super().update()

def main(page: ft.Page):  
    page.title \= "To-Do App"  
    page.horizontal\_alignment \= ft.CrossAxisAlignment.CENTER  
    page.scroll \= ft.ScrollMode.ADAPTIVE  
    page.update()

    app \= TodoApp()  
    page.add(app)

ft.app(target=main)

## **Conclusion and Further Resources**

Flet presents a compelling value proposition for Python developers: it is a simple, Python-native, "batteries-included" framework that enables the rapid development of multi-platform applications.2 Its defining characteristic is the trade-off it makes, choosing a straightforward, imperative UI model over the more complex declarative patterns found in other modern frameworks. This choice makes Flet exceptionally accessible for developers new to GUI programming and highly productive for a wide range of applications.

Mastery of Flet involves understanding a few key development patterns: the fundamental instantiate \-\> mutate \-\> page.update() workflow, the creation of composite custom controls to build a reusable component library, and the use of isolation (UserControl, self.update()) as a crucial performance optimization technique.

For developers looking to continue their Flet journey, the following resources are invaluable:

* **Official Flet Documentation**: The canonical source for all information on controls, concepts, and deployment.1  
* **Flet Controls Gallery**: An interactive showcase of all available controls with live demos and code samples.15  
* **Official Flet Examples Repository**: A collection of complete sample applications on GitHub, including the To-Do app, a calculator, a chat app, and more.3  
* **Community Channels**: The official Flet Discord server and GitHub Discussions are active communities for getting help, sharing projects, and collaborating with other developers.3
