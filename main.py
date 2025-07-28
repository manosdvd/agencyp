import flet as ft
import logging
import uuid
import json
import os
import zipfile
import shutil
from PIL import Image

# --- Schema Imports ---
# Assuming schemas.py is in the same directory and contains all necessary dataclasses
from schemas import (
    Character, Alignment, Gender, WealthClass, Location, District, Faction,
    ValidationResult, CaseMeta, Item, TimelineEvent, Clue
)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'  # Use 'w' to overwrite the log on each run, making it easier to read
)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    """Main function to build and run the Flet application."""
    page.title = "The Agency"

    # --- App Window and Theme Configuration ---
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.window_width = 1600
    page.window_height = 900
    page.window_min_width = 1200
    page.window_min_height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121a23"

    # --- Data Storage (In-Memory) ---
    # Using dictionaries for lists and their corresponding ID-based lookups
    data_stores = {
        "characters": {"list": [], "dict": {}},
        "locations": {"list": [], "dict": {}},
        "factions": {"list": [], "dict": {}},
        "districts": {"list": [], "dict": {}},
        "items": {"list": [], "dict": {}},
        "clues": {"list": [], "dict": {}},
        "timeline_events": {"list": [], "dict": {}},
    }
    case_meta: CaseMeta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="")
    lore_history_text = "" # Added from original main.py
    bulletin_board_nodes = [] # Added from original main.py
    validation_results: list[ValidationResult] = []

    # --- File Path Configuration ---
    DATA_DIR = "./data"
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    
    def get_filepath(name):
        return os.path.join(DATA_DIR, f"{name}.json")

    # --- Generic Save/Load/Add Functions ---
    def save_asset_list(asset_type: str):
        filepath = get_filepath(asset_type)
        with open(filepath, "w") as f:
            json.dump([asset.__dict__ for asset in data_stores[asset_type]["list"]], f, indent=4)

    def load_asset_list(asset_type: str, asset_class):
        asset_list = data_stores[asset_type]["list"]
        asset_dict = data_stores[asset_type]["dict"]
        asset_list.clear()
        asset_dict.clear()
        filepath = get_filepath(asset_type)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    for item_data in data:
                        asset = asset_class(**item_data)
                        asset_list.append(asset)
                        asset_dict[asset.id] = asset
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Could not load or parse {filepath}: {e}")

    def add_new_asset(name: str, asset_type: str, asset_class, **kwargs):
        if not name:
            return None
        new_id = str(uuid.uuid4())
        new_asset = asset_class(id=new_id, name=name, **kwargs)
        if hasattr(new_asset, 'fullName'): # Handle Character schema
            new_asset.fullName = name
        
        data_stores[asset_type]["list"].append(new_asset)
        data_stores[asset_type]["dict"][new_id] = new_asset
        save_asset_list(asset_type)
        return new_asset

    # --- File Picker Dialogs and Handlers ---
    def on_pick_open_file_result(e: ft.FilePickerResultEvent):
        nonlocal DATA_DIR, IMAGES_DIR, lore_history_text, bulletin_board_nodes, case_meta # Added nonlocal for lore_history_text, bulletin_board_nodes, case_meta
        if e.files and e.files[0].path:
            DATA_DIR = os.path.dirname(e.files[0].path)
            IMAGES_DIR = os.path.join(DATA_DIR, "images")
            load_all_data()
            # A full rebuild is necessary after loading a new case
            page.controls.clear()
            build_page_layout()
            page.update()

    def on_export_file_result(e: ft.FilePickerResultEvent):
        if e.path:
            try:
                # Ensure the export path ends with .zip
                export_path_base = os.path.splitext(e.path)[0]
                shutil.make_archive(export_path_base, 'zip', DATA_DIR)
                page.snack_bar = ft.SnackBar(ft.Text(f"Case exported to {export_path_base}.zip"), open=True)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error exporting case: {ex}"), open=True)
            page.update()

    def on_import_file_result(e: ft.FilePickerResultEvent): # Added from original main.py
        if e.files:
            try:
                import_path = e.files[0].path
                target_dir = os.path.join(os.path.expanduser("~"), "TheAgencyCases", os.path.splitext(os.path.basename(import_path))[0])
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                os.makedirs(target_dir, exist_ok=True)

                with zipfile.ZipFile(import_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                
                page.snack_bar = ft.SnackBar(ft.Text(f"Case imported to {target_dir}"), open=True)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error importing case: {ex}"), open=True)
            page.update()

    pick_open_file_dialog = ft.FilePicker(on_result=on_pick_open_file_result)
    pick_export_file_dialog = ft.FilePicker(on_result=on_export_file_result)
    pick_import_file_dialog = ft.FilePicker(on_result=on_import_file_result) # Added from original main.py
    page.overlay.extend([pick_open_file_dialog, pick_export_file_dialog, pick_import_file_dialog]) # Added pick_import_file_dialog

    # --- Top-Level Data Functions ---
    def save_all_data(e=None):
        for asset_type in data_stores:
            save_asset_list(asset_type)
        # Save case_meta, lore_history_text, bulletin_board_nodes (from original main.py)
        with open(os.path.join(DATA_DIR, "case_meta.json"), "w") as f: json.dump(case_meta.__dict__, f, indent=4)
        with open(os.path.join(DATA_DIR, "lore_history.txt"), "w") as f: f.write(lore_history_text)
        with open(os.path.join(DATA_DIR, "bulletin_board.json"), "w") as f: json.dump(bulletin_board_nodes, f, indent=4)
        page.snack_bar = ft.SnackBar(ft.Text("Case data saved."), open=True)
        page.update()

    def load_all_data():
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        load_asset_list("characters", Character)
        load_asset_list("locations", Location)
        load_asset_list("factions", Faction)
        load_asset_list("districts", District) # Added from original main.py
        load_asset_list("items", Item) # Added from original main.py
        load_asset_list("clues", Clue) # Added from original main.py
        load_asset_list("timeline_events", TimelineEvent) # Added from original main.py

        # Load case_meta, lore_history_text, bulletin_board_nodes (from original main.py)
        nonlocal case_meta, lore_history_text, bulletin_board_nodes
        if os.path.exists(os.path.join(DATA_DIR, "case_meta.json")):
            with open(os.path.join(DATA_DIR, "case_meta.json"), "r") as f:
                case_meta = CaseMeta(**json.load(f))
        if os.path.exists(os.path.join(DATA_DIR, "lore_history.txt")):
            with open(os.path.join(DATA_DIR, "lore_history.txt"), "r") as f:
                lore_history_text = f.read()
        if os.path.exists(os.path.join(DATA_DIR, "bulletin_board.json")):
            with open(os.path.join(DATA_DIR, "bulletin_board.json"), "r") as f:
                bulletin_board_nodes = json.load(f)

        run_validation()

    def process_and_save_image(file_path: str, asset_id: str) -> str | None: # Added from original main.py
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
            logger.error(f"Error processing image: {e}")
            return None

    def new_case(): # Added from original main.py
        nonlocal lore_history_text, bulletin_board_nodes, case_meta
        for asset_type in data_stores:
            data_stores[asset_type]["list"].clear()
            data_stores[asset_type]["dict"].clear()
        case_meta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="")
        lore_history_text = ""
        bulletin_board_nodes.clear()
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

    # --- Validation ---
    validator_output = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    def run_validation():
        validation_results.clear()
        # --- Add Validation Logic Here ---
        # Example: Check for characters without a biography
        for char in data_stores["characters"]["list"]:
            if not char.biography:
                validation_results.append(ValidationResult(
                    message=f"Character '{char.fullName}' has no biography.",
                    type="warning",
                    asset_id=char.id,
                    asset_type="Character"
                ))
        update_validator_ui()

    def update_validator_ui():
        validator_output.controls.clear()
        if not validation_results:
            validator_output.controls.append(ft.Text("No validation issues found.", color="grey500"))
        else:
            for result in validation_results:
                color="red400" if result.type == "error" else "amber400"
                validator_output.controls.append(ft.Text(f"{result.type.upper()}: {result.message}", color=color))
        if page.controls:
            validator_output.update()

    # --- UI Component Creators ---
    def create_list_item(asset, on_click_handler):
        # A generic list item with a hover effect
        item_text = getattr(asset, 'fullName', getattr(asset, 'name', 'Unnamed'))
        
        def on_hover(e):
            e.control.bgcolor = "rgba(255, 255, 255, 0.05)" if e.data == "true" else None
            e.control.update()

        return ft.Container(
            content=ft.Text(item_text),
            padding=10,
            border_radius=5,
            ink=True,
            on_click=lambda e: on_click_handler(asset),
            on_hover=on_hover,
        )

    # --- Character Detail View ---
    def create_character_detail_view(character: Character, list_view_ref, on_select_handler, detail_container_ref):
        
        def save_character_details(e):
            character.fullName = full_name_field.value
            character.alias = alias_field.value
            character.age = int(age_field.value) if age_field.value.isdigit() else None
            character.gender = gender_field.value
            character.biography = biography_field.value
            character.personality = personality_field.value
            character.alignment = alignment_field.value
            character.wealthClass = wealth_class_field.value
            character.faction = faction_field.value
            character.district = district_field.value
            character.employment = employment_field.value
            character.honesty = int(honesty_slider.value)
            character.victimLikelihood = int(victim_likelihood_slider.value)
            character.killerLikelihood = int(killer_likelihood_slider.value)
            character.motivations = motivations_field.value.split('\n')
            character.secrets = secrets_field.value.split("\n")
            character.allies = [s.strip() for s in allies_field.value.split(',') if s.strip()]
            character.enemies = [s.strip() for s in enemies_field.value.split(',') if s.strip()]
            character.flawsHandicapsLimitations = flaws_field.value.split('\n')
            character.quirks = quirks_field.value.split("\n")
            character.characteristics = characteristics_field.value.split("\n")
            character.vulnerabilities = vulnerabilities_field.value.split('\n')
            character.expertise = expertise_field.value.split('\n')
            character.portrayalNotes = portrayal_notes_field.value
            character.voiceModel = voice_model_field.value
            character.dialogueStyle = dialogue_style_field.value
            save_asset_list("characters")
            run_validation()
            # Update the list view item text
            for item in list_view_ref.controls:
                if item.on_click.__closure__[0].cell_contents.id == character.id:
                    item.content.value = character.fullName
                    break
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {character.fullName}."), open=True)
            page.update()

        def delete_character(e):
            data_stores["characters"]["list"].remove(character)
            del data_stores["characters"]["dict"][character.id]
            save_asset_list("characters")
            
            # Clear the detail view
            detail_container_ref.content = ft.Column([ft.Text("Select a character to view details.", color="grey500")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            # Rebuild the list view
            list_view_ref.controls.clear()
            for char_item in data_stores["characters"]["list"]:
                list_view_ref.controls.append(create_list_item(char_item, on_select_handler))
            
            run_validation()
            page.update()

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path = process_and_save_image(e.files[0].path, character.id)
                if image_path:
                    character.image = image_path
                    character_image.src = image_path
                    save_asset_list("characters")
                    page.update()

        pick_image_dialog = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(pick_image_dialog)

        # --- Define all the fields for the character form ---
        
        # Vitals Tab
        full_name_field = ft.TextField(label="Full Name", value=character.fullName, expand=True, tooltip="The character's complete, official name.")
        alias_field = ft.TextField(label="Alias", value=character.alias, expand=True, tooltip="Any other names the character goes by.")
        age_field = ft.TextField(label="Age", value=str(character.age) if character.age else "", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"), width=150, tooltip="The character's age in years.")
        gender_field = ft.Dropdown(label="Gender", value=character.gender, options=[ft.dropdown.Option(g) for g in Gender.__args__], expand=True, tooltip="The character's gender identity.")
        character_image = ft.Image(src=character.image if character.image else "", width=150, height=150, fit=ft.ImageFit.COVER, border_radius=ft.border_radius.all(5))
        upload_button = ft.ElevatedButton("Upload Image", icon="upload", on_click=lambda _: pick_image_dialog.pick_files(), tooltip="Upload a portrait for the character.")

        vitals_content = ft.Row(
            [
                ft.Column(
                    [character_image, upload_button], 
                    spacing=10, 
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Column(
                    [
                        ft.Row([full_name_field, alias_field], spacing=10),
                        ft.Row([age_field, gender_field], spacing=10),
                    ], 
                    spacing=10, 
                    expand=True
                )
            ], 
            spacing=20, 
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # Profile Tab
        biography_field = ft.TextField(label="Biography", value=character.biography, multiline=True, min_lines=5, max_lines=10, tooltip="A detailed history of the character's life and background.")
        personality_field = ft.TextField(label="Personality", value=character.personality, multiline=True, min_lines=3, max_lines=5, tooltip="A summary of the character's key personality traits.")
        alignment_field = ft.Dropdown(label="Alignment", value=character.alignment, options=[ft.dropdown.Option(a) for a in Alignment.__args__], expand=True, tooltip="The character's moral and ethical alignment (e.g., Lawful Good, Chaotic Evil).")
        wealth_class_field = ft.Dropdown(label="Wealth Class", value=character.wealthClass, options=[ft.dropdown.Option(w) for w in WealthClass.__args__], expand=True, tooltip="The character's socioeconomic status.")
        faction_field = ft.Dropdown(label="Faction", value=character.faction, options=[ft.dropdown.Option(f.id, f.name) for f in data_stores["factions"]["list"]], expand=True, tooltip="The faction this character belongs to, if any.")
        district_field = ft.Dropdown(label="Home District", value=character.district, options=[ft.dropdown.Option(d.id, d.name) for d in data_stores["districts"]["list"]], expand=True, tooltip="The district where the character primarily resides.")
        employment_field = ft.TextField(label="Employment", value=character.employment, tooltip="The character's current job or profession.")

        profile_content = ft.Column(
            [
                biography_field,
                personality_field,
                ft.Row([alignment_field, wealth_class_field], spacing=10),
                ft.Row([faction_field, district_field], spacing=10),
                employment_field
            ], 
            spacing=10
        )

        # Traits Tab
        motivations_field = ft.TextField(label="Motivations", value="\n".join(character.motivations), multiline=True, min_lines=4, expand=True, tooltip="What drives this character? (One per line)")
        secrets_field = ft.TextField(label="Secrets", value='\n'.join(character.secrets), multiline=True, min_lines=4, expand=True, tooltip="What is this character hiding? (One per line)")
        flaws_field = ft.TextField(label="Flaws/Handicaps", value='\n'.join(character.flawsHandicapsLimitations), multiline=True, min_lines=4, expand=True, tooltip="What are their weaknesses or limitations? (One per line)")
        quirks_field = ft.TextField(label="Quirks", value='\n'.join(character.quirks), multiline=True, min_lines=4, expand=True, tooltip="Unique habits or eccentricities. (One per line)")
        characteristics_field = ft.TextField(label="Characteristics", value='\n'.join(character.characteristics), multiline=True, min_lines=4, expand=True, tooltip="Defining physical or behavioral traits. (One per line)")
        vulnerabilities_field = ft.TextField(label="Vulnerabilities", value='\n'.join(character.vulnerabilities), multiline=True, min_lines=4, expand=True, tooltip="What can be exploited by others? (One per line)")
        expertise_field = ft.TextField(label="Expertise", value='\n'.join(character.expertise), multiline=True, min_lines=4, expand=True, tooltip="Areas of special skill or knowledge. (One per line)")

        traits_content = ft.Column(
            [
                ft.Row([motivations_field, secrets_field], spacing=10),
                ft.Row([flaws_field, quirks_field], spacing=10),
                ft.Row([characteristics_field, vulnerabilities_field], spacing=10),
                ft.Row([expertise_field], spacing=10),
            ], 
            spacing=10, 
            scroll=ft.ScrollMode.ADAPTIVE
        )

        # Relationships Tab
        allies_field = ft.TextField(label="Allies", value=", ".join(character.allies), multiline=True, min_lines=3, tooltip="Enter Character IDs, separated by commas.")
        enemies_field = ft.TextField(label="Enemies", value=", ".join(character.enemies), multiline=True, min_lines=3, tooltip="Enter Character IDs, separated by commas.")
        
        relationships_content = ft.Column(
            [
                ft.Text("Define relationships by adding other characters' unique IDs."),
                allies_field,
                enemies_field
            ], 
            spacing=10
        )

        # Case Role Tab
        honesty_slider = ft.Slider(min=0, max=100, divisions=100, value=character.honesty, expand=True, label="Honesty: {value}")
        victim_likelihood_slider = ft.Slider(min=0, max=100, divisions=100, value=character.victimLikelihood, expand=True, label="Victim Likelihood: {value}")
        killer_likelihood_slider = ft.Slider(min=0, max=100, divisions=100, value=character.killerLikelihood, expand=True, label="Killer Likelihood: {value}")
        items_list = ft.ListView(tooltip="Items this character possesses.")

        case_role_content = ft.Column(
            [
                ft.Row(
                    [ft.Text("Honesty:", width=150), honesty_slider], 
                    spacing=10, 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [ft.Text("Victim Likelihood:", width=150), victim_likelihood_slider], 
                    spacing=10, 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [ft.Text("Killer Likelihood:", width=150), killer_likelihood_slider], 
                    spacing=10, 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Text("Items (Coming Soon)"),
                ft.Container(
                    items_list, 
                    border=ft.border.all(1, "grey700"), 
                    border_radius=ft.border_radius.all(5), 
                    padding=5, 
                    expand=True
                )
            ], 
            spacing=15
        )

        # AI/Voice Tab
        portrayal_notes_field = ft.TextField(label="Portrayal Notes", value=character.portrayalNotes, multiline=True, min_lines=4, tooltip="Notes for voice actors or AI on how to portray this character.")
        voice_model_field = ft.TextField(label="Voice Model", value=character.voiceModel, tooltip="Identifier for a specific AI voice model to be used.")
        dialogue_style_field = ft.TextField(label="Dialogue Style", value=character.dialogueStyle, multiline=True, min_lines=3, tooltip="A description of the character's speaking patterns, vocabulary, and tone.")

        ai_voice_content = ft.Column(
            [
                portrayal_notes_field, 
                voice_model_field, 
                dialogue_style_field
            ], 
            spacing=10
        )

        tab_content_area = ft.Container(vitals_content, padding=ft.padding.only(top=10), expand=True)

        def change_detail_tab(e):
            idx = e.control.selected_index
            tabs = [vitals_content, profile_content, traits_content, relationships_content, case_role_content, ai_voice_content]
            tab_content_area.content = tabs[idx]
            page.update()

        detail_tabs = ft.Tabs(
            selected_index=0,
            on_change=change_detail_tab,
            tabs=[
                ft.Tab(text="Vitals"),
                ft.Tab(text="Profile"),
                ft.Tab(text="Traits"),
                ft.Tab(text="Relationships"),
                ft.Tab(text="Case Role"),
                ft.Tab(text="AI/Voice"),
            ]
        )

        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text(f"Editing: {character.fullName}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton("Save", icon="save", on_click=save_character_details),
                            ft.ElevatedButton("Delete", icon="delete_forever", on_click=delete_character, color="white", bgcolor="red700"),
                        ])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                detail_tabs,
                ft.Container(tab_content_area, expand=True, padding=ft.padding.all(10))
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE
        )

    # --- Generic Asset Management View ---
    def create_asset_management_view(asset_type_name, asset_type_key, asset_class, detail_view_creator, **kwargs):
        
        detail_container = ft.Container(
            content=ft.Column(
                [ft.Text(f"Select a {asset_type_name.lower()} to view details.", color="grey500")],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            expand=True,
            padding=ft.padding.all(20)
        )
        
        list_view = ft.ListView(expand=True, spacing=5, padding=5)

        def on_select_asset(asset):
            detail_container.content = detail_view_creator(asset, list_view, on_select_asset, detail_container)
            detail_container.update()

        for asset in data_stores[asset_type_key]["list"]:
            list_view.controls.append(create_list_item(asset, on_select_asset))
            
        name_input = ft.TextField(label=f"New {asset_type_name} Name", dense=True, expand=True)

        def on_add_new_asset(e):
            if not name_input.value:
                name_input.error_text = "Name cannot be empty"
                name_input.update()
                return
            
            new_asset = add_new_asset(name_input.value, asset_type_key, asset_class, **kwargs)
            if new_asset:
                list_view.controls.append(create_list_item(new_asset, on_select_asset))
                name_input.value = ""
                name_input.error_text = None
                list_view.update()
                name_input.update()
        
        list_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"{asset_type_name}s", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [name_input, ft.IconButton("add", on_click=on_add_new_asset, tooltip=f"Add {asset_type_name}")],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(),
                    list_view,
                ],
                expand=True
            ),
            width=350,
            padding=ft.padding.all(10),
            border=ft.border.only(right=ft.BorderSide(1, "white10"))
        )
        
        return ft.Row([list_container, detail_container], expand=True)

    # --- Specific View Creators that use the generic manager ---
    def create_characters_view():
        return create_asset_management_view(
            "Character", 
            "characters", 
            Character, 
            create_character_detail_view,
            biography="", 
            personality="", 
            alignment="True Neutral", # Corrected from "True-Neutral"
            honesty=50, 
            victimLikelihood=50, 
            killerLikelihood=50
        )
    
    def create_location_detail_view(location: Location, locations_list_view, select_location, detail_container_ref): # Added from original main.py

        def save_location_details(e):
            location.name = name_field.value
            location.description = description_field.value
            location.type = type_field.value
            location.district = district_field.value
            location.owningFaction = faction_field.value
            location.dangerLevel = int(danger_level_slider.value)
            location.population = int(population_field.value) if population_field.value else None
            location.accessibility = accessibility_field.value
            location.hidden = hidden_switch.value
            location.internalLogicNotes = internal_logic_notes_field.value
            save_asset_list("locations") # Updated save call
            run_validation()
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {location.name}."), open=True)
            page.update()

        def delete_location(e):
            data_stores["locations"]["list"].remove(location) # Updated delete call
            del data_stores["locations"]["dict"][location.id] # Updated delete call
            detail_container_ref.content = ft.Column([ft.Text("Select a location to view details", color="grey500")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            locations_list_view.controls.clear()
            for loc_item in data_stores["locations"]["list"]:
                locations_list_view.controls.append(create_list_item(loc_item, select_location))
            save_asset_list("locations") # Updated save call
            run_validation()
            page.update()

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path = process_and_save_image(e.files[0].path, location.id)
                if image_path:
                    location.image = image_path
                    location_image.src = image_path
                    save_asset_list("locations") # Updated save call
                    page.update()

        pick_image_dialog = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(pick_image_dialog)

        # (All the field definitions below this are correct and don't need to change)
        name_field = ft.TextField(label="Location Name", value=location.name)
        description_field = ft.TextField(label="Description", value=location.description, multiline=True, min_lines=3)
        type_field = ft.TextField(label="Type (e.g., Speakeasy, Warehouse)", value=location.type)
        district_field = ft.Dropdown(label="District", value=location.district, options=[ft.dropdown.Option(d.id, d.name) for d in data_stores["districts"]["list"]]) # Updated district reference
        faction_field = ft.Dropdown(label="Owning Faction", value=location.owningFaction, options=[ft.dropdown.Option(f.id, f.name) for f in data_stores["factions"]["list"]]) # Updated faction reference
        danger_level_slider = ft.Slider(min=1, max=5, divisions=4, label="Danger Level: {value}", value=location.dangerLevel or 1)
        population_field = ft.TextField(label="Population", value=str(location.population) if location.population else "", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"))
        accessibility_field = ft.Dropdown(label="Accessibility", value=location.accessibility, options=[ft.dropdown.Option(a) for a in ["Public", "Semi-Private", "Private", "Restricted"]])
        hidden_switch = ft.Switch(label="Hidden", value=location.hidden)
        internal_logic_notes_field = ft.TextField(label="Internal Logic Notes", value=location.internalLogicNotes, multiline=True, min_lines=4)
        location_image = ft.Image(src=location.image if location.image else "", width=150, height=150, fit=ft.ImageFit.COVER, border_radius=ft.border_radius.all(5))
        upload_button = ft.ElevatedButton("Upload Image", icon="upload", on_click=lambda _: pick_image_dialog.pick_files())

        details_content = ft.Column([
            name_field,
            description_field,
            type_field,
            ft.Row([district_field, faction_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            danger_level_slider,
            ft.Row([population_field, accessibility_field, hidden_switch]),
            ft.Row([location_image, upload_button], alignment=ft.MainAxisAlignment.START, spacing=20)
        ], spacing=10)

        associations_content = ft.Column([
                ft.Text("Key Characters (Coming Soon)"),
                ft.Text("Associated Items (Coming Soon)"),
                ft.Text("Clues (Coming Soon)"),
        ], spacing=10)
        
        notes_content = ft.Column([internal_logic_notes_field], spacing=10)

        tab_content_area = ft.Container(details_content, padding=ft.padding.only(top=10), expand=True)

        def change_detail_tab(e):
            idx = e.control.selected_index
            tabs = [details_content, associations_content, notes_content]
            tab_content_area.content = tabs[idx]
            page.update()

        detail_tabs = ft.Tabs(
            selected_index=0,
            on_change=change_detail_tab,
            tabs=[
                ft.Tab(text="Details"),
                ft.Tab(text="Associations"),
                ft.Tab(text="Notes"),
            ]
        )

        return ft.Column(
            [
                ft.Row([
                    ft.Text(f"Editing: {location.name}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Save", icon="save", on_click=save_location_details),
                        ft.ElevatedButton("Delete", icon="delete_forever", on_click=delete_location, color="white", bgcolor="red700"),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                detail_tabs,
                ft.Container(tab_content_area, expand=True, padding=ft.padding.all(10))
            ],
            expand=True,
            spacing=10
        )

    def create_locations_view():
        return create_asset_management_view("Location", "locations", Location, create_location_detail_view, description="")

    def create_faction_detail_view(faction: Faction, factions_list_view, select_faction, detail_container_ref):

        def save_faction_details(e):
            faction.name = name_field.value
            faction.description = description_field.value
            faction.archetype = archetype_field.value
            faction.ideology = ideology_field.value
            faction.headquarters = headquarters_field.value
            faction.influence = influence_field.value
            faction.publicPerception = public_perception_field.value
            save_asset_list("factions")
            run_validation()
            # Update the list view item text
            for item in factions_list_view.controls:
                if item.on_click.__closure__[0].cell_contents.id == faction.id:
                    item.content.value = faction.name
                    break
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {faction.name}."), open=True)
            page.update()

        def delete_faction(e):
            data_stores["factions"]["list"].remove(faction)
            del data_stores["factions"]["dict"][faction.id]
            save_asset_list("factions")
            detail_container_ref.content = ft.Column([ft.Text("Select a faction to view details", color="grey500")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            factions_list_view.controls.clear()
            for fac_item in data_stores["factions"]["list"]:
                factions_list_view.controls.append(create_list_item(fac_item, select_faction))
            run_validation()
            page.update()

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path = process_and_save_image(e.files[0].path, faction.id)
                if image_path:
                    faction.image = image_path
                    faction_image.src = image_path
                    save_asset_list("factions")
                    page.update()

        pick_image_dialog = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(pick_image_dialog)

        # --- Define fields ---
        name_field = ft.TextField(label="Faction Name", value=faction.name)
        description_field = ft.TextField(label="Description", value=faction.description, multiline=True, min_lines=3)
        archetype_field = ft.TextField(label="Archetype (e.g., Criminal Syndicate, Political Movement)", value=faction.archetype)
        ideology_field = ft.TextField(label="Ideology", value=faction.ideology)
        headquarters_field = ft.Dropdown(label="Headquarters", value=faction.headquarters, options=[ft.dropdown.Option(l.id, l.name) for l in data_stores["locations"]["list"]])
        influence_field = ft.Dropdown(label="Influence", value=faction.influence, options=[ft.dropdown.Option(i) for i in ["Local", "District-wide", "City-wide", "Regional", "Global"]])
        public_perception_field = ft.TextField(label="Public Perception", value=faction.publicPerception)
        faction_image = ft.Image(src=faction.image if faction.image else "", width=150, height=150, fit=ft.ImageFit.COVER, border_radius=ft.border_radius.all(5))
        upload_button = ft.ElevatedButton("Upload Image", icon="upload", on_click=lambda _: pick_image_dialog.pick_files())

        details_content = ft.Column([
            name_field,
            description_field,
            archetype_field,
            ideology_field,
            headquarters_field,
            influence_field,
            public_perception_field,
            ft.Row([faction_image, upload_button], alignment=ft.MainAxisAlignment.START, spacing=20)
        ], spacing=10)

        relationships_content = ft.Column([
            ft.Text("Ally Factions (Coming Soon)"),
            ft.Text("Enemy Factions (Coming Soon)"),
        ], spacing=10)

        members_content = ft.Column([
            ft.Text("Members (Coming Soon)"),
        ], spacing=10)

        tab_content_area = ft.Container(details_content, padding=ft.padding.only(top=10), expand=True)

        def change_detail_tab(e):
            idx = e.control.selected_index
            tabs = [details_content, relationships_content, members_content]
            tab_content_area.content = tabs[idx]
            page.update()

        detail_tabs = ft.Tabs(
            selected_index=0,
            on_change=change_detail_tab,
            tabs=[
                ft.Tab(text="Details"),
                ft.Tab(text="Relationships"),
                ft.Tab(text="Members"),
            ]
        )

        return ft.Column(
            [
                ft.Row([
                    ft.Text(f"Editing: {faction.name}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Save", icon="save", on_click=save_faction_details),
                        ft.ElevatedButton("Delete", icon="delete_forever", on_click=delete_faction, color="white", bgcolor="red700"),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                detail_tabs,
                ft.Container(tab_content_area, expand=True, padding=ft.padding.all(10))
            ],
            expand=True,
            spacing=10
        )

    def create_factions_view():
        return create_asset_management_view("Faction", "factions", Faction, create_faction_detail_view, description="")

    def create_district_detail_view(district: District, districts_list_view, select_district, detail_container_ref): # Added from original main.py

        def save_district_details(e):
            district.name = name_field.value
            district.description = description_field.value
            district.wealthClass = wealth_class_field.value
            district.atmosphere = atmosphere_field.value
            district.populationDensity = population_density_field.value
            district.dominantFaction = dominant_faction_field.value
            district.notableFeatures = [s.strip() for s in notable_features_field.value.split('\n') if s.strip()]
            district.keyLocations = [s.strip() for s in key_locations_field.value.split('\n') if s.strip()]
            save_asset_list("districts") # Updated save call
            run_validation()
            # Update the list view item text
            for item in districts_list_view.controls:
                if item.on_click.__closure__[0].cell_contents.id == district.id:
                    item.content.value = district.name
                    break
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {district.name}."), open=True)
            page.update()

        def delete_district(e):
            data_stores["districts"]["list"].remove(district) # Updated delete call
            del data_stores["districts"]["dict"][district.id] # Updated delete call
            save_asset_list("districts") # Updated save call
            detail_container_ref.content = ft.Column([ft.Text("Select a district to view details", color="grey500")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            districts_list_view.controls.clear()
            for dist_item in data_stores["districts"]["list"]:
                districts_list_view.controls.append(create_list_item(dist_item, select_district))
            run_validation()
            page.update()

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path = process_and_save_image(e.files[0].path, district.id)
                if image_path:
                    district.image = image_path
                    district_image.src = image_path
                    save_asset_list("districts") # Updated save call
                    page.update()

        pick_image_dialog = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(pick_image_dialog)

        # --- Define fields ---
        name_field = ft.TextField(label="District Name", value=district.name, tooltip="The name of the district.")
        description_field = ft.TextField(label="Description", value=district.description, multiline=True, min_lines=3, tooltip="A general description of the district.")
        wealth_class_field = ft.Dropdown(label="Dominant Wealth Class", value=district.wealthClass, options=[ft.dropdown.Option(w) for w in WealthClass.__args__], expand=True, tooltip="The predominant wealth class in this district.")
        atmosphere_field = ft.TextField(label="Atmosphere", value=district.atmosphere, tooltip="Describe the general mood or ambiance of the district.")
        population_density_field = ft.Dropdown(label="Population Density", value=district.populationDensity, options=[ft.dropdown.Option(p) for p in ["Sparse", "Moderate", "Dense", "Crowded"]], expand=True, tooltip="How densely populated is this district?")
        dominant_faction_field = ft.Dropdown(label="Dominant Faction", value=district.dominantFaction, options=[ft.dropdown.Option(f.id, f.name) for f in data_stores["factions"]["list"]], expand=True, tooltip="The faction that holds the most influence in this district.") # Updated faction reference
        notable_features_field = ft.TextField(label="Notable Features (one per line)", value='\n'.join(district.notableFeatures), multiline=True, min_lines=3, tooltip="Key landmarks or characteristics of the district.")
        key_locations_field = ft.TextField(label="Key Locations (one per line)", value='\n'.join(district.keyLocations), multiline=True, min_lines=3, tooltip="IDs of important locations within this district.")
        district_image = ft.Image(src=district.image if district.image else "", width=150, height=150, fit=ft.ImageFit.COVER, border_radius=ft.border_radius.all(5))
        upload_button = ft.ElevatedButton("Upload Image", icon="upload", on_click=lambda _: pick_image_dialog.pick_files(), tooltip="Upload an image representing the district.")

        # --- Tab Content ---
        details_content = ft.Column([
            name_field,
            description_field,
            ft.Row([wealth_class_field, population_density_field], spacing=10),
            atmosphere_field,
            dominant_faction_field,
            ft.Row([district_image, upload_button], alignment=ft.MainAxisAlignment.START, spacing=20)
        ], spacing=10)

        features_content = ft.Column([
            notable_features_field,
            key_locations_field,
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)

        tab_content_area = ft.Container(details_content, padding=ft.padding.only(top=10), expand=True)

        def change_detail_tab(e):
            idx = e.control.selected_index
            tabs = [details_content, features_content]
            tab_content_area.content = tabs[idx]
            page.update()

        detail_tabs = ft.Tabs(
            selected_index=0,
            on_change=change_detail_tab,
            tabs=[
                ft.Tab(text="Details"),
                ft.Tab(text="Features"),
            ]
        )

        return ft.Column(
            [
                ft.Row([
                    ft.Text(f"Editing: {district.name}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Save", icon="save", on_click=save_district_details),
                        ft.ElevatedButton("Delete", icon="delete_forever", on_click=delete_district, color="white", bgcolor="red700"),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                detail_tabs,
                ft.Container(tab_content_area, expand=True, padding=ft.padding.all(10))
            ],
            expand=True,
            spacing=10
        )

    def create_districts_view(): # Added from original main.py
        return create_asset_management_view("District", "districts", District, create_district_detail_view, description="")

    def create_items_view():
        # Placeholder detail view for items
        def create_item_detail_view(item: Item, list_ref, select_handler, detail_ref):
            
            def save_item_details(e):
                item.name = name_field.value
                item.description = description_field.value
                item.type = type_field.value
                item.defaultLocation = location_field.value
                item.defaultOwner = owner_field.value
                item.cluePotential = clue_potential_field.value
                item.value = value_field.value
                item.condition = condition_field.value
                item.possibleMeans = possible_means_switch.value
                item.possibleMotive = possible_motive_switch.value
                item.possibleOpportunity = possible_opportunity_switch.value
                item.significance = significance_field.value
                item.use = use_field.value.split('\n')
                item.uniqueProperties = unique_properties_field.value.split('\n')
                save_asset_list("items")
                run_validation()
                for i in list_ref.controls:
                    if i.on_click.__closure__[0].cell_contents.id == item.id:
                        i.content.value = item.name
                        break
                page.snack_bar = ft.SnackBar(ft.Text(f"Saved {item.name}."), open=True)
                page.update()

            def delete_item(e):
                data_stores["items"]["list"].remove(item)
                del data_stores["items"]["dict"][item.id]
                save_asset_list("items")
                detail_ref.content = ft.Column([ft.Text("Select an item to view details", color="grey500")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                list_ref.controls.clear()
                for item_item in data_stores["items"]["list"]:
                    list_ref.controls.append(create_list_item(item_item, select_handler))
                run_validation()
                page.update()

            def pick_image_result(e: ft.FilePickerResultEvent):
                if e.files:
                    image_path = process_and_save_image(e.files[0].path, item.id)
                    if image_path:
                        item.image = image_path
                        item_image.src = image_path
                        save_asset_list("items")
                        page.update()

            pick_image_dialog = ft.FilePicker(on_result=pick_image_result)
            page.overlay.append(pick_image_dialog)

            # --- Define fields ---
            name_field = ft.TextField(label="Item Name", value=item.name)
            description_field = ft.TextField(label="Description", value=item.description, multiline=True, min_lines=3)
            type_field = ft.TextField(label="Type (e.g., Weapon, Document)", value=item.type)
            location_field = ft.Dropdown(label="Default Location", value=item.defaultLocation, options=[ft.dropdown.Option(l.id, l.name) for l in data_stores["locations"]["list"]])
            owner_field = ft.Dropdown(label="Default Owner", value=item.defaultOwner, options=[ft.dropdown.Option(c.id, c.fullName) for c in data_stores["characters"]["list"]])
            clue_potential_field = ft.Dropdown(label="Clue Potential", value=item.cluePotential, options=[ft.dropdown.Option(c) for c in ["None", "Low", "Medium", "High", "Critical"]])
            value_field = ft.TextField(label="Value", value=item.value)
            condition_field = ft.Dropdown(label="Condition", value=item.condition, options=[ft.dropdown.Option(c) for c in ["New", "Good", "Used", "Worn", "Damaged", "Broken"]])
            possible_means_switch = ft.Switch(label="Possible Means", value=item.possibleMeans)
            possible_motive_switch = ft.Switch(label="Possible Motive", value=item.possibleMotive)
            possible_opportunity_switch = ft.Switch(label="Possible Opportunity", value=item.possibleOpportunity)
            significance_field = ft.TextField(label="Significance", value=item.significance, multiline=True, min_lines=2)
            use_field = ft.TextField(label="Use (one per line)", value='\n'.join(item.use), multiline=True, min_lines=3)
            unique_properties_field = ft.TextField(label="Unique Properties (one per line)", value='\n'.join(item.uniqueProperties), multiline=True, min_lines=3)
            item_image = ft.Image(src=item.image if item.image else "", width=150, height=150, fit=ft.ImageFit.COVER, border_radius=ft.border_radius.all(5))
            upload_button = ft.ElevatedButton("Upload Image", icon="upload", on_click=lambda _: pick_image_dialog.pick_files())

            details_content = ft.Column([
                name_field,
                description_field,
                type_field,
                ft.Row([location_field, owner_field]),
                ft.Row([clue_potential_field, value_field, condition_field]),
                ft.Row([possible_means_switch, possible_motive_switch, possible_opportunity_switch]),
                significance_field,
                use_field,
                unique_properties_field,
                ft.Row([item_image, upload_button], alignment=ft.MainAxisAlignment.START, spacing=20)
            ], spacing=10)

            return ft.Column(
                [
                    ft.Row([
                        ft.Text(f"Editing: {item.name}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton("Save", icon="save", on_click=save_item_details),
                            ft.ElevatedButton("Delete", icon="delete_forever", on_click=delete_item, color="white", bgcolor="red700"),
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    details_content
                ],
                expand=True,
                spacing=10,
                scroll=ft.ScrollMode.ADAPTIVE
            )
        return create_asset_management_view("Item", "items", Item, create_item_detail_view, description="")

    def create_lore_view():
        def save_lore_history_text(e):
            nonlocal lore_history_text
            lore_history_text = lore_text_field.value
            save_all_data()
            page.snack_bar = ft.SnackBar(ft.Text("Lore history saved."), open=True)
            page.update()

        lore_text_field = ft.TextField(
            label="Lore & World History",
            value=lore_history_text,
            multiline=True,
            min_lines=20,
            expand=True,
            tooltip="Document the overarching lore and historical events of your game world."
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Lore & World History", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton("Save Lore", icon="save", on_click=save_lore_history_text),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                lore_text_field,
            ],
            expand=True,
            spacing=10
        )

    # --- Main Page Layout Builder ---
    def build_page_layout():
        main_content_area = ft.Container(content=create_world_builder_view(), expand=True)
        
        def on_change_main_tab(e):
            idx = e.control.selected_index
            if idx == 0:
                main_content_area.content = create_world_builder_view()
            elif idx == 1:
                main_content_area.content = create_case_builder_view() # Updated to call actual function
            main_content_area.update()

        page.appbar = ft.AppBar(
            title=ft.Text("The Agency Case Builder"),
            center_title=False,
            bgcolor="rgba(255, 255, 255, 0.05)",
            actions=[
                ft.IconButton("save", on_click=save_all_data, tooltip="Save All Data"),
                ft.IconButton("create_new_folder_outlined", on_click=lambda e: new_case(), tooltip="New Case"),
                ft.IconButton("folder_open_outlined", on_click=lambda e: pick_open_file_dialog.pick_files(allow_multiple=False), tooltip="Open Case Folder"),
                ft.IconButton("upload_file_outlined", on_click=lambda e: pick_export_file_dialog.save_file(file_name="case.zip"), tooltip="Export Case as .zip"),
                ft.IconButton("download_for_offline_outlined", on_click=lambda e: pick_import_file_dialog.pick_files(allow_multiple=False), tooltip="Import Case"),
            ]
        )

        main_tabs = ft.Tabs(
            selected_index=0,
            on_change=on_change_main_tab,
            tabs=[
                ft.Tab(text="World Builder", icon="public"),
                ft.Tab(text="Case Builder", icon="assignment"),
            ],
        )

        validator_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Validator", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    validator_output,
                ],
                expand=True,
                spacing=10,
            ),
            width=350,
            padding=ft.padding.all(10),
            border=ft.border.only(right=ft.BorderSide(1, "white10"))
        )
        
        page.add(
            ft.Column(
                [
                    page.appbar,
                    ft.Row(
                        [
                            validator_panel,
                            main_content_area,
                        ],
                        expand=True,
                    ),
                    main_tabs,
                ],
                expand=True,
            )
        )

    def create_world_builder_view():
        world_builder_content = ft.Container(create_characters_view(), expand=True)
        
        def on_change_world_builder_tab(e):
            idx = e.control.selected_index
            tabs = {
                0: create_characters_view,
                1: create_locations_view,
                2: create_factions_view,
                3: create_districts_view, # Added from original main.py
                4: create_items_view, # Added from original main.py
                5: create_lore_view, # Added from original main.py
            }
            # Get the function from the dictionary and call it
            view_function = tabs.get(idx, lambda: ft.Text(f"Tab {idx+1} not implemented"))
            world_builder_content.content = view_function()
            world_builder_content.update()

        return ft.Column(
            [
                ft.Tabs(
                    selected_index=0,
                    on_change=on_change_world_builder_tab,
                    tabs=[
                        ft.Tab(text="Characters", icon="person_outline"),
                        ft.Tab(text="Locations", icon="location_on_outlined"),
                        ft.Tab(text="Factions", icon="groups_outlined"),
                        ft.Tab(text="Districts", icon="map_outlined"),
                        ft.Tab(text="Items", icon="category_outlined"),
                        ft.Tab(text="Lore", icon="history_edu_outlined"), # Added from original main.py
                    ],
                ),
                world_builder_content,
            ],
            expand=True,
        )

    def create_case_builder_view(): # Added from original main.py
        # This view would be structured similarly to the world builder view
        return ft.Text("Case Builder Area", color="grey500")


    # --- Initial Load and Page Construction ---
    load_all_data()
    build_page_layout()
    page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")