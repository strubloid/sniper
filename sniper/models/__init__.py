"""
Models module for the Sniper Game.

This package contains game entity model classes:
- Character models 
- Projectile models
- UI element models
"""

from .characters import Character, SniperType
from .projectiles import Projectile
from .ui_elements import Button

__all__ = ['Character', 'SniperType', 'Projectile', 'Button']