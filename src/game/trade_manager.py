import logging
from typing import Dict

from src.core.constants import BASE_TRADING_COST, MAXIMUM_TRADING_RESOURCES
from src.core.types import Resource
from src.game.player import Player

logger = logging.getLogger(__name__)


def pay_costs(
    player: Player,
    cost: Dict[Resource, int],
    left_neighbor: Player,
    right_neighbor: Player,
) -> None:
    """Handle payment of costs, including trading with neighbors"""

    resources_required_left = 0
    resources_required_right = 0

    for resource, cost_amount in cost.items():
        if resource == Resource.COIN:
            player.add_coins(
                -cost_amount
            )  # Since the function is pay, here we subtract the amount
            continue

        # Track how many resources come from neighbors
        if player.get_resources().get(resource, 0) < cost_amount:
            # TODO: introduce trading discounts

            missing_amount = cost_amount - player.get_resources().get(resource, 0)
            if missing_amount > MAXIMUM_TRADING_RESOURCES:
                raise ValueError(f"Player {player.name} cannot afford card")

            if (
                resources_required_right == 0
                and player.coins >= BASE_TRADING_COST
                and missing_amount > 0
            ):
                if right_neighbor.get_resources().get(resource, 0) > 0:
                    resources_required_right += 1
                    right_neighbor.add_coins(BASE_TRADING_COST)
                    player.add_coins(-BASE_TRADING_COST)
                    missing_amount -= 1

            if (
                resources_required_left == 0
                and player.coins >= BASE_TRADING_COST
                and missing_amount > 0
            ):
                if left_neighbor.get_resources().get(resource, 0) >= 0:
                    resources_required_left += 1
                    left_neighbor.add_coins(BASE_TRADING_COST)
                    player.add_coins(-BASE_TRADING_COST)
                    missing_amount -= 1

            if missing_amount > 0:
                raise ValueError(
                    f"Player {player.name} cannot afford card and neighbors cannot help"
                )
