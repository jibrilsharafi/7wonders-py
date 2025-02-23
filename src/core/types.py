from dataclasses import dataclass
from typing import List, Optional
from .enums import Resource, CardType, ScienceSymbol

# The effect will hold a string that will be parsed by the game engine
# This allows flexibility and compactness in the card data

@dataclass
class Card:
    name: str
    type: CardType
    age: int
    min_players: int
    cost: str
    chain_to: Optional[str]
    effect: str

@dataclass
class WonderStage:
    cost: str
    effect: str

@dataclass
class Wonder:
    name: str
    resource: Resource
    stages: List[WonderStage]