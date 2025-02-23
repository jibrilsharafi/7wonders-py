from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
import random

class Resource(Enum):
    WOOD = auto()
    STONE = auto()
    ORE = auto()
    CLAY = auto()
    GLASS = auto()
    PAPYRUS = auto()
    LOOM = auto()

class CardType(Enum):
    RAW_MATERIAL = auto()    # Brown cards
    MANUFACTURED_GOOD = auto() # Grey cards
    CIVILIAN = auto()        # Blue cards
    COMMERCIAL = auto()      # Yellow cards
    MILITARY = auto()        # Red cards
    SCIENTIFIC = auto()      # Green cards

class ScienceSymbol(Enum):
    TABLET = auto()
    COMPASS = auto()
    GEAR = auto()

class Age(Enum):
    ONE = auto()
    TWO = auto()
    THREE = auto()

class Action(Enum):
    PLAY_CARD = auto()
    BUILD_WONDER = auto()
    DISCARD = auto()

@dataclass
class Card:
    name: str
    type: CardType
    age: Age
    cost: Dict[Resource, int]
    chain_builds: List[str]  # Names of cards that can be built for free
    resources_produced: Dict[Resource, int]
    victory_points: int
    military_shields: int
    science_symbol: Optional[ScienceSymbol]
    
@dataclass
class Wonder:
    name: str
    starting_resource: Resource
    stages: List[Dict]  # Each stage will have its costs and benefits

class Player:
    def __init__(self, name: str, wonder: Wonder):
        self.name = name
        self.wonder = wonder
        self.cards_played = []
        self.coins = 3
        self.military_tokens = []
        self.wonder_stages_built = 0
        
    def get_available_resources(self) -> Dict[Resource, int]:
        resources = {self.wonder.starting_resource: 1}
        for card in self.cards_played:
            for resource, amount in card.resources_produced.items():
                resources[resource] = resources.get(resource, 0) + amount
        return resources


class PlayerAction:
    def __init__(self, action_type: Action, card: Card, resources_borrowed: Dict[str, List[Resource]] = None):
        self.action_type = action_type
        self.card = card
        self.resources_borrowed = resources_borrowed or {}  # Format: {player_name: [resources]}

class Game:
    def __init__(self, num_players: int):
        if not 3 <= num_players <= 7:
            raise ValueError("Player count must be between 3 and 7")
        
        self.num_players = num_players
        self.current_age = Age.ONE
        self.players = []
        self.current_hands = []
        self.current_round = 1
        self.cards_per_age = self._initialize_card_counts()
        
    def _initialize_card_counts(self) -> Dict[Age, int]:
        # Cards needed per age based on player count
        # Each player needs 7 cards for 6 rounds + 1 discard
        return {
            Age.ONE: self.num_players * 7,
            Age.TWO: self.num_players * 7,
            Age.THREE: self.num_players * 7
        }

    def can_player_afford_card(self, player: Player, card: Card, neighbors: Tuple[Player, Player]) -> bool:
        available_resources = player.get_available_resources()
        
        # Check if player has enough coins
        if player.coins < self._calculate_coin_cost(card):
            return False
            
        # Check if card can be built for free via chains
        if card.name in [c.chain_builds for c in player.cards_played]:
            return True
            
        # Check if player has required resources
        for resource, amount in card.cost.items():
            if isinstance(resource, Resource):  # Resource cost
                if available_resources.get(resource, 0) < amount:
                    # Check if neighbors can provide missing resources
                    missing = amount - available_resources.get(resource, 0)
                    if not self._can_trade_for_resource(player, resource, missing, neighbors):
                        return False
        return True

    def _can_trade_for_resource(self, player: Player, resource: Resource, amount: int, 
                              neighbors: Tuple[Player, Player]) -> bool:
        left_neighbor, right_neighbor = neighbors
        total_available = 0
        
        for neighbor in (left_neighbor, right_neighbor):
            neighbor_resources = neighbor.get_available_resources()
            total_available += neighbor_resources.get(resource, 0)
            
        return total_available >= amount and player.coins >= amount * 2  # Basic trading cost

    def _calculate_coin_cost(self, card: Card) -> int:
        # Some cards might have direct coin costs
        # This could be expanded based on card effects
        return 0  # Placeholder for actual implementation

    def play_round(self, player_actions: List[PlayerAction]):
        """Execute one round of play where all players simultaneously play their actions"""
        if len(player_actions) != self.num_players:
            raise ValueError("Must receive actions from all players")

        # Process all actions
        for i, action in enumerate(player_actions):
            player = self.players[i]
            
            if action.action_type == Action.PLAY_CARD:
                if self.can_player_afford_card(player, action.card, 
                                            self._get_neighbors(i)):
                    self._execute_card_play(player, action)
                    
            elif action.action_type == Action.BUILD_WONDER:
                if self.can_player_build_wonder(player, action.card):
                    self._execute_wonder_build(player, action.card)
                    
            elif action.action_type == Action.DISCARD:
                self._execute_discard(player, action.card)

        # Rotate hands
        self._rotate_hands(self.current_age)
        self.current_round += 1
        
        # Check if age is complete
        if self.current_round > 6:
            self._end_age()

    def _rotate_hands(self, age: Age):
        """Rotate hands clockwise or counterclockwise based on age"""
        if age in [Age.ONE, Age.THREE]:
            self.current_hands = self.current_hands[1:] + [self.current_hands[0]]
        else:  # Age.TWO
            self.current_hands = [self.current_hands[-1]] + self.current_hands[:-1]

    def _get_neighbors(self, player_index: int) -> Tuple[Player, Player]:
        """Get left and right neighbors of a player"""
        left_idx = (player_index - 1) % self.num_players
        right_idx = (player_index + 1) % self.num_players
        return self.players[left_idx], self.players[right_idx]

    def _end_age(self):
        """Handle end of age procedures"""
        self.calculate_military_conflicts()
        
        if self.current_age == Age.THREE:
            self._end_game()
        else:
            self.current_age = Age.TWO if self.current_age == Age.ONE else Age.THREE
            self.current_round = 1
            self.deal_cards()

    def _end_game(self):
        """Calculate final scores and determine winner"""
        scores = {player: self.calculate_final_score(player) for player in self.players}
        self.winner = max(scores.items(), key=lambda x: x[1])[0]
        self.final_scores = scores