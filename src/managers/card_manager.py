# src/managers/card_manager.py
import csv
from typing import List
from ..core.types import Card

class CardManager:
    @staticmethod
    def load_cards() -> List[Card]:
        """Load cards from CSV file"""
        cards: List[Card] = []
        with open('data/cards.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # TODO: Implement card loading
                pass
        return cards