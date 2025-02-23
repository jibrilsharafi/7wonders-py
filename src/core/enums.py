from enum import Enum, auto


class Resource(Enum):
    WOOD = auto()
    STONE = auto()
    ORE = auto()
    BRICK = auto()
    GLASS = auto()
    PAPYRUS = auto()
    LOOM = auto()
    COIN = auto()


class ScienceSymbol(Enum):
    TABLET = auto()
    COMPASS = auto()
    GEAR = auto()


class CardType(Enum):
    RAW_MATERIAL = auto()
    MANUFACTURED_GOOD = auto()
    CIVILIAN = auto()
    COMMERCIAL = auto()
    MILITARY = auto()
    SCIENTIFIC = auto()
    GUILD = auto()


class Action(Enum):
    PLAY_CARD = auto()
    BUILD_WONDER = auto()
    DISCARD = auto()
