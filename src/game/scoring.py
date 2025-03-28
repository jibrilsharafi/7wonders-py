from typing import Counter

from src.core.enums import CARD_TYPE_MAP, CardType, ScienceSymbol
from src.core.types import Score

from src.game.player import Player


def calculate_military_score(player: Player) -> int:
    """Calculate military score from military tokens"""
    return player.military_tokens


def calculate_treasury_score(player: Player) -> int:
    """Calculate treasury score (3 coins = 1 point)"""
    return player.coins // 3


def calculate_wonders_score(player: Player) -> int:
    """Calculate wonder score by counting victory points in built stages"""
    score = 0
    built_stages = player.stages_built

    for i in range(built_stages):
        effect = player.wonder.stages[i].effect
        score += int(effect.count("V"))

    return score


def calculate_civilian_score(player: Player) -> int:
    """Calculate civilian (blue card) score"""
    score = 0
    civilian_cards = [card for card in player.cards if card.type == CardType.CIVILIAN]

    for card in civilian_cards:
        score += card.effect.count("V")

    return score


def calculate_science_score(player: Player) -> int:
    """Calculate scientific score using sets and individual symbols, optimizing jolly symbols"""
    JOLLY_EFFECT_NAME = "C/T/G"

    science_cards = [card for card in player.cards if card.type == CardType.SCIENTIFIC]
    jolly_cards = 0

    # Count base symbols
    symbols: Counter[ScienceSymbol] = Counter()
    for card in science_cards:
        if "C" in card.effect:
            symbols[ScienceSymbol.COMPASS] += 1
        elif "G" in card.effect:
            symbols[ScienceSymbol.GEAR] += 1
        elif "T" in card.effect:
            symbols[ScienceSymbol.TABLET] += 1

    # Count jolly cards from wonder stages and cards
    for i in range(player.stages_built):
        if player.wonder.stages[i].effect == JOLLY_EFFECT_NAME:
            jolly_cards += 1

    for card in player.cards:
        if card.effect == JOLLY_EFFECT_NAME:
            jolly_cards += 1

    def calculate_score(symbol_counts: Counter[ScienceSymbol]) -> int:
        """Calculate score for a specific symbol distribution"""
        min_sets = min(symbol_counts.values())
        set_score = min_sets * 7
        individual_score = sum(count * count for count in symbol_counts.values())
        return set_score + individual_score

    # Try all possible combinations of jolly card assignments
    # If no science cards are available, return already the square of jolly cards (max possible score)
    if not symbols:
        return jolly_cards * jolly_cards

    max_score = calculate_score(symbols)
    science_symbols = list(ScienceSymbol)

    # Try each jolly card one at a time
    for j in range(jolly_cards):
        for symbol in science_symbols:
            temp_symbols = symbols.copy()
            temp_symbols[symbol] += 1

            # For the second jolly (if available), try all symbols again
            if j < jolly_cards - 1:
                for symbol2 in science_symbols:
                    final_symbols = temp_symbols.copy()
                    final_symbols[symbol2] += 1
                    score = calculate_score(final_symbols)
                    max_score = max(max_score, score)
            else:
                score = calculate_score(temp_symbols)
                max_score = max(max_score, score)

    return max_score


def calculate_commercial_score(player: Player) -> int:
    """Calculate commercial (yellow card) score"""
    score = 0
    commercial_cards = [
        card for card in player.cards if card.type == CardType.COMMERCIAL
    ]

    for card in commercial_cards:
        multiplier_score = card.effect.count("V")
        if multiplier_score == 0:
            continue

        brackets_content = card.effect.split("{")[1].split("}")[0]

        if brackets_content == "wonder":
            score += multiplier_score * player.stages_built

        elif brackets_content == "military":
            score += multiplier_score * player.military_tokens

        elif brackets_content == "commercial":
            score += multiplier_score * player.count_cards_by_type(CardType.COMMERCIAL)

        elif brackets_content == "raw_material":
            score += multiplier_score * player.count_cards_by_type(
                CardType.RAW_MATERIAL
            )

        elif brackets_content == "manufactured_good":
            score += multiplier_score * player.count_cards_by_type(
                CardType.MANUFACTURED_GOOD
            )

        else:
            raise ValueError(f"Unknown commercial card effect: {card.effect}")

    return score


def calculate_guild_score(
    player: Player, left_neighbor: Player, right_neighbor: Player
) -> int:
    """Calculate guild (purple card) score based on various conditions"""
    score = 0
    guild_cards = [card for card in player.cards if card.type == CardType.GUILD]

    for card in guild_cards:
        # If no brackets, skip since it is the scientific guild with no direct effect here
        if "{" not in card.effect:
            continue
        
        brackets_content = card.effect.split("{")[1].split("}")[0]

        if brackets_content == "wonders_complete":
            if player.stages_built == len(player.wonder.stages):
                score += 7

        elif brackets_content == "wonder":
            score += player.stages_built
            score += left_neighbor.stages_built
            score += right_neighbor.stages_built

        else:
            for card_type_brackets in brackets_content.split(";"):
                card_type = CARD_TYPE_MAP[card_type_brackets]

                # Consider self
                if "<v>" in card.effect or ("<" not in card.effect and ">" not in card.effect):
                    score += player.count_cards_by_type(card_type)
                
                # Consider neighbors
                if "<" in card.effect:
                    score += left_neighbor.count_cards_by_type(card_type)
                if ">" in card.effect:
                    score += right_neighbor.count_cards_by_type(card_type)

    return score


def calculate_total_score(
    player: Player, left_neighbor: Player, right_neighbor: Player
) -> Score:
    """Calculate total score for a player"""
    return Score(
        military=calculate_military_score(player),
        treasury=calculate_treasury_score(player),
        wonders=calculate_wonders_score(player),
        civilian=calculate_civilian_score(player),
        scientific=calculate_science_score(player),
        commercial=calculate_commercial_score(player),
        guilds=calculate_guild_score(player, left_neighbor, right_neighbor),
    )
