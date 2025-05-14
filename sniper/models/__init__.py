"""
Models module for the Sniper Game.

This package contains game entity model classes:
- Character models 
- Projectile models
- UI element models
- Scenario objects (blocks with health and animations)
"""

from .characters import Character, SniperType
from .projectiles import Projectile
from .ui_elements import Button
from .scenario_objects import Block, ScenarioManager

__all__ = ['Character', 'SniperType', 'Projectile', 'Button', 'Block', 'ScenarioManager']