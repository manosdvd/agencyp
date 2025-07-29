import flet as ft
import logging
import uuid
import json
import os
import zipfile
import shutil
from PIL import Image
from typing import get_args
from dataclasses import asdict

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

# --- Data Management ---
class DataManager:
    """Handles loading, saving, and indexing all project data."""
    def __init__(self, base_path="data"):
        self.base_path = base_path
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
        return self.asset_map.get(asset_type, {}).get("dict", [])

    def load_all(self):
        """Loads all data files from the base path."""
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "images"), exist_ok=True)

        for asset_type, data in self.asset_map.items():
            self._load_json(asset_type, data["class"])

        # Load CaseMeta
        case_meta_path = os.path.join(self.base_path, "case_meta.json")
        if os.path.exists(case_meta_path):
            try:
                with open(case_meta_path, "r") as f:
                    self.case_meta = CaseMeta(**json.load(f))
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Could not load or parse {case_meta_path}: {e}")


    def _load_json(self, asset_type, data_class):
        """Helper to load a single JSON file into its corresponding asset list and dict."""
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
                            asset = data_class(**item_data)
                            asset_list.append(asset)
                            asset_dict[asset.id] = asset
                        except TypeError as te:
                            logger.warning(f"Skipping invalid item in {path} due to TypeError: {te} - Data: {item_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Could not parse {path}: {e}")


    def save_asset(self, asset_type):
        """Saves a specific asset type to its JSON file."""
        path = os.path.join(self.base_path, f"{asset_type}.json")
        asset_list = self.get_asset_list(asset_type)
        try:
            with open(path, "w") as f:
                json.dump([asdict(c) for c in asset_list], f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save {asset_type} to {path}: {e}")
            
    def save_case_meta(self):
        """Saves the CaseMeta data to its JSON file."""
        path = os.path.join(self.base_path, "case_meta.json")
        try:
            with open(path, "w") as f:
                json.dump(asdict(self.case_meta), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save case_meta to {path}: {e}")

    def add_asset(self, asset_type, **kwargs):
        """Adds a new asset to the appropriate list and returns it."""
        if asset_type not in self.asset_map:
            return None
        
        asset_class = self.asset_map[asset_type]["class"]
        new_id = str(uuid.uuid4())
        
        # Ensure 'name' or 'fullName' is present
        if 'name' not in kwargs and 'fullName' not in kwargs:
             kwargs['name'] = "Unnamed"

        new_asset = asset_class(id=new_id, **kwargs)
        
        self.get_asset_list(asset_type).append(new_asset)
        self.get_asset_dict(asset_type)[new_id] = new_asset
        self.save_asset(asset_type)
        return new_asset

    def delete_asset(self, asset_type, asset_id):
        """Deletes an asset from the lists and saves."""
        asset_list = self.get_asset_list(asset_type)
        asset_dict = self.get_asset_dict(asset_type)
        
        asset_to_delete = asset_dict.get(asset_id)
        if asset_to_delete:
            asset_list.remove(asset_to_delete)
            del asset_dict[asset_id]
            self.save_asset(asset_type)
            return True
        return False


def main(page: ft.Page):
    """Main function to build and run the Flet application."""
    page.title = "The Agency"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    
    # --- Holo-Noir Theme ---
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_ACCENT_700,
            primary_container=ft.Colors.BLUE_GREY_800,
            background=ft.Colors.with_opacity(0.95, "#1C2128"),
        ),
        font_family="Inter"
    )

    data_manager = DataManager()
    
    # --- UI Components ---
    list_pane = ft.ListView(expand=True, spacing=5)
    detail_pane = ft.Column([ft.Text("Select an item to see details")], expand=True, scroll=ft.ScrollMode.ADAPTIVE)

    def show_character_details(char: Character):
        # This function will now build and display the detail view
        # It's a large function, but necessary without UserControl
        detail_pane.controls.clear()
        
        def save_character_changes(e):
            # Update the character object from the control values
            char.fullName = name_field.value
            char.biography = bio_field.value
            char.personality = personality_field.value
            char.alignment = alignment_dropdown.value
            char.wealthClass = wealth_dropdown.value
            char.gender = gender_dropdown.value
            char.age = int(age_field.value) if age_field.value.isdigit() else None
            # ... update all other fields ...
            data_manager.save_asset("characters")
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {char.fullName}."), open=True)
            # Also update the name in the list_pane
            for item in list_pane.controls:
                if hasattr(item, 'data') and item.data.id == char.id:
                    item.title.value = char.fullName
                    break
            list_pane.update()
            page.update()

        def delete_character(e):
            data_manager.delete_asset("characters", char.id)
            detail_pane.controls.clear()
            detail_pane.controls.append(ft.Text("Select an item to see details"))
            # Refresh the list pane
            nav_change(ft.ControlEvent(target=nav_rail, name="change", data="0", control=nav_rail, page=page))


        name_field = ft.TextField(label="Full Name", value=char.fullName)
        bio_field = ft.TextField(label="Biography", value=char.biography, multiline=True, min_lines=3)
        personality_field = ft.TextField(label="Personality", value=char.personality, multiline=True, min_lines=3)
        age_field = ft.TextField(label="Age", value=str(char.age) if char.age is not None else "")

        alignment_dropdown = ft.Dropdown(
            label="Alignment",
            value=char.alignment,
            options=[ft.dropdown.Option(align) for align in get_args(Alignment)],
        )
        
        wealth_dropdown = ft.Dropdown(
            label="Wealth Class",
            value=char.wealthClass,
            options=[ft.dropdown.Option(wc) for wc in get_args(WealthClass)],
        )

        gender_dropdown = ft.Dropdown(
            label="Gender",
            value=char.gender,
            options=[ft.dropdown.Option(g) for g in get_args(Gender)],
        )

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_character_changes),
                ft.ElevatedButton("Delete", icon=ft.Icons.DELETE, on_click=delete_character, color=ft.colors.RED)
            ]
        )

        detail_pane.controls.extend([
            ft.Text(f"Editing: {char.fullName}", size=20),
            name_field,
            age_field,
            gender_dropdown,
            alignment_dropdown,
            wealth_dropdown,
            bio_field,
            personality_field,
            button_row
        ])
        detail_pane.update()

    def show_location_details(loc: Location):
        detail_pane.controls.clear()

        def save_location_changes(e):
            loc.name = name_field.value
            loc.description = desc_field.value
            data_manager.save_asset("locations")
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {loc.name}."), open=True)
            for item in list_pane.controls:
                if hasattr(item, 'data') and item.data.id == loc.id:
                    item.title.value = loc.name
                    break
            list_pane.update()
            page.update()

        def delete_location(e):
            data_manager.delete_asset("locations", loc.id)
            detail_pane.controls.clear()
            detail_pane.controls.append(ft.Text("Select an item to see details"))
            nav_change(ft.ControlEvent(target=nav_rail, name="change", data="1", control=nav_rail, page=page))

        name_field = ft.TextField(label="Name", value=loc.name)
        desc_field = ft.TextField(label="Description", value=loc.description, multiline=True, min_lines=3)

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_location_changes),
                ft.ElevatedButton("Delete", icon=ft.Icons.DELETE, on_click=delete_location, color=ft.Colors.RED)
            ]
        )

        detail_pane.controls.extend([
            ft.Text(f"Editing: {loc.name}", size=20),
            name_field,
            desc_field,
            button_row
        ])
        detail_pane.update()

    def show_faction_details(fac: Faction):
        detail_pane.controls.clear()

        def save_faction_changes(e):
            fac.name = name_field.value
            fac.description = desc_field.value
            data_manager.save_asset("factions")
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {fac.name}."), open=True)
            for item in list_pane.controls:
                if hasattr(item, 'data') and item.data.id == fac.id:
                    item.title.value = fac.name
                    break
            list_pane.update()
            page.update()

        def delete_faction(e):
            data_manager.delete_asset("factions", fac.id)
            detail_pane.controls.clear()
            detail_pane.controls.append(ft.Text("Select an item to see details"))
            nav_change(ft.ControlEvent(target=nav_rail, name="change", data="2", control=nav_rail, page=page))

        name_field = ft.TextField(label="Name", value=fac.name)
        desc_field = ft.TextField(label="Description", value=fac.description, multiline=True, min_lines=3)

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_faction_changes),
                ft.ElevatedButton("Delete", icon=ft.Icons.DELETE, on_click=delete_faction, color=ft.Colors.RED)
            ]
        )

        detail_pane.controls.extend([
            ft.Text(f"Editing: {fac.name}", size=20),
            name_field,
            desc_field,
            button_row
        ])
        detail_pane.update()

    def show_district_details(dist: District):
        detail_pane.controls.clear()

        def save_district_changes(e):
            dist.name = name_field.value
            dist.description = desc_field.value
            data_manager.save_asset("districts")
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {dist.name}."), open=True)
            for item in list_pane.controls:
                if hasattr(item, 'data') and item.data.id == dist.id:
                    item.title.value = dist.name
                    break
            list_pane.update()
            page.update()

        def delete_district(e):
            data_manager.delete_asset("districts", dist.id)
            detail_pane.controls.clear()
            detail_pane.controls.append(ft.Text("Select an item to see details"))
            nav_change(ft.ControlEvent(target=nav_rail, name="change", data="3", control=nav_rail, page=page))

        name_field = ft.TextField(label="Name", value=dist.name)
        desc_field = ft.TextField(label="Description", value=dist.description, multiline=True, min_lines=3)

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_district_changes),
                ft.ElevatedButton("Delete", icon=ft.Icons.DELETE, on_click=delete_district, color=ft.Colors.RED)
            ]
        )

        detail_pane.controls.extend([
            ft.Text(f"Editing: {dist.name}", size=20),
            name_field,
            desc_field,
            button_row
        ])
        detail_pane.update()

    def show_item_details(item: Item):
        detail_pane.controls.clear()

        def save_item_changes(e):
            item.name = name_field.value
            item.description = desc_field.value
            data_manager.save_asset("items")
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {item.name}."), open=True)
            for list_item in list_pane.controls:
                if hasattr(list_item, 'data') and list_item.data.id == item.id:
                    list_item.title.value = item.name
                    break
            list_pane.update()
            page.update()

        def delete_item(e):
            data_manager.delete_asset("items", item.id)
            detail_pane.controls.clear()
            detail_pane.controls.append(ft.Text("Select an item to see details"))
            nav_change(ft.ControlEvent(target=nav_rail, name="change", data="4", control=nav_rail, page=page))

        name_field = ft.TextField(label="Name", value=item.name)
        desc_field = ft.TextField(label="Description", value=item.description, multiline=True, min_lines=3)

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton("Save", icon=ft.Icons.SAVE, on_click=save_item_changes),
                ft.ElevatedButton("Delete", icon=ft.Icons.DELETE, on_click=delete_item, color=ft.Colors.RED)
            ]
        )

        detail_pane.controls.extend([
            ft.Text(f"Editing: {item.name}", size=20),
            name_field,
            desc_field,
            button_row
        ])
        detail_pane.update()

    def add_character(e):
        new_char = data_manager.add_asset(
            "characters",
            fullName="New Character",
            biography="",
            personality="",
            alignment="True Neutral",
            honesty=50,
            victimLikelihood=50,
            killerLikelihood=50,
            wealthClass="Working Stiff",
            gender="Unspecified"
        )
        # Refresh the list
        nav_change(ft.ControlEvent(target=nav_rail, name="change", data="0", control=nav_rail, page=page))
        # Select the new character
        show_character_details(new_char)

    def add_location(e):
        new_loc = data_manager.add_asset(
            "locations",
            name="New Location",
            description=""
        )
        nav_change(ft.ControlEvent(target=nav_rail, name="change", data="1", control=nav_rail, page=page))
        show_location_details(new_loc)

    def add_faction(e):
        new_fac = data_manager.add_asset(
            "factions",
            name="New Faction",
            description=""
        )
        nav_change(ft.ControlEvent(target=nav_rail, name="change", data="2", control=nav_rail, page=page))
        show_faction_details(new_fac)

    def add_district(e):
        new_dist = data_manager.add_asset(
            "districts",
            name="New District",
            description=""
        )
        nav_change(ft.ControlEvent(target=nav_rail, name="change", data="3", control=nav_rail, page=page))
        show_district_details(new_dist)

    def add_item(e):
        new_item = data_manager.add_asset(
            "items",
            name="New Item",
            description="",
            possibleMeans=False,
            possibleMotive=False,
            possibleOpportunity=False,
            cluePotential="None",
            value="",
            condition="Good"
        )
        nav_change(ft.ControlEvent(target=nav_rail, name="change", data="4", control=nav_rail, page=page))
        show_item_details(new_item)


    def nav_change(e):
        selected_index = int(e.control.selected_index)
        list_pane.controls.clear()
        detail_pane.controls.clear()
        detail_pane.controls.append(ft.Text("Select an item to see details"))

        # Update Add button functionality
        if selected_index == 0:
            nav_rail.leading.on_click = add_character
        elif selected_index == 1:
            nav_rail.leading.on_click = add_location
        elif selected_index == 2:
            nav_rail.leading.on_click = add_faction
        elif selected_index == 3:
            nav_rail.leading.on_click = add_district
        elif selected_index == 4:
            nav_rail.leading.on_click = add_item
        elif selected_index == 5: # Plot Graph
            nav_rail.leading.on_click = None
        # Add other asset types here
        else:
            nav_rail.leading.on_click = None


        if selected_index == 0: # Characters
            for char in data_manager.get_asset_list("characters"):
                list_pane.controls.append(
                    ft.ListTile(
                        title=ft.Text(char.fullName),
                        on_click=lambda _, char=char: show_character_details(char),
                        data=char
                    )
                )
        elif selected_index == 1: # Locations
            for loc in data_manager.get_asset_list("locations"):
                list_pane.controls.append(
                    ft.ListTile(
                        title=ft.Text(loc.name),
                        on_click=lambda _, loc=loc: show_location_details(loc),
                        data=loc
                    )
                )
        elif selected_index == 2: # Factions
            for fac in data_manager.get_asset_list("factions"):
                list_pane.controls.append(
                    ft.ListTile(
                        title=ft.Text(fac.name),
                        on_click=lambda _, fac=fac: show_faction_details(fac),
                        data=fac
                    )
                )
        elif selected_index == 3: # Districts
            for dist in data_manager.get_asset_list("districts"):
                list_pane.controls.append(
                    ft.ListTile(
                        title=ft.Text(dist.name),
                        on_click=lambda _, dist=dist: show_district_details(dist),
                        data=dist
                    )
                )
        elif selected_index == 4: # Items
            for item in data_manager.get_asset_list("items"):
                list_pane.controls.append(
                    ft.ListTile(
                        title=ft.Text(item.name),
                        on_click=lambda _, item=item: show_item_details(item),
                        data=item
                    )
                )
        elif selected_index == 5: # Plot Graph
            detail_pane.controls.clear()
            
            nodes = []
            for i, char in enumerate(data_manager.get_asset_list("characters")):
                nodes.append(
                    ft.Container(
                        content=ft.Text(char.fullName),
                        top=50 + i * 100,
                        left=50,
                        bgcolor=ft.colors.BLUE_GREY_700,
                        padding=10,
                        border_radius=5
                    )
                )

            plot_canvas = ft.Stack(
                nodes,
                expand=True
            )

            def on_pan_update(e: ft.DragUpdateEvent):
                for control in plot_canvas.controls:
                    if isinstance(control, ft.Container): # Assuming nodes are containers
                        control.top += e.delta_y
                        control.left += e.delta_x
                plot_canvas.update()

            def on_scroll(e: ft.ScrollEvent):
                for control in plot_canvas.controls:
                    if isinstance(control, ft.Container):
                        # A simple scaling effect
                        scale_factor = 1.1 if e.scroll_delta_y < 0 else 0.9
                        control.scale = ft.transform.Scale(scale=control.scale.scale * scale_factor if control.scale else scale_factor)
                plot_canvas.update()

            gesture_detector = ft.GestureDetector(
                content=plot_canvas,
                on_pan_update=on_pan_update,
                on_scroll=on_scroll,
                drag_interval=10,
            )

            detail_pane.controls.append(gesture_detector)
        # Add elif blocks for other asset types (locations, items, etc.)
        
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.FloatingActionButton(icon=ft.Icons.ADD, text="Add", on_click=add_character),
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Characters"),
            ft.NavigationRailDestination(icon=ft.Icons.LOCATION_ON, label="Locations"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Factions"),
            ft.NavigationRailDestination(icon=ft.Icons.MAP, label="Districts"),
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER, label="Items"),
            ft.NavigationRailDestination(icon=ft.Icons.SHARE, label="Plot Graph"),
        ],
        on_change=nav_change,
    )

    # Initial load
    nav_change(ft.ControlEvent(target=nav_rail, name="change", data="0", control=nav_rail, page=page))


    page.add(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column([list_pane]),
                ft.VerticalDivider(width=1),
                detail_pane,
            ],
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)