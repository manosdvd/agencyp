import flet as ft
from schemas import Character, Alignment, Gender, WealthClass, Location, District, Faction # Import all necessary dataclasses and enums
import uuid # For generating unique IDs

def main(page: ft.Page):
    page.title = "The Agency"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600

    # Noir Theme
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1A2B3C"  # Dark navy blue

    # --- Data Storage (in-memory for now) ---
    characters: list[Character] = []
    locations: list[Location] = []
    factions: list[Faction] = []
    lore_history_text = ""
    bulletin_board_text = ""
    timeline_text = ""

    # --- Character Detail View ---
    def create_character_detail_view(character: Character):
        # Create TextField controls for each editable field
        full_name_field = ft.TextField(label="Full Name", value=character.fullName, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        biography_field = ft.TextField(label="Biography", value=character.biography, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        personality_field = ft.TextField(label="Personality", value=character.personality, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        alignment_field = ft.Dropdown(
            label="Alignment",
            value=character.alignment,
            options=[ft.dropdown.Option(align) for align in Alignment.__args__],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        honesty_field = ft.TextField(label="Honesty", value=str(character.honesty), keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        victim_likelihood_field = ft.TextField(label="Victim Likelihood", value=str(character.victimLikelihood), keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        killer_likelihood_field = ft.TextField(label="Killer Likelihood", value=str(character.killerLikelihood), keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        gender_field = ft.Dropdown(
            label="Gender",
            value=character.gender,
            options=[ft.dropdown.Option(g) for g in Gender.__args__],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        wealth_class_field = ft.Dropdown(
            label="Wealth Class",
            value=character.wealthClass,
            options=[ft.dropdown.Option(wc) for wc in WealthClass.__args__],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )

        def save_character_details(e):
            character.fullName = full_name_field.value
            character.biography = biography_field.value
            character.personality = personality_field.value
            character.alignment = alignment_field.value
            character.honesty = int(honesty_field.value)
            character.victimLikelihood = int(victim_likelihood_field.value)
            character.killerLikelihood = int(killer_likelihood_field.value)
            character.gender = gender_field.value if gender_field.value else None
            character.wealthClass = wealth_class_field.value if wealth_class_field.value else None

            # Update the character list view to reflect name changes
            characters_list_view.controls.clear()
            for char in characters:
                characters_list_view.controls.append(ft.Text(char.fullName, color="#FFFFFF", on_click=select_character))
            page.update()

        def delete_character(e):
            characters.remove(character)
            characters_list_view.controls.clear()
            for char in characters:
                characters_list_view.controls.append(ft.Text(char.fullName, color="#FFFFFF", on_click=select_character))
            character_detail_container.content = ft.Column([ft.Text("Select a character to view details", color="#9E9E9E")])
            page.update()

        return ft.Column(
            [
                ft.Text(f"Character Details: {character.fullName}", color="#FFFFFF", size=20),
                full_name_field,
                biography_field,
                personality_field,
                alignment_field,
                honesty_field,
                victim_likelihood_field,
                killer_likelihood_field,
                gender_field,
                wealth_class_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_character_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Character",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_character
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Location Detail View ---
    def create_location_detail_view(location: Location):
        # Create TextField controls for each editable field
        name_field = ft.TextField(label="Name", value=location.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=location.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        type_field = ft.TextField(label="Type", value=location.type, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        district_field = ft.TextField(label="District", value=location.district, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        owning_faction_field = ft.TextField(label="Owning Faction", value=location.owningFaction, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        danger_level_field = ft.TextField(label="Danger Level", value=str(location.dangerLevel), keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        population_field = ft.TextField(label="Population", value=str(location.population), keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        accessibility_field = ft.Dropdown(
            label="Accessibility",
            value=location.accessibility,
            options=[ft.dropdown.Option("Public"), ft.dropdown.Option("Semi-Private"), ft.dropdown.Option("Private"), ft.dropdown.Option("Restricted")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        hidden_field = ft.Checkbox(label="Hidden", value=location.hidden, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        internal_logic_notes_field = ft.TextField(label="Internal Logic Notes", value=location.internalLogicNotes, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_location_details(e):
            location.name = name_field.value
            location.description = description_field.value
            location.type = type_field.value
            location.district = district_field.value
            location.owningFaction = owning_faction_field.value
            location.dangerLevel = int(danger_level_field.value) if danger_level_field.value else None
            location.population = int(population_field.value) if population_field.value else None
            location.accessibility = accessibility_field.value
            location.hidden = hidden_field.value
            location.internalLogicNotes = internal_logic_notes_field.value

            # Update the location list view to reflect name changes
            locations_list_view.controls.clear()
            for loc in locations:
                locations_list_view.controls.append(ft.Text(loc.name, color="#FFFFFF", on_click=select_location))
            page.update()

        def delete_location(e):
            locations.remove(location)
            locations_list_view.controls.clear()
            for loc in locations:
                locations_list_view.controls.append(ft.Text(loc.name, color="#FFFFFF", on_click=select_location))
            location_detail_container.content = ft.Column([ft.Text("Select a location to view details", color="#9E9E9E")])
            page.update()

        return ft.Column(
            [
                ft.Text(f"Location Details: {location.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                type_field,
                district_field,
                owning_faction_field,
                danger_level_field,
                population_field,
                accessibility_field,
                hidden_field,
                internal_logic_notes_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_location_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Location",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_location
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Faction Detail View ---
    def create_faction_detail_view(faction: Faction):
        # Create TextField controls for each editable field
        name_field = ft.TextField(label="Name", value=faction.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=faction.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        archetype_field = ft.TextField(label="Archetype", value=faction.archetype, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        ideology_field = ft.TextField(label="Ideology", value=faction.ideology, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        headquarters_field = ft.TextField(label="Headquarters", value=faction.headquarters, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        public_perception_field = ft.TextField(label="Public Perception", value=faction.publicPerception, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_faction_details(e):
            faction.name = name_field.value
            faction.description = description_field.value
            faction.archetype = archetype_field.value
            faction.ideology = ideology_field.value
            faction.headquarters = headquarters_field.value
            faction.publicPerception = public_perception_field.value

            # Update the faction list view to reflect name changes
            factions_list_view.controls.clear()
            for fac in factions:
                factions_list_view.controls.append(ft.Text(fac.name, color="#FFFFFF", on_click=select_faction))
            page.update()

        def delete_faction(e):
            factions.remove(faction)
            factions_list_view.controls.clear()
            for fac in factions:
                factions_list_view.controls.append(ft.Text(fac.name, color="#FFFFFF", on_click=select_faction))
            faction_detail_container.content = ft.Column([ft.Text("Select a faction to view details", color="#9E9E9E")])
            page.update()

        return ft.Column(
            [
                ft.Text(f"Faction Details: {faction.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                archetype_field,
                ideology_field,
                headquarters_field,
                public_perception_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_faction_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Faction",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_faction
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Content Views ---
    def create_characters_view():
        character_name_input = ft.TextField(
            label="Character Name",
            hint_text="Enter character's full name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        characters_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        character_detail_container = ft.Container(
            content=ft.Column([ft.Text("Select a character to view details", color="#9E9E9E")]), # Placeholder
            expand=True,
            padding=20
        )

        def select_character(e):
            selected_char_name = e.control.text
            selected_character = next((char for char in characters if char.fullName == selected_char_name), None)
            if selected_character:
                character_detail_container.content = create_character_detail_view(selected_character)
                page.update()

        def add_character(e):
            if character_name_input.value:
                # Create a new Character object with a unique ID and placeholder values
                new_character = Character(
                    id=str(uuid.uuid4()),
                    fullName=character_name_input.value,
                    biography="", # Placeholder
                    personality="", # Placeholder
                    alignment=Alignment.__args__[0], # Use first value from Literal as default
                    honesty=50, # Placeholder
                    victimLikelihood=50, # Placeholder
                    killerLikelihood=50, # Placeholder
                    gender=Gender.__args__[0], # Use first value from Literal as default
                    wealthClass=WealthClass.__args__[0] # Use first value from Literal as default
                )
                characters.append(new_character)
                characters_list_view.controls.append(ft.Text(new_character.fullName, color="#FFFFFF", on_click=select_character))
                character_name_input.value = ""
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Characters Management", color="#FFFFFF", size=20),
                    ft.Text("List of characters and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            character_name_input,
                            ft.ElevatedButton(
                                text="Add Character",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_character
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=characters_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            character_detail_container,
                        ],
                        expand=True
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    def create_locations_view():
        location_name_input = ft.TextField(
            label="Location Name",
            hint_text="Enter location name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        locations_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        location_detail_container = ft.Container(
            content=ft.Column([ft.Text("Select a location to view details", color="#9E9E9E")]), # Placeholder
            expand=True,
            padding=20
        )

        def select_location(e):
            selected_loc_name = e.control.text
            selected_location = next((loc for loc in locations if loc.name == selected_loc_name), None)
            if selected_location:
                location_detail_container.content = create_location_detail_view(selected_location)
                page.update()

        def add_location(e):
            if location_name_input.value:
                new_location = Location(
                    id=str(uuid.uuid4()),
                    name=location_name_input.value,
                    description="", # Placeholder
                    type="", # Placeholder
                    district="", # Placeholder
                    owningFaction="", # Placeholder
                    dangerLevel=1, # Placeholder
                    population=0, # Placeholder
                    accessibility="Public", # Placeholder
                    hidden=False, # Placeholder
                    internalLogicNotes="", # Placeholder
                )
                locations.append(new_location)
                locations_list_view.controls.append(ft.Text(new_location.name, color="#FFFFFF", on_click=select_location))
                location_name_input.value = ""
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Locations Management", color="#FFFFFF", size=20),
                    ft.Text("List of locations and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            location_name_input,
                            ft.ElevatedButton(
                                text="Add Location",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_location
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=locations_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            location_detail_container,
                        ],
                        expand=True
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    def create_factions_view():
        faction_name_input = ft.TextField(
            label="Faction Name",
            hint_text="Enter faction name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        factions_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        faction_detail_container = ft.Container(
            content=ft.Column([ft.Text("Select a faction to view details", color="#9E9E9E")]), # Placeholder
            expand=True,
            padding=20
        )

        def select_faction(e):
            selected_fac_name = e.control.text
            selected_faction = next((fac for fac in factions if fac.name == selected_fac_name), None)
            if selected_faction:
                faction_detail_container.content = create_faction_detail_view(selected_faction)
                page.update()

        def add_faction(e):
            if faction_name_input.value:
                new_faction = Faction(
                    id=str(uuid.uuid4()),
                    name=faction_name_input.value,
                    description="", # Placeholder
                    archetype="", # Placeholder
                    ideology="", # Placeholder
                    headquarters="", # Placeholder
                    publicPerception="", # Placeholder
                )
                factions.append(new_faction)
                factions_list_view.controls.append(ft.Text(new_faction.name, color="#FFFFFF", on_click=select_faction))
                faction_name_input.value = ""
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Factions Management", color="#FFFFFF", size=20),
                    ft.Text("List of factions and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            faction_name_input,
                            ft.ElevatedButton(
                                text="Add Faction",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_faction
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=factions_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            faction_detail_container,
                        ],
                        expand=True
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    def create_lore_history_view():
        lore_history_text_field = ft.TextField(
            label="Lore and World History",
            hint_text="Enter historical events, world lore, and background information here.",
            multiline=True,
            min_lines=10,
            max_lines=20,
            value=lore_history_text,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
            expand=True
        )

        def save_lore_history(e):
            nonlocal lore_history_text
            lore_history_text = lore_history_text_field.value
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Lore & World History", color="#FFFFFF", size=20),
                    ft.Text("Timeline of events and world lore will go here.", color="#9E9E9E"),
                    lore_history_text_field,
                    ft.ElevatedButton(
                        text="Save Lore & History",
                        icon=ft.Icons.SAVE,
                        bgcolor="#64B5F6",
                        color="#FFFFFF",
                        on_click=save_lore_history
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    def create_bulletin_board_view():
        bulletin_board_text_field = ft.TextField(
            label="Interactive Bulletin Board",
            hint_text="Describe the plot graph and node editor here.",
            multiline=True,
            min_lines=10,
            max_lines=20,
            value=bulletin_board_text,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
            expand=True
        )

        def save_bulletin_board(e):
            nonlocal bulletin_board_text
            bulletin_board_text = bulletin_board_text_field.value
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Interactive Bulletin Board", color="#FFFFFF", size=20),
                    ft.Text("The plot graph and node editor will go here.", color="#9E9E9E"),
                    bulletin_board_text_field,
                    ft.ElevatedButton(
                        text="Save Bulletin Board",
                        icon=ft.Icons.SAVE,
                        bgcolor="#64B5F6",
                        color="#FFFFFF",
                        on_click=save_bulletin_board
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    def create_timeline_view():
        timeline_text_field = ft.TextField(
            label="Gamified Timeline Editor",
            hint_text="Describe the event chain editor here.",
            multiline=True,
            min_lines=10,
            max_lines=20,
            value=timeline_text,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
            expand=True
        )

        def save_timeline(e):
            nonlocal timeline_text
            timeline_text = timeline_text_field.value
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gamified Timeline Editor", color="#FFFFFF", size=20),
                    ft.Text("The event chain editor will go here.", color="#9E9E9E"),
                    timeline_text_field,
                    ft.ElevatedButton(
                        text="Save Timeline",
                        icon=ft.Icons.SAVE,
                        bgcolor="#64B5F6",
                        color="#FFFFFF",
                        on_click=save_timeline
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    # --- Main Content Area ---
    main_content_area = ft.Column([create_characters_view()], expand=True)

    # --- Secondary Navigation ---
    secondary_nav_column = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.PERSON, tooltip="Characters", on_click=lambda e: update_main_content(create_characters_view())),
            ft.IconButton(icon=ft.Icons.LOCATION_ON, tooltip="Locations", on_click=lambda e: update_main_content(create_locations_view())),
            ft.IconButton(icon=ft.Icons.GROUPS, tooltip="Factions", on_click=lambda e: update_main_content(create_factions_view())),
            ft.IconButton(icon=ft.Icons.HISTORY, tooltip="Lore & History", on_click=lambda e: update_main_content(create_lore_history_view())),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
    )

    secondary_nav_container = ft.Container(
        content=secondary_nav_column,
        width=70,
        height=page.height, # This will be dynamic
        bgcolor="#2C3E50",
        padding=ft.padding.symmetric(vertical=10),
        alignment=ft.alignment.top_center,
    )

    def update_main_content(new_content):
        main_content_area.controls.clear()
        main_content_area.controls.append(new_content)
        page.update()

    def on_navigation_change(e):
        if e.control.selected_index == 0:  # World Builder
            secondary_nav_column.controls.clear()
            secondary_nav_column.controls.extend([
                ft.IconButton(icon=ft.Icons.PERSON, tooltip="Characters", on_click=lambda e: update_main_content(create_characters_view())),
                ft.IconButton(icon=ft.Icons.LOCATION_ON, tooltip="Locations", on_click=lambda e: update_main_content(create_locations_view())),
                ft.IconButton(icon=ft.Icons.GROUPS, tooltip="Factions", on_click=lambda e: update_main_content(create_factions_view())),
                ft.IconButton(icon=ft.Icons.HISTORY, tooltip="Lore & History", on_click=lambda e: update_main_content(create_lore_history_view())),
            ])
            update_main_content(create_characters_view()) # Default to Characters view
        elif e.control.selected_index == 1:  # Case Builder
            secondary_nav_column.controls.clear()
            secondary_nav_column.controls.extend([
                ft.IconButton(icon=ft.Icons.DASHBOARD, tooltip="Bulletin Board", on_click=lambda e: update_main_content(create_bulletin_board_view())),
                ft.IconButton(icon=ft.Icons.ACCESS_TIME, tooltip="Timeline", on_click=lambda e: update_main_content(create_timeline_view())),
            ])
            update_main_content(create_bulletin_board_view()) # Default to Bulletin Board view
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor="#2C3E50",  # Slightly lighter navy for nav bar
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="World Builder"),
            ft.NavigationBarDestination(icon=ft.Icons.CASES, label="Case Builder"),
        ],
        on_change=on_navigation_change,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("The Agency", color="#FFFFFF"),
        center_title=False,
        bgcolor="#2C3E50",
        actions=[
            ft.TextField(
                hint_text="Global Search...",
                width=300,
                content_padding=ft.padding.only(left=10, right=10),
                border_radius=5,
                filled=True,
                fill_color="#3A4D60",
                text_style=ft.TextStyle(color="#FFFFFF"),
                hint_style=ft.TextStyle(color="#9E9E9E"), # Grey 500 equivalent
                border_color="#00000000", # Transparent
            ),
            ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#FFFFFF"),
        ]
    )

    page.add(
        ft.Row(
            [
                secondary_nav_container,
                main_content_area,
            ],
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
