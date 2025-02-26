from typing import List, Dict
import csv
from enum import Enum
from ..core.enums import Resource, CARD_TYPE_MAP, RESOURCE_MAP
from ..core.types import Card, Wonder, WonderStage


class CardsCsvHeaders(Enum):
    AGE = "age"
    MIN_PLAYERS = "min_players"
    NAME = "name"
    TYPE = "type"
    COST = "cost"
    CHAIN_TO = "chain_to"
    EFFECT = "effect"


class WondersCsvHeaders(Enum):
    NAME = "name"
    RESOURCE = "resource"
    DAY_STAGES = "day_stages"
    NIGHT_STAGES = "night_stages"


def parse_cards(csv_content: str) -> List[Card]:
    """
    Parse cards CSV content into Card objects.
    """
    cards = []
    reader = csv.DictReader(csv_content.splitlines())

    for row in reader:
        card = Card(
            name=row[CardsCsvHeaders.NAME.value],
            type=CARD_TYPE_MAP[row[CardsCsvHeaders.TYPE.value]],
            age=int(row[CardsCsvHeaders.AGE.value]),
            min_players=int(row[CardsCsvHeaders.MIN_PLAYERS.value]),
            cost=parse_cost(row[CardsCsvHeaders.COST.value]),
            chain_to=(
                row[CardsCsvHeaders.CHAIN_TO.value].split(";")
                if row[CardsCsvHeaders.CHAIN_TO.value]
                else []
            ),
            effect=row[CardsCsvHeaders.EFFECT.value],
        )
        cards.append(card)

    return cards


def parse_wonder_stages(stages_str: str) -> List[WonderStage]:
    """
    Parse wonder stages string into WonderStage objects.
    Format: [[cost;effect];[cost;effect];...]
    """

    stage_patterns = stages_str.split("|")

    stages = []
    for pattern in stage_patterns:
        cost_str, effect = pattern.split(";")
        cost = parse_cost(cost_str)
        stages.append(WonderStage(cost=cost, effect=effect))

    return stages


def parse_wonders(csv_content: str, day: bool = True) -> List[Wonder]:
    """
    Parse wonders CSV content into Wonder objects.
    """
    wonders = []
    reader = csv.DictReader(csv_content.splitlines())

    for row in reader:
        name = row[WondersCsvHeaders.NAME.value]
        resource = RESOURCE_MAP[row[WondersCsvHeaders.RESOURCE.value]]
        stages_str = (
            row[WondersCsvHeaders.DAY_STAGES.value]
            if day
            else row[WondersCsvHeaders.NIGHT_STAGES.value]
        )

        stages = parse_wonder_stages(stages_str)
        wonder = Wonder(name=name, resource=resource, stages=stages)
        wonders.append(wonder)

    return wonders


def parse_cost(cost_str: str) -> Dict[Resource, int]:
    """
    Parse cost string into a dictionary.
    Format: {resource: amount, ...}
    """
    cost: Dict[Resource, int] = {}

    if not cost_str:
        return cost

    for letter in cost_str:
        resource = RESOURCE_MAP[letter]
        cost[resource] = cost.get(resource, 0) + 1

    return cost
