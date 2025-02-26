from typing import List
from src.core.types import Card, CardType
from src.utils.validators import (
    can_card_be_chained,
    drop_duplicates_cards,
    get_left_in_list,
    get_random_cards,
    get_right_in_list,
    is_card_present,
)


def test_is_card_present() -> None:
    card1: Card = Card(
        name="test1",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    card2: Card = Card(
        name="test2",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    cards: List[Card] = [card1]

    assert is_card_present(cards, card1) is True
    assert is_card_present(cards, card2) is False


def test_can_card_be_chained() -> None:
    card1: Card = Card(
        name="test1",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=["test2"],
        effect="",
    )
    card2: Card = Card(
        name="test2",
        type=CardType.CIVILIAN,
        age=2,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    card3: Card = Card(
        name="test3",
        type=CardType.CIVILIAN,
        age=2,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    cards: List[Card] = [card1]

    assert can_card_be_chained(cards, card2) is True
    assert can_card_be_chained(cards, card3) is False


def test_drop_duplicates_cards() -> None:
    card1: Card = Card(
        name="test1",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    card2: Card = Card(
        name="test1",
        type=CardType.CIVILIAN,
        age=2,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    cards: List[Card] = [card1, card2]

    result: List[Card] = drop_duplicates_cards(cards)
    assert len(result) == 1
    assert result[0].age == 1


def test_get_random_cards() -> None:
    card1: Card = Card(
        name="test1",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="",
    )
    card2: Card = Card(
        name="test2",
        type=CardType.MILITARY,
        age=2,
        min_players=4,
        cost={},
        chain_to=None,
        effect="",
    )
    cards: List[Card] = [card1, card2]

    result: List[Card] = get_random_cards(cards, 1)
    assert len(result) == 1

    result = get_random_cards(cards, 1, filter_age=[1])
    assert len(result) == 1
    assert result[0].age == 1

    result = get_random_cards(cards, 1, filter_min_players=[4])
    assert len(result) == 1
    assert result[0].min_players == 4

    result = get_random_cards(cards, 1, filter_type=[CardType.MILITARY])
    assert len(result) == 1
    assert result[0].type == CardType.MILITARY


def test_get_left_in_list() -> None:
    assert get_left_in_list(1, 3) == 0
    assert get_left_in_list(0, 3) == 2
    assert get_left_in_list(2, 3) == 1


def test_get_right_in_list() -> None:
    assert get_right_in_list(1, 3) == 2
    assert get_right_in_list(2, 3) == 0
    assert get_right_in_list(0, 3) == 1
