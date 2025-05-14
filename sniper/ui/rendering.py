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
        self.show_commands = False  # Add toggle for commands visibility
        
        # Load tree image
        try:
            self.tree_image = pygame.image.load("assets/tree.png").convert_alpha()
            # Scale it to fit in a grid cell (slightly smaller than grid size)
            scale_size = int(const.GRID_SIZE * 0.9)
            self.tree_image = pygame.transform.scale(self.tree_image, (scale_size, scale_size))
        except (pygame.error, FileNotFoundError):
            print("Warning: Could not load tree image, using fallback.")
            self.tree_image = None
            
    # Helper methods for futuristic UI
    def draw_rounded_rect(self, surface, color, rect, radius=15, alpha=255, border_width=0, border_color=None):
        """Draw a rounded rectangle with optional transparency and border."""
        if alpha < 255:
            shape_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (*color, alpha), shape_surf.get_rect(), border_radius=radius)
            surface.blit(shape_surf, rect)
        else:
            pygame.draw.rect(surface, color, rect, border_radius=radius)
        
        # Draw border if specified
        if border_width > 0 and border_color:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
    
    def draw_energy_bar(self, surface, rect, value, max_value, fg_color, bg_color, border_color=None, 
                        segments=5, glow=False, text=None, text_color=None, font=None):
        """Draw a segmented energy bar with optional glow effect."""
        # Background
        self.draw_rounded_rect(surface, bg_color, rect, radius=rect.height//2)
        
        # Calculate filled width
        fill_width = int((value / max_value) * rect.width)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            
            # Draw with segments
            segment_width = rect.width / segments
            for i in range(segments):
                segment_x = rect.x + (i * segment_width)
                segment_w = min(segment_width - 2, rect.x + rect.width - segment_x)
                
                if segment_x < rect.x + fill_width:
                    seg_width = min(segment_w, rect.x + fill_width - segment_x)
                    if seg_width > 0:
                        segment_rect = pygame.Rect(segment_x, rect.y, seg_width, rect.height)
                        self.draw_rounded_rect(surface, fg_color, segment_rect, radius=rect.height//2)
            
            # Add glow effect
            if glow:
                glow_surf = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*fg_color, 100), glow_surf.get_rect(), border_radius=rect.height//2)
                surface.blit(glow_surf, (fill_rect.x, fill_rect.y - 2))  # Offset slightly for glow effect
        
        # Border
        if border_color:
            pygame.draw.rect(surface, border_color, rect, 1, border_radius=rect.height//2)
        
        # Text
        if text and font:
            text_surf = font.render(text, True, text_color or (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)
    
    def draw_hexagonal_button(self, surface, center_pos, radius, color, border_color=None, 
                              text=None, font=None, text_color=None, enabled=True, alpha=255):
        """Draw a hexagonal button with optional text."""
        # Calculate vertices for a hexagon
        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_pos[0] + radius * math.cos(angle_rad)
            y = center_pos[1] + radius * math.sin(angle_rad)
            vertices.append((x, y))
        
        # Draw the hexagon
        if alpha < 255:
            # Create a surface with per-pixel alpha
            button_surf = pygame.Surface((radius*2 + 4, radius*2 + 4), pygame.SRCALPHA)
            button_rect = button_surf.get_rect(center=center_pos)
            pygame.draw.polygon(button_surf, (*color, alpha), [(x - button_rect.x, y - button_rect.y) for x, y in vertices])
            
            # Draw border if needed
            if border_color:
                pygame.draw.polygon(button_surf, border_color, [(x - button_rect.x, y - button_rect.y) for x, y in vertices], 2)
                
            # Add text if provided
            if text and font:
                alpha_factor = 255 if enabled else 150
                text_surf = font.render(text, True, text_color or (min(255, text_color[0] + 30), 
                                                                  min(255, text_color[1] + 30), 
                                                                  min(255, text_color[2] + 30)))
                text_surf.set_alpha(alpha_factor)
                text_rect = text_surf.get_rect(center=(button_rect.width//2, button_rect.height//2))
                button_surf.blit(text_surf, text_rect)
            
            surface.blit(button_surf, button_rect)
        else:
            pygame.draw.polygon(surface, color, vertices)
            if border_color:
                pygame.draw.polygon(surface, border_color, vertices, 2)
            
            if text and font:
                text_surf = font.render(text, True, text_color or (255, 255, 255))
                text_rect = text_surf.get_rect(center=center_pos)
                surface.blit(text_surf, text_rect)
                
        # Return a rect that approximates the hexagon for hit detection
        return pygame.Rect(center_pos[0] - radius, center_pos[1] - radius, radius*2, radius*2)
    
    def draw_grid(self) -> None:
        """Draw the game grid with space theme."""
        for x in range(0, const.SCREEN_WIDTH, const.GRID_SIZE):
            # Lighter grid lines
            pygame.draw.line(self.surface, const.SPACE_GRID, (x, 0), (x, const.SCREEN_HEIGHT))
        for y in range(0, const.SCREEN_HEIGHT, const.GRID_SIZE):
            pygame.draw.line(self.surface, const.SPACE_GRID, (0, y), (const.SCREEN_WIDTH, y))
            
    def draw_space_background(self):
        """Draw the space background with stars."""
        # Fill with deep space color
        self.surface.fill(const.SPACE_BG)
        
        # Draw stars if we haven't generated them yet
        if not hasattr(self, '_stars'):
            import random
            self._stars = []
            # Generate 100 stars with random positions and sizes
            for _ in range(100):
                x = random.randint(0, const.SCREEN_WIDTH)
                y = random.randint(0, const.SCREEN_HEIGHT)
                size = random.randint(1, 2)
                brightness = random.randint(150, 255)
                self._stars.append((x, y, size, brightness))
        
        # Draw stars
        for x, y, size, brightness in self._stars:
            pygame.draw.circle(
                self.surface, 
                (brightness, brightness, brightness), 
                (x, y), 
                size
            )
            
    def draw_obstacles(self, obstacles: List[Tuple[int, int]]) -> None:
        """
        Draw obstacles on the grid.
        This is used when we have a simple list of obstacle positions.
        """
        for x, y in obstacles:
            rect = pygame.Rect(
                x * const.GRID_SIZE, 
                y * const.GRID_SIZE,
                const.GRID_SIZE, 
                const.GRID_SIZE
            )
            pygame.draw.rect(self.surface, const.GRAY, rect)
            
    def draw_scenario(self, scenario_manager) -> None:
        """
        Draw the scenario objects with their visual states and animations.
        This should be used instead of draw_obstacles when using ScenarioManager.
        """
        if scenario_manager:
            scenario_manager.draw(self.surface)
            
    def draw_round_info(self, round_number: int) -> None:
        """Draw round information at the top right of the screen."""
        round_text = f"Round: {round_number}"
        text_surf = self.fonts['normal'].render(round_text, True, (220, 180, 100))
        text_rect = text_surf.get_rect(topright=(const.SCREEN_WIDTH - 10, 10))
        self.surface.blit(text_surf, text_rect)
    
    def draw_projectiles(self, projectiles: List[Projectile]) -> None:
        """Draw active projectiles."""
        for p in projectiles:
            center_x = int((p.x + 0.5) * const.GRID_SIZE)
            center_y = int((p.y + 0.5) * const.GRID_SIZE)
            pygame.draw.circle(self.surface, p.color, (center_x, center_y), const.PROJECTILE_RADIUS)
    
    def draw_hud_grid(self, player: Character, enemy: Character, player_turn: bool = True) -> None:
        """Draw HUD with player and enemy info."""
        # Compact Player info at top
        pygame.draw.rect(self.surface, (50, 50, 50), 
                       pygame.Rect(const.HUD_SPACING, const.HUD_SPACING, 300, 40))
        
        # Player text - more compact display
        text = f"Player: {player.sniper_type.name} ({player.moves_left} moves, {player.shots_left} shots)"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        self.surface.blit(text_surf, (const.HUD_SPACING + 10, const.HUD_SPACING + 12))
        
        # Turn indicator in center top
        text = "Player's Turn" if player_turn else "Enemy's Turn"
        color = const.GREEN if player_turn else const.RED
        text_surf = self.fonts['normal'].render(text, True, color)
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.HUD_SPACING + 20))
        self.surface.blit(text_surf, text_rect)
        
        # Enemy info - right side, more compact
        pygame.draw.rect(self.surface, (50, 50, 50), 
                       pygame.Rect(const.SCREEN_WIDTH - 200 - const.HUD_SPACING, 
                                 const.HUD_SPACING, 200, 40))
        
        # Enemy text - more compact display
        text = f"Enemy: {enemy.sniper_type.name}"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        self.surface.blit(text_surf, (const.SCREEN_WIDTH - 190 - const.HUD_SPACING, 
                                    const.HUD_SPACING + 12))
    
    def draw_turn_indicator(self, player_turn: bool) -> None:
        """Draw an indicator showing whose turn it is."""
        text = "Player's Turn" if player_turn else "Enemy's Turn"
        color = const.GREEN if player_turn else const.RED
        
        text_surf = self.fonts['normal'].render(text, True, color)
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.HUD_SPACING + 20))
        self.surface.blit(text_surf, text_rect)
    
    def draw_shooting_arrow(self, x: int, y: int, target_pos: Tuple[int, int]) -> None:
        """Draw an arrow indicating shooting direction."""
        start_pos = (x * const.GRID_SIZE + const.GRID_SIZE // 2, 
                    y * const.GRID_SIZE + const.GRID_SIZE // 2)
        
        # Calculate direction vector
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        
        # Normalize
        length = max(0.01, (dx**2 + dy**2)**0.5)
        dx /= length
        dy /= length
        
        # Draw line
        end_pos = (start_pos[0] + dx * 100, start_pos[1] + dy * 100)
        pygame.draw.line(self.surface, const.YELLOW, start_pos, end_pos, 2)
        
        # Draw arrowhead
        arrow_size = 10
        pygame.draw.polygon(self.surface, const.YELLOW, [
            end_pos,
            (end_pos[0] - arrow_size * dx - arrow_size * dy * 0.5, 
             end_pos[1] - arrow_size * dy + arrow_size * dx * 0.5),
            (end_pos[0] - arrow_size * dx + arrow_size * dy * 0.5, 
             end_pos[1] - arrow_size * dy - arrow_size * dx * 0.5)
        ])
    
    def draw_end_turn_button(self) -> pygame.Rect:
        """Draw the end turn button."""
        # Position in the bottom panel, right-aligned with 40px margin
        button_width = 160
        button_height = 40
        button_rect = pygame.Rect(
            const.SCREEN_WIDTH - button_width - 40,  # Right-aligned with 40px margin
            const.SCREEN_HEIGHT - 70,                # Vertically centered in the bottom HUD
            button_width,
            button_height
        )
        pygame.draw.rect(self.surface, (80, 30, 20), button_rect)  # Brown background
        pygame.draw.rect(self.surface, (220, 180, 100), button_rect, 2)  # Gold border
        
        # Text
        text_surf = self.fonts['normal'].render("End Turn", True, (220, 180, 100))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.surface.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_debug_button(self) -> pygame.Rect:
        """Draw the debug toggle button."""
        # Position in the header - left corner
        button_rect = pygame.Rect(
            10,  # Left position - very close to the left edge
            5,   # Vertically centered in the header
            80,  # Width (80px)
            30   # Height
        )
        pygame.draw.rect(self.surface, (80, 30, 20), button_rect)  # Brown background
        pygame.draw.rect(self.surface, (220, 180, 100), button_rect, 2)  # Gold border
        
        # Text
        text_surf = self.fonts['normal'].render("Debug", True, (220, 180, 100))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.surface.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_show_commands_button(self) -> pygame.Rect:
        """Draw the button to toggle command instructions visibility."""
        # Position in the header - to the right of debug
        button_rect = pygame.Rect(
            100,  # To the right of Debug button
            5,    # Vertically centered in the header
            100,  # Width
            30,   # Height
            )
        pygame.draw.rect(self.surface, (80, 30, 20), button_rect)  # Brown background
        pygame.draw.rect(self.surface, (220, 180, 100), button_rect, 2)  # Gold border
        
        # Text
        text_surf = self.fonts['normal'].render("Commands", True, (220, 180, 100))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.surface.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_debug_info(self, ai_state: Optional[str] = None) -> None:
        """Draw debug information."""
        # Create a semi-transparent background for the debug info
        debug_bg = pygame.Rect(10, const.SCREEN_HEIGHT - 150, 300, 140)
        bg_surface = pygame.Surface((debug_bg.width, debug_bg.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.surface.blit(bg_surface, debug_bg)
        
        # Show AI state status
        y_offset = const.SCREEN_HEIGHT - 145
        
        # Display AI state
        if ai_state:
            text = f"AI State: {ai_state}"
            text_surf = self.fonts['normal'].render(text, True, (220, 180, 100))  # Golden color for visibility
            self.surface.blit(text_surf, (15, y_offset))
            y_offset += 25
            
        # Display additional debug information
        debug_lines = [
            f"FPS: {int(pygame.time.Clock().get_fps())}",
            f"Debug Mode: ON",
            f"Round Animation Active: {hasattr(pygame, 'ScenarioManager') and getattr(pygame.ScenarioManager, 'round_transition_active', False)}",
            f"Asteroid Count: {len([b for b in getattr(pygame, 'blocks', []) if not getattr(b, 'is_destroyed', True)])}"
        ]
        
        for line in debug_lines:
            text_surf = self.fonts['normal'].render(line, True, (220, 180, 100))
            self.surface.blit(text_surf, (15, y_offset))
            y_offset += 20
    
    def draw_instructions(self) -> None:
        """Draw game instructions."""
        # Only display instructions if the show_commands toggle is on
        if not self.show_commands:
            return
            
        instructions = [
            "SPACE - Enter shooting mode",
            "Click - Move / Shoot",
            "ESC - Cancel action"
        ]
        
        # Draw a semi-transparent background for better readability
        bg_rect = pygame.Rect(5, const.SCREEN_HEIGHT - 165, 210, 80)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.surface.blit(bg_surface, bg_rect)
        
        y_offset = const.SCREEN_HEIGHT - 160
        for instruction in instructions:
            text_surf = self.fonts['normal'].render(instruction, True, const.WHITE)
            self.surface.blit(text_surf, (10, y_offset))
            y_offset += 20
    
    def draw_menu(self) -> List[Tuple[pygame.Rect, str]]:
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
                # Use tree image if loaded
                if hasattr(self, 'tree_image') and self.tree_image:
                    # Calculate position to center the tree in the grid cell
                    tree_pos = (x * const.GRID_SIZE + (const.GRID_SIZE - self.tree_image.get_width()) // 2,
                                y * const.GRID_SIZE + (const.GRID_SIZE - self.tree_image.get_height()) // 2)
                    self.surface.blit(self.tree_image, tree_pos)
                else:
                    # Fallback to circular bush
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
        
        # Create title text
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
        # Apply themed background if a character is selected
        if selected:
            # Create a darker version of the character's color for the background
            char_color = selected.color if hasattr(selected, 'color') else (100, 100, 100)
            bg_color = (
                max(0, char_color[0] * 0.15),  # Darker R
                max(0, char_color[1] * 0.15),  # Darker G
                max(0, char_color[2] * 0.15)   # Darker B
            )
            accent_color = char_color
            glow_color = (
                min(255, char_color[0] + 40),
                min(255, char_color[1] + 40),
                min(255, char_color[2] + 40)
            )
            
            # Fill with dark themed background
            self.surface.fill(bg_color)
            
            # Add tech patterns - horizontal lines for a high-tech feel
            for y in range(0, const.SCREEN_HEIGHT, 20):
                alpha = 10 + (y % 40) // 20 * 5  # Alternate line opacity
                pygame.draw.line(self.surface, (*accent_color, alpha), 
                                (0, y), (const.SCREEN_WIDTH, y), 1)
            
            # Add decorative hexagons matching character theme
            for _ in range(8):
                x = random.randint(50, const.SCREEN_WIDTH - 50)
                y = random.randint(50, const.SCREEN_HEIGHT - 50)
                size = random.randint(20, 80)
                alpha = random.randint(10, 25)
                
                self.draw_hexagonal_button(
                    self.surface,
                    center_pos=(x, y),
                    radius=size,
                    color=bg_color,
                    border_color=accent_color,
                    enabled=True,
                    alpha=alpha
                )
        else:
            # Default black background if no character selected
            self.surface.fill((0, 0, 0))
        
        # Title text with glow effect if character selected
        title = f"Select {stage.capitalize()} Character"
        if selected:
            title_glow = self.fonts['big'].render(title, True, glow_color)
            title_text = self.fonts['big'].render(title, True, accent_color)
            title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 50))
            # Add glow behind text
            self.surface.blit(title_glow, (title_rect.x + 1, title_rect.y + 1))
            self.surface.blit(title_text, title_rect)
            
            # Add decorative hex symbols beside title
            self.draw_hexagonal_button(
                self.surface,
                center_pos=(title_rect.left - 30, 50),
                radius=10,
                color=bg_color,
                border_color=accent_color,
                enabled=True,
                alpha=230
            )
            self.draw_hexagonal_button(
                self.surface,
                center_pos=(title_rect.right + 30, 50),
                radius=10,
                color=bg_color,
                border_color=accent_color,
                enabled=True,
                alpha=230
            )
        else:
            # Standard white title if no character selected
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
            
            # Character box background - apply styling based on selection
            char_rect = pygame.Rect(x_pos, y_pos, 180, 180)
            
            if selected == sniper_type:
                # Selected character gets themed styling with glow
                char_color = sniper_type.color if hasattr(sniper_type, 'color') else (200, 200, 200)
                
                # Draw glow effect for selected character
                glow_surf = pygame.Surface((char_rect.width + 10, char_rect.height + 10), pygame.SRCALPHA)
                glow_color = (
                    min(255, char_color[0] + 40),
                    min(255, char_color[1] + 40),
                    min(255, char_color[2] + 40)
                )
                
                for i in range(5):
                    glow_alpha = 50 - i * 10
                    glow_rect = pygame.Rect(i, i, char_rect.width + 10 - i*2, char_rect.height + 10 - i*2)
                    pygame.draw.rect(glow_surf, (*glow_color, glow_alpha), glow_rect, border_radius=15)
                
                self.surface.blit(glow_surf, (char_rect.x - 5, char_rect.y - 5))
                
                # Draw character box with themed color and border
                self.draw_rounded_rect(
                    self.surface,
                    (max(20, char_color[0] * 0.4), max(20, char_color[1] * 0.4), max(20, char_color[2] * 0.4)),
                    char_rect,
                    radius=10,
                    border_width=3,
                    border_color=char_color
                )
            else:
                # Non-selected characters get simple dark styling
                pygame.draw.rect(self.surface, (70, 70, 70), char_rect)
                pygame.draw.rect(self.surface, (100, 100, 100), char_rect, 2)  # Border
            
            # Character sprite
            sprite_rect = pygame.Rect(x_pos + 25, y_pos + 25, 130, 130)
            if hasattr(sniper_type, 'sprite') and sniper_type.sprite:
                scaled_sprite = pygame.transform.scale(sniper_type.sprite, (130, 130))
                self.surface.blit(scaled_sprite, sprite_rect)
            else:
                # Draw a colored rectangle if no sprite
                pygame.draw.rect(self.surface, sniper_type.color if hasattr(sniper_type, 'color') else (200, 0, 0), sprite_rect)
            
            # Character name with glow effect if selected
            if selected == sniper_type and hasattr(sniper_type, 'color'):
                glow_color = (
                    min(255, sniper_type.color[0] + 40),
                    min(255, sniper_type.color[1] + 40),
                    min(255, sniper_type.color[2] + 40)
                )
                name_glow = self.fonts['big'].render(sniper_type.name, True, glow_color)
                name_text = self.fonts['big'].render(sniper_type.name, True, sniper_type.color)
                name_rect = name_text.get_rect(center=(x_pos + 90, y_pos + 210))
                
                # Add glow effect
                self.surface.blit(name_glow, (name_rect.x + 1, name_rect.y + 1))
                self.surface.blit(name_text, name_rect)
            else:
                name_text = self.fonts['big'].render(sniper_type.name, True, const.WHITE)
                name_rect = name_text.get_rect(center=(x_pos + 90, y_pos + 210))
                self.surface.blit(name_text, name_rect)
            
            # Character description - with theme if selected
            if selected == sniper_type and hasattr(sniper_type, 'color'):
                desc_text = self.fonts['normal'].render(sniper_type.description, True, sniper_type.color)
            else:
                desc_text = self.fonts['normal'].render(sniper_type.description, True, const.WHITE)
                
            desc_rect = desc_text.get_rect(center=(x_pos + 90, y_pos + 240))
            self.surface.blit(desc_text, desc_rect)
            
            # Add to clickable elements
            clickable_elements.append((char_rect, "character", i))
        
        # Draw select button if character is selected - themed with character color
        if selected:
            select_button_width = 300
            select_button_height = 70
            select_button_rect = pygame.Rect(
                const.SCREEN_WIDTH // 2 - select_button_width // 2,
                const.SCREEN_HEIGHT - 100,
                select_button_width,
                select_button_height
            )
            
            char_color = selected.color if hasattr(selected, 'color') else (200, 200, 200)
            glow_color = (
                min(255, char_color[0] + 40),
                min(255, char_color[1] + 40),
                min(255, char_color[2] + 40)
            )
            
            # Create button with character theme
            self.draw_rounded_rect(
                self.surface,
                (max(40, char_color[0] * 0.5), max(40, char_color[1] * 0.5), max(40, char_color[2] * 0.5)),
                select_button_rect,
                radius=15,
                border_width=3,
                border_color=char_color
            )
            
            # Button text with glow
            button_text = f"Select {selected.name}"
            text_glow = self.fonts['big'].render(button_text, True, glow_color)
            text_surf = self.fonts['big'].render(button_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT - 65))
            
            # Add glow effect
            self.surface.blit(text_glow, (text_rect.x + 1, text_rect.y + 1))
            self.surface.blit(text_surf, text_rect)
            
            clickable_elements.append((select_button_rect, "select_button", None))
        
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
    
    def draw_game_header(self, player: Character, player_turn: bool = True) -> None:
        """Draw the game header with turn indicator and player stats."""
        # Header background - full width bar at top with rounded bottom corners
        header_height = 40
        header_rect = pygame.Rect(0, 0, const.SCREEN_WIDTH, header_height)
        
        # Use player's character color for styling
        if player_turn:
            player_color = player.sniper_type.color
            # Create a darker version of the player's color for the background
            background_color = (
                max(0, player_color[0] * 0.2),  # R
                max(0, player_color[1] * 0.2),  # G
                max(0, player_color[2] * 0.2)   # B
            )
            accent_color = player_color
            glow_color = (min(255, player_color[0] + 40),
                         min(255, player_color[1] + 40),
                         min(255, player_color[2] + 40))
        else:
            # Enemy's turn - use red theme
            background_color = (40, 10, 10)  # Dark red background
            accent_color = const.RED
            glow_color = (230, 60, 60)  # Brighter red
        
        # Draw semi-transparent background with bottom rounded corners
        header_surface = pygame.Surface((const.SCREEN_WIDTH, header_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(header_surface, (*background_color, 230), 
                        pygame.Rect(0, 0, const.SCREEN_WIDTH, header_height + 10),
                        border_bottom_left_radius=15, border_bottom_right_radius=15)
        
        # Add tech patterns - horizontal lines for a high-tech feel
        for y in range(5, header_height, 4):
            pygame.draw.line(header_surface, (*accent_color, 25), (10, y), (const.SCREEN_WIDTH - 10, y), 1)
        
        # Add a subtle glow at the bottom edge
        for i in range(3):
            pygame.draw.rect(header_surface, (*accent_color, 15 - i * 5), 
                            pygame.Rect(0, header_height - i, const.SCREEN_WIDTH, 1))
        
        self.surface.blit(header_surface, (0, 0))
        
        # Draw accent border with bottom rounded corners (just the bottom part)
        pygame.draw.line(self.surface, accent_color, (0, header_height), (15, header_height), 2)
        pygame.draw.line(self.surface, accent_color, (const.SCREEN_WIDTH - 15, header_height), (const.SCREEN_WIDTH, header_height), 2)
        
        # Turn text with glow effect
        name = player.sniper_type.name if player_turn else "Enemy"
        header_text = f"{name}'s Turn"
        
        text_glow = self.fonts['big'].render(header_text, True, glow_color)
        text_surf = self.fonts['big'].render(header_text, True, accent_color)
        
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, 20))
        
        # Add glow effect behind text
        self.surface.blit(text_glow, (text_rect.x + 1, text_rect.y + 1))
        self.surface.blit(text_surf, text_rect)
        
        # Add decorative hex symbols at the sides of the header text
        if player_turn:
            self.draw_hexagonal_button(
                self.surface,
                center_pos=(text_rect.left - 30, 20),
                radius=8,
                color=background_color,
                border_color=accent_color,
                enabled=True,
                alpha=230
            )
            self.draw_hexagonal_button(
                self.surface,
                center_pos=(text_rect.right + 30, 20),
                radius=8,
                color=background_color,
                border_color=accent_color,
                enabled=True,
                alpha=230
            )
        
        # Show moves and shots remaining with a tech-styled info panel
        if player_turn:
            stats_rect = pygame.Rect(const.SCREEN_WIDTH // 2 - 100, header_height + 5, 200, 25)
            self.draw_rounded_rect(
                self.surface,
                background_color,
                stats_rect,
                radius=10,
                alpha=180,
                border_width=1,
                border_color=accent_color
            )
            
            # Stats text with glow
            stats_text = f"Moves: {player.moves_left} | Shots: {player.shots_left}"
            stats_glow = self.fonts['normal'].render(stats_text, True, glow_color)
            stats_surf = self.fonts['normal'].render(stats_text, True, accent_color)
            stats_rect = stats_surf.get_rect(center=(const.SCREEN_WIDTH // 2, header_height + 17))
            
            self.surface.blit(stats_glow, (stats_rect.x + 1, stats_rect.y + 1))
            self.surface.blit(stats_surf, stats_rect)
    
    def draw_player_stats_panel(self, player: Character, player_turn: bool = True) -> pygame.Rect:
        """Draw the player stats panel at the bottom of the screen and return the courage button rect."""
        # Main panel container (spans bottom of screen)
        panel_height = 100
        panel_top = const.SCREEN_HEIGHT - panel_height
        main_panel = pygame.Rect(0, panel_top, const.SCREEN_WIDTH, panel_height)

        # Get color based on player's character when it's player's turn, or red for enemy's turn
        if player_turn:
            player_color = player.sniper_type.color
            # Create a darker version of the player's color for the background
            panel_bg_color = (
                max(0, player_color[0] * 0.15),  # Darker R
                max(0, player_color[1] * 0.15),  # Darker G
                max(0, player_color[2] * 0.15)   # Darker B
            )
            accent_color = player.sniper_type.color
            glow_color = (min(255, player_color[0] + 40),
                        min(255, player_color[1] + 40),
                        min(255, player_color[2] + 40))
        else:
            # Enemy's turn - use red theme
            panel_bg_color = (30, 10, 10)  # Darker red background
            accent_color = const.RED
            glow_color = (230, 60, 60)  # Brighter red for glow
            
        # Draw the panel with rounded corners and semi-transparency
        self.draw_rounded_rect(
            self.surface,
            panel_bg_color,
            main_panel,
            radius=15,
            alpha=230,
            border_width=2,
            border_color=accent_color
        )

        # LEFT SECTION - Player portrait and stats
        portrait_size = 80
        portrait_rect = pygame.Rect(20, panel_top + 10, portrait_size, portrait_size)
        
        # Draw portrait background with glow effect
        glow_surf = pygame.Surface((portrait_size + 6, portrait_size + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*accent_color, 100), glow_surf.get_rect(), border_radius=10)
        self.surface.blit(glow_surf, (portrait_rect.x - 3, portrait_rect.y - 3))
        
        # Draw portrait background
        self.draw_rounded_rect(
            self.surface,
            (40, 40, 60),
            portrait_rect,
            radius=10,
            border_width=2,
            border_color=accent_color
        )

        # Display player portrait if available
        if hasattr(player, 'sniper_type') and hasattr(player.sniper_type, 'sprite') and player.sniper_type.sprite:
            scaled_sprite = pygame.transform.scale(player.sniper_type.sprite, (portrait_size - 16, portrait_size - 16))
            self.surface.blit(scaled_sprite, (portrait_rect.x + 8, portrait_rect.y + 8))

        # Player name just right of the portrait with a subtle glow effect
        stats_x = portrait_rect.right + 20
        name_text = self.fonts['big'].render(player.sniper_type.name, True, accent_color)
        name_glow = self.fonts['big'].render(player.sniper_type.name, True, glow_color)
        name_rect = name_text.get_rect(topleft=(stats_x, panel_top + 15))
        self.surface.blit(name_glow, (name_rect.x + 1, name_rect.y + 1))
        self.surface.blit(name_text, name_rect)

        # Health bar - futuristic energy shield style
        health_width = 150
        health_height = 18
        health_rect = pygame.Rect(stats_x, panel_top + 50, health_width, health_height)
        
        # Draw health bar
        self.draw_energy_bar(
            self.surface,
            health_rect,
            player.health,
            100,  # Max health
            (220, 60, 60),  # Red foreground
            (50, 20, 20),   # Dark red background
            accent_color,   # Border color
            segments=8,     # Number of segments for tech look
            glow=True,      # Add glow effect
            text=f"{int(player.health)}/100",
            text_color=(255, 255, 255),
            font=self.fonts['normal']
        )

        # COURAGE SECTION
        courage_x = stats_x + 180
        courage_width = 120
        courage_height = 18

        # Draw "Courage:" label with subtle glow
        courage_label = self.fonts['normal'].render("Courage", True, accent_color)
        courage_glow = self.fonts['normal'].render("Courage", True, glow_color)
        self.surface.blit(courage_glow, (courage_x + 1, panel_top + 26))
        self.surface.blit(courage_label, (courage_x, panel_top + 25))

        # Draw courage bar
        courage_rect = pygame.Rect(courage_x, panel_top + 50, courage_width, courage_height)
        
        self.draw_energy_bar(
            self.surface,
            courage_rect,
            player.courage,
            const.COURAGE_MAX,
            (80, 100, 230),  # Blue foreground
            (20, 20, 60),    # Dark blue background
            accent_color,    # Border color
            segments=5,      # Number of segments for tech look
            glow=True,       # Add glow effect
            text=f"{int(player.courage)}/{const.COURAGE_MAX}",
            text_color=(255, 255, 255),
            font=self.fonts['normal']
        )

        # Courage Button - now hexagonal for a more space-tech feel
        courage_button_size = 34
        courage_button_x = courage_x + courage_width + 30
        courage_button_y = panel_top + (panel_height - courage_button_size) // 2 + 5
        
        # Determine if button is enabled
        button_enabled = player.courage >= const.COURAGE_BUTTON_COST
        button_color = (80, 100, 230) if button_enabled else (40, 40, 70)
        
        # Draw hexagonal button
        courage_button_rect = self.draw_hexagonal_button(
            self.surface,
            center_pos=(courage_button_x + courage_button_size//2, courage_button_y + courage_button_size//2),
            radius=courage_button_size//2,
            color=button_color,
            border_color=accent_color,
            text="+",
            font=self.fonts['normal'],
            text_color=(255, 255, 255),
            enabled=button_enabled,
            alpha=255 if button_enabled else 180
        )

        # Draw cost below button with subtle glow if enabled
        cost_color = accent_color if button_enabled else (120, 120, 120)
        cost_text = self.fonts['normal'].render(f"{const.COURAGE_BUTTON_COST}", True, cost_color)
        cost_pos = (courage_button_x + courage_button_size//2 - cost_text.get_width()//2, 
                    courage_button_y + courage_button_size + 5)
        
        # Add glow if enabled
        if button_enabled:
            cost_glow = self.fonts['normal'].render(f"{const.COURAGE_BUTTON_COST}", True, glow_color)
            self.surface.blit(cost_glow, (cost_pos[0] + 1, cost_pos[1] + 1))
            
        self.surface.blit(cost_text, cost_pos)

        # CENTER SECTION - Powers - position next to End Turn button
        # Calculate End Turn left position for alignment
        button_width = 160
        end_turn_left = const.SCREEN_WIDTH - button_width - 40
        # Vertical center of panel
        center_y = panel_top + panel_height // 2
        
        # Create a special power section with tech design
        power_section_rect = pygame.Rect(
            end_turn_left - 220, 
            panel_top + 20, 
            200, 
            60
        )
        
        # Draw power section background
        self.draw_rounded_rect(
            self.surface,
            (20, 30, 40),
            power_section_rect,
            radius=10,
            alpha=180,
            border_width=1,
            border_color=accent_color
        )
        
        # Power label with glow
        power_label = self.fonts['normal'].render("Sniper Power", True, accent_color)
        power_label_glow = self.fonts['normal'].render("Sniper Power", True, glow_color)
        power_label_rect = power_label.get_rect(centerx=power_section_rect.centerx, top=power_section_rect.top + 8)
        
        self.surface.blit(power_label_glow, (power_label_rect.x + 1, power_label_rect.y + 1))
        self.surface.blit(power_label, power_label_rect)
        
        # Power text with glow effect
        power_text = self.fonts['big'].render(player.sniper_type.special_power, True, accent_color)
        power_glow = self.fonts['big'].render(player.sniper_type.special_power, True, glow_color)
        power_rect = power_text.get_rect(centerx=power_section_rect.centerx, bottom=power_section_rect.bottom - 8)
        
        self.surface.blit(power_glow, (power_rect.x + 1, power_rect.y + 1))
        self.surface.blit(power_text, power_rect)

        # END TURN BUTTON - make it hexagonal for sci-fi look
        end_turn_rect = self.draw_hexagonal_button(
            self.surface,
            center_pos=(const.SCREEN_WIDTH - button_width//2 - 40, panel_top + panel_height//2),
            radius=30,
            color=(60, 20, 10),
            border_color=accent_color,
            text="END TURN",
            font=self.fonts['normal'],
            text_color=(220, 180, 100),
            enabled=True
        )

        # Return the courage button rect for interaction
        return courage_button_rect

    def draw_bush_button(self, player: Character, anchor_rect: pygame.Rect) -> pygame.Rect:
        """Draw the bush ability button next to courage button and return its rect."""
        # Button dimensions
        bush_button_size = 34
        x = anchor_rect.right + 20
        y = anchor_rect.y
        
        # Determine if button is enabled
        enabled = player.courage >= const.COURAGE_BUSH_COST
        button_color = (80, 160, 40) if enabled else (40, 50, 40)
        
        # Get player color for consistent styling
        accent_color = player.sniper_type.color if hasattr(player, 'sniper_type') else (220, 180, 100)
        
        # Draw hexagonal button
        bush_rect = self.draw_hexagonal_button(
            self.surface,
            center_pos=(x + bush_button_size//2, y + bush_button_size//2),
            radius=bush_button_size//2,
            color=button_color,
            border_color=accent_color,
            text="B",
            font=self.fonts['normal'],
            text_color=(255, 255, 255),
            enabled=enabled,
            alpha=255 if enabled else 180
        )
        
        # Draw cost text with glow effect if enabled
        cost_color = accent_color if enabled else (120, 120, 120)
        cost_text = self.fonts['normal'].render(str(const.COURAGE_BUSH_COST), True, cost_color)
        cost_rect = cost_text.get_rect(center=(x + bush_button_size//2, y + bush_button_size + 10))
        
        # Add glow if enabled
        if enabled:
            glow_color = (min(255, accent_color[0] + 40),
                         min(255, accent_color[1] + 40),
                         min(255, accent_color[2] + 40))
            cost_glow = self.fonts['normal'].render(str(const.COURAGE_BUSH_COST), True, glow_color)
            self.surface.blit(cost_glow, (cost_rect.x + 1, cost_rect.y + 1))
            
        self.surface.blit(cost_text, cost_rect)
        
        return bush_rect
    
    def draw_enemy_info_box(self, enemy: Character) -> None:
        """Draw a compact, rounded enemy info box above the enemy character."""
        # Calculate position above the enemy
        info_width = 120  # Reduced width for more compact display
        info_height = 70  # Increased height slightly to fit courage bar
        
        # Convert grid coordinates to pixel coordinates
        enemy_center_x = enemy.x * const.GRID_SIZE + const.GRID_SIZE // 2
        enemy_center_y = enemy.y * const.GRID_SIZE + const.GRID_SIZE // 2
        
        # Position box above enemy with appropriate offset
        x = enemy_center_x - info_width // 2
        y = enemy_center_y - info_height - 20
        
        # Keep box on screen
        x = max(10, min(x, const.SCREEN_WIDTH - info_width - 10))
        y = max(45, min(y, const.SCREEN_HEIGHT - info_height - 10))
        
        # Draw the holographic info panel with glowing effect
        # First add a subtle glow effect
        glow_rect = pygame.Rect(x - 4, y - 4, info_width + 8, info_height + 8)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        for i in range(3):
            alpha = 60 - i * 20  # Fade out
            size_increase = i * 2
            inner_rect = pygame.Rect(size_increase, size_increase, 
                                    glow_rect.width - size_increase * 2,
                                    glow_rect.height - size_increase * 2)
            pygame.draw.rect(glow_surf, (180, 120, 60, alpha), inner_rect, border_radius=12)
        self.surface.blit(glow_surf, glow_rect)
        
        # Draw main panel with rounded corners
        self.draw_rounded_rect(
            self.surface,
            (10, 10, 25),  # Very dark space blue
            pygame.Rect(x, y, info_width, info_height),
            radius=10,
            alpha=220,
            border_width=1,
            border_color=(220, 180, 100)  # Gold border
        )
        
        # Add a scanline effect for high-tech feel
        for line_y in range(y, y + info_height, 4):
            line_rect = pygame.Rect(x + 4, line_y, info_width - 8, 1)
            pygame.draw.rect(self.surface, (220, 180, 100, 15), line_rect)
        
        # Use a smaller font for more compact display
        small_font = pygame.font.SysFont(None, 20)
        
        # Enemy name with subtle glow
        name = enemy.sniper_type.name if hasattr(enemy, 'sniper_type') else "Enemy"
        name_glow = small_font.render(name, True, (255, 220, 150))
        name_text = small_font.render(name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + info_width // 2, y + 12))
        self.surface.blit(name_glow, (name_rect.x + 1, name_rect.y + 1))
        self.surface.blit(name_text, name_rect)
        
        # Health bar - futuristic energy style
        health_bar_width = 100
        health_bar_height = 10
        health_rect = pygame.Rect(
            x + (info_width - health_bar_width) // 2, 
            y + 25,
            health_bar_width, 
            health_bar_height
        )
        
        # Draw health bar with energy segments
        self.draw_energy_bar(
            self.surface,
            health_rect,
            enemy.health,
            100,  # Max health
            (220, 60, 60),  # Red foreground
            (40, 10, 10),   # Dark red background
            (180, 60, 60),  # Border color
            segments=5,     # Number of segments
            glow=True,
            text=f"{int(enemy.health)}/100",
            text_color=(255, 255, 255),
            font=small_font
        )
        
        # Courage bar - futuristic energy style
        courage_bar_width = 100
        courage_bar_height = 10
        courage_rect = pygame.Rect(
            x + (info_width - courage_bar_width) // 2, 
            y + 42,
            courage_bar_width, 
            courage_bar_height
        )
        
        # Draw courage bar with energy segments
        self.draw_energy_bar(
            self.surface,
            courage_rect,
            enemy.courage,
            const.COURAGE_MAX,
            (80, 120, 220),  # Blue foreground
            (20, 30, 60),    # Dark blue background
            (60, 100, 200),  # Border color
            segments=4,      # Number of segments
            glow=True,
            text=f"{int(enemy.courage)}/{const.COURAGE_MAX}",
            text_color=(255, 255, 255),
            font=small_font
        )
        
        # Special ability - with tech style
        ability_text = enemy.sniper_type.special_power if hasattr(enemy.sniper_type, 'special_power') else "Bouncing Shot"
        ability_surf = small_font.render(ability_text, True, (220, 180, 100))
        ability_rect = ability_surf.get_rect(center=(x + info_width // 2, y + 58))
        self.surface.blit(ability_surf, ability_rect)
    
    def draw_countdown(self, seconds: int) -> None:
        """Draw a round transition countdown in the center of the screen."""
        # Create a semi-transparent overlay with radial gradient effect
        overlay = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Create subtle radial gradient
        center = (const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
        max_radius = max(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        
        # Draw gradient circles from outside in
        for radius in range(max_radius, 0, -40):
            alpha = 180 - min(180, int(radius * 0.2))
            pygame.draw.circle(overlay, (0, 0, 20, alpha), center, radius)
            
        # Add subtle tech pattern - concentric circles
        for radius in range(50, max_radius, 80):
            pygame.draw.circle(overlay, (80, 120, 200, 15), center, radius, 2)
            
        # Add horizontal scan lines across the screen
        for y in range(0, const.SCREEN_HEIGHT, 4):
            # Vary opacity based on distance from center for a more dynamic effect
            dist_from_center = abs(y - center[1])
            alpha = max(5, 20 - int(dist_from_center / 10))
            pygame.draw.line(overlay, (100, 150, 250, alpha), (0, y), (const.SCREEN_WIDTH, y), 1)
            
        self.surface.blit(overlay, (0, 0))
        
        # Create a glowing halo around the round number
        glow_radius = 120
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for i in range(5):
            alpha = 50 - i * 10
            pygame.draw.circle(glow_surf, (80, 120, 200, alpha), (glow_radius, glow_radius), glow_radius - i * 10)
        
        # Position the glow at the center of the screen
        glow_pos = (center[0] - glow_radius, center[1] - glow_radius - 20)
        self.surface.blit(glow_surf, glow_pos)
        
        # Draw the round number with glow effect
        round_text = f"ROUND {seconds}"
        # Create glow layer
        round_glow = self.fonts['huge'].render(round_text, True, (100, 180, 255))
        round_surf = self.fonts['huge'].render(round_text, True, (220, 230, 255))
        round_rect = round_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2 - 20))
        
        # Draw multiple glow layers for stronger effect
        for offset in [3, 2, 1]:
            self.surface.blit(round_glow, (round_rect.x - offset, round_rect.y))
            self.surface.blit(round_glow, (round_rect.x + offset, round_rect.y))
            self.surface.blit(round_glow, (round_rect.x, round_rect.y - offset))
            self.surface.blit(round_glow, (round_rect.x, round_rect.y + offset))
            
        # Draw the main text on top
        self.surface.blit(round_surf, round_rect)
        
        # Create a hexagonal frame around the round number for tech style
        hex_radius = 160
        hex_points = []
        for i in range(6):
            angle_rad = 2 * math.pi / 6 * i + math.pi / 6
            x = center[0] + hex_radius * math.cos(angle_rad)
            y = center[1] + hex_radius * math.sin(angle_rad) - 20  # Adjust to match round text position
            hex_points.append((x, y))
            
        # Draw the hexagon with a glowing effect
        pygame.draw.polygon(self.surface, (80, 120, 200, 30), hex_points)
        pygame.draw.polygon(self.surface, (100, 180, 255), hex_points, 2)
        
        # Draw a smaller instruction text below with glow effect
        instruction_text = "Get ready for next round..."
        instruction_glow = self.fonts['big'].render(instruction_text, True, (100, 180, 255))
        instruction_surf = self.fonts['big'].render(instruction_text, True, (220, 230, 255))
        instruction_rect = instruction_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2 + 70))
        
        # Add glow effect
        self.surface.blit(instruction_glow, (instruction_rect.x + 1, instruction_rect.y + 1))
        self.surface.blit(instruction_surf, instruction_rect)
    
    def draw_enemy_with_info(self, enemy: Character) -> None:
        """Draw the enemy info box, then the enemy sprite on top to avoid hiding the character."""
        self.draw_enemy_info_box(enemy)
        # Draw the enemy sprite on top of the info box
        enemy.draw(self.surface)
    
    def draw_bush_arrow(self, x: int, y: int, target: Tuple[int, int]) -> None:
        """Draw an arrow indicating bush placement direction to the target grid cell and show tree image preview."""
        # Compute start and end positions in pixels (center of grid)
        start_pos = (x * const.GRID_SIZE + const.GRID_SIZE // 2,
                     y * const.GRID_SIZE + const.GRID_SIZE // 2)
        end_pos = (target[0] * const.GRID_SIZE + const.GRID_SIZE // 2,
                   target[1] * const.GRID_SIZE + const.GRID_SIZE // 2)
        
        # Draw line in a space-themed color
        arrow_color = (80, 200, 255)  # Cyan-like preview
        pygame.draw.line(self.surface, arrow_color, start_pos, end_pos, 3)
        
        # Draw arrowhead
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max(0.01, (dx**2 + dy**2)**0.5)
        ux, uy = dx/length, dy/length
        size = 12
        left = (end_pos[0] - ux * size - uy * size/2, end_pos[1] - uy * size + ux * size/2)
        right = (end_pos[0] - ux * size + uy * size/2, end_pos[1] - uy * size - ux * size/2)
        pygame.draw.polygon(self.surface, arrow_color, [end_pos, left, right])
        
        # Draw tree preview at the target position
        if self.tree_image:
            # Calculate position to center the tree in the target grid cell
            tree_rect = self.tree_image.get_rect()
            tree_pos = (target[0] * const.GRID_SIZE + (const.GRID_SIZE - tree_rect.width) // 2,
                        target[1] * const.GRID_SIZE + (const.GRID_SIZE - tree_rect.height) // 2)
            
            # Draw with semi-transparency for preview effect
            preview_image = self.tree_image.copy()
            preview_image.set_alpha(150)  # 150/255 opacity
            self.surface.blit(preview_image, tree_pos)