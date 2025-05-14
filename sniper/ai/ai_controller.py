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
        1. Move to find a position with line of sight to player
        2. Shoot if player is in line of sight
        3. Retreat to a covered position if possible
        
        Args:
            game_manager: Reference to GameManager for health checks
        """
        print("AI.take_turn called - starting AI decision process")
        print(f"AI position: ({enemy.x}, {enemy.y}), Player position: ({player.x}, {player.y})")
        print(f"AI has {enemy.moves_left} moves and {enemy.shots_left} shots")
        
        # Ensure enemy stats are reset for this turn
        enemy.start_turn()
        
        # Initialize AI state and show thinking animation
        ai_state = cls._state_manager.transition_to_thinking(redraw_callback)
        
        try:
            print("--- AI Turn Start ---")
            print(f"Enemy at ({enemy.x}, {enemy.y}), Player at ({player.x}, {player.y})")
            print(f"Moves left: {enemy.moves_left}, Shots left: {enemy.shots_left}")
            
            # PHASE 1: Check if we already have line of sight - this saves movement points
            current_can_shoot = cls._line_of_sight.has_line_of_fire(enemy, player, obstacles)
            print(f"Current position line of sight check: {current_can_shoot}")
            
            if not current_can_shoot:
                # PHASE 2: Move to find a position with line of sight
                print("AI doesn't have line of sight - trying to find position with line of sight")
                ai_state = cls._execute_offensive_movement_phase(enemy, player, obstacles, redraw_callback, game_manager)
                print(f"After offensive movement, AI is at ({enemy.x}, {enemy.y}) with {enemy.moves_left} moves left")
            
            # PHASE 3: Shoot if we have line of sight
            print("AI attempting to shoot")
            ai_state = cls._execute_shooting_phase(enemy, player, obstacles, projectiles, redraw_callback)
            
            # PHASE 4: Retreat to safety if we have moves left
            if enemy.moves_left > 0:
                print(f"AI has {enemy.moves_left} moves left - attempting retreat")
                ai_state = cls._execute_retreat_phase(enemy, player, obstacles, redraw_callback, game_manager)
                print(f"After retreat, AI is at ({enemy.x}, {enemy.y})")
            
            # End turn with status
            ai_state = cls._state_manager.transition_to_end(redraw_callback)
            print("--- AI Turn End ---")
        except Exception as e:
            print(f"AI ERROR: {str(e)}")
            import traceback
            print(f"AI ERROR TRACEBACK: {traceback.format_exc()}")
            ai_state = const.AI_STATE_END
        
        # Reset enemy movement and shots at end of turn
        enemy.moves_left = 0
        enemy.shots_left = 0
        
        return ai_state
    
    @classmethod
    def _execute_offensive_movement_phase(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], redraw_callback: Callable, game_manager=None
    ) -> str:
        """Execute movement to find a position with line of sight to the player, or get close for courage."""
        debug_print("Phase 1: Offensive Movement - Finding position with line of sight or proximity")

        if enemy.moves_left <= 0:
            debug_print("  No moves left for offensive movement phase")
            return const.AI_STATE_THINKING
            
        debug_print(f"  Enemy has {enemy.moves_left} moves left, finding position with line of sight")
        ai_state = cls._state_manager.transition_to_aiming(redraw_callback)

        # Try to find a position with line of sight to player
        offensive_move = cls._tactical_finder.find_position_with_line_of_sight(
            enemy, player, obstacles, enemy.moves_left
        )

        if offensive_move:
            new_pos, path = offensive_move
            debug_print(f"  Offensive move: {new_pos} via path of length {len(path)}")
            cls._movement_executor.execute_movement(enemy, path, redraw_callback, game_manager)
            debug_print(f"  Movement executed, enemy now at ({enemy.x}, {enemy.y})")
        else:
            debug_print("  No position with line of sight found, trying to move within courage proximity range")
            # Try to move within COURAGE_PROXIMITY_RANGE of the player
            proximity_move = cls._tactical_finder.find_position_within_proximity(
                enemy, player, obstacles, enemy.moves_left, const.COURAGE_PROXIMITY_RANGE
            ) if hasattr(cls._tactical_finder, 'find_position_within_proximity') else None
            if proximity_move:
                new_pos, path = proximity_move
                debug_print(f"  Proximity move: {new_pos}")
                cls._movement_executor.execute_movement(enemy, path, redraw_callback, game_manager)
                debug_print(f"  Movement executed, enemy now at ({enemy.x}, {enemy.y})")
            else:
                debug_print("  No proximity move found, falling back to tactical move")
                best_move = cls._tactical_finder.find_best_tactical_position(
                    enemy, player, obstacles, enemy.moves_left
                )
                if best_move:
                    new_pos, path = best_move
                    debug_print(f"  Standard tactical move: {new_pos}")
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
    def _execute_shooting_phase(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], projectiles: List[Projectile],
            redraw_callback: Callable
    ) -> str:
        """Execute the shooting phase if we have line of sight."""
        debug_print("Phase 2: Shooting - Checking line of sight")

        # Spend courage for extra shots as long as possible
        while enemy.courage >= const.COURAGE_BUTTON_COST:
            used = enemy.use_courage_ability()
            if used:
                debug_print(f"AI spent courage for extra shot. Shots left: {enemy.shots_left}, Courage: {enemy.courage}")
            else:
                break

        if enemy.shots_left <= 0:
            debug_print("  No shots available")
            return const.AI_STATE_THINKING
            
        debug_print(f"Enemy has {enemy.shots_left} shots left, checking line of fire...")
        can_shoot = cls._line_of_sight.has_line_of_fire(enemy, player, obstacles)
        debug_print(f"  Can shoot: {can_shoot}")
        
        if can_shoot:
            debug_print("  -> Taking shots for all available shots")
            ai_state = cls._state_manager.transition_to_shooting(redraw_callback)
            # Loop through all available shots
            while enemy.shots_left > 0 and cls._line_of_sight.has_line_of_fire(enemy, player, obstacles):
                shot_success = cls._projectile_manager.create_projectile(enemy, player, projectiles)
                debug_print(f"  Shot executed with success: {shot_success}, shots remaining: {enemy.shots_left}")
                redraw_callback()
                pygame.time.delay(const.AI_SHOT_FEEDBACK_DELAY)
            return ai_state
        
        return const.AI_STATE_THINKING
    
    @classmethod
    def _execute_retreat_phase(
            cls, enemy: Character, player: Character, 
            obstacles: List[Tuple[int, int]], redraw_callback: Callable, game_manager=None
    ) -> str:
        """Execute retreat to safety if we have moves left."""
        debug_print("Phase 3: Retreat - Finding safe position")
        
        if enemy.moves_left <= 0:
            debug_print("  No moves left for retreat phase")
            return const.AI_STATE_THINKING
            
        debug_print(f"  Enemy has {enemy.moves_left} moves left, finding retreat position")
        ai_state = cls._state_manager.transition_to_aiming(redraw_callback)
        
        # Try to find a retreat position
        retreat_move = cls._tactical_finder.find_retreat_position(
            enemy, player, obstacles, enemy.moves_left
        )
        
        if retreat_move:
            new_pos, path = retreat_move
            debug_print(f"  Retreat move: {new_pos} via path of length {len(path)}")
            cls._movement_executor.execute_movement(enemy, path, redraw_callback, game_manager)
            debug_print(f"  Retreat executed, enemy now at ({enemy.x}, {enemy.y})")
        else:
            debug_print("  No retreat position found")
            
        return ai_state