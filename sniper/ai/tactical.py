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
        
        # Allow shooting in straight lines (orthogonal and diagonal)
        if shooter_x == target_x or shooter_y == target_y or abs(shooter_x - target_x) == abs(shooter_y - target_y):
            debug_print("Target is in a shootable line")
            
            # Check for obstacles between shooter and target
            if shooter_x == target_x:  # Same column
                start_y, end_y = min(shooter_y, target_y), max(shooter_y, target_y)
                for y in range(start_y + 1, end_y):
                    if (shooter_x, y) in obstacles:
                        debug_print(f"Line of fire blocked by obstacle at ({shooter_x}, {y})")
                        return False
                        
            elif shooter_y == target_y:  # Same row
                start_x, end_x = min(shooter_x, target_x), max(shooter_x, target_x)
                for x in range(start_x + 1, end_x):
                    if (x, shooter_y) in obstacles:
                        debug_print(f"Line of fire blocked by obstacle at ({x}, {shooter_y})")
                        return False
                        
            else:  # Diagonal
                # Calculate step direction
                x_step = 1 if target_x > shooter_x else -1
                y_step = 1 if target_y > shooter_y else -1
                
                # Check each position along diagonal
                x, y = shooter_x + x_step, shooter_y + y_step
                while x != target_x and y != target_y:
                    if (x, y) in obstacles:
                        debug_print(f"Line of fire blocked by obstacle at ({x}, {y})")
                        return False
                    x += x_step
                    y += y_step
            
            # If we get here, there's a clear line of fire
            debug_print("Line of fire result: True (clear shot)")
            return True
        
        debug_print("Line of fire result: False (not in a shootable line)")
        return False


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
    
    def find_position_with_line_of_sight(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], max_moves: int
        ) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """
        Find a position that has line of sight to the target.
        Prioritizes positions that can see the target.
        
        Args:
            character: The character moving
            target: The target character to get line of sight to
            obstacles: List of obstacle positions
            max_moves: Maximum number of moves allowed
            
        Returns:
            Tuple of (position, path) or None if no position found
        """
        debug_print(f"Finding position with line of sight within {max_moves} moves")
        
        # Generate list of all possible positions within movement range
        possible_positions = self._generate_candidate_positions(character, target, obstacles, max_moves)
        
        # Score and sort positions - with heavy priority on positions with line of sight
        position_scores = {}
        for pos in possible_positions:
            # Get a path to this position
            path = PathFinder.find_path((character.x, character.y), pos, obstacles, target)
            
            # Skip if no path or too far
            if not path or len(path) > max_moves:
                continue
            
            # Convert target position to integers for the range check
            target_x_int, target_y_int = int(target.x), int(target.y)
            
            # Check if this position has line of sight
            has_line_of_sight = False
            if pos[0] == target_x_int or pos[1] == target_y_int:  # Same column or row
                # Check if path is clear
                if pos[0] == target_x_int:  # Same column
                    start_y, end_y = min(pos[1], target_y_int), max(pos[1], target_y_int)
                    has_line_of_sight = all((pos[0], check_y) not in obstacles 
                                          for check_y in range(start_y + 1, end_y))
                else:  # Same row
                    start_x, end_x = min(pos[0], target_x_int), max(pos[0], target_x_int)
                    has_line_of_sight = all((check_x, pos[1]) not in obstacles 
                                          for check_x in range(start_x + 1, end_x))
            
            # Calculate base score - HEAVILY prioritize positions with line of sight
            base_score = 1000 if has_line_of_sight else 0
            
            # Add standard position evaluation
            evaluation_score = self.strategy.evaluate_position(character, target, pos, obstacles, len(path))
            
            # Combined score
            position_scores[pos] = (base_score + evaluation_score, path)
        
        # Find best position
        if position_scores:
            best_pos = max(position_scores.items(), key=lambda x: x[1][0])[0]
            best_score, best_path = position_scores[best_pos]
            debug_print(f"Best position with line of sight: {best_pos} Score: {best_score}")
            return best_pos, best_path
        
        # If no position with line of sight, fall back to regular tactical position
        debug_print("No position with line of sight found")
        return None
    
    def find_retreat_position(
            self, character: Character, target: Character, 
            obstacles: List[Tuple[int, int]], max_moves: int
        ) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """
        Find a position to retreat to after shooting.
        Prioritizes positions with cover and away from the target.
        
        Args:
            character: The character moving
            target: The target character to retreat from
            obstacles: List of obstacle positions
            max_moves: Maximum number of moves allowed
            
        Returns:
            Tuple of (position, path) or None if no position found
        """
        debug_print(f"Finding retreat position within {max_moves} moves")
        
        # Generate list of all possible positions within movement range
        possible_positions = self._generate_candidate_positions(character, target, obstacles, max_moves)
        
        # Score and sort positions - prioritizing cover and distance from target
        position_scores = {}
        for pos in possible_positions:
            # Get a path to this position
            path = PathFinder.find_path((character.x, character.y), pos, obstacles, target)
            
            # Skip if no path or too far
            if not path or len(path) > max_moves:
                continue
            
            # Convert target position to integers for the range check
            target_x_int, target_y_int = int(target.x), int(target.y)
            
            # Calculate retreat score - prioritize:
            # 1. Positions with cover nearby
            # 2. Positions farther from target
            # 3. Positions that don't have line of sight (safer)
            
            # Cover score - count adjacent obstacles
            cover_count = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                           if (pos[0] + dx, pos[1] + dy) in obstacles)
            cover_score = cover_count * const.AI_SCORE_PER_COVER * 2  # Double cover importance
            
            # Distance score - prefer being farther away for retreat
            dist_to_target = abs(pos[0] - target_x_int) + abs(pos[1] - target_y_int)
            distance_score = min(100, dist_to_target * 10)  # Cap at 100
            
            # Line of sight penalty - prefer NOT having line of sight for safety
            has_line_of_sight = False
            if pos[0] == target_x_int or pos[1] == target_y_int:  # Same column or row
                # Check if path is clear
                if pos[0] == target_x_int:  # Same column
                    start_y, end_y = min(pos[1], target_y_int), max(pos[1], target_y_int)
                    has_line_of_sight = all((pos[0], check_y) not in obstacles 
                                          for check_y in range(start_y + 1, end_y))
                else:  # Same row
                    start_x, end_x = min(pos[0], target_x_int), max(pos[0], target_x_int)
                    has_line_of_sight = all((check_x, pos[1]) not in obstacles 
                                          for check_x in range(start_x + 1, end_x))
            
            line_of_sight_score = -200 if has_line_of_sight else 0  # Penalty for line of sight
            
            # Combined score
            total_score = cover_score + distance_score + line_of_sight_score
            position_scores[pos] = (total_score, path)
        
        # Find best position
        if position_scores:
            best_pos = max(position_scores.items(), key=lambda x: x[1][0])[0]
            best_score, best_path = position_scores[best_pos]
            debug_print(f"Best retreat position: {best_pos} Score: {best_score}")
            return best_pos, best_path
        
        # If no position found
        debug_print("No retreat position found")
        return None