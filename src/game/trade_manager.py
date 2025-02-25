from typing import Dict
from src.core.types import Resource
from src.game.state import GameState
from src.game.player import Player
from src.core.constants import (
    BASE_TRADING_COST,
    MAXIMUM_TRADING_RESOURCES,
    DISCARD_CARD_VALUE,
    CARDS_PER_PLAYER,
)


class TradeManager:
    """Handles resource trading between players"""

    def __init__(self, game_state: GameState):
        self._game_state = game_state

    def _pay_costs(self, player: Player, costs: Dict[Resource, int]) -> None:
        """Handle payment of costs, including trading with neighbors"""

        resources_required_left = 0
        resources_required_right = 0

        for resource, cost_amount in costs.items():
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
                    right_neighbor = player.get_right_neighbor(self.players)
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
                    left_neighbor = player.get_left_neighbor(self.players)
                    if left_neighbor.get_resources().get(resource, 0) >= 0:
                        resources_required_left += 1
                        left_neighbor.add_coins(BASE_TRADING_COST)
                        player.add_coins(-BASE_TRADING_COST)
                        missing_amount -= 1

                if missing_amount > 0:
                    raise ValueError(
                        f"Player {player.name} cannot afford card and neighbors cannot help"
                    )
