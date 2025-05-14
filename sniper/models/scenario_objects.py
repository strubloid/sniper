"""
Scenario Objects module for the Sniper Game.

This module contains classes for scenario objects like blocks/obstacles
with health states and animation capabilities.
"""
import time
import pygame
from typing import Tuple, Optional

from sniper.config.constants import const, debug_print

class Block:
    """
    Class representing a block/obstacle in the game scenario with health
    and animation capabilities.
    """
    
    def __init__(self, x: int, y: int):
        """Initialize a block with position and full health."""
        self.x = x
        self.y = y
        self.health = const.BLOCK_MAX_HEALTH
        
        # Animation properties
        self.is_fading = False
        self.is_appearing = False
        self.animation_start_time = 0
        self.alpha = 255  # Full opacity
    
    @property
    def position(self) -> Tuple[int, int]:
        """Get the grid position as a tuple."""
        return (self.x, self.y)
    
    @property
    def is_destroyed(self) -> bool:
        """Check if the block is destroyed (health <= 0)."""
        return self.health <= 0
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the color based on the block's health."""
        if self.health >= const.BLOCK_MAX_HEALTH:
            return const.BLOCK_HEALTHY
        elif self.health == 2:
            return const.BLOCK_DAMAGED
        else:
            return const.BLOCK_CRITICAL
    
    def take_damage(self, damage: int = 1) -> bool:
        """
        Apply damage to the block and return True if the block is destroyed.
        """
        self.health -= damage
        debug_print(f"Block at {self.position} took damage. Health: {self.health}")
        return self.is_destroyed
    
    def start_fade_out(self):
        """Start the fade out animation."""
        self.is_fading = True
        self.is_appearing = False
        self.animation_start_time = time.time() * 1000  # Current time in ms
        debug_print(f"Block at {self.position} starting fade out")
    
    def start_fade_in(self):
        """Start the fade in animation."""
        self.is_appearing = True
        self.is_fading = False
        self.animation_start_time = time.time() * 1000  # Current time in ms
        self.alpha = 0  # Start completely transparent
        debug_print(f"Block at {self.position} starting fade in")
    
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
        """Draw the block on the surface with appropriate health state and animation."""
        rect = pygame.Rect(
            self.x * const.GRID_SIZE,
            self.y * const.GRID_SIZE,
            const.GRID_SIZE,
            const.GRID_SIZE
        )
        
        # Create a transparent surface for animation
        block_surface = pygame.Surface((const.GRID_SIZE, const.GRID_SIZE), pygame.SRCALPHA)
        
        # Get base color based on health
        base_color = self.color
        
        # Apply alpha for animations
        color_with_alpha = (*base_color, self.alpha)
        
        # Draw the block with appropriate transparency
        pygame.draw.rect(block_surface, color_with_alpha, block_surface.get_rect())
        
        # Add visual indicators for damaged state
        if self.health < const.BLOCK_MAX_HEALTH and self.health > 0:
            # Add cracks or visual damage indicators
            crack_color = (30, 30, 30, self.alpha)
            
            if self.health == 2:  # Damaged - one crack
                pygame.draw.line(block_surface, crack_color, 
                                (5, 5), (const.GRID_SIZE - 5, const.GRID_SIZE - 5), 2)
            elif self.health == 1:  # Critical - two cracks
                pygame.draw.line(block_surface, crack_color, 
                                (5, 5), (const.GRID_SIZE - 5, const.GRID_SIZE - 5), 2)
                pygame.draw.line(block_surface, crack_color, 
                                (const.GRID_SIZE - 5, 5), (5, const.GRID_SIZE - 5), 2)
        
        # Blit the block surface onto the main surface
        surface.blit(block_surface, rect)


class ScenarioManager:
    """
    Manages scenario objects and their population in the game stage.
    """
    def __init__(self, population: int = const.SCENARIO_POPULATION):
        """Initialize with the given population size."""
        self.population = population
        self.blocks = []
        self.round_transition_active = False
        self.transition_start_time = 0
        self.fade_phase_complete = False
    
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
    
    def handle_projectile_collision(self, x: int, y: int) -> bool:
        """
        Handle a projectile collision with a block at the given position.
        Returns True if a collision occurred, False otherwise.
        """
        for block in self.blocks:
            if block.position == (int(x), int(y)) and not block.is_destroyed:
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
        
        current_time = time.time() * 1000
        
        # Phase 1: Wait for all blocks to fade out
        if not self.fade_phase_complete:
            all_faded = all(not block.is_fading for block in self.blocks)
            
            if all_faded:
                self.fade_phase_complete = True
                
                # Regenerate blocks with new positions
                import random
                
                # Keep track of which blocks are still "alive"
                healthy_blocks = [block for block in self.blocks if not block.is_destroyed]
                destroyed_blocks = [block for block in self.blocks if block.is_destroyed]
                
                # Reset block list
                self.blocks = []
                
                # Re-add healthy blocks with new positions
                attempts = 0
                while len(self.blocks) < len(healthy_blocks) and attempts < len(healthy_blocks) * 3:
                    attempts += 1
                    x = random.randint(0, const.GRID_WIDTH - 1)
                    y = random.randint(0, const.GRID_HEIGHT - 1)
                    
                    # Don't place blocks on players or existing blocks
                    if ((x, y) == player_pos or (x, y) == enemy_pos or 
                        any(block.position == (x, y) for block in self.blocks)):
                        continue
                    
                    # Create a new block with same health as an old one
                    if healthy_blocks:
                        old_block = healthy_blocks.pop(0)
                        block = Block(x, y)
                        block.health = old_block.health
                        block.start_fade_in()
                        self.blocks.append(block)
                
                # Add destroyed blocks back at full health to maintain population
                while len(self.blocks) < self.population and attempts < self.population * 3:
                    attempts += 1
                    x = random.randint(0, const.GRID_WIDTH - 1)
                    y = random.randint(0, const.GRID_HEIGHT - 1)
                    
                    # Don't place blocks on players or existing blocks
                    if ((x, y) == player_pos or (x, y) == enemy_pos or 
                        any(block.position == (x, y) for block in self.blocks)):
                        continue
                    
                    # Create a new block
                    block = Block(x, y)
                    block.start_fade_in()
                    self.blocks.append(block)
                
                debug_print(f"Regenerated {len(self.blocks)} blocks, starting fade in phase")
        
        # Phase 2: Wait for all blocks to fade in
        else:
            # Check if all blocks have completed their fade-in animation
            all_appeared = all(not block.is_appearing for block in self.blocks)
            
            # Check if enough time has passed since transition start
            elapsed = current_time - self.transition_start_time
            time_complete = elapsed >= (const.BLOCK_FADE_DURATION + const.ROUND_TRANSITION_DELAY + const.BLOCK_APPEAR_DURATION)
            
            if all_appeared and time_complete:
                self.round_transition_active = False
                debug_print("Round transition complete")
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all blocks with their appropriate visual state."""
        for block in self.blocks:
            # Skip drawing destroyed blocks unless they're fading out
            if block.is_destroyed and not block.is_fading:
                continue
                
            # Update animation state
            block.update_animation()
            
            # Draw the block
            block.draw(surface)