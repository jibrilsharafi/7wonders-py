import pytest
from src.game.strategies.simple.simple import SimpleStrategy
from src.game.player import Player
from src.game.player_view import PlayerView
from src.game.moves import Move
from src.core.types import Wonder, Card, WonderStage
from src.core.enums import Resource, Action, CardType


@pytest.fixture
def strategy() -> SimpleStrategy:
    return SimpleStrategy()


@pytest.fixture
def wonder() -> Wonder:
    stages = [
        WonderStage({Resource.WOOD: 1}, "WW"),
        WonderStage({Resource.STONE: 2}, "SSS"),
    ]
    return Wonder("Test Wonder", Resource.WOOD, stages)


@pytest.fixture
def player(wonder: Wonder) -> Player:
    return Player("Test Player", wonder)


@pytest.fixture
def sample_cards() -> list[Card]:
    return [
        Card("Card1", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"),
        Card("Card2", CardType.CIVILIAN, 1, 3, {}, None, "VVV"),
        Card("Card3", CardType.MILITARY, 1, 3, {}, None, "M"),
    ]


@pytest.fixture
def all_players(player: Player) -> list[Player]:
    return [player]


@pytest.fixture
def view(player: Player, all_players: list[Player]) -> PlayerView:
    return PlayerView(player, all_players)


def test_prioritizes_wonder_building(
    strategy: SimpleStrategy, view: PlayerView, player: Player, sample_cards: list[Card]
) -> None:
    """Should choose wonder building over playing or discarding"""
    moves = [
        Move(player, Action.WONDER, sample_cards[0]),
        Move(player, Action.PLAY, sample_cards[1]),
        Move(player, Action.DISCARD, sample_cards[2]),
    ]

    chosen = strategy.choose_move(view)
    assert chosen.action == Action.WONDER


def test_prioritizes_playing_when_no_wonder_possible(
    strategy: SimpleStrategy, view: PlayerView, player: Player, sample_cards: list[Card]
) -> None:
    """Should choose playing a card when wonder building isn't an option"""
    moves = [
        Move(player, Action.PLAY, sample_cards[0]),
        Move(player, Action.DISCARD, sample_cards[1]),
    ]

    chosen = strategy.choose_move(view)
    assert chosen.action == Action.PLAY


def test_falls_back_to_discard(
    strategy: SimpleStrategy, view: PlayerView, player: Player, sample_cards: list[Card]
) -> None:
    """Should choose discard when it's the only option"""
    moves = [Move(player, Action.DISCARD, sample_cards[0])]

    chosen = strategy.choose_move(view)
    assert chosen.action == Action.DISCARD


def test_raises_on_no_valid_moves(strategy: SimpleStrategy, view: PlayerView) -> None:
    """Should raise an exception when no valid moves are available"""
    view._player.hand = []  # Empty the hand to ensure no valid moves

    with pytest.raises(Exception) as exc_info:
        strategy.choose_move(view)
    assert str(exc_info.value) == "No valid moves found"
