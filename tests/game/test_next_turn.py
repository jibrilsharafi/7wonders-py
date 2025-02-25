import pytest
from src.game.state import GameState
from src.game.player import Player
from src.core.types import Card, Wonder
from src.core.enums import Resource, CardType, Action
from src.game.moves import Move
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def turn_game() -> GameState:
    players = [
        Player("P1", Wonder("W1", Resource.WOOD, [])),
        Player("P2", Wonder("W2", Resource.BRICK, [])),
        Player("P3", Wonder("W3", Resource.STONE, [])),
    ]
    return GameState(players)


def test_hand_rotation_age1(turn_game: GameState) -> None:
    """Test clockwise hand rotation in age 1"""
    p1_cards = [
        Card("C1", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("C4", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("C7", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
    ]
    p2_cards = [
        Card("C2", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
        Card("C5", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
        Card("C8", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
    ]
    p3_cards = [
        Card("C3", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
        Card("C6", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
        Card("C9", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
    ]

    turn_game.hands = {
        turn_game.players[0]: p1_cards,
        turn_game.players[1]: p2_cards,
        turn_game.players[2]: p3_cards,
    }

    turn_game.next_turn()

    # In age 1, hands should rotate clockwise
    assert turn_game.hands[turn_game.players[0]] == p3_cards
    assert turn_game.hands[turn_game.players[1]] == p1_cards
    assert turn_game.hands[turn_game.players[2]] == p2_cards


def test_hand_rotation_age2(turn_game: GameState) -> None:
    """Test counter-clockwise hand rotation in age 2"""
    turn_game.age = 2
    # Similar to above but counter-clockwise

    p1_cards = [
        Card("C1", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("C4", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("C7", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
    ]
    p2_cards = [
        Card("C2", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
        Card("C5", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
        Card("C8", CardType.RAW_MATERIAL, 1, 3, {}, None, "S"),
    ]
    p3_cards = [
        Card("C3", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
        Card("C6", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
        Card("C9", CardType.RAW_MATERIAL, 1, 3, {}, None, "O"),
    ]

    turn_game.hands = {
        turn_game.players[0]: p1_cards,
        turn_game.players[1]: p2_cards,
        turn_game.players[2]: p3_cards,
    }

    turn_game.next_turn()

    # In age 2, hands should rotate counter-clockwise
    assert turn_game.hands[turn_game.players[0]] == p2_cards
    assert turn_game.hands[turn_game.players[1]] == p3_cards
    assert turn_game.hands[turn_game.players[2]] == p1_cards


def test_military_conflict_end_age(turn_game: GameState) -> None:
    """Test military conflicts at end of age"""
    p1 = turn_game.players[0]
    p2 = turn_game.players[1]
    p3 = turn_game.players[2]

    p1.add_card(Card("Shield1", CardType.MILITARY, 1, 3, {}, None, "M"))

    # P1: M, P2: , P3:
    turn_game.next_turn()
    assert p1.military_tokens == 2 # W, W (+2)
    assert p2.military_tokens == -1 # L, D (-1)
    assert p3.military_tokens == -1 # D, L (-1)
    turn_game.next_age()
    logger.info(
        f"First age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )

    # Now give player 2 a military card
    p2.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, None, "MM"))

    # P1: M, P2: MM, P3:
    turn_game.next_turn()
    assert p1.military_tokens == 4 # W, L (+2)
    assert p2.military_tokens == 5 # W, W (+6)
    assert p3.military_tokens == -3 # L, L (-2)
    logger.info(
        f"Second age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )
    turn_game.next_age()
    
    # Now give player 3 a military card
    p1.add_card(Card("Shield2", CardType.MILITARY, 1, 3, {}, None, "MM"))
    p3.add_card(Card("Shield3", CardType.MILITARY, 1, 3, {}, None, "MMM"))
    
    # P1: MMM, P2: MM, P3: MMM
    turn_game.next_turn()
    assert p1.military_tokens == 9 # D, W (+5)
    assert p2.military_tokens == 3 # L, L (-2)
    assert p3.military_tokens == 2 # W, D (+5)
    logger.info(
        f"Third age: {p1.military_tokens}, {p2.military_tokens}, {p3.military_tokens}"
    )
