from typing import List
from ..core.types import Card, CardType
import random


def is_card_present(cards: List[Card], card_name: str) -> bool:
    """Check if a card is present in a list of cards"""
    return any(card.name == card_name for card in cards)


def drop_duplicates_cards(cards: List[Card]) -> List[Card]:
    """Drop duplicate cards with the same name"""
    return list({card.name: card for card in cards}.values())


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