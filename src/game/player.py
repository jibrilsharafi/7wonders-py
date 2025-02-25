from src.core.types import Card, Wonder, Score
from typing import Dict, List
from src.core.enums import Resource, CardType, Action, RESOURCE_MAP
from src.game.moves import Move
from src.core.constants import DISCARD_CARD_VALUE
from src.game.strategy import PlayerStrategy
from src.game.strategies.simple.simple import SimpleStrategy
import logging

logger = logging.getLogger(__name__)


class Player:
    def __init__(
        self, name: str, wonder: Wonder, strategy: PlayerStrategy = SimpleStrategy()
    ):
        self.name: str = name
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

    def discard_hand(self) -> None:
        self.hand = []

    def apply_move(self, move: Move) -> None:
        self.hand.remove(move.card)
        if move.action == Action.PLAY:
            self.add_card(move.card)
        elif move.action == Action.WONDER:
            self.add_stage()
        elif move.action == Action.DISCARD:
            self.add_coins(DISCARD_CARD_VALUE)

    def get_shields(self) -> int:
        return sum(card.effect.count("M") for card in self.cards)

    def count_cards_by_type(self, card_type: CardType) -> int:
        return sum(card.type == card_type for card in self.cards)

    def can_add_card(self, card: Card) -> bool:
        return card.name not in [c.name for c in self.cards]

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
