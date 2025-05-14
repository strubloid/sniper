"""
UI Rendering module for the Sniper Game.
"""
import pygame
import random
import math
from typing import List, Tuple, Dict, Any, Optional

from sniper.config.constants import const, debug_print
from sniper.models.characters import Character
from sniper.models.projectiles import Projectile
from sniper.models.ui_elements import Button

class UI:
    """Handles rendering of UI elements and game state visualization."""
    
    def __init__(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """Initialize UI renderer with a surface and fonts."""
        self.surface = surface
        self.fonts = fonts
        self.info_panel_active = False
        self.info_panel_position = -250  # Start off-screen
        self.info_panel_target = -250  # Default is hidden
        self.bottom_bar_height = 80  # Height of the bottom bar
        self.show_instructions = False  # Only show instructions when toggled
        
        # Initialize menu button rectangles
        self.menu_start_button_rect = None
        self.menu_exit_button_rect = None
        self.confirm_button_rect = None
        self.cancel_button_rect = None
        self.back_button_rect = None
        
    def draw_grid(self, camera_x=0, camera_y=0) -> None:
        """Draw a grid on the screen with camera offset."""
        # Draw the grid with an offset based on camera position
        for x in range(const.GRID_WIDTH + 1):
            adjusted_x = x * const.GRID_SIZE - camera_x
            if 0 <= adjusted_x < const.SCREEN_WIDTH:
                pygame.draw.line(
                    self.surface, 
                    const.GRID_COLOR, 
                    (adjusted_x, 0), 
                    (adjusted_x, const.SCREEN_HEIGHT - self.bottom_bar_height)
                )
        
        for y in range(const.GRID_HEIGHT + 1):
            adjusted_y = y * const.GRID_SIZE - camera_y
            if 0 <= adjusted_y < const.SCREEN_HEIGHT - self.bottom_bar_height:
                pygame.draw.line(
                    self.surface, 
                    const.GRID_COLOR, 
                    (0, adjusted_y), 
                    (const.SCREEN_WIDTH, adjusted_y)
                )

        # Draw the bottom black bar - this is not affected by camera
        pygame.draw.rect(
            self.surface, 
            const.BLACK, 
            pygame.Rect(0, const.SCREEN_HEIGHT - self.bottom_bar_height, const.SCREEN_WIDTH, self.bottom_bar_height)
        )
        # Add a border line at the top of the black bar
        pygame.draw.line(
            self.surface,
            const.GRAY,
            (0, const.SCREEN_HEIGHT - self.bottom_bar_height),
            (const.SCREEN_WIDTH, const.SCREEN_HEIGHT - self.bottom_bar_height),
            2
        )
    
    def draw_obstacles(self, obstacles: List[pygame.Rect], camera_x=0, camera_y=0) -> None:
        """Draw obstacles on the grid with camera offset."""
        for obstacle in obstacles:
            # Apply camera offset
            screen_x = obstacle.x * const.GRID_SIZE - camera_x
            screen_y = obstacle.y * const.GRID_SIZE - camera_y
            
            # Calculate width and height in screen pixels
            screen_width = obstacle.width * const.GRID_SIZE
            screen_height = obstacle.height * const.GRID_SIZE
            
            # Only draw if obstacle is within visible area
            if (0 <= screen_x < const.SCREEN_WIDTH and 
                0 <= screen_y < const.SCREEN_HEIGHT - self.bottom_bar_height):
                rect = pygame.Rect(
                    screen_x, 
                    screen_y, 
                    screen_width, 
                    screen_height
                )
                pygame.draw.rect(self.surface, const.OBSTACLE_COLOR, rect)
    
    def draw_projectiles(self, projectiles: List[Projectile], camera_x=0, camera_y=0) -> None:
        """Draw projectiles on the screen with camera offset."""
        for p in projectiles:
            # Apply camera offset
            screen_x = int(p.x * const.GRID_SIZE - camera_x)
            screen_y = int(p.y * const.GRID_SIZE - camera_y)
            
            # Only draw if projectile is within visible area
            if (0 <= screen_x < const.SCREEN_WIDTH and 
                0 <= screen_y < const.SCREEN_HEIGHT - self.bottom_bar_height):
                p_screen = Projectile(
                    x=screen_x + const.GRID_SIZE // 2,
                    y=screen_y + const.GRID_SIZE // 2,
                    radius=const.GRID_SIZE // 4,
                    color=p.color,
                    velocity_x=p.velocity_x,
                    velocity_y=p.velocity_y
                )
                self.draw_projectile(p_screen)
    
    def draw_projectile(self, projectile):
        """Draw a projectile with enhanced visual effects."""
        # Draw the projectile with a glowing effect
        base_color = projectile.color
        glow_color = [min(c + 100, 255) for c in base_color]
        
        # Draw outer glow
        glow_radius = projectile.radius + 3
        pygame.draw.circle(self.surface, glow_color, (int(projectile.x), int(projectile.y)), glow_radius, 0)
        
        # Draw inner core
        pygame.draw.circle(self.surface, base_color, (int(projectile.x), int(projectile.y)), projectile.radius, 0)
        
        # Add a highlight spot for more dimension
        highlight_pos = (int(projectile.x - projectile.radius * 0.3), int(projectile.y - projectile.radius * 0.3))
        highlight_radius = max(1, int(projectile.radius * 0.4))
        highlight_color = [min(c + 150, 255) for c in base_color]
        pygame.draw.circle(self.surface, highlight_color, highlight_pos, highlight_radius, 0)
        
        # Draw trail effect if projectile is moving fast enough
        if abs(projectile.velocity_x) > 5 or abs(projectile.velocity_y) > 5:
            trail_length = 5
            for i in range(1, trail_length + 1):
                trail_pos_x = int(projectile.x - (projectile.velocity_x * 0.1 * i))
                trail_pos_y = int(projectile.y - (projectile.velocity_y * 0.1 * i))
                trail_radius = int(projectile.radius * (1 - (i / (trail_length + 2))))
                trail_alpha = 255 - (i * 40)
                trail_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                trail_color = base_color + [trail_alpha]
                pygame.draw.circle(trail_surface, trail_color, (trail_radius, trail_radius), trail_radius)
                self.surface.blit(trail_surface, (trail_pos_x - trail_radius, trail_pos_y - trail_radius))
    
    def draw_hud(self, character):
        """Draw the HUD (heads-up display) for the character including improved CP box."""
        # Health bar
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = character.health / character.max_health
        health_color = (255, 0, 0)  # Red
        if health_percentage > 0.6:
            health_color = (0, 255, 0)  # Green
        elif health_percentage > 0.3:
            health_color = (255, 165, 0)  # Orange
        
        # Draw health bar background
        pygame.draw.rect(self.surface, (50, 50, 50), (20, 20, health_bar_width, health_bar_height))
        
        # Draw health bar fill
        pygame.draw.rect(self.surface, health_color, 
                        (20, 20, int(health_bar_width * health_percentage), health_bar_height))
        
        # Draw health bar border
        pygame.draw.rect(self.surface, (200, 200, 200), 
                        (20, 20, health_bar_width, health_bar_height), 2)
        
        # Draw health text
        health_text = f"HP: {int(character.health)}/{character.max_health}"
        health_font = pygame.font.SysFont('Arial', 16)
        health_surface = health_font.render(health_text, True, (255, 255, 255))
        self.surface.blit(health_surface, (25, 22))
        
        # Improved CP (Combat Points) box
        cp_box_width = 120
        cp_box_height = 40
        cp_box_x = 20
        cp_box_y = 50
        
        # Draw CP box with gradient background
        cp_gradient = pygame.Surface((cp_box_width, cp_box_height))
        for i in range(cp_box_height):
            gradient_color = (30, 30, 80 + i * 3)
            pygame.draw.line(cp_gradient, gradient_color, (0, i), (cp_box_width, i))
        self.surface.blit(cp_gradient, (cp_box_x, cp_box_y))
        
        # Draw CP box border
        pygame.draw.rect(self.surface, (100, 100, 255), 
                       (cp_box_x, cp_box_y, cp_box_width, cp_box_height), 2)
        
        # Draw CP text with shadow for better visibility
        cp_font = pygame.font.SysFont('Arial', 18, bold=True)
        cp_text = f"CP: {character.combat_points}"
        
        # Draw text shadow
        cp_shadow = cp_font.render(cp_text, True, (0, 0, 0))
        self.surface.blit(cp_shadow, (cp_box_x + 11, cp_box_y + 11))
        
        # Draw text
        cp_surface = cp_font.render(cp_text, True, (150, 150, 255))
        self.surface.blit(cp_surface, (cp_box_x + 10, cp_box_y + 10))
        
        # Draw ability cooldowns
        self.draw_cooldowns(character)
    
    def draw_hud_grid(self, player, enemy):
        """Draw the HUD grid at the top of the screen."""
        # Draw grid background
        grid_rect = pygame.Rect(0, 0, const.SCREEN_WIDTH, 60)
        pygame.draw.rect(self.surface, (40, 40, 60), grid_rect)
        pygame.draw.line(self.surface, (80, 80, 100), (0, 60), (const.SCREEN_WIDTH, 60), 2)
        
        # Draw player health and courage points
        player_health_text = f"HP: {player.health}/{player.max_health}"
        player_health_surface = self.fonts['normal'].render(player_health_text, True, (255, 255, 255))
        self.surface.blit(player_health_surface, (20, 15))
        
        # Improved CP box with proper sizing and better visuals
        cp_box_width = 130  # Increased width to fit text better
        cp_box_height = 30
        cp_box_x = 20
        cp_box_y = 35
        cp_rect = pygame.Rect(cp_box_x, cp_box_y, cp_box_width, cp_box_height)
        
        # Draw CP box with gradient background
        cp_color = (80, 100, 180)
        pygame.draw.rect(self.surface, cp_color, cp_rect)
        pygame.draw.rect(self.surface, (50, 70, 150), cp_rect, 2)  # Border
        
        # Draw CP text with proper centering
        cp_text = f"CP: {player.courage_points}/{player.max_courage}"
        cp_surface = self.fonts['normal'].render(cp_text, True, (255, 255, 255))
        cp_text_rect = cp_surface.get_rect(midleft=(cp_box_x + 10, cp_box_y + cp_box_height // 2))
        self.surface.blit(cp_surface, cp_text_rect)
        
        # Draw enemy health
        enemy_health_text = f"Enemy HP: {enemy.health}/{enemy.max_health}"
        enemy_health_surface = self.fonts['normal'].render(enemy_health_text, True, (255, 255, 255))
        enemy_health_rect = enemy_health_surface.get_rect(topright=(const.SCREEN_WIDTH - 20, 15))
        self.surface.blit(enemy_health_surface, enemy_health_rect)
        
        # Draw enemy CP with improved styling to match player CP
        enemy_cp_box_width = 130
        enemy_cp_box_height = 30
        enemy_cp_box_x = const.SCREEN_WIDTH - enemy_cp_box_width - 20
        enemy_cp_box_y = 35
        enemy_cp_rect = pygame.Rect(enemy_cp_box_x, enemy_cp_box_y, enemy_cp_box_width, enemy_cp_box_height)
        
        enemy_cp_color = (180, 80, 80)  # Red for enemy
        pygame.draw.rect(self.surface, enemy_cp_color, enemy_cp_rect)
        pygame.draw.rect(self.surface, (150, 50, 50), enemy_cp_rect, 2)  # Border
        
        enemy_cp_text = f"CP: {enemy.courage_points}/{enemy.max_courage}"
        enemy_cp_surface = self.fonts['normal'].render(enemy_cp_text, True, (255, 255, 255))
        enemy_cp_text_rect = enemy_cp_surface.get_rect(midright=(enemy_cp_box_x + enemy_cp_box_width - 10, enemy_cp_box_y + enemy_cp_box_height // 2))
        self.surface.blit(enemy_cp_surface, enemy_cp_text_rect)
    
    def draw_turn_indicator(self, player_turn: bool) -> None:
        """Draw an indicator showing whose turn it is."""
        text = "Player's Turn" if player_turn else "Enemy's Turn"
        color = const.GREEN if player_turn else const.RED
        
        text_surf = self.fonts['normal'].render(text, True, color)
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.HUD_SPACING + 20))
        self.surface.blit(text_surf, text_rect)
    
    def draw_shooting_arrow(self, player_x, player_y, mouse_pos, camera_x=0, camera_y=0) -> None:
        """Draw an arrow indicating shooting direction with camera offset."""
        # Apply camera offset to player position
        player_screen_x = player_x * const.GRID_SIZE - camera_x + const.GRID_SIZE // 2
        player_screen_y = player_y * const.GRID_SIZE - camera_y + const.GRID_SIZE // 2
        
        # Calculate direction vector from player to mouse
        dx = mouse_pos[0] - player_screen_x
        dy = mouse_pos[1] - player_screen_y
        
        # Normalize the vector
        length = max(0.001, (dx**2 + dy**2)**0.5)  # Avoid division by zero
        dx = dx / length
        dy = dy / length
        
        # Determine the main direction
        if abs(dx) > abs(dy):
            dy = 0
            dx = 1 if dx > 0 else -1
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
            
        # Calculate end point of the arrow
        end_x = player_screen_x + dx * const.GRID_SIZE * 3
        end_y = player_screen_y + dy * const.GRID_SIZE * 3
        
        # Draw the arrow
        pygame.draw.line(
            self.surface, 
            const.ARROW_COLOR, 
            (player_screen_x, player_screen_y), 
            (end_x, end_y), 
            3
        )
        
        # Draw arrowhead
        arrowhead_length = const.GRID_SIZE // 2
        if dx == 1:  # Right
            pygame.draw.polygon(self.surface, const.ARROW_COLOR, [
                (end_x, end_y),
                (end_x - arrowhead_length, end_y - arrowhead_length // 2),
                (end_x - arrowhead_length, end_y + arrowhead_length // 2)
            ])
        elif dx == -1:  # Left
            pygame.draw.polygon(self.surface, const.ARROW_COLOR, [
                (end_x, end_y),
                (end_x + arrowhead_length, end_y - arrowhead_length // 2),
                (end_x + arrowhead_length, end_y + arrowhead_length // 2)
            ])
        elif dy == 1:  # Down
            pygame.draw.polygon(self.surface, const.ARROW_COLOR, [
                (end_x, end_y),
                (end_x - arrowhead_length // 2, end_y - arrowhead_length),
                (end_x + arrowhead_length // 2, end_y - arrowhead_length)
            ])
        elif dy == -1:  # Up
            pygame.draw.polygon(self.surface, const.ARROW_COLOR, [
                (end_x, end_y),
                (end_x - arrowhead_length // 2, end_y + arrowhead_length),
                (end_x + arrowhead_length // 2, end_y + arrowhead_length)
            ])
    
    def toggle_info_panel(self, active: bool = None) -> None:
        """Toggle or set the info panel visibility."""
        if active is None:
            self.info_panel_active = not self.info_panel_active
        else:
            self.info_panel_active = active
            
        # Set target position based on visibility
        self.info_panel_target = 0 if self.info_panel_active else -250
        
        # When showing the panel, hide instructions to avoid clutter
        if self.info_panel_active:
            self.show_instructions = False
    
    def update_info_panel(self) -> None:
        """Update the sliding animation of the info panel."""
        # Animate the sliding of the info panel
        if self.info_panel_position != self.info_panel_target:
            # Move the panel towards the target with easing
            diff = self.info_panel_target - self.info_panel_position
            self.info_panel_position += diff * 0.2  # Adjust speed as needed
            
            # Snap to target if very close
            if abs(diff) < 1:
                self.info_panel_position = self.info_panel_target
    
    def draw_info_panel(self, game_state_text) -> None:
        """Draw the sliding info panel with game state text."""
        if self.info_panel_position > -250:  # Only draw if at least partially visible
            # The panel slides in from the left
            panel_width = 250
            grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
            
            # Draw the panel background
            panel_rect = pygame.Rect(
                self.info_panel_position, 
                0, 
                panel_width, 
                grid_height
            )
            pygame.draw.rect(self.surface, (30, 30, 40), panel_rect)
            pygame.draw.line(
                self.surface,
                const.WHITE,
                (panel_width + self.info_panel_position - 1, 0),
                (panel_width + self.info_panel_position - 1, grid_height),
                2
            )
            
            # Draw the game state text
            if game_state_text:
                # Handle both string and list input types
                if isinstance(game_state_text, str):
                    lines = game_state_text.split('\n')
                else:
                    lines = game_state_text  # Assume it's already a list
                    
                y_offset = 20
                
                for line in lines:
                    line_surf = self.fonts['normal'].render(line, True, const.WHITE)
                    line_rect = line_surf.get_rect(x=self.info_panel_position + 10, y=y_offset)
                    self.surface.blit(line_surf, line_rect)
                    y_offset += 20
    
    def draw_info_button(self) -> pygame.Rect:
        """Draw the info toggle button in the bottom bar."""
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        button_width = 100
        button_height = 40
        
        button = Button(
            10,  # X position
            grid_height + (self.bottom_bar_height - button_height) // 2,  # Centered in bottom bar
            button_width,
            button_height,
            "Info" if not self.info_panel_active else "Hide Info",
            (100, 150, 200)
        )
        button.draw(self.surface, self.fonts['normal'])
        return button.rect
    
    def draw_end_turn_button(self, should_blink=False) -> Tuple[pygame.Rect, Button]:
        """Draw the end turn button in the bottom bar."""
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        button_width = 120
        button_height = 40
        
        button = Button(
            const.SCREEN_WIDTH - button_width - 10,  # Right aligned
            grid_height + (self.bottom_bar_height - button_height) // 2,  # Centered in bottom bar
            button_width,
            button_height,
            "End Turn",
            (200, 100, 100)
        )
        
        # Randomly decide if the button should blink
        if should_blink and not hasattr(self, '_blink_decision_timer'):
            self._blink_decision_timer = 0
            self._should_blink = False
        
        if should_blink:
            # Every 5 seconds, decide whether to blink or not
            if not hasattr(self, '_last_update_time'):
                self._last_update_time = pygame.time.get_ticks()
            
            current_time = pygame.time.get_ticks()
            delta_time = current_time - self._last_update_time
            self._last_update_time = current_time
            
            self._blink_decision_timer += delta_time
            if self._blink_decision_timer >= 5000:  # 5 seconds
                self._blink_decision_timer = 0
                self._should_blink = random.random() < 0.7  # 70% chance to blink
            
            button.set_blinking(self._should_blink)
            button.update_blink(delta_time)
        
        button.draw(self.surface, self.fonts['normal'])
        return button.rect, button
    
    def draw_leave_match_button(self) -> Tuple[pygame.Rect, Button]:
        """Draw the leave match button in the bottom bar."""
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        button_width = 120
        button_height = 40
        
        button = Button(
            360,  # Positioned after the center view button
            grid_height + (self.bottom_bar_height - button_height) // 2,  # Centered in bottom bar
            button_width,
            button_height,
            "Leave Match",
            (200, 50, 50)  # Red color for leave button
        )
        
        button.draw(self.surface, self.fonts['normal'])
        return button.rect, button
    
    def draw_debug_button(self) -> pygame.Rect:
        """Draw the debug toggle button in the bottom bar."""
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        button_width = 100
        button_height = 40
        
        button = Button(
            120,  # Positioned after the info button
            grid_height + (self.bottom_bar_height - button_height) // 2,  # Centered in bottom bar
            button_width,
            button_height,
            "Debug",
            (100, 100, 200)
        )
        button.draw(self.surface, self.fonts['normal'])
        return button.rect
    
    def draw_debug_info(self, ai_state: Optional[str] = None) -> None:
        """Draw debug information in the bottom bar."""
        if not ai_state:
            return
            
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        
        # Display AI state in the bottom right portion of the bottom bar
        text = f"AI State: {ai_state}"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        text_rect = text_surf.get_rect(
            right=const.SCREEN_WIDTH - 150, 
            centery=grid_height + self.bottom_bar_height // 2
        )
        self.surface.blit(text_surf, text_rect)
    
    def draw_instructions(self) -> None:
        """Draw game instructions in the bottom bar."""
        if not self.show_instructions:
            return
        
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        
        # Draw instructions in the center of the bottom bar
        instructions = [
            "SPACE - Enter shooting mode",
            "Click - Move / Shoot",
            "ESC - Cancel action"
        ]
        
        # Calculate centering position
        instruction_text = " | ".join(instructions)
        text_surf = self.fonts['normal'].render(instruction_text, True, const.WHITE)
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, grid_height + self.bottom_bar_height // 2))
        self.surface.blit(text_surf, text_rect)
    
    def draw_menu(self, title_image=None) -> List[Tuple[pygame.Rect, str]]:
        """Draw the main menu and return clickable elements."""
        # Draw a grid background
        self.draw_grid()
        
        # Generate some random obstacles for visual interest
        if not hasattr(self, '_menu_obstacles'):
            self._menu_obstacles = []
            for _ in range(10):  # Add some bushes
                x = random.randint(0, const.GRID_WIDTH - 1)
                y = random.randint(0, const.GRID_HEIGHT - 1)
                self._menu_obstacles.append(('bush', (x, y)))
            
            for _ in range(5):  # Add some crates
                x = random.randint(0, const.GRID_WIDTH - 1)
                y = random.randint(0, const.GRID_HEIGHT - 1)
                self._menu_obstacles.append(('crate', (x, y)))
        
        # Draw the obstacles
        for obstacle_type, (x, y) in self._menu_obstacles:
            rect = pygame.Rect(
                x * const.GRID_SIZE, 
                y * const.GRID_SIZE,
                const.GRID_SIZE, 
                const.GRID_SIZE
            )
            
            if obstacle_type == 'bush':
                # Draw a bush (green circle)
                pygame.draw.circle(
                    self.surface, 
                    (60, 80, 30),  # Dark green
                    (x * const.GRID_SIZE + const.GRID_SIZE // 2, 
                     y * const.GRID_SIZE + const.GRID_SIZE // 2),
                    const.GRID_SIZE // 2 - 2
                )
            else:  # crate
                # Draw a crate (brown rectangle)
                pygame.draw.rect(
                    self.surface, 
                    (90, 60, 40),  # Brown
                    rect.inflate(-8, -8)
                )
                # Add some details to the crate
                pygame.draw.line(
                    self.surface,
                    (70, 45, 30),
                    (rect.left + 4, rect.centery),
                    (rect.right - 4, rect.centery),
                    2
                )
        
        # Create title background
        title_bg_rect = pygame.Rect(
            const.SCREEN_WIDTH // 2 - 225,
            100, 
            450, 
            80
        )
        pygame.draw.rect(self.surface, (15, 30, 60), title_bg_rect)  # Dark navy blue
        pygame.draw.rect(self.surface, (200, 160, 80), title_bg_rect, 3)  # Gold border
        
        # Create title text or use provided image
        if title_image:
            # Use the provided title image
            img_rect = title_image.get_rect(center=(const.SCREEN_WIDTH // 2, 140))
            self.surface.blit(title_image, img_rect)
        else:
            # Use text as fallback
            title_text = self.fonts['big'].render("SNIPER", True, (220, 180, 100))  # Golden color
            title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 140))
            self.surface.blit(title_text, title_rect)
        
        # Return all clickable elements
        buttons = []
        
        # Check if we're showing the main menu or submenu
        if not hasattr(self, 'showing_play_submenu') or not self.showing_play_submenu:
            # Main menu buttons
            button_options = ["PLAY", "OPTIONS", "LEADERBOARD", "EXIT"]
            y_offset = 250
            
            for option in button_options:
                # Create button background
                button_bg_rect = pygame.Rect(
                    const.SCREEN_WIDTH // 2 - 175,
                    y_offset,
                    350,
                    70
                )
                pygame.draw.rect(self.surface, (80, 30, 20), button_bg_rect)  # Brown color
                pygame.draw.rect(self.surface, (200, 160, 80), button_bg_rect, 3)  # Gold border
                
                # Create button text
                button_text = self.fonts['big'].render(option, True, (220, 180, 100))  # Golden color
                button_text_rect = button_text.get_rect(center=(const.SCREEN_WIDTH // 2, y_offset + 35))
                self.surface.blit(button_text, button_text_rect)
                
                # Store button rectangles for click detection
                if option == "PLAY":
                    self.menu_start_button_rect = button_bg_rect
                elif option == "EXIT":
                    self.menu_exit_button_rect = button_bg_rect
                
                buttons.append((button_bg_rect, option))
                y_offset += 90  # Closer spacing to fit all buttons
        else:
            # Back button
            back_rect = pygame.Rect(20, 20, 100, 40)
            pygame.draw.rect(self.surface, (80, 30, 20), back_rect)  # Brown color
            pygame.draw.rect(self.surface, (200, 160, 80), back_rect, 2)  # Gold border
            back_text = self.fonts['normal'].render("< BACK", True, (220, 180, 100))
            back_text_rect = back_text.get_rect(center=(70, 40))
            self.surface.blit(back_text, back_text_rect)
            
            self.back_button_rect = back_rect
            buttons.append((back_rect, "BACK_TO_MENU"))
            
            # Play submenu title
            submenu_text = self.fonts['big'].render("GAME MODE", True, (220, 180, 100))
            submenu_rect = submenu_text.get_rect(center=(const.SCREEN_WIDTH // 2, 220))
            self.surface.blit(submenu_text, submenu_rect)
            
            # Play options
            play_options = ["PLAYER VS AI", "PLAYER VS PLAYER"]
            y_offset = 300
            
            for option in play_options:
                # Create button background
                button_bg_rect = pygame.Rect(
                    const.SCREEN_WIDTH // 2 - 175,
                    y_offset,
                    350,
                    70
                )
                pygame.draw.rect(self.surface, (80, 30, 20), button_bg_rect)  # Brown color
                pygame.draw.rect(self.surface, (200, 160, 80), button_bg_rect, 3)  # Gold border
                
                # Create button text
                button_text = self.fonts['normal'].render(option, True, (220, 180, 100))  # Golden color
                button_text_rect = button_text.get_rect(center=(const.SCREEN_WIDTH // 2, y_offset + 35))
                self.surface.blit(button_text, button_text_rect)
                
                buttons.append((button_bg_rect, option))
                y_offset += 100
        
        return buttons
    
    def toggle_play_submenu(self, show: bool = None) -> None:
        """Toggle or set the play submenu visibility."""
        if show is None:
            # Toggle current state
            self.showing_play_submenu = not getattr(self, 'showing_play_submenu', False)
        else:
            # Set to specified state
            self.showing_play_submenu = show
    
    def draw_scoreboard(self) -> None:
        """Draw the scoreboard screen."""
        title_text = self.fonts['big'].render("Scoreboard", True, const.WHITE)
        title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 100))
        self.surface.blit(title_text, title_rect)
        
        info_text = self.fonts['normal'].render("Press ESC to return to menu", True, const.WHITE)
        info_rect = info_text.get_rect(center=(const.SCREEN_WIDTH // 2, 150))
        self.surface.blit(info_text, info_rect)
    
    def draw_game_over(self, winner: str) -> None:
        """Draw the game over screen."""
        title_text = self.fonts['big'].render("Game Over", True, const.WHITE)
        title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 100))
        self.surface.blit(title_text, title_rect)
        
        winner_text = self.fonts['normal'].render(f"Winner: {winner}", True, const.WHITE)
        winner_rect = winner_text.get_rect(center=(const.SCREEN_WIDTH // 2, 150))
        self.surface.blit(winner_text, winner_rect)
        
        info_text = self.fonts['normal'].render("Press ESC to return to menu", True, const.WHITE)
        info_rect = info_text.get_rect(center=(const.SCREEN_WIDTH // 2, 200))
        self.surface.blit(info_text, info_rect)
    
    def draw_character_select(self, stage: str, selected: Optional[Any], 
                            sniper_types: List) -> List[Tuple[pygame.Rect, str, int]]:
        """Draw the character selection screen."""
        # Black background
        self.surface.fill((0, 0, 0))
        
        # Title text
        title = f"Select {stage.capitalize()} Character"
        title_text = self.fonts['big'].render(title, True, const.WHITE)
        title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 50))
        self.surface.blit(title_text, title_rect)
        
        clickable_elements = []
        
        # Calculate spacing between character boxes
        num_characters = len(sniper_types)
        total_width = num_characters * 180 + (num_characters - 1) * 20  # 180px per char, 20px spacing
        start_x = (const.SCREEN_WIDTH - total_width) // 2
        
        # Draw character options
        for i, sniper_type in enumerate(sniper_types):
            # Calculate position
            x_pos = start_x + i * 200  # 180px box + 20px spacing
            y_pos = 150  # Start y position for character boxes
            
            # Character box background
            char_rect = pygame.Rect(x_pos, y_pos, 180, 180)
            bg_color = (200, 200, 200) if selected == sniper_type else (100, 100, 100)
            pygame.draw.rect(self.surface, bg_color, char_rect)
            
            # Character sprite
            sprite_rect = pygame.Rect(x_pos + 25, y_pos + 25, 130, 130)
            if hasattr(sniper_type, 'sprite') and sniper_type.sprite:
                scaled_sprite = pygame.transform.scale(sniper_type.sprite, (130, 130))
                self.surface.blit(scaled_sprite, sprite_rect)
            else:
                # Draw a colored rectangle if no sprite
                pygame.draw.rect(self.surface, sniper_type.color, sprite_rect)
            
            # Character name - below the sprite box
            name_text = self.fonts['big'].render(sniper_type.name, True, const.WHITE)
            name_rect = name_text.get_rect(center=(x_pos + 90, y_pos + 210))
            self.surface.blit(name_text, name_rect)
            
            # Character description - below the name
            desc_text = self.fonts['normal'].render(sniper_type.description, True, const.WHITE)
            desc_rect = desc_text.get_rect(center=(x_pos + 90, y_pos + 240))
            self.surface.blit(desc_text, desc_rect)
            
            # Add to clickable elements
            clickable_elements.append((char_rect, "character", i))
        
        # Create confirm button rectangle even if no character is selected yet
        # This ensures it's always initialized even if it won't be drawn
        confirm_button_rect = pygame.Rect(
            const.SCREEN_WIDTH // 2 - 150,
            const.SCREEN_HEIGHT - 100,
            300,
            70
        )
        # Store the confirm button rect for future reference always
        self.confirm_button_rect = confirm_button_rect
        
        # Also initialize the cancel button in the same area but not visible
        # This avoids NoneType errors when checking for clicks
        cancel_button_rect = pygame.Rect(
            const.SCREEN_WIDTH // 2 - 150,
            const.SCREEN_HEIGHT - 170,
            300,
            70
        )
        self.cancel_button_rect = cancel_button_rect
        
        # Draw select button if character is selected
        if selected:
            pygame.draw.rect(self.surface, (200, 200, 200), confirm_button_rect)
            pygame.draw.rect(self.surface, (50, 50, 50), confirm_button_rect, 2)
            
            button_text = self.fonts['normal'].render(f"Select {selected.name}", True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT - 65))
            self.surface.blit(button_text, button_text_rect)
            
            clickable_elements.append((confirm_button_rect, "select_button", None))
        
        # Draw back button
        back_button_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.surface, (80, 30, 20), back_button_rect)  # Brown color
        pygame.draw.rect(self.surface, (200, 160, 80), back_button_rect, 2)  # Gold border
        back_text = self.fonts['normal'].render("< BACK", True, (220, 180, 100))
        back_text_rect = back_text.get_rect(center=(70, 40))
        self.surface.blit(back_text, back_text_rect)
        
        # Store the back button rect for future reference
        self.back_button_rect = back_button_rect
        clickable_elements.append((back_button_rect, "back", None))
        
        return clickable_elements
    
    def draw_confirmation_popup(self) -> None:
        """Draw a confirmation popup."""
        # Darken the screen
        overlay = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        # Draw popup box
        popup_rect = pygame.Rect(
            const.SCREEN_WIDTH // 2 - 150,
            const.SCREEN_HEIGHT // 2 - 100,
            300, 200
        )
        pygame.draw.rect(self.surface, (50, 50, 50), popup_rect)
        pygame.draw.rect(self.surface, const.WHITE, popup_rect, 2)
        
        # Text
        text1 = self.fonts['normal'].render("Are you sure?", True, const.WHITE)
        text_rect1 = text1.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2 - 50))
        self.surface.blit(text1, text_rect1)
        
        text2 = self.fonts['normal'].render("Press ESC to cancel", True, const.WHITE)
        text_rect2 = text2.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2))
        self.surface.blit(text2, text_rect2)
    
    def draw_character(self, character: Character, is_player: bool = False, 
                        is_turn: bool = False, camera_x=0, camera_y=0) -> None:
        """Draw a character on the grid with enhanced visual effects."""
        if not character:
            return
            
        # Calculate drawn position with camera offset
        x = character.x * const.GRID_SIZE - camera_x
        y = character.y * const.GRID_SIZE - camera_y
        
        # Draw character background
        rect = pygame.Rect(x, y, const.GRID_SIZE, const.GRID_SIZE)
        
        # Different background colors for player vs enemy
        bg_color = character.sniper_type.color
        
        # Highlight whose turn it is with pulsating glow effect
        if is_turn:
            # Use sine wave for pulsating effect
            pulse_intensity = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # 0.0 to 1.0
            glow_size = int(6 + 4 * pulse_intensity)  # Pulsate between 6-10 pixels
            glow_rect = rect.inflate(glow_size, glow_size)
            
            # Create a glowing halo effect
            glow_color = const.YELLOW if is_player else const.ORANGE
            
            # Draw multiple rectangles with decreasing opacity for glow effect
            for i in range(3):
                glow_alpha = int(200 - i * 60)  # Decreasing opacity
                # Create proper RGBA tuple for the glow color
                glow_color_rgba = (glow_color[0], glow_color[1], glow_color[2], glow_alpha)
                glow_surf = pygame.Surface(glow_rect.inflate(i*2, i*2).size, pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color_rgba, 
                               pygame.Rect(0, 0, glow_rect.width + i*2, glow_rect.height + i*2))
                self.surface.blit(glow_surf, glow_rect.inflate(i*2, i*2).topleft)
        
        pygame.draw.rect(self.surface, bg_color, rect)
        
        # If there's a sprite, draw it
        if hasattr(character.sniper_type, 'sprite') and character.sniper_type.sprite:
            sprite = pygame.transform.scale(character.sniper_type.sprite, 
                                          (const.GRID_SIZE, const.GRID_SIZE))
            
            # Add a subtle bobbing effect for characters
            bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 2
            sprite_y = y + bob_offset
            self.surface.blit(sprite, (x, sprite_y))
        
        # Draw health indicator above character
        health_width = const.GRID_SIZE * (character.health / character.max_health)
        health_height = 5
        health_y = y - health_height - 2
        
        # Background bar with slight transparency
        health_bg = pygame.Surface((const.GRID_SIZE, health_height), pygame.SRCALPHA)
        health_bg.fill((200, 0, 0, 180))
        self.surface.blit(health_bg, (x, health_y))
        
        # Foreground health with gradient based on health percentage
        health_percent = character.health / character.max_health
        if health_percent > 0.7:
            health_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            health_color = (255, 165, 0)  # Orange
        else:
            health_color = (255, 0, 0)  # Red
            
        health_fg = pygame.Surface((health_width, health_height), pygame.SRCALPHA)
        # Create proper RGBA tuple for health color
        health_color_rgba = (health_color[0], health_color[1], health_color[2], 220)
        health_fg.fill(health_color_rgba)
        self.surface.blit(health_fg, (x, health_y))
        
        # Add a player/enemy indicator with improved visibility
        label = "P" if is_player else "E"
        label_color = (0, 200, 255) if is_player else (255, 100, 100)
        label_surf = self.fonts['small'].render(label, True, label_color)
        label_rect = label_surf.get_rect(center=(x + const.GRID_SIZE - 8, y + const.GRID_SIZE - 8))
        
        # Add background to make text more readable
        pygame.draw.rect(
            self.surface,
            (0, 0, 0, 180),
            label_rect.inflate(6, 6)
        )
        
        # Draw text with shadow for better visibility
        shadow_surf = self.fonts['small'].render(label, True, (0, 0, 0))
        self.surface.blit(shadow_surf, (label_rect.x + 1, label_rect.y + 1))
        self.surface.blit(label_surf, label_rect)
    
    def draw_return_to_player_button(self) -> pygame.Rect:
        """Draw the return to player button in the bottom bar."""
        grid_height = const.SCREEN_HEIGHT - self.bottom_bar_height
        button_width = 120
        button_height = 40
        
        button = Button(
            230,  # Positioned after the debug button
            grid_height + (self.bottom_bar_height - button_height) // 2,  # Centered in bottom bar
            button_width,
            button_height,
            "Center View",
            (50, 150, 50)  # Green color for the button
        )
        button.draw(self.surface, self.fonts['normal'])
        return button.rect
    
    def handle_character_select_click(self, mouse_pos, sniper_types, stage):
        """Handle clicks on the character selection screen and return selected character if any."""
        # mouse_pos should already be properly scaled by the caller
        
        # Check if a character is clicked
        num_characters = len(sniper_types)
        total_width = num_characters * 180 + (num_characters - 1) * 20  # 180px per char, 20px spacing
        start_x = (const.SCREEN_WIDTH - total_width) // 2
        
        for i, sniper_type in enumerate(sniper_types):
            # Calculate position
            x_pos = start_x + i * 200  # 180px box + 20px spacing
            y_pos = 150  # Start y position for character boxes
            
            # Character box rectangle
            char_rect = pygame.Rect(x_pos, y_pos, 180, 180)
            
            if char_rect.collidepoint(mouse_pos):
                debug_print(f"Selected character: {sniper_type.name}")
                return sniper_type
                
        return None
    
    def draw_valid_movement_tiles(self, player, obstacles, camera_x=0, camera_y=0):
        """Highlight valid movement tiles based on player's courage points."""
        if not player:
            return
            
        # Get player's current position and courage points
        px, py = player.x, player.y
        courage = player.courage_points
        
        # For each possible position within courage range
        for dx in range(-courage, courage + 1):
            for dy in range(-courage, courage + 1):
                # Skip if Manhattan distance exceeds courage points
                if abs(dx) + abs(dy) > courage:
                    continue
                    
                # Calculate target grid position
                grid_x = px + dx
                grid_y = py + dy
                
                # Skip if out of grid bounds
                if (grid_x < 0 or grid_x >= const.GRID_WIDTH or
                    grid_y < 0 or grid_y >= const.GRID_HEIGHT):
                    continue
                    
                # Skip if position is occupied by an obstacle
                is_obstacle = False
                for obstacle in obstacles:
                    if obstacle.collidepoint(grid_x, grid_y):
                        is_obstacle = True
                        break
                if is_obstacle:
                    continue
                    
                # Skip the current player position
                if grid_x == px and grid_y == py:
                    continue
                    
                # This is a valid movement position, draw highlight
                screen_x = grid_x * const.GRID_SIZE - camera_x
                screen_y = grid_y * const.GRID_SIZE - camera_y
                
                # Only draw if position is within visible area
                if (0 <= screen_x < const.SCREEN_WIDTH and 
                    0 <= screen_y < const.SCREEN_HEIGHT - self.bottom_bar_height):
                    
                    # Draw a semi-transparent highlight rectangle
                    highlight_surf = pygame.Surface((const.GRID_SIZE, const.GRID_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(
                        highlight_surf, 
                        (0, 255, 0, 80),  # Green with alpha
                        pygame.Rect(0, 0, const.GRID_SIZE, const.GRID_SIZE)
                    )
                    
                    # Draw a border for the highlight
                    pygame.draw.rect(
                        highlight_surf, 
                        (0, 255, 0, 160),  # Green border with alpha
                        pygame.Rect(0, 0, const.GRID_SIZE, const.GRID_SIZE),
                        2  # Border width
                    )
                    
                    self.surface.blit(highlight_surf, (screen_x, screen_y))