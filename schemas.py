# schemas.py
# This file is the single source of truth for all data structures,
# meticulously updated to match the 'Agency of Ellen Kruger: Complete Data Bible' PDF.

from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict

# --- Type Definitions for Constrained Values ---

CaseStatus = Literal["unsolved", "solved", "closed"]
ClueType = Literal["Physical Evidence", "Digital Trail", "Testimony", "Forensic Report", "Document"]
Relevance = Literal["Motive", "Means", "Opportunity", "Red Herring", "Contextual"]
DiscoveryMethodType = Literal["Initial", "Observation", "Interview", "Unlocked"]
ItemType = Literal["Tool", "Consumable", "KeyItem"]
RuleCategory = Literal["Ground Truth", "Referential Integrity", "Logical Consistency", "Playability"]
RuleSeverity = Literal["Error", "Warning"]

# --- Nested Schema Components ---

@dataclass
class GroundTruth:
    """Defines the objective solution to the case."""
    victimId: str
    perpetratorId: str
    motiveClueId: str
    meansClueId: str
    opportunityClueId: str

@dataclass
class Event:
    """Defines a single event in the case's chronological timeline."""
    eventId: int
    description: str
    timestamp: str  # ISO 8601 format
    locationId: Optional[str] = None
    involvedCharacterIds: List[str] = field(default_factory=list)

@dataclass
class InterviewTopic:
    characterId: str
    topicId: str

@dataclass
class Unlocks:
    """Defines what a clue reveals to the player."""
    clueIds: List[str] = field(default_factory=list)
    interviewTopics: List[InterviewTopic] = field(default_factory=list)

@dataclass
class DiscoveryMethod:
    """Defines how a clue is revealed to the player."""
    type: DiscoveryMethodType
    locationId: Optional[str] = None  # For 'Observation'
    characterId: Optional[str] = None # For 'Interview'
    topicId: Optional[str] = None     # For 'Interview'

@dataclass
class Clue:
    clueId: str
    name: str
    description: str
    type: ClueType
    relevance: Relevance
    discoveryMethod: DiscoveryMethod
    imageUrl: Optional[str] = None
    isLie: bool = False
    debunkedBy: Optional[str] = None # clueId of the clue that proves this is a lie
    unlocks: Optional[Unlocks] = None

@dataclass
class CoreIdentity:
    fullName: str
    age: int
    employment: str
    imageUrl: Optional[str] = None

@dataclass
class PsychologicalProfile:
    personalityArchetype: str
    motivations: List[str] = field(default_factory=list)

@dataclass
class SystemFacing:
    voiceModelArchetype: str
    knowledgeAreas: List[str] = field(default_factory=list)
    murderLikelihood: Optional[float] = None
    victimLikelihood: Optional[float] = None

@dataclass
class Character:
    characterId: str
    coreIdentity: CoreIdentity
    psychologicalProfile: PsychologicalProfile
    systemFacing: SystemFacing

@dataclass
class LocationCoreDetails:
    name: str
    description: str
    type: str # e.g., "Apartment", "Office", "Warehouse"
    imageUrl: Optional[str] = None

@dataclass
class Geographic:
    district: str

@dataclass
class Systemic:
    securityLevel: int
    factionOwner: str # Should be a factionId
    informationValue: int

@dataclass
class Location:
    locationId: str
    coreDetails: LocationCoreDetails
    geographic: Geographic
    systemic: Systemic

# --- Top-Level Schemas ---

@dataclass
class CaseFile:
    """A schema for validating a single, self-contained case file."""
    caseId: str
    title: str
    synopsis: str
    status: CaseStatus
    difficulty: int # 1-5
    groundTruth: GroundTruth
    locations: List[Location]
    characters: List[Character]
    clues: List[Clue]
    eventChain: List[Event]
    imageUrl: Optional[str] = None

@dataclass
class Faction:
    """A schema for defining a major faction."""
    factionId: str
    name: str
    archetype: str
    description: str
    ideology: Dict
    assets: Dict
    relationships: Dict
    imageUrl: Optional[str] = None

@dataclass
class Item:
    """A schema for defining a tangible item."""
    itemId: str
    name: str
    description: str
    type: ItemType
    usage: Dict
    imageUrl: Optional[str] = None

@dataclass
class Lore:
    """A schema for defining an in-game lore document."""
    loreId: str
    title: str
    type: str
    source: str
    content: List[str] # Changed to always be a list for consistency
    imageUrl: Optional[str] = None
    unlocks: Optional[Dict] = None

@dataclass
class PlayerProgress:
    """A schema for the player's save file."""
    playerState: Dict
    worldKnowledge: Dict
    caseHistory: List[Dict]
    activeCase: Optional[Dict] = None

@dataclass
class VerifierRule:
    ruleId: str
    category: RuleCategory
    severity: RuleSeverity
    description: str
    suggestion: str

@dataclass
class VerifierRuleSet:
    rules: List[VerifierRule]
