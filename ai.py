"""
AI module for the Sniper Game.
This module handles AI movement, decision-making, and actions using advanced algorithms.
"""
import pygame
import random
import heapq
import math
from typing import List, Tuple, Optional, Dict, Set

import constants as const
from models import Character, Projectile


class AI:
    """Handles AI logic for enemy characters with advanced pathfinding and decision making."""

    @staticmethod
    def take_turn(
            screen: pygame.Surface,
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]], 
            projectiles: List[Projectile],
            redraw_callback
    ) -> str:
        """
        Execute AI's turn with tactical decision making and animations.
        Returns the current AI state.
        """
        # Calculate direction to player
        dx, dy = player.x - enemy.x, player.y - enemy.y
        distance_to_player = abs(dx) + abs(dy)
        
        # Initialize AI state
        ai_state = const.AI_STATE_THINKING
        redraw_callback()  # Show the THINKING state in the debug display
        pygame.time.delay(const.AI_AIMING_DELAY)
        
        # Track if any actions were taken
        action_taken = False
        
        # Tactical decision: determine whether to shoot or move first
        should_shoot_first = AI._should_shoot_first(enemy, player, obstacles)

        # SHOOTING PHASE - if we decide to shoot first
        if should_shoot_first and enemy.shots_left > 0:
            # Update AI state to SHOOTING before taking the shot
            ai_state = const.AI_STATE_SHOOTING
            redraw_callback()  # Update the UI to show SHOOTING state
            
            shot_taken = AI._handle_shooting(enemy, player, obstacles, projectiles, redraw_callback)
            if shot_taken:
                action_taken = True

        # MOVEMENT PHASE - if we didn't shoot or need to reposition
        if enemy.moves_left > 0:
            # Update AI state to AIMING (which represents movement planning)
            ai_state = const.AI_STATE_AIMING
            redraw_callback()  # Update the UI to show AIMING state
            pygame.time.delay(const.AI_AIMING_DELAY // 2)  # Short delay for state change
            
            # Determine best tactical position
            target_position = AI._determine_best_position(enemy, player, obstacles)
            
            if target_position and target_position != (enemy.x, enemy.y):
                # Use A* to find optimal path
                path = AI._astar_pathfinding(
                    (enemy.x, enemy.y), 
                    target_position, 
                    obstacles + [(player.x, player.y)],
                    enemy.moves_left
                )
                
                if path:
                    # Execute movement with animation
                    AI._animate_movement(enemy, path, redraw_callback)
                    action_taken = True
        
        # SHOOTING PHASE (after movement) - if we didn't shoot earlier
        if not should_shoot_first and enemy.shots_left > 0:
            # Update AI state to SHOOTING before taking the shot
            ai_state = const.AI_STATE_SHOOTING
            redraw_callback()  # Update the UI to show SHOOTING state
            
            shot_taken = AI._handle_shooting(enemy, player, obstacles, projectiles, redraw_callback)
            if shot_taken:
                action_taken = True

        # If no action was taken, attempt a random move as fallback
        if not action_taken and enemy.moves_left > 0:
            possible_moves = AI._calculate_possible_moves(enemy, player, obstacles, 1)  # Just try to move 1 space
            if possible_moves:
                # Choose a random move
                new_pos = random.choice(possible_moves)
                
                # Update AI state to show we're making a desperation move
                ai_state = const.AI_STATE_AIMING
                redraw_callback()
                pygame.time.delay(const.AI_AIMING_DELAY // 2)
                
                # Move to the position
                enemy.x, enemy.y = new_pos
                enemy.moves_left -= 1
                
                # Redraw after movement
                redraw_callback()
                pygame.time.delay(const.ANIMATION_DELAY)
                action_taken = True

        # End turn
        ai_state = const.AI_STATE_END
        redraw_callback()  # Show the END state in the debug display
        pygame.time.delay(const.AI_END_TURN_DELAY)
        enemy.moves_left = 0
        enemy.shots_left = 0
        
        return ai_state

    @staticmethod
    def _should_shoot_first(enemy: Character, player: Character, obstacles: List[Tuple[int, int]]) -> bool:
        """Decide whether to shoot first or move first based on tactical considerations."""
        dx, dy = player.x - enemy.x, player.y - enemy.y
        
        # If player is in line of sight and path is clear, shoot first
        if (dx == 0 or dy == 0) and not AI._is_path_blocked(enemy.x, enemy.y, player.x, player.y, obstacles):
            return True
            
        # If player is adjacent, definitely shoot first
        if abs(dx) + abs(dy) == 1:
            return True
            
        # If low on health, prioritize shooting to deal damage
        if enemy.health < enemy.max_health * 0.3:
            return True
            
        # Otherwise, move first for better positioning
        return False

    @staticmethod
    def _handle_shooting(
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]], 
            projectiles: List[Projectile],
            redraw_callback
    ) -> bool:
        """Handle AI shooting logic with improved targeting."""
        dx, dy = player.x - enemy.x, player.y - enemy.y
        shot_taken = False
        
        # Line of sight shooting (same row or column)
        if (dx == 0 or dy == 0) and not AI._is_path_blocked(enemy.x, enemy.y, player.x, player.y, obstacles):
            pygame.time.delay(const.AI_SHOOTING_DELAY)
            
            # Determine shooting direction
            shoot_dx, shoot_dy = 0, 0
            if dx == 0:  # Same column
                shoot_dy = 1 if dy > 0 else -1
            else:  # Same row
                shoot_dx = 1 if dx > 0 else -1
            
            # Create projectile
            projectiles.append(
                Projectile(
                    enemy.x, enemy.y, shoot_dx, shoot_dy, 
                    enemy.sniper_type.color, enemy
                )
            )
            enemy.shots_left -= 1
            shot_taken = True
            
            # After shooting, redraw
            redraw_callback()
            pygame.time.delay(const.AI_SHOOTING_DELAY)
            
        # Adjacent shooting
        elif abs(dx) + abs(dy) == 1 and enemy.shots_left > 0:
            pygame.time.delay(const.AI_SHOOTING_DELAY)
            player.health -= const.PROJECTILE_DAMAGE
            enemy.shots_left -= 1
            shot_taken = True
            
        return shot_taken

    @staticmethod
    def _determine_best_position(
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]]
    ) -> Optional[Tuple[int, int]]:
        """
        Determine the best tactical position for the AI to move to,
        considering both offensive and defensive factors.
        """
        # Get all possible moves within range
        possible_moves = AI._calculate_possible_moves(enemy, player, obstacles, enemy.moves_left)
        if not possible_moves:
            return None
            
        # Score each position based on tactical value
        move_scores = {}
        for pos in possible_moves:
            score = 0
            pos_x, pos_y = pos
            
            # Distance to player (closer is usually better but not too close)
            distance = abs(pos_x - player.x) + abs(pos_y - player.y)
            
            # Prefer positions where we can shoot the player
            if (pos_x == player.x or pos_y == player.y) and not AI._is_path_blocked(
                    pos_x, pos_y, player.x, player.y, obstacles):
                score += 50  # Strong bonus for shooting positions
            
            # Prefer positions with medium distance (not too close, not too far)
            if 2 <= distance <= 3:
                score += 30
            elif distance == 1:
                score += 10  # Being adjacent is okay but risky
            else:
                score += max(0, 20 - (distance - 3) * 5)  # Diminishing returns for distances > 3
            
            # Prefer positions near cover (adjacent to obstacles)
            cover_score = sum(1 for ox, oy in obstacles if abs(ox - pos_x) + abs(oy - pos_y) == 1)
            score += cover_score * 10
            
            # Avoid dead ends (positions with limited exits)
            exit_count = sum(1 for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)] 
                            if (pos_x + dx, pos_y + dy) not in obstacles 
                            and 0 <= pos_x + dx < const.GRID_WIDTH 
                            and 0 <= pos_y + dy < const.GRID_HEIGHT)
            if exit_count <= 1:
                score -= 40  # Heavy penalty for positions with only 0-1 exits
            
            move_scores[pos] = score
        
        # Return the position with the highest score
        if move_scores:
            return max(move_scores.items(), key=lambda x: x[1])[0]
        return None

    @staticmethod
    def _calculate_possible_moves(
            enemy: Character, 
            player: Character, 
            obstacles: List[Tuple[int, int]], 
            move_limit: int
    ) -> List[Tuple[int, int]]:
        """Calculate all possible positions the AI can move to."""
        possible_moves = []
        for mx in range(-move_limit, move_limit + 1):
            for my in range(-move_limit, move_limit + 1):
                if abs(mx) + abs(my) <= move_limit:  # Include current position
                    new_x, new_y = enemy.x + mx, enemy.y + my
                    if 0 <= new_x < const.GRID_WIDTH and 0 <= new_y < const.GRID_HEIGHT:
                        if (new_x, new_y) not in obstacles and (new_x, new_y) != (player.x, player.y):
                            possible_moves.append((new_x, new_y))
        return possible_moves

    @staticmethod
    def _astar_pathfinding(
            start: Tuple[int, int],
            goal: Tuple[int, int],
            obstacles: List[Tuple[int, int]],
            move_limit: int
    ) -> List[Tuple[int, int]]:
        """
        A* pathfinding algorithm to find the optimal path from start to goal,
        avoiding obstacles and respecting the move limit.
        """
        # If start and goal are the same, return empty path
        if start == goal:
            return []
            
        # Convert obstacles to a set for faster lookups
        obstacles_set = set(obstacles)
        
        # Initialize the open and closed sets
        open_set = []
        closed_set = set()
        
        # Cost from start to current node
        g_score = {start: 0}
        
        # Estimated total cost from start to goal through this node
        f_score = {start: AI._heuristic(start, goal)}
        
        # Use heapq to manage the priority queue
        heapq.heappush(open_set, (f_score[start], start))
        
        # For path reconstruction
        came_from = {}
        
        # Avoid infinite loops with a counter
        max_iterations = 1000  # Set a reasonable limit
        iteration_count = 0
        
        while open_set and iteration_count < max_iterations:
            iteration_count += 1
            
            # Get the node with the lowest f_score
            try:
                _, current = heapq.heappop(open_set)
            except IndexError:
                break  # Safety check if heapq is empty
            
            # If we've reached the goal, reconstruct path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]  # Reverse the path
                
            # Mark as visited
            closed_set.add(current)
            
            # Check if we've exceeded move limit
            if g_score[current] >= move_limit:
                continue
                
            # Check all valid neighbor tiles
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Skip if out of bounds
                if (neighbor[0] < 0 or neighbor[0] >= const.GRID_WIDTH or
                    neighbor[1] < 0 or neighbor[1] >= const.GRID_HEIGHT):
                    continue
                
                # Skip if obstacle or already visited    
                if neighbor in obstacles_set or neighbor in closed_set:
                    continue
                    
                # Calculate new g_score
                tentative_g_score = g_score[current] + 1
                
                # Skip if exceeds move limit
                if tentative_g_score > move_limit:
                    continue
                
                # If neighbor not in open set or this path is better
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + AI._heuristic(neighbor, goal)
                    
                    # Add to open set if not already there
                    if not any(node == neighbor for _, node in open_set):
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # If no path is found, return best partial path
        if came_from:
            # Find the closest we got to the goal
            closest = min(came_from.keys(), key=lambda x: AI._heuristic(x, goal))
            path = []
            current = closest
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Reverse the path
        
        return []  # No path found at all

    @staticmethod
    def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance heuristic for A* algorithm."""
        return abs(b[0] - a[0]) + abs(b[1] - a[1])

    @staticmethod
    def _animate_movement(enemy: Character, path: List[Tuple[int, int]], redraw_callback) -> None:
        """Animate enemy movement along a path."""
        distance_moved = 0
        
        for path_x, path_y in path:
            # Calculate distance of this step
            step_distance = abs(path_x - enemy.x) + abs(path_y - enemy.y)
            
            # Check if this step would exceed the move limit
            if distance_moved + step_distance > enemy.moves_left:
                break
                
            # Move one tile at a time
            enemy.x, enemy.y = path_x, path_y
            distance_moved += step_distance
            
            # Redraw the screen to show movement
            redraw_callback()
            
            # Delay between each tile movement
            pygame.time.delay(const.ANIMATION_DELAY)
        
        # Update remaining moves
        enemy.moves_left -= distance_moved

    @staticmethod
    def _is_path_blocked(
            x1: int, 
            y1: int, 
            x2: int, 
            y2: int, 
            obstacles: List[Tuple[int, int]]
    ) -> bool:
        """Check if there's an obstacle between two points."""
        # If not in the same row or column, path is not straight
        if x1 != x2 and y1 != y2:
            return True
            
        # Check for obstacles in path
        if x1 == x2:  # Same column
            start, end = min(y1, y2), max(y1, y2)
            return any((x1, y) in obstacles for y in range(start + 1, end))
        else:  # Same row
            start, end = min(x1, x2), max(x1, x2)
            return any((x, y1) in obstacles for x in range(start + 1, end))