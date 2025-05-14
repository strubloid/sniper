"""
Constants for the Sniper Game.
This file contains all the constants used across the game to ensure consistency
and make changing values easier.
"""
import os
import pygame

# Screen and grid settings
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
GRID_SIZE = 32
# Visual grid dimensions (what's displayed on screen)
VISIBLE_GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE  
VISIBLE_GRID_HEIGHT = (SCREEN_HEIGHT - 110) // GRID_SIZE  # Accounting for top HUD space
# Actual game world dimensions (10x bigger)
GRID_WIDTH = VISIBLE_GRID_WIDTH * 10
GRID_HEIGHT = VISIBLE_GRID_HEIGHT * 10
FPS = 60

# Camera settings
CAMERA_MOVE_SPEED = 15  # Camera movement speed

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
RED = (200, 50, 50)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255, 100)
ORANGE = (255, 140, 0)  # Adding the missing ORANGE color
BG_COLOR = (30, 30, 40)  # Dark blue-gray background color
GRID_COLOR = (50, 50, 50)  # Dark gray color for grid lines
OBSTACLE_COLOR = (120, 80, 40)  # Brown color for obstacles
ARROW_COLOR = (255, 200, 0)  # Bright yellow color for direction arrows

# Game settings
HEALTH_DAMAGE_PER_MOVE = 5
PROJECTILE_DAMAGE = 20
PROJECTILE_SPEED = 8  # Added missing projectile speed constant
OBSTACLE_COUNT = 100  # Increased from 60 to 100 for an even fuller map
ANIMATION_DELAY = 300
AI_AIMING_DELAY = 500
AI_SHOOTING_DELAY = 500
AI_END_TURN_DELAY = 500
AI_TURN_DELAY = 1500  # Delay before AI takes its turn (milliseconds)

# AI Animation and Timing Constants
AI_THINKING_DELAY = 300
AI_END_DELAY = 300
MOVEMENT_ANIMATION_DELAY = 200
AI_SHOT_FEEDBACK_DELAY = 400

# AI Tactical Decision Making Constants
AI_SCORE_HAS_SHOT = 100       # Score bonus for positions with line of fire
AI_SCORE_PER_COVER = 15       # Score bonus per cover adjacent to position
AI_SCORE_HEALTH_DANGER = 50   # Penalty for health-threatening moves
AI_HEALTH_PENALTY_FACTOR = 0.5  # Factor for scaling health penalties
AI_MAX_HEALTH_PENALTY_RATIO = 0.3  # Maximum health percentage AI will risk
AI_SCORE_OPTIMAL_DIST = 30    # Score for optimal distance from player
AI_SCORE_TOO_CLOSE = 20       # Penalty for being too close to player
AI_SCORE_DISTANT = 25         # Base score for distance-related calculations
AI_DIST_PENALTY_FACTOR = 5    # Factor for penalizing excessive distance
AI_RANDOM_FACTOR = 5          # Random variance to avoid predictability
AI_OPTIMAL_DIST_MIN = 2       # Minimum preferred distance from player
AI_OPTIMAL_DIST_MAX = 3       # Maximum preferred distance from player

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Game states
STATE_MENU = "menu"
STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_SCOREBOARD = "scoreboard"
STATE_GAME_OVER = "game_over"

# Game modes
MODE_AI = "ai"          # Player vs AI
MODE_PVP = "pvp"        # Player vs Player (local)
MODE_NETWORK = "net"    # Player vs Player (network)

# AI states
AI_STATE_THINKING = "THINKING"
AI_STATE_AIMING = "AIMING"
AI_STATE_SHOOTING = "SHOOTING"
AI_STATE_END = "END"

# Character positions
PLAYER_START_X = 5
PLAYER_START_Y = 5
ENEMY_START_X = 15
ENEMY_START_Y = 5

# UI Settings
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200
BUTTON_SPACING = 20
HUD_SPACING = 10
PROJECTILE_RADIUS = 6

# Debugging control
DEBUG = 1

def debug_print(*args, **kwargs):
    """Print debug messages if DEBUG is enabled."""
    if DEBUG:
        print(*args, **kwargs)

# Create a namespace for the constants to make imports cleaner
class _Constants:
    def __init__(self):
        # Copy all module-level constants to this object
        for name, value in globals().items():
            if name.isupper() or name == 'debug_print':
                setattr(self, name, value)

# Export a single 'const' instance that can be imported elsewhere
const = _Constants()