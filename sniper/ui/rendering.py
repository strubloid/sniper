"""
UI Rendering module for the Sniper Game.
"""
import pygame
import random
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
        
        # Draw select button if character is selected
        if selected:
            select_button_rect = pygame.Rect(
                const.SCREEN_WIDTH // 2 - 150,
                const.SCREEN_HEIGHT - 100,
                300,
                70
            )
            pygame.draw.rect(self.surface, (200, 200, 200), select_button_rect)
            pygame.draw.rect(self.surface, (50, 50, 50), select_button_rect, 2)
            
            button_text = self.fonts['normal'].render(f"Select {selected.name}", True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT - 65))
            self.surface.blit(button_text, button_text_rect)
            
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
        # Header background - full width bar at top
        header_rect = pygame.Rect(0, 0, const.SCREEN_WIDTH, 40)
        
        # Use player's character color for HUD when it's player's turn,
        # or red when it's enemy's turn
        if player_turn:
            # Get player's color from their sniper type
            player_color = player.sniper_type.color
            # Create a darker version of the player's color for the background
            background_color = (
                max(0, player_color[0] * 0.3),  # R
                max(0, player_color[1] * 0.3),  # G
                max(0, player_color[2] * 0.3)   # B
            )
            header_text_color = player_color
        else:
            # Enemy's turn - use red theme
            background_color = (50, 10, 10)  # Dark red background
            header_text_color = const.RED
        
        pygame.draw.rect(self.surface, background_color, header_rect)
        pygame.draw.rect(self.surface, header_text_color, header_rect, 2)  # Border matching text color
        
        # Turn text
        current_player = player if player_turn else "Enemy"
        name = player.sniper_type.name if player_turn else "Enemy"
        header_text = f"{name}'s Turn"
        text_surf = self.fonts['big'].render(header_text, True, header_text_color)
        text_rect = text_surf.get_rect(center=(const.SCREEN_WIDTH // 2, 20))
        self.surface.blit(text_surf, text_rect)
        
        # Show moves and shots remaining
        if player_turn:
            stats_text = f"Moves: {player.moves_left} | Shots: {player.shots_left}"
            stats_surf = self.fonts['normal'].render(stats_text, True, header_text_color)
            stats_rect = stats_surf.get_rect(center=(const.SCREEN_WIDTH // 2, 50))
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
                max(0, player_color[0] * 0.2 + 15),  # R
                max(0, player_color[1] * 0.2 + 15),  # G
                max(0, player_color[2] * 0.2 + 15)   # B
            )
            panel_border_color = player.sniper_type.color
        else:
            # Enemy's turn - use red theme
            panel_bg_color = (40, 15, 15)  # Dark red background
            panel_border_color = const.RED
            
        # Draw the panel with appropriate background color
        pygame.draw.rect(self.surface, panel_bg_color, main_panel)
        pygame.draw.rect(self.surface, panel_border_color, main_panel, 2)  # Border using character color

        # LEFT SECTION - Player portrait and stats
        portrait_size = 80
        portrait_rect = pygame.Rect(10, panel_top + 10, portrait_size, portrait_size)
        pygame.draw.rect(self.surface, (60, 60, 80), portrait_rect)
        pygame.draw.rect(self.surface, panel_border_color, portrait_rect, 2)  # Border using character color

        # Display player portrait if available
        if hasattr(player, 'sniper_type') and hasattr(player.sniper_type, 'sprite') and player.sniper_type.sprite:
            scaled_sprite = pygame.transform.scale(player.sniper_type.sprite, (portrait_size - 10, portrait_size - 10))
            self.surface.blit(scaled_sprite, (portrait_rect.x + 5, portrait_rect.y + 5))

        # Player name just right of the portrait
        stats_x = portrait_rect.right + 20
        name_text = self.fonts['big'].render(player.sniper_type.name, True, panel_border_color)
        self.surface.blit(name_text, (stats_x, panel_top + 15))

        # Health/XP bar - red bar with clear 100/100 styling
        health_width = 150
        health_rect = pygame.Rect(stats_x, panel_top + 50, health_width, 15)
        pygame.draw.rect(self.surface, (150, 30, 30), health_rect)  # Red background

        # Calculate actual health width
        current_health_width = int((player.health / 100) * health_width)
        if current_health_width > 0:
            current_health_rect = pygame.Rect(stats_x, panel_top + 50, 
                                             current_health_width, 15)
            pygame.draw.rect(self.surface, (200, 50, 50), current_health_rect)

        # Health text (100/100) below the bar
        health_text = f"{int(player.health)}/100"
        health_surf = self.fonts['normal'].render(health_text, True, panel_border_color)
        self.surface.blit(health_surf, (stats_x, panel_top + 70))

        # COURAGE SECTION
        courage_x = stats_x + 180

        # Draw "Courage:" label
        courage_label = self.fonts['normal'].render("Courage", True, panel_border_color)
        self.surface.blit(courage_label, (courage_x, panel_top + 30))

        # Draw courage bar
        courage_width = 100
        courage_height = 15
        courage_bar_y = panel_top + 50
        courage_bar_rect = pygame.Rect(courage_x, courage_bar_y, courage_width, courage_height)
        pygame.draw.rect(self.surface, (50, 50, 80), courage_bar_rect)  # Dark background

        # Draw current courage level
        current_courage_width = int((player.courage / const.COURAGE_MAX) * courage_width)
        if current_courage_width > 0:
            current_courage_rect = pygame.Rect(courage_x, courage_bar_y, current_courage_width, courage_height)
            pygame.draw.rect(self.surface, (100, 100, 220), current_courage_rect)  # Blue courage bar

        # Display courage value
        courage_value = str(int(player.courage))
        courage_text = self.fonts['normal'].render(f"{courage_value}/{const.COURAGE_MAX}", True, panel_border_color)
        self.surface.blit(courage_text, (courage_x, courage_bar_y + courage_height + 5))

        # Courage Button - circular button to the right of courage bar
        courage_button_size = 30
        courage_button_x = courage_x + courage_width + 20
        # Vertically center button in panel
        courage_button_y = panel_top + (panel_height - courage_button_size) // 2
        courage_button_rect = pygame.Rect(
            courage_button_x, 
            courage_button_y, 
            courage_button_size, 
            courage_button_size
        )

        # Draw button with different appearance based on whether it's usable
        button_enabled = player.courage >= const.COURAGE_BUTTON_COST
        button_color = (100, 100, 220) if button_enabled else (60, 60, 80)  # Blue if enabled, grey if disabled
        pygame.draw.circle(
            self.surface, 
            button_color, 
            (courage_button_x + (courage_button_size // 2), courage_button_y + (courage_button_size // 2)), 
            courage_button_size // 2
        )
        pygame.draw.circle(
            self.surface, 
            panel_border_color, 
            (courage_button_x + (courage_button_size // 2), courage_button_y + (courage_button_size // 2)), 
            courage_button_size // 2,
            2  # 2px width border
        )

        # Draw "+" in the button
        plus_text = self.fonts['normal'].render("+", True, panel_border_color if button_enabled else (120, 120, 120))
        plus_rect = plus_text.get_rect(
            center=(courage_button_x + (courage_button_size // 2), courage_button_y + (courage_button_size // 2))
        )
        self.surface.blit(plus_text, plus_rect)

        # Draw cost tooltip near courage button below the button
        cost_text = self.fonts['normal'].render(f"{const.COURAGE_BUTTON_COST}", True, panel_border_color if button_enabled else (120, 120, 120))
        self.surface.blit(cost_text, (courage_button_x, courage_button_y + courage_button_size + 5))  # cost in courage to use + ability

        # CENTER SECTION - Powers - position next to End Turn button
        # Calculate End Turn left position for alignment
        button_width = 160
        end_turn_left = const.SCREEN_WIDTH - button_width - 40
        # Vertical center of panel
        center_y = panel_top + panel_height // 2
        gap = 20  # gap between power section and End Turn button

        # Sniper Power label above, right-aligned just before End Turn
        header_surf = self.fonts['normal'].render("Sniper Power", True, panel_border_color)
        header_rect = header_surf.get_rect(midright=(end_turn_left - gap, center_y - 14))
        self.surface.blit(header_surf, header_rect)
        
        # Selected Power text below, same right alignment
        power_surf = self.fonts['big'].render(player.sniper_type.special_power, True, panel_border_color)
        power_rect = power_surf.get_rect(midright=(end_turn_left - gap, center_y + 18))
        self.surface.blit(power_surf, power_rect)

        # RIGHT SECTION - Power buttons and End Turn
        # Calculate positions from right to left
        button_height = 40
        end_turn_rect = pygame.Rect(
            const.SCREEN_WIDTH - button_width - 40,  # Right-aligned with 40px margin
            const.SCREEN_HEIGHT - 70,                # Vertically centered in the bottom HUD
            button_width,
            button_height
        )

        # Draw the End Turn button
        pygame.draw.rect(self.surface, (80, 30, 20), end_turn_rect)  # Brown background
        pygame.draw.rect(self.surface, panel_border_color, end_turn_rect, 2)  # Border using character color

        # End Turn text
        end_turn_text = self.fonts['normal'].render("End Turn", True, panel_border_color)
        end_turn_text_rect = end_turn_text.get_rect(center=end_turn_rect.center)
        self.surface.blit(end_turn_text, end_turn_text_rect)

        # Return the courage button rect so we can detect clicks on it
        return courage_button_rect

    def draw_bush_button(self, player: Character, anchor_rect: pygame.Rect) -> pygame.Rect:
        """Draw the bush ability button next to courage button and return its rect."""
        # Button dimensions
        bush_button_size = 30
        x = anchor_rect.right + 20
        y = anchor_rect.y
        bush_rect = pygame.Rect(x, y, bush_button_size, bush_button_size)
        # Enabled if player has enough courage
        enabled = player.courage >= const.COURAGE_BUSH_COST
        button_color = (80, 160, 40) if enabled else (60, 60, 60)
        # Draw circle button
        pygame.draw.circle(self.surface, button_color,
                           (x + bush_button_size//2, y + bush_button_size//2),
                           bush_button_size//2)
        pygame.draw.circle(self.surface, (220, 180, 100),
                           (x + bush_button_size//2, y + bush_button_size//2),
                           bush_button_size//2, 2)
        # Draw 'B' for bush
        letter = self.fonts['normal'].render('B', True, (220, 180, 100) if enabled else (120, 120, 120))
        letter_rect = letter.get_rect(center=(x + bush_button_size//2, y + bush_button_size//2))
        self.surface.blit(letter, letter_rect)
        # Draw cost text
        cost_text = self.fonts['small'] if hasattr(self.fonts, 'small') else self.fonts['normal']
        cost = self.fonts['normal'].render(str(const.COURAGE_BUSH_COST), True,
                                          (220, 180, 100) if enabled else (120, 120, 120))
        self.surface.blit(cost, (x, y + bush_button_size + 5))  # cost in courage to place bush
        return bush_rect
    
    def draw_enemy_info_box(self, enemy: Character) -> None:
        """Draw a compact, rounded enemy info box above the enemy character."""
        # Calculate position above the enemy
        info_width = 120  # Reduced width for more compact display
        info_height = 70  # Increased height slightly to fit courage bar
        margin = 4  # Adding a 4px margin as requested
        
        # Convert grid coordinates to pixel coordinates
        enemy_center_x = enemy.x * const.GRID_SIZE + const.GRID_SIZE // 2
        enemy_center_y = enemy.y * const.GRID_SIZE + const.GRID_SIZE // 2
        
        # Position box above enemy with appropriate offset, without the connecting line
        x = enemy_center_x - info_width // 2
        y = enemy_center_y - info_height - 20  # More space above character to remove the need for connecting line
        
        # Keep box on screen with proper margins
        x = max(10, min(x, const.SCREEN_WIDTH - info_width - 10))
        y = max(45, min(y, const.SCREEN_HEIGHT - info_height - 10))
        
        # Create a semi-transparent background with rounded corners and margin
        info_bg = pygame.Surface((info_width + margin*2, info_height + margin*2), pygame.SRCALPHA)
        
        # First, draw a rounded rectangle on this surface
        radius = 10  # Corner radius
        rect = pygame.Rect(margin, margin, info_width, info_height)
        
        # Draw the semi-transparent background with rounded corners
        pygame.draw.rect(info_bg, (10, 10, 20, 210), rect, border_radius=radius)
        
        # Draw a gold border with rounded corners
        pygame.draw.rect(info_bg, (220, 180, 100), rect, 2, border_radius=radius)
        
        # Blit the background to the main surface
        self.surface.blit(info_bg, (x - margin, y - margin))
        
        # Use a smaller font for more compact display
        small_font = pygame.font.SysFont(None, 20)  # Smaller font size
        
        # Enemy name - use actual enemy name if available - now with WHITE color
        name = enemy.sniper_type.name if hasattr(enemy, 'sniper_type') else "Enemy"
        name_text = small_font.render(name, True, (255, 255, 255))  # Changed to WHITE
        name_rect = name_text.get_rect(center=(x + info_width // 2, y + 12))
        self.surface.blit(name_text, name_rect)
        
        # Health bar - smaller and more compact
        health_bar_width = 90  # Reduced width
        health_bar_height = 12  # Slightly reduced height for more compact display
        health_bar_rect = pygame.Rect(
            x + (info_width - health_bar_width) // 2, 
            y + 25,  # Adjusted position
            health_bar_width, 
            health_bar_height
        )
        pygame.draw.rect(self.surface, (150, 30, 30), health_bar_rect)  # Red background
        
        # Calculate actual health
        max_health = 100  # Characters are initialized with 100 health
        current_health_width = int((enemy.health / max_health) * health_bar_width)
        if current_health_width > 0:
            current_health_rect = pygame.Rect(
                x + (info_width - health_bar_width) // 2, 
                y + 25,
                current_health_width, 
                health_bar_height
            )
            pygame.draw.rect(self.surface, (200, 50, 50), current_health_rect)
        
        # Health text - smaller font and more compact format
        # Now displayed ON TOP of the health bar with WHITE text
        health_text = f"{int(enemy.health)}/{max_health}"
        health_text_surf = small_font.render(health_text, True, (255, 255, 255))  # Changed to WHITE
        health_text_rect = health_text_surf.get_rect(center=(x + info_width // 2, y + 25 + health_bar_height//2))
        self.surface.blit(health_text_surf, health_text_rect)
        
        # Add courage bar - compact format below health bar
        courage_bar_width = 90  # Same width as health bar
        courage_bar_height = 12  # Same height as health bar
        courage_bar_rect = pygame.Rect(
            x + (info_width - courage_bar_width) // 2, 
            y + 40,  # Position below health bar
            courage_bar_width, 
            courage_bar_height
        )
        pygame.draw.rect(self.surface, (50, 50, 80), courage_bar_rect)  # Dark background
        
        # Draw current courage level
        current_courage_width = int((enemy.courage / const.COURAGE_MAX) * courage_bar_width)
        if current_courage_width > 0:
            current_courage_rect = pygame.Rect(
                x + (info_width - courage_bar_width) // 2, 
                y + 40,
                current_courage_width, 
                courage_bar_height
            )
            pygame.draw.rect(self.surface, (100, 100, 220), current_courage_rect)  # Blue courage bar
        
        # Courage text - displayed ON TOP of the courage bar with WHITE text
        courage_text = f"{int(enemy.courage)}/{const.COURAGE_MAX}"
        courage_text_surf = small_font.render(courage_text, True, (255, 255, 255))
        courage_text_rect = courage_text_surf.get_rect(center=(x + info_width // 2, y + 40 + courage_bar_height//2))
        self.surface.blit(courage_text_surf, courage_text_rect)
        
        # Special ability - smaller font with WHITE text - moved down to accommodate courage bar
        ability_text = enemy.sniper_type.special_power if hasattr(enemy.sniper_type, 'special_power') else "Bouncing Shot"
        ability_surf = small_font.render(ability_text, True, (255, 255, 255))
        ability_rect = ability_surf.get_rect(center=(x + info_width // 2, y + 58))
        self.surface.blit(ability_surf, ability_rect)
        
    def draw_countdown(self, seconds: int) -> None:
        """Draw a round transition countdown in the center of the screen."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(const.ROUND_TRANSITION_BG_COLOR)
        self.surface.blit(overlay, (0, 0))
        
        # Draw the round number
        round_text = f"Round {seconds}"
        round_surf = self.fonts['huge'].render(round_text, True, const.ROUND_TRANSITION_TEXT_COLOR)
        round_rect = round_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2))
        self.surface.blit(round_surf, round_rect)
        
        # Draw a smaller instruction text below
        instruction_text = "Get ready..."
        instruction_surf = self.fonts['big'].render(instruction_text, True, const.ROUND_TRANSITION_TEXT_COLOR)
        instruction_rect = instruction_surf.get_rect(center=(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2 + 70))
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