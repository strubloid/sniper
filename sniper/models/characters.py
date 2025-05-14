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
        
        # Experience system
        self.experience = 0
        self.level = 1
        
        # Courage system
        self.courage = 0  # Start with 0 courage
        self.last_proximity_time = 0  # Track when courage was last gained from proximity
        # Facing direction for abilities (dx, dy)
        self.facing = (0, -1)
    
    def start_turn(self):
        """Reset character for a new turn."""
        self.moves_left = self.sniper_type.move_limit
        self.shots_left = 1  # Default is 1 shot per turn
    
    def use_bush_ability(self) -> bool:
        """
        Consume courage to place a bush. Returns True if used.
        """
        from sniper.config.constants import const
        if self.courage >= const.COURAGE_BUSH_COST:
            self.courage -= const.COURAGE_BUSH_COST
            return True
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the character on the surface."""
        rect = pygame.Rect(
            int(self.x) * const.GRID_SIZE, 
            int(self.y) * const.GRID_SIZE,
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
            # Convert coordinates to integers to avoid TypeError with range()
            int_x, int_y = int(self.x), int(self.y)
            moves_left = int(self.moves_left)  # Ensure moves_left is also an integer
            
            for x in range(max(0, int_x - moves_left), min(const.GRID_WIDTH, int_x + moves_left + 1)):
                for y in range(max(0, int_y - moves_left), min(const.GRID_HEIGHT, int_y + moves_left + 1)):
                    # Skip positions that are out of range (using Manhattan distance)
                    if abs(x - int_x) + abs(y - int_y) <= moves_left:
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
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience to the character and return True if leveled up.
        """
        self.experience += amount
        # Simple level calculation: 100 XP per level
        new_level = 1 + self.experience // 100
        leveled_up = new_level > self.level
        self.level = new_level
        return leveled_up
    
    def add_courage(self, amount: int) -> None:
        """
        Add courage points to the character, capped at COURAGE_MAX.
        """
        self.courage = min(const.COURAGE_MAX, self.courage + amount)
    
    def use_courage_ability(self) -> bool:
        """
        Use courage points for a special ability.
        Returns True if the ability was used successfully.
        """
        if self.courage >= const.COURAGE_BUTTON_COST:
            self.courage -= const.COURAGE_BUTTON_COST
            self.shots_left += 1  # Grant an extra shot
            return True
        return False
    
    def check_proximity_courage(self, other_character) -> None:
        """
        Check if character is in proximity to another character and grant courage if so.
        This should be called once per second or at an appropriate interval.
        """
        current_time = pygame.time.get_ticks()
        # Only check once per second
        if current_time - self.last_proximity_time >= 1000:
            distance = abs(self.x - other_character.x) + abs(self.y - other_character.y)
            if distance <= const.COURAGE_PROXIMITY_RANGE:
                self.add_courage(const.COURAGE_PROXIMITY_GAIN)
                self.last_proximity_time = current_time