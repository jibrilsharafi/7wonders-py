from typing import List, Dict
from src.core.types import Card, Resource, CardType
from src.game.player import Player
from src.game.player_view import PlayerView
from src.core.enums import Action, CARD_TYPE_MAP
from src.core.constants import (
    BASE_TRADING_COST,
    MAXIMUM_TRADING_RESOURCES,
    DISCARD_CARD_VALUE,
    CARDS_PER_PLAYER,
)
from src.game.moves import Move
from src.game.strategy import PlayerStrategy
from src.utils.validators import get_random_cards
from src.game.military import resolve_military_conflicts, apply_military_tokens
from src.game.trade_manager import TradeManager
from src.game.effect_resolver import EffectResolver
import logging

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, players: List[Player]):
        self.age = 1
        self.turn = 1
        self.players = players
        self.discarded_cards: List[Card] = []
        self.hands: Dict[Player, List[Card]] = {}

        # Initialize managers
        self.trade_manager = TradeManager(self)
        self.effect_resolver = EffectResolver(self)

        logger.info(f"Game state created with {len(players)} players")

    def deal_age(self, cards: List[Card]) -> None:
        """Deal 7 cards to each player at the start of an age"""

        n_cards = len(self.players) * CARDS_PER_PLAYER

        shuffled_cards = get_random_cards(
            cards,
            n_cards,
            filter_age=[self.age],  # Only cards for the current age
            filter_min_players=list(
                range(3, len(self.players) + 1)
            ),  # Only cards for the current number of players
            unique=True,
        )

        logger.info(f"Dealing {n_cards} cards for age {self.age}")

        for i, player in enumerate(self.players):
            start = i * CARDS_PER_PLAYER
            end = start + CARDS_PER_PLAYER
            self.hands[player] = shuffled_cards[start:end]

    def next_age(self) -> bool:
        """Advance to next age, return True if game is complete"""
        self.age += 1
        self.turn = 1
        return self.age > 3

    def next_turn(self) -> bool:
        """Advance to next turn, return True if age is complete"""
        if all(len(player.hand) == 1 for player in self.players):
            # Last card of the age
            # TODO: some effect allow on the last card to be played, check this

            # Discard cards from players
            for player in self.players:
                self.discarded_cards.extend(player.hand)
                player.discard_hand()

            # Handle military conflicts at end of age
            outcomes = resolve_military_conflicts(self.players, self.age)
            apply_military_tokens(self.players, outcomes)

            return True

        self.rotate_hands()
        self.turn += 1
        return False

    def rotate_hands(self) -> None:
        """Pass hands to neighbors (clockwise in ages 1 and 3, counter-clockwise in age 2)"""
        old_hands = {player: player.hand for player in self.players}
        if self.age in [1, 3]:  # Pass clockwise
            for i, player in enumerate(self.players):
                next_player = self.players[(i + 1) % len(self.players)]
                player.discard_hand()
                player.add_to_hand(old_hands[next_player])
        else:  # Pass counter-clockwise
            for i, player in enumerate(self.players):
                prev_player = self.players[(i - 1) % len(self.players)]
                player.discard_hand()
                player.add_to_hand(old_hands[prev_player])

    def make_turn(self, current_player: Player) -> None:
        # Create PlayerView with access to game state
        player_view = PlayerView(current_player, self)

        strategy = current_player.strategy
        move = strategy.choose_move(player_view)

        if self._is_valid_move(move):
            self._execute_move(move)
        else:
            raise ValueError("Invalid move suggested")

    def make_move(self, move: Move) -> None:
        player = move.player
        card = move.card
        player_view = PlayerView(player, self)

        if move.action == Action.PLAY:
            if not player_view.can_chain(card):
                self.trade_manager.pay_costs(player, card.cost)
            player.add_card(card)
            self.effect_resolver.apply_card_effects(player, card)

        elif move.action == Action.WONDER:
            stage = player_view.get_current_wonder_stage()
            self.trade_manager.pay_costs(player, stage.cost)
            player.add_stage()
            self.effect_resolver.apply_wonder_effects(player, stage.effect)

        elif move.action == Action.DISCARD:
            player.add_coins(DISCARD_CARD_VALUE)

        self.hands[player].remove(card)
