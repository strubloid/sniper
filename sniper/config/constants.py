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

# Space theme colors
SPACE_BG = (10, 10, 25)       # Deep space background
SPACE_GRID = (30, 30, 50)     # Subtle grid lines

# Asteroid colors (replacing block health colors)
ASTEROID_HEALTHY = (110, 100, 90)    # Healthy asteroid
ASTEROID_DAMAGED = (130, 90, 70)     # Damaged asteroid
ASTEROID_CRITICAL = (150, 70, 60)    # Critically damaged asteroid

# Block health colors (renamed but kept for backwards compatibility)
BLOCK_HEALTHY = ASTEROID_HEALTHY
BLOCK_DAMAGED = ASTEROID_DAMAGED
BLOCK_CRITICAL = ASTEROID_CRITICAL

# Round transition settings
ROUND_TRANSITION_DURATION = 3000   # Total duration of round transition (3 seconds)
ROUND_TRANSITION_TEXT_COLOR = (255, 255, 255)  # White text for countdown
ROUND_TRANSITION_BG_COLOR = (0, 0, 0, 180)    # Semi-transparent black background
ROUND_TRANSITION_COUNTDOWN = 3     # Countdown value in seconds
ROUND_TRANSITION_MAX_TIME = 10000  # Maximum time (10 seconds) a round transition can take before being forced to complete
POST_ENEMY_DELAY = 1000            # Delay after enemy turn before showing round transition (1 second)

# Game settings
HEALTH_DAMAGE_PER_MOVE = 5
PROJECTILE_DAMAGE = 20
OBSTACLE_COUNT = 50
BLOCK_MAX_HEALTH = 2              # Maximum health for blocks/obstacles
BLOCK_DAMAGE_PER_HIT = 1          # Damage per projectile hit
SCENARIO_POPULATION = 20          # Default population count for obstacles in a scenario
ANIMATION_DELAY = 300
BLOCK_FADE_DURATION = 500         # Duration for blocks fading out (ms)
BLOCK_APPEAR_DURATION = 500       # Duration for blocks appearing (ms)
ROUND_TRANSITION_DELAY = 1000     # Delay between rounds (ms)
AI_AIMING_DELAY = 1000
AI_SHOOTING_DELAY = 500
AI_END_TURN_DELAY = 500
AI_TURN_DELAY = 500  # Delay before AI takes its turn (milliseconds)

# AI Animation and Timing Constants
AI_THINKING_DELAY = 300
AI_END_DELAY = 300
MOVEMENT_ANIMATION_DELAY = 200
AI_SHOT_FEEDBACK_DELAY = 800

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

# Experience System Constants
EXPERIENCE_HIT_ROCK = 15          # Experience for hitting a rock
EXPERIENCE_DAMAGE_PLAYER = 25    # Experience for damaging a player
EXPERIENCE_KILL_PLAYER = 50      # Experience for killing a player
EXPERIENCE_DESTROY_ELEMENT = 15   # Experience for destroying environmental elements

# Courage System Constants
COURAGE_MAX = 100                # Maximum courage value
COURAGE_PROXIMITY_GAIN = 15       # Courage gained per second when near opponent
COURAGE_PROXIMITY_RANGE = 15      # Grid cells radius for proximity detection
COURAGE_HIT_ENVIRONMENT = 10      # Courage for destroying environment elements
COURAGE_KILL_PLAYER = 50         # Courage for killing a player
COURAGE_BUTTON_COST = 25         # Courage points consumed for extra shot
COURAGE_DAMAGE_OPPONENT = 15     # Courage gained for hitting an opponent
COURAGE_BUSH_COST = 10           # Courage cost to place a bush

# Health Regeneration for not moving
HEALTH_REGEN_NO_MOVE = 15         # Health regained when not moving in a turn

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
HUD_SPACING = 15
PROJECTILE_RADIUS = 10

# Debugging control
DEBUG = 1

# Bush settings
BUSH_GLOW_MARGIN = 2  # Margin for bush energy field in pixels
BUSH_HEALTH_DISPLAY = True  # Whether to show bush health

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