"""
AI Controller module - Main AI class that coordinates AI decision making.
"""
import traceback
from typing import List, Tuple, Callable, Optional

import pygame
from sniper.config.constants import const, debug_print
from sniper.models.characters import Character
from sniper.models.projectiles import Projectile
from sniper.ai.state import AIStateManager
from sniper.ai.tactical import LineOfSightCalculator, TacticalPositionFinder
from sniper.ai.movement import MovementExecutor
from sniper.ai.projectiles import ProjectileManager

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
            redraw_callback: Callable,
            game_manager=None
    ) -> str:
        """
        Execute AI's turn with improved tactical decision making.
        Uses a phase-based approach to prioritize actions:
        1. Attack if player is in line of sight
        2. Move to optimal tactical position
        3. Attack again if possible after movement
        
        Args:
            game_manager: Reference to GameManager for health checks
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
            ai_state = cls._execute_movement_phase(enemy, player, obstacles, redraw_callback, game_manager)
            ai_state = cls._execute_post_move_shooting(enemy, player, obstacles, projectiles, redraw_callback)
            
            # End turn with status
            ai_state = cls._state_manager.transition_to_end(redraw_callback)
            debug_print("--- AI Turn End ---")
        except Exception as e:
            debug_print(f"AI Error: {str(e)}")
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
            obstacles: List[Tuple[int, int]], redraw_callback: Callable, game_manager=None
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
            cls._movement_executor.execute_movement(enemy, path, redraw_callback, game_manager)
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