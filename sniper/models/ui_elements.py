"""
UI elements for the Sniper Game.
"""
import pygame
from typing import Tuple, List, Dict, Any

from sniper.config.constants import const

class Button:
    """Class representing a clickable button in the UI."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int] = (200, 200, 200)):
        """Initialize a new button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 50, 255), 
                           min(color[1] + 50, 255),
                           min(color[2] + 50, 255))
        self.is_hovered = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the given surface."""
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)  # Border
        
        # Draw button text
        text_surface = font.render(self.text, True, (10, 10, 10))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the hover state of the button."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)