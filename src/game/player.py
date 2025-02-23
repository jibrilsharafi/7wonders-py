from typing import Dict, List, Tuple
from ..core.types import Card, Wonder
from ..core.enums import Resource

class Player:
    def __init__(self, name: str, wonder: Wonder):
        self.name: str = name
        self.wonder: Wonder = wonder
        self.cards: List[Card] = []
        self.coins: int = 3
        self.military_tokens: int = 0
        self.stages_built: int = 0
        self.resources: Dict[Resource, int] = {wonder.resource: 1}