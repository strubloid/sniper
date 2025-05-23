"""
Scenario Objects module for the Sniper Game.

This module contains classes for scenario objects like asteroids/obstacles
with health states and animation capabilities.
"""
import time
import pygame
from typing import Tuple, Optional

from sniper.config.constants import const, debug_print

class Block:
    """
    Class representing an asteroid/obstacle in the game scenario with health
    and animation capabilities.
    """
    
    def __init__(self, x: int, y: int):
        """Initialize an asteroid with position and full health."""
        self.x = x
        self.y = y
        self.health = const.BLOCK_MAX_HEALTH
        
        # Animation properties
        self.is_fading = False
        self.is_appearing = False
        self.animation_start_time = 0
        self.alpha = 255  # Full opacity
        
        # Random rotation for asteroid appearance
        import random
        self.rotation = random.randint(0, 360)
        # Random size variation (0.7 to 1.0 of grid size)
        self.size_factor = 0.7 + random.random() * 0.3
    
    @property
    def position(self) -> Tuple[int, int]:
        """Get the grid position as a tuple."""
        return (self.x, self.y)
    
    @property
    def is_destroyed(self) -> bool:
        """Check if the asteroid is destroyed (health <= 0)."""
        return self.health <= 0
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the color based on the asteroid's health."""
        if self.health >= const.BLOCK_MAX_HEALTH:
            return const.ASTEROID_HEALTHY
        elif self.health == 2:
            return const.ASTEROID_DAMAGED
        else:
            return const.ASTEROID_CRITICAL
    
    def take_damage(self, damage: int = 1) -> bool:
        """
        Apply damage to the asteroid and return True if the asteroid is destroyed.
        """
        self.health -= damage
        debug_print(f"Asteroid at {self.position} took damage. Health: {self.health}")
        return self.is_destroyed
    
    def start_fade_out(self):
        """Start the fade out animation."""
        self.is_fading = True
        self.is_appearing = False
        self.animation_start_time = time.time() * 1000  # Current time in ms
        debug_print(f"Asteroid at {self.position} starting fade out")
    
    def start_fade_in(self):
        """Start the fade in animation."""
        self.is_appearing = True
        self.is_fading = False
        self.animation_start_time = time.time() * 1000  # Current time in ms
        self.alpha = 0  # Start completely transparent
        debug_print(f"Asteroid at {self.position} starting fade in")
    
    def update_animation(self) -> bool:
        """
        Update the animation state and return True if the animation is complete.
        """
        if not (self.is_fading or self.is_appearing):
            return True
        
        current_time = time.time() * 1000
        
        if self.is_fading:
            # Calculate alpha based on elapsed time
            progress = min(1.0, (current_time - self.animation_start_time) / const.BLOCK_FADE_DURATION)
            self.alpha = int(255 * (1.0 - progress))
            
            # Check if fade out is complete
            if progress >= 1.0:
                self.is_fading = False
                self.alpha = 0
                return True
        
        elif self.is_appearing:
            # Calculate alpha based on elapsed time
            progress = min(1.0, (current_time - self.animation_start_time) / const.BLOCK_APPEAR_DURATION)
            self.alpha = int(255 * progress)
            
            # Check if fade in is complete
            if progress >= 1.0:
                self.is_appearing = False
                self.alpha = 255
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the asteroid on the surface with appropriate health state and animation."""
        # Create a transparent surface for animation
        size = int(const.GRID_SIZE * self.size_factor)
        asteroid_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Get base color based on health
        base_color = self.color
        
        # Apply alpha for animations
        color_with_alpha = (*base_color, self.alpha)
        
        # Draw the asteroid with irregular shape instead of a rectangle
        center = (size // 2, size // 2)
        radius = size // 2 - 2
        
        # Draw main asteroid body (circle)
        pygame.draw.circle(asteroid_surface, color_with_alpha, center, radius)
        
        # Add some crater details
        if self.health == const.BLOCK_MAX_HEALTH:
            # Healthy asteroid - just a few small craters
            crater_color = (max(0, base_color[0] - 20), 
                           max(0, base_color[1] - 20), 
                           max(0, base_color[2] - 20), 
                           self.alpha)
            
            # Add 2-3 small craters with 50% opacity
            import random
            for _ in range(random.randint(2, 3)):
                crater_pos = (
                    center[0] + random.randint(-radius//2, radius//2),
                    center[1] + random.randint(-radius//2, radius//2)
                )
                crater_size = random.randint(2, 5)
                pygame.draw.circle(asteroid_surface, crater_color, crater_pos, crater_size)
        
        # Add visual indicators for damaged state
        elif self.health < const.BLOCK_MAX_HEALTH and self.health > 0:
            # Darker crater color for more contrast
            crater_color = (max(0, base_color[0] - 30), 
                           max(0, base_color[1] - 30), 
                           max(0, base_color[2] - 30), 
                           self.alpha)
            
            if self.health == 2:  # Damaged - one big crack
                pygame.draw.line(asteroid_surface, crater_color, 
                                (center[0] - radius//2, center[1] - radius//2), 
                                (center[0] + radius//2, center[1] + radius//2), 
                                3)
            elif self.health == 1:  # Critical - two big cracks
                pygame.draw.line(asteroid_surface, crater_color, 
                                (center[0] - radius//2, center[1] - radius//2), 
                                (center[0] + radius//2, center[1] + radius//2), 
                                3)
                pygame.draw.line(asteroid_surface, crater_color, 
                                (center[0] + radius//2, center[1] - radius//2), 
                                (center[0] - radius//2, center[1] + radius//2), 
                                3)
        
        # Calculate position to center the asteroid in the grid cell
        x = self.x * const.GRID_SIZE + (const.GRID_SIZE - size) // 2
        y = self.y * const.GRID_SIZE + (const.GRID_SIZE - size) // 2
        
        # Blit the asteroid surface onto the main surface
        surface.blit(asteroid_surface, (x, y))


class ScenarioManager:
    """
    Manages scenario objects and their population in the game stage.
    """
    def __init__(self, population: int = const.SCENARIO_POPULATION):
        """Initialize with the given population size."""
        self.population = population
        self.blocks = []
        # Bush blocks are special obstacles placed by players or AI
        # Each block may have attributes: is_bush (bool) and owner ('player'/'enemy')
        for block in self.blocks:
            setattr(block, 'is_bush', False)
            setattr(block, 'owner', None)
        self.round_transition_active = False
        self.transition_start_time = 0
        self.fade_phase_complete = False
        
        # Load tree image
        try:
            self.tree_image = pygame.image.load("assets/tree.png").convert_alpha()
            # Scale it to fit in a grid cell with slight overflow
            scale_size = int(const.GRID_SIZE * 1.1)  # 110% of grid size for slight overflow
            self.tree_image = pygame.transform.scale(self.tree_image, (scale_size, scale_size))
            self.tree_loaded = True
        except (pygame.error, FileNotFoundError):
            print("Warning: Could not load tree.png, trying tree_no_bg.png")
            try:
                self.tree_image = pygame.image.load("assets/tree_no_bg.png").convert_alpha()
                # Scale it to fit in a grid cell with slight overflow
                scale_size = int(const.GRID_SIZE * 1.1)  # 110% of grid size for slight overflow
                self.tree_image = pygame.transform.scale(self.tree_image, (scale_size, scale_size))
                self.tree_loaded = True
            except (pygame.error, FileNotFoundError):
                print("Warning: Could not load tree images, using fallback.")
                self.tree_loaded = False
    
    def add_bush(self, x: int, y: int, owner: str) -> bool:
        """
        Place a bush at the given coordinates for the specified owner ('player' or 'enemy').
        Returns True if placed successfully.
        """
        # Don't place if occupied
        if any(block.position == (x, y) for block in self.blocks):
            return False
        bush = Block(x, y)
        bush.is_bush = True
        bush.owner = owner
        self.blocks.append(bush)
        debug_print(f"Bush placed at {(x, y)} for {owner}")
        return True
    
    @property
    def obstacles(self) -> list:
        """
        Return list of block positions for collision detection.
        Only includes blocks that aren't destroyed.
        """
        return [block.position for block in self.blocks if not block.is_destroyed]
    
    def get_obstacles(self) -> list:
        """Get the list of current obstacle positions for pathfinding/collision."""
        return self.obstacles
        
    def is_obstacle(self, x: int, y: int) -> bool:
        """Check if there is an obstacle at the given position."""
        pos = (int(x), int(y))
        return pos in self.obstacles
    
    def generate_scenario(self, player_pos: Tuple[int, int], enemy_pos: Tuple[int, int]) -> None:
        """Generate a new scenario with blocks at random positions."""
        import random
        self.blocks = []
        
        # Add blocks up to the population size
        attempts = 0
        while len(self.blocks) < self.population and attempts < self.population * 3:
            attempts += 1
            x = random.randint(0, const.GRID_WIDTH - 1)
            y = random.randint(0, const.GRID_HEIGHT - 1)
            
            # Don't place blocks on players or existing blocks
            if ((x, y) == player_pos or (x, y) == enemy_pos or 
                any(block.position == (x, y) for block in self.blocks)):
                continue
                
            # Create a new block and add it to the list
            block = Block(x, y)
            block.start_fade_in()  # Start with fade-in animation
            self.blocks.append(block)
    
    def handle_projectile_collision(self, x: int, y: int, projectile=None) -> bool:
        """
        Handle a projectile collision with a block at the given position.
        Returns True if a collision occurred, False otherwise.
        
        Args:
            x: X position to check
            y: Y position to check
            projectile: Optional projectile object that includes owner information
        """
        for block in self.blocks:
            if block.position == (int(x), int(y)) and not block.is_destroyed:
                # Check if this is a player-owned bush and the shooter is also the player
                # If so, allow the shot to pass through
                if getattr(block, 'is_bush', False) and getattr(block, 'owner', None) == 'player' and projectile and getattr(projectile.owner, 'is_player', False):
                    # Skip collision for player shots hitting player's own bushes
                    debug_print(f"Player shot passing through player's own bush at {block.position}")
                    return False
                
                # Otherwise, damage the block (whether it's a regular obstacle or an enemy bush)
                destroyed = block.take_damage(const.BLOCK_DAMAGE_PER_HIT)
                return True
        return False
    
    def start_round_transition(self) -> None:
        """Start the round transition animation."""
        self.round_transition_active = True
        self.transition_start_time = time.time() * 1000
        self.fade_phase_complete = False
        
        # Start fade out animation for all blocks
        for block in self.blocks:
            if not block.is_destroyed:
                block.start_fade_out()
        
        debug_print("Starting round transition - fade out phase")
    
    def update_round_transition(self, player_pos: Tuple[int, int], enemy_pos: Tuple[int, int]) -> bool:
        """
        Update the round transition animation.
        Returns True when the transition is complete.
        """
        if not self.round_transition_active:
            return True
        
        # Backup any existing bush blocks so they persist across rounds
        bush_blocks = [block for block in self.blocks if getattr(block, 'is_bush', False)]
         
        current_time = time.time() * 1000
        elapsed = current_time - self.transition_start_time
        
        # Log transition progress every second
        seconds_elapsed = int(elapsed / 1000)
        if not hasattr(self, '_last_log_time') or seconds_elapsed > self._last_log_time:
            self._last_log_time = seconds_elapsed
            print(f"[{seconds_elapsed}s] Round transition in progress - Phase: {'Fade-out' if not self.fade_phase_complete else 'Fade-in'}")
         
        # Phase 1: Wait for all blocks to fade out
        if not self.fade_phase_complete:
            # Check if any non-bush blocks are still fading
            non_bush_blocks = [b for b in self.blocks if not getattr(b, 'is_bush', False)]
            fading_blocks = [b for b in non_bush_blocks if b.is_fading]
            
            # Debug the fade-out progress more frequently
            if len(fading_blocks) > 0 and (elapsed % 500 < 20):  # Log approximately every 500ms
                debug_print(f"[{elapsed:.0f}ms] Waiting for {len(fading_blocks)} blocks to finish fading out")
            
            # Force fade-out completion after sufficient time has elapsed (reduced timeout)
            time_to_force = const.BLOCK_FADE_DURATION + 200  # Add a small buffer
            
            # Determine if fade phase is complete
            all_faded = len(fading_blocks) == 0
            force_complete = elapsed >= time_to_force
            
            if all_faded or force_complete:
                if force_complete:
                    print(f"[{elapsed:.0f}ms] Force completing fade-out phase due to timeout")
                    # Force any remaining blocks to complete fading
                    for block in self.blocks:
                        if block.is_fading:
                            block.is_fading = False
                            block.alpha = 0
                
                self.fade_phase_complete = True
                print(f"[{elapsed:.0f}ms] Fade-out phase complete, regenerating blocks")
                
                # IMPORTANT: Reset transition start time for the second phase
                # This ensures that the elapsed time calculation is accurate for the fade-in phase
                self.transition_start_time = current_time
                
                # Regenerate blocks with new positions
                import random
                
                # Keep track of which non-bush blocks are still alive
                healthy = [b for b in self.blocks if not b.is_destroyed and not getattr(b, 'is_bush', False)]
                destroyed = [b for b in self.blocks if b.is_destroyed and not getattr(b, 'is_bush', False)]
                # Reset block list to start fresh, re-add bush blocks
                self.blocks = list(bush_blocks)
                
                # Make sure positions are integers
                player_pos_int = (int(player_pos[0]), int(player_pos[1]))
                enemy_pos_int = (int(enemy_pos[0]), int(enemy_pos[1]))
                
                # Create buffer zones around characters to prevent blocks from being too close
                protected_positions = [
                    player_pos_int,
                    enemy_pos_int,
                    # Add adjacent positions to prevent rocks too close to characters
                    (player_pos_int[0] + 1, player_pos_int[1]),
                    (player_pos_int[0] - 1, player_pos_int[1]),
                    (player_pos_int[0], player_pos_int[1] + 1),
                    (player_pos_int[0], player_pos_int[1] - 1),
                    (enemy_pos_int[0] + 1, enemy_pos_int[1]),
                    (enemy_pos_int[0] - 1, enemy_pos_int[1]),
                    (enemy_pos_int[0], enemy_pos_int[1] + 1),
                    (enemy_pos_int[0], enemy_pos_int[1] - 1),
                ]
                
                print(f"Protected positions for block generation: {protected_positions}")
                
                # Re-add healthy non-bush blocks with new positions
                attempts = 0
                while len(self.blocks) < len(healthy) + len(bush_blocks) and attempts < len(healthy) * 5:
                    attempts += 1
                    x = random.randint(0, const.GRID_WIDTH - 1)
                    y = random.randint(0, const.GRID_HEIGHT - 1)
                    
                    # Don't place blocks on players, near players, or on existing blocks
                    if ((x, y) in protected_positions or
                        any(block.position == (x, y) for block in self.blocks)):
                        continue
                    
                    # Create a new block with same health as an old one
                    if healthy:
                        old_block = healthy.pop(0)
                        block = Block(x, y)
                        block.health = old_block.health
                        block.start_fade_in()
                        self.blocks.append(block)
                
                # Add destroyed non-bush blocks back at full health to maintain population
                while len(self.blocks) < self.population + len(bush_blocks) and attempts < self.population * 5:
                    attempts += 1
                    x = random.randint(0, const.GRID_WIDTH - 1)
                    y = random.randint(0, const.GRID_HEIGHT - 1)
                    
                    # Don't place blocks on players, near players, or on existing blocks
                    if ((x, y) in protected_positions or
                        any(block.position == (x, y) for block in self.blocks)):
                        continue
                    
                    # Create a new block
                    block = Block(x, y)
                    block.start_fade_in()
                    self.blocks.append(block)
                    
                debug_print(f"Regenerated {len(self.blocks) - len(bush_blocks)} blocks, starting fade in phase")
         
        # Phase 2: Wait for all blocks to fade in
        else:
            # Check if any non-bush blocks are still appearing
            non_bush_blocks = [b for b in self.blocks if not getattr(b, 'is_bush', False)]
            appearing_blocks = [b for b in non_bush_blocks if b.is_appearing]
            
            if appearing_blocks:
                debug_print(f"Waiting for {len(appearing_blocks)} blocks to finish fading in")
            
            # Check if enough time has passed since transition start
            elapsed = current_time - self.transition_start_time
            time_to_force = const.BLOCK_FADE_DURATION + const.ROUND_TRANSITION_DELAY + const.BLOCK_APPEAR_DURATION + 200
            
            # Determine if transition is complete
            all_appeared = len(appearing_blocks) == 0
            force_complete = elapsed >= time_to_force
             
            if all_appeared or force_complete:
                if force_complete:
                    debug_print("Force completing fade-in phase due to timeout")
                    # Force any remaining blocks to complete appearing
                    for block in self.blocks:
                        if block.is_appearing:
                            block.is_appearing = False
                            block.alpha = 255
                
                self.round_transition_active = False
                debug_print("Round transition complete")
                return True
         
        return False
    
    def update_animations(self) -> None:
        """Update all animation states for blocks without redrawing them."""
        for block in self.blocks:
            block.update_animation()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all blocks with their appropriate visual state."""
        for block in self.blocks:
            if getattr(block, 'is_bush', False):
                # Draw tree image for bushes if available, otherwise use the space-themed bush with glow effect
                x, y = block.position
                if hasattr(self, 'tree_loaded') and self.tree_loaded and self.tree_image:
                    # Calculate position to center the tree in the grid cell with slight overflow
                    tree_pos = (x * const.GRID_SIZE + (const.GRID_SIZE - self.tree_image.get_width()) // 2,
                                y * const.GRID_SIZE + (const.GRID_SIZE - self.tree_image.get_height()) // 2)
                    
                    # Add a slight glow effect based on owner with smaller margin
                    tint = (80, 200, 255) if block.owner == 'player' else (200, 100, 255)
                    
                    # Use the configurable margin
                    margin = const.BUSH_GLOW_MARGIN
                    glow_size = const.GRID_SIZE + (margin * 2)
                    glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                    
                    # Draw glow circles
                    center = (glow_size // 2, glow_size // 2)
                    for i in range(3, 0, -1):
                        glow_radius = const.GRID_SIZE // 2 + i
                        glow_color = (*tint, 30)
                        pygame.draw.circle(glow_surface, glow_color, center, glow_radius)
                    
                    # Draw the glow around the tree with the specified margin
                    glow_pos = (x * const.GRID_SIZE - margin, y * const.GRID_SIZE - margin)
                    surface.blit(glow_surface, glow_pos)
                    
                    # Draw the tree image
                    surface.blit(self.tree_image, tree_pos)
                    
                    # Display bush health if enabled
                    if const.BUSH_HEALTH_DISPLAY:
                        # Create font if we don't have one
                        if not hasattr(self, 'font'):
                            self.font = pygame.font.SysFont(None, 20)
                        
                        # Render health text
                        health_text = str(block.health)
                        text_color = (255, 255, 255)  # White text
                        health_surface = self.font.render(health_text, True, text_color)
                        
                        # Position the health text at the top center of the bush
                        text_pos = (
                            x * const.GRID_SIZE + (const.GRID_SIZE - health_surface.get_width()) // 2,
                            y * const.GRID_SIZE - 2  # Position slightly above the top of the bush
                        )
                        
                        # Draw a small dark background for better visibility
                        bg_rect = health_surface.get_rect()
                        bg_rect.topleft = text_pos
                        bg_rect = bg_rect.inflate(4, 2)  # Make the background slightly larger
                        bg_color = (0, 0, 0, 180)  # Semi-transparent black
                        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                        bg_surface.fill(bg_color)
                        surface.blit(bg_surface, bg_rect.topleft)
                        
                        # Draw the health text
                        surface.blit(health_surface, text_pos)
                else:
                    # Fallback to original circular bush
                    center = (x * const.GRID_SIZE + const.GRID_SIZE//2, y * const.GRID_SIZE + const.GRID_SIZE//2)
                    # Color tint based on owner
                    tint = (80, 200, 255) if block.owner == 'player' else (200, 100, 255)
                    # Outer glow layers
                    for i in range(3, 0, -1):
                        glow_radius = const.GRID_SIZE//2 - 2 + i*3
                        glow_color = (*tint, 30)
                        pygame.draw.circle(surface, glow_color, center, glow_radius)
                    # Solid core
                    pygame.draw.circle(surface, tint, center, const.GRID_SIZE//2 - 5)
                    
                    # Display bush health for fallback rendering too
                    if const.BUSH_HEALTH_DISPLAY:
                        if not hasattr(self, 'font'):
                            self.font = pygame.font.SysFont(None, 20)
                        health_text = str(block.health)
                        text_surface = self.font.render(health_text, True, (255, 255, 255))
                        text_pos = (
                            center[0] - text_surface.get_width() // 2,
                            y * const.GRID_SIZE - 2
                        )
                        surface.blit(text_surface, text_pos)
                continue
            # Skip destroyed blocks unless fading
            if block.is_destroyed and not block.is_fading:
                continue
            # Draw normal block
            block.draw(surface)