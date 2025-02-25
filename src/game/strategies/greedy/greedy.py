from src.game.strategy import PlayerStrategy
from src.game.player_view import PlayerView
from src.game.moves import Move


class GreedyStrategy(PlayerStrategy):
    """Prioritizes wonder building, then playing cards, then discarding"""

    def choose_move(self, view: PlayerView) -> Move:
        # TODO: Implement this method
        raise NotImplementedError("GreedyStrategy.choose_move")
