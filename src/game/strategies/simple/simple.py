import logging
from typing import List

from src.core.enums import Action
from src.game.move import Move
from src.game.player import GameView, Player, PlayerStrategy, get_valid_moves

logger = logging.getLogger(__name__)


class SimpleStrategy(PlayerStrategy):
    """Prioritizes wonder building, then playing cards, then discarding"""

    def choose_move(self, player: Player, game_view: GameView) -> Move:
        LIST_PRIORITY: List[Action] = [Action.WONDER, Action.PLAY, Action.DISCARD]

        player_view = player.get_player_view()
        left_neighbor = game_view.get_left_neighbor(player_view)
        right_neighbor = game_view.get_right_neighbor(player_view)

        valid_moves = get_valid_moves(player, left_neighbor, right_neighbor)

        for action in LIST_PRIORITY:
            # Just return the first valid move we find
            for move in valid_moves:
                if move.action == action:
                    return move

        raise Exception("No valid moves found")
