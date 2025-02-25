# src/game/strategies/simple.py
from src.game.strategy import PlayerStrategy
from src.game.player_view import PlayerView
from src.game.moves import Move
from src.core.enums import Action
from typing import List


class SimpleStrategy(PlayerStrategy):
    """Prioritizes wonder building, then playing cards, then discarding"""

    def choose_move(self, view: PlayerView) -> Move:
        LIST_PRIORITY: List[Action] = [Action.WONDER, Action.PLAY, Action.DISCARD]

        valid_moves = view.get_valid_moves()

        for action in LIST_PRIORITY:
            for move in valid_moves:
                if move.action == action:
                    return move

        raise Exception("No valid moves found")
