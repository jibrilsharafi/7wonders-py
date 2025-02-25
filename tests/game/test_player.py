import pytest
from src.game.player import Player
from src.core.types import Wonder, WonderStage, Card
from src.core.enums import Resource, CardType, Action
from typing import List


@pytest.fixture
def test_wonder() -> Wonder:
    stages = [
        WonderStage({Resource.WOOD: 2}, "V3"),
        WonderStage({Resource.STONE: 2}, "V5"),
    ]
    return Wonder("TestWonder", Resource.WOOD, stages)


@pytest.fixture
def test_player(test_wonder: Wonder) -> Player:
    return Player("TestPlayer", test_wonder)


@pytest.fixture
def sample_card() -> Card:
    return Card("TestCard", CardType.RAW_MATERIAL, 1, 3, {}, None, "W")


def test_player_initialization(test_player: Player) -> None:
    assert test_player.name == "TestPlayer"
    assert test_player.coins == 3
    assert test_player.military_tokens == 0
    assert test_player.stages_built == 0
    assert len(test_player.cards) == 0


def test_player_add_card(test_player: Player, sample_card: Card) -> None:
    test_player.add_card(sample_card)
    assert len(test_player.cards) == 1
    assert test_player.cards[0] == sample_card

    # Test duplicate card
    with pytest.raises(AssertionError):
        test_player.add_card(sample_card)


def test_player_add_coins(test_player: Player) -> None:
    test_player.add_coins(2)
    assert test_player.coins == 5

    test_player.add_coins(-3)
    assert test_player.coins == 2

    with pytest.raises(AssertionError):
        test_player.add_coins(-3)  # Would make coins negative


def test_player_allowed_actions(test_player: Player, sample_card: Card) -> None:
    cards_hand: List[Card] = [sample_card]

    # Initially can play or discard
    actions = test_player.get_allowed_actions(cards_hand)
    assert Action.PLAY in actions
    assert Action.DISCARD in actions

    # After playing card, can't play it again
    test_player.add_card(sample_card)
    actions = test_player.get_allowed_actions(cards_hand)
    assert Action.PLAY not in actions
    assert Action.DISCARD in actions


def test_player_wonder_building(test_player: Player) -> None:
    assert test_player.can_build_wonder()

    test_player.add_stage()
    assert test_player.stages_built == 1
    assert test_player.can_build_wonder()

    test_player.add_stage()
    assert test_player.stages_built == 2
    assert not test_player.can_build_wonder()


def test_player_resources(test_player: Player) -> None:
    wood_card = Card("Wood", CardType.RAW_MATERIAL, 1, 3, {}, None, "W")
    stone_card = Card("Stone", CardType.RAW_MATERIAL, 1, 3, {}, None, "SS")

    test_player.add_card(wood_card)
    resources = test_player.get_resources()
    assert resources == {Resource.WOOD: 1}

    test_player.add_card(stone_card)
    resources = test_player.get_resources()
    assert resources == {Resource.WOOD: 1, Resource.STONE: 2}
