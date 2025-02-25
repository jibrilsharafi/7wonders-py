import logging
from typing import List

from src.core.enums import Action
from src.game.move import Moves
from src.game.player import Player
from src.game.state import GameState
from src.game.strategy import PlayerStrategy
from src.utils.generic import get_left_neighbor, get_right_neighbor, get_valid_moves

logger = logging.getLogger(__name__)


class SimpleStrategy(PlayerStrategy):
    """Prioritizes wonder building, then playing cards, then discarding"""

    def choose_move(self, player: Player, game_state: GameState) -> Move:
        LIST_PRIORITY: List[Action] = [Action.WONDER, Action.PLAY, Action.DISCARD]

        left_neighbor = get_left_neighbor(game_state.all_players, player)
        right_neighbor = get_right_neighbor(game_state.all_players, player)

        valid_moves = get_valid_moves(player, left_neighbor, right_neighbor)

        for action in LIST_PRIORITY:
            # Just return the first valid move we find
            for move in valid_moves:
                if move.action == action:
                    return move

        raise Exception("No valid moves found")
