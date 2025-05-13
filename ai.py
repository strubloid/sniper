"""
AI module for the Sniper Game.
This module handles AI movement, decision-making, and actions using better sniper tactics.
"""
import pygame
import random
import math
from typing import List, Tuple, Optional, Dict, Set, Protocol, Callable, Any

import constants as const
from constants import debug_print
from models import Character, Projectile


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


class AIStateManager:
    """Manages AI state transitions and actions."""
    
    @staticmethod
    def transition_to_thinking(redraw_callback: Callable) -> str:
        """Transition to thinking state with visual feedback."""
        redraw_callback()
        pygame.time.delay(const.AI_THINKING_DELAY)
        return const.AI_STATE_THINKING
    
    @staticmethod
    def transition_to_aiming(redraw_callback: Callable) -> str:
        """Transition to aiming state with visual feedback."""
        redraw_callback()
        pygame.time.delay(const.AI_AIMING_DELAY)
        return const.AI_STATE_AIMING
    
    @staticmethod
    def transition_to_shooting(redraw_callback: Callable) -> str:
        """Transition to shooting state with visual feedback."""
        redraw_callback()
        pygame.time.delay(const.AI_SHOOTING_DELAY)
        return const.AI_STATE_SHOOTING
    
    @staticmethod
    def transition_to_end(redraw_callback: Callable) -> str:
        """Transition to end state with visual feedback."""
        redraw_callback()
        pygame.time.delay(const.AI_END_DELAY)
        return const.AI_STATE_END


class PathFinder:
    """Handles pathfinding for the AI."""
    
    @staticmethod
    def find_path(start: Tuple[int, int], end: Tuple[int, int], 
                 obstacles: List[Tuple[int, int]], player: Character) -> List[Tuple[int, int]]:
        """
        Find a path from start to end, avoiding obstacles and player.
        Uses A* algorithm for optimal pathfinding.
        """
        # Convert obstacles to a set for faster lookup
        obstacles_set = set(obstacles + [(player.x, player.y)])
        
        # A* algorithm implementation
        open_set = {start}
        closed_set = set()
        
        # Track path and costs
        came_from = {}
        g_score = {start: 0}  # Cost from start to current node
        f_score = {start: PathFinder._manhattan_distance(start, end)}  # Estimated total cost
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            # Goal check
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]  # Reverse to get start-to-end
            
            # Process current node
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Skip invalid positions
                if (neighbor[0] < 0 or neighbor[0] >= const.GRID_WIDTH or
                    neighbor[1] < 0 or neighbor[1] >= const.GRID_HEIGHT or
                    neighbor in obstacles_set or neighbor in closed_set):
                    continue
                
                # Calculate scores
                tentative_g = g_score[current] + 1
                
                # Add to open set if not there, or if we found a better path
                if neighbor not in open_set or tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + PathFinder._manhattan_distance(neighbor, end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # No path found
        debug_print("No path found")
        return []
    
    @staticmethod
    def _manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


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


class MovementExecutor:
    """Handles movement execution for characters."""
    
    @staticmethod
    def execute_movement(character: Character, path: List[Tuple[int, int]], 
                       redraw_callback: Callable) -> None:
        """Move a character along a path with visual feedback."""
        debug_print(f"Executing movement along path: {path}")
        # Track how far we've moved
        moves_used = 0
        
        for pos in path:
            # Check if we still have moves left
            if moves_used >= character.moves_left:
                break
                
            # Update position and count moves
            character.x, character.y = pos
            moves_used += 1
            
            # Visual feedback
            debug_print(f"Moving to ({character.x}, {character.y}), moves left: {character.moves_left - moves_used}")
            redraw_callback()
            pygame.time.delay(const.MOVEMENT_ANIMATION_DELAY)
        
        # Update the actual moves counter
        character.moves_left -= moves_used


class ProjectileManager:
    """Handles projectile creation and management."""
    
    @staticmethod
    def create_projectile(shooter: Character, target: Character, 
                        projectiles: List[Projectile]) -> bool:
        """Create a projectile from shooter toward target's direction."""
        # Calculate direction vector
        dx, dy = 0, 0
        
        if shooter.x == target.x:  # Same column
            dy = 1 if target.y > shooter.y else -1
        elif shooter.y == target.y:  # Same row
            dx = 1 if target.x > shooter.x else -1
        
        # Create projectile if we have a valid direction
        if dx != 0 or dy != 0:
            debug_print(f"AI SHOOTING in direction ({dx}, {dy}) from ({shooter.x}, {shooter.y})")
            projectiles.append(
                Projectile(
                    shooter.x, shooter.y, dx, dy, 
                    shooter.sniper_type.color, shooter
                )
            )
            shooter.shots_left -= 1
            return True
        
        debug_print("Failed to shoot - no valid direction calculated")
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


class AI:
    """Handles AI logic for enemy characters with smart pathfinding and decision making."""
    
    # Create singleton instances of required components
    _line_of_sight = LineOfSightCalculator()
    _movement_executor = MovementExecutor()
    _projectile_manager = ProjectileManager()
    _state_manager = AIStateManager()
    _tactical_finder = TacticalPositionFinder()

    @classmethod
    def take_turn(
            cls,
            screen: pygame.Surface,
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]], 
            projectiles: List[Projectile],
            redraw_callback: Callable
    ) -> str:
        """
        Execute AI's turn with improved tactical decision making.
        Uses a phase-based approach to prioritize actions:
        1. Attack if player is in line of sight
        2. Move to optimal tactical position
        3. Attack again if possible after movement
        """
        debug_print("AI.take_turn called")
        
        # Ensure enemy stats are reset for this turn
        enemy.start_turn()
        
        # Initialize AI state and show thinking animation
        ai_state = cls._state_manager.transition_to_thinking(redraw_callback)
        
        try:
            debug_print("--- AI Turn Start ---")
            debug_print(f"Enemy at ({enemy.x}, {enemy.y}), Player at ({player.x}, {player.y})")
            debug_print(f"Moves left: {enemy.moves_left}, Shots left: {enemy.shots_left}")
            
            # Execute the turn in phases
            ai_state = cls._execute_shooting_phase(enemy, player, obstacles, projectiles, redraw_callback)
            ai_state = cls._execute_movement_phase(enemy, player, obstacles, redraw_callback)
            ai_state = cls._execute_post_move_shooting(enemy, player, obstacles, projectiles, redraw_callback)
            
            # End turn with status
            ai_state = cls._state_manager.transition_to_end(redraw_callback)
            debug_print("--- AI Turn End ---")
        except Exception as e:
            debug_print(f"AI Error: {str(e)}")
            import traceback
            debug_print(f"Traceback: {traceback.format_exc()}")
            ai_state = const.AI_STATE_END
        
        # Reset enemy movement and shots at end of turn
        enemy.moves_left = 0
        enemy.shots_left = 0
        
        return ai_state
    
    @classmethod
    def _execute_shooting_phase(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], projectiles: List[Projectile],
            redraw_callback: Callable
    ) -> str:
        """Execute the initial shooting phase if possible."""
        debug_print("Phase 1: Checking line of sight for initial shot")
        
        if enemy.shots_left <= 0:
            debug_print("  No shots available for initial phase")
            return const.AI_STATE_THINKING
            
        debug_print(f"Enemy has {enemy.shots_left} shots left, checking line of fire...")
        can_shoot = cls._line_of_sight.has_line_of_fire(enemy, player, obstacles)
        debug_print(f"  Can shoot initial: {can_shoot}")
        
        if can_shoot:
            debug_print("  -> Taking initial shot")
            ai_state = cls._state_manager.transition_to_shooting(redraw_callback)
            
            shot_success = cls._projectile_manager.create_projectile(enemy, player, projectiles)
            debug_print(f"  Shot executed with success: {shot_success}")
            redraw_callback()
            pygame.time.delay(const.AI_SHOT_FEEDBACK_DELAY)
            return ai_state
            
        return const.AI_STATE_THINKING
    
    @classmethod
    def _execute_movement_phase(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], redraw_callback: Callable
    ) -> str:
        """Execute the movement phase to reposition tactically."""
        debug_print("Phase 2: Movement/Tactical repositioning")
        
        if enemy.moves_left <= 0:
            debug_print("  No moves left for movement phase")
            return const.AI_STATE_THINKING
            
        debug_print(f"  Enemy has {enemy.moves_left} moves left, finding tactical position")
        ai_state = cls._state_manager.transition_to_aiming(redraw_callback)
        
        # Try to find the best tactical position
        best_move = cls._tactical_finder.find_best_tactical_position(
            enemy, player, obstacles, enemy.moves_left
        )
        
        if best_move:
            new_pos, path = best_move
            debug_print(f"  Best tactical move: {new_pos} via path of length {len(path)}")
            cls._movement_executor.execute_movement(enemy, path, redraw_callback)
            debug_print(f"  Movement executed, enemy now at ({enemy.x}, {enemy.y})")
        else:
            debug_print("  No tactical position found, trying simple tactical move")
            moved = cls._tactical_finder.make_simple_tactical_move(
                enemy, player, obstacles, redraw_callback
            )
            debug_print(f"  Simple move result: {moved}")
            
        return ai_state
    
    @classmethod
    def _execute_post_move_shooting(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], projectiles: List[Projectile],
            redraw_callback: Callable
    ) -> str:
        """Execute shooting after movement if possible."""
        debug_print("Phase 3: Checking line of sight after movement")
        
        if enemy.shots_left <= 0:
            debug_print("  No shots available for post-move phase")
            return const.AI_STATE_THINKING
            
        debug_print(f"Enemy still has {enemy.shots_left} shots left, checking line of fire again...")
        can_shoot = cls._line_of_sight.has_line_of_fire(enemy, player, obstacles)
        debug_print(f"  Can shoot after move: {can_shoot}")
        
        if can_shoot:
            debug_print("  -> Taking post-move shot")
            ai_state = cls._state_manager.transition_to_shooting(redraw_callback)
            
            shot_success = cls._projectile_manager.create_projectile(enemy, player, projectiles)
            debug_print(f"  Post-move shot executed with success: {shot_success}")
            redraw_callback()
            pygame.time.delay(const.AI_SHOT_FEEDBACK_DELAY)
            return ai_state
            
        return const.AI_STATE_THINKING