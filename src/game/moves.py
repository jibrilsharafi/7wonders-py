from src.core.types import Card, Resource
from src.game.player import Player
from src.core.enums import Action


class Move:
    def __init__(self, player: Player, action: Action, card: Card):
        self.player = player
        self.action = action
        self.card = card

    @property
    def shields(self) -> int:
        """Get number of shields this move would provide"""
        if self.action == Action.PLAY and "M" in self.card.effect:
            return self.card.effect.count("M")
        return 0