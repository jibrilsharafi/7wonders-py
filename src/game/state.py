from typing import List, Dict
from src.core.types import Card, Resource, CardType
from src.game.player import Player
from src.core.enums import Action, CARD_TYPE_MAP, RESOURCE_MAP
from src.game.moves import Move
from src.utils.validators import get_random_cards
import logging

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, players: List[Player]):
        self.age = 1
        self.turn = 1
        self.players = players
        self.hands: Dict[Player, List[Card]] = {}
        self.played_cards: Dict[Player, List[Card]] = {}

        logger.info(f"Game state created with {len(players)} players")

    def _check_resource_availability(
        self, player: Player, resource: Resource, amount: int
    ) -> bool:
        """Check if a resource is available either from player or neighbors"""
        # Check player's own resources
        if player.get_resources().get(resource, 0) >= amount:
            return True

        # Check neighbors' resources
        left_neighbor = player.get_left_neighbor(self.players)
        right_neighbor = player.get_right_neighbor(self.players)

        return (
            left_neighbor.get_resources().get(resource, 0) >= amount
            or right_neighbor.get_resources().get(resource, 0) >= amount
        )

    def get_valid_moves(self, player: Player) -> List[Move]:
        """Get all valid moves for a player considering resources"""
        valid_moves = []
        cards_hand = self.hands[player]

        for action in player.get_allowed_actions(cards_hand):
            if action == Action.PLAY:
                # Filter cards that can be afforded
                for card in cards_hand:
                    if player.can_play(card) and self.can_afford_cost(
                        player, card.cost
                    ):
                        valid_moves.append(Move(player, action, card))

            elif action == Action.WONDER:
                # Check if wonder stage can be afforded
                if player.can_build_wonder():
                    stage = player.wonder.stages[player.stages_built]
                    if self.can_afford_cost(player, stage.cost):
                        # Any card can be used for wonder
                        valid_moves.extend(
                            [Move(player, action, card) for card in cards_hand]
                        )

            elif action == Action.DISCARD:
                # Can always discard any card
                valid_moves.extend([Move(player, action, card) for card in cards_hand])

        return valid_moves

    def can_afford_cost(self, player: Player, costs: Dict[Resource, int]) -> bool:
        """Check if player can afford costs considering own and neighbors' resources"""
        BASE_TRADING_COST = 2
        MAXIMUM_TRADING_RESOURCES = 2

        # TODO: add chains

        # First check coins separately
        total_coins_needed = 0
        for resource, amount in costs.items():
            if resource == Resource.COIN:
                total_coins_needed += amount

        if total_coins_needed > player.coins:
            return False

        # Then check each resource
        resources_from_neighbors = 0
        coins_for_trading = (
            player.coins - total_coins_needed
        )  # Remaining coins after direct costs

        for resource, amount in costs.items():
            if resource == Resource.COIN:
                continue

            # How many of this resource do we need from neighbors?
            player_has = player.get_resources().get(resource, 0)
            if player_has >= amount:
                continue

            missing = amount - player_has

            # Check if neighbors have enough
            left_neighbor = player.get_left_neighbor(self.players)
            right_neighbor = player.get_right_neighbor(self.players)
            left_has = left_neighbor.get_resources().get(resource, 0)
            right_has = right_neighbor.get_resources().get(resource, 0)

            # Can we get the missing resources from neighbors?
            available_from_neighbors = 0
            if left_has > 0:
                available_from_neighbors += min(left_has, missing)
            if right_has > 0:
                available_from_neighbors += min(
                    right_has, missing - available_from_neighbors
                )

            if available_from_neighbors < missing:
                return False

            # Do we have enough coins to trade?
            resources_from_neighbors += missing
            coins_needed_for_trade = missing * BASE_TRADING_COST

            if (
                resources_from_neighbors > MAXIMUM_TRADING_RESOURCES
                or coins_needed_for_trade > coins_for_trading
            ):
                return False

            coins_for_trading -= coins_needed_for_trade

        return True

    def deal_age(self, cards: List[Card]) -> None:
        """Deal 7 cards to each player at the start of an age"""
        CARDS_PER_PLAYER = 7

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

    def make_move(self, move: Move) -> None:
        player = move.player
        card = move.card

        if move.action == Action.PLAY:
            if not player.can_play(card):
                raise ValueError(f"Player {player.name} cannot play card {card.name}")

            if not self.can_afford_cost(player, card.cost):
                raise ValueError(f"Player {player.name} cannot afford card {card.name}")

            self._pay_costs(player, card.cost)
            player.add_card(card)
            self._apply_card_effects(player, card)

        elif move.action == Action.WONDER:
            if not player.can_build_wonder():
                raise ValueError(f"Player {player.name} cannot build wonder stage")

            stage = player.wonder.stages[player.stages_built]
            if not self.can_afford_cost(player, stage.cost):
                raise ValueError(f"Player {player.name} cannot afford wonder stage")

            self._pay_costs(player, stage.cost)
            player.add_stage()
            self._apply_wonder_effects(player, stage.effect)

        elif move.action == Action.DISCARD:
            player.add_coins(3)

        self.hands[player].remove(card)
        self.played_cards.setdefault(player, []).append(card)

    def _pay_costs(self, player: Player, costs: Dict[Resource, int]) -> None:
        """Handle payment of costs, including trading with neighbors"""
        BASE_TRADING_COST = 2
        DISCOUNTED_TRADING_COST = 1
        MAXIMUM_TRADING_RESOURCES = 2

        resources_required_left = 0
        resources_required_right = 0
        
        
        # TODO: add chains

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
                        total_cards += player.total_cards_of_type(required_card_type)

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

    def rotate_hands(self) -> None:
        """Pass hands to neighbors (clockwise in ages 1 and 3, counter-clockwise in age 2)"""
        old_hands = self.hands.copy()
        if self.age in [1, 3]:  # Pass clockwise
            for i, player in enumerate(self.players):
                next_player = self.players[(i + 1) % len(self.players)]
                self.hands[next_player] = old_hands[player]
        else:  # Pass counter-clockwise
            for i, player in enumerate(self.players):
                prev_player = self.players[(i - 1) % len(self.players)]
                self.hands[prev_player] = old_hands[player]

    def next_age(self) -> bool:
        """Advance to next age, return True if game is complete"""
        self.age += 1
        self.turn = 1
        return self.age > 3

    def _handle_military_conflicts(self) -> None:
        """Handle military conflicts at the end of an age"""

        MAP_AGE_TO_TOKENS = {1: 1, 2: 3, 3: 5}
        TOKEN_LOST = -1

        for player in self.players:
            left_neighbor = player.get_left_neighbor(self.players)
            right_neighbor = player.get_right_neighbor(self.players)

            player_shields = player.get_shields()
            left_shields = left_neighbor.get_shields()
            right_shields = right_neighbor.get_shields()

            # Compare with left neighbor
            if player_shields > left_shields:
                player.add_military_tokens(MAP_AGE_TO_TOKENS[self.age])
            elif player_shields < left_shields:
                player.add_military_tokens(TOKEN_LOST)
            else:
                logger.debug(f"A boring draw for {player.name} vs {left_neighbor.name}")

            # Compare with right neighbor
            if player_shields > right_shields:
                player.add_military_tokens(MAP_AGE_TO_TOKENS[self.age])
            elif player_shields < right_shields:
                player.add_military_tokens(TOKEN_LOST)
            else:
                logger.debug(
                    f"A boring draw for {player.name} vs {right_neighbor.name}"
                )

    def next_turn(self) -> bool:
        """Advance to next turn, return True if age is complete"""
        if all(len(hand) == 1 for hand in self.hands.values()):
            # Last card of the age
            for player, hand in self.hands.items():
                # Get valid moves for the last card
                valid_moves = self.get_valid_moves(player)
                if not valid_moves:
                    # If can't play, must discard
                    self.make_move(Move(player, Action.DISCARD, hand[0]))
                else:
                    # Take first valid move (could be random or AI-driven)
                    self.make_move(valid_moves[0])

            # Handle military conflicts at end of age
            self._handle_military_conflicts()
            return True

        self.rotate_hands()
        self.turn += 1
        return False
