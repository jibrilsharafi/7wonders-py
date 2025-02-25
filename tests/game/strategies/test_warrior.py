import logging

import pytest

from src.core.enums import Action, CardType, Resource
from src.core.types import Card, Wonder, WonderStage
from src.game.player import Player
from src.game.state import GameState
from src.game.strategies.warrior.warrior import WarriorStrategy

logger = logging.getLogger(__name__)


@pytest.fixture
def strategy() -> WarriorStrategy:
    return WarriorStrategy()


@pytest.fixture
def wonder() -> Wonder:
    stages = [
        WonderStage({Resource.WOOD: 1}, "M"),  # Military stage
        WonderStage({Resource.WOOD: 1}, "MMM"),
        WonderStage({Resource.WOOD: 10}, "VV"),
    ]
    return Wonder("Test Wonder", Resource.WOOD, stages)


@pytest.fixture
def player(wonder: Wonder) -> Player:
    return Player("Test Player", wonder, WarriorStrategy())


@pytest.fixture
def sample_cards() -> list[Card]:
    return [
        Card("Shields2", CardType.MILITARY, 1, 3, {}, None, "MM"),  # 2 shields
        Card("Shields1", CardType.MILITARY, 1, 3, {}, None, "M"),  # 1 shield
        Card("NoShields", CardType.CIVILIAN, 1, 3, {}, None, "VVV"),  # 0 shields
    ]


@pytest.fixture
def sample_costly_card() -> Card:
    return Card(
        "Costly Card", CardType.RAW_MATERIAL, 1, 3, {Resource.WOOD: 10}, None, "SSS"
    )


@pytest.fixture
def game_state(player: Player) -> GameState:
    return GameState([player])


def test_prioritizes_most_shields(
    strategy: WarriorStrategy,
    player: Player,
    game_state: GameState,
    sample_cards: list[Card],
) -> None:
    """Should choose the move that provides the most shields"""
    player.add_to_hand(sample_cards)

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.PLAY
    assert chosen.card.effect.count("M") == 2  # Should pick card with 2 shields


def test_wonder_stage_with_shields(
    strategy: WarriorStrategy,
    game_state: GameState,
    player: Player,
    sample_cards: list[Card],
) -> None:
    """Should consider wonder stages that provide shields"""
    player.add_to_hand(sample_cards)
    player.add_stage()  # Go to stage two which provides more shields

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.WONDER  # Should choose wonder stage


def test_fallback_when_no_military(
    strategy: WarriorStrategy,
    player: Player,
    game_state: GameState,
    sample_costly_card: Card,
) -> None:
    """Should default to first move when no military options available"""
    player.add_to_hand([sample_costly_card])
    player.add_stage()
    player.add_stage()  # Go to the last unaffordable stage

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.DISCARD  # Should discard the card
