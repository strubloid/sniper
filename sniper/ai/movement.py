"""
Movement module - Controls character movement execution and animation.
"""
from typing import List, Tuple, Callable

import pygame
from sniper.config.constants import const, debug_print
from sniper.models.characters import Character

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