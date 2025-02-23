from dataclasses import dataclass
from typing import List, Optional, Dict
from .enums import Resource, CardType, ScienceSymbol

# The effect will hold a string that will be parsed by the game engine
# This allows flexibility and compactness in the card data

@dataclass
class Card:
    name: str
    type: CardType
    age: int
    min_players: int
    cost: Dict[Resource, int]
    chain_to: Optional[List[str]]
    effect: str

@dataclass
class WonderStage:
    cost: Dict[Resource, int]
    effect: str

@dataclass
class Wonder:
    name: str
    resource: Resource
    stages: List[WonderStage]