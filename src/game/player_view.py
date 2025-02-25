from typing import Dict, List, Optional
from dataclasses import dataclass
from src.core.types import Card, Wonder, WonderStage
from src.core.enums import Resource, CardType, Action, RESOURCE_MAP
from src.game.moves import Move
from src.game.player import Player
from src.game.state import GameState
from src.core.constants import (
    BASE_TRADING_COST,
    DISCOUNTED_TRADING_COST,
    MAXIMUM_TRADING_RESOURCES,
    AGE_MILITARY_TOKENS,
    MILITARY_DEFEAT_TOKEN,
)
import random


@dataclass
class TradeOption:
    """Represents a trade option with a neighbor"""

    player: Player
    cost: int
    is_left: bool


class PlayerView:
    """Read-only view of game state from a player's perspective"""

    def __init__(self, player: Player, game_state: GameState):
        self._player = player
        self._game_state = game_state
        self._left_neighbor = self.get_left_neighbor()
        self._right_neighbor = self.get_right_neighbor()

    @property
    def current_age(self) -> int:
        """Get current age (1-3)"""
        return int(self._game_state.age)

    @property
    def current_turn(self) -> int:
        """Get current turn number within the age"""
        return int(self._game_state.turn)

    @property
    def discarded_cards(self) -> List[Card]:
        """Get list of all discarded cards (public information)"""
        return (
            self._game_state.discarded_cards.copy()
        )  # Return copy to prevent modification

    @property
    def name(self) -> str:
        return str(self._player.name)

    @property
    def wonder(self) -> Wonder:
        return self._player.wonder

    @property
    def cards(self) -> List[Card]:
        return self._player.cards.copy()  # Return copy to prevent modification

    @property
    def coins(self) -> int:
        return int(self._player.coins)

    @property
    def military_tokens(self) -> int:
        return int(self._player.military_tokens)

    @property
    def stages_built(self) -> int:
        return int(self._player.stages_built)

    @property
    def hand(self) -> List[Card]:
        return self._player.hand.copy()

    @property
    def neighbors(self) -> List[Player]:
        return [self._left_neighbor, self._right_neighbor].copy()

    def get_current_wonder_stage(self) -> WonderStage:
        return self.wonder.stages[self.stages_built]

    def get_shields(self) -> int:
        return int(self._player.get_shields())

    def get_neighbor_shields(self) -> Dict[str, int]:
        """Get visible military strength of neighbors"""
        return {
            "left": int(self._left_neighbor.get_shields()),
            "right": int(self._right_neighbor.get_shields()),
        }

    def evaluate_military_battle(self, opponent_shields: int, age: int) -> int:
        """Evaluate outcome of a single military battle"""
        player_shields = self._player.get_shields()
        if player_shields > opponent_shields:
            return AGE_MILITARY_TOKENS[age]
        elif player_shields < opponent_shields:
            return MILITARY_DEFEAT_TOKEN
        return 0

    def evaluate_military_situation(self, age: int) -> int:
        """Evaluate potential military outcomes against both neighbors"""
        left_outcome = self.evaluate_military_battle(
            self._left_neighbor.get_shields(), age
        )
        right_outcome = self.evaluate_military_battle(
            self._right_neighbor.get_shields(), age
        )
        return left_outcome + right_outcome

    def get_military_score(self) -> int:
        """Get current military victory tokens"""
        return int(self._player.military_tokens)

    def can_play(self, card: Card) -> bool:
        """Check if card can be added (ignoring resources)"""
        return bool(self._player.can_add_card(card))

    def can_build_wonder(self) -> bool:
        """Check if wonder can be built (ignoring resources)"""
        return bool(self.stages_built < len(self.wonder.stages))

    def can_chain(self, card: Card) -> bool:
        """Check if card can be chained from existing cards"""
        return bool(any(c.chain_to == card.name for c in self.cards))

    def get_left_neighbor(self) -> Player:
        index = self._game_state.players.index(self._player)
        return self._game_state.players[(index - 1) % len(self._game_state.players)]

    def get_right_neighbor(self) -> Player:
        index = self._game_state.players.index(self._player)
        return self._game_state.players[(index + 1) % len(self._game_state.players)]

    def get_best_trade_option(self, resource: Resource) -> Optional[TradeOption]:
        """Get the best neighbor to trade with for a specific resource"""
        options: List[TradeOption] = []

        # Check left neighbor resources
        if self._left_neighbor.get_resources().get(resource, 0) > 0:
            cost = (
                DISCOUNTED_TRADING_COST
                if self.is_trading_discounted(resource, self._left_neighbor, True)
                else BASE_TRADING_COST
            )
            options.append(TradeOption(self._left_neighbor, cost, True))

        # Check right neighbor resources
        if self._right_neighbor.get_resources().get(resource, 0) > 0:
            cost = (
                DISCOUNTED_TRADING_COST
                if self.is_trading_discounted(resource, self._right_neighbor, False)
                else BASE_TRADING_COST
            )
            options.append(TradeOption(self._right_neighbor, cost, False))

        if not options:
            return None

        # Get cheapest options
        min_cost = min(opt.cost for opt in options)
        cheapest_options = [opt for opt in options if opt.cost == min_cost]
        return random.choice(cheapest_options)

    def is_trading_discounted(
        self, resource: Resource, neighbor: Player, is_left: bool
    ) -> bool:
        """Check if trading for a resource with a neighbor is discounted"""
        for card in self.cards:
            if card.type != CardType.COMMERCIAL or "trade" not in card.effect:
                continue

            resources_part = card.effect.split("{")[1].split("}")[0].split("/")
            discounted_resources = [
                RESOURCE_MAP[letter]
                for letter in resources_part
                if letter in RESOURCE_MAP
            ]

            if resource not in discounted_resources:
                continue

            if is_left and "<" in card.effect:
                return True
            if not is_left and ">" in card.effect:
                return True

        return False

    def can_afford_cost(self, costs: Dict[Resource, int]) -> bool:
        """Check if player can afford costs with available resources"""
        if Resource.COIN in costs:
            assert len(costs) == 1, "Coin cost should be the only cost"
            return bool(costs[Resource.COIN] <= self.coins)

        coins_available = self.coins
        resources_needed: Dict[Resource, int] = {}

        # Check what resources we need to trade for
        own_resources = self._player.get_resources()
        for resource, amount in costs.items():
            if own_resources.get(resource, 0) < amount:
                resources_needed[resource] = amount - own_resources.get(resource, 0)

        if not resources_needed:
            return True

        # Calculate trading costs
        total_resources_traded = 0
        for resource, amount_needed in resources_needed.items():
            remaining = amount_needed
            while remaining > 0:
                trade = self.get_best_trade_option(resource)
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

    def get_valid_moves(self) -> List[Move]:
        """Get all valid moves for current hand"""
        valid_moves = []

        for card in self.hand:
            if self.can_play(card) and (
                self.can_afford_cost(card.cost) or self.can_chain(card)
            ):
                valid_moves.append(Move(self._player, Action.PLAY, card))

            if self.can_build_wonder():
                stage = self.get_current_wonder_stage()
                if self.can_afford_cost(stage.cost):
                    valid_moves.append(Move(self._player, Action.WONDER, card))

            valid_moves.append(Move(self._player, Action.DISCARD, card))

        return valid_moves.copy()

    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid"""
        if move.action == Action.PLAY:
            return bool(
                self.can_play(move.card)
                and (self.can_afford_cost(move.card.cost) or self.can_chain(move.card))
            )

        if move.action == Action.WONDER:
            stage = self.get_current_wonder_stage()
            return bool(self.can_build_wonder() and self.can_afford_cost(stage.cost))

        if move.action == Action.DISCARD:
            return bool(move.card in self.hand)
