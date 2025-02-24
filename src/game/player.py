from ..core.types import Card, Wonder, Score
from typing import Dict, List
from ..core.enums import Resource, CardType, Action, RESOURCE_MAP
import logging

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, name: str, wonder: Wonder):
        self.name: str = name
        self.wonder: Wonder = wonder
        self.cards: List[Card] = []
        self.coins: int = 3
        self.military_tokens: int = 0
        self.stages_built: int = 0
        self.score: Score = Score()

        logger.info(f"Player {self.name} created with wonder {self.wonder.name}")

    # Getters
    def total_cards(self) -> int:
        return len(self.cards)

    def total_cards_of_type(self, card_type: CardType) -> int:
        return len([card for card in self.cards if card.type == card_type])

    def get_left_neighbor(self, all_players: List["Player"]) -> "Player":
        index = all_players.index(self)
        return all_players[(index - 1) % len(all_players)]

    def get_right_neighbor(self, all_players: List["Player"]) -> "Player":
        index = all_players.index(self)
        return all_players[(index + 1) % len(all_players)]
    
    def get_shields(self) -> int:
        return sum(card.effect.count("M") for card in self.cards)

    def get_resources(self) -> Dict[Resource, int]:
        resources: Dict[Resource, int] = {}

        for card in self.cards:
            # Check the effect of the card
            # If the effect contains /, it means it has multiple effects
            if "/" in card.effect:
                # TODO: Implement multiple effects
                pass

            if (
                card.type == CardType.RAW_MATERIAL
                or card.type == CardType.MANUFACTURED_GOOD
            ):
                letter = card.effect[0]
                resource = RESOURCE_MAP[letter]
                amount = card.effect.count(letter)
                resources[resource] = resources.get(resource, 0) + amount

            # TODO: implement also the other cards which also provide one of the resources
            # in an out-out way

        return resources

    # Setters
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
        ) >= 0, f"Player {self.name} cannot have negative coins (has {self.coins} but amount is {amount})"
        self.coins += amount

    def add_military_tokens(self, amount: int) -> None:
        logger.debug(f"Player {self.name} won {amount} military tokens")
        self.military_tokens += amount

    def add_stage(self) -> None:
        self.stages_built += 1

    def get_allowed_actions(self, cards_hand: List[Card]) -> List[Action]:
        """Get all allowed moves for a player"""
        actions = []

        for card in cards_hand:
            if self.can_play(card):  # Only check if card can be added
                actions.append(Action.PLAY)
                break

        if self.can_build_wonder():  # Only check if wonder stage available
            actions.append(Action.WONDER)

        actions.append(Action.DISCARD)  # Can always discard
        return actions

    def can_play(self, card: Card) -> bool:
        """Check if card can be added (ignoring resources)"""
        return card.name not in [c.name for c in self.cards]

    def can_build_wonder(self) -> bool:
        """Check if wonder can be built (ignoring resources)"""
        return self.stages_built < len(self.wonder.stages)

    def can_add_card(self, card: Card) -> bool:
        return card.name not in [c.name for c in self.cards]
