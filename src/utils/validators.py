from typing import List
from ..core.types import Card, CardType
import random


def is_card_present(cards: List[Card], card_to_check: Card) -> bool:
    """Check if a card is present in a list of cards"""
    return any(card_to_check.name == card.name for card in cards)


def can_card_be_chained(cards: List[Card], new_card: Card) -> bool:
    return bool(any(new_card.name in c.chain_to for c in cards))


def drop_duplicates_cards(cards: List[Card]) -> List[Card]:
    """Drop duplicate cards with the same name"""
    seen = set()
    unique_cards = []
    for card in cards:
        if card.name not in seen:
            unique_cards.append(card)
            seen.add(card.name)
    return unique_cards


def get_random_cards(
    cards: List[Card],
    n: int,
    filter_age: List[int] = [],
    filter_min_players: List[int] = [],
    filter_type: List[CardType] = [],
    unique: bool = False,
) -> List[Card]:
    """Get n random cards from a list of cards with optional filters"""
    if filter_age:
        cards = [card for card in cards if card.age in filter_age]
    if filter_min_players:
        cards = [card for card in cards if card.min_players in filter_min_players]
    if filter_type:
        cards = [card for card in cards if card.type in filter_type]

    if unique:
        cards = drop_duplicates_cards(cards)

    return random.sample(cards, n)

def get_left_in_list(index: int, list_length: int) -> int:
    """Get the left neighbor of an element in a list"""
    return (index - 1) % list_length

def get_right_in_list(index: int, list_length: int) -> int:
    """Get the right neighbor of an element in a list"""
    return (index + 1) % list_length