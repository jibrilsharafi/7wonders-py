import logging
from typing import Dict, List

from src.core.enums import RESOURCE_MAP, CardType, Resource
from src.core.types import Card, Score, Wonder, WonderStage
from src.game.strategy import PlayerStrategy
from src.utils.generic import can_card_be_added, can_card_be_chained

logger = logging.getLogger(__name__)


class Player:
    def __init__(
        self, name: str, wonder: Wonder, strategy: PlayerStrategy
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

    def count_cards_by_type(self, card_type: CardType) -> int:
        return sum(card.type == card_type for card in self.cards)

    def can_add_card(self, card: Card) -> bool:
        return can_card_be_added(self.cards, card)

    def can_play_no_costs(self, card: Card) -> bool:
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
