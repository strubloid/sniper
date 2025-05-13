"""
AI module for the Sniper Game.
This module handles AI movement, decision-making, and actions using better sniper tactics.
"""
import pygame
import random
import math
from typing import List, Tuple, Optional, Dict, Set

import constants as const
from constants import debug_print
from models import Character, Projectile


class AI:
    """Handles AI logic for enemy characters with smart pathfinding and decision making."""

    @staticmethod
    def take_turn(
            screen: pygame.Surface,
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]], 
            projectiles: List[Projectile],
            redraw_callback
    ) -> str:
        debug_print("AI.take_turn called")
        """
        Execute AI's turn with sniper tactics:
        1. Attack if player is in line of sight
        2. Move to get closer to player while staying in cover
        3. Avoid taking too much damage from movement
        """
        # Ensure enemy stats are reset for this turn
        enemy.start_turn()
        # Initialize AI state and show thinking
        ai_state = const.AI_STATE_THINKING
        redraw_callback()
        pygame.time.delay(300)  # Short thinking delay
        
        try:
            debug_print("--- AI Turn Start ---")
            debug_print(f"Enemy at ({enemy.x}, {enemy.y}), Player at ({player.x}, {player.y})")
            debug_print(f"Moves left: {enemy.moves_left}, Shots left: {enemy.shots_left}")
            
            # PRIORITY 1: SHOOT IF PLAYER IS IN LINE OF SIGHT
            debug_print("Phase 1: Checking line of sight for initial shot")
            if enemy.shots_left > 0:
                debug_print(f"Enemy has {enemy.shots_left} shots left, checking line of fire...")
                can_shoot = AI._has_line_of_fire(enemy, player, obstacles)
                debug_print(f"  Can shoot initial: {can_shoot}")
                if can_shoot:
                    debug_print("  -> Taking initial shot")
                    ai_state = const.AI_STATE_SHOOTING
                    redraw_callback()
                    pygame.time.delay(300)

                    shot_success = AI._execute_shot(enemy, player, projectiles)
                    debug_print(f"  Shot executed with success: {shot_success}")
                    redraw_callback()
                    pygame.time.delay(400)
            else:
                debug_print("  No shots available for initial phase")

            # PRIORITY 2: FIND COVER NEAR PLAYER
            debug_print("Phase 2: Movement/Tactical repositioning")
            if enemy.moves_left > 0:
                debug_print(f"  Enemy has {enemy.moves_left} moves left, finding tactical position")
                ai_state = const.AI_STATE_AIMING
                redraw_callback()
                pygame.time.delay(300)

                best_move = AI._find_best_tactical_position(enemy, player, obstacles, enemy.moves_left)
                if best_move:
                    new_pos, path = best_move
                    debug_print(f"  Best tactical move: {new_pos} via path of length {len(path)}")
                    AI._execute_movement(enemy, path, redraw_callback)
                    debug_print(f"  Movement executed, enemy now at ({enemy.x}, {enemy.y})")
                else:
                    debug_print("  No tactical position found, trying simple tactical move")
                    moved = AI._make_simple_tactical_move(enemy, player, obstacles, redraw_callback)
                    debug_print(f"  Simple move result: {moved}")
                    if not moved:
                        debug_print("  No simple tactical move made")
            else:
                debug_print("  No moves left for movement phase")

            # PRIORITY 3: SHOOT AFTER REPOSITIONING
            debug_print("Phase 3: Checking line of sight after movement")
            if enemy.shots_left > 0:
                debug_print(f"Enemy still has {enemy.shots_left} shots left, checking line of fire again...")
                can_shoot2 = AI._has_line_of_fire(enemy, player, obstacles)
                debug_print(f"  Can shoot after move: {can_shoot2}")
                if can_shoot2:
                    debug_print("  -> Taking post-move shot")
                    ai_state = const.AI_STATE_SHOOTING
                    redraw_callback()
                    pygame.time.delay(300)

                    shot_success = AI._execute_shot(enemy, player, projectiles)
                    debug_print(f"  Post-move shot executed with success: {shot_success}")
                    redraw_callback()
                    pygame.time.delay(400)
            else:
                debug_print("  No shots available for post-move phase")

            # End turn
            debug_print("Phase 4: Ending AI turn")
            ai_state = const.AI_STATE_END
            redraw_callback()
            pygame.time.delay(300)
            debug_print("--- AI Turn End ---")
        except Exception as e:
            debug_print(f"AI Error: {str(e)}")
            import traceback
            debug_print(f"Traceback: {traceback.format_exc()}")
            ai_state = const.AI_STATE_END
        
        # Reset enemy movement and shots
        enemy.moves_left = 0
        enemy.shots_left = 0
        
        return ai_state
    
    @staticmethod
    def _has_line_of_fire(enemy: Character, player: Character, obstacles: List[Tuple[int, int]]) -> bool:
        debug_print(f"Checking line of fire between Enemy({enemy.x},{enemy.y}) and Player({player.x},{player.y})")
        
        # Convert positions to integers for reliable comparison
        enemy_x, enemy_y = int(enemy.x), int(enemy.y)
        player_x, player_y = int(player.x), int(player.y)
        
        # Direct hit check - must be in same row or column
        if enemy_x != player_x and enemy_y != player_y:
            debug_print("Line of fire result: False")
            return False
        
        # Check for obstacles in between
        if enemy_x == player_x:  # Same column
            start_y, end_y = min(enemy_y, player_y), max(enemy_y, player_y)
            for y in range(start_y + 1, end_y):
                if (enemy_x, y) in obstacles:
                    debug_print("Line of fire result: False")
                    return False
        else:  # Same row
            start_x, end_x = min(enemy_x, player_x), max(enemy_x, player_x)
            for x in range(start_x + 1, end_x):
                if (x, enemy_y) in obstacles:
                    debug_print("Line of fire result: False")
                    return False
        
        # If we reach here, there's a clear line of fire
        debug_print("Line of fire result: True")
        return True
    
    @staticmethod
    def _execute_shot(enemy: Character, player: Character, projectiles: List[Projectile]) -> bool:
        """Execute a shot at the player."""
        # Calculate direction vector
        dx, dy = 0, 0
        
        if enemy.x == player.x:  # Same column
            dy = 1 if player.y > enemy.y else -1
        elif enemy.y == player.y:  # Same row
            dx = 1 if player.x > enemy.x else -1
        
        # Create projectile
        if dx != 0 or dy != 0:
            debug_print(f"AI SHOOTING in direction ({dx}, {dy}) from ({enemy.x}, {enemy.y})")
            projectiles.append(
                Projectile(
                    enemy.x, enemy.y, dx, dy, 
                    enemy.sniper_type.color, enemy
                )
            )
            enemy.shots_left -= 1
            return True
        
        debug_print("Failed to shoot - no direction calculated")
        return False
    
    @staticmethod
    def _find_best_tactical_position(enemy: Character, player: Character, 
                                    obstacles: List[Tuple[int, int]], max_moves: int) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        debug_print(f"Finding tactical positions within {max_moves} moves from ({enemy.x},{enemy.y})")
        # Generate list of all possible positions within movement range
        possible_positions = []
        for x in range(max(0, enemy.x - max_moves), min(const.GRID_WIDTH, enemy.x + max_moves + 1)):
            for y in range(max(0, enemy.y - max_moves), min(const.GRID_HEIGHT, enemy.y + max_moves + 1)):
                # Skip obstacles and player position
                if (x, y) in obstacles or (x, y) == (player.x, player.y):
                    continue
                
                # Skip current position
                if (x, y) == (enemy.x, enemy.y):
                    continue
                
                # Check if position is theoretically reachable
                manhattan_dist = abs(x - enemy.x) + abs(y - enemy.y)
                if manhattan_dist <= max_moves:
                    # We'll verify actual path length later
                    possible_positions.append((x, y))
        
        # Score and sort positions
        position_scores = {}
        for pos in possible_positions:
            # Get a path to this position
            path = AI._find_path((enemy.x, enemy.y), pos, obstacles, player)
            
            # Skip if no path or too far
            if not path or len(path) > max_moves:
                continue
            
            # Score the position
            score = AI._score_tactical_position(enemy, player, pos, obstacles, len(path))
            position_scores[pos] = (score, path)
            
        # Find best position
        if position_scores:
            best_pos = max(position_scores.items(), key=lambda x: x[1][0])[0]
            best_score, best_path = position_scores[best_pos]
            debug_print(f"Best position: {best_pos} Score: {best_score} Path: {best_path}")
            return best_pos, best_path
        
        debug_print("No tactical positions available")
        return None
    
    @staticmethod
    def _score_tactical_position(enemy: Character, player: Character, 
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
                score += 100  # Very high priority to get a shot
        
        # FACTOR 2: Is there cover nearby?
        cover_count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if (x + dx, y + dy) in obstacles:
                cover_count += 1
        
        score += cover_count * 15  # Good bonus for each piece of nearby cover
        
        # FACTOR 3: Avoid health penalties from excessive movement
        # Each move costs health, so penalize long paths
        health_penalty = path_length * const.HEALTH_DAMAGE_PER_MOVE
        max_allowed_penalty = enemy.health * 0.3  # Don't lose more than 30% health
        
        if health_penalty > max_allowed_penalty:
            score -= 50  # Heavy penalty for dangerous moves
        else:
            # Small penalty proportional to damage taken
            score -= health_penalty * 0.5
        
        # FACTOR 4: Distance from player
        dist_to_player = abs(x - player_x) + abs(y - player_y)
        
        # Prefer medium distances - not too close, not too far
        if 2 <= dist_to_player <= 3:
            score += 30  # Optimal firing range
        elif dist_to_player <= 1:
            score -= 20  # Too close is dangerous
        else:
            score += max(0, 25 - (dist_to_player - 3) * 5)  # Diminishing returns
            
        # Small random factor for variety
        score += random.uniform(-5, 5)
        
        return score
    
    @staticmethod
    def _find_path(start: Tuple[int, int], end: Tuple[int, int], 
                  obstacles: List[Tuple[int, int]], player: Character) -> List[Tuple[int, int]]:
        """
        Find a path from start to end, avoiding obstacles and player.
        Uses a simple A* implementation.
        """
        # Convert obstacles to a set for faster lookup
        obstacles_set = set(obstacles + [(player.x, player.y)])
        
        # A* algorithm implementation
        open_set = {start}
        closed_set = set()
        
        # Track path and costs
        came_from = {}
        g_score = {start: 0}  # Cost from start to current node
        f_score = {start: AI._manhattan_distance(start, end)}  # Estimated total cost
        
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
                    f_score[neighbor] = tentative_g + AI._manhattan_distance(neighbor, end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # No path found
        debug_print("No path found")
        return []
    
    @staticmethod
    def _manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    @staticmethod
    def _execute_movement(enemy: Character, path: List[Tuple[int, int]], redraw_callback) -> None:
        """Move the enemy along a path with animation."""
        debug_print(f"Executing movement along path: {path}")
        # Track how far we've moved
        moves_used = 0
        
        for pos in path:
            # Check if we still have moves left
            if moves_used >= enemy.moves_left:
                break
                
            # Update position and count moves
            old_x, old_y = enemy.x, enemy.y
            enemy.x, enemy.y = pos
            moves_used += 1
            
            # Visual feedback
            debug_print(f"AI moving to ({enemy.x}, {enemy.y}), moves left: {enemy.moves_left - moves_used}")
            redraw_callback()
            pygame.time.delay(200)
        
        # Update the actual moves counter
        enemy.moves_left -= moves_used
    
    @staticmethod
    def _make_simple_tactical_move(enemy: Character, player: Character, 
                                 obstacles: List[Tuple[int, int]], redraw_callback) -> bool:
        debug_print("Trying simple tactical move")
        if enemy.moves_left <= 0:
            debug_print("No moves left for simple tactical move")
            return False
            
        # Convert positions to integers for reliable comparison
        player_x, player_y = int(player.x), int(player.y)
        
        # Check all adjacent squares
        best_pos = None
        best_score = -float('inf')
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = enemy.x + dx, enemy.y + dy
            
            # Skip invalid positions
            if (x < 0 or x >= const.GRID_WIDTH or
                y < 0 or y >= const.GRID_HEIGHT or
                (x, y) in obstacles or (x, y) == (player_x, player_y)):
                continue
            
            # Score this position
            score = 0
            
            # Check if we can shoot from here
            can_shoot = False
            if x == player_x or y == player_y:
                # Check line of sight
                if x == player_x:  # Same column
                    start_y, end_y = min(y, player_y), max(y, player_y)
                    if all((x, check_y) not in obstacles for check_y in range(start_y + 1, end_y)):
                        can_shoot = True
                else:  # Same row
                    start_x, end_x = min(x, player_x), max(x, player_x)
                    if all((check_x, y) not in obstacles for check_x in range(start_x + 1, end_x)):
                        can_shoot = True
                
                if can_shoot:
                    score += 50  # Big bonus for shooting position
            
            # Cover bonus
            cover = sum(1 for cover_dx, cover_dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                      if (x + cover_dx, y + cover_dy) in obstacles)
            score += cover * 10
            
            # Distance factor - prefer medium distance
            dist = abs(x - player_x) + abs(y - player_y)
            if 2 <= dist <= 3:
                score += 20
            elif dist == 1:
                score -= 10  # Too close!
            
            if score > best_score:
                best_score = score
                best_pos = (x, y)
        
        # Make the move if we found one
        if best_pos:
            debug_print(f"Simple tactical move chosen: {best_pos}")
            enemy.x, enemy.y = best_pos
            enemy.moves_left -= 1
            debug_print(f"AI made tactical move to ({enemy.x}, {enemy.y})")
            redraw_callback()
            pygame.time.delay(200)
            return True
        
        debug_print("No simple tactical move found")
        return False