from typing import List, Dict
from src.core.constants import AGE_MILITARY_TOKENS, MILITARY_DEFEAT_TOKEN
from src.game.player import Player, get_neighbors
import logging

logger = logging.getLogger(__name__)


def calculate_battle(player_shields: int, opponent_shields: int, age: int) -> int:
    """Calculate military tokens for a single battle"""
    if player_shields > opponent_shields:
        return int(AGE_MILITARY_TOKENS[age])
    elif player_shields < opponent_shields:
        return int(MILITARY_DEFEAT_TOKEN)
    return 0


def calculate_military_outcome(
    player: Player, neighbors: List[Player], age: int
) -> int:
    """Calculate total military tokens for a player against both neighbors"""
    player_shields = player.get_shields()
    total_tokens = 0

    for neighbor in neighbors:
        neighbor_shields = neighbor.get_shields()
        tokens = calculate_battle(player_shields, neighbor_shields, age)
        if tokens != 0:
            logger.debug(
                f"{player.name} {'wins' if tokens > 0 else 'loses'} against {neighbor.name} ({player_shields} vs {neighbor_shields})"
            )
        total_tokens += tokens

    return total_tokens


def resolve_military_conflicts(
    all_players: List[Player], age: int # TODO: make all of these view
) -> Dict[Player, int]:
    """Calculate and return military outcomes for all players"""
    outcomes: Dict[Player, int] = {}

    for player in all_players:
        neighbors = get_neighbors(player.position, all_players)
        outcomes[player] = calculate_military_outcome(player, neighbors, age)

    return outcomes


def apply_military_tokens_to_all(all_players: List[Player], outcomes: Dict[Player, int]) -> None:
    """Apply military tokens to players"""
    for player in all_players:
        player.add_military_tokens(outcomes[player])
