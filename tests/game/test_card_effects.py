import pytest
from src.game.state import GameState
from src.game.player import Player
from src.game.moves import Move
from src.core.types import Card, Wonder
from src.core.enums import Resource, CardType, Action


@pytest.fixture
def effect_game() -> GameState:
    players = [
        Player("P1", Wonder("W1", Resource.WOOD, [])),
        Player("P2", Wonder("W2", Resource.BRICK, [])),
    ]
    return GameState(players)


def test_resource_production(effect_game: GameState) -> None:
    """Test resource production cards"""
    player = effect_game.players[0]
    card = Card("Wood", CardType.RAW_MATERIAL, 1, 3, {}, None, "W")

    move = Move(player, Action.PLAY, card)
    effect_game.make_move(move)

    assert player.get_resources()[Resource.WOOD] == 1


def test_choice_resource_production(effect_game: GameState) -> None:
    """Test resource choice cards"""
    player = effect_game.players[0]
    card = Card("Choice", CardType.RAW_MATERIAL, 1, 3, {}, None, "W/S")

    move = Move(player, Action.PLAY, card)
    effect_game.make_move(move)

    resources = player.get_resources()
    assert Resource.WOOD in resources or Resource.STONE in resources


def test_commercial_effects(effect_game: GameState) -> None:
    """Test commercial card effects"""
    player = effect_game.players[0]
    card = Card("Market", CardType.COMMERCIAL, 1, 3, {}, None, "$$")

    initial_coins = player.coins
    move = Move(player, Action.PLAY, card)
    effect_game.make_move(move)

    assert player.coins == initial_coins + 2
