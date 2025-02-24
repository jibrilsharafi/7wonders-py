from src.core.types import Card
from src.game.player import Player
from src.core.enums import Action


class Move:
    def __init__(self, player: Player, action: Action, card: Card):
        self.player = player
        self.action = action
        self.card = card
