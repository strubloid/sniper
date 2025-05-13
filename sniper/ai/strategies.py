"""
AI Strategy module - Contains different AI behavior strategies.
"""
import random
from typing import Protocol, Tuple, List

import pygame
from sniper.config.constants import const
from sniper.config.constants import debug_print
from sniper.models.characters import Character

class AIStrategy(Protocol):
    """Protocol defining the interface for AI strategies."""
    
    def evaluate_position(self, enemy: Character, player: Character, 
                        position: Tuple[int, int], obstacles: List[Tuple[int, int]], 
                        path_length: int) -> float:
        """Evaluate a position and return a score."""
        ...


class TacticalAI(AIStrategy):
    """Tactical AI strategy focusing on taking cover while maintaining line of sight."""
    
    def evaluate_position(self, enemy: Character, player: Character, 
                        position: Tuple[int, int], obstacles: List[Tuple[int, int]], 
                        path_length: int) -> float:
        """
        Score a potential position based on tactical considerations:
        - Line of sight to player (good for shooting)
        - Cover nearby (good for defense)
        - Not taking too much damage from movement
        - Optimal distance from player
        """
        score = 0
        x, y = position
        
        # Get integer positions for player
        player_x, player_y = int(player.x), int(player.y)
        
        # FACTOR 1: Can we shoot the player from here?
        if x == player_x or y == player_y:
            # Check if path would be clear
            would_have_shot = True
            
            if x == player_x:  # Same column
                start_y, end_y = min(y, player_y), max(y, player_y)
                for check_y in range(start_y + 1, end_y):
                    if (x, check_y) in obstacles:
                        would_have_shot = False
                        break
            else:  # Same row
                start_x, end_x = min(x, player_x), max(x, player_x)
                for check_x in range(start_x + 1, end_x):
                    if (check_x, y) in obstacles:
                        would_have_shot = False
                        break
            
            if would_have_shot:
                score += const.AI_SCORE_HAS_SHOT  # Very high priority to get a shot
        
        # FACTOR 2: Is there cover nearby?
        cover_count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if (x + dx, y + dy) in obstacles:
                cover_count += 1
        
        score += cover_count * const.AI_SCORE_PER_COVER  # Good bonus for each piece of nearby cover
        
        # FACTOR 3: Avoid health penalties from excessive movement
        # Each move costs health, so penalize long paths
        health_penalty = path_length * const.HEALTH_DAMAGE_PER_MOVE
        max_allowed_penalty = enemy.health * const.AI_MAX_HEALTH_PENALTY_RATIO
        
        if health_penalty > max_allowed_penalty:
            score -= const.AI_SCORE_HEALTH_DANGER  # Heavy penalty for dangerous moves
        else:
            # Small penalty proportional to damage taken
            score -= health_penalty * const.AI_HEALTH_PENALTY_FACTOR
        
        # FACTOR 4: Distance from player
        dist_to_player = abs(x - player_x) + abs(y - player_y)
        
        # Prefer medium distances - not too close, not too far
        if const.AI_OPTIMAL_DIST_MIN <= dist_to_player <= const.AI_OPTIMAL_DIST_MAX:
            score += const.AI_SCORE_OPTIMAL_DIST  # Optimal firing range
        elif dist_to_player <= 1:
            score -= const.AI_SCORE_TOO_CLOSE  # Too close is dangerous
        else:
            score += max(0, const.AI_SCORE_DISTANT - 
                        (dist_to_player - const.AI_OPTIMAL_DIST_MAX) * const.AI_DIST_PENALTY_FACTOR)
            
        # Small random factor for variety
        score += random.uniform(-const.AI_RANDOM_FACTOR, const.AI_RANDOM_FACTOR)
        
        return score