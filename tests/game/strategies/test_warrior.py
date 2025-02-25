import pytest
from src.game.strategies.warrior.warrior import WarriorStrategy
from src.game.player import Player
from src.game.player_view import PlayerView
from src.game.moves import Move
from src.core.types import Wonder, Card, WonderStage
from src.core.enums import Resource, Action, CardType
from src.game.state import GameState


@pytest.fixture
def strategy() -> WarriorStrategy:
    return WarriorStrategy()


@pytest.fixture
def wonder() -> Wonder:
    stages = [
        WonderStage({Resource.WOOD: 1}, "M"),  # Military stage
        WonderStage({Resource.STONE: 2}, "VV"),
    ]
    return Wonder("Test Wonder", Resource.WOOD, stages)


@pytest.fixture
def player(wonder: Wonder) -> Player:
    return Player("Test Player", wonder)


@pytest.fixture
def sample_cards() -> list[Card]:
    return [
        Card("Shields2", CardType.MILITARY, 1, 3, {}, None, "MM"),  # 2 shields
        Card("Shields1", CardType.MILITARY, 1, 3, {}, None, "M"),  # 1 shield
        Card("NoShields", CardType.CIVILIAN, 1, 3, {}, None, "VVV"),  # 0 shields
    ]


@pytest.fixture
def view(player: Player) -> PlayerView:
    return PlayerView(player, GameState([player]))


def test_prioritizes_most_shields(
    strategy: WarriorStrategy,
    view: PlayerView,
    player: Player,
    sample_cards: list[Card],
) -> None:
    """Should choose the move that provides the most shields"""
    moves = [
        Move(player, Action.PLAY, sample_cards[0]),  # 2 shields
        Move(player, Action.PLAY, sample_cards[1]),  # 1 shield
        Move(player, Action.PLAY, sample_cards[2]),  # 0 shields
    ]

    chosen = strategy.choose_move(view)
    assert chosen.card.effect.count("M") == 2  # Should pick card with 2 shields


def test_wonder_stage_with_shields(
    strategy: WarriorStrategy,
    view: PlayerView,
    player: Player,
    sample_cards: list[Card],
) -> None:
    """Should consider wonder stages that provide shields"""
    moves = [
        Move(player, Action.WONDER, sample_cards[0]),  # Wonder stage with 1 shield
        Move(player, Action.PLAY, sample_cards[1]),  # Card with 1 shield
        Move(player, Action.PLAY, sample_cards[2]),  # Card with no shields
    ]

    chosen = strategy.choose_move(view)
    assert chosen.action == Action.WONDER  # Should choose wonder stage


def test_fallback_when_no_military(
    strategy: WarriorStrategy,
    view: PlayerView,
    player: Player,
    sample_cards: list[Card],
) -> None:
    """Should default to first move when no military options available"""
    moves = [
        Move(player, Action.PLAY, sample_cards[2]),  # No shields
        Move(player, Action.DISCARD, sample_cards[2]),  # No shields
    ]

    chosen = strategy.choose_move(view)
    assert chosen == moves[0]  # Should pick first available move
