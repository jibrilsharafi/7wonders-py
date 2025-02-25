from src.game.player import Player
from src.core.enums import CardType, CARD_TYPE_MAP
from src.core.types import Card
import logging

logger = logging.getLogger(__name__)


def apply_card_effects(player: Player, card: Card, left_neighbor: Player, right_neighbor: Player) -> None:
    """Apply card effects when played. Only instantaneous ones"""
    effect = card.effect

    if card.type == CardType.COMMERCIAL:
        logger.debug(f"Applying commercial card '{card.name}' effect: {effect}")
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

                if "<" in bracket_content: # ALl cards with < also have >
                    total_cards += left_neighbor.count_cards_by_type(required_card_type)

                    total_cards += right_neighbor.count_cards_by_type(
                        required_card_type
                    )

                player.add_coins(coins_multiplier * total_cards)


def apply_wonder_effects(player: Player, effect: str) -> None:
    """Apply wonder stage effects when built"""
    if "$" in effect:
        # TODO: get moneyyy
        pass
    elif "_" in effect:
        # TODO: implement custom effects
        pass
