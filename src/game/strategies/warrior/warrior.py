from src.game.strategy import PlayerStrategy
from src.game.player_view import PlayerView
from src.game.moves import Move
from src.core.enums import Action


class WarriorStrategy(PlayerStrategy):
    """Prioritizes military tokens"""

    def choose_move(self, view: PlayerView) -> Move:
        valid_moves = view.get_valid_moves()
        best_move = valid_moves[0]
        max_shields = 0

        for move in valid_moves:
            shields = 0
            if move.action == Action.PLAY:
                shields = move.card.effect.count("M")
            elif move.action == Action.WONDER:
                stage_effect = view.wonder.stages[view.stages_built].effect
                shields = stage_effect.count("M")

            if shields > max_shields:
                max_shields = shields
                best_move = move

        return best_move
