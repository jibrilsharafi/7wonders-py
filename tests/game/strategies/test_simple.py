import logging

import pytest

from src.core.enums import Action, CardType, Resource
from src.core.types import Card, Wonder, WonderStage
from src.game.player import Player
from src.game.state import GameState
from src.game.strategies.simple.simple import SimpleStrategy

logger = logging.getLogger(__name__)


@pytest.fixture
def strategy() -> SimpleStrategy:
    return SimpleStrategy()


@pytest.fixture
def wonder() -> Wonder:
    stages = [
        WonderStage({Resource.WOOD: 1}, "WW"),
        WonderStage({Resource.WOOD: 1}, "SSS"),
    ]
    return Wonder("Test Wonder", Resource.WOOD, stages)


@pytest.fixture
def player(wonder: Wonder) -> Player:
    return Player("Test Player", wonder, SimpleStrategy())


@pytest.fixture
def sample_cards() -> list[Card]:
    return [
        Card("Card1", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("Card2", CardType.CIVILIAN, 1, 3, {}, None, "VVV"),
        Card("Card3", CardType.MILITARY, 1, 3, {}, None, "M"),
    ]


@pytest.fixture
def sample_costly_card() -> Card:
    return Card(
        "Costly Card", CardType.RAW_MATERIAL, 1, 3, {Resource.WOOD: 10}, None, "SSS"
    )


@pytest.fixture
def game_state(player: Player) -> GameState:
    return GameState([player])


def test_prioritizes_wonder_building(
    strategy: SimpleStrategy,
    player: Player,
    game_state: GameState,
    sample_cards: list[Card],
) -> None:
    """Should choose wonder building over playing or discarding"""
    player.add_to_hand(sample_cards)

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.WONDER


def test_prioritizes_playing_when_no_wonder_possible(
    strategy: SimpleStrategy,
    player: Player,
    game_state: GameState,
    sample_cards: list[Card],
) -> None:
    """Should choose playing a card when wonder building isn't an option"""
    player.add_stage()
    player.add_to_hand(sample_cards)

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.PLAY
    assert chosen.card == sample_cards[0]


def test_falls_back_to_discard(
    strategy: SimpleStrategy,
    player: Player,
    game_state: GameState,
    sample_costly_card: Card,
) -> None:
    """Should choose discard when it's the only option"""
    player.add_stage()
    player.add_to_hand([sample_costly_card])

    chosen = strategy.choose_move(player, game_state)
    assert chosen.action == Action.DISCARD


def test_raises_on_no_valid_moves(
    strategy: SimpleStrategy, player: Player, game_state: GameState
) -> None:
    """Should raise an exception when no valid moves are available"""
    player.hand = []  # Empty the hand to ensure no valid moves

    with pytest.raises(Exception) as exc_info:
        strategy.choose_move(player, game_state)
    assert str(exc_info.value) == "No valid moves found"
