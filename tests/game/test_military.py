import pytest
from src.game.player import Player
from src.core.types import Card, Wonder
from src.core.enums import Resource, CardType
from src.game.military import (
    calculate_battle,
    calculate_military_outcome,
    resolve_military_conflicts,
    apply_military_tokens,
)
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


@pytest.fixture
def three_players() -> List[Player]:
    p1 = Player("P1", Wonder("W1", Resource.WOOD, []))
    p2 = Player("P2", Wonder("W2", Resource.BRICK, []))
    p3 = Player("P3", Wonder("W3", Resource.STONE, []))
    return [p1, p2, p3]


def test_calculate_battle() -> None:
    """Test single battle calculations"""
    # Age 1 battles
    assert calculate_battle(1, 0, 1) == 1  # Win
    assert calculate_battle(0, 1, 1) == -1  # Loss
    assert calculate_battle(1, 1, 1) == 0  # Tie

    # Age 2 battles
    assert calculate_battle(2, 1, 2) == 3  # Win
    assert calculate_battle(1, 2, 2) == -1  # Loss

    # Age 3 battles
    assert calculate_battle(3, 1, 3) == 5  # Win
    assert calculate_battle(1, 3, 3) == -1  # Loss


def test_military_conflicts_age1(three_players: List[Player]) -> None:
    """Test military conflicts in age 1"""
    p1, p2, p3 = three_players

    # Add 1 shield to P1
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, None, "M"))

    # Calculate outcomes
    outcomes = resolve_military_conflicts(three_players, 1)

    # P1 should win against both neighbors
    assert outcomes[p1] == 2  # Two wins (+1 each)
    assert outcomes[p2] == -1  # One loss
    assert outcomes[p3] == -1  # One loss


def test_military_conflicts_age2(three_players: List[Player]) -> None:
    """Test military conflicts in age 2"""
    p1, p2, p3 = three_players

    # P1: 1 shield, P2: 2 shields, P3: 0 shields
    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, None, "M"))
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, None, "MM"))

    outcomes = resolve_military_conflicts(three_players, 2)

    assert outcomes[p1] == 2  # Win vs P3 (+3), loss vs P2 (-1)
    assert outcomes[p2] == 6  # Two wins (+3 each)
    assert outcomes[p3] == -2  # Two losses (-1 each)


def test_military_conflicts_age3(three_players: List[Player]) -> None:
    """Test military conflicts in age 3"""
    p1, p2, p3 = three_players

    # P1: 3 shields, P2: 2 shields, P3: 3 shields
    p1.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, None, "MMM"))
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, None, "MM"))
    p3.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, None, "MMM"))

    outcomes = resolve_military_conflicts(three_players, 3)

    assert outcomes[p1] == 5  # Win vs P2 (+5), tie vs P3 (0)
    assert outcomes[p2] == -2  # Two losses (-1 each)
    assert outcomes[p3] == 5  # Win vs P2 (+5), tie vs P1 (0)


def test_apply_military_tokens(three_players: List[Player]) -> None:
    """Test applying military tokens to players"""
    p1, p2, p3 = three_players
    outcomes: Dict[Player, int] = {p1: 2, p2: -1, p3: -1}

    apply_military_tokens(three_players, outcomes)

    assert p1.military_tokens == 2
    assert p2.military_tokens == -1
    assert p3.military_tokens == -1
