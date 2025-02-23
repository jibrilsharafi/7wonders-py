# constants.py
from dataclasses import dataclass
import random
from typing import Dict, List, Optional
from enum import Enum

from game_types import Age, Card, Resource, CardType, CardCost, ScienceSymbol




def parse_card(row: Dict[str, str]) -> Card:
    """Parse a card from a row in the CSV"""

    card_type = CARD_TYPE_MAP[row[CardsCsvHeaders.TYPE.value]]

    age = Age(int(row[CardsCsvHeaders.AGE.value]))

    cost = parse_card_cost(row[CardsCsvHeaders.COST.value])

    chain_builds = row[CardsCsvHeaders.CHAIN_TO.value].split(" | ")

    resources_produced = parse_resource_effect(row[CardsCsvHeaders.EFFECT.value])

    victory_points = int(row[CardsCsvHeaders.VICTORY_POINTS.value])

    military_shields = int(row[CardsCsvHeaders.MILITARY_SHIELDS.value])

    science_symbol = SCIENCE_SYMBOL_MAP.get(row[CardsCsvHeaders.SCIENCE_SYMBOL.value])

    return Card(
        name=row[CardsCsvHeaders.NAME.value],
        type=card_type,
        age=age,
        cost=cost,
        min_players=int(row[CardsCsvHeaders.MIN_PLAYERS.value]),
        chain_builds=chain_builds,
        resources_produced=resources_produced,
        effect=row[CardsCsvHeaders.EFFECT.value],
        victory_points=victory_points,
        military_shields=military_shields,
        science_symbol=science_symbol,
    )


def parse_card_cost(cost: str) -> CardCost:

    resources = {}
    coins = 0
    if cost:
        cost = cost.split("/")
        for c in cost:
            if c[0].isdigit():
                coins = int(c)
            else:
                resources[RESOURCE_MAP[c]] = 1
    return CardCost(resources, coins)


def parse_resource_effect(effect: str) -> Dict[Resource, int]:
    """Parse resource production effect from CSV format.
    Examples:
        'W' -> {Resource.WOOD: 1}
        'S/W' -> {Resource.STONE: 1, Resource.WOOD: 1}
    """
    if not effect:
        return {}
    resources = effect.split("/")
    return {RESOURCE_MAP[r]: 1 for r in resources}
