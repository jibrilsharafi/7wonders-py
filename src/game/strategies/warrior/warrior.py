import logging

from src.core.enums import Action
from src.game.move import Move
from src.game.player import GameView, Player, PlayerStrategy, get_valid_moves

logger = logging.getLogger(__name__)


class WarriorStrategy(PlayerStrategy):
    """Prioritizes military tokens"""

    def choose_move(self, player: Player, game_view: GameView) -> Move:

        player_view = player.get_player_view()
        left_neighbor = game_view.get_left_neighbor(player_view)
        right_neighbor = game_view.get_right_neighbor(player_view)

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
