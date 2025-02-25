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
    PLAY = auto()
    WONDER = auto()
    DISCARD = auto()


CARD_TYPE_MAP = {
    "raw_material": CardType.RAW_MATERIAL,
    "manufactured_good": CardType.MANUFACTURED_GOOD,
    "civilian": CardType.CIVILIAN,
    "commercial": CardType.COMMERCIAL,
    "military": CardType.MILITARY,
    "scientific": CardType.SCIENTIFIC,
    "guild": CardType.GUILD,
}


RESOURCE_MAP = {
    "W": Resource.WOOD,
    "S": Resource.STONE,
    "O": Resource.ORE,
    "B": Resource.BRICK,
    "F": Resource.GLASS,  # F for "fire" (glass) to avoid conflict with G for "gear"
    "P": Resource.PAPYRUS,
    "L": Resource.LOOM,
    "$": Resource.COIN,
}


SCIENCE_SYMBOL_MAP = {
    "T": ScienceSymbol.TABLET,
    "C": ScienceSymbol.COMPASS,
    "G": ScienceSymbol.GEAR,
}
