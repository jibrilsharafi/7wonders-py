import logging
import random
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from src.core.constants import (
    BASE_TRADING_COST,
    DISCOUNTED_TRADING_COST,
    MAXIMUM_TRADING_RESOURCES,
)
from src.core.enums import CARD_TYPE_MAP, RESOURCE_MAP, Action, CardType, Resource
from src.core.types import Card, Score, Wonder, WonderStage
from src.game.move import Move
from src.utils.validators import is_card_present, can_card_be_chained

logger = logging.getLogger(__name__)


@dataclass
class GameView:
    age: int
    turn: int
    all_players_no_hand: List["PlayerView"]
    discarded_cards: List[Card]

    def get_player_by_name(self, name: str) -> "PlayerView":
        for player in self.all_players_no_hand:
            if player.name == name:
                return player
        raise ValueError(f"Player '{name}' not found")

    def get_left_neighbor(self, player: "PlayerView") -> "PlayerView":
        index = self.all_players_no_hand.index(player)
        return self.all_players_no_hand[(index - 1) % len(self.all_players_no_hand)]

    def get_right_neighbor(self, player: "PlayerView") -> "PlayerView":
        index = self.all_players_no_hand.index(player)
        return self.all_players_no_hand[(index + 1) % len(self.all_players_no_hand)]


class PlayerStrategy(ABC):
    @abstractmethod
    def choose_move(self, player: "Player", game_view: GameView) -> Move:
        """
        Choose next move based only on visible information through PlayerView.
        The view provides:
        - Own cards, resources and wonder state
        - Visible neighbor information
        - Valid moves calculation
        - Military strength evaluation
        """
        pass


@dataclass
class PlayerView:
    name: str
    position: int
    wonder: Wonder
    cards: List[Card]
    coins: int
    military_tokens: int
    stages_built: int
    score: Score

    def get_shields(self) -> int:
        return sum(card.effect.count("M") for card in self.cards)

    def count_cards_by_type(self, card_type: CardType) -> int:
        return sum(card.type == card_type for card in self.cards)

    def get_resources(self) -> Dict[Resource, int]:
        resources: Dict[Resource, int] = {}
        resources[self.wonder.resource] = resources.get(self.wonder.resource, 0) + 1
        return resources

    def get_built_wonder_stages(self) -> List[WonderStage]:
        return self.wonder.stages[: self.stages_built]

    def get_current_wonder_stage_to_be_built(self) -> WonderStage:
        return self.wonder.stages[self.stages_built]

    def get_military_score(self) -> int:
        return self.military_tokens

    def can_play_no_cost(self, card: Card) -> bool:
        return bool(card in self.cards)

    def can_build_wonder_no_cost(self) -> bool:
        return bool(self.stages_built < len(self.wonder.stages))

    def can_chain(self, card: Card) -> bool:
        return can_card_be_chained(self.cards, card)

    def get_left_neighbor(self, all_players: List["PlayerView"]) -> "PlayerView":
        index = self.position - 1 if self.position > 0 else len(all_players) - 1
        return all_players[index]

    def get_right_neighbor(self, all_players: List["PlayerView"]) -> "PlayerView":
        index = self.position + 1 if self.position < len(all_players) - 1 else 0
        return all_players[index]

    def get_neighbors(self, all_players: List["PlayerView"]) -> List["PlayerView"]:
        return [
            self.get_left_neighbor(all_players),
            self.get_right_neighbor(all_players),
        ]


class Player:
    def __init__(
        self, name: str, position: int, wonder: Wonder, strategy: PlayerStrategy
    ):
        self.name: str = name
        self.position: int = position
        self.wonder: Wonder = wonder
        self.cards: List[Card] = []
        self.coins: int = 3
        self.military_tokens: int = 0
        self.stages_built: int = 0
        self.score: Score = Score()
        self.hand: List[Card] = []
        self.strategy: PlayerStrategy = strategy

        logger.info(f"Player {self.name} created with wonder {self.wonder.name}")

    # Keep core state modification methods
    def add_card(self, card: Card) -> None:
        assert self.can_add_card(
            card
        ), f"Player {self.name} already has card '{card.name}'"
        logger.debug(f"Player {self.name} added the card '{card.name}'")
        self.cards.append(card)

    def add_coins(self, amount: int) -> None:
        logger.debug(f"Player {self.name} received {amount} coins")
        assert (
            self.coins + amount
        ) >= 0, f"Player {self.name} cannot have negative coins"
        self.coins += amount

    def add_military_tokens(self, amount: int) -> None:
        logger.debug(f"Player {self.name} got {amount} military tokens")
        self.military_tokens += amount

    def add_stage(self) -> None:
        assert self.stages_built < 3, f"Player {self.name} already built all stages"
        logger.debug(f"Player {self.name} proudly built stage {self.stages_built + 1}")
        self.stages_built += 1

    def add_to_hand(self, cards: List[Card]) -> None:
        self.hand.extend(cards)

    def remove_from_hand(self, card: Card) -> None:
        self.hand.remove(card)

    def discard_hand(self) -> None:
        self.hand = []

    def get_shields(self) -> int:
        return sum(card.effect.count("M") for card in self.cards)

    def get_current_wonder_stage_to_be_built(self) -> WonderStage:
        return self.wonder.stages[self.stages_built]

    def get_built_wonder_stages(self) -> List[WonderStage]:
        return self.wonder.stages[: self.stages_built]

    def get_military_score(self) -> int:
        return self.military_tokens

    def get_player_view(player: "Player") -> PlayerView:
        return PlayerView(
            deepcopy(player.name),
            deepcopy(player.position),
            deepcopy(player.wonder),
            deepcopy(player.cards),
            deepcopy(player.coins),
            deepcopy(player.military_tokens),
            deepcopy(player.stages_built),
            deepcopy(player.score),
        )

    def get_left_neighbor(self, all_players: List["PlayerView"]) -> "PlayerView":
        index = self.position - 1 if self.position > 0 else len(all_players) - 1
        return all_players[index]

    def get_right_neighbor(self, all_players: List["PlayerView"]) -> "PlayerView":
        index = self.position + 1 if self.position < len(all_players) - 1 else 0
        return all_players[index]

    def get_neighbors(self, all_players: List["PlayerView"]) -> List["PlayerView"]:
        return [
            self.get_left_neighbor(all_players),
            self.get_right_neighbor(all_players),
        ]

    def count_cards_by_type(self, card_type: CardType) -> int:
        return sum(card.type == card_type for card in self.cards)

    def can_add_card(self, card: Card) -> bool:
        return not is_card_present(self.cards, card)

    def can_play_no_cost(self, card: Card) -> bool:
        return bool(self.can_add_card(card))

    def can_build_wonder_no_cost(self) -> bool:
        return bool(self.stages_built < len(self.wonder.stages))

    def can_chain(self, card: Card) -> bool:
        return can_card_be_chained(self.cards, card)

    def get_resources(
        self, priority_resources: List[Resource] = []
    ) -> Dict[Resource, int]:
        resources: Dict[Resource, int] = {}

        # Add wonder resource
        resources[self.wonder.resource] = resources.get(self.wonder.resource, 0) + 1
        # If any of the stages of the wonder has resources, add them
        for stage in self.wonder.stages:
            if "-" in stage.effect or "_" in stage.effect:
                # This is either a special effect or it does not give resources
                continue

            # Let's check stage.effect
            # If the effect contains /, it means it has multiple effects
            if "/" in stage.effect:
                # Here we check which resources are on higher priority based on input
                if not priority_resources:
                    # If nothing is set, just take the first effect
                    letter = stage.effect[0]
                    resource = RESOURCE_MAP[letter]
                    amount = stage.effect.count(letter)
                    resources[resource] = resources.get(resource, 0) + amount
                else:
                    # If we have priority resources, take the first one that is in the effect
                    for resource in priority_resources:
                        for letter, res in RESOURCE_MAP.items():
                            if res == resource:
                                break
                        if letter in stage.effect:
                            amount = stage.effect.count(letter)
                            resources[resource] = resources.get(resource, 0) + amount
                            break
            else:
                letter = stage.effect[0]
                resource = RESOURCE_MAP[letter]
                amount = stage.effect.count(letter)
                resources[resource] = resources.get(resource, 0) + amount

        for card in self.cards:
            # Check the effect of the card
            # If the effect contains /, it means it has multiple effects
            if "/" in card.effect:
                # Here we check which resources are on higher priority based on input
                if not priority_resources:
                    # If nothing is set, just take the first effect
                    letter = card.effect[0]
                    resource = RESOURCE_MAP[letter]
                    amount = card.effect.count(letter)
                    resources[resource] = resources.get(resource, 0) + amount
                else:
                    # If we have priority resources, take the first one that is in the effect
                    for resource in priority_resources:
                        for letter, res in RESOURCE_MAP.items():
                            if res == resource:
                                break
                        if letter in card.effect:
                            amount = card.effect.count(letter)
                            resources[resource] = resources.get(resource, 0) + amount
                            break

            elif (
                card.type == CardType.RAW_MATERIAL
                or card.type == CardType.MANUFACTURED_GOOD
            ):
                letter = card.effect[0]
                resource = RESOURCE_MAP[letter]
                amount = card.effect.count(letter)
                resources[resource] = resources.get(resource, 0) + amount

            # If commercial, it can be another priority list
            elif card.type == CardType.COMMERCIAL:
                if "/" not in card.effect:
                    continue

                # Here we check which resources are on higher priority based on input
                if not priority_resources:
                    # If nothing is set, just take the first effect
                    letter = card.effect[0]
                    resource = RESOURCE_MAP[letter]
                    amount = card.effect.count(letter)
                    resources[resource] = resources.get(resource, 0) + amount
                else:
                    # If we have priority resources, take the first one that is in the effect
                    for resource in priority_resources:
                        for letter, res in RESOURCE_MAP.items():
                            if res == resource:
                                break
                        if letter in card.effect:
                            amount = card.effect.count(letter)
                            resources[resource] = resources.get(resource, 0) + amount
                            break
        return resources

    def pay_costs(
        self,
        cost: Dict[Resource, int],
        left_neighbor: PlayerView,
        right_neighbor: PlayerView,
    ) -> List[int]:
        """Handle payment of costs, including trading with neighbors"""

        resources_required_left = 0
        resources_required_right = 0

        neighbors_coins: List[int] = [0, 0]

        for resource, cost_amount in cost.items():
            if resource == Resource.COIN:
                self.add_coins(
                    -cost_amount
                )  # Since the function is pay, here we subtract the amount
                continue

            # Track how many resources come from neighbors
            if self.get_resources().get(resource, 0) < cost_amount:
                # TODO: introduce trading discounts

                missing_amount = cost_amount - self.get_resources().get(resource, 0)
                if missing_amount > MAXIMUM_TRADING_RESOURCES:
                    raise ValueError(f"Player {self.name} cannot afford card")

                if (
                    resources_required_right == 0
                    and self.coins >= BASE_TRADING_COST
                    and missing_amount > 0
                ):
                    if right_neighbor.get_resources().get(resource, 0) > 0:
                        resources_required_right += 1
                        neighbors_coins[1] += BASE_TRADING_COST
                        self.add_coins(-BASE_TRADING_COST)
                        missing_amount -= 1

                if (
                    resources_required_left == 0
                    and self.coins >= BASE_TRADING_COST
                    and missing_amount > 0
                ):
                    if left_neighbor.get_resources().get(resource, 0) >= 0:
                        resources_required_left += 1
                        neighbors_coins[0] += BASE_TRADING_COST
                        self.add_coins(-BASE_TRADING_COST)
                        missing_amount -= 1

                if missing_amount > 0:
                    raise ValueError(
                        f"Player {self.name} cannot afford card and neighbors cannot help"
                    )

        return neighbors_coins

    def apply_card_effects(
        self,
        card: Card,
        left_neighbor: PlayerView,
        right_neighbor: PlayerView,
    ) -> None:
        """Apply card effects when played. Only instantaneous ones"""
        effect = card.effect

        if card.type == CardType.COMMERCIAL:
            logger.debug(f"Applying commercial card '{card.name}' effect: {effect}")
            if "$" in effect:
                coins_multiplier = effect.count("$")
                if "{" in effect:
                    bracket_content = effect.split("{")[1].split("}")[0]
                    if bracket_content == "wonder":
                        self.add_coins(coins_multiplier * self.stages_built)
                        return

                    total_cards = 0
                    required_card_type = CARD_TYPE_MAP[bracket_content]

                    if (
                        "v" in bracket_content or "<" not in bracket_content
                    ):  # Either only self or self and neighbors
                        total_cards += self.count_cards_by_type(required_card_type)

                    if "<" in bracket_content:  # ALl cards with < also have >
                        total_cards += left_neighbor.count_cards_by_type(
                            required_card_type
                        )

                        total_cards += right_neighbor.count_cards_by_type(
                            required_card_type
                        )

                    self.add_coins(coins_multiplier * total_cards)

    def apply_wonder_effects(self, effect: str) -> None:
        """Apply wonder stage effects when built"""
        if "$" in effect:
            # TODO: get moneyyy
            pass
        elif "_" in effect:
            # TODO: implement custom effects
            pass


@dataclass
class TradeOption:
    """Represents a trade option with a neighbor"""

    player: PlayerView
    cost: int
    is_left: bool


def get_left_neighbor(position: int, all_players: List[Player]) -> Player:
    index = position - 1 if position > 0 else len(all_players) - 1
    return all_players[index]


def get_right_neighbor(position: int, all_players: List[Player]) -> Player:
    index = position + 1 if position < len(all_players) - 1 else 0
    return all_players[index]


def get_neighbors(position: int, all_players: List[Player]) -> List[Player]:
    return [
        get_left_neighbor(position, all_players),
        get_right_neighbor(position, all_players),
    ]


def get_neighbor_shields(neighbors: Union[List[Player], List[PlayerView]]) -> List[int]:
    """
    Get visible military strength of neighbors
    Always ordered left to right
    """

    return [neighbor.get_shields() for neighbor in neighbors]


def get_best_trade_option(
    player: PlayerView,
    left_neighbor: PlayerView,
    right_neighbor: PlayerView,
    resource: Resource,
) -> Optional[TradeOption]:
    """Get the best neighbor to trade with for a specific resource"""
    options: List[TradeOption] = []

    # Check left neighbor resources
    if left_neighbor.get_resources().get(resource, 0) > 0:
        cost = (
            DISCOUNTED_TRADING_COST
            if is_trading_discounted(player, resource, True)
            else BASE_TRADING_COST
        )
        options.append(TradeOption(left_neighbor, cost, True))

    # Check right neighbor resources
    if right_neighbor.get_resources().get(resource, 0) > 0:
        cost = (
            DISCOUNTED_TRADING_COST
            if is_trading_discounted(player, resource, False)
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
    player: PlayerView,
    resource: Resource,
    is_left: bool,
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
    player: PlayerView,
    left_neighbor: PlayerView,
    right_neighbor: PlayerView,
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
    player: Player,
    left_neighbor: PlayerView,
    right_neighbor: PlayerView,
) -> List[Move]:
    """Get all valid moves for current hand"""
    valid_moves = []

    player_view = player.get_player_view()
    for card in player.hand:
        if player.can_play_no_cost(card) and (
            can_afford_cost(player_view, left_neighbor, right_neighbor, card.cost)
            or player.can_chain(card)
        ):
            valid_moves.append(Move(player.name, Action.PLAY, card))

        if player.can_build_wonder_no_cost():
            stage = player.get_current_wonder_stage_to_be_built()
            if can_afford_cost(player_view, left_neighbor, right_neighbor, stage.cost):
                valid_moves.append(Move(player.name, Action.WONDER, card))

        valid_moves.append(Move(player.name, Action.DISCARD, card))

    return valid_moves.copy()


def is_valid_move(
    player: PlayerView,
    move: Move,
    left_neighbor: PlayerView,
    right_neighbor: PlayerView,
) -> bool:
    """Check if a move is valid"""
    if move.action == Action.PLAY:
        return bool(
            player.can_play_no_cost(move.card)
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
        return True
