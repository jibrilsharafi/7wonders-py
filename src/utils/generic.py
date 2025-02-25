import logging
import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.core.constants import (
    BASE_TRADING_COST,
    DISCOUNTED_TRADING_COST,
    MAXIMUM_TRADING_RESOURCES,
)
from src.core.enums import RESOURCE_MAP, Action, CardType, Resource
from src.core.types import Card
from src.game.move import Move
from src.game.player import Player

logger = logging.getLogger(__name__)


@dataclass
class TradeOption:
    """Represents a trade option with a neighbor"""

    player: Player
    cost: int
    is_left: bool


def get_left_neighbor(all_players: List[Player], player: Player) -> Player:
    index = all_players.index(player)
    return all_players[(index - 1) % len(all_players)]


def get_right_neighbor(all_players: List[Player], player: Player) -> Player:
    index = all_players.index(player)
    return all_players[(index + 1) % len(all_players)]


def get_neighbors(all_players: List[Player], player: Player) -> List[Player]:
    return [
        get_left_neighbor(all_players, player),
        get_right_neighbor(all_players, player),
    ]


def get_neighbor_shields(neighbors: List[Player], player: Player) -> List[int]:
    """
    Get visible military strength of neighbors
    Always ordered left to right
    """

    return [neighbor.get_shields() for neighbor in neighbors]


def can_card_be_added(list_cards: List[Card], new_card: Card) -> bool:
    return new_card.name not in [card.name for card in list_cards]


def can_card_be_chained(list_cards: List[Card], new_card: Card) -> bool:
    return bool(any(c.chain_to == new_card.name for c in list_cards))


def get_best_trade_option(
    player: Player, left_neighbor: Player, right_neighbor: Player, resource: Resource
) -> Optional[TradeOption]:
    """Get the best neighbor to trade with for a specific resource"""
    options: List[TradeOption] = []

    # Check left neighbor resources
    if left_neighbor.get_resources().get(resource, 0) > 0:
        cost = (
            DISCOUNTED_TRADING_COST
            if is_trading_discounted(player, resource, left_neighbor, True)
            else BASE_TRADING_COST
        )
        options.append(TradeOption(left_neighbor, cost, True))

    # Check right neighbor resources
    if right_neighbor.get_resources().get(resource, 0) > 0:
        cost = (
            DISCOUNTED_TRADING_COST
            if is_trading_discounted(player, resource, right_neighbor, False)
            else BASE_TRADING_COST
        )
        options.append(TradeOption(right_neighbor, cost, False))

    if not options:
        return None

    # Get cheapest options
    min_cost = min(opt.cost for opt in options)
    cheapest_options = [opt for opt in options if opt.cost == min_cost]
    return random.choice(cheapest_options)


def is_trading_discounted(
    player: Player, resource: Resource, neighbor: Player, is_left: bool
) -> bool:
    """Check if trading for a resource with a neighbor is discounted"""
    for card in player.cards:
        if card.type != CardType.COMMERCIAL or "trade" not in card.effect:
            continue

        resources_part = card.effect.split("{")[1].split("}")[0].split("/")
        discounted_resources = [
            RESOURCE_MAP[letter] for letter in resources_part if letter in RESOURCE_MAP
        ]

        if resource not in discounted_resources:
            continue

        if is_left and "<" in card.effect:
            return True
        if not is_left and ">" in card.effect:
            return True

    return False


def can_afford_cost(
    player: Player,
    left_neighbor: Player,
    right_neighbor: Player,
    cost: Dict[Resource, int],
) -> bool:
    """Check if player can afford costs with available resources"""
    if Resource.COIN in cost:
        assert len(cost) == 1, "Coin cost should be the only cost"
        return bool(cost[Resource.COIN] <= player.coins)

    coins_available = player.coins
    resources_needed: Dict[Resource, int] = {}

    # Check what resources we need to trade for
    own_resources = player.get_resources()
    for resource, amount in cost.items():
        if own_resources.get(resource, 0) < amount:
            resources_needed[resource] = amount - own_resources.get(resource, 0)

    if not resources_needed:
        return True

    # Calculate trading costs
    total_resources_traded = 0
    for resource, amount_needed in resources_needed.items():
        remaining = amount_needed
        while remaining > 0:
            trade = get_best_trade_option(
                player, left_neighbor, right_neighbor, resource
            )
            if not trade:
                return False

            total_resources_traded += 1
            if total_resources_traded > MAXIMUM_TRADING_RESOURCES:
                return False

            coins_available -= trade.cost
            if coins_available < 0:
                return False

            remaining -= 1

    return True


def get_valid_moves(
    player: Player, left_neighbor: Player, right_neighbor: Player
) -> List[Move]:
    """Get all valid moves for current hand"""
    valid_moves = []

    for card in player.hand:
        if player.can_play_no_costs(card) and (
            can_afford_cost(player, left_neighbor, right_neighbor, card.cost)
            or player.can_chain(card)
        ):
            valid_moves.append(Move(player, Action.PLAY, card))

        if player.can_build_wonder_no_cost():
            stage = player.get_current_wonder_stage_to_be_built()
            if can_afford_cost(player, left_neighbor, right_neighbor, stage.cost):
                valid_moves.append(Move(player, Action.WONDER, card))

        valid_moves.append(Move(player, Action.DISCARD, card))

    return valid_moves.copy()


def is_valid_move(
    player: Player, move: Move, left_neighbor: Player, right_neighbor: Player
) -> bool:
    """Check if a move is valid"""
    if move.action == Action.PLAY:
        return bool(
            player.can_play_no_costs(move.card)
            and (
                can_afford_cost(player, left_neighbor, right_neighbor, move.card.cost)
                or player.can_chain(move.card)
            )
        )

    if move.action == Action.WONDER:
        stage = player.get_current_wonder_stage_to_be_built()
        return bool(
            player.can_build_wonder_no_cost()
            and can_afford_cost(player, left_neighbor, right_neighbor, stage.cost)
        )

    if move.action == Action.DISCARD:
        return bool(move.card in player.hand)
