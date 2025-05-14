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
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
RED = (200, 50, 50)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255, 100)

# Block health colors
BLOCK_HEALTHY = (80, 80, 80)       # Healthy/undamaged blocks
BLOCK_DAMAGED = (120, 70, 70)      # Damaged blocks
BLOCK_CRITICAL = (180, 60, 60)     # Critically damaged blocks

# Game settings
HEALTH_DAMAGE_PER_MOVE = 5
PROJECTILE_DAMAGE = 20
OBSTACLE_COUNT = 20
BLOCK_MAX_HEALTH = 3              # Maximum health for blocks/obstacles
BLOCK_DAMAGE_PER_HIT = 1          # Damage per projectile hit
SCENARIO_POPULATION = 20          # Default population count for obstacles in a scenario
ANIMATION_DELAY = 300
BLOCK_FADE_DURATION = 500         # Duration for blocks fading out (ms)
BLOCK_APPEAR_DURATION = 500       # Duration for blocks appearing (ms)
ROUND_TRANSITION_DELAY = 1000     # Delay between rounds (ms)
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
PROJECTILE_RADIUS = 10

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