from typing import Dict, List
from ..core.types import Card, Wonder
from ..core.enums import Resource, CardType


class Player:
    def __init__(self, name: str, wonder: Wonder):
        self.name: str = name
        self.wonder: Wonder = wonder
        self.cards: List[Card] = []
        self.coins: int = 3
        self.military_tokens: int = 0
        self.stages_built: int = 0
        self.resources: Dict[Resource, int] = {wonder.resource: 1}

    # Getters
    def total_cards(self) -> int:
        return len(self.cards)

    def total_cards_of_type(self, card_type: CardType) -> int:
        return len([card for card in self.cards if card.type == card_type])

    def total_resources(self) -> int:
        return sum(self.resources.values())

    def get_left_neighbor(self, all_players: List["Player"]) -> "Player":
        index = all_players.index(self)
        return all_players[(index - 1) % len(all_players)]

    def get_right_neighbor(self, all_players: List["Player"]) -> "Player":
        index = all_players.index(self)
        return all_players[(index + 1) % len(all_players)]

    # Setters
    def add_card(self, card: Card) -> None:
        if card.name in [c.name for c in self.cards]:
            raise ValueError(f"Card {card.name} is already in player's hand")

        self.cards.append(card)

    def add_resource(self, resource: Resource, amount: int = 1) -> None:
        self.resources[resource] += amount

    def add_coins(self, amount: int) -> None:
        self.coins += amount

    def add_military_tokens(self, amount: int) -> None:
        self.military_tokens += amount

    def add_stage(self) -> None:
        self.stages_built += 1
        
    def can_add_card(self, card: Card) -> bool:
        return card.name not in [c.name for c in self.cards]
