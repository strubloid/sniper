"""
Tactical module - Handles tactical position finding and line of sight calculations.
"""
import random
from typing import List, Tuple, Optional, Callable

import pygame
from sniper.config.constants import const, debug_print
from sniper.models.characters import Character
from sniper.ai.strategies import AIStrategy, TacticalAI
from sniper.ai.pathfinding import PathFinder

class LineOfSightCalculator:
    """Handles line of sight calculations."""
    
    @staticmethod
    def has_line_of_fire(shooter: Character, target: Character, 
                        obstacles: List[Tuple[int, int]]) -> bool:
        """Check if shooter has a clear line of fire to the target."""
        debug_print(f"Checking line of fire between ({shooter.x},{shooter.y}) and ({target.x},{target.y})")
        
        # Convert positions to integers for reliable comparison
        shooter_x, shooter_y = int(shooter.x), int(shooter.y)
        target_x, target_y = int(target.x), int(target.y)
        
        # Direct hit check - must be in same row or column for orthogonal movement
        if shooter_x != target_x and shooter_y != target_y:
            debug_print("Line of fire result: False (not orthogonal)")
            return False
        
        # Check for obstacles between shooter and target
        if shooter_x == target_x:  # Same column
            start_y, end_y = min(shooter_y, target_y), max(shooter_y, target_y)
            for y in range(start_y + 1, end_y):
                if (shooter_x, y) in obstacles:
                    debug_print(f"Line of fire blocked by obstacle at ({shooter_x}, {y})")
                    return False
        else:  # Same row
            start_x, end_x = min(shooter_x, target_x), max(shooter_x, target_x)
            for x in range(start_x + 1, end_x):
                if (x, shooter_y) in obstacles:
                    debug_print(f"Line of fire blocked by obstacle at ({x}, {shooter_y})")
                    return False
        
        # If we reach here, there's a clear line of fire
        debug_print("Line of fire result: True (clear shot)")
        return True


class TacticalPositionFinder:
    """Finds tactical positions for AI movement."""
    
    def __init__(self, strategy: AIStrategy = TacticalAI()):
        """Initialize with specified strategy."""
        self.strategy = strategy
    
    def find_best_tactical_position(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], max_moves: int
        ) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """Find the best tactical position within movement range."""
        debug_print(f"Finding tactical positions within {max_moves} moves from ({character.x},{character.y})")
        
        # Generate list of all possible positions within movement range
        possible_positions = self._generate_candidate_positions(character, target, obstacles, max_moves)
        
        # Score and sort positions
        position_scores = {}
        for pos in possible_positions:
            # Get a path to this position
            path = PathFinder.find_path((character.x, character.y), pos, obstacles, target)
            
            # Skip if no path or too far
            if not path or len(path) > max_moves:
                continue
            
            # Score the position using the strategy
            score = self.strategy.evaluate_position(character, target, pos, obstacles, len(path))
            position_scores[pos] = (score, path)
            
        # Find best position
        if position_scores:
            best_pos = max(position_scores.items(), key=lambda x: x[1][0])[0]
            best_score, best_path = position_scores[best_pos]
            debug_print(f"Best position: {best_pos} Score: {best_score}")
            return best_pos, best_path
        
        debug_print("No tactical positions available")
        return None
    
    def _generate_candidate_positions(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], max_moves: int
        ) -> List[Tuple[int, int]]:
        """Generate candidate positions within movement range."""
        possible_positions = []
        for x in range(max(0, character.x - max_moves), min(const.GRID_WIDTH, character.x + max_moves + 1)):
            for y in range(max(0, character.y - max_moves), min(const.GRID_HEIGHT, character.y + max_moves + 1)):
                # Skip obstacles, target position, and current position
                if ((x, y) in obstacles or 
                    (x, y) == (target.x, target.y) or
                    (x, y) == (character.x, character.y)):
                    continue
                
                # Check if position is theoretically reachable (Manhattan distance)
                manhattan_dist = abs(x - character.x) + abs(y - character.y)
                if manhattan_dist <= max_moves:
                    possible_positions.append((x, y))
                    
        return possible_positions
    
    def make_simple_tactical_move(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], redraw_callback: Callable
        ) -> bool:
        """Make a simple one-step tactical move when full pathfinding is not feasible."""
        debug_print("Trying simple tactical move")
        if character.moves_left <= 0:
            debug_print("No moves left for simple tactical move")
            return False
            
        # Convert target position to integers for reliable comparison
        target_x, target_y = int(target.x), int(target.y)
        
        # Check all adjacent squares
        best_pos = None
        best_score = -float('inf')
        
        # Check the four orthogonal directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = character.x + dx, character.y + dy
            
            # Skip invalid positions
            if (x < 0 or x >= const.GRID_WIDTH or
                y < 0 or y >= const.GRID_HEIGHT or
                (x, y) in obstacles or (x, y) == (target_x, target_y)):
                continue
            
            # Calculate a simple score for this position
            score = self._calculate_simple_move_score(character, target, obstacles, x, y)
            
            if score > best_score:
                best_score = score
                best_pos = (x, y)
        
        # Make the move if we found one
        if best_pos:
            debug_print(f"Simple tactical move chosen: {best_pos}")
            character.x, character.y = best_pos
            character.moves_left -= 1
            debug_print(f"Made tactical move to ({character.x}, {character.y})")
            redraw_callback()
            pygame.time.delay(const.MOVEMENT_ANIMATION_DELAY)
            return True
        
        debug_print("No simple tactical move found")
        return False
    
    def _calculate_simple_move_score(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], x: int, y: int
        ) -> float:
        """Calculate a score for a simple one-step move."""
        score = 0
        target_x, target_y = int(target.x), int(target.y)
        
        # Check if we can shoot from here
        can_shoot = False
        if x == target_x or y == target_y:
            # Check line of sight
            if x == target_x:  # Same column
                start_y, end_y = min(y, target_y), max(y, target_y)
                if all((x, check_y) not in obstacles for check_y in range(start_y + 1, end_y)):
                    can_shoot = True
            else:  # Same row
                start_x, end_x = min(x, target_x), max(x, target_x)
                if all((check_x, y) not in obstacles for check_x in range(start_x + 1, end_x)):
                    can_shoot = True
            
            if can_shoot:
                score += const.AI_SCORE_HAS_SHOT  # Big bonus for shooting position
        
        # Cover bonus
        cover = sum(1 for cover_dx, cover_dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                  if (x + cover_dx, y + cover_dy) in obstacles)
        score += cover * const.AI_SCORE_PER_COVER
        
        # Distance factor - prefer medium distance
        dist = abs(x - target_x) + abs(y - target_y)
        if const.AI_OPTIMAL_DIST_MIN <= dist <= const.AI_OPTIMAL_DIST_MAX:
            score += const.AI_SCORE_OPTIMAL_DIST
        elif dist == 1:
            score -= const.AI_SCORE_TOO_CLOSE  # Too close!
        
        # Small random factor
        score += random.uniform(-const.AI_RANDOM_FACTOR, const.AI_RANDOM_FACTOR)
        
        return score