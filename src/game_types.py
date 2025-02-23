import enum
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional


class Resource(Enum):
    WOOD = auto()
    STONE = auto()
    ORE = auto()
    BRICK = auto()
    GLASS = auto()
    PAPYRUS = auto()
    LOOM = auto()


class CardType(Enum):
    RAW_MATERIAL = auto()  # Brown cards
    MANUFACTURED_GOOD = auto()  # Grey cards
    CIVILIAN = auto()  # Blue cards
    COMMERCIAL = auto()  # Yellow cards
    MILITARY = auto()  # Red cards
    SCIENTIFIC = auto()  # Green cards
    GUILD = auto()  # Purple cards


class ScienceSymbol(Enum):
    TABLET = auto()
    COMPASS = auto()
    GEAR = auto()


class Age(Enum):
    ONE = auto()
    TWO = auto()
    THREE = auto()


class Action(Enum):
    PLAY_CARD = auto()
    BUILD_WONDER = auto()
    DISCARD = auto()


@dataclass
class CardCost:
    resources: Dict[Resource, int]
    coins: int = 0


@dataclass
class Card:
    name: str
    type: CardType
    age: Age
    cost: CardCost
    min_players: int
    chain_builds: List[str]  # Names of cards that can be built for free
    resources_produced: Dict[Resource, int]
    effect: str
    victory_points: int
    military_shields: int
    science_symbol: Optional[ScienceSymbol]


@dataclass
class WonderStage:
    cost: Dict[Resource, int]
    victory_points: int
    benefits: Dict[str, int]  # TODO: Define benefits better as they can vary


@dataclass
class Wonder:
    name: str
    starting_resource: Resource
    stages: List[WonderStage]
