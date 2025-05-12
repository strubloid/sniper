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

# Game settings
HEALTH_DAMAGE_PER_MOVE = 5
PROJECTILE_DAMAGE = 20
OBSTACLE_COUNT = 20
ANIMATION_DELAY = 300
AI_AIMING_DELAY = 500
AI_SHOOTING_DELAY = 500
AI_END_TURN_DELAY = 500
AI_TURN_DELAY = 1500  # Delay before AI takes its turn (milliseconds)

# Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Game states
STATE_MENU = "menu"
STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_SCOREBOARD = "scoreboard"
STATE_GAME_OVER = "game_over"

# AI states
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