import logging
from typing import Dict, List

import pytest

from src.core.enums import CardType, Resource
from src.core.types import Card, Wonder
from src.game.military import (
    apply_military_tokens_to_all,
    calculate_battle,
    calculate_military_outcome,
    resolve_military_conflicts,
)
from src.core.constants import MILITARY_DEFEAT_TOKEN, AGE_MILITARY_TOKENS
from src.game.player import Player
from src.game.strategies.simple.simple import SimpleStrategy

logger = logging.getLogger(__name__)


@pytest.fixture
def three_players() -> List[Player]:
    p1 = Player("P1", 0, Wonder("W1", Resource.WOOD, []), SimpleStrategy())
    p2 = Player("P2", 1, Wonder("W2", Resource.BRICK, []), SimpleStrategy())
    p3 = Player("P3", 2, Wonder("W3", Resource.STONE, []), SimpleStrategy())
    return [p1, p2, p3]


def test_calculate_battle() -> None:
    """Test single battle calculations"""
    # Age 1 battles
    age = 1
    assert calculate_battle(1, 0, age) == AGE_MILITARY_TOKENS[age]  # Win
    assert calculate_battle(0, 1, age) == MILITARY_DEFEAT_TOKEN  # Loss
    assert calculate_battle(1, 1, age) == 0  # Tie

    # Age 2 battles
    age = 2
    assert calculate_battle(2, 1, age) == AGE_MILITARY_TOKENS[age]  # Win
    assert calculate_battle(1, 2, age) == MILITARY_DEFEAT_TOKEN  # Loss

    # Age 3 battles
    age = 3
    assert calculate_battle(3, 1, age) == AGE_MILITARY_TOKENS[age]  # Win
    assert calculate_battle(1, 3, age) == MILITARY_DEFEAT_TOKEN  # Loss


def test_calculate_battle_invalid_age() -> None:
    """Test battle calculations with invalid ages"""
    with pytest.raises(KeyError):
        calculate_battle(1, 0, 0)  # Age 0 doesn't exist
    with pytest.raises(KeyError):
        calculate_battle(1, 0, 4)  # Age 4 doesn't exist


def test_calculate_military_outcome(three_players: List[Player]) -> None:
    """Test calculating military outcomes for a player"""
    p1, p2, p3 = three_players

    # P1: 1 shield, P2: 2 shields, P3: 0 shields
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, [], "M"))
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))

    logging.info(f"p1: {p1.get_shields()} shields")
    logging.info(f"p2: {p2.get_shields()} shields")
    logging.info(f"p3: {p3.get_shields()} shields")

    age = 1

    # P1 should win against P3 and lose against P2
    assert calculate_military_outcome(p1, [p2, p3], age) == 0  # W, L
    # P2 should win against P1 and P3
    assert calculate_military_outcome(p2, [p1, p3], age) == 2  # W, W
    # P3 should lose against P1 and P2
    assert calculate_military_outcome(p3, [p1, p2], age) == -2  # L, L


def test_military_conflicts_age1(three_players: List[Player]) -> None:
    """Test military conflicts in age 1"""
    p1, p2, p3 = three_players

    # Add 1 shield to P1
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, [], "M"))

    logging.info(f"p1: {p1.get_shields()} shields")
    logging.info(f"p2: {p2.get_shields()} shields")
    logging.info(f"p3: {p3.get_shields()} shields")

    # Calculate outcomes
    outcomes = resolve_military_conflicts(three_players, 1)

    logging.info(f"outcomes: {outcomes}")

    # P1 should win against both neighbors
    assert outcomes[p1] == 2  # W, W
    assert outcomes[p2] == -1  # D, L
    assert outcomes[p3] == -1  # L, D


def test_military_conflicts_age2(three_players: List[Player]) -> None:
    """Test military conflicts in age 2"""
    p1, p2, p3 = three_players

    # P1: 1 shield, P2: 2 shields, P3: 0 shields
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, [], "M"))
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))

    logging.info(f"p1: {p1.get_shields()} shields")
    logging.info(f"p2: {p2.get_shields()} shields")
    logging.info(f"p3: {p3.get_shields()} shields")

    outcomes = resolve_military_conflicts(three_players, 2)

    logging.info(f"outcomes: {outcomes}")

    assert outcomes[p1] == 2  # W, L
    assert outcomes[p2] == 6  # W, W
    assert outcomes[p3] == -2  # L, L


def test_military_conflicts_age3(three_players: List[Player]) -> None:
    """Test military conflicts in age 3"""
    p1, p2, p3 = three_players

    # P1: 3 shields, P2: 2 shields, P3: 3 shields
    p1.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, [], "MMM"))
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))
    p3.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, [], "MMM"))

    outcomes = resolve_military_conflicts(three_players, 3)

    assert outcomes[p1] == 5  # W, D
    assert outcomes[p2] == -2  # L, L
    assert outcomes[p3] == 5  # W, D


def test_accumulating_military_tokens(three_players: List[Player]) -> None:
    """Test accumulating military tokens across multiple ages"""
    p1, p2, p3 = three_players

    # Age 1: P1 wins against P2 and P3
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, [], "M"))
    
    outcomes = resolve_military_conflicts(three_players, 1)

    apply_military_tokens_to_all(three_players, outcomes)
    assert p1.get_military_score() == 2 # W, W
    assert p2.get_military_score() == -1 # L, D
    assert p3.get_military_score() == -1 # D, L

    # Age 2: P2 wins against P1 and P3
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))

    outcomes = resolve_military_conflicts(three_players, 2)

    apply_military_tokens_to_all(three_players, outcomes)
    assert p1.get_military_score() == 4  # 2 + W, L
    assert p2.get_military_score() == 5  # -1 + W, W
    assert p3.get_military_score() == -3 # -1 + L, L  


def test_max_shields(three_players: List[Player]) -> None:
    """Test military conflicts with maximum possible shields"""
    p1, p2, p3 = three_players

    # Add maximum reasonable number of shields to P1
    for i in range(10):  # No game should have more than 10 military cards
        p1.add_card(Card(f"Shield_{i}", CardType.MILITARY, 1, 3, {}, [], "MMM"))

    outcomes = resolve_military_conflicts(three_players, 3)
    
    assert outcomes[p1] == 10  # Should still only get normal victory points
    assert outcomes[p2] == -1  # Normal defeat token
    assert outcomes[p3] == -1  # Normal defeat token


def test_apply_military_tokens(three_players: List[Player]) -> None:
    """Test applying military tokens to players"""
    p1, p2, p3 = three_players
    outcomes: Dict[Player, int] = {
        p1: 2,
        p2: -1,
        p3: -1,
    }

    apply_military_tokens_to_all(three_players, outcomes)

    assert p1.get_military_score() == 2
    assert p2.get_military_score() == -1
    assert p3.get_military_score() == -1
