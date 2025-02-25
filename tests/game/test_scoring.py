import pytest

from src.core.enums import CardType, Resource
from src.core.types import Card, Score, Wonder, WonderStage
from src.game.player import Player
from src.game.scoring import (
    calculate_civilian_score,
    calculate_commercial_score,
    calculate_guild_score,
    calculate_military_score,
    calculate_science_score,
    calculate_total_score,
    calculate_treasury_score,
    calculate_wonders_score,
)


@pytest.fixture
def basic_wonder() -> Wonder:
    return Wonder(
        name="test_wonder",
        resource=Resource.WOOD,
        stages=[
            WonderStage(cost={}, effect="VVV"),
            WonderStage(cost={}, effect="VVV"),
            WonderStage(cost={}, effect="VVVV"),
        ],
    )


@pytest.fixture
def basic_player(basic_wonder: Wonder) -> Player:
    return Player(name="test_player", wonder=basic_wonder)


def test_military_score(basic_player: Player) -> None:
    basic_player.add_military_tokens(5)
    assert calculate_military_score(basic_player) == 5


def test_treasury_score(basic_player: Player) -> None:
    basic_player.coins = 0
    basic_player.add_coins(11)  # Should give 3 points (11 // 3)
    assert calculate_treasury_score(basic_player) == 3


def test_wonders_score(basic_player: Player) -> None:
    basic_player.add_stage()
    basic_player.add_stage()
    assert calculate_wonders_score(basic_player) == 6  # Two stages with VVV each


def test_civilian_score(basic_player: Player) -> None:
    civilian_card1 = Card(
        name="test_civil1",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="VVV",
    )
    civilian_card2 = Card(
        name="test_civil2",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="VVVV",
    )
    basic_player.add_card(civilian_card1)
    basic_player.add_card(civilian_card2)
    assert calculate_civilian_score(basic_player) == 7


def test_science_score(basic_player: Player) -> None:
    # Test with 2 of each symbol (no jokers)
    basic_player.cards = [
        Card(
            name="test_science1",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="C",
        ),
        Card(
            name="test_science2",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="C",
        ),
        Card(
            name="test_science3",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="T",
        ),
        Card(
            name="test_science4",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="T",
        ),
        Card(
            name="test_science5",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="G",
        ),
        Card(
            name="test_science6",
            type=CardType.SCIENTIFIC,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="G",
        ),
    ]
    # Score should be: (2^2 + 2^2 + 2^2) + (2 * 7) = 12 + 14 = 26
    assert calculate_science_score(basic_player) == 26


def test_commercial_score(basic_player: Player) -> None:
    basic_player.cards = [
        Card(
            name="test_commercial",
            type=CardType.COMMERCIAL,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="VV-{wonder}",
        ),
    ]
    basic_player.stages_built = 2
    assert calculate_commercial_score(basic_player) == 4  # 2 stages * 2 points


def test_guild_score() -> None:
    wonder = Wonder(
        name="test_wonder",
        resource=Resource.WOOD,
        stages=[WonderStage(cost={}, effect="VVV")],
    )

    player1 = Player(name="p1", wonder=wonder)
    player2 = Player(name="p2", wonder=wonder)
    player3 = Player(name="p3", wonder=wonder)

    # Add some cards to neighbors
    civilian_card = Card(
        name="test_civil",
        type=CardType.CIVILIAN,
        age=1,
        min_players=3,
        cost={},
        chain_to=None,
        effect="VVV",
    )

    player2.cards = [civilian_card, civilian_card]  # Left neighbor
    player3.cards = [civilian_card]  # Right neighbor

    # Add guild card to main player
    player1.cards = [
        Card(
            name="test_guild",
            type=CardType.GUILD,
            age=3,
            min_players=3,
            cost={},
            chain_to=None,
            effect="V-{civilian}_<>",
        )
    ]

    assert calculate_guild_score(player1, player2, player3) == 3


def test_total_score(basic_player: Player) -> None:
    # Set up a complete scoring scenario
    basic_player.military_tokens = 5
    basic_player.coins = 9
    basic_player.stages_built = 2
    basic_player.cards = [
        Card(
            name="test_civil",
            type=CardType.CIVILIAN,
            age=1,
            min_players=3,
            cost={},
            chain_to=None,
            effect="VVV",
        ),
    ]

    score = calculate_total_score(basic_player, basic_player, basic_player)

    assert isinstance(score, Score)
    assert score.military == 5
    assert score.treasury == 3
    assert score.wonders == 6
    assert score.civilian == 3
    assert score.scientific == 0
    assert score.commercial == 0
    assert score.guilds == 0
    assert score.total == 17
