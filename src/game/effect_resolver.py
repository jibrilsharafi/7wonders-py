from src.game.player import Player
from src.game.state import GameState
from src.core.enums import CardType, CARD_TYPE_MAP
from src.core.types import Card


class EffectResolver:
    """Handles resolution of card and wonder effects"""

    def __init__(self, game_state: GameState):
        self._game_state = game_state

    def _apply_card_effects(self, player: Player, card: Card) -> None:
        """Apply card effects when played. Only instantaneous ones"""
        effect = card.effect

        if card.type == CardType.COMMERCIAL:
            if "$" in effect:
                coins_multiplier = effect.count("$")
                if "{" in effect:
                    bracket_content = effect.split("{")[1].split("}")[0]
                    if bracket_content == "wonder":
                        player.add_coins(coins_multiplier * player.stages_built)
                        return

                    total_cards = 0
                    required_card_type = CARD_TYPE_MAP[bracket_content]

                    if (
                        "v" in bracket_content or "<" not in bracket_content
                    ):  # Either only self or self and neighbors
                        total_cards += player.count_cards_by_type(required_card_type)

                    if "<" in bracket_content:
                        left_neighbor = player.get_left_neighbor(self.players)
                        total_cards += left_neighbor.total_cards_of_type(
                            required_card_type
                        )

                        right_neighbor = player.get_right_neighbor(self.players)
                        total_cards += right_neighbor.total_cards_of_type(
                            required_card_type
                        )

                    player.add_coins(coins_multiplier * total_cards)

    def _apply_wonder_effects(self, player: Player, effect: str) -> None:
        """Apply wonder stage effects when built"""
        if "$" in effect:
            # TODO: get moneyyy
            pass
        elif "_" in effect:
            # TODO: implement custom effects
            pass
