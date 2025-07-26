import flet as ft
from schemas import Character, Alignment, Gender, WealthClass, Location, District, Faction, ValidationResult, CaseMeta, Item, TimelineEvent, Clue # Import all necessary dataclasses and enums
import uuid # For generating unique IDs
import json # For JSON serialization
import os # For path operations

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
    districts: list[District] = []
    items: list[Item] = []
    clues: list[Clue] = [] # Added clues list
    case_meta: CaseMeta = CaseMeta(victim="", culprit="", crimeScene="", murderWeapon="", coreMysterySolutionDetails="") # Initialize CaseMeta
    lore_history_text = ""
    bulletin_board_nodes = [] # Changed to store node data
    timeline_events: list[TimelineEvent] = [] # Changed to store TimelineEvent objects
    validation_results: list[ValidationResult] = []

    # --- File Paths ---
    DATA_DIR = "./data"
    CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
    LOCATIONS_FILE = os.path.join(DATA_DIR, "locations.json")
    FACTIONS_FILE = os.path.join(DATA_DIR, "factions.json")
    DISTRICTS_FILE = os.path.join(DATA_DIR, "districts.json")
    ITEMS_FILE = os.path.join(DATA_DIR, "items.json")
    CLUES_FILE = os.path.join(DATA_DIR, "clues.json") # Added clues file path
    CASE_META_FILE = os.path.join(DATA_DIR, "case_meta.json") # Added case meta file path
    LORE_HISTORY_FILE = os.path.join(DATA_DIR, "lore_history.txt")
    BULLETIN_BOARD_FILE = os.path.join(DATA_DIR, "bulletin_board.json") # Changed to JSON
    TIMELINE_FILE = os.path.join(DATA_DIR, "timeline.json") # Changed to JSON

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Save/Load Functions ---
    def save_characters():
        with open(CHARACTERS_FILE, "w") as f:
            json.dump([char.__dict__ for char in characters], f, indent=4)

    def load_characters():
        if os.path.exists(CHARACTERS_FILE):
            with open(CHARACTERS_FILE, "r") as f:
                data = json.load(f)
                characters.clear()
                for item in data:
                    # Convert dictionary back to Character object
                    # Handle optional fields that might be None in JSON
                    characters.append(Character(
                        id=item['id'],
                        fullName=item['fullName'],
                        biography=item['biography'],
                        personality=item['personality'],
                        alignment=item['alignment'],
                        honesty=item['honesty'],
                        victimLikelihood=item['victimLikelihood'],
                        killerLikelihood=item['killerLikelihood'],
                        alias=item.get('alias'),
                        age=item.get('age'),
                        gender=item.get('gender'),
                        employment=item.get('employment'),
                        image=item.get('image'),
                        faction=item.get('faction'),
                        wealthClass=item.get('wealthClass'),
                        district=item.get('district'),
                        motivations=item.get('motivations', []), # Default to empty list
                        secrets=item.get('secrets', []), # Default to empty list
                        allies=item.get('allies', []), # Default to empty list
                        enemies=item.get('enemies', []), # Default to empty list
                        items=item.get('items', []), # Default to empty list
                        archetype=item.get('archetype'),
                        values=item.get('values', []), # Default to empty list
                        flawsHandicapsLimitations=item.get('flawsHandicapsLimitations', []), # Default to empty list
                        quirks=item.get('quirks', []), # Default to empty list
                        characteristics=item.get('characteristics', []), # Default to empty list
                        vulnerabilities=item.get('vulnerabilities', []), # Default to empty list
                        voiceModel=item.get('voiceModel'),
                        dialogueStyle=item.get('dialogueStyle'),
                        expertise=item.get('expertise', []), # Default to empty list
                        portrayalNotes=item.get('portrayalNotes')
                    ))

    def save_locations():
        with open(LOCATIONS_FILE, "w") as f:
            json.dump([loc.__dict__ for loc in locations], f, indent=4)

    def load_locations():
        if os.path.exists(LOCATIONS_FILE):
            with open(LOCATIONS_FILE, "r") as f:
                data = json.load(f)
                locations.clear()
                for item in data:
                    locations.append(Location(
                        id=item['id'],
                        name=item['name'],
                        description=item['description'],
                        type=item.get('type'),
                        district=item.get('district'),
                        owningFaction=item.get('owningFaction'),
                        dangerLevel=item.get('dangerLevel'),
                        population=item.get('population'),
                        image=item.get('image'),
                        keyCharacters=item.get('keyCharacters', []), # Default to empty list
                        associatedItems=item.get('associatedItems', []), # Default to empty list
                        accessibility=item.get('accessibility'),
                        hidden=item.get('hidden'),
                        internalLogicNotes=item.get('internalLogicNotes'),
                        clues=item.get('clues', []) # Default to empty list
                    ))

    def save_factions():
        with open(FACTIONS_FILE, "w") as f:
            json.dump([fac.__dict__ for fac in factions], f, indent=4)

    def load_factions():
        if os.path.exists(FACTIONS_FILE):
            with open(FACTIONS_FILE, "r") as f:
                data = json.load(f)
                factions.clear()
                for item in data:
                    factions.append(Faction(
                        id=item['id'],
                        name=item['name'],
                        description=item['description'],
                        archetype=item.get('archetype'),
                        ideology=item.get('ideology'),
                        headquarters=item.get('headquarters'),
                        resources=item.get('resources', []), # Default to empty list
                        image=item.get('image'),
                        allyFactions=item.get('allyFactions', []), # Default to empty list
                        enemyFactions=item.get('enemies', []), # Default to empty list
                        members=item.get('members', []), # Default to empty list
                        influence=item.get('influence'),
                        publicPerception=item.get('publicPerception')
                    ))

    def save_districts():
        with open(DISTRICTS_FILE, "w") as f:
            json.dump([dist.__dict__ for dist in districts], f, indent=4)

    def load_districts():
        if os.path.exists(DISTRICTS_FILE):
            with open(DISTRICTS_FILE, "r") as f:
                data = json.load(f)
                districts.clear()
                for item in data:
                    districts.append(District(
                        id=item['id'],
                        name=item['name'],
                        description=item['description'],
                        image=item.get('image'),
                        wealthClass=item.get('wealthClass'),
                        atmosphere=item.get('atmosphere'),
                        populationDensity=item.get('populationDensity'),
                        notableFeatures=item.get('notableFeatures', []), # Default to empty list
                        dominantFaction=item.get('dominantFaction'),
                        keyLocations=item.get('keyLocations', []) # Default to empty list
                    ))

    def save_items(): # Added save_items function
        with open(ITEMS_FILE, "w") as f:
            json.dump([item.__dict__ for item in items], f, indent=4)

    def load_items(): # Added load_items function
        if os.path.exists(ITEMS_FILE):
            with open(ITEMS_FILE, "r") as f:
                data = json.load(f)
                items.clear()
                for item_data in data:
                    items.append(Item(
                        id=item_data['id'],
                        name=item_data['name'],
                        description=item_data['description'],
                        possibleMeans=item_data['possibleMeans'],
                        possibleMotive=item_data['possibleMotive'],
                        possibleOpportunity=item_data['possibleOpportunity'],
                        cluePotential=item_data['cluePotential'],
                        value=item_data['value'],
                        condition=item_data['condition'],
                        image=item_data.get('image'),
                        type=item_data.get('type'),
                        defaultLocation=item_data.get('defaultLocation'),
                        defaultOwner=item_data.get('defaultOwner'),
                        use=item_data.get('use', []), # Default to empty list
                        uniqueProperties=item_data.get('uniqueProperties', []), # Default to empty list
                        significance=item_data.get('significance')
                    ))

    def save_clues(): # Added save_clues function
        with open(CLUES_FILE, "w") as f:
            json.dump([clue.__dict__ for clue in clues], f, indent=4)

    def load_clues(): # Added load_clues function
        nonlocal clues
        if os.path.exists(CLUES_FILE):
            with open(CLUES_FILE, "r") as f:
                data = json.load(f)
                clues.clear()
                for item in data:
                    clues.append(Clue(
                        id=item['id'],
                        criticalClue=item['criticalClue'],
                        redHerring=item['redHerring'],
                        isLie=item['isLie'],
                        source=item['source'],
                        clueSummary=item['clueSummary'],
                        knowledgeLevel=item['knowledgeLevel'],
                        discoveryPath=item.get('discoveryPath', []), # Default to empty list
                        presentationMethod=item.get('presentationMethod', []), # Default to empty list
                        characterImplicated=item.get('characterImplicated'),
                        redHerringType=item.get('redHerringType'),
                        mechanismOfMisdirection=item.get('mechanismOfMisdirection'),
                        debunkingClue=item.get('debunkingClue'),
                        dependencies=item.get('dependencies', []), # Default to empty list
                        requiredActionsForDiscovery=item.get('requiredActionsForDiscovery', []), # Default to empty list
                        revealsUnlocks=item.get('revealsUnlocks', []), # Default to empty list
                        associatedItem=item.get('associatedItem'),
                        associatedLocation=item.get('associatedLocation'),
                        associatedCharacter=item.get('associatedCharacter')
                    ))

    def save_case_meta(): # Added save_case_meta function
        with open(CASE_META_FILE, "w") as f:
            json.dump(case_meta.__dict__, f, indent=4)

    def load_case_meta(): # Added load_case_meta function
        nonlocal case_meta
        if os.path.exists(CASE_META_FILE):
            with open(CASE_META_FILE, "r") as f:
                data = json.load(f)
                case_meta = CaseMeta(
                    victim=data['victim'],
                    culprit=data['culprit'],
                    crimeScene=data['crimeScene'],
                    murderWeapon=data['murderWeapon'],
                    coreMysterySolutionDetails=data['coreMysterySolutionDetails'],
                    murderWeaponHidden=data.get('murderWeaponHidden', False),
                    meansClue=data.get('meansClue'),
                    motiveClue=data.get('motiveClue'),
                    opportunityClue=data.get('opportunityClue'),
                    redHerringClues=data.get('redHerringClues', []), # Default to empty list
                    narrativeViewpoint=data.get('narrativeViewpoint'),
                    narrativeTense=data.get('narrativeTense'),
                    openingMonologue=data.get('openingMonologue'),
                    ultimateRevealSceneDescription=data.get('ultimateRevealSceneDescription'),
                    successfulDenouement=data.get('successfulDenouement'),
                    failedDenouement=data.get('failedDenouement')
                )

    def save_lore_history():
        with open(LORE_HISTORY_FILE, "w") as f:
            f.write(lore_history_text)

    def load_lore_history():
        nonlocal lore_history_text
        if os.path.exists(LORE_HISTORY_FILE):
            with open(LORE_HISTORY_FILE, "r") as f:
                lore_history_text = f.read()

    def save_bulletin_board_nodes():
        with open(BULLETIN_BOARD_FILE, "w") as f:
            json.dump(bulletin_board_nodes, f, indent=4)

    def load_bulletin_board_nodes():
        nonlocal bulletin_board_nodes
        if os.path.exists(BULLETIN_BOARD_FILE):
            with open(BULLETIN_BOARD_FILE, "r") as f:
                bulletin_board_nodes = json.load(f)

    def save_timeline_events(): # Added save_timeline_events function
        with open(TIMELINE_FILE, "w") as f:
            json.dump([event.__dict__ for event in timeline_events], f, indent=4)

    def load_timeline_events(): # Added load_timeline_events function
        nonlocal timeline_events
        if os.path.exists(TIMELINE_FILE):
            with open(TIMELINE_FILE, "r") as f:
                data = json.load(f)
                timeline_events.clear()
                for item in data:
                    timeline_events.append(TimelineEvent(
                        id=item['id'],
                        name=item['name'],
                        description=item['description'],
                        timestamp=item['timestamp'],
                        associatedCharacters=item.get('associatedCharacters', []), # Default to empty list
                        associatedLocations=item.get('associatedLocations', []), # Default to empty list
                        associatedItems=item.get('associatedItems', []), # Default to empty list
                        cluesGenerated=item.get('cluesGenerated', []), # Default to empty list
                        revealsTruth=item.get('revealsTruth', False),
                        revealsLie=item.get('revealsLie', False),
                        lieDebunked=item.get('lieDebunked')
                    ))

    # --- Validation Logic ---
    def run_validation():
        validation_results.clear()

        # Helper to check for duplicate IDs
        def check_duplicate_ids(asset_list, asset_type_name):
            ids = set()
            for asset in asset_list:
                if asset.id in ids:
                    validation_results.append(ValidationResult(
                        message=f"Duplicate ID found for {asset_type_name}: {asset.id}",
                        type="error",
                        asset_id=asset.id,
                        asset_type=asset_type_name,
                        field_name="id"
                    ))
                else:
                    ids.add(asset.id)

        # Helper to check for missing required fields
        def check_missing_required_fields(asset_list, asset_type_name, required_fields):
            for asset in asset_list:
                asset_identifier = "Case Metadata" # Default for CaseMeta
                if hasattr(asset, 'fullName'):
                    asset_identifier = asset.fullName
                elif hasattr(asset, 'name'):
                    asset_identifier = asset.name
                elif hasattr(asset, 'id'):
                    asset_identifier = asset.id

                for field_name in required_fields:
                    if not getattr(asset, field_name):
                        validation_results.append(ValidationResult(
                            message=f"Missing required field '{field_name}' for {asset_type_name}: {asset_identifier}",
                            type="error",
                            asset_id=getattr(asset, 'id', None),
                            asset_type=asset_type_name,
                            field_name=field_name
                        ))

        # Run checks for Characters
        check_duplicate_ids(characters, "Character")
        check_missing_required_fields(characters, "Character", ["fullName", "biography", "personality", "alignment", "honesty", "victimLikelihood", "killerLikelihood"])

        # Run checks for Locations
        check_duplicate_ids(locations, "Location")
        check_missing_required_fields(locations, "Location", ["name", "description"])

        # Run checks for Factions
        check_duplicate_ids(factions, "Faction")
        check_missing_required_fields(factions, "Faction", ["name", "description"])

        # Run checks for Districts
        check_duplicate_ids(districts, "District")
        check_missing_required_fields(districts, "District", ["name", "description"])

        # Run checks for Items
        check_duplicate_ids(items, "Item")
        check_missing_required_fields(items, "Item", ["name", "description", "possibleMeans", "possibleMotive", "possibleOpportunity", "cluePotential", "value", "condition"])

        # Run checks for Clues
        check_duplicate_ids(clues, "Clue")
        check_missing_required_fields(clues, "Clue", ["id", "criticalClue", "redHerring", "isLie", "source", "clueSummary", "knowledgeLevel"])

        # Run checks for CaseMeta
        check_missing_required_fields([case_meta], "CaseMeta", ["victim", "culprit", "crimeScene", "murderWeapon", "coreMysterySolutionDetails"])

        # Run checks for Timeline Events
        check_duplicate_ids(timeline_events, "TimelineEvent")
        check_missing_required_fields(timeline_events, "TimelineEvent", ["name", "description", "timestamp"])

        # Tier 2: Logical Consistency (Errors)
        # Orphan Clues (simplified: check if victim, culprit, crimeScene, murderWeapon exist as IDs)
        all_asset_ids = set([c.id for c in characters] + [l.id for l in locations] + [f.id for f in factions] + [d.id for d in districts] + [i.id for i in items])
        if case_meta.victim and case_meta.victim not in all_asset_ids:
            validation_results.append(ValidationResult(message=f"CaseMeta: Victim ID '{case_meta.victim}' not found in assets.", type="error", asset_type="CaseMeta", field_name="victim"))
        if case_meta.culprit and case_meta.culprit not in all_asset_ids:
            validation_results.append(ValidationResult(message=f"CaseMeta: Culprit ID '{case_meta.culprit}' not found in assets.", type="error", asset_type="CaseMeta", field_name="culprit"))
        if case_meta.crimeScene and case_meta.crimeScene not in all_asset_ids:
            validation_results.append(ValidationResult(message=f"CaseMeta: Crime Scene ID '{case_meta.crimeScene}' not found in assets.", type="error", asset_type="CaseMeta", field_name="crimeScene"))
        if case_meta.murderWeapon and case_meta.murderWeapon not in all_asset_ids:
            validation_results.append(ValidationResult(message=f"CaseMeta: Murder Weapon ID '{case_meta.murderWeapon}' not found in assets.", type="error", asset_type="CaseMeta", field_name="murderWeapon"))

        # Basic Chronology check for Timeline Events
        # Convert timestamps to comparable format (e.g., datetime objects) for proper comparison
        # For simplicity, assuming timestamps are sortable strings for now.
        sorted_timeline = sorted(timeline_events, key=lambda x: x.timestamp)
        for i in range(len(sorted_timeline) - 1):
            if sorted_timeline[i].timestamp > sorted_timeline[i+1].timestamp:
                validation_results.append(ValidationResult(
                    message=f"Timeline Event '{sorted_timeline[i+1].name}' (at {sorted_timeline[i+1].timestamp}) is chronologically before '{sorted_timeline[i].name}' (at {sorted_timeline[i].timestamp}).",
                    type="error",
                    asset_id=sorted_timeline[i+1].id,
                    asset_type="TimelineEvent",
                    field_name="timestamp"
                ))

        # Circular Logic (direct allies/enemies)
        for char in characters:
            for ally_id in char.allies:
                ally_char = next((c for c in characters if c.id == ally_id), None)
                if ally_char and char.id in ally_char.allies:
                    validation_results.append(ValidationResult(
                        message=f"Circular alliance detected between {char.fullName} and {ally_char.fullName}.",
                        type="error",
                        asset_id=char.id,
                        asset_type="Character",
                        field_name="allies"
                    ))
            for enemy_id in char.enemies:
                enemy_char = next((c for c in characters if c.id == enemy_id), None)
                if enemy_char and char.id in enemy_char.enemies:
                    validation_results.append(ValidationResult(
                        message=f"Circular enmity detected between {char.fullName} and {enemy_char.fullName}.",
                        type="error",
                        asset_id=char.id,
                        asset_type="Character",
                        field_name="enemies"
                    ))

        # Undebunkable Lies
        for clue in clues:
            if clue.isLie and not clue.debunkingClue:
                validation_results.append(ValidationResult(
                    message=f"Undebunkable lie detected for clue '{clue.clueSummary}'. All lies must have a debunking clue.",
                    type="error",
                    asset_id=clue.id,
                    asset_type="Clue",
                    field_name="debunkingClue"
                ))

        # Tier 3: Playability & Narrative Craft (Warnings)
        # Plausible Suspects
        killer_suspects = [char for char in characters if char.killerLikelihood > 50]
        if len(killer_suspects) < 2:
            validation_results.append(ValidationResult(
                message="Consider adding more plausible killer suspects (characters with killerLikelihood > 50).",
                type="warning",
                asset_type="Character",
                field_name="killerLikelihood"
            ))

        # Red Herring Sufficiency
        red_herring_clues = [clue for clue in clues if clue.redHerring]
        if len(red_herring_clues) < 2:
            validation_results.append(ValidationResult(
                message="Consider adding more red herring clues for narrative depth.",
                type="warning",
                asset_type="Clue",
                field_name="redHerring"
            ))

        # Update Validator UI
        update_validator_ui()

    # --- Validator UI Component ---
    validator_output = ft.Column(
        [],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True
    )

    validator_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("Validation Results", color="#FFFFFF", size=18),
                ft.Divider(),
                validator_output,
            ],
            expand=True
        ),
        width=300, # Fixed width for now
        height=page.height, # Will be dynamic
        bgcolor="#1A2B3C",
        padding=ft.padding.all(10),
        border=ft.border.only(left=ft.border.BorderSide(1, "#3A4D60")),
        visible=True # Initially visible for testing
    )

    def update_validator_ui():
        validator_output.controls.clear()
        if not validation_results:
            validator_output.controls.append(ft.Text("No validation issues found.", color="#9E9E9E"))
        else:
            for result in validation_results:
                color = "#FF5252" if result.type == "error" else "#FFC107" # Red for error, Amber for warning
                validator_output.controls.append(ft.Text(f"{result.type.upper()}: {result.message}", color=color))
        page.update()

    # --- CaseMeta View ---
    def create_case_meta_view():
        victim_field = ft.TextField(label="Victim", value=case_meta.victim, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        culprit_field = ft.TextField(label="Culprit", value=case_meta.culprit, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        crime_scene_field = ft.TextField(label="Crime Scene", value=case_meta.crimeScene, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        murder_weapon_field = ft.TextField(label="Murder Weapon", value=case_meta.murderWeapon, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        core_mystery_solution_details_field = ft.TextField(label="Core Mystery Solution Details", value=case_meta.coreMysterySolutionDetails, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        murder_weapon_hidden_field = ft.Checkbox(label="Murder Weapon Hidden", value=case_meta.murderWeaponHidden, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        means_clue_field = ft.TextField(label="Means Clue", value=case_meta.meansClue, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        motive_clue_field = ft.TextField(label="Motive Cl", value=case_meta.motiveClue, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        opportunity_clue_field = ft.TextField(label="Opportunity Clue", value=case_meta.opportunityClue, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        narrative_viewpoint_field = ft.Dropdown(
            label="Narrative Viewpoint",
            value=case_meta.narrativeViewpoint,
            options=[ft.dropdown.Option("First-Person"), ft.dropdown.Option("Third-Limited (Sleuth)"), ft.dropdown.Option("Third-Limited (Multiple)"), ft.dropdown.Option("Omniscient"), ft.dropdown.Option("Storyteller Omniscient"), ft.dropdown.Option("Epistolary")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        narrative_tense_field = ft.Dropdown(
            label="Narrative Tense",
            value=case_meta.narrativeTense,
            options=[ft.dropdown.Option("Past"), ft.dropdown.Option("Present")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        opening_monologue_field = ft.TextField(label="Opening Monologue", value=case_meta.openingMonologue, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        ultimate_reveal_scene_description_field = ft.TextField(label="Ultimate Reveal Scene Description", value=case_meta.ultimateRevealSceneDescription, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        successful_denouement_field = ft.TextField(label="Successful Denouement", value=case_meta.successfulDenouement, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        failed_denouement_field = ft.TextField(label="Failed Denouement", value=case_meta.failedDenouement, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_case_meta_details(e):
            case_meta.victim = victim_field.value
            case_meta.culprit = culprit_field.value
            case_meta.crimeScene = crime_scene_field.value
            case_meta.murderWeapon = murder_weapon_field.value
            case_meta.coreMysterySolutionDetails = core_mystery_solution_details_field.value
            case_meta.murderWeaponHidden = murder_weapon_hidden_field.value
            case_meta.meansClue = means_clue_field.value
            case_meta.motiveClue = motive_clue_field.value
            case_meta.opportunityClue = opportunity_clue_field.value
            case_meta.narrativeViewpoint = narrative_viewpoint_field.value
            case_meta.narrativeTense = narrative_tense_field.value
            case_meta.openingMonologue = opening_monologue_field.value
            case_meta.ultimateRevealSceneDescription = ultimate_reveal_scene_description_field.value
            case_meta.successfulDenouement = successful_denouement_field.value
            case_meta.failedDenouement = failed_denouement_field.value

            save_case_meta()
            run_validation()
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Case Metadata", color="#FFFFFF", size=20),
                    victim_field,
                    culprit_field,
                    crime_scene_field,
                    murder_weapon_field,
                    core_mystery_solution_details_field,
                    murder_weapon_hidden_field,
                    means_clue_field,
                    motive_clue_field,
                    opportunity_clue_field,
                    narrative_viewpoint_field,
                    narrative_tense_field,
                    opening_monologue_field,
                    ultimate_reveal_scene_description_field,
                    successful_denouement_field,
                    failed_denouement_field,
                    ft.ElevatedButton(
                        text="Save Case Metadata",
                        icon=ft.Icons.SAVE,
                        bgcolor="#64B5F6",
                        color="#FFFFFF",
                        on_click=save_case_meta_details
                    )
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    # --- Character Detail View ---
    def create_character_detail_view(character: Character, characters_list_view, character_detail_container, select_character):
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
        alias_field = ft.TextField(label="Alias", value=character.alias, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        age_field = ft.TextField(label="Age", value=str(character.age) if character.age else "", keyboard_type=ft.KeyboardType.NUMBER, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        employment_field = ft.TextField(label="Employment", value=character.employment, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        image_field = ft.TextField(label="Image URL", value=character.image, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        faction_field = ft.TextField(label="Faction", value=character.faction, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        district_field = ft.TextField(label="District", value=character.district, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        motivations_field = ft.TextField(label="Motivations (comma-separated)", value=", ".join(character.motivations), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        secrets_field = ft.TextField(label="Secrets (comma-separated)", value=", ".join(character.secrets), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        allies_field = ft.TextField(label="Allies (comma-separated IDs)", value=", ".join(character.allies), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        enemies_field = ft.TextField(label="Enemies (comma-separated IDs)", value=", ".join(character.enemies), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        items_field = ft.TextField(label="Items (comma-separated IDs)", value=", ".join(character.items), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        archetype_field = ft.TextField(label="Archetype", value=character.archetype, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        values_field = ft.TextField(label="Values (comma-separated)", value=", ".join(character.values), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        flaws_field = ft.TextField(label="Flaws/Limitations (comma-separated)", value=", ".join(character.flawsHandicapsLimitations), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        quirks_field = ft.TextField(label="Quirks (comma-separated)", value=", ".join(character.quirks), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        characteristics_field = ft.TextField(label="Characteristics (comma-separated)", value=", ".join(character.characteristics), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        vulnerabilities_field = ft.TextField(label="Vulnerabilities (comma-separated)", value=", ".join(character.vulnerabilities), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        voice_model_field = ft.TextField(label="Voice Model", value=character.voiceModel, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        dialogue_style_field = ft.TextField(label="Dialogue Style", value=character.dialogueStyle, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        expertise_field = ft.TextField(label="Expertise (comma-separated)", value=", ".join(character.expertise), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        portrayal_notes_field = ft.TextField(label="Portrayal Notes", value=character.portrayalNotes, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

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
            character.alias = alias_field.value
            character.age = int(age_field.value) if age_field.value else None
            character.employment = employment_field.value
            character.image = image_field.value
            character.faction = faction_field.value
            character.district = district_field.value
            character.motivations = [m.strip() for m in motivations_field.value.split(',') if m.strip()]
            character.secrets = [s.strip() for s in secrets_field.value.split(',') if s.strip()]
            character.allies = [a.strip() for a in allies_field.value.split(',') if a.strip()]
            character.enemies = [en.strip() for en in enemies_field.value.split(',') if en.strip()]
            character.items = [it.strip() for it in items_field.value.split(',') if it.strip()]
            character.archetype = archetype_field.value
            character.values = [v.strip() for v in values_field.value.split(',') if v.strip()]
            character.flawsHandicapsLimitations = [f.strip() for f in flaws_field.value.split(',') if f.strip()]
            character.quirks = [q.strip() for q in quirks_field.value.split(',') if q.strip()]
            character.characteristics = [c.strip() for c in characteristics_field.value.split(',') if c.strip()]
            character.vulnerabilities = [v.strip() for v in vulnerabilities_field.value.split(',') if v.strip()]
            character.voiceModel = voice_model_field.value
            character.dialogueStyle = dialogue_style_field.value
            character.expertise = [e.strip() for e in expertise_field.value.split(',') if e.strip()]
            character.portrayalNotes = portrayal_notes_field.value

            # Update the character list view to reflect name changes
            characters_list_view.controls.clear()
            for char_item in characters:
                characters_list_view.controls.append(ft.GestureDetector(content=ft.Text(char_item.fullName, color="#FFFFFF"), on_tap=lambda e, char=char_item: select_character(char))) # Use GestureDetector
            save_characters() # Save characters after modification
            run_validation() # Run validation after modification
            page.update()

        def delete_character(e):
            characters.remove(character)
            characters_list_view.controls.clear()
            for char_item in characters:
                characters_list_view.controls.append(ft.GestureDetector(content=ft.Text(char_item.fullName, color="#FFFFFF"), on_tap=lambda e, char=char_item: select_character(char))) # Use GestureDetector
            character_detail_container.content = ft.Column([ft.Text("Select a character to view details", color="#9E9E9E")])
            save_characters() # Save characters after modification
            run_validation() # Run validation after modification
            page.update()

        return ft.Column(
            [
                ft.Text(f"Character Details: {character.fullName}", color="#FFFFFF", size=20),
                full_name_field,
                alias_field,
                age_field,
                gender_field,
                employment_field,
                image_field,
                faction_field,
                wealth_class_field,
                district_field,
                biography_field,
                personality_field,
                alignment_field,
                honesty_field,
                victim_likelihood_field,
                killer_likelihood_field,
                motivations_field,
                secrets_field,
                allies_field,
                enemies_field,
                items_field,
                archetype_field,
                values_field,
                flaws_field,
                quirks_field,
                characteristics_field,
                vulnerabilities_field,
                voice_model_field,
                dialogue_style_field,
                expertise_field,
                portrayal_notes_field,
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
    def create_location_detail_view(location: Location, locations_list_view, location_detail_container, select_location):
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
        image_field = ft.TextField(label="Image URL", value=location.image, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        key_characters_field = ft.TextField(label="Key Characters (comma-separated IDs)", value=", ".join(location.keyCharacters), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_items_field = ft.TextField(label="Associated Items (comma-separated IDs)", value=", ".join(location.associatedItems), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        clues_field = ft.TextField(label="Clues (comma-separated IDs)", value=", ".join(location.clues), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

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
            location.image = image_field.value
            location.keyCharacters = [kc.strip() for kc in key_characters_field.value.split(',') if kc.strip()]
            location.associatedItems = [ai.strip() for ai in associated_items_field.value.split(',') if ai.strip()]
            location.clues = [c.strip() for c in clues_field.value.split(',') if c.strip()]

            # Update the location list view to reflect name changes
            locations_list_view.controls.clear()
            for loc_item in locations:
                locations_list_view.controls.append(ft.GestureDetector(content=ft.Text(loc_item.name, color="#FFFFFF"), on_tap=lambda e, loc=loc_item: select_location(loc))) # Use GestureDetector
            save_locations() # Save locations after modification
            run_validation() # Run validation after modification
            page.update()

        def delete_location(e):
            locations.remove(location)
            locations_list_view.controls.clear()
            for loc_item in locations:
                locations_list_view.controls.append(ft.GestureDetector(content=ft.Text(loc_item.name, color="#FFFFFF"), on_tap=lambda e, loc=loc_item: select_location(loc))) # Use GestureDetector
            location_detail_container.content = ft.Column([ft.Text("Select a location to view details", color="#9E9E9E")])
            save_locations() # Save locations after modification
            run_validation() # Run validation after modification
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
                image_field,
                key_characters_field,
                associated_items_field,
                accessibility_field,
                hidden_field,
                internal_logic_notes_field,
                clues_field,
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
    def create_faction_detail_view(faction: Faction, factions_list_view, faction_detail_container, select_faction):
        # Create TextField controls for each editable field
        name_field = ft.TextField(label="Name", value=faction.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=faction.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        archetype_field = ft.TextField(label="Archetype", value=faction.archetype, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        ideology_field = ft.TextField(label="Ideology", value=faction.ideology, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        headquarters_field = ft.TextField(label="Headquarters", value=faction.headquarters, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        public_perception_field = ft.TextField(label="Public Perception", value=faction.publicPerception, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        image_field = ft.TextField(label="Image URL", value=faction.image, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        resources_field = ft.TextField(label="Resources (comma-separated)", value=", ".join(faction.resources), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        ally_factions_field = ft.TextField(label="Ally Factions (comma-separated IDs)", value=", ".join(faction.allyFactions), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        enemy_factions_field = ft.TextField(label="Enemy Factions (comma-separated IDs)", value=", ".join(faction.enemyFactions), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        members_field = ft.TextField(label="Members (comma-separated IDs)", value=", ".join(faction.members), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        influence_field = ft.Dropdown(
            label="Influence",
            value=faction.influence,
            options=[ft.dropdown.Option("Local"), ft.dropdown.Option("District-wide"), ft.dropdown.Option("City-wide"), ft.dropdown.Option("Regional"), ft.dropdown.Option("Global")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )

        def save_faction_details(e):
            faction.name = name_field.value
            faction.description = description_field.value
            faction.archetype = archetype_field.value
            faction.ideology = ideology_field.value
            faction.headquarters = headquarters_field.value
            faction.publicPerception = public_perception_field.value
            faction.image = image_field.value
            faction.resources = [r.strip() for r in resources_field.value.split(',') if r.strip()]
            faction.allyFactions = [af.strip() for af in ally_factions_field.value.split(',') if af.strip()]
            faction.enemyFactions = [ef.strip() for ef in enemy_factions_field.value.split(',') if ef.strip()]
            faction.members = [m.strip() for m in members_field.value.split(',') if m.strip()]
            faction.influence = influence_field.value

            # Update the faction list view to reflect name changes
            factions_list_view.controls.clear()
            for fac_item in factions:
                factions_list_view.controls.append(ft.GestureDetector(content=ft.Text(fac_item.name, color="#FFFFFF"), on_tap=lambda e, fac=fac_item: select_faction(fac))) # Use GestureDetector
            save_factions() # Save factions after modification
            run_validation() # Run validation after modification
            page.update()

        def delete_faction(e):
            factions.remove(faction)
            factions_list_view.controls.clear()
            for fac_item in factions:
                factions_list_view.controls.append(ft.GestureDetector(content=ft.Text(fac_item.name, color="#FFFFFF"), on_tap=lambda e, fac=fac_item: select_faction(fac))) # Use GestureDetector
            faction_detail_container.content = ft.Column([ft.Text("Select a faction to view details", color="#9E9E9E")])
            save_factions() # Save factions after modification
            run_validation() # Run validation after modification
            page.update()

        return ft.Column(
            [
                ft.Text(f"Faction Details: {faction.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                archetype_field,
                ideology_field,
                headquarters_field,
                image_field,
                resources_field,
                ally_factions_field,
                enemy_factions_field,
                members_field,
                influence_field,
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

    # --- District Detail View ---
    def create_district_detail_view(district: District, districts_list_view, district_detail_container, select_district):
        # Create TextField controls for each editable field
        name_field = ft.TextField(label="Name", value=district.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=district.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        wealth_class_field = ft.Dropdown(
            label="Wealth Class",
            value=district.wealthClass,
            options=[ft.dropdown.Option(wc) for wc in WealthClass.__args__],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        atmosphere_field = ft.TextField(label="Atmosphere", value=district.atmosphere, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        population_density_field = ft.Dropdown(
            label="Population Density",
            value=district.populationDensity,
            options=[ft.dropdown.Option("Sparse"), ft.dropdown.Option("Moderate"), ft.dropdown.Option("Dense"), ft.dropdown.Option("Crowded")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        dominant_faction_field = ft.TextField(label="Dominant Faction", value=district.dominantFaction, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        image_field = ft.TextField(label="Image URL", value=district.image, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        notable_features_field = ft.TextField(label="Notable Features (comma-separated)", value=", ".join(district.notableFeatures), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        key_locations_field = ft.TextField(label="Key Locations (comma-separated IDs)", value=", ".join(district.keyLocations), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_district_details(e):
            district.name = name_field.value
            district.description = description_field.value
            district.wealthClass = wealth_class_field.value if wealth_class_field.value else None
            district.atmosphere = atmosphere_field.value
            district.populationDensity = population_density_field.value if population_density_field.value else None
            district.dominantFaction = dominant_faction_field.value
            district.image = image_field.value
            district.notableFeatures = [nf.strip() for nf in notable_features_field.value.split(',') if nf.strip()]
            district.keyLocations = [kl.strip() for kl in key_locations_field.value.split(',') if kl.strip()]

            # Update the district list view to reflect name changes
            districts_list_view.controls.clear()
            for dist_item in districts:
                districts_list_view.controls.append(ft.GestureDetector(content=ft.Text(dist_item.name, color="#FFFFFF"), on_tap=lambda e, dist=dist_item: select_district(dist))) # Use GestureDetector
            save_districts() # Save districts after modification
            run_validation() # Run validation after modification
            page.update()

        def delete_district(e):
            districts.remove(district)
            districts_list_view.controls.clear()
            for dist_item in districts:
                districts_list_view.controls.append(ft.GestureDetector(content=ft.Text(dist_item.name, color="#FFFFFF"), on_tap=lambda e, dist=dist_item: select_district(dist))) # Use GestureDetector
            district_detail_container.content = ft.Column([ft.Text("Select a district to view details", color="#9E9E9E")])
            save_districts() # Save districts after modification
            run_validation() # Run validation after modification
            page.update()

        return ft.Column(
            [
                ft.Text(f"District Details: {district.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                wealth_class_field,
                atmosphere_field,
                population_density_field,
                dominant_faction_field,
                image_field,
                notable_features_field,
                key_locations_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_district_details
                        ),
                        ft.ElevatedButton(
                            text="Delete District",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_district
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Item Detail View ---
    def create_item_detail_view(item: Item, items_list_view, item_detail_container, select_item):
        name_field = ft.TextField(label="Name", value=item.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=item.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        possible_means_field = ft.Checkbox(label="Possible Means", value=item.possibleMeans, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        possible_motive_field = ft.Checkbox(label="Possible Motive", value=item.possibleMotive, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        possible_opportunity_field = ft.Checkbox(label="Possible Opportunity", value=item.possibleOpportunity, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        clue_potential_field = ft.Dropdown(
            label="Clue Potential",
            value=item.cluePotential,
            options=[ft.dropdown.Option("None"), ft.dropdown.Option("Low"), ft.dropdown.Option("Medium"), ft.dropdown.Option("High"), ft.dropdown.Option("Critical")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        value_field = ft.TextField(label="Value", value=item.value, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        condition_field = ft.Dropdown(
            label="Condition",
            value=item.condition,
            options=[ft.dropdown.Option("New"), ft.dropdown.Option("Good"), ft.dropdown.Option("Used"), ft.dropdown.Option("Worn"), ft.dropdown.Option("Damaged"), ft.dropdown.Option("Broken")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        image_field = ft.TextField(label="Image URL", value=item.image, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        type_field = ft.TextField(label="Type", value=item.type, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        default_location_field = ft.TextField(label="Default Location ID", value=item.defaultLocation, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        default_owner_field = ft.TextField(label="Default Owner ID", value=item.defaultOwner, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        use_field = ft.TextField(label="Use (comma-separated)", value=", ".join(item.use), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        unique_properties_field = ft.TextField(label="Unique Properties (comma-separated)", value=", ".join(item.uniqueProperties), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        significance_field = ft.TextField(label="Significance", value=item.significance, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_item_details(e):
            item.name = name_field.value
            item.description = description_field.value
            item.possibleMeans = possible_means_field.value
            item.possibleMotive = possible_motive_field.value
            item.possibleOpportunity = possible_opportunity_field.value
            item.cluePotential = clue_potential_field.value
            item.value = value_field.value
            item.condition = condition_field.value
            item.image = image_field.value
            item.type = type_field.value
            item.defaultLocation = default_location_field.value
            item.defaultOwner = default_owner_field.value
            item.use = [u.strip() for u in use_field.value.split(',') if u.strip()]
            item.uniqueProperties = [up.strip() for up in unique_properties_field.value.split(',') if up.strip()]
            item.significance = significance_field.value

            items_list_view.controls.clear()
            for item_obj in items:
                items_list_view.controls.append(ft.GestureDetector(content=ft.Text(item_obj.name, color="#FFFFFF"), on_tap=lambda e, item=item_obj: select_item(item))) # Use GestureDetector
            save_items()
            run_validation()
            page.update()

        def delete_item(e):
            items.remove(item)
            items_list_view.controls.clear()
            for item_obj in items:
                items_list_view.controls.append(ft.GestureDetector(content=ft.Text(item_obj.name, color="#FFFFFF"), on_tap=lambda e, item=item_obj: select_item(item))) # Use GestureDetector
            item_detail_container.content = ft.Column([ft.Text("Select an item to view details", color="#9E9E9E")])
            save_items()
            run_validation()
            page.update()

        return ft.Column(
            [
                ft.Text(f"Item Details: {item.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                possible_means_field,
                possible_motive_field,
                possible_opportunity_field,
                clue_potential_field,
                value_field,
                condition_field,
                image_field,
                type_field,
                default_location_field,
                default_owner_field,
                use_field,
                unique_properties_field,
                significance_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_item_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Item",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_item
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Clue Detail View ---
    def create_clue_detail_view(clue: Clue, clues_list_view, clue_detail_container, select_clue):
        clue_summary_field = ft.TextField(label="Clue Summary", value=clue.clueSummary, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        source_field = ft.TextField(label="Source", value=clue.source, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        critical_clue_field = ft.Checkbox(label="Critical Clue", value=clue.criticalClue, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        red_herring_field = ft.Checkbox(label="Red Herring", value=clue.redHerring, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        is_lie_field = ft.Checkbox(label="Is Lie", value=clue.isLie, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        knowledge_level_field = ft.Dropdown(
            label="Knowledge Level",
            value=clue.knowledgeLevel,
            options=[ft.dropdown.Option("Sleuth Only"), ft.dropdown.Option("Reader Only"), ft.dropdown.Option("Both"), ft.dropdown.Option("Neither (Off-Page)")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        debunking_clue_field = ft.TextField(label="Debunking Clue ID", value=clue.debunkingClue, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        character_implicated_field = ft.TextField(label="Character Implicated ID", value=clue.characterImplicated, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        red_herring_type_field = ft.Dropdown(
            label="Red Herring Type",
            value=clue.redHerringType,
            options=[ft.dropdown.Option("Decoy Suspect"), ft.dropdown.Option("Misleading Object"), ft.dropdown.Option("False Alibi"), ft.dropdown.Option("Misleading Dialogue")],
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6",
            filled=True,
            fill_color="#3A4D60",
        )
        mechanism_of_misdirection_field = ft.TextField(label="Mechanism of Misdirection", value=clue.mechanismOfMisdirection, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_item_field = ft.TextField(label="Associated Item ID", value=clue.associatedItem, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_location_field = ft.TextField(label="Associated Location ID", value=clue.associatedLocation, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_character_field = ft.TextField(label="Associated Character ID", value=clue.associatedCharacter, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_clue_details(e):
            clue.clueSummary = clue_summary_field.value
            clue.source = source_field.value
            clue.criticalClue = critical_clue_field.value
            clue.redHerring = red_herring_field.value
            clue.isLie = is_lie_field.value
            clue.knowledgeLevel = knowledge_level_field.value
            clue.debunkingClue = debunking_clue_field.value
            clue.characterImplicated = character_implicated_field.value
            clue.redHerringType = red_herring_type_field.value
            clue.mechanismOfMisdirection = mechanism_of_misdirection_field.value
            clue.associatedItem = associated_item_field.value
            clue.associatedLocation = associated_location_field.value
            clue.associatedCharacter = associated_character_field.value

            clues_list_view.controls.clear()
            for clue_obj in clues:
                clues_list_view.controls.append(ft.GestureDetector(content=ft.Text(clue_obj.clueSummary, color="#FFFFFF"), on_tap=lambda e, clue=clue_obj: select_clue(clue))) # Use GestureDetector
            save_clues()
            run_validation()
            page.update()

        def delete_clue(e):
            clues.remove(clue)
            clues_list_view.controls.clear()
            for clue_obj in clues:
                clues_list_view.controls.append(ft.GestureDetector(content=ft.Text(clue_obj.clueSummary, color="#FFFFFF"), on_tap=lambda e, clue=clue_obj: select_clue(clue))) # Use GestureDetector
            clue_detail_container.content = ft.Column([ft.Text("Select a clue to view details", color="#9E9E9E")])
            save_clues()
            run_validation()
            page.update()

        return ft.Column(
            [
                ft.Text(f"Clue Details: {clue.clueSummary}", color="#FFFFFF", size=20),
                clue_summary_field,
                source_field,
                critical_clue_field,
                red_herring_field,
                is_lie_field,
                knowledge_level_field,
                debunking_clue_field,
                character_implicated_field,
                red_herring_type_field,
                mechanism_of_misdirection_field,
                associated_item_field,
                associated_location_field,
                associated_character_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_clue_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Clue",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_clue
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    # --- Content Views ---
    # Declare these outside to make them accessible to save/delete functions
    characters_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    character_detail_container = ft.Container(content=ft.Column([ft.Text("Select a character to view details", color="#9E9E9E")]), expand=True, padding=20)

    locations_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    location_detail_container = ft.Container(content=ft.Column([ft.Text("Select a location to view details", color="#9E9E9E")]), expand=True, padding=20)

    factions_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    faction_detail_container = ft.Container(content=ft.Column([ft.Text("Select a faction to view details", color="#9E9E9E")]), expand=True, padding=20)

    districts_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    district_detail_container = ft.Container(content=ft.Column([ft.Text("Select a district to view details", color="#9E9E9E")]), expand=True, padding=20)

    items_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    item_detail_container = ft.Container(content=ft.Column([ft.Text("Select an item to view details", color="#9E9E9E")]), expand=True, padding=20)

    clues_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    clue_detail_container = ft.Container(content=ft.Column([ft.Text("Select a clue to view details", color="#9E9E9E")]), expand=True, padding=20)

    timeline_events_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    timeline_event_detail_container = ft.Container(content=ft.Column([ft.Text("Select a timeline event to view details", color="#9E9E9E")]), expand=True, padding=20)

    def select_character(char):
        character_detail_container.content = create_character_detail_view(char, characters_list_view, character_detail_container, select_character)
        page.update()

    def select_location(loc):
        location_detail_container.content = create_location_detail_view(loc, locations_list_view, location_detail_container, select_location)
        page.update()

    def select_faction(fac):
        faction_detail_container.content = create_faction_detail_view(fac, factions_list_view, faction_detail_container, select_faction)
        page.update()

    def select_district(dist):
        district_detail_container.content = create_district_detail_view(dist, districts_list_view, district_detail_container, select_district)
        page.update()

    def select_item(item):
        item_detail_container.content = create_item_detail_view(item, items_list_view, item_detail_container, select_item)
        page.update()

    def select_clue(clue):
        clue_detail_container.content = create_clue_detail_view(clue, clues_list_view, clue_detail_container, select_clue)
        page.update()

    def select_timeline_event(event):
        timeline_event_detail_container.content = create_timeline_event_detail_view(event, timeline_events_list_view, timeline_event_detail_container, select_timeline_event)
        page.update()

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

        # Populate on load
        characters_list_view.controls.clear()
        for char in characters:
            characters_list_view.controls.append(ft.GestureDetector(content=ft.Text(char.fullName, color="#FFFFFF"), on_tap=lambda e, char=char: select_character(char)))

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
                characters_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_character.fullName, color="#FFFFFF"), on_tap=lambda e, char=new_character: select_character(char))) # Use GestureDetector
                character_name_input.value = ""
                save_characters() # Save characters after adding
                run_validation() # Run validation after modification
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

        # Populate on load
        locations_list_view.controls.clear()
        for loc in locations:
            locations_list_view.controls.append(ft.GestureDetector(content=ft.Text(loc.name, color="#FFFFFF"), on_tap=lambda e, loc=loc: select_location(loc)))

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
                locations_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_location.name, color="#FFFFFF"), on_tap=lambda e, loc=new_location: select_location(loc))) # Use GestureDetector
                location_name_input.value = ""
                save_locations() # Save locations after adding
                run_validation() # Run validation after modification
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

        # Populate on load
        factions_list_view.controls.clear()
        for fac in factions:
            factions_list_view.controls.append(ft.GestureDetector(content=ft.Text(fac.name, color="#FFFFFF"), on_tap=lambda e, fac=fac: select_faction(fac)))

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
                factions_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_faction.name, color="#FFFFFF"), on_tap=lambda e, fac=new_faction: select_faction(fac))) # Use GestureDetector
                faction_name_input.value = ""
                save_factions() # Save factions after adding
                run_validation() # Run validation after modification
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

    def create_districts_view():
        district_name_input = ft.TextField(
            label="District Name",
            hint_text="Enter district name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        # Populate on load
        districts_list_view.controls.clear()
        for dist in districts:
            districts_list_view.controls.append(ft.GestureDetector(content=ft.Text(dist.name, color="#FFFFFF"), on_tap=lambda e, dist=dist: select_district(dist)))

        def add_district(e):
            if district_name_input.value:
                new_district = District(
                    id=str(uuid.uuid4()),
                    name=district_name_input.value,
                    description="", # Placeholder
                    wealthClass=WealthClass.__args__[0], # Placeholder
                    atmosphere="", # Placeholder
                    populationDensity="Sparse", # Placeholder
                    dominantFaction="", # Placeholder
                )
                districts.append(new_district)
                districts_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_district.name, color="#FFFFFF"), on_tap=lambda e, dist=new_district: select_district(dist))) # Use GestureDetector
                district_name_input.value = ""
                save_districts() # Save districts after adding
                run_validation() # Run validation after modification
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Districts Management", color="#FFFFFF", size=20),
                    ft.Text("List of districts and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            district_name_input,
                            ft.ElevatedButton(
                                text="Add District",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_district
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=districts_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            district_detail_container,
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

    def create_items_view(): # Added create_items_view
        item_name_input = ft.TextField(
            label="Item Name",
            hint_text="Enter item name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        # Populate on load
        items_list_view.controls.clear()
        for item_obj in items:
            items_list_view.controls.append(ft.GestureDetector(content=ft.Text(item_obj.name, color="#FFFFFF"), on_tap=lambda e, item=item_obj: select_item(item)))

        def add_item(e):
            if item_name_input.value:
                new_item = Item(
                    id=str(uuid.uuid4()),
                    name=item_name_input.value,
                    description="", # Placeholder
                    possibleMeans=False, # Placeholder
                    possibleMotive=False, # Placeholder
                    possibleOpportunity=False, # Placeholder
                    cluePotential="None", # Placeholder
                    value="", # Placeholder
                    condition="New", # Placeholder
                )
                items.append(new_item)
                items_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_item.name, color="#FFFFFF"), on_tap=lambda e, item=new_item: select_item(item))) # Use GestureDetector
                item_name_input.value = ""
                save_items() # Save items after adding
                run_validation() # Run validation after modification
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Items Management", color="#FFFFFF", size=20),
                    ft.Text("List of items and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            item_name_input,
                            ft.ElevatedButton(
                                text="Add Item",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_item
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=items_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            item_detail_container,
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

    def create_clues_view(): # Added create_clues_view
        clue_summary_input = ft.TextField(
            label="Clue Summary",
            hint_text="Enter clue summary",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        # Populate on load
        clues_list_view.controls.clear()
        for clue_obj in clues:
            clues_list_view.controls.append(ft.GestureDetector(content=ft.Text(clue_obj.clueSummary, color="#FFFFFF"), on_tap=lambda e, clue=clue_obj: select_clue(clue)))

        def add_clue(e):
            if clue_summary_input.value:
                new_clue = Clue(
                    id=str(uuid.uuid4()),
                    clueSummary=clue_summary_input.value,
                    criticalClue=False, # Placeholder
                    redHerring=False, # Placeholder
                    isLie=False, # Placeholder
                    source="", # Placeholder
                    knowledgeLevel="Sleuth Only", # Placeholder
                )
                clues.append(new_clue)
                clues_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_clue.clueSummary, color="#FFFFFF"), on_tap=lambda e, clue=new_clue: select_clue(clue))) # Use GestureDetector
                clue_summary_input.value = ""
                save_clues() # Save clues after adding
                run_validation() # Run validation after modification
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Clues Management", color="#FFFFFF", size=20),
                    ft.Text("List of clues and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            clue_summary_input,
                            ft.ElevatedButton(
                                text="Add Clue",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6", # Light blue button
                                color="#FFFFFF",
                                on_click=add_clue
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=clues_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            clue_detail_container,
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
            save_lore_history() # Save lore history after modification
            run_validation() # Run validation after modification
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
        # Node data structure: {"id": "node1", "type": "character", "x": 100, "y": 100, "text": "Node 1 Text"}
        # This will be populated from bulletin_board_nodes list
        node_controls = []

        def on_pan_update(e: ft.DragUpdateEvent, node_data):
            node_data["x"] += e.delta_x
            node_data["y"] += e.delta_y
            e.control.top = node_data["y"]
            e.control.left = node_data["x"]
            e.control.update()

        def create_draggable_node(node_data):
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text(node_data["text"], color="#FFFFFF"),
                        # Add more node content here based on node_data["type"]
                    ]
                ),
                width=150,
                height=100,
                bgcolor="#3A4D60",
                border_radius=5,
                padding=10,
                top=node_data["y"],
                left=node_data["x"],
                data=node_data, # Store node data in the control
                on_pan_update=lambda e: on_pan_update(e, node_data)
            )

        def add_node(e):
            new_node_data = {"id": str(uuid.uuid4()), "type": "generic", "x": 50, "y": 50, "text": "New Node"}
            bulletin_board_nodes.append(new_node_data)
            node_controls.append(create_draggable_node(new_node_data))
            save_bulletin_board_nodes()
            page.update()

        # Populate nodes from loaded data
        for node_data in bulletin_board_nodes:
            node_controls.append(create_draggable_node(node_data))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Interactive Bulletin Board", color="#FFFFFF", size=20),
                    ft.Text("Drag and drop nodes to organize your plot.", color="#9E9E9E"),
                    ft.ElevatedButton(
                        text="Add Node",
                        icon=ft.Icons.ADD,
                        bgcolor="#64B5F6",
                        color="#FFFFFF",
                        on_click=add_node
                    ),
                    ft.Container(
                        content=ft.Stack(
                            node_controls,
                            expand=True
                        ),
                        expand=True,
                        border=ft.border.all(1, "#3A4D60"),
                        border_radius=5,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE, # Clip content outside bounds
                        scroll=ft.ScrollMode.AUTO # Enable scrolling
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=20
        )

    # --- Timeline Event Detail View ---
    def create_timeline_event_detail_view(event: TimelineEvent, timeline_events_list_view, timeline_event_detail_container, select_timeline_event):
        name_field = ft.TextField(label="Event Name", value=event.name, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        description_field = ft.TextField(label="Description", value=event.description, multiline=True, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        timestamp_field = ft.TextField(label="Timestamp", value=event.timestamp, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_characters_field = ft.TextField(label="Associated Characters (comma-separated IDs)", value=", ".join(event.associatedCharacters), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_locations_field = ft.TextField(label="Associated Locations (comma-separated IDs)", value=", ".join(event.associatedLocations), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        associated_items_field = ft.TextField(label="Associated Items (comma-separated IDs)", value=", ".join(event.associatedItems), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        clues_generated_field = ft.TextField(label="Clues Generated (comma-separated IDs)", value=", ".join(event.cluesGenerated), text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")
        reveals_truth_field = ft.Checkbox(label="Reveals Truth", value=event.revealsTruth, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        reveals_lie_field = ft.Checkbox(label="Reveals Lie", value=event.revealsLie, check_color="#64B5F6", label_style=ft.TextStyle(color="#FFFFFF"))
        lie_debunked_field = ft.TextField(label="Lie Debunked ID", value=event.lieDebunked, text_style=ft.TextStyle(color="#FFFFFF"), label_style=ft.TextStyle(color="#9E9E9E"), border_color="#3A4D60", focused_border_color="#64B5F6", filled=True, fill_color="#3A4D60")

        def save_timeline_event_details(e):
            event.name = name_field.value
            event.description = description_field.value
            event.timestamp = timestamp_field.value
            event.associatedCharacters = [c.strip() for c in associated_characters_field.value.split(',') if c.strip()]
            event.associatedLocations = [l.strip() for l in associated_locations_field.value.split(',') if l.strip()]
            event.associatedItems = [i.strip() for i in associated_items_field.value.split(',') if i.strip()]
            event.cluesGenerated = [cg.strip() for cg in clues_generated_field.value.split(',') if cg.strip()]
            event.revealsTruth = reveals_truth_field.value
            event.revealsLie = reveals_lie_field.value
            event.lieDebunked = lie_debunked_field.value

            timeline_events_list_view.controls.clear()
            for event_obj in timeline_events:
                timeline_events_list_view.controls.append(ft.GestureDetector(content=ft.Text(event_obj.name, color="#FFFFFF"), on_tap=lambda e, event=event_obj: select_timeline_event(event))) # Use GestureDetector
            save_timeline_events()
            run_validation()
            page.update()

        def delete_timeline_event(e):
            timeline_events.remove(event)
            timeline_events_list_view.controls.clear()
            for event_obj in timeline_events:
                timeline_events_list_view.controls.append(ft.GestureDetector(content=ft.Text(event_obj.name, color="#FFFFFF"), on_tap=lambda e, event=event_obj: select_timeline_event(event))) # Use GestureDetector
            timeline_event_detail_container.content = ft.Column([ft.Text("Select a timeline event to view details", color="#9E9E9E")])
            save_timeline_events()
            run_validation()
            page.update()

        return ft.Column(
            [
                ft.Text(f"Timeline Event Details: {event.name}", color="#FFFFFF", size=20),
                name_field,
                description_field,
                timestamp_field,
                associated_characters_field,
                associated_locations_field,
                associated_items_field,
                clues_generated_field,
                reveals_truth_field,
                reveals_lie_field,
                lie_debunked_field,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Save Changes",
                            icon=ft.Icons.SAVE,
                            bgcolor="#64B5F6",
                            color="#FFFFFF",
                            on_click=save_timeline_event_details
                        ),
                        ft.ElevatedButton(
                            text="Delete Event",
                            icon=ft.Icons.DELETE,
                            bgcolor="#FF5252", # Red for delete
                            color="#FFFFFF",
                            on_click=delete_timeline_event
                        ),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    def create_timeline_view():
        timeline_name_input = ft.TextField(
            label="Event Name",
            hint_text="Enter event name",
            width=300,
            text_style=ft.TextStyle(color="#FFFFFF"),
            label_style=ft.TextStyle(color="#9E9E9E"),
            border_color="#3A4D60",
            focused_border_color="#64B5F6", # Light blue for focus
            filled=True,
            fill_color="#3A4D60",
        )

        # Populate on load
        timeline_events_list_view.controls.clear()
        for event_obj in timeline_events:
            timeline_events_list_view.controls.append(ft.GestureDetector(content=ft.Text(event_obj.name, color="#FFFFFF"), on_tap=lambda e, event=event_obj: select_timeline_event(event)))

        def add_timeline_event(e):
            if timeline_name_input.value:
                new_event = TimelineEvent(
                    id=str(uuid.uuid4()),
                    name=timeline_name_input.value,
                    description="", # Placeholder
                    timestamp="", # Placeholder
                )
                timeline_events.append(new_event)
                timeline_events_list_view.controls.append(ft.GestureDetector(content=ft.Text(new_event.name, color="#FFFFFF"), on_tap=lambda e, event=new_event: select_timeline_event(event))) # Use GestureDetector
                timeline_name_input.value = ""
                save_timeline_events()
                run_validation()
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gamified Timeline Editor", color="#FFFFFF", size=20),
                    ft.Text("List of timeline events and their details will go here.", color="#9E9E9E"),
                    ft.Row(
                        [
                            timeline_name_input,
                            ft.ElevatedButton(
                                text="Add Event",
                                icon=ft.Icons.ADD,
                                bgcolor="#64B5F6",
                                color="#FFFFFF",
                                on_click=add_timeline_event
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=timeline_events_list_view,
                                expand=1,
                                border=ft.border.all(1, "#3A4D60"),
                                border_radius=5,
                                padding=ft.padding.all(10)
                            ),
                            timeline_event_detail_container,
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

    # Load all data on startup
    load_characters()
    load_locations()
    load_factions()
    load_districts()
    load_items()
    load_clues() # Load clues on startup
    load_case_meta()
    load_lore_history()
    load_bulletin_board_nodes()
    load_timeline_events()

    # Populate sample data if no characters exist (simple check to avoid overwriting existing data)
    if not characters:
        populate_sample_data()

    # Run initial validation
    run_validation()

    # --- Main Content Area ---
    main_content_area = ft.Column([create_characters_view()], expand=True)

    # --- Secondary Navigation ---
    secondary_nav_column = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.PERSON, tooltip="Characters", on_click=lambda e: update_main_content(create_characters_view())),
            ft.IconButton(icon=ft.Icons.LOCATION_ON, tooltip="Locations", on_click=lambda e: update_main_content(create_locations_view())),
            ft.IconButton(icon=ft.Icons.GROUPS, tooltip="Factions", on_click=lambda e: update_main_content(create_factions_view())),
            ft.IconButton(icon=ft.Icons.HOME, tooltip="Districts", on_click=lambda e: update_main_content(create_districts_view())),
            ft.IconButton(icon=ft.Icons.WORK, tooltip="Items", on_click=lambda e: update_main_content(create_items_view())),
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
                ft.IconButton(icon=ft.Icons.HOME, tooltip="Districts", on_click=lambda e: update_main_content(create_districts_view())),
                ft.IconButton(icon=ft.Icons.WORK, tooltip="Items", on_click=lambda e: update_main_content(create_items_view())),
                ft.IconButton(icon=ft.Icons.HISTORY, tooltip="Lore & History", on_click=lambda e: update_main_content(create_lore_history_view())),
            ])
            update_main_content(create_characters_view()) # Default to Characters view
        elif e.control.selected_index == 1:  # Case Builder
            secondary_nav_column.controls.clear()
            secondary_nav_column.controls.extend([
                ft.IconButton(icon=ft.Icons.DESCRIPTION, tooltip="Case Metadata", on_click=lambda e: update_main_content(create_case_meta_view())),
                ft.IconButton(icon=ft.Icons.DASHBOARD, tooltip="Bulletin Board", on_click=lambda e: update_main_content(create_bulletin_board_view())),
                ft.IconButton(icon=ft.Icons.ACCESS_TIME, tooltip="Timeline", on_click=lambda e: update_main_content(create_timeline_view())),
                ft.IconButton(icon=ft.Icons.LIGHTBULB, tooltip="Clues", on_click=lambda e: update_main_content(create_clues_view())),
            ])
            update_main_content(create_case_meta_view()) # Default to Case Metadata view
        page.update()

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
                validator_panel # Add validator panel to the right
            ],
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)