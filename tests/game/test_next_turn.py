import logging

import pytest

from src.core.enums import CardType, Resource
from src.core.types import Card, Wonder
from src.game.game_state import GameState
from src.game.player import Player
from src.game.strategies.simple.simple import SimpleStrategy

logger = logging.getLogger(__name__)


@pytest.fixture
def turn_game() -> GameState:
    players = [
        Player("P1", 0, Wonder("W1", Resource.WOOD, []), SimpleStrategy()),
        Player("P2", 1, Wonder("W2", Resource.BRICK, []), SimpleStrategy()),
        Player("P3", 2, Wonder("W3", Resource.STONE, []), SimpleStrategy()),
    ]
    return GameState(players, [])


def test_hand_rotation_age1(turn_game: GameState) -> None:
    """Test clockwise hand rotation in age 1"""
    p1_cards = [
        Card("C1", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
        Card("C4", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
        Card("C7", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
    ]
    p2_cards = [
        Card("C2", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
        Card("C5", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
        Card("C8", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
    ]
    p3_cards = [
        Card("C3", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
        Card("C6", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
        Card("C9", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
    ]

    turn_game.all_players[0].add_to_hand(p1_cards)
    turn_game.all_players[1].add_to_hand(p2_cards)
    turn_game.all_players[2].add_to_hand(p3_cards)

    turn_game.next_turn()

    # In age 1, hands should rotate clockwise
    assert turn_game.all_players[0].hand == p2_cards
    assert turn_game.all_players[1].hand == p3_cards
    assert turn_game.all_players[2].hand == p1_cards


def test_hand_rotation_age2(turn_game: GameState) -> None:
    """Test counter-clockwise hand rotation in age 2"""
    turn_game.age = 2
    # Similar to above but counter-clockwise

    p1_cards = [
        Card("C1", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
        Card("C4", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
        Card("C7", CardType.RAW_MATERIAL, 1, 3, {}, [], "W"),
    ]
    p2_cards = [
        Card("C2", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
        Card("C5", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
        Card("C8", CardType.RAW_MATERIAL, 1, 3, {}, [], "S"),
    ]
    p3_cards = [
        Card("C3", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
        Card("C6", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
        Card("C9", CardType.RAW_MATERIAL, 1, 3, {}, [], "O"),
    ]

    turn_game.all_players[0].add_to_hand(p1_cards)
    turn_game.all_players[1].add_to_hand(p2_cards)
    turn_game.all_players[2].add_to_hand(p3_cards)

    turn_game.next_turn()

    # In age 2, hands should rotate counter-clockwise
    assert turn_game.all_players[0].hand == p3_cards
    assert turn_game.all_players[1].hand == p1_cards
    assert turn_game.all_players[2].hand == p2_cards


def test_military_conflict_end_age(turn_game: GameState) -> None:
    """Test military conflicts at end of age"""
    p1 = turn_game.all_players[0]
    p2 = turn_game.all_players[1]
    p3 = turn_game.all_players[2]

    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, [], "M"))

    # P1: M, P2: , P3:
    turn_game.next_turn()

    assert p1.military_tokens == 2  # W, W (+2)
    assert p2.military_tokens == -1  # L, D (-1)
    assert p3.military_tokens == -1  # D, L (-1)

    turn_game.age = 2

    logger.info(
        f"First age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )

    # Now give player 2 a military card
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))

    # P1: M, P2: MM, P3:
    turn_game.next_turn()

    assert p1.military_tokens == 4  # W, L (+2)
    assert p2.military_tokens == 5  # W, W (+6)
    assert p3.military_tokens == -3  # L, L (-2)

    logger.info(
        f"Second age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )

    turn_game.age = 3

    # Now give player 3 a military card
    p1.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, [], "MM"))
    p3.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, [], "MMM"))

    # P1: MMM, P2: MM, P3: MMM
    turn_game.next_turn()
    assert p1.military_tokens == 9  # D, W (+5)
    assert p2.military_tokens == 3  # L, L (-2)
    assert p3.military_tokens == 2  # W, D (+5)
    logger.info(
        f"Third age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )
