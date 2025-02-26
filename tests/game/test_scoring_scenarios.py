import logging
from typing import List

import pytest

from src.core.enums import CardType
from src.core.types import Card, Resource, Wonder
from src.game.player import Player, get_left_neighbor, get_right_neighbor
from src.game.strategies.simple.simple import SimpleStrategy
from src.game.scoring import (
    calculate_commercial_score,
    calculate_guild_score,
    calculate_military_score,
    calculate_science_score,
    calculate_total_score,
)
from src.utils.parsers import parse_cards, parse_wonders
from src.utils.validators import (
    drop_duplicates_cards,
    get_random_cards,
    is_card_present,
)


@pytest.fixture
def cards() -> List[Card]:
    with open("data/cards.csv", "r") as f:
        return parse_cards(f.read())


@pytest.fixture
def wonders() -> List[Wonder]:
    with open("data/wonders.csv", "r") as f:
        return parse_wonders(f.read())


@pytest.fixture
def babylon_player(wonders: List[Wonder]) -> Player:
    """Player with Babylon wonder (has science symbol in second stage)"""
    babylon = next(w for w in wonders if w.name == "babylon")
    return Player("babylon_player", 0, babylon, SimpleStrategy())


@pytest.fixture
def alexandria_player(wonders: List[Wonder]) -> Player:
    """Player with Alexandria wonder (has resource choice effects)"""
    alexandria = next(w for w in wonders if w.name == "alexandria")
    return Player("alexandria_player", 1, alexandria, SimpleStrategy())


def test_science_score_with_babylon(babylon_player: Player, cards: List[Card]) -> None:
    """Test science scoring with Babylon's science symbol and multiple cards"""
    # Add scientific cards
    scientific_cards = [
        card
        for card in cards
        if card.type == CardType.SCIENTIFIC
        and card.name
        in ["apothecary", "workshop", "scriptorium", "dispensary", "school"] # scientific
    ]
    # Discard duplicates with the same name
    scientific_cards = drop_duplicates_cards(scientific_cards)

    for card in scientific_cards:
        babylon_player.add_card(card)

    # Build two stages (second stage gives science symbol choice)
    babylon_player.add_stage()
    babylon_player.add_stage()

    # 2^2 + 2^2 + 2^(1 base + 1 jolly from second stage) + 7 * 3 = 26
    assert calculate_science_score(babylon_player) == 26


def test_commercial_score_with_real_cards(
    babylon_player: Player, cards: List[Card]
) -> None:
    """Test commercial scoring with actual yellow cards"""
    # Add cards
    relevant_cards = [
        card
        for card in cards
        if card.name
        in [
            "haven", # Commercial
            "chamber_of_commerce", # Commercial
            "lumber_yard", # Raw materials
            "ore_vein", # Raw materials
            "clay_pool", # Raw materials
            "loom", # Manufactured goods
            "glassworks", # Manufactured goods
        ]
    ]

    relevant_cards = drop_duplicates_cards(relevant_cards)

    for card in relevant_cards:
        babylon_player.add_card(card)

    # Haven: V per raw material, Chamber of Commerce: VV per manufactured good
    # 1 * 3 + 2 * 2 = 7
    assert calculate_commercial_score(babylon_player) == 7


def test_guild_score_complex_scenario(cards: List[Card], wonders: List[Wonder]) -> None:
    """Test guild scoring with multiple players and different guild types"""
    p1 = Player(
        "p1", 0, next(w for w in wonders if w.name == "alexandria"), SimpleStrategy()
    )
    p2 = Player(
        "p2", 1, next(w for w in wonders if w.name == "babylon"), SimpleStrategy()
    )
    p3 = Player(
        "p3", 2, next(w for w in wonders if w.name == "rhodes"), SimpleStrategy()
    )

    # Add cards to neighbors
    for card in cards:
        if card.name in [
            "haven",  # Commercial
            "chamber_of_commerce",  # Commercial
            "builders_guild",  # Guild
            "philosophers_guild",  # Guild
            "decorators_guild",  # Guild
        ] and not is_card_present(p1.cards, card):
            p1.add_card(card)
        elif card.name in [
            "library",  # Scientific
            "laboratory",  # Scientific
            "study",  # Scientific
            "altar",  # Civilian
            "theatre",  # Civilian
            "craftsmens_guild",  # Guild
        ] and not is_card_present(p2.cards, card):
            p2.add_card(card)
        elif card.name in [
            "stockade",  # Military
            "barracks",  # Military
            "lumber_yard",  # Raw materials
            "clay_pool",  # Raw materials
            "shipowners_guild",  # Guild
        ] and not is_card_present(p3.cards, card):
            p3.add_card(card)

    # Add stages to players
    for player in [p1, p2, p3]:
        player.add_stage()
        player.add_stage()

    # Add last stage to p1 (complete wonder)
    p1.add_stage()

    assert (
        calculate_guild_score(
            p1,
            get_left_neighbor(p1.position, [p1, p2, p3]),
            get_right_neighbor(p1.position, [p1, p2, p3]),
        )
        == 17 # builders_guild: V per wonder <v> (1 * (3 + 2 + 2)), philosophers_guild: V per science symbol <> (1 * 3), decorators_guild: VVVVVVV per wonders complete (7 * 1)
    )
    assert (
        calculate_guild_score(
            p2,
            get_left_neighbor(p2.position, [p1, p2, p3]),
            get_right_neighbor(p2.position, [p1, p2, p3]),
        )
        == 0
    )
    assert (
        calculate_guild_score(
            p3,
            get_left_neighbor(p3.position, [p1, p2, p3]),
            get_right_neighbor(p3.position, [p1, p2, p3]),
        )
        == 3 # shipowners_guild: V per raw material, manufactured good, guild (1 * 3)
    )


def test_military_conflict_complete_game(cards: List[Card]) -> None:
    """Test military scoring through all ages"""
    player = Player("test", 1, Wonder("test", Resource.WOOD, []), SimpleStrategy())

    # Add military cards
    military_cards = [
        card
        for card in cards
        if card.type == CardType.MILITARY
        and card.name in ["stockade", "walls", "fortification"]
    ]
    military_cards = drop_duplicates_cards(military_cards)

    for card in military_cards:
        player.add_card(card)

    player.add_military_tokens(9)
    assert calculate_military_score(player) == 9


def test_complete_game_scoring_scenario(
    cards: List[Card], wonders: List[Wonder]
) -> None:
    """Test a complete game scoring scenario with multiple players"""
    science_player = Player(
        "science", 0, next(w for w in wonders if w.name == "babylon"), SimpleStrategy()
    )
    military_player = Player(
        "military", 1, next(w for w in wonders if w.name == "rhodes"), SimpleStrategy()
    )
    civilian_player = Player(
        "civilian", 2, next(w for w in wonders if w.name == "giza"), SimpleStrategy()
    )

    # Set up science player
    list_science_cards = get_random_cards(
        cards, 7, filter_type=[CardType.SCIENTIFIC], unique=True
    )
    for card in list_science_cards:
        science_player.add_card(card)
    science_player.add_stage()
    science_player.add_stage()

    # Set up military player
    list_military_cards = get_random_cards(
        cards, 6, filter_type=[CardType.MILITARY], unique=True
    )
    for card in list_military_cards:
        military_player.add_card(card)
    military_player.add_military_tokens(12)
    military_player.add_stage()
    military_player.add_stage()
    military_player.add_stage()

    # Set up civilian player
    list_civilian_cards = get_random_cards(
        cards, 7, filter_type=[CardType.CIVILIAN], unique=True
    )
    for card in list_civilian_cards:
        civilian_player.add_card(card)
    civilian_player.add_stage()
    civilian_player.add_stage()
    civilian_player.add_stage()
    civilian_player.add_coins(12)

    all_players = [science_player, military_player, civilian_player]

    # Get final scores
    science_score = calculate_total_score(
        science_player,
        get_left_neighbor(science_player.position, all_players),
        get_right_neighbor(science_player.position, all_players),
    )
    military_score = calculate_total_score(
        military_player,
        get_left_neighbor(military_player.position, all_players),
        get_right_neighbor(military_player.position, all_players),
    )
    civilian_score = calculate_total_score(
        civilian_player,
        get_left_neighbor(civilian_player.position, all_players),
        get_right_neighbor(civilian_player.position, all_players),
    )
    logging.info(f"Science player: {science_score.total} | {science_score}")
    logging.info(f"Military player: {military_score.total} | {military_score}")
    logging.info(f"Civilian player: {civilian_score.total} | {civilian_score}")

    # Assert general expectations
    assert science_score.scientific > military_score.scientific
    assert military_score.military > civilian_score.military
    assert civilian_score.civilian > science_score.civilian

    # Assert each player's main strategy contributed significantly to their score
    assert science_score.scientific >= 20
    assert military_score.military >= 12
    assert civilian_score.civilian >= 15
