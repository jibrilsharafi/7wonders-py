import logging
from typing import Dict, List

from src.core.constants import CARDS_PER_PLAYER, DISCARD_CARD_VALUE
from src.core.enums import Action
from src.core.types import Card
from src.game.effect_resolver import apply_card_effects, apply_wonder_effects
from src.game.military import apply_military_tokens, resolve_military_conflicts
from src.game.player import Player
from src.game.move import Move
from src.game.trade_manager import pay_costs
from src.utils.generic import get_left_neighbor, get_right_neighbor, is_valid_move
from src.utils.validators import get_random_cards

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, players: List[Player]):
        self.age = 1
        self.turn = 1
        self.all_players = players
        self.discarded_cards: List[Card] = []
        self.hands: Dict[Player, List[Card]] = {}

        logger.info(f"Game state created with {len(players)} players")

    def deal_age(self, cards: List[Card]) -> None:
        """Deal 7 cards to each player at the start of an age"""

        n_cards = len(self.all_players) * CARDS_PER_PLAYER

        shuffled_cards = get_random_cards(
            cards,
            n_cards,
            filter_age=[self.age],  # Only cards for the current age
            filter_min_players=list(
                range(3, len(self.all_players) + 1)
            ),  # Only cards for the current number of players
            unique=True,
        )

        logger.info(f"Dealing {n_cards} cards for age {self.age}")

        for i, player in enumerate(self.all_players):
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
        if all(len(player.hand) == 1 for player in self.all_players):
            # Last card of the age
            # TODO: some effect allow on the last card to be played, check this

            # Discard cards from players
            for player in self.all_players:
                self.discarded_cards.extend(player.hand)
                player.discard_hand()

            # Handle military conflicts at end of age
            outcomes = resolve_military_conflicts(self.all_players, self.age)
            apply_military_tokens(self.all_players, outcomes)

            return True

        self.rotate_hands()
        self.turn += 1
        return False

    def rotate_hands(self) -> None:
        """Pass hands to neighbors (clockwise in ages 1 and 3, counter-clockwise in age 2)"""
        old_hands = {player: player.hand for player in self.all_players}
        if self.age in [1, 3]:  # Pass clockwise
            for i, player in enumerate(self.all_players):
                next_player = self.all_players[(i + 1) % len(self.all_players)]
                player.discard_hand()
                player.add_to_hand(old_hands[next_player])
        else:  # Pass counter-clockwise
            for i, player in enumerate(self.all_players):
                prev_player = self.all_players[(i - 1) % len(self.all_players)]
                player.discard_hand()
                player.add_to_hand(old_hands[prev_player])

    def make_turn(self, current_player: Player) -> None:
        strategy = current_player.strategy
        move = strategy.choose_move(current_player, self)

        left_neighbor = get_left_neighbor(self.all_players, current_player)
        right_neighbor = get_right_neighbor(self.all_players, current_player)

        if is_valid_move(current_player, move, left_neighbor, right_neighbor):
            self.make_move(move)
        else:
            raise ValueError("Invalid move suggested")

    def make_move(self, move: Move) -> None:
        # Here we apply the move to the game state without checking if it's valid
        
        player = move.player
        card = move.card

        left_neighbor = get_left_neighbor(self.all_players, player)
        right_neighbor = get_right_neighbor(self.all_players, player)

        if move.action == Action.PLAY:
            if not player.can_chain(card):
                pay_costs(player, card.cost, left_neighbor, right_neighbor)
            player.add_card(card)
            player.remove_from_hand(card)
            apply_card_effects(player, card, left_neighbor, right_neighbor)

        elif move.action == Action.WONDER:
            stage = player.get_current_wonder_stage_to_be_built()
            pay_costs(player, stage.cost, left_neighbor, right_neighbor)
            player.add_stage()
            apply_wonder_effects(player, stage.effect)

        elif move.action == Action.DISCARD:
            player.add_coins(DISCARD_CARD_VALUE)

        self.hands[player].remove(card)
