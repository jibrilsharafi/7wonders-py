from abc import ABC, abstractmethod

from src.game.player import Player
from src.game.move import Move
from src.game.state import GameState


class PlayerStrategy(ABC):
    @abstractmethod
    def choose_move(self, player: Player, game_state: GameState) -> Move:
        """
        Choose next move based only on visible information through PlayerView.
        The view provides:
        - Own cards, resources and wonder state
        - Visible neighbor information
        - Valid moves calculation
        - Military strength evaluation
        """
        pass
