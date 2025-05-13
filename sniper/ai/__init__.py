"""
AI module for the Sniper Game.

This package contains AI-related classes for enemy behavior:
- Strategy implementations
- Pathfinding algorithms
- Decision making logic
- State management
"""

from .ai_controller import AI
from .strategies import AIStrategy, TacticalAI
from .pathfinding import PathFinder
from .movement import MovementExecutor
from .state import AIStateManager
from .tactical import TacticalPositionFinder, LineOfSightCalculator
from .projectiles import ProjectileManager

# Make these classes available when importing from the ai package
__all__ = [
    'AI', 
    'AIStrategy', 
    'TacticalAI', 
    'PathFinder',
    'MovementExecutor', 
    'AIStateManager',
    'TacticalPositionFinder',
    'LineOfSightCalculator',
    'ProjectileManager'
]