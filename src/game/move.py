from dataclasses import dataclass

from src.core.enums import Action
from src.core.types import Card
from src.game.player import Player


@dataclass
class Move:
    player: Player
    action: Action
    card: Card
