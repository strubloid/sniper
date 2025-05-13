"""
Game configuration using object-oriented design.
This module replaces the old constants-based approach with proper OOP structure.
"""

import os
from typing import Dict, Tuple, Any, List, Optional
import pygame

class Color:
    """Color definitions used throughout the game."""
    
    # Basic colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    GREEN = (50, 255, 50)
    BLUE = (50, 50, 255)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    
    # Game-specific colors
    BACKGROUND = (25, 25, 35)
    GRID_LINE = (60, 60, 80)
    UI_BACKGROUND = (40, 40, 60)
    UI_BORDER = (100, 100, 140)
    TEXT = (220, 220, 240)
    
    # Character colors
    GHOST_COLOR = (120, 180, 255)
    JUGGERNAUT_COLOR = (220, 100, 80)
    SCOUT_COLOR = (100, 220, 80)
    SHADE_COLOR = (180, 120, 220)
    
    @staticmethod
    def get_health_color(health_ratio: float) -> Tuple[int, int, int]:
        """
        Get a color representing health based on the ratio.
        
        Args:
            health_ratio: A float between 0.0 and 1.0 indicating health percentage
            
        Returns:
            A color tuple (r, g, b) representing the health level
        """
        if health_ratio > 0.7:
            return (50, 255, 50)  # Green for high health
        elif health_ratio > 0.3:
            return (255, 255, 50)  # Yellow for medium health
        else:
            return (255, 50, 50)   # Red for low health


class Paths:
    """Manages file paths for game assets and resources."""
    
    # Base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    
    @classmethod
    def get_asset_path(cls, filename: str) -> str:
        """
        Get the absolute path to an asset file.
        
        Args:
            filename: The name of the asset file
            
        Returns:
            The absolute path to the asset file
        """
        return os.path.join(cls.ASSETS_DIR, filename)
    
    @classmethod
    def get_character_description(cls, character_name: str) -> str:
        """
        Get the character description from a text file.
        
        Args:
            character_name: The name of the character
            
        Returns:
            The description text or an empty string if the file is not found
        """
        filename = f"{character_name.lower()}.txt"
        try:
            with open(cls.get_asset_path(filename), "r") as f:
                return f.read().strip()
        except (FileNotFoundError, IOError):
            return f"No description available for {character_name}."


class Debug:
    """Handles debug logging and settings."""
    
    ENABLED = True
    VERBOSE = False
    
    @classmethod
    def log(cls, *args, **kwargs):
        """Log a debug message if debug mode is enabled."""
        if cls.ENABLED:
            print(*args, **kwargs)
    
    @classmethod
    def verbose_log(cls, *args, **kwargs):
        """Log a verbose debug message if both debug and verbose modes are enabled."""
        if cls.ENABLED and cls.VERBOSE:
            print("[VERBOSE]", *args, **kwargs)


class DisplayConfig:
    """Configuration for display settings."""
    
    # Screen dimensions and grid settings
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 720
    GRID_SIZE = 32
    GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
    FPS = 60
    
    # UI elements sizing
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 200
    BUTTON_SPACING = 20
    HUD_SPACING = 10
    PROJECTILE_RADIUS = 6
    
    @classmethod
    def get_grid_position(cls, x: int, y: int) -> Tuple[int, int]:
        """Convert grid coordinates to pixel position."""
        return (x * cls.GRID_SIZE, y * cls.GRID_SIZE)
    
    @classmethod
    def get_grid_coords(cls, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """Convert pixel position to grid coordinates."""
        return (pixel_x // cls.GRID_SIZE, pixel_y // cls.GRID_SIZE)


class GameplayConfig:
    """Configuration for gameplay settings."""
    
    # Health and damage settings
    HEALTH_DAMAGE_PER_MOVE = 5
    PROJECTILE_DAMAGE = 20
    
    # Level generation settings
    OBSTACLE_COUNT = 20
    
    # Animation and timing settings
    ANIMATION_DELAY = 300
    
    # Character starting positions
    PLAYER_START_X = 5
    PLAYER_START_Y = 5
    ENEMY_START_X = 15
    ENEMY_START_Y = 5
    
    @classmethod
    def get_starting_position(cls, is_player: bool) -> Tuple[int, int]:
        """Get starting position based on whether it's a player or enemy."""
        if is_player:
            return (cls.PLAYER_START_X, cls.PLAYER_START_Y)
        else:
            return (cls.ENEMY_START_X, cls.ENEMY_START_Y)


class AIConfig:
    """Configuration for AI behavior."""
    
    # AI timing settings
    AI_AIMING_DELAY = 500
    AI_SHOOTING_DELAY = 500
    AI_END_TURN_DELAY = 500
    AI_TURN_DELAY = 1500
    
    # AI state constants
    STATE_THINKING = "THINKING"
    STATE_AIMING = "AIMING"
    STATE_SHOOTING = "SHOOTING"
    STATE_END = "END"
    
    @classmethod
    def get_state_delay(cls, state: str) -> int:
        """Get the delay for a specific AI state in milliseconds."""
        if state == cls.STATE_THINKING:
            return cls.AI_TURN_DELAY
        elif state == cls.STATE_AIMING:
            return cls.AI_AIMING_DELAY
        elif state == cls.STATE_SHOOTING:
            return cls.AI_SHOOTING_DELAY
        elif state == cls.STATE_END:
            return cls.AI_END_TURN_DELAY
        else:
            return 0


class GameState:
    """Game state constants and management."""
    
    # Game state constants
    MENU = "menu"
    SELECT = "select"
    PLAY = "play"
    SCOREBOARD = "scoreboard"
    GAME_OVER = "game_over"
    
    @classmethod
    def is_valid_state(cls, state: str) -> bool:
        """Check if a string is a valid game state."""
        return state in {cls.MENU, cls.SELECT, cls.PLAY, cls.SCOREBOARD, cls.GAME_OVER}


class CharacterConfig:
    """Configuration for character attributes and types."""
    
    # Base health for all characters
    BASE_HEALTH = 100
    
    # Character type definitions
    GHOST = {
        'name': 'Ghost',
        'sprite_file': 'ghost.png',
        'color': Color.GHOST_COLOR,
        'description': 'Fast, high courage',
        'move_limit': 3,
        'power': 25,
        'projectiles_per_turn': 1
    }
    
    JUGGERNAUT = {
        'name': 'Juggernaut',
        'sprite_file': 'juggernaut.png',
        'color': Color.JUGGERNAUT_COLOR,
        'description': 'Tanky, bouncing shots',
        'move_limit': 2,
        'power': 35,
        'projectiles_per_turn': 1
    }
    
    SCOUT = {
        'name': 'Scout',
        'sprite_file': 'scout.png',
        'color': Color.SCOUT_COLOR,
        'description': 'Quick & nimble',
        'move_limit': 4,
        'power': 15,
        'projectiles_per_turn': 2
    }
    
    SHADE = {
        'name': 'Shade',
        'sprite_file': 'shade.png',
        'color': Color.SHADE_COLOR,
        'description': 'Can freeze enemies',
        'move_limit': 3,
        'power': 20,
        'projectiles_per_turn': 1
    }


class Config:
    """Master configuration class that provides access to all config components."""
    
    def __init__(self):
        self.display = DisplayConfig
        self.gameplay = GameplayConfig
        self.ai = AIConfig
        self.game_state = GameState
        self.color = Color
        self.paths = Paths
        self.debug = Debug
        self.character = CharacterConfig
        
    @staticmethod
    def get_instance() -> 'Config':
        """Get the singleton instance of the Config class."""
        if not hasattr(Config, '_instance'):
            Config._instance = Config()
        return Config._instance


# Create a global instance for easy access
config = Config.get_instance()