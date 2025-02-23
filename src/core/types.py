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

@dataclass
class Score:
    military: int = 0
    treasury: int = 0
    wonders: int = 0
    civilian: int = 0
    scientific: int = 0
    commercial: int = 0
    guilds: int = 0
    
    @property
    def total(self) -> int:
        return (self.military + self.treasury + self.wonders +
                self.civilian + self.scientific + self.commercial +
                self.guilds)