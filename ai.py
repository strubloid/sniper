"""
AI module for the Sniper Game.
This module handles AI movement, decision-making, and actions.
"""
import pygame
import random
from typing import List, Tuple, Optional

import constants as const
from models import Character, Projectile


class AI:
    """Handles AI logic for enemy characters."""

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
        Execute AI's turn with various decisions and animations.
        Returns the current AI state.
        """
        # Calculate direction to player
        dx, dy = player.x - enemy.x, player.y - enemy.y
        move_limit = enemy.sniper_type.move_limit

        # Aiming phase
        ai_state = const.AI_STATE_AIMING
        pygame.time.delay(const.AI_AIMING_DELAY)

        # Check if player is in line of sight (same row or column) and shoot if possible
        if enemy.shots_left > 0:
            # Line of sight shooting (same row or column)
            if dx == 0 or dy == 0:
                ai_state = const.AI_STATE_SHOOTING
                pygame.time.delay(const.AI_SHOOTING_DELAY)
                
                # Check for obstacles in the path
                if not AI._is_path_blocked(enemy.x, enemy.y, player.x, player.y, obstacles):
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
                    
                    # After shooting, redraw
                    redraw_callback()
                    pygame.time.delay(const.AI_SHOOTING_DELAY)
                    
            # Adjacent shooting
            elif abs(dx) + abs(dy) == 1 and enemy.shots_left > 0:
                ai_state = const.AI_STATE_SHOOTING
                pygame.time.delay(const.AI_SHOOTING_DELAY)
                player.health -= const.PROJECTILE_DAMAGE
                enemy.shots_left -= 1

        # Movement phase - if we didn't shoot or need to move closer
        if enemy.moves_left > 0:
            # Calculate possible moves within the move limit
            possible_moves = AI._calculate_possible_moves(enemy, player, obstacles, move_limit)

            # Choose the move that gets closest to the player
            best_move = AI._select_best_move(enemy, player, possible_moves)

            if best_move:
                # Calculate path and move AI character
                path = AI._calculate_path(enemy.x, enemy.y, best_move[0], best_move[1], obstacles)
                
                # Execute movement with animation
                AI._animate_movement(enemy, path, redraw_callback)

        # End turn
        ai_state = const.AI_STATE_END
        pygame.time.delay(const.AI_END_TURN_DELAY)
        enemy.moves_left = 0
        enemy.shots_left = 0
        
        return ai_state

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
                if abs(mx) + abs(my) <= move_limit and abs(mx) + abs(my) > 0:  # Exclude current position
                    new_x, new_y = enemy.x + mx, enemy.y + my
                    if 0 <= new_x < const.GRID_WIDTH and 0 <= new_y < const.GRID_HEIGHT:
                        if (new_x, new_y) not in obstacles and (new_x, new_y) != (player.x, player.y):
                            possible_moves.append((new_x, new_y))
        return possible_moves

    @staticmethod
    def _select_best_move(
            enemy: Character, 
            player: Character, 
            possible_moves: List[Tuple[int, int]]
    ) -> Optional[Tuple[int, int]]:
        """Select the best move from the possible moves."""
        if not possible_moves:
            return None
            
        # Choose the move that gets closest to the player
        best_move = min(
            possible_moves, 
            key=lambda pos: abs(pos[0] - player.x) + abs(pos[1] - player.y)
        )
        
        # Check if the move is within the remaining moves
        distance_moved = abs(best_move[0] - enemy.x) + abs(best_move[1] - enemy.y)
        if distance_moved <= enemy.moves_left:
            return best_move
        return None

    @staticmethod
    def _calculate_path(
            start_x: int, 
            start_y: int, 
            end_x: int, 
            end_y: int,
            obstacles: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Calculate a path from start to end position, moving one tile at a time."""
        path = []
        current_x, current_y = start_x, start_y
        
        while (current_x, current_y) != (end_x, end_y):
            # Move horizontally or vertically (whichever is larger)
            next_x, next_y = current_x, current_y
            
            if abs(end_x - current_x) > abs(end_y - current_y):
                next_x += 1 if end_x > current_x else -1
            else:
                next_y += 1 if end_y > current_y else -1
            
            # If we've somehow reached an obstacle, try another direction
            if (next_x, next_y) in obstacles:
                # Try alternate direction
                if abs(end_x - current_x) > 0:
                    next_x = current_x
                    next_y = current_y + (1 if end_y > current_y else -1)
                else:
                    next_x = current_x + (1 if end_x > current_x else -1)
                    next_y = current_y
                    
                # If still an obstacle, stop movement
                if (next_x, next_y) in obstacles:
                    break
            
            current_x, current_y = next_x, next_y
            path.append((current_x, current_y))
                
        return path

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