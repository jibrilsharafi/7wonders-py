import pytest
from src.game.state import GameState
from src.game.player import Player
from src.game.moves import Move
from src.core.types import Card, Wonder
from src.core.enums import Resource, CardType, Action

@pytest.fixture
def trade_game() -> GameState:
    players = [
        Player("P1", Wonder("W1", Resource.WOOD, [])),
        Player("P2", Wonder("W2", Resource.BRICK, [])),
    ]
    return GameState(players)

def test_basic_trading(trade_game: GameState) -> None:
    """Test basic resource trading"""
    p1, p2 = trade_game.players[:2]
    
    # Give p2 a resource
    p2.add_card(Card("Wood", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"))
    
    # P1 tries to build something requiring wood
    card = Card("Test", CardType.CIVILIAN, 1, 3, {Resource.WOOD: 1}, None, "V")
    p1.coins = 2
    
    assert trade_game.can_afford_cost(p1, card.cost)
    move = Move(p1, Action.PLAY, card)
    trade_game.make_move(move)
    assert p1.coins == 0  # Paid 2 coins for trade

def test_trading_with_insufficient_coins(trade_game: GameState) -> None:
    """Test trading not possible with insufficient coins"""
    p1, p2 = trade_game.players[:2]
    p2.add_card(Card("Wood", CardType.RAW_MATERIAL, 1, 3, {}, None, "W"))
    
    card = Card("Test", CardType.CIVILIAN, 1, 3, {Resource.WOOD: 1}, None, "V")
    p1.coins = 1  # Not enough for trading
    
    assert not trade_game.can_afford_cost(p1, card.cost)