from abc import ABC, abstractmethod
from src.game.player_view import PlayerView
from src.game.moves import Move


class PlayerStrategy(ABC):
    @abstractmethod
    def choose_move(self, view: PlayerView) -> Move:
        """
        Choose next move based only on visible information through PlayerView.
        The view provides:
        - Own cards, resources and wonder state
        - Visible neighbor information
        - Valid moves calculation
        - Military strength evaluation
        """
        pass
