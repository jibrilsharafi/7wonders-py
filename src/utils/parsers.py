from enum import Enum
from ..core.enums import Resource, CardType, ScienceSymbol


class CardsCsvHeaders(Enum):
    AGE = "age"
    MIN_PLAYERS = "min_players"
    NAME = "name"
    TYPE = "type"
    COST = "cost"
    CHAIN_TO = "chain_to"
    EFFECT = "effect"


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
    "F": Resource.GLASS, # F for "fire" (glass)
    "P": Resource.PAPYRUS,
    "L": Resource.LOOM,
}


SCIENCE_SYMBOL_MAP = {
    "T": ScienceSymbol.TABLET,
    "C": ScienceSymbol.COMPASS,
    "G": ScienceSymbol.GEAR
}
