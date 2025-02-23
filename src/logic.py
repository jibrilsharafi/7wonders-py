from typing import List, Dict, Optional, Tuple
import random
import logging

from game_types import Resource, CardType, Age, Action, Card, Wonder, WonderStage, Player, PlayerAction

class Player:
    def __init__(self, name: str, wonder: Wonder):
        self.name = name
        self.wonder = wonder
        self.cards_played: List[Card] = []
        self.coins = 3
        self.military_tokens = 0
        self.wonder_stages_built = 0
        
        logging.info(f"Player {name} initialized with wonder {wonder.name}")
        
    def get_available_resources(self) -> Dict[Resource, int]:
        resources = {self.wonder.starting_resource: 1}
        
        for card in self.cards_played:
            for resource, amount in card.resources_produced.items():
                resources[resource] = resources.get(resource, 0) + amount
        
        return resources


class PlayerAction:
    def __init__(self, action_type: Action, card: Card, resources_borrowed: Optional[Dict[str, List[Resource]]] = None):
        self.action_type = action_type
        self.card = card
        self.resources_borrowed = resources_borrowed or {}  # Format: {player_name: [resources]}

class Game:
    def __init__(self, num_players: int):
        if not 3 <= num_players <= 7:
            raise ValueError("Player count must be between 3 and 7")
        
        self.num_players = num_players
        self.current_age = Age.ONE
        self.players: List[Player] = []
        self.current_hands: List[List[Card]] = [[], [], []]
        self.current_round = 1
        self.cards_per_age = self._initialize_card_counts()
        
        logging.info(f"Initialized game with {num_players} players")
        
    def _initialize_card_counts(self) -> Dict[Age, int]:
        # Cards needed per age based on player count
        # Each player needs 7 cards for 6 rounds + 1 discard
        return {
            Age.ONE: self.num_players * 7,
            Age.TWO: self.num_players * 7,
            Age.THREE: self.num_players * 7
        }

    def can_player_afford_card(self, player: Player, card: Card, neighbors: Tuple[Player, Player]) -> bool:
        
        # Check if player has enough coins
        if player.coins < self._calculate_coin_cost(card):
            return False
            
        # Check if card can be built for free via chains
        if card.name in [c.chain_builds for c in player.cards_played]:
            return True
            
        # Check if player has required resources
        for resource, amount in card.cost.items():
            if isinstance(resource, Resource):  # Resource cost
                available_resources = player.get_available_resources()
                
                if available_resources.get(resource, 0) < amount:
                    # Check if neighbors can provide missing resources
                    missing = amount - available_resources.get(resource, 0)
                    if not self._can_trade_for_resource(player, resource, missing, neighbors):
                        return False
        
        return True

    def _can_trade_for_resource(self, player: Player, resource: Resource, amount: int, 
                              neighbors: Tuple[Player, Player]) -> bool:
        # TODO: implement trading logic with commercial cards
        left_neighbor, right_neighbor = neighbors
        total_available = 0
        
        for neighbor in (left_neighbor, right_neighbor):
            neighbor_resources = neighbor.get_available_resources()
            total_available += neighbor_resources.get(resource, 0)
            
        return total_available >= amount and player.coins >= amount * 2  # Basic trading cost

    def _calculate_coin_cost(self, card: Card) -> int:
        # TODO: Implement coin cost calculation
        # Some cards might have direct coin costs
        # This could be expanded based on card effects
        return 0  # Placeholder for actual implementation

    def play_round(self, player_actions: List[PlayerAction]) -> None:
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

    def deal_cards(self) -> None:
        """Deal cards to players for the current age"""
        for i in range(self.num_players):
            for _ in range(7):
                self.players[i].cards_played.append(self.current_hands[0].pop(0))
                
    

    def _rotate_hands(self, age: Age) -> None:
        """Rotate hands clockwise or counterclockwise based on age"""
        if age in [Age.ONE, Age.THREE]:
            self.current_hands = self.current_hands[1:] + [self.current_hands[0]]
        elif age == Age.TWO:
            self.current_hands = [self.current_hands[-1]] + self.current_hands[:-1]
        else:
            logging.error(f"Invalid age: {age}")

    def _get_neighbors(self, player_index: int) -> Tuple[Player, Player]:
        """Get left and right neighbors of a player"""
        left_idx = (player_index - 1) % self.num_players
        right_idx = (player_index + 1) % self.num_players
        return self.players[left_idx], self.players[right_idx]

    def _end_age(self) -> None:
        """Handle end of age procedures"""
        self.calculate_military_conflicts()
        
        if self.current_age == Age.THREE:
            self._end_game()
        else:
            self.current_age = Age.TWO if self.current_age == Age.ONE else Age.THREE
            self.current_round = 1
            self.deal_cards()

    def _end_game(self) -> None:
        """Calculate final scores and determine winner"""
        scores = {player: self.calculate_final_score(player) for player in self.players}
        self.winner = max(scores.items(), key=lambda x: x[1])[0]
        self.final_scores = scores
        
    def _execute_card_play(self, player: Player, action: PlayerAction) -> None:
        """Execute playing a card, handling resources and effects"""
        card = action.card
        
        logging.debug(f"Player {player.name} attempting to play card {card.name}")
        
        # Handle resource costs
        if not self._handle_resource_costs(player, card, action.resources_borrowed):
            logging.error(f"Failed to handle resource costs for {card.name}")
            return
        
        # Add card to player's played cards
        player.cards_played.append(card)
        
        # Handle immediate effects
        self._handle_card_effects(player, card)
        
        logging.info(f"Player {player.name} successfully played {card.name}")

    def _handle_resource_costs(self, player: Player, card: Card, 
                            resources_borrowed: Dict[str, List[Resource]]) -> bool:
        """Handle the payment of resources for a card"""
        # Handle chain builds
        if card.name in [c.chain_builds for c in player.cards_played]:
            logging.debug(f"Card {card.name} built for free via chain")
            return True
        
        # Calculate coin costs including trading
        total_coin_cost = self._calculate_total_coin_cost(card, resources_borrowed)
        if total_coin_cost > player.coins:
            logging.debug(f"Player {player.name} cannot afford coin cost {total_coin_cost}")
            return False
        
        player.coins -= total_coin_cost
        return True

    def _calculate_total_coin_cost(self, card: Card,
                                resources_borrowed: Dict[str, List[Resource]]) -> int:
        """Calculate total coin cost including trading costs"""
        base_cost = self._calculate_coin_cost(card)
        trading_cost = sum(len(resources) * 2 for resources in resources_borrowed.values())
        return base_cost + trading_cost

    def _handle_card_effects(self, player: Player, card: Card) -> None:
        """Handle immediate effects of playing a card"""
        
        if card.type == CardType.COMMERCIAL:
            # TODO: Handle immediate coin gains or other commercial effects
            pass

    def calculate_military_conflicts(self) -> None:
        """Calculate military conflicts at the end of an age"""
        logging.info(f"Calculating military conflicts for age {self.current_age}")
        
        for i, player in enumerate(self.players):
            left_neighbor, right_neighbor = self._get_neighbors(i)
            player_strength = self._calculate_military_strength(player)
            
            # Compare with left neighbor
            left_strength = self._calculate_military_strength(left_neighbor)
            self._resolve_military_conflict(player, left_neighbor, player_strength, left_strength)
            
            # Compare with right neighbor
            right_strength = self._calculate_military_strength(right_neighbor)
            self._resolve_military_conflict(player, right_neighbor, player_strength, right_strength)

    def _calculate_military_strength(self, player: Player) -> int:
        """Calculate total military strength for a player"""
        return sum(card.military_shields for card in player.cards_played 
                if card.type == CardType.MILITARY)

    def _resolve_military_conflict(self, player: Player, opponent: Player,
                                player_strength: int, opponent_strength: int) -> None:
        """Resolve military conflict between two players"""
        if player_strength > opponent_strength:
            victory_points = self._get_military_victory_points()
            player.military_tokens += victory_points
            logging.debug(f"Player {player.name} won conflict against {opponent.name} "
                        f"({player_strength} vs {opponent_strength}): +{victory_points} points")
        elif player_strength < opponent_strength:
            player.military_tokens -= 1
            logging.debug(f"Player {player.name} lost conflict against {opponent.name} "
                        f"({player_strength} vs {opponent_strength}): -1 point")

    def _get_military_victory_points(self) -> int:
        """Get victory points for winning military conflict based on current age"""
        points_by_age = {
            Age.ONE: 1,
            Age.TWO: 3,
            Age.THREE: 5
        }
        return points_by_age[self.current_age]

    def _execute_wonder_build(self, player: Player, card: Card) -> None:
        """Execute building a wonder stage"""
        if player.wonder_stages_built >= len(player.wonder.stages):
            logging.error(f"Player {player.name} cannot build more wonder stages")
            return
        
        stage = player.wonder.stages[player.wonder_stages_built]
        
        # Handle resource costs similar to card playing
        if not self._handle_resource_costs(player, card, {}):  # Empty dict as no trading for wonder builds
            logging.error(f"Failed to handle resource costs for wonder stage")
            return
        
        # Apply wonder stage effects
        self._handle_wonder_stage_effects(player, stage)
        player.wonder_stages_built += 1
        logging.info(f"Player {player.name} built wonder stage {player.wonder_stages_built}")

    def _execute_discard(self, player: Player, card: Card) -> None:
        """Execute discarding a card for coins"""
        player.coins += 3
        logging.debug(f"Player {player.name} discarded {card.name} for 3 coins")
        
    def _can_player_build_wonder(self, player: Player, card: Card) -> bool:
        """Check if player can build a wonder stage"""
        # First check if player has enough stages left
        if player.wonder_stages_built >= len(player.wonder.stages):
            logging.debug(f"Player {player.name} cannot build more wonder stages")
            return False
        
        # Check if player has enough resources
        stage = player.wonder.stages[player.wonder_stages_built] # Access the next stage using stages built index
        for resource, amount in stage.cost.items():
            if player.get_available_resources().get(resource, 0) < amount:
                logging.debug(f"Player {player.name} does not have enough resources for wonder stage")
                return False
            
        return True
    
    def _handle_wonder_stage_effects(self, player: Player, stage: WonderStage) -> None:
        """Apply effects of building a wonder stage"""
        # TODO: actual implementation of wonder stage effects
        pass