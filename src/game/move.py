from dataclasses import dataclass

from src.core.enums import Action
from src.core.types import Card


@dataclass
class Move:
    player_name: str
    action: Action
    card: Card
