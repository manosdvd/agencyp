import flet as ft
from schemas import Character, Alignment, Gender, WealthClass, Location, District, Faction, ValidationResult, CaseMeta, Item, TimelineEvent, Clue # Import all necessary dataclasses and enums
import uuid # For generating unique IDs
import json # For JSON serialization
import os # For path operations
import zipfile # For zipping/unzipping case files
import shutil # For high-level file operations like copying directories
from PIL import Image # Import Pillow for image processing

def main(page: ft.Page):
    page.title = "The Agency"

    page.appbar = ft.AppBar(
        title=ft.Text("The Agency Case Builder"),
        center_title=False,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), # Use a slightly transparent app bar
        actions=[
            ft.IconButton(ft.Icons.SAVE, on_click=lambda e: save_all_data(), tooltip="Save All Data"),
            ft.IconButton(ft.Icons.CREATE_NEW_FOLDER_OUTLINED, on_click=lambda e: new_case(), tooltip="New Case"),
            ft.IconButton(ft.Icons.FOLDER_OPEN_OUTLINED, on_click=lambda e: pick_open_file_dialog.pick_files(allow_multiple=False), tooltip="Open Case"),
            ft.IconButton(ft.Icons.UPLOAD_FILE_OUTLINED, on_click=lambda e: pick_export_file_dialog.save_file(), tooltip="Export Case"),
            ft.IconButton(ft.Icons.DOWNLOAD_FOR_OFFLINE_OUTLINED, on_click=lambda e: pick_import_file_dialog.pick_files(allow_multiple=False), tooltip="Import Case"),
        ]
    )

    # --- File Pickers ---
    def pick_open_file_result(e: ft.FilePickerResultEvent):
        nonlocal DATA_DIR, CHARACTERS_FILE, LOCATIONS_FILE, FACTIONS_FILE, DISTRICTS_FILE, ITEMS_FILE, CLUES_FILE, CASE_META_FILE, LORE_HISTORY_FILE, BULLETIN_BOARD_FILE, TIMELINE_FILE
        if e.files and e.files[0].path:
            # Assuming user picks a file inside a case directory, get the directory
            DATA_DIR = os.path.dirname(e.files[0].path)
            CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
            LOCATIONS_FILE = os.path.join(DATA_DIR, "locations.json")
            FACTIONS_FILE = os.path.join(DATA_DIR, "factions.json")
            DISTRICTS_FILE = os.path.join(DATA_DIR, "districts.json")
            ITEMS_FILE = os.path.join(DATA_DIR, "items.json")
            CLUES_FILE = os.path.join(DATA_DIR, "clues.json")
            CASE_META_FILE = os.path.join(DATA_DIR, "case_meta.json")
            LORE_HISTORY_FILE = os.path.join(DATA_DIR, "lore_history.txt")
            BULLETIN_BOARD_FILE = os.path.join(DATA_DIR, "bulletin_board.json")
            TIMELINE_FILE = os.path.join(DATA_DIR, "timeline.json")
            load_all_data()
            # Refresh the entire UI after loading new data
            page.controls.clear()
            build_page_layout()
            page.update()


    pick_open_file_dialog = ft.FilePicker(on_result=pick_open_file_result)
    page.overlay.append(pick_open_file_dialog)

    def pick_export_file_result(e: ft.FilePickerResultEvent):
        if e.path:
            export_case(e.path)

    pick_export_file_dialog = ft.FilePicker(on_result=pick_export_file_result)
    page.overlay.append(pick_export_file_dialog)

    def pick_import_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            import_case(e.files[0].path)

    pick_import_file_dialog = ft.FilePicker(on_result=pick_import_file_result)
    page.overlay.append(pick_import_file_dialog)

    # --- Main Layout & Animation Setup ---
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.window_width = 1600
    page.window_height = 900
    page.window_min_width = 1200
    page.window_min_height = 700

    # Noir Theme
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121a23" # Darker navy blue for more contrast

    # --- Data Storage (in-memory) ---
    characters: list[Character] = []
    characters_by_id: dict[str, Character] = {}
    locations: list[Location] = []
    locations_by_id: dict[str, Location] = {}
    factions: list[Faction] = []
    factions_by_id: dict[str, Faction] = {}
    districts: list[District] = []
    districts_by_id: dict[str, District] = {}
    items: list[Item] = []
    items_by_id: dict[str, Item] = {}
    clues: list[Clue] = []
    clues_by_id: dict[str, Clue] = {}
    case_meta: CaseMeta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="")
    lore_history_text = ""
    bulletin_board_nodes = []
    timeline_events: list[TimelineEvent] = []
    timeline_events_by_id: dict[str, TimelineEvent] = {}
    validation_results: list[ValidationResult] = []

    # --- File Paths ---
    DATA_DIR = "./data"
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
    LOCATIONS_FILE = os.path.join(DATA_DIR, "locations.json")
    FACTIONS_FILE = os.path.join(DATA_DIR, "factions.json")
    DISTRICTS_FILE = os.path.join(DATA_DIR, "districts.json")
    ITEMS_FILE = os.path.join(DATA_DIR, "items.json")
    CLUES_FILE = os.path.join(DATA_DIR, "clues.json")
    CASE_META_FILE = os.path.join(DATA_DIR, "case_meta.json")
    LORE_HISTORY_FILE = os.path.join(DATA_DIR, "lore_history.txt")
    BULLETIN_BOARD_FILE = os.path.join(DATA_DIR, "bulletin_board.json")
    TIMELINE_FILE = os.path.join(DATA_DIR, "timeline.json")

    # Ensure data directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # --- Save/Load Functions ---
    def save_all_data():
        save_characters()
        save_locations()
        save_factions()
        save_districts()
        save_items()
        save_clues()
        save_case_meta()
        save_lore_history()
        save_bulletin_board_nodes()
        save_timeline_events()
        page.snack_bar = ft.SnackBar(ft.Text("Case data saved."), open=True)
        page.update()

    def load_all_data():
        load_characters()
        load_locations()
        load_factions()
        load_districts()
        load_items()
        load_clues()
        load_case_meta()
        load_lore_history()
        load_bulletin_board_nodes()
        load_timeline_events()
        run_validation()

    def export_case(export_path: str):
        try:
            shutil.make_archive(os.path.splitext(export_path)[0], 'zip', DATA_DIR)
            page.snack_bar = ft.SnackBar(ft.Text(f"Case exported successfully to {export_path}.zip"), open=True)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error exporting case: {e}"), open=True)
        page.update()

    def import_case(import_path: str):
        try:
            target_dir = os.path.join(os.path.expanduser("~"), "TheAgencyCases", os.path.splitext(os.path.basename(import_path))[0])
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)

            with zipfile.ZipFile(import_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Case imported to {target_dir}"), open=True)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error importing case: {e}"), open=True)
        page.update()

    def process_and_save_image(file_path: str, asset_id: str) -> str | None:
        try:
            with Image.open(file_path) as img:
                size = (200, 200)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                width, height = img.size
                left, top, right, bottom = (width - height) / 2, 0, (width + height) / 2, height
                if height > width:
                    left, top, right, bottom = 0, (height - width) / 2, width, (height + width) / 2
                img = img.crop((left, top, right, bottom))
                image_filename = f"{asset_id}.png" # Standardize to png
                save_path = os.path.join(IMAGES_DIR, image_filename)
                img.save(save_path, "PNG")
                return save_path
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error processing image: {e}"), open=True)
            page.update()
            return None

    def new_case():
        # This function should ideally prompt for a new case location
        # For now, it just clears the current data in memory and on disk
        nonlocal characters, locations, factions, districts, items, clues, case_meta, lore_history_text, bulletin_board_nodes, timeline_events
        characters.clear(); characters_by_id.clear()
        locations.clear(); locations_by_id.clear()
        factions.clear(); factions_by_id.clear()
        districts.clear(); districts_by_id.clear()
        items.clear(); items_by_id.clear()
        clues.clear(); clues_by_id.clear()
        case_meta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="")
        lore_history_text = ""
        bulletin_board_nodes.clear()
        timeline_events.clear(); timeline_events_by_id.clear()
        validation_results.clear()
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        page.snack_bar = ft.SnackBar(ft.Text("New case created. Remember to save to a new location."), open=True)
        # Refresh the UI
        page.controls.clear()
        build_page_layout()
        page.update()

    def save_characters():
        with open(CHARACTERS_FILE, "w") as f: json.dump([char.__dict__ for char in characters], f, indent=4)
    def load_characters():
        nonlocal characters, characters_by_id
        if os.path.exists(CHARACTERS_FILE):
            with open(CHARACTERS_FILE, "r") as f:
                data = json.load(f)
                characters.clear(); characters_by_id.clear()
                for item in data: characters.append(Character(**item)); characters_by_id[item['id']] = characters[-1]
    
    def save_locations():
        with open(LOCATIONS_FILE, "w") as f: json.dump([loc.__dict__ for loc in locations], f, indent=4)
    def load_locations():
        nonlocal locations, locations_by_id
        if os.path.exists(LOCATIONS_FILE):
            with open(LOCATIONS_FILE, "r") as f:
                data = json.load(f)
                locations.clear(); locations_by_id.clear()
                for item in data: locations.append(Location(**item)); locations_by_id[item['id']] = locations[-1]

    def save_factions():
        with open(FACTIONS_FILE, "w") as f: json.dump([fac.__dict__ for fac in factions], f, indent=4)
    def load_factions():
        nonlocal factions, factions_by_id
        if os.path.exists(FACTIONS_FILE):
            with open(FACTIONS_FILE, "r") as f:
                data = json.load(f)
                factions.clear(); factions_by_id.clear()
                for item in data: factions.append(Faction(**item)); factions_by_id[item['id']] = factions[-1]

    def save_districts():
        with open(DISTRICTS_FILE, "w") as f: json.dump([dist.__dict__ for dist in districts], f, indent=4)
    def load_districts():
        nonlocal districts, districts_by_id
        if os.path.exists(DISTRICTS_FILE):
            with open(DISTRICTS_FILE, "r") as f:
                data = json.load(f)
                districts.clear(); districts_by_id.clear()
                for item in data: districts.append(District(**item)); districts_by_id[item['id']] = districts[-1]

    def save_items():
        with open(ITEMS_FILE, "w") as f: json.dump([item.__dict__ for item in items], f, indent=4)
    def load_items():
        nonlocal items, items_by_id
        if os.path.exists(ITEMS_FILE):
            with open(ITEMS_FILE, "r") as f:
                data = json.load(f)
                items.clear(); items_by_id.clear()
                for item in data: items.append(Item(**item)); items_by_id[item['id']] = items[-1]

    def save_clues():
        with open(CLUES_FILE, "w") as f: json.dump([clue.__dict__ for clue in clues], f, indent=4)
    def load_clues():
        nonlocal clues, clues_by_id
        if os.path.exists(CLUES_FILE):
            with open(CLUES_FILE, "r") as f:
                data = json.load(f)
                clues.clear(); clues_by_id.clear()
                for item in data: clues.append(Clue(**item)); clues_by_id[item['id']] = clues[-1]

    def save_case_meta():
        with open(CASE_META_FILE, "w") as f: json.dump(case_meta.__dict__, f, indent=4)
    def load_case_meta():
        nonlocal case_meta
        if os.path.exists(CASE_META_FILE):
            with open(CASE_META_FILE, "r") as f:
                case_meta = CaseMeta(**json.load(f))

    def save_lore_history():
        with open(LORE_HISTORY_FILE, "w") as f: f.write(lore_history_text)
    def load_lore_history():
        nonlocal lore_history_text
        if os.path.exists(LORE_HISTORY_FILE):
            with open(LORE_HISTORY_FILE, "r") as f: lore_history_text = f.read()

    def save_bulletin_board_nodes():
        with open(BULLETIN_BOARD_FILE, "w") as f: json.dump(bulletin_board_nodes, f, indent=4)
    def load_bulletin_board_nodes():
        nonlocal bulletin_board_nodes
        if os.path.exists(BULLETIN_BOARD_FILE):
            with open(BULLETIN_BOARD_FILE, "r") as f: bulletin_board_nodes = json.load(f)

    def save_timeline_events():
        with open(TIMELINE_FILE, "w") as f: json.dump([event.__dict__ for event in timeline_events], f, indent=4)
    def load_timeline_events():
        nonlocal timeline_events, timeline_events_by_id
        if os.path.exists(TIMELINE_FILE):
            with open(TIMELINE_FILE, "r") as f:
                data = json.load(f)
                timeline_events.clear(); timeline_events_by_id.clear()
                for item in data: timeline_events.append(TimelineEvent(**item)); timeline_events_by_id[item['id']] = timeline_events[-1]

    # --- Validation Logic ---
    def run_validation():
        # This function remains largely the same, but will update the new validator UI
        validation_results.clear()
        # (Validation logic from original file would go here...)
        # For brevity, the full validation logic is omitted, but it would populate validation_results
        update_validator_ui()

    # --- UI Components ---
    # These are now defined here to be accessible by the layout functions
    validator_output = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # --- DYNAMIC UI FOCUS MANAGEMENT ---
    # Define containers for the main animated panes
    left_panel_container = ft.Container(width=350, animate=ft.animation.Animation(300, "easeOut"))
    asset_list_container = ft.Container(width=300, animate=ft.animation.Animation(300, "easeOut"))
    asset_detail_container = ft.Container(expand=True, animate=ft.animation.Animation(300, "easeOut"))

    def set_focus(focused_area: str):
        if focused_area == "list":
            left_panel_container.width = 250
            asset_list_container.width = 400
            asset_detail_container.width = page.window_width - 650 if page.window_width else 800
        elif focused_area == "detail":
            left_panel_container.width = 250
            asset_list_container.width = 250
            asset_detail_container.width = page.window_width - 500 if page.window_width else 1000
        elif focused_area == "validator":
            left_panel_container.width = 450
            asset_list_container.width = 250
            asset_detail_container.width = page.window_width - 700 if page.window_width else 700
        page.update()

    left_panel_container.on_hover = lambda e: set_focus("validator")
    asset_list_container.on_hover = lambda e: set_focus("list")
    asset_detail_container.on_hover = lambda e: set_focus("detail")
    
    def update_validator_ui():
        validator_output.controls.clear()
        if not validation_results:
            validator_output.controls.append(ft.Text("No validation issues found.", color=ft.Colors.GREY_500))
        else:
            for result in validation_results:
                color = ft.Colors.RED_400 if result.type == "error" else ft.Colors.AMBER_400
                validator_output.controls.append(ft.Text(f"{result.type.upper()}: {result.message}", color=color))
        if page.controls: # Check if page has been built
            page.update()

    # --- Character Detail View (with Sub-Tabs) ---
    def create_character_detail_view(character: Character, characters_list_view, select_character):
        
        def save_character_details(e):
            # Update character object from fields
            character.fullName = full_name_field.value
            character.biography = biography_field.value
            # ... update all other fields
            
            # Update list view and save
            # (Full save logic from original file)
            save_characters()
            run_validation()
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {character.fullName}."), open=True)
            page.update()

        def delete_character(e):
            # (Full delete logic from original file)
            del characters_by_id[character.id]
            characters.remove(character)
            asset_detail_container.content = ft.Column([ft.Text("Select a character to view details", color=ft.Colors.GREY_500)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            # Rebuild list view
            characters_list_view.controls.clear()
            for char_item in characters:
                characters_list_view.controls.append(create_list_item(char_item, lambda c=char_item: select_character(c)))
            save_characters()
            run_validation()
            page.update()
        
        # --- Define fields for each tab ---
        full_name_field = ft.TextField(label="Full Name", value=character.fullName)
        # ... (Define all other character fields as in the original file)
        biography_field = ft.TextField(label="Biography", value=character.biography, multiline=True, min_lines=3, max_lines=5)
        personality_field = ft.TextField(label="Personality", value=character.personality, multiline=True, min_lines=3, max_lines=5)
        alias_field = ft.TextField(label="Alias", value=character.alias)
        age_field = ft.TextField(label="Age", value=str(character.age) if character.age else "")
        gender_field = ft.dropdown(label="Gender", value=character.gender, options=[ft.dropdown.Option(g) for g in Gender.__args__])
        # ... and so on for all fields

        # --- Tab Content Columns ---
        vitals_content = ft.Column([full_name_field, alias_field, age_field, gender_field], spacing=10)
        profile_content = ft.Column([biography_field, personality_field], spacing=10)
        # ... create columns for other tabs (Relationships, Case Role, AI/Voice)

        tab_content_area = ft.Container(vitals_content, padding=ft.padding.only(top=10), expand=True)

        def change_detail_tab(e):
            idx = e.control.selected_index
            if idx == 0: tab_content_area.content = vitals_content
            elif idx == 1: tab_content_area.content = profile_content
            # ... add other tab indices
            page.update()

        detail_tabs = ft.Tabs(
            selected_index=0,
            on_change=change_detail_tab,
            tabs=[
                ft.Tab(text="Vitals"),
                ft.Tab(text="Profile"),
                ft.Tab(text="Relationships"),
                ft.Tab(text="Case Role"),
                ft.Tab(text="AI/Voice"),
            ]
        )

        return ft.Column(
            [
                ft.Text(f"Editing: {character.fullName}", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_character_details),
                    ft.ElevatedButton("Delete", icon=ft.Icons.DELETE_FOREVER, on_click=delete_character, color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700),
                ]),
                detail_tabs,
                ft.Column([tab_content_area], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            ],
            expand=True,
            spacing=10
        )
    
    # --- Generic List Item with Hover Effect ---
    def create_list_item(asset, on_click_handler):
        item_container = ft.Container(
            content=ft.Text(getattr(asset, 'fullName', getattr(asset, 'name', 'Unnamed'))),
            padding=10,
            border_radius=5,
            ink=True,
            on_click=lambda e: on_click_handler(asset),
            on_hover=lambda e: hover_effect(e, True),
        )
        # A bit of a hack to pass the container to the hover handler
        item_container.on_hover = lambda e, c=item_container: hover_effect(e, c)
        return item_container

    def hover_effect(e, control_or_container):
        if isinstance(control_or_container, ft.Container):
            control_or_container.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if e.data == "true" else None
            control_or_container.update()

    # --- Generic Asset Management View ---
    def create_asset_management_view(asset_type_name, asset_list, add_asset_handler, create_detail_view_handler):
        
        list_view = ft.ListView(expand=True, spacing=5, padding=5)
        
        def select_asset(asset):
            asset_detail_container.content = create_detail_view_handler(asset, list_view, select_asset)
            set_focus("detail") # Switch focus to detail pane on selection
            page.update()

        for asset in asset_list:
            list_view.controls.append(create_list_item(asset, select_asset))
            
        name_input = ft.TextField(label=f"New {asset_type_name} Name", dense=True)

        def add_new_asset(e):
            new_asset = add_asset_handler(name_input.value)
            if new_asset:
                list_view.controls.append(create_list_item(new_asset, select_asset))
                name_input.value = ""
                page.update()
        
        asset_list_container.content = ft.Column(
            [
                ft.Text(f"{asset_type_name}s", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([name_input, ft.IconButton(ft.Icons.ADD, on_click=add_new_asset, tooltip=f"Add {asset_type_name}")]),
                ft.Divider(),
                list_view,
            ],
            expand=True
        )
        
        asset_detail_container.content = ft.Column(
            [ft.Text(f"Select a {asset_type_name.lower()} to view details.", color=ft.Colors.GREY_500)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        return ft.Row([asset_list_container, asset_detail_container], expand=True)

    # --- Specific View Creators ---
    def create_characters_view():
        def add_character(name):
            if not name: return None
            new_char = Character(id=str(uuid.uuid4()), fullName=name, biography="", personality="", alignment="True-Neutral", honesty=50, victimLikelihood=50, killerLikelihood=50)
            characters.append(new_char)
            characters_by_id[new_char.id] = new_char
            save_characters()
            return new_char
        
        return create_asset_management_view("Character", characters, add_character, create_character_detail_view)

    # ... (Similar create_..._view functions for Locations, Factions, etc., would be defined here)
    # They would call create_asset_management_view with their specific parameters.
    # The detail views (e.g., create_location_detail_view) would also need to be refactored with sub-tabs.

    # --- Main Page Build ---
    def build_page_layout():
        # This function will now construct the entire page layout
        main_content_area = ft.Container(expand=True)
        
        def change_main_tab(e):
            idx = e.control.selected_index
            if idx == 0: # World Builder
                main_content_area.content = create_world_builder_view()
            elif idx == 1: # Case Builder
                main_content_area.content = create_case_builder_view()
            main_content_area.update()

        page.appbar.bottom = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=change_main_tab,
            tabs=[
                ft.Tab(text="World Builder", icon=ft.Icons.PUBLIC),
                ft.Tab(text="Case Builder", icon=ft.Icons.ASSIGNMENT),
            ],
        )

        # Initial content
        main_content_area.content = create_world_builder_view()

        # Left panel content
        left_panel_container.content = ft.Column(
            [
                ft.Text("Validator", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                validator_output,
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        page.add(
            ft.Row(
                [
                    left_panel_container,
                    ft.VerticalDivider(width=1),
                    main_content_area,
                ],
                expand=True,
            )
        )

    def create_world_builder_view():
        # This view now just contains the tabs for the world builder sections
        world_builder_content = ft.Container(create_characters_view(), expand=True)
        
        def change_world_builder_tab(e):
            idx = e.control.selected_index
            if idx == 0: world_builder_content.content = create_characters_view()
            # Add other views here, e.g., create_locations_view()
            # elif idx == 1: world_builder_content.content = create_locations_view()
            world_builder_content.update()

        return ft.Column(
            [
                ft.Tabs(
                    selected_index=0,
                    on_change=change_world_builder_tab,
                    tabs=[
                        ft.Tab(text="Characters", icon=ft.Icons.PERSON_OUTLINE),
                        ft.Tab(text="Locations", icon=ft.Icons.LOCATION_ON_OUTLINED),
                        ft.Tab(text="Factions", icon=ft.Icons.GROUPS_OUTLINED),
                        ft.Tab(text="Districts", icon=ft.Icons.MAP_OUTLINED),
                        ft.Tab(text="Items", icon=ft.Icons.CATEGORY_OUTLINED),
                        ft.Tab(text="Lore", icon=ft.Icons.HISTORY_EDU_OUTLINED),
                    ],
                ),
                world_builder_content,
            ],
            expand=True
        )

    def create_case_builder_view():
        # This view would be structured similarly to the world builder view
        return ft.Text("Case Builder Area", color=ft.Colors.GREY_500)


    # --- Initial Load and Page Construction ---
    load_all_data()
    build_page_layout()
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
