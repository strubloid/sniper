"""
Models for the Sniper Game.
This module contains the data classes and models for game entities.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import pygame

from constants import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, BLUE


@dataclass
class SniperType:
    """Defines a character type with specific attributes and abilities."""
    name: str
    sprite: pygame.Surface
    color: tuple
    description: str
    move_limit: int
    power: str
    projectiles_per_turn: int = 1


@dataclass
class Character:
    """Represents a player or enemy character in the game."""
    x: int
    y: int
    sniper_type: SniperType
    health: int = 100
    max_health: int = 100
    is_player: bool = True
    moves_left: int = 0
    shots_left: int = 0
    show_range: bool = False

    def start_turn(self) -> None:
        """Reset character stats for the start of a new turn."""
        self.moves_left = self.sniper_type.move_limit
        self.shots_left = self.sniper_type.projectiles_per_turn
        self.show_range = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the character on the given surface."""
        sprite = pygame.transform.scale(self.sniper_type.sprite, (GRID_SIZE, GRID_SIZE))
        surface.blit(sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def draw_range(self, surface: pygame.Surface) -> None:
        """Draw the movement range for the character."""
        if not self.show_range or self.moves_left == 0:
            return
        for dx in range(-self.moves_left, self.moves_left + 1):
            for dy in range(-self.moves_left, self.moves_left + 1):
                if abs(dx) + abs(dy) <= self.moves_left:
                    tx, ty = self.x + dx, self.y + dy
                    if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                        s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                        s.fill(BLUE)
                        surface.blit(s, (tx * GRID_SIZE, ty * GRID_SIZE))


@dataclass
class Projectile:
    """Represents a projectile fired by a character."""
    x: int
    y: int
    dx: int
    dy: int
    color: tuple
    owner: Character


@dataclass
class Button:
    """Represents a UI button with text and click detection."""
    rect: pygame.Rect
    text: str
    color: tuple
    border_color: tuple
    text_color: tuple
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the button was clicked given a position."""
        return self.rect.collidepoint(pos)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the given surface."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)