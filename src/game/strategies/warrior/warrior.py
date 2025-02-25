import logging

from src.core.enums import Action
from src.game.move import Move
from src.game.player import Player
from src.game.state import GameState
from src.game.strategy import PlayerStrategy
from src.utils.generic import get_left_neighbor, get_right_neighbor, get_valid_moves

logger = logging.getLogger(__name__)


class WarriorStrategy(PlayerStrategy):
    """Prioritizes military tokens"""

    def choose_move(self, player: Player, game_state: GameState) -> Move:
        left_neighbor = get_left_neighbor(game_state.all_players, player)
        right_neighbor = get_right_neighbor(game_state.all_players, player)

        valid_moves = get_valid_moves(player, left_neighbor, right_neighbor)

        best_move = valid_moves[0]
        max_shields = 0

        for move in valid_moves:
            shields = 0
            if move.action == Action.PLAY:
                shields = move.card.effect.count("M")
            elif move.action == Action.WONDER:
                stage_effect = player.get_current_wonder_stage_to_be_built().effect
                shields = stage_effect.count("M")

            if shields > max_shields:
                max_shields = shields
                best_move = move

        return best_move
