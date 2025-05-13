"""
Character models for the Sniper Game.
"""
import pygame
from typing import Tuple, Optional

from sniper.config.constants import const

class SniperType:
    """Class representing a type of sniper with specific abilities."""
    
    def __init__(self, name: str, sprite: pygame.Surface, color: Tuple[int, int, int], 
                 description: str, move_limit: int, special_power: str):
        """Initialize a new sniper type."""
        self.name = name
        self.sprite = sprite
        self.color = color
        self.description = description
        self.move_limit = move_limit
        self.special_power = special_power


class Character:
    """Class representing a character in the game (player or enemy)."""
    
    def __init__(self, x: int, y: int, sniper_type: SniperType, is_player: bool = True):
        """Initialize a new character."""
        self.x = x
        self.y = y
        self.sniper_type = sniper_type
        self.health = 100
        self.shots_left = 1
        self.moves_left = 0
        self.is_player = is_player
        self.show_range = False
    
    def start_turn(self):
        """Reset character for a new turn."""
        self.moves_left = self.sniper_type.move_limit
        self.shots_left = 1  # Default is 1 shot per turn
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the character on the surface."""
        rect = pygame.Rect(
            self.x * const.GRID_SIZE, 
            self.y * const.GRID_SIZE,
            const.GRID_SIZE, 
            const.GRID_SIZE
        )
        
        # Draw character sprite if available, otherwise use a colored rectangle
        if hasattr(self.sniper_type, 'sprite') and self.sniper_type.sprite:
            surface.blit(self.sniper_type.sprite, rect)
        else:
            pygame.draw.rect(surface, self.sniper_type.color, rect)
    
    def draw_range(self, surface: pygame.Surface) -> None:
        """Draw the movement range if shown."""
        if self.show_range and self.moves_left > 0:
            for x in range(max(0, self.x - self.moves_left), min(const.GRID_WIDTH, self.x + self.moves_left + 1)):
                for y in range(max(0, self.y - self.moves_left), min(const.GRID_HEIGHT, self.y + self.moves_left + 1)):
                    # Skip positions that are out of range (using Manhattan distance)
                    if abs(x - self.x) + abs(y - self.y) <= self.moves_left:
                        highlight_rect = pygame.Rect(
                            x * const.GRID_SIZE, 
                            y * const.GRID_SIZE,
                            const.GRID_SIZE, 
                            const.GRID_SIZE
                        )
                        highlight_surface = pygame.Surface(
                            (const.GRID_SIZE, const.GRID_SIZE), 
                            pygame.SRCALPHA
                        )
                        pygame.draw.rect(
                            highlight_surface, 
                            (*self.sniper_type.color[:3], 50),  # Semi-transparent color
                            highlight_surface.get_rect()
                        )
                        surface.blit(highlight_surface, highlight_rect)