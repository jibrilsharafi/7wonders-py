from logic import Player, CardType, ScienceSymbol
from typing import Dict


def calculate_final_score(player: Player) -> int:
    """Calculate final score for a player"""

    # Calculate military score
    military_score = player.military_tokens

    # Calculate civilian score
    civilian_score = calculate_civilian_score(player)

    # Calculate scientific score
    scientific_score = calculate_scientific_score(player)

    # Calculate commercial score
    commercial_score = calculate_commercial_score(player)

    # Calculate guild score
    guild_score = calculate_guild_score(player)

    # Calculate wonder score
    wonder_score = calculate_wonder_score(player)

    # Calculate total score
    total_score = (
        military_score
        + civilian_score
        + scientific_score
        + commercial_score
        + guild_score
        + wonder_score
    )

    return total_score


def calculate_civilian_score(player: Player) -> int:
    """Calculate civilian score for a player"""
    return sum(
        card.victory_points
        for card in player.cards_played
        if card.type == CardType.CIVILIAN
    )


def calculate_scientific_score(player: Player) -> int:
    """Calculate scientific score for a player"""

    # Count symbols
    symbol_counts = {symbol: 0 for symbol in ScienceSymbol}
    for card in player.cards_played:
        if card.type == CardType.SCIENTIFIC and card.science_symbol is not None:
            symbol_counts[card.science_symbol] += 1

    # Calculate score based on sets
    return _calculate_scientific_score_from_counts(symbol_counts)


def _calculate_scientific_score_from_counts(
    symbol_counts: Dict[ScienceSymbol, int]
) -> int:
    """Calculate scientific score from symbol counts"""

    # TODO: first unit tests to implement

    # Check for complete sets
    if all(count > 0 for count in symbol_counts.values()):
        return sum(count**2 for count in symbol_counts.values()) + 7 * min(
            symbol_counts.values()
        )

    # Check for incomplete sets
    return sum(count**2 for count in symbol_counts.values())


def calculate_commercial_score(player: Player) -> int:
    """Calculate commercial score for a player"""
    return sum(
        card.victory_points
        for card in player.cards_played
        if card.type == CardType.COMMERCIAL
    )
    

def calculate_guild_score(player: Player) -> int:
    """Calculate guild score for a player"""
    return sum(
        card.victory_points
        for card in player.cards_played
        if card.type == CardType.GUILD
    )
    

def calculate_wonder_score(player: Player) -> int:
    """Calculate wonder score for a player"""
    # TODO: implement also other wonder scoring rules
    return sum(stage.victory_points for stage in player.wonder.stages)
    
