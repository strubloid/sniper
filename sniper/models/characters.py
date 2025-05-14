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
        self.max_health = 100  # Adding max_health attribute
        self.shots_left = 1
        self.moves_left = 0
        self.is_player = is_player
        self.show_range = False
        
        # New attributes for game mechanics
        self.courage_points = 0
        self.xp = 0
        self.level = 1
        self.lives = 2  # Each character has 2 lives
        self.max_courage = 100
        self.max_xp = 100
        
        # Bonus stats based on level
        self.bonus_damage = 0
        self.bonus_moves = 0
    
    def start_turn(self):
        """Reset character for a new turn."""
        base_moves = self.sniper_type.move_limit
        self.moves_left = base_moves + self.bonus_moves
        self.shots_left = 1  # Default is 1 shot per turn
    
    def add_courage(self, amount: int) -> None:
        """Add courage points when landing a hit."""
        self.courage_points = min(self.max_courage, self.courage_points + amount)
        
    def add_xp(self, amount: int) -> bool:
        """
        Add experience points when getting a kill.
        Returns True if leveled up, False otherwise.
        """
        self.xp += amount
        
        # Check for level up
        if self.xp >= self.max_xp:
            self.level_up()
            self.xp = 0  # Reset XP after level up
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the character, improving their stats."""
        self.level += 1
        
        # Improve stats based on level
        self.bonus_damage += 5  # +5 damage per level
        self.bonus_moves += 1  # +1 move per level
        
        # Heal on level up
        self.health = min(self.max_health, self.health + 20)
    
    def lose_life(self) -> bool:
        """
        Lose a life when health reaches zero.
        Returns True if character still has lives left, False if game over.
        """
        self.lives -= 1
        
        if self.lives > 0:
            # Reset health for next life
            self.health = self.max_health
            return True
        return False
    
    def get_damage_output(self) -> int:
        """Get the total damage output with bonuses."""
        return const.PROJECTILE_DAMAGE + self.bonus_damage
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """Draw the character on the surface."""
        # Apply camera offset to position
        screen_x = int(self.x * const.GRID_SIZE) - camera_x
        screen_y = int(self.y * const.GRID_SIZE) - camera_y
        
        # Only draw if character is on screen
        if (0 <= screen_x < const.SCREEN_WIDTH and 
            0 <= screen_y < const.SCREEN_HEIGHT - 80):  # Account for bottom bar
            
            rect = pygame.Rect(
                screen_x,
                screen_y,
                const.GRID_SIZE, 
                const.GRID_SIZE
            )
            
            # Draw character sprite if available, otherwise use a colored rectangle
            if hasattr(self.sniper_type, 'sprite') and self.sniper_type.sprite:
                surface.blit(self.sniper_type.sprite, rect)
            else:
                pygame.draw.rect(surface, self.sniper_type.color, rect)
                
            # Draw health bar above character
            health_width = const.GRID_SIZE * (self.health / self.max_health)
            health_height = 5
            health_y = screen_y - health_height - 2
            
            # Background bar
            pygame.draw.rect(
                surface, 
                (200, 50, 50),  # Red
                pygame.Rect(screen_x, health_y, const.GRID_SIZE, health_height)
            )
            
            # Foreground health
            pygame.draw.rect(
                surface, 
                (50, 200, 50),  # Green
                pygame.Rect(screen_x, health_y, health_width, health_height)
            )
                
            # Draw level indicator
            if self.level > 1:
                level_text = str(self.level)
                font = pygame.font.SysFont(None, 20)
                text_surf = font.render(level_text, True, (255, 255, 255))
                text_rect = text_surf.get_rect(
                    center=(screen_x + const.GRID_SIZE - 10, 
                            screen_y + 10)
                )
                surface.blit(text_surf, text_rect)
                
            # Draw lives indicator
            for i in range(self.lives):
                life_x = screen_x + 6 + (i * 10)
                life_y = screen_y + const.GRID_SIZE - 10
                pygame.draw.circle(surface, (255, 0, 0), (life_x, life_y), 4)
    
    def draw_range(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """Draw the movement range if shown."""
        if self.show_range and self.moves_left > 0:
            # Convert coordinates to integers to avoid TypeError with range()
            int_x, int_y = int(self.x), int(self.y)
            moves_left = int(self.moves_left)  # Ensure moves_left is also an integer
            
            for x in range(max(0, int_x - moves_left), min(const.GRID_WIDTH, int_x + moves_left + 1)):
                for y in range(max(0, int_y - moves_left), min(const.GRID_HEIGHT, int_y + moves_left + 1)):
                    # Skip positions that are out of range (using Manhattan distance)
                    if abs(x - int_x) + abs(y - int_y) <= moves_left:
                        # Apply camera offset to the position
                        screen_x = x * const.GRID_SIZE - camera_x
                        screen_y = y * const.GRID_SIZE - camera_y
                        
                        highlight_rect = pygame.Rect(
                            screen_x, 
                            screen_y,
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