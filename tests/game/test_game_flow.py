import pytest
from src.game.state import GameState
from src.game.player import Player
from src.core.types import Wonder
from src.core.enums import Resource
from src.game.strategies.simple.simple import SimpleStrategy
from src.utils.parsers import parse_cards
from src.game.scoring import calculate_total_score
import logging
import random

logger = logging.getLogger(__name__)

SEED = 42
random.seed(SEED)


@pytest.fixture
def game_state() -> GameState:
    players = [
        Player("P1", Wonder("Test1", Resource.WOOD, [])),
        Player("P2", Wonder("Test2", Resource.BRICK, [])),
        Player("P3", Wonder("Test3", Resource.STONE, [])),
    ]
    return GameState(players)


def test_game_flow(game_state: GameState) -> None:
    # Load real cards
    with open("data/cards.csv", "r") as f:
        cards = parse_cards(f.read())

    # Create strategies for players
    strategies = {player: SimpleStrategy() for player in game_state.players}

    # Play through all 3 ages
    for age in range(1, 4):
        logger.info(f"Starting age {age}")
        game_state.deal_age(cards)

        while True:
            # Each player makes a move
            for player in game_state.players:
                game_state.make_turn(player, strategies[player])

            if game_state.next_turn():
                logger.debug(f"Ending age {age}")
                break

        if game_state.next_age():
            break

    logger.info("Game completed")
    # Verify game completed
    assert game_state.age == 4

    # Compute scoring
    for player in game_state.players:
        player.score = calculate_total_score(player, game_state.players)
        logger.info(f"Player {player.name} scored {player.score.total} points")

    # Show winner
    winner = max(game_state.players, key=lambda p: p.score.total)
    logger.info(f"Player {winner.name} won with {winner.score} points")
