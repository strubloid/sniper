"""
Sniper Game - Main Entry Point

This is the main entry module for the Sniper Game which initializes and starts
the game loop, handling basic initialization and error management.
"""
import os
import sys
import random
import pygame

from sniper.config.constants import const, debug_print
from sniper.models import SniperType, Character, Projectile
from sniper.ui import UI
from sniper.ai import AI
from sniper.utils import load_image

class GameManager:
    """Main game manager class that coordinates game logic and rendering."""

    def __init__(self):
        """Initialize the game manager and pygame."""
        # Initialize pygame
        pygame.init()
        
        # Get the screen info to set borderless windowed fullscreen
        screen_info = pygame.display.Info()
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        
        # Set up the screen and clock - using borderless windowed mode 
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        pygame.display.set_caption("Sniper Game")
        self.clock = pygame.time.Clock()
        
        # Create a virtual screen at the original resolution for the game logic
        self.virtual_screen = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        self.surface = self.virtual_screen  # Add this line to fix the missing surface attribute
        
        # Set scaling to fill the entire screen width and height
        self.scale_x = self.screen_width / const.SCREEN_WIDTH
        self.scale_y = self.screen_height / const.SCREEN_HEIGHT
        
        # Set up fonts
        self.fonts = {
            'normal': pygame.font.SysFont(None, 24),
            'big': pygame.font.SysFont(None, 48),
            'small': pygame.font.SysFont(None, 18)  # Adding the missing small font
        }
        
        # Create UI manager
        self.ui = UI(self.virtual_screen, self.fonts)
        self.ui_renderer = self.ui  # Add this line to fix the missing ui_renderer attribute
        
        # Game state
        self.game_state = const.STATE_MENU
        self.player = None
        self.enemy = None
        self.projectiles = []
        self.character_select_stage = "player"
        self.selected_candidate = None
        self.show_confirm_popup = False
        self.player_turn = True
        self.shooting_mode = False  # Changed from self.shoot_mode to self.shooting_mode
        self.obstacles = []
        self.winner = None
        self.show_debug = False
        self.ai_state = None
        self.scores = []
        
        # Camera system variables
        self.camera_x = 0
        self.camera_y = 0
        self.is_camera_dragging = False
        self.camera_drag_start = (0, 0)
        # Define map boundaries (add margins based on grid size)
        self.max_camera_x = const.GRID_SIZE * (const.GRID_WIDTH + 10)
        self.max_camera_y = const.GRID_SIZE * (const.GRID_HEIGHT + 10)
        
        # AI turn handling
        self.ai_turn_started = False
        self.ai_turn_time = 0
        
        # Load sniper types
        self.sniper_types = self._load_sniper_types()
    
    def _load_sniper_types(self) -> list:
        """Load available sniper types."""
        sniper_types = []
        
        # Define sniper types with their properties
        type_data = [
            ("Ghost", "Fast, high courage", (150, 150, 255), 3, "piercing"),
            ("Juggernaut", "Tanky, bouncing shots", (255, 100, 100), 2, "bouncing"),
            ("Scout", "Quick & nimble", (100, 255, 100), 4, "fast"),
            ("Shade", "Can freeze enemies", (200, 0, 200), 3, "freezing")
        ]
        
        # Load sprite for each type
        for name, desc, color, limit, power in type_data:
            try:
                sprite_path = f"{name.lower()}.png"
                sprite = load_image(sprite_path)
                sniper_types.append(SniperType(name, sprite, color, desc, limit, power))
            except Exception as e:
                debug_print(f"Error loading sprite for {name}: {e}")
                # Use a fallback if sprite loading fails
                sniper_types.append(SniperType(name, None, color, desc, limit, power))
        
        return sniper_types

    def start_game(self):
        """Start a new game by generating random spawn positions and obstacles."""
        # Generate random spawn positions
        player_pos, enemy_pos = self._generate_spawn_positions()
        
        # Update character positions
        self.player.x, self.player.y = player_pos
        self.enemy.x, self.enemy.y = enemy_pos
        
        # Generate obstacles including protective blocks
        self.obstacles = self._generate_obstacles(self.player, self.enemy)
        
        # Update the camera boundaries based on the map size
        self.max_camera_x = const.GRID_SIZE * const.GRID_WIDTH
        self.max_camera_y = const.GRID_SIZE * const.GRID_HEIGHT
        
        # Center camera on player at start
        self.return_to_player()
        
        debug_print(f"Game started with player at {player_pos} and enemy at {enemy_pos}")

    def regenerate_map(self):
        """Creates a new map layout for the next round."""
        # Clear projectiles
        self.projectiles.clear()
        
        # Generate new spawn positions
        player_pos, enemy_pos = self._generate_spawn_positions()
        
        # Update character positions
        self.player.x, self.player.y = player_pos
        self.enemy.x, self.enemy.y = enemy_pos
        
        # Regenerate obstacles
        self.obstacles = self._generate_obstacles(self.player, self.enemy)
        
        # Reset health for both players for the new round
        self.player.health = self.player.max_health
        self.enemy.health = self.enemy.max_health
        
        # If using an AI controller, update its knowledge of the map
        if hasattr(self, 'ai_controller'):
            self.ai_controller.update_environment(self.obstacles)
            
        # Center camera on player for the new map
        self.return_to_player()
            
        debug_print("Map regenerated for the next round!")

    def _generate_spawn_positions(self) -> tuple:
        """Generate random spawn positions for player and enemy."""
        # Start the player exactly at the center of the map
        player_x = const.GRID_WIDTH // 2
        player_y = const.GRID_HEIGHT // 2
        
        # Ensure player is in bounds (should always be true for center position)
        player_x = max(1, min(player_x, const.GRID_WIDTH - 2))
        player_y = max(1, min(player_y, const.GRID_HEIGHT - 2))
        
        # Calculate optimal distance range for enemy to be visible on screen
        min_distance = 6  # Minimum Manhattan distance between player and enemy
        max_distance = 10  # Maximum Manhattan distance to keep enemy on screen
        
        # Determine the viewport size in grid units
        viewport_width = const.SCREEN_WIDTH // const.GRID_SIZE
        viewport_height = const.SCREEN_HEIGHT // const.GRID_SIZE
        
        # Try to position enemy within visible range of player
        for _ in range(10):  # Try up to 10 times to find a good position
            # Generate random direction vector
            direction_x = random.choice([-1, 1])
            direction_y = random.choice([-1, 1])
            
            # Generate enemy position within the desired distance range
            distance = random.randint(min_distance, min(max_distance, viewport_width // 2))
            
            # Distribute the distance between x and y components
            distance_x = random.randint(2, distance - 2)
            distance_y = distance - distance_x
            
            enemy_x = player_x + (distance_x * direction_x)
            enemy_y = player_y + (distance_y * direction_y)
            
            # Ensure enemy is in bounds
            if (0 < enemy_x < const.GRID_WIDTH - 1 and 
                0 < enemy_y < const.GRID_HEIGHT - 1):
                
                # Additional check: make sure enemy is within visible area
                if (abs(player_x - enemy_x) <= viewport_width // 2 and
                    abs(player_y - enemy_y) <= viewport_height // 2):
                    return (player_x, player_y), (enemy_x, enemy_y)
        
        # Fallback if no optimal position found after attempts
        # Place enemy at a fixed offset from player
        enemy_x = min(max(1, player_x + 8), const.GRID_WIDTH - 2)
        enemy_y = min(max(1, player_y + 5), const.GRID_HEIGHT - 2)
        return (player_x, player_y), (enemy_x, enemy_y)

    def _generate_obstacles(self, player, enemy):
        """Generate obstacles for the map."""
        obstacles = []
        
        # Ensure map is fully generated with varied obstacle patterns
        # Use different obstacle generation strategies
        
        # 1. Create some random scattered obstacles
        num_scattered_obstacles = random.randint(20, 30)
        for _ in range(num_scattered_obstacles):
            obstacle_width = random.randint(1, 3)
            obstacle_height = random.randint(1, 2)
            
            # Try to find a valid position
            for attempt in range(100):  # Limit attempts to avoid infinite loop
                ox = random.randint(0, const.GRID_WIDTH - obstacle_width - 1)
                oy = random.randint(0, const.GRID_HEIGHT - obstacle_height - 1)
                
                # Check if this position would overlap with player or enemy
                if (abs(ox - player.x) < 5 and abs(oy - player.y) < 5) or \
                   (abs(ox - enemy.x) < 5 and abs(oy - enemy.y) < 5):
                    continue
                
                # Create obstacle rectangle
                obstacle = pygame.Rect(ox, oy, obstacle_width, obstacle_height)
                obstacles.append(obstacle)
                break
        
        # 2. Create some wall-like structures (horizontal and vertical)
        num_walls = random.randint(8, 12)
        for _ in range(num_walls):
            is_horizontal = random.choice([True, False])
            
            if is_horizontal:
                wall_length = random.randint(4, 10)
                wall_height = 1
                wx = random.randint(0, const.GRID_WIDTH - wall_length)
                wy = random.randint(0, const.GRID_HEIGHT - 2)
            else:
                wall_length = random.randint(4, 8)
                wall_width = 1
                wx = random.randint(0, const.GRID_WIDTH - 2)
                wy = random.randint(0, const.GRID_HEIGHT - wall_length)
            
            # Check if position is valid (not too close to players)
            if (abs(wx - player.x) < 3 and abs(wy - player.y) < 3) or \
               (abs(wx - enemy.x) < 3 and abs(wy - enemy.y) < 3):
                continue
                
            if is_horizontal:
                obstacle = pygame.Rect(wx, wy, wall_length, wall_height)
            else:
                obstacle = pygame.Rect(wx, wy, wall_width, wall_length)
            
            obstacles.append(obstacle)
        
        # 3. Create some L-shaped obstacles
        num_l_shapes = random.randint(5, 8)
        for _ in range(num_l_shapes):
            lx = random.randint(0, const.GRID_WIDTH - 4)
            ly = random.randint(0, const.GRID_HEIGHT - 4)
            
            # Check if position is valid
            if (abs(lx - player.x) < 5 and abs(ly - player.y) < 5) or \
               (abs(lx - enemy.x) < 5 and abs(ly - enemy.y) < 5):
                continue
            
            # Create L shape (horizontal part)
            h_width = random.randint(2, 3)
            obstacles.append(pygame.Rect(lx, ly, h_width, 1))
            
            # Add vertical part
            obstacles.append(pygame.Rect(lx, ly, 1, random.randint(2, 3)))
        
        # 4. Create some room-like structures
        num_rooms = random.randint(3, 5)
        for _ in range(num_rooms):
            room_width = random.randint(4, 7)
            room_height = random.randint(4, 7)
            rx = random.randint(0, const.GRID_WIDTH - room_width - 1)
            ry = random.randint(0, const.GRID_HEIGHT - room_height - 1)
            
            # Check if position is valid
            if (abs(rx - player.x) < 7 and abs(ry - player.y) < 7) or \
               (abs(rx - enemy.x) < 7 and abs(ry - enemy.y) < 7):
                continue
            
            # Create room walls (top, bottom, left, right)
            obstacles.append(pygame.Rect(rx, ry, room_width, 1))  # Top wall
            obstacles.append(pygame.Rect(rx, ry + room_height, room_width, 1))  # Bottom wall
            obstacles.append(pygame.Rect(rx, ry, 1, room_height + 1))  # Left wall
            obstacles.append(pygame.Rect(rx + room_width, ry, 1, room_height + 1))  # Right wall
            
            # Add a door (gap) in one of the walls
            door_side = random.choice(["top", "bottom", "left", "right"])
            if door_side == "top":
                door_pos = random.randint(rx + 1, rx + room_width - 2)
                # Remove part of the top wall for the door
                for obs in list(obstacles):
                    if isinstance(obs, pygame.Rect) and obs.x == door_pos and obs.y == ry and obs.width == 1 and obs.height == 1:
                        obstacles.remove(obs)
                        break
            elif door_side == "bottom":
                door_pos = random.randint(rx + 1, rx + room_width - 2)
                # Remove part of the bottom wall for the door
                for obs in list(obstacles):
                    if isinstance(obs, pygame.Rect) and obs.x == door_pos and obs.y == ry + room_height and obs.width == 1 and obs.height == 1:
                        obstacles.remove(obs)
                        break
            elif door_side == "left":
                door_pos = random.randint(ry + 1, ry + room_height - 1)
                # Remove part of the left wall for the door
                for obs in list(obstacles):
                    if isinstance(obs, pygame.Rect) and obs.x == rx and obs.y == door_pos and obs.width == 1 and obs.height == 1:
                        obstacles.remove(obs)
                        break
            else:  # right
                door_pos = random.randint(ry + 1, ry + room_height - 1)
                # Remove part of the right wall for the door
                for obs in list(obstacles):
                    if isinstance(obs, pygame.Rect) and obs.x == rx + room_width and obs.y == door_pos and obs.width == 1 and obs.height == 1:
                        obstacles.remove(obs)
                        break
        
        return obstacles

    def _generate_protective_block(self, char_x: int, char_y: int) -> list:
        """Generate a protective block formation around a character."""
        block_positions = []
        
        # Determine which side to protect (randomize orientation)
        orientation = random.choice(['left', 'right', 'up', 'down'])
        
        if orientation == 'left':
            # Block to the left
            if char_x > 0:
                block_positions.append((char_x - 1, char_y))
            if char_x > 0 and char_y > 0:
                block_positions.append((char_x - 1, char_y - 1))
            if char_x > 0 and char_y < const.GRID_HEIGHT - 1:
                block_positions.append((char_x - 1, char_y + 1))
        elif orientation == 'right':
            # Block to the right
            if char_x < const.GRID_WIDTH - 1:
                block_positions.append((char_x + 1, char_y))
            if char_x < const.GRID_WIDTH - 1 and char_y > 0:
                block_positions.append((char_x + 1, char_y - 1))
            if char_x < const.GRID_WIDTH - 1 and char_y < const.GRID_HEIGHT - 1:
                block_positions.append((char_x + 1, char_y + 1))
        elif orientation == 'up':
            # Block above
            if char_y > 0:
                block_positions.append((char_x, char_y - 1))
            if char_x > 0 and char_y > 0:
                block_positions.append((char_x - 1, char_y - 1))
            if char_x < const.GRID_WIDTH - 1 and char_y > 0:
                block_positions.append((char_x + 1, char_y - 1))
        else:  # orientation == 'down'
            # Block below
            if char_y < const.GRID_HEIGHT - 1:
                block_positions.append((char_x, char_y + 1))
            if char_x > 0 and char_y < const.GRID_HEIGHT - 1:
                block_positions.append((char_x - 1, char_y + 1))
            if char_x < const.GRID_WIDTH - 1 and char_y < const.GRID_HEIGHT - 1:
                block_positions.append((char_x + 1, char_y + 1))
                
        return block_positions

    def return_to_player(self):
        """Center the camera on the player character."""
        if self.player:
            # Center the camera on the player with proper grid positioning
            self.camera_x = self.player.x * const.GRID_SIZE - (const.SCREEN_WIDTH // 2) + (const.GRID_SIZE // 2)
            self.camera_y = self.player.y * const.GRID_SIZE - (const.SCREEN_HEIGHT // 2) + (const.GRID_SIZE // 2)
            
            # Keep camera within map boundaries
            self.camera_x = max(0, min(self.camera_x, self.max_camera_x - const.SCREEN_WIDTH))
            self.camera_y = max(0, min(self.camera_y, self.max_camera_y - const.SCREEN_HEIGHT))
            return True
        return False

    def _update_projectiles(self):
        """Update all projectiles in the game, handling movement and collisions."""
        # Process each projectile
        for projectile in list(self.projectiles):  # Create a copy of the list to safely remove items
            # Update projectile position
            projectile.x += projectile.dx
            projectile.y += projectile.dy
            
            # Convert to grid coordinates for collision detection
            grid_x = int(projectile.x)
            grid_y = int(projectile.y)
            
            # Check if projectile is out of bounds
            if (grid_x < 0 or grid_x >= const.GRID_WIDTH or 
                grid_y < 0 or grid_y >= const.GRID_HEIGHT):
                self.projectiles.remove(projectile)
                continue
                
            # Check collision with obstacles
            for obstacle in self.obstacles:
                if obstacle.collidepoint(grid_x, grid_y):
                    # Handle collision with obstacle
                    self.projectiles.remove(projectile)
                    break
                    
            # Check if projectile was already removed
            if projectile not in self.projectiles:
                continue
                
            # Check collision with player
            if (grid_x == self.player.x and grid_y == self.player.y and
                projectile.owner != self.player):
                self.player.health -= 1  # Decrease player health
                self.projectiles.remove(projectile)
                continue
                
            # Check collision with enemy
            if (grid_x == self.enemy.x and grid_y == self.enemy.y and
                projectile.owner != self.enemy):
                self.enemy.health -= 1  # Decrease enemy health
                self.projectiles.remove(projectile)

    def _is_game_over(self):
        """Check if the game is over based on player or enemy health."""
        # Game is over if either player or enemy has no health left
        if self.player.health <= 0 or self.enemy.health <= 0:
            # Record the winner
            if self.enemy.health <= 0:
                self.winner = "Player"
            else:
                self.winner = "Enemy"
            return True
        return False

    def _process_movement(self, grid_x, grid_y):
        """Process player movement to a new grid position."""
        # Check if the clicked position is valid for movement
        if not self._is_valid_move(grid_x, grid_y):
            return
            
        # Calculate distance to move
        distance = abs(self.player.x - grid_x) + abs(self.player.y - grid_y)
        
        # Check if player has enough courage points to move
        if distance > self.player.courage_points:
            # Display message or feedback that move is too far
            debug_print(f"Not enough courage points! Need {distance}, have {self.player.courage_points}.")
            return
            
        # Update player position
        self.player.x = grid_x
        self.player.y = grid_y
        
        # Reduce courage points by distance moved
        self.player.courage_points -= distance
        
        # Center camera on new position
        self.return_to_player()
        
        debug_print(f"Player moved to ({grid_x}, {grid_y}). Courage remaining: {self.player.courage_points}")

    def _is_valid_move(self, grid_x, grid_y):
        """Check if the move to the given grid position is valid."""
        # Check if position is within grid bounds
        if (grid_x < 0 or grid_x >= const.GRID_WIDTH or
            grid_y < 0 or grid_y >= const.GRID_HEIGHT):
            return False
            
        # Check if position is occupied by an obstacle
        for obstacle in self.obstacles:
            if obstacle.collidepoint(grid_x, grid_y):
                return False
                
        # Check if position is occupied by enemy
        if grid_x == self.enemy.x and grid_y == self.enemy.y:
            return False
            
        # Check if the move is within the allowed range based on courage points
        distance = abs(self.player.x - grid_x) + abs(self.player.y - grid_y)
        if distance > self.player.courage_points:
            # Move is valid but will be rejected in _process_movement due to courage points
            return True
            
        return True

    def _process_shooting(self, target_x, target_y):
        """Process player shooting action towards the target coordinates."""
        # Check if player has already shot this turn
        if not self.player_turn:
            debug_print("Not player's turn to shoot!")
            return False
            
        # Calculate direction vector from player to target
        dx = target_x - self.player.x
        dy = target_y - self.player.y
        
        # Normalize the vector to get a unit direction
        length = max(0.01, (dx**2 + dy**2)**0.5)
        dx /= length
        dy /= length
        
        # Create projectile
        projectile = Projectile(
            x=float(self.player.x) + 0.5,  # Start from center of player cell
            y=float(self.player.y) + 0.5,
            dx=dx * const.PROJECTILE_SPEED,
            dy=dy * const.PROJECTILE_SPEED,
            owner=self.player
        )
        
        # Add projectile to game
        self.projectiles.append(projectile)
        
        debug_print(f"Player shot at ({target_x}, {target_y})")
        
        # End player turn after shooting
        self._end_player_turn()
        
        return True

    def _end_player_turn(self):
        """End the player's turn and switch to AI turn."""
        self.player_turn = False
        
        # Reset player's courage points for next turn
        self.player.courage_points = self.player.max_courage
        
        debug_print("Player turn ended. Enemy turn starting.")

    def _process_ai_turn(self):
        """Handle AI turn processing with appropriate timing."""
        # Initialize AI turn if not started
        if not self.ai_turn_started:
            self.ai_turn_started = True
            self.ai_turn_time = pygame.time.get_ticks()
            debug_print("AI turn initialized")
            return
            
        # Add a small delay before AI makes moves (makes gameplay feel more natural)
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_turn_time < const.AI_TURN_DELAY:
            return
            
        # Perform AI actions
        self._perform_ai_actions()
        
        # End AI turn and switch back to player turn
        self._end_ai_turn()

    def _perform_ai_actions(self):
        """Implement the enemy's movement and shooting logic."""
        # If we have an AI controller, use it
        if hasattr(self, 'ai_controller'):
            self.ai_controller.process_turn()
            return
            
        # Simple AI logic if no controller exists:
        # 1. Try to move toward the player if not in line of sight
        # 2. Shoot if player is in line of sight
        
        # Check if enemy can see player
        can_shoot = self._can_enemy_shoot_player()
        
        if can_shoot:
            # Enemy can see player, shoot at them
            dx = self.player.x - self.enemy.x
            dy = self.player.y - self.enemy.y
            
            # Normalize direction vector
            length = max(0.01, (dx**2 + dy**2)**0.5)
            dx /= length
            dy /= length
            
            # Create projectile from enemy position
            projectile = Projectile(
                x=float(self.enemy.x) + 0.5,
                y=float(self.enemy.y) + 0.5,
                dx=dx * const.PROJECTILE_SPEED,
                dy=dy * const.PROJECTILE_SPEED,
                owner=self.enemy
            )
            
            # Add projectile to game
            self.projectiles.append(projectile)
            debug_print("Enemy shot at player")
            
        else:
            # Enemy can't see player, try to move toward them
            # Calculate direction toward player
            dx = 1 if self.player.x > self.enemy.x else -1 if self.player.x < self.enemy.x else 0
            dy = 1 if self.player.y > self.enemy.y else -1 if self.player.y < self.enemy.y else 0
            
            # Try to move in x direction first if possible
            if dx != 0:
                new_x = self.enemy.x + dx
                if self._is_valid_move_for_enemy(new_x, self.enemy.y):
                    self.enemy.x = new_x
                    self.enemy.courage_points -= 1
                    debug_print(f"Enemy moved to ({self.enemy.x}, {self.enemy.y})")
                    return
                    
            # Try to move in y direction if x movement wasn't possible
            if dy != 0:
                new_y = self.enemy.y + dy
                if self._is_valid_move_for_enemy(self.enemy.x, new_y):
                    self.enemy.y = new_y
                    self.enemy.courage_points -= 1
                    debug_print(f"Enemy moved to ({self.enemy.x}, {self.enemy.y})")
                    return
                    
            # If neither direction works, try diagonal movement
            if dx != 0 and dy != 0:
                new_x = self.enemy.x + dx
                new_y = self.enemy.y + dy
                if self._is_valid_move_for_enemy(new_x, new_y):
                    self.enemy.x = new_x
                    self.enemy.y = new_y
                    self.enemy.courage_points -= 2  # Diagonal movement costs 2 courage points
                    debug_print(f"Enemy moved diagonally to ({self.enemy.x}, {self.enemy.y})")
                    return
                    
            debug_print("Enemy couldn't find a valid move")
    
    def _is_valid_move_for_enemy(self, grid_x, grid_y):
        """Check if the move is valid for the enemy."""
        # Check if position is within grid bounds
        if (grid_x < 0 or grid_x >= const.GRID_WIDTH or
            grid_y < 0 or grid_y >= const.GRID_HEIGHT):
            return False
            
        # Check if position is occupied by an obstacle
        for obstacle in self.obstacles:
            if obstacle.collidepoint(grid_x, grid_y):
                return False
                
        # Check if position is occupied by player
        if grid_x == self.player.x and grid_y == self.player.y:
            return False
            
        # Check if the enemy has enough courage points to move
        distance = abs(self.enemy.x - grid_x) + abs(self.enemy.y - grid_y)
        if distance > self.enemy.courage_points:
            return False
            
        return True
        
    def _can_enemy_shoot_player(self):
        """Check if enemy has line of sight to shoot the player."""
        # Simple line-of-sight check between enemy and player
        # Get positions
        x0, y0 = self.enemy.x, self.enemy.y
        x1, y1 = self.player.x, self.player.y
        
        # Use Bresenham's line algorithm to check line of sight
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while x0 != x1 or y0 != y1:
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
                
            # If we hit an obstacle before reaching the player, no line of sight
            if (x0 == x1 and y0 == y1):  # We've reached the player
                return True
                
            # Check if current position has an obstacle
            for obstacle in self.obstacles:
                if obstacle.collidepoint(x0, y0):
                    return False
                    
        return True
        
    def _end_ai_turn(self):
        """End the AI's turn and switch back to player turn."""
        self.player_turn = True
        self.ai_turn_started = False
        
        # Reset enemy's courage points for next turn
        self.enemy.courage_points = self.enemy.max_courage
        
        debug_print("Enemy turn ended. Player turn starting.")
        
    def _game_loop(self) -> None:
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True
        show_debug = False
        
        # Center the camera on the player at game start
        self.return_to_player()
        
        # Make sure obstacle generation is complete before starting game
        if not self.obstacles:
            self.obstacles = self._generate_obstacles(self.player, self.enemy)
        
        while running:
            # Get delta time for animations
            delta_time = clock.tick(const.FPS)
            
            # Clear screen with background color
            self.virtual_screen.fill(const.BG_COLOR)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                # Handle escape key to cancel actions
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Cancel shooting mode if active
                        self.shooting_mode = False
                    
                    # Enter shooting mode with space
                    if event.key == pygame.K_SPACE and self.player_turn:
                        self.shooting_mode = True
                
                # Handle mouse events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Convert physical screen coordinates to virtual screen coordinates
                    virtual_mouse_pos = (
                        int(mouse_pos[0] / self.scale_x),
                        int(mouse_pos[1] / self.scale_y)
                    )
                    
                    # Check if click is in the playable area (not in HUD)
                    if virtual_mouse_pos[1] > 60 and virtual_mouse_pos[1] < const.SCREEN_HEIGHT - self.ui_renderer.bottom_bar_height:
                        # Handle shooting mode
                        if self.shooting_mode and self.player_turn:
                            # Convert virtual mouse position to game grid coordinates
                            grid_x = (virtual_mouse_pos[0] + self.camera_x) // const.GRID_SIZE
                            grid_y = (virtual_mouse_pos[1] + self.camera_y) // const.GRID_SIZE
                            
                            # Process shooting action
                            self._process_shooting(grid_x, grid_y)
                            self.shooting_mode = False
                        
                        # Handle movement
                        elif self.player_turn and not self.shooting_mode:
                            # Convert virtual mouse position to game grid coordinates
                            grid_x = (virtual_mouse_pos[0] + self.camera_x) // const.GRID_SIZE
                            grid_y = (virtual_mouse_pos[1] + self.camera_y) // const.GRID_SIZE
                            
                            # Process movement
                            self._process_movement(grid_x, grid_y)
                    
                    # Check for info button click
                    info_button_rect = self.ui_renderer.draw_info_button()
                    if info_button_rect.collidepoint(virtual_mouse_pos):
                        self.ui_renderer.toggle_info_panel()
                    
                    # Check for debug button click
                    debug_button_rect = self.ui_renderer.draw_debug_button()
                    if debug_button_rect.collidepoint(virtual_mouse_pos):
                        show_debug = not show_debug
                    
                    # Check for center view button click
                    center_view_button_rect = self.ui_renderer.draw_return_to_player_button()
                    if center_view_button_rect.collidepoint(virtual_mouse_pos):
                        self.return_to_player()
                    
                    # Check for leave match button click
                    leave_button_rect, _ = self.ui_renderer.draw_leave_match_button()
                    if leave_button_rect.collidepoint(virtual_mouse_pos):
                        # Go back to main menu
                        running = False
                        self.game_state = const.STATE_MENU
                        return
                    
                    # Check for end turn button click if it's player's turn
                    if self.player_turn:
                        end_turn_rect, end_turn_button = self.ui_renderer.draw_end_turn_button()
                        if end_turn_rect.collidepoint(virtual_mouse_pos):
                            self._end_player_turn()
                
                # Update button states for hover effects and animations
                end_turn_rect, end_turn_button = self.ui_renderer.draw_end_turn_button(should_blink=True)
                end_turn_button.handle_event(event)
                
                leave_button_rect, leave_button = self.ui_renderer.draw_leave_match_button()
                leave_button.handle_event(event)
            
            # Draw the game
            self.ui_renderer.draw_grid(self.camera_x, self.camera_y)
            self.ui_renderer.draw_obstacles(self.obstacles, self.camera_x, self.camera_y)
            
            # Draw valid movement positions if it's player's turn
            if self.player_turn and not self.shooting_mode:
                self.ui_renderer.draw_valid_moves(self.player, self.obstacles, self.camera_x, self.camera_y)
            
            # Draw projectiles
            self.ui_renderer.draw_projectiles(self.projectiles, self.camera_x, self.camera_y)
            
            # Draw characters
            self.ui_renderer.draw_character(
                self.player, 
                is_player=True, 
                is_turn=self.player_turn,
                camera_x=self.camera_x,
                camera_y=self.camera_y
            )
            
            self.ui_renderer.draw_character(
                self.enemy, 
                is_player=False, 
                is_turn=not self.player_turn,
                camera_x=self.camera_x,
                camera_y=self.camera_y
            )
            
            # Draw UI
            self.ui_renderer.draw_hud_grid(self.player, self.enemy)
            self.ui_renderer.draw_turn_indicator(self.player_turn)
            
            # Draw shooting arrow in shooting mode
            if self.shooting_mode and self.player_turn:
                mouse_pos = pygame.mouse.get_pos()
                self.ui_renderer.draw_shooting_arrow(
                    self.player.x, 
                    self.player.y, 
                    mouse_pos,
                    self.camera_x, 
                    self.camera_y
                )
            
            # Update and draw info panel if active
            self.ui_renderer.update_info_panel()
            if self.ui_renderer.info_panel_active:
                game_state_text = [
                    f"Player: {self.player.sniper_type.name}",
                    f"Health: {self.player.health}/{self.player.max_health}",
                    f"Courage: {self.player.courage_points}/{self.player.max_courage}",
                    "",
                    f"Enemy: {self.enemy.sniper_type.name}",
                    f"Health: {self.enemy.health}/{self.enemy.max_health}",
                    f"Courage: {self.enemy.courage_points}/{self.enemy.max_courage}",
                    "",
                    f"Turn: {'Player' if self.player_turn else 'Enemy'}",
                ]
                self.ui_renderer.draw_info_panel(game_state_text)
            
            # Draw buttons
            self.ui_renderer.draw_info_button()
            self.ui_renderer.draw_debug_button()
            self.ui_renderer.draw_return_to_player_button()
            self.ui_renderer.draw_leave_match_button()
            
            # Draw end turn button only during player turn
            if self.player_turn:
                self.ui_renderer.draw_end_turn_button(should_blink=True)
            
            # Draw instructions
            self.ui_renderer.draw_instructions()
            
            # Draw debug info if enabled
            if show_debug:
                ai_state = "Thinking" if not self.player_turn else "Inactive"
                self.ui_renderer.draw_debug_info(ai_state)
            
            # Scale the virtual screen to the actual screen size
            scaled_screen = pygame.transform.scale(
                self.virtual_screen, 
                (self.screen_width, self.screen_height)
            )
            self.screen.blit(scaled_screen, (0, 0))
            
            # Update display
            pygame.display.flip()
            
            # Update game state
            if not self.player_turn:
                # AI turn processing
                self._process_ai_turn()
            
            # Update projectiles
            self._update_projectiles()
            
            # Check for game over
            if self._is_game_over():
                running = False
                winner = "Player" if self.enemy.health <= 0 else "Enemy"
                self.ui_renderer.draw_game_over(winner)
                self.game_state = const.STATE_GAME_OVER
            
            # Update display
            pygame.display.flip()
            
        # End of game loop

    def run(self):
        """Start the game and enter the main game loop."""
        # Initialize the AI controller only if playing against AI
        if hasattr(self, 'game_mode') and self.game_mode == const.MODE_AI:
            from sniper.ai.ai_controller import AIController
            self.ai_controller = AIController(self)
        
        # Process game state and enter appropriate loop
        if self.game_state == const.STATE_MENU:
            self._menu_loop()
        else:
            # If somehow we start directly in game state, prepare the game
            if self.player is None or self.enemy is None:
                # Set default characters if they haven't been selected
                self.player = Character(self.sniper_types[0])
                self.enemy = Character(self.sniper_types[1])
                self.start_game()
                
            # Begin the game loop
            self._game_loop()
            
    def _menu_loop(self):
        """Handle the menu state of the game."""
        running = True
        
        # Load title image if available
        title_image = None
        try:
            title_image = load_image("title_characters.png")
            title_image = pygame.transform.scale(title_image, 
                                              (const.SCREEN_WIDTH - 100, 200))
        except Exception as e:
            debug_print(f"Failed to load title image: {e}")
        
        while running and self.game_state == const.STATE_MENU:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                        sys.exit()
                        
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Get the mouse position and scale it to match the virtual screen
                    screen_mouse_pos = pygame.mouse.get_pos()
                    virtual_mouse_pos = (
                        int(screen_mouse_pos[0] / self.scale_x),
                        int(screen_mouse_pos[1] / self.scale_y)
                    )
                    
                    debug_print(f"Mouse clicked at: {virtual_mouse_pos}")
                    debug_print(f"Start button rect: {self.ui.menu_start_button_rect}")
                    debug_print(f"Exit button rect: {self.ui.menu_exit_button_rect}")
                    
                    # Check if we clicked the start button
                    if self.ui.menu_start_button_rect and self.ui.menu_start_button_rect.collidepoint(virtual_mouse_pos):
                        debug_print("Start button clicked!")
                        self.game_state = const.STATE_SELECT
                        # Transition to character selection
                        self._character_selection_loop()
                        return
                        
                    # Check if we clicked the exit button    
                    if self.ui.menu_exit_button_rect and self.ui.menu_exit_button_rect.collidepoint(virtual_mouse_pos):
                        debug_print("Exit button clicked!")
                        running = False
                        pygame.quit()
                        sys.exit()
            
            # Clear screen
            self.virtual_screen.fill(const.BG_COLOR)
            
            # Draw title and menu options
            menu_buttons = self.ui.draw_menu(title_image)
            
            # Scale the virtual screen to the actual screen
            scaled_screen = pygame.transform.scale(
                self.virtual_screen, 
                (self.screen_width, self.screen_height)
            )
            self.screen.blit(scaled_screen, (0, 0))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(const.FPS)
            
    def _character_selection_loop(self):
        """Handle character selection screen."""
        running = True
        
        while running and self.game_state == const.STATE_SELECT:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Go back to main menu on escape
                        self.game_state = const.STATE_MENU
                        return
                        
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Get the mouse position and scale it for virtual screen
                    mouse_pos = pygame.mouse.get_pos()
                    virtual_mouse_pos = (
                        int(mouse_pos[0] / self.scale_x),
                        int(mouse_pos[1] / self.scale_y)
                    )
                    
                    # Handle clicks on character options
                    selected = self.ui.handle_character_select_click(
                        virtual_mouse_pos, 
                        self.sniper_types,
                        self.character_select_stage
                    )
                    
                    if selected is not None:
                        self.selected_candidate = selected
                        debug_print(f"Selected character: {selected.name}")
                    
                    # Check for confirm button click
                    if self.selected_candidate and self.ui.confirm_button_rect and self.ui.confirm_button_rect.collidepoint(virtual_mouse_pos):
                        debug_print(f"Confirm button clicked for: {self.selected_candidate.name}")
                        if self.character_select_stage == "player":
                            # Create player character with initial position (center of the grid)
                            player_x = const.GRID_WIDTH // 4
                            player_y = const.GRID_HEIGHT // 2
                            self.player = Character(player_x, player_y, self.selected_candidate)
                            self.character_select_stage = "enemy"
                            self.selected_candidate = None
                        else:
                            # Create enemy character with initial position
                            enemy_x = const.GRID_WIDTH - (const.GRID_WIDTH // 4)
                            enemy_y = const.GRID_HEIGHT // 2
                            self.enemy = Character(enemy_x, enemy_y, self.selected_candidate)
                            self.game_state = const.STATE_PLAY
                            self.start_game()
                            # Start the game loop
                            self._game_loop()
                            return
                    
                    # Check for back button
                    if self.ui.back_button_rect and self.ui.back_button_rect.collidepoint(virtual_mouse_pos):
                        debug_print("Back button clicked")
                        if self.character_select_stage == "enemy":
                            # Go back to player selection
                            self.character_select_stage = "player"
                            self.player = None
                            self.selected_candidate = None
                        else:
                            # Go back to main menu
                            self.game_state = const.STATE_MENU
                            return
            
            # Clear screen
            self.virtual_screen.fill(const.BG_COLOR)
            
            # Draw character selection screen
            self.ui.draw_character_select(
                self.character_select_stage,
                self.selected_candidate,
                self.sniper_types
            )
            
            # Scale the virtual screen to the actual screen
            scaled_screen = pygame.transform.scale(
                self.virtual_screen, 
                (self.screen_width, self.screen_height)
            )
            self.screen.blit(scaled_screen, (0, 0))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(const.FPS)

def main():
    """Main entry point function."""
    try:
        # Initialize and run the game
        game = GameManager()
        game.run()
    except Exception as e:
        debug_print(f"Fatal error: {e}")
        import traceback
        debug_print(traceback.format_exc())
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()