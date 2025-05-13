"""
Projectile models for the Sniper Game.
"""
import pygame
from typing import Tuple, Optional

from sniper.config.constants import const

class Projectile:
    """Class representing a projectile (bullet) in the game."""
    
    def __init__(self, x: float, y: float, dx: float, dy: float, 
                color: Tuple[int, int, int], owner=None):
        """Initialize a new projectile."""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.owner = owner  # Reference to the Character who fired this projectile