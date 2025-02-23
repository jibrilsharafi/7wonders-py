import pytest
from src.utils.parsers import (
    parse_cost,
    parse_cards,
    parse_wonders,
    parse_wonder_stages,
)
from src.core.enums import Resource, CardType


def test_parse_cost() -> None:
    # Test empty string
    assert parse_cost("") == {}

    # Test single resource
    assert parse_cost("W") == {Resource.WOOD: 1}

    # Test multiple resources
    assert parse_cost("WS") == {Resource.WOOD: 1, Resource.STONE: 1}

    # With coins
    assert parse_cost("$$") == {Resource.COIN: 2}

    # Test all resources
    complex_cost = "WSOFBPL"
    expected = {
        Resource.WOOD: 1,
        Resource.STONE: 1,
        Resource.ORE: 1,
        Resource.BRICK: 1,
        Resource.GLASS: 1,
        Resource.PAPYRUS: 1,
        Resource.LOOM: 1,
    }
    assert parse_cost(complex_cost) == expected

    # Test different amounts
    assert parse_cost("WWWWW") == {Resource.WOOD: 5}

    # Test multiple same resource
    assert parse_cost("WWS") == {Resource.WOOD: 2, Resource.STONE: 1}

    # Test mixed multiple resources
    assert parse_cost("WWSSOOL") == {
        Resource.WOOD: 2,
        Resource.STONE: 2,
        Resource.ORE: 2,
        Resource.LOOM: 1,
    }


def test_parse_cost_invalid_input() -> None:
    # Test invalid character
    with pytest.raises(KeyError):
        parse_cost("X")


def test_parse_cards() -> None:
    csv_content = """age,min_players,name,type,cost,chain_to,effect
1,3,Lumber Yard,raw_material,,,W
1,4,Stone Pit,raw_material,,,S
2,3,Glassworks,manufactured_good,,,F
3,3,Workers Guild,guild,WWLL,,guild_effect"""

    cards = parse_cards(csv_content)

    assert len(cards) == 4

    # Test first card
    assert cards[0].name == "Lumber Yard"
    assert cards[0].type == CardType.RAW_MATERIAL
    assert cards[0].age == 1
    assert cards[0].min_players == 3
    assert cards[0].cost == {}
    assert cards[0].chain_to is None
    assert cards[0].effect == "W"

    # Test second card
    assert cards[1].name == "Stone Pit"
    assert cards[1].type == CardType.RAW_MATERIAL
    assert cards[1].age == 1
    assert cards[1].min_players == 4
    assert cards[1].cost == {}
    assert cards[1].chain_to is None
    assert cards[1].effect == "S"

    # Test third card
    assert cards[2].name == "Glassworks"
    assert cards[2].type == CardType.MANUFACTURED_GOOD
    assert cards[2].age == 2
    assert cards[2].min_players == 3
    assert cards[2].cost == {}
    assert cards[2].chain_to is None
    assert cards[2].effect == "F"

    # Test fourth card
    assert cards[3].name == "Workers Guild"
    assert cards[3].type == CardType.GUILD
    assert cards[3].age == 3
    assert cards[3].min_players == 3
    assert cards[3].cost == {Resource.WOOD: 2, Resource.LOOM: 2}
    assert cards[3].chain_to is None
    assert cards[3].effect == "guild_effect"


def test_parse_cards_with_chains() -> None:
    csv_content = """age,min_players,name,type,cost,chain_to,effect
2,3,Brickyard,raw_material,L,Workshop;Library,BB"""

    cards = parse_cards(csv_content)
    assert len(cards) == 1
    assert cards[0].chain_to == ["Workshop", "Library"]


def test_parse_cards_invalid_input() -> None:
    invalid_csv = """age,min_players,name,type,cost,chain_to,effect
1,3,Test Card,invalid_type,,,effect"""

    with pytest.raises(KeyError):
        parse_cards(invalid_csv)


def test_parse_wonder_stages() -> None:
    # Test simple stage
    stages = parse_wonder_stages("WW;V3")
    assert len(stages) == 1
    assert stages[0].cost == {Resource.WOOD: 2}
    assert stages[0].effect == "V3"

    # Test multiple stages
    stages = parse_wonder_stages("WW;V3|SSS;V7")
    assert len(stages) == 2
    assert stages[0].cost == {Resource.WOOD: 2}
    assert stages[0].effect == "V3"
    assert stages[1].cost == {Resource.STONE: 3}
    assert stages[1].effect == "V7"

    # Test complex cost
    stages = parse_wonder_stages("WWSSOOL;effect")
    assert stages[0].cost == {
        Resource.WOOD: 2,
        Resource.STONE: 2,
        Resource.ORE: 2,
        Resource.LOOM: 1,
    }
    assert stages[0].effect == "effect"


def test_parse_wonders() -> None:
    csv_content = """name,resource,day_stages,night_stages
giza,S,WW;V3|SSS;V7,WW;V3|SSS;V5
rhodes,O,WW;V3|OOO;M2,SS;M1"""

    # Test day side
    wonders = parse_wonders(csv_content, day=True)
    assert len(wonders) == 2

    # Check Giza
    giza = wonders[0]
    assert giza.name == "giza"
    assert giza.resource == Resource.STONE
    assert len(giza.stages) == 2
    assert giza.stages[0].cost == {Resource.WOOD: 2}
    assert giza.stages[0].effect == "V3"

    # Check Rhodes
    rhodes = wonders[1]
    assert rhodes.name == "rhodes"
    assert rhodes.resource == Resource.ORE
    assert len(rhodes.stages) == 2
    assert rhodes.stages[1].cost == {Resource.ORE: 3}
    assert rhodes.stages[1].effect == "M2"

    # Test night side
    night_wonders = parse_wonders(csv_content, day=False)
    assert night_wonders[0].stages[1].cost == {Resource.STONE: 3}
    assert night_wonders[0].stages[1].effect == "V5"


def test_parse_wonders_invalid_input() -> None:
    invalid_csv = """name,resource,day_stages,night_stages
invalid,X,WW;V3|WW;V3"""

    with pytest.raises(KeyError):
        parse_wonders(invalid_csv)


def test_parse_cards_from_resources() -> None:
    CSV_PATH = "data/cards.csv"
    with open(CSV_PATH, "r") as file:
        csv_content = file.read()

    cards = parse_cards(csv_content)
    assert len(cards) == 148

    # Test first card
    assert cards[0].name == "altar"
    assert cards[0].type == CardType.CIVILIAN
    assert cards[0].age == 1
    assert cards[0].min_players == 3
    assert cards[0].cost == {}
    assert cards[0].chain_to == ["pantheon"]
    assert cards[0].effect == "VVV"

    # Test 93th card
    assert cards[93].name == "school"
    assert cards[93].type == CardType.SCIENTIFIC
    assert cards[93].age == 2
    assert cards[93].min_players == 3
    assert cards[93].cost == {Resource.WOOD: 1, Resource.PAPYRUS: 1}
    assert cards[93].chain_to == ["academy", "study"]
    assert cards[93].effect == "T"

    # Test 127th card
    assert cards[127].name == "decorators_guild"
    assert cards[127].type == CardType.GUILD
    assert cards[127].age == 3
    assert cards[127].min_players == 1
    assert cards[127].cost == {Resource.ORE: 2, Resource.STONE: 1, Resource.LOOM: 1}
    assert cards[127].chain_to == None
    assert cards[127].effect == "V-{wonders_complete}"


# now wonders csv
def test_parse_wonders_from_resources() -> None:
    CSV_PATH = "data/wonders.csv"
    with open(CSV_PATH, "r") as file:
        csv_content = file.read()

    wonders = parse_wonders(csv_content)
    assert len(wonders) == 7

    # Test second wonder
    assert wonders[1].name == "babylon"
    assert wonders[1].resource == Resource.WOOD
    assert len(wonders[1].stages) == 3
    assert wonders[1].stages[1].cost == {Resource.ORE: 2, Resource.LOOM: 1}
    assert wonders[1].stages[1].effect == "+science{C/T/G}"

    # Test 4th wonder
    assert wonders[4].name == "halicarnassus"
    assert wonders[4].resource == Resource.LOOM
    assert len(wonders[4].stages) == 3
    assert wonders[4].stages[1].cost == {Resource.GLASS: 1, Resource.PAPYRUS: 1}
    assert wonders[4].stages[1].effect == "build_discard"

    # Test 6th wonder
    assert wonders[6].name == "rhodes"
    assert wonders[6].resource == Resource.ORE
    assert len(wonders[6].stages) == 3
    assert wonders[6].stages[2].cost == {Resource.ORE: 4}
    assert wonders[6].stages[2].effect == "VVVVVVV"

    # Test night
    night_wonders = parse_wonders(csv_content, day=False)

    # Test first night wonder
    assert night_wonders[0].name == "alexandria"
    assert night_wonders[0].resource == Resource.GLASS
    assert len(night_wonders[0].stages) == 3
    assert night_wonders[0].stages[0].cost == {Resource.BRICK: 2}
    assert night_wonders[0].stages[0].effect == "+resource{W/S/O/B}"
