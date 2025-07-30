# schemas.py
# This file is the single source of truth for all data structures,
# meticulously updated to match the 'Case builder fields.pdf' document.

from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict

# --- Type Definitions for Constrained Values ---

WealthClass = Literal["Old Money Rich", "New Money Rich", "Business Person", "Working Stiff", "Poor", "Transient"]
PopulationDensity = Literal["Sparse", "Moderate", "Dense", "Crowded"]
DangerLevel = Literal[1, 2, 3, 4, 5] # 1: Safe -> 5: Deadly
AccessibilityLevel = Literal["Public", "Semi-Private", "Private", "Restricted"]
FactionInfluence = Literal["Local", "District-wide", "City-wide", "Regional", "Global"]
Gender = Literal["Male", "Female", "Nonbinary", "Trans Man", "Trans Woman", "Unknown", "Unspecified"]
Alignment = Literal["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"]
ItemCondition = Literal["New", "Good", "Used", "Worn", "Damaged", "Broken"]
CluePotential = Literal["None", "Low", "Medium", "High", "Critical"]
NarrativeViewpoint = Literal["First-Person", "Third-Limited (Sleuth)", "Third-Limited (Multiple)", "Omniscient", "Storyteller Omniscient", "Epistolary"]
NarrativeTense = Literal["Past", "Present"]
RedHerringType = Literal["Decoy Suspect", "Misleading Object", "False Alibi", "Misleading Dialogue"]
PresentationMethod = Literal["Dialogue", "Setting/Description", "Character Action", "Introspection"]
KnowledgeLevel = Literal["Sleuth Only", "Reader Only", "Both", "Neither (Off-Page)"]

# --- World Builder Schemas ---

@dataclass
class District:
    """Defines a district in the game world."""
    district_id: str = field(default_factory=str) # Auto-generated unique identifier
    district_name: str = ""
    description: str = ""
    wealth_class: Optional[WealthClass] = None
    atmosphere: str = ""
    key_locations: List[str] = field(default_factory=list) # List of location_id
    population_density: Optional[PopulationDensity] = None
    notable_features: List[str] = field(default_factory=list)
    dominant_faction: Optional[str] = None # faction_id

@dataclass
class Faction:
    """Defines a faction in the game world."""
    faction_id: str = field(default_factory=str) # Auto-generated unique identifier
    name: str = ""
    archetype: str = ""
    description: str = ""
    ideology: str = ""
    headquarters: Optional[str] = None # location_id
    resources: List[str] = field(default_factory=list)
    image: Optional[str] = None # Path to image
    ally_factions: List[str] = field(default_factory=list) # List of faction_id
    enemy_factions: List[str] = field(default_factory=list) # List of faction_id
    members: List[str] = field(default_factory=list) # List of character_id
    influence: Optional[FactionInfluence] = None
    public_perception: str = ""

@dataclass
class Item:
    """Defines a tangible item in the game world."""
    item_id: str = field(default_factory=str) # Auto-generated unique identifier
    name: str = ""
    image: Optional[str] = None # Path to image
    type: str = ""
    description: str = ""
    use: List[str] = field(default_factory=list)
    possible_means: bool = False
    possible_motive: bool = False
    possible_opportunity: bool = False
    default_location: Optional[str] = None # location_id
    default_owner: Optional[str] = None # character_id
    significance: Optional[str] = None
    clue_potential: CluePotential = "None"
    value: str = ""
    condition: Optional[ItemCondition] = None
    unique_properties: List[str] = field(default_factory=list)

@dataclass
class Character:
    """Defines a character in the game world."""
    character_id: str = field(default_factory=str) # Auto-generated unique identifier
    full_name: str = ""
    alias: str = ""
    age: Optional[int] = None
    gender: Optional[Gender] = None
    employment: str = ""
    biography: str = ""
    image: Optional[str] = None # Path to image
    faction: Optional[str] = None # faction_id
    wealth_class: Optional[WealthClass] = None
    district: Optional[str] = None # district_id
    allies: List[str] = field(default_factory=list) # List of character_id
    enemies: List[str] = field(default_factory=list) # List of character_id
    items: List[str] = field(default_factory=list) # List of item_id
    archetype: str = ""
    personality: str = ""
    values: List[str] = field(default_factory=list)
    flaws_handicaps_limitations: List[str] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)
    characteristics: List[str] = field(default_factory=list)
    alignment: Optional[Alignment] = None
    motivations: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    voice_model: str = ""
    dialogue_style: str = ""
    expertise: List[str] = field(default_factory=list)
    honesty: float = 0.5 # 0.0 to 1.0
    victim_likelihood: float = 0.5 # 0.0 to 1.0
    killer_likelihood: float = 0.5 # 0.0 to 1.0
    portrayal_notes: str = ""

@dataclass
class Sleuth(Character):
    """Extends Character schema for the main sleuth."""
    city: str = ""
    relationships: List[str] = field(default_factory=list) # List of character_id
    nemesis: List[str] = field(default_factory=list) # List of character_id
    primary_arc: str = ""

@dataclass
class Location:
    """Defines a location in the game world."""
    location_id: str = field(default_factory=str) # Auto-generated unique identifier
    name: str = ""
    type: str = ""
    description: str = ""
    district: Optional[str] = None # district_id
    owning_faction: Optional[str] = None # faction_id
    danger_level: Optional[DangerLevel] = None
    population: Optional[int] = None
    image: Optional[str] = None # Path to image
    key_characters: List[str] = field(default_factory=list) # List of character_id
    associated_items: List[str] = field(default_factory=list) # List of item_id
    accessibility: Optional[AccessibilityLevel] = None
    hidden: bool = False
    clues: List[str] = field(default_factory=list) # List of clue_id
    internal_logic_notes: str = ""


# --- Case Builder Schemas ---

@dataclass
class Clue:
    """Defines a clue within a case."""
    clue_id: str = field(default_factory=str) # Auto-generated unique identifier
    critical_clue: bool = False
    character_implicated: Optional[str] = None # character_id
    red_herring: bool = False
    red_herring_type: Optional[RedHerringType] = None
    mechanism_of_misdirection: str = ""
    debunking_clue: Optional[str] = None # clue_id
    source: str = ""
    clue_summary: str = ""
    discovery_path: List[str] = field(default_factory=list)
    presentation_method: List[PresentationMethod] = field(default_factory=list)
    knowledge_level: Optional[KnowledgeLevel] = None
    dependencies: List[str] = field(default_factory=list) # List of clue_id
    required_actions_for_discovery: List[str] = field(default_factory=list)
    reveals_unlocks: List[str] = field(default_factory=list) # List of clue_id, location_id, item_id, character_id
    associated_item: Optional[str] = None # item_id
    associated_location: Optional[str] = None # location_id
    associated_character: Optional[str] = None # character_id

@dataclass
class InterviewAnswer:
    """Defines a single answer in an interview."""
    answer_id: str = field(default_factory=str) # Auto-generated unique identifier
    answer: str = ""
    is_lie: bool = False
    debunking_clue: Optional[str] = None # clue_id (mandatory if is_lie)
    is_clue: bool = False
    clue_id: Optional[str] = None # clue_id (mandatory if is_clue)
    has_item: Optional[str] = None # item_id

@dataclass
class InterviewQuestion:
    """Defines a single question and its answer in an interview."""
    question_id: str = field(default_factory=str) # Auto-generated unique identifier
    question: str = ""
    answer: InterviewAnswer = field(default_factory=InterviewAnswer)

@dataclass
class CaseSuspect:
    """Defines a key suspect in the case."""
    character_id: str
    interviews: List[InterviewQuestion] = field(default_factory=list) # Up to 6

@dataclass
class CaseWitness(CaseSuspect):
    """Defines a witness at a location, who can also be interviewed."""
    pass # Inherits from CaseSuspect, structure is identical for interviews

@dataclass
class CaseLocation:
    """Defines a relevant location in the case."""
    location_id: str
    location_clues: List[str] = field(default_factory=list) # List of clue_id
    witnesses: List[CaseWitness] = field(default_factory=list)

@dataclass
class CaseMeta:
    """Defines the core metadata and solution for the case."""
    victim: Optional[str] = None # character_id
    culprit: Optional[str] = None # character_id
    crime_scene: Optional[str] = None # location_id
    murder_weapon: Optional[str] = None # item_id
    murder_weapon_hidden: bool = False
    means_clue: Optional[str] = None # clue_id
    motive_clue: Optional[str] = None # clue_id
    opportunity_clue: Optional[str] = None # clue_id
    red_herring_clues: List[str] = field(default_factory=list) # List of clue_id
    narrative_viewpoint: Optional[NarrativeViewpoint] = None
    narrative_tense: Optional[NarrativeTense] = None
    core_mystery_solution_details: str = ""
    ultimate_reveal_scene_description: str = ""
    opening_monologue: str = ""
    successful_denouement: str = ""
    failed_denouement: str = ""

# --- Top-Level Container ---

@dataclass
class CaseFile:
    """A schema for a single, self-contained case file, combining world and case data."""
    case_meta: CaseMeta = field(default_factory=CaseMeta)
    key_suspects: List[CaseSuspect] = field(default_factory=list) # Up to 10
    locations: List[CaseLocation] = field(default_factory=list) # Up to 10
    clues: List[Clue] = field(default_factory=list)

@dataclass
class WorldData:
    """A container for all the foundational world-building elements."""
    districts: Dict[str, District] = field(default_factory=dict)
    locations: Dict[str, Location] = field(default_factory=dict)
    factions: Dict[str, Faction] = field(default_factory=dict)
    characters: Dict[str, Character] = field(default_factory=dict)
    items: Dict[str, Item] = field(default_factory=dict)
    sleuth: Sleuth = field(default_factory=Sleuth)
