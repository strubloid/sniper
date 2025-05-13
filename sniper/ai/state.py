"""
AI State Management module - Manages AI state transitions and rendering.
"""
from typing import Callable

import pygame
from sniper.config.constants import const

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