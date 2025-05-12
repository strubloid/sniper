"""
UI rendering module for Sniper Game.
This module handles drawing the game's user interface components with enhanced styling.
"""
import os
import pygame
from typing import List, Tuple, Optional, Dict, Any

import constants as const
from models import Button, Character, Projectile, SniperType


class UI:
    """Handles rendering of all UI elements in the game."""
    
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """Initialize UI renderer with screen and fonts."""
        self.screen = screen
        self.fonts = fonts
        
        # Load UI assets if available
        self.ui_assets = {}
        try:
            # Add UI assets here if you have them
            pass
        except pygame.error as e:
            print(f"Could not load UI assets: {e}")
    
    def draw_grid(self) -> None:
        """Draw the game grid with a slight gradient effect."""
        # Draw a subtle gradient background for the grid
        for y in range(0, const.SCREEN_HEIGHT, 4):
            color_value = max(10, min(50, 30 + (y // 10)))
            pygame.draw.rect(self.screen, (color_value, color_value, color_value + 10), 
                           (0, y, const.SCREEN_WIDTH, 4))
        
        # Draw grid lines with transparency
        grid_color = (80, 80, 100, 128)
        grid_surface = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for x in range(0, const.SCREEN_WIDTH, const.GRID_SIZE):
            pygame.draw.line(grid_surface, grid_color, (x, 0), (x, const.SCREEN_HEIGHT))
        for y in range(0, const.SCREEN_HEIGHT, const.GRID_SIZE):
            pygame.draw.line(grid_surface, grid_color, (0, y), (const.SCREEN_WIDTH, y))
            
        self.screen.blit(grid_surface, (0, 0))
    
    def draw_menu(self) -> List[Tuple[pygame.Rect, str]]:
        """Draw the game menu with enhanced styling."""
        # Create gradient background
        for y in range(0, const.SCREEN_HEIGHT, 5):
            color_val = int(20 + (y / const.SCREEN_HEIGHT * 40))
            pygame.draw.rect(self.screen, (color_val, color_val, color_val + 20), 
                           (0, y, const.SCREEN_WIDTH, 5))
        
        # Add fancy title panel
        title_panel = pygame.Surface((600, 120), pygame.SRCALPHA)
        pygame.draw.rect(title_panel, (0, 0, 0, 180), (0, 0, 600, 120), border_radius=15)
        pygame.draw.rect(title_panel, (255, 215, 0, 200), (0, 0, 600, 120), 3, border_radius=15)
        self.screen.blit(title_panel, (180, 80))
        
        # Title with shadow effect
        title_shadow = self.fonts['big'].render("SNIPER GAME", True, (30, 30, 30))
        title = self.fonts['big'].render("SNIPER GAME", True, (255, 220, 0))
        self.screen.blit(title_shadow, (302, 102))
        self.screen.blit(title, (300, 100))
        
        # Add subtitle
        subtitle = self.fonts['normal'].render("TACTICAL ELIMINATION", True, (220, 220, 220))
        self.screen.blit(subtitle, (const.SCREEN_WIDTH//2 - subtitle.get_width()//2, 155))
        
        # Draw menu options with enhanced styling
        menu_options = ["Play", "Scoreboard", "Quit"]
        button_rects = []
        
        for i, option in enumerate(menu_options):
            button_y = 250 + i * (const.BUTTON_HEIGHT + const.BUTTON_SPACING)
            button_rect = pygame.Rect(
                const.SCREEN_WIDTH//2 - const.BUTTON_WIDTH//2, 
                button_y, 
                const.BUTTON_WIDTH, 
                const.BUTTON_HEIGHT
            )
            
            # Draw button with gradient and rounded corners
            button_surface = pygame.Surface((const.BUTTON_WIDTH, const.BUTTON_HEIGHT), pygame.SRCALPHA)
            
            # Button background with alpha
            pygame.draw.rect(button_surface, (40, 40, 60, 200), 
                           (0, 0, const.BUTTON_WIDTH, const.BUTTON_HEIGHT), border_radius=10)
            
            # Button border glow
            pygame.draw.rect(button_surface, (100, 100, 200, 128), 
                           (0, 0, const.BUTTON_WIDTH, const.BUTTON_HEIGHT), 2, border_radius=10)
            
            self.screen.blit(button_surface, button_rect)
            
            # Text with shadow
            text_shadow = self.fonts['normal'].render(option, True, (0, 0, 0))
            text = self.fonts['normal'].render(option, True, (220, 220, 255))
            
            text_x = button_rect.x + (button_rect.width - text.get_width()) // 2
            text_y = button_rect.y + (button_rect.height - text.get_height()) // 2
            
            self.screen.blit(text_shadow, (text_x + 1, text_y + 1))
            self.screen.blit(text, (text_x, text_y))
            
            button_rects.append((button_rect, option))
        
        try:
            banner = pygame.image.load(os.path.join(const.ASSETS_DIR, "title_characters.png"))
            self.screen.blit(banner, (320, 170))
        except pygame.error:
            print("Warning: Could not load title banner image")
        
        return button_rects
    
    def draw_scoreboard(self) -> None:
        """Draw the scoreboard screen with styled panels."""
        # Create gradient background
        for y in range(0, const.SCREEN_HEIGHT, 5):
            color_val = int(20 + (y / const.SCREEN_HEIGHT * 40))
            pygame.draw.rect(self.screen, (color_val, color_val, color_val + 20), 
                           (0, y, const.SCREEN_WIDTH, 5))
        
        # Create panel
        panel = pygame.Surface((600, 400), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 30, 200), (0, 0, 600, 400), border_radius=15)
        pygame.draw.rect(panel, (100, 100, 200, 200), (0, 0, 600, 400), 2, border_radius=15)
        self.screen.blit(panel, (180, 80))
        
        # Title with shadow effect
        title_shadow = self.fonts['big'].render("SCOREBOARD", True, (30, 30, 30))
        title = self.fonts['big'].render("SCOREBOARD", True, (200, 200, 255))
        self.screen.blit(title_shadow, (302, 102))
        self.screen.blit(title, (300, 100))
        
        # In a real implementation, you'd load scores from a file
        self.screen.blit(
            self.fonts['normal'].render("No scores yet! Play a game to record your score.", True, (200, 200, 255)), 
            (250, 200)
        )
        
        # Return button
        return_text = self.fonts['normal'].render("Press ESC to return to menu", True, (180, 180, 200))
        self.screen.blit(return_text, (300, 400))
    
    def draw_character_select(self, select_stage: str, candidate: Optional[SniperType], 
                              sniper_types: List[SniperType]) -> List[pygame.Rect]:
        """Draw character selection screen with enhanced styling."""
        # Create gradient background
        for y in range(0, const.SCREEN_HEIGHT, 5):
            color_val = int(20 + (y / const.SCREEN_HEIGHT * 40))
            pygame.draw.rect(self.screen, (color_val, color_val, color_val + 20), 
                           (0, y, const.SCREEN_WIDTH, 5))
        
        # Create panel
        main_panel = pygame.Surface((760, 500), pygame.SRCALPHA)
        pygame.draw.rect(main_panel, (20, 20, 40, 220), (0, 0, 760, 500), border_radius=15)
        pygame.draw.rect(main_panel, (100, 100, 180, 200), (0, 0, 760, 500), 2, border_radius=15)
        self.screen.blit(main_panel, (100, 80))
        
        # Draw title with style
        title = "Select Your Character" if select_stage == "player" else "Select AI Opponent"
        title_shadow = self.fonts['big'].render(title, True, (30, 30, 30))
        title_text = self.fonts['big'].render(title, True, (220, 220, 255))
        self.screen.blit(title_shadow, (252, 102))
        self.screen.blit(title_text, (250, 100))
        
        rects = []
        for i, sniper in enumerate(sniper_types):
            rect = pygame.Rect(120, 160 + i * 65, 400, 55)
            
            # Create character panel
            char_panel = pygame.Surface((400, 55), pygame.SRCALPHA)
            
            # Different highlight for selected candidate
            if sniper == candidate:
                pygame.draw.rect(char_panel, (60, 60, 100, 220), (0, 0, 400, 55), border_radius=10)
                pygame.draw.rect(char_panel, (180, 180, 255, 200), (0, 0, 400, 55), 2, border_radius=10)
            else:
                pygame.draw.rect(char_panel, (40, 40, 70, 180), (0, 0, 400, 55), border_radius=10)
                pygame.draw.rect(char_panel, (100, 100, 150, 150), (0, 0, 400, 55), 1, border_radius=10)
            
            self.screen.blit(char_panel, rect)
            
            # Character info with shadow
            text_shadow = self.fonts['normal'].render(f"{sniper.name}: {sniper.description}", True, (0, 0, 0))
            text = self.fonts['normal'].render(f"{sniper.name}: {sniper.description}", True, (220, 220, 255))
            self.screen.blit(text_shadow, (rect.x + 11, rect.y + 16))
            self.screen.blit(text, (rect.x + 10, rect.y + 15))
            
            # Display sprite
            sprite = pygame.transform.scale(sniper.sprite, (40, 40))
            self.screen.blit(sprite, (rect.x + 340, rect.y + 7))
            rects.append(rect)

        if candidate:
            # Create detailed info panel
            detail_panel = pygame.Surface((600, 120), pygame.SRCALPHA)
            pygame.draw.rect(detail_panel, (40, 40, 80, 200), (0, 0, 600, 120), border_radius=10)
            pygame.draw.rect(detail_panel, (140, 140, 200, 200), (0, 0, 600, 120), 2, border_radius=10)
            self.screen.blit(detail_panel, (120, 400))
            
            # Character info with stats bars
            info = [
                f"Name: {candidate.name}",
                f"Power: {candidate.power}",
                f"Move Limit: {candidate.move_limit}"
            ]
            for i, line in enumerate(info):
                shadow = self.fonts['normal'].render(line, True, (0, 0, 0))
                text = self.fonts['normal'].render(line, True, (220, 220, 255))
                self.screen.blit(shadow, (131, 411 + i * 30))
                self.screen.blit(text, (130, 410 + i * 30))
                
            # Add stat bars for move_limit
            pygame.draw.rect(self.screen, (60, 60, 100), (240, 470, 100, 15))
            pygame.draw.rect(self.screen, (100, 100, 255), (240, 470, candidate.move_limit * 25, 15))
                
        return rects
    
    def draw_confirmation_popup(self) -> Tuple[pygame.Rect, pygame.Rect]:
        """Draw confirmation popup with Yes/No buttons."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Create popup panel
        popup = pygame.Surface((450, 200), pygame.SRCALPHA)
        pygame.draw.rect(popup, (40, 40, 70, 230), (0, 0, 450, 200), border_radius=15)
        pygame.draw.rect(popup, (150, 150, 255, 200), (0, 0, 450, 200), 3, border_radius=15)
        self.screen.blit(popup, (const.SCREEN_WIDTH//2 - 225, const.SCREEN_HEIGHT//2 - 120))
        
        # Title with shadow
        txt_shadow = self.fonts['big'].render("Are you sure?", True, (20, 20, 20))
        txt = self.fonts['big'].render("Are you sure?", True, (220, 220, 30))
        self.screen.blit(txt_shadow, (const.SCREEN_WIDTH//2 - txt.get_width()//2 + 2, 252))
        self.screen.blit(txt, (const.SCREEN_WIDTH//2 - txt.get_width()//2, 250))
        
        # Yes button
        yes_rect = pygame.Rect(const.SCREEN_WIDTH//2 - 130, 320, 100, 40)
        yes_surface = pygame.Surface((100, 40), pygame.SRCALPHA)
        pygame.draw.rect(yes_surface, (0, 80, 0, 220), (0, 0, 100, 40), border_radius=8)
        pygame.draw.rect(yes_surface, (100, 255, 100, 200), (0, 0, 100, 40), 2, border_radius=8)
        self.screen.blit(yes_surface, yes_rect)
        
        # No button
        no_rect = pygame.Rect(const.SCREEN_WIDTH//2 + 30, 320, 100, 40)
        no_surface = pygame.Surface((100, 40), pygame.SRCALPHA)
        pygame.draw.rect(no_surface, (80, 0, 0, 220), (0, 0, 100, 40), border_radius=8)
        pygame.draw.rect(no_surface, (255, 100, 100, 200), (0, 0, 100, 40), 2, border_radius=8)
        self.screen.blit(no_surface, no_rect)
        
        # Button text
        yes_txt = self.fonts['normal'].render("Yes", True, (220, 255, 220))
        no_txt = self.fonts['normal'].render("No", True, (255, 220, 220))
        self.screen.blit(yes_txt, (yes_rect.x + 35, yes_rect.y + 10))
        self.screen.blit(no_txt, (no_rect.x + 40, no_rect.y + 10))
        
        return yes_rect, no_rect
    
    def draw_turn_info(self, player: Character) -> None:
        """Draw turn information display."""
        turn_panel = pygame.Surface((400, 40), pygame.SRCALPHA)
        pygame.draw.rect(turn_panel, (20, 20, 40, 200), (0, 0, 400, 40), border_radius=10)
        pygame.draw.rect(turn_panel, (150, 150, 200, 200), (0, 0, 400, 40), 2, border_radius=10)
        self.screen.blit(turn_panel, (10, 10))
        
        # Text with shadow
        txt = f"{player.sniper_type.name}'s Turn — Moves: {player.moves_left} | Shots: {player.shots_left}"
        txt_shadow = self.fonts['normal'].render(txt, True, (0, 0, 0))
        text = self.fonts['normal'].render(txt, True, (220, 220, 30))
        self.screen.blit(txt_shadow, (21, 21))
        self.screen.blit(text, (20, 20))
    
    def draw_instructions(self) -> None:
        """Draw game instructions."""
        instruction_panel = pygame.Surface((640, 40), pygame.SRCALPHA)
        pygame.draw.rect(instruction_panel, (20, 20, 40, 180), (0, 0, 640, 40), border_radius=10)
        pygame.draw.rect(instruction_panel, (100, 100, 150, 150), (0, 0, 640, 40), 1, border_radius=10)
        self.screen.blit(instruction_panel, (10, const.SCREEN_HEIGHT - 50))
        
        # Text with shadow
        text = "Click your character to move | Press SPACE to shoot | Click a tile to fire"
        text_shadow = self.fonts['normal'].render(text, True, (0, 0, 0))
        instruction_text = self.fonts['normal'].render(text, True, (180, 180, 220))
        self.screen.blit(text_shadow, (21, const.SCREEN_HEIGHT - 41))
        self.screen.blit(instruction_text, (20, const.SCREEN_HEIGHT - 40))
    
    def draw_hud_grid(self, player: Character, enemy: Character) -> None:
        """Draw HUD with player and enemy information in a fancy panel."""
        hud_x, hud_y = 10, const.SCREEN_HEIGHT - 150
        spacing = const.HUD_SPACING
        
        # Create HUD panel
        hud_panel = pygame.Surface((300, 90), pygame.SRCALPHA)
        pygame.draw.rect(hud_panel, (20, 20, 40, 200), (0, 0, 300, 90), border_radius=10)
        pygame.draw.rect(hud_panel, (100, 100, 180, 200), (0, 0, 300, 90), 2, border_radius=10)
        self.screen.blit(hud_panel, (hud_x, hud_y))

        # Player health with decorative elements
        pygame.draw.rect(self.screen, (40, 40, 40), (hud_x + 10, hud_y + 10, 200, 20), border_radius=5)
        player_health_ratio = max(0, min(1, player.health / player.max_health))
        
        # Health gradient
        if player_health_ratio > 0.6:
            health_color = (0, 200, 0)  # Green
        elif player_health_ratio > 0.3:
            health_color = (200, 200, 0)  # Yellow
        else:
            health_color = (200, 0, 0)  # Red
            
        pygame.draw.rect(self.screen, health_color, 
                      (hud_x + 10, hud_y + 10, int(200 * player_health_ratio), 20), border_radius=5)
                      
        # Health text with shadow
        hp_text = f"Player HP: {player.health}"
        shadow = self.fonts['normal'].render(hp_text, True, (0, 0, 0))
        text = self.fonts['normal'].render(hp_text, True, (220, 220, 220))
        self.screen.blit(shadow, (hud_x + 221, hud_y + 11))
        self.screen.blit(text, (hud_x + 220, hud_y + 10))

        # Enemy health
        pygame.draw.rect(self.screen, (40, 40, 40), (hud_x + 10, hud_y + 40, 200, 20), border_radius=5)
        enemy_health_ratio = max(0, min(1, enemy.health / enemy.max_health))
        
        # Health gradient for enemy
        if enemy_health_ratio > 0.6:
            enemy_health_color = (0, 200, 0)  # Green
        elif enemy_health_ratio > 0.3:
            enemy_health_color = (200, 200, 0)  # Yellow
        else:
            enemy_health_color = (200, 0, 0)  # Red
            
        pygame.draw.rect(self.screen, enemy_health_color, 
                      (hud_x + 10, hud_y + 40, int(200 * enemy_health_ratio), 20), border_radius=5)
                      
        # Enemy health text with shadow
        enemy_hp_text = f"Enemy HP: {enemy.health}"
        shadow = self.fonts['normal'].render(enemy_hp_text, True, (0, 0, 0))
        text = self.fonts['normal'].render(enemy_hp_text, True, (220, 220, 220))
        self.screen.blit(shadow, (hud_x + 221, hud_y + 41))
        self.screen.blit(text, (hud_x + 220, hud_y + 40))

        # Player stats panel
        stats_panel = pygame.Surface((200, 30), pygame.SRCALPHA)
        pygame.draw.rect(stats_panel, (30, 30, 50, 200), (0, 0, 200, 30), border_radius=5)
        self.screen.blit(stats_panel, (hud_x + 350, hud_y + 10))
        
        # Player stats text
        moves_text = f"Moves: {player.moves_left}"
        shots_text = f"Shots: {player.shots_left}"
        
        moves = self.fonts['normal'].render(moves_text, True, (180, 180, 220))
        shots = self.fonts['normal'].render(shots_text, True, (180, 180, 220))
        
        self.screen.blit(moves, (hud_x + 360, hud_y + 15))
        self.screen.blit(shots, (hud_x + 460, hud_y + 15))
    
    def draw_projectiles(self, projectiles: List[Projectile]) -> None:
        """Draw all projectiles with glow effect."""
        for p in projectiles:
            # Draw glow
            glow_surface = pygame.Surface((const.PROJECTILE_RADIUS*4, const.PROJECTILE_RADIUS*4), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (p.color[0], p.color[1], p.color[2], 100),
                (const.PROJECTILE_RADIUS*2, const.PROJECTILE_RADIUS*2),
                const.PROJECTILE_RADIUS*2
            )
            self.screen.blit(
                glow_surface,
                (p.x * const.GRID_SIZE + const.GRID_SIZE // 2 - const.PROJECTILE_RADIUS*2,
                 p.y * const.GRID_SIZE + const.GRID_SIZE // 2 - const.PROJECTILE_RADIUS*2)
            )
            
            # Draw main projectile
            pygame.draw.circle(
                self.screen, 
                p.color, 
                (p.x * const.GRID_SIZE + const.GRID_SIZE // 2, p.y * const.GRID_SIZE + const.GRID_SIZE // 2), 
                const.PROJECTILE_RADIUS
            )
            
            # Draw highlight
            pygame.draw.circle(
                self.screen, 
                (255, 255, 255), 
                (p.x * const.GRID_SIZE + const.GRID_SIZE // 2 - 1, p.y * const.GRID_SIZE + const.GRID_SIZE // 2 - 1), 
                const.PROJECTILE_RADIUS // 2
            )
    
    def draw_turn_indicator(self, is_player_turn: bool) -> None:
        """Draw the current turn indicator with enhanced styling."""
        # Create panel
        indicator_panel = pygame.Surface((200, 50), pygame.SRCALPHA)
        
        if is_player_turn:
            panel_color = (0, 60, 0, 200)
            border_color = (0, 200, 0, 200)
            text_color = (180, 255, 180)
            text = "YOUR TURN"
        else:
            panel_color = (60, 0, 0, 200)
            border_color = (200, 0, 0, 200)
            text_color = (255, 180, 180)
            text = "AI'S TURN"
            
        pygame.draw.rect(indicator_panel, panel_color, (0, 0, 200, 50), border_radius=10)
        pygame.draw.rect(indicator_panel, border_color, (0, 0, 200, 50), 2, border_radius=10)
        
        # Draw the panel
        self.screen.blit(indicator_panel, (const.SCREEN_WIDTH // 2 - 100, 10))
        
        # Draw text with shadow
        shadow = self.fonts['big'].render(text, True, (0, 0, 0))
        turn_text = self.fonts['big'].render(text, True, text_color)
        
        self.screen.blit(shadow, 
                       (const.SCREEN_WIDTH // 2 - turn_text.get_width() // 2 + 1, 21))
        self.screen.blit(turn_text, 
                       (const.SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 20))
    
    def draw_end_turn_button(self) -> Optional[pygame.Rect]:
        """Draw the end turn button with enhanced styling."""
        button_rect = pygame.Rect(const.SCREEN_WIDTH - 150, const.SCREEN_HEIGHT - 80, 120, 40)
        button_surface = pygame.Surface((120, 40), pygame.SRCALPHA)
        
        # Button with gradient
        pygame.draw.rect(button_surface, (60, 10, 10, 220), (0, 0, 120, 40), border_radius=8)
        pygame.draw.rect(button_surface, (200, 60, 60, 200), (0, 0, 120, 40), 2, border_radius=8)
        
        # Draw button
        self.screen.blit(button_surface, button_rect)
        
        # Text with shadow
        shadow = self.fonts['normal'].render("END TURN", True, (0, 0, 0))
        text = self.fonts['normal'].render("END TURN", True, (255, 200, 200))
        self.screen.blit(shadow, (button_rect.x + 21, button_rect.y + 11))
        self.screen.blit(text, (button_rect.x + 20, button_rect.y + 10))
        
        return button_rect
    
    def draw_obstacles(self, obstacles: List[Tuple[int, int]]) -> None:
        """Draw game obstacles with enhanced styling."""
        for x, y in obstacles:
            obstacle_rect = (x * const.GRID_SIZE, y * const.GRID_SIZE, const.GRID_SIZE, const.GRID_SIZE)
            
            # Create obstacle with shadow
            pygame.draw.rect(
                self.screen, 
                (50, 50, 60), 
                (x * const.GRID_SIZE + 2, y * const.GRID_SIZE + 2, const.GRID_SIZE - 2, const.GRID_SIZE - 2)
            )
            
            # Main obstacle
            pygame.draw.rect(
                self.screen, 
                (80, 80, 95), 
                (x * const.GRID_SIZE, y * const.GRID_SIZE, const.GRID_SIZE - 2, const.GRID_SIZE - 2)
            )
            
            # Highlight
            pygame.draw.line(
                self.screen,
                (120, 120, 140),
                (x * const.GRID_SIZE, y * const.GRID_SIZE),
                (x * const.GRID_SIZE + const.GRID_SIZE - 2, y * const.GRID_SIZE)
            )
            pygame.draw.line(
                self.screen,
                (120, 120, 140),
                (x * const.GRID_SIZE, y * const.GRID_SIZE),
                (x * const.GRID_SIZE, y * const.GRID_SIZE + const.GRID_SIZE - 2)
            )
    
    def draw_shooting_arrow(self, player_x: int, player_y: int, mouse_pos: Tuple[int, int]) -> None:
        """Draw an arrow from the player to the mouse position with enhanced styling."""
        player_center = (
            player_x * const.GRID_SIZE + const.GRID_SIZE // 2, 
            player_y * const.GRID_SIZE + const.GRID_SIZE // 2
        )
        
        # Draw trajectory path
        for i in range(4):
            alpha = 150 - i*30
            width = 7 - i*2
            pygame.draw.line(
                self.screen, 
                (255, 255, 0, alpha), 
                player_center, 
                mouse_pos, 
                width
            )
        
        # Main trajectory line
        pygame.draw.line(self.screen, const.YELLOW, player_center, mouse_pos, 2)
        
        # Draw target indicator
        pygame.draw.circle(self.screen, const.RED, mouse_pos, 8, 1)
        pygame.draw.circle(self.screen, const.RED, mouse_pos, 2)
    
    def draw_game_over(self, winner: str) -> None:
        """Draw game over screen with enhanced styling."""
        # Create gradient background
        for y in range(0, const.SCREEN_HEIGHT, 5):
            color_val = int(20 + (y / const.SCREEN_HEIGHT * 40))
            pygame.draw.rect(self.screen, (color_val, color_val//2, color_val//2), 
                           (0, y, const.SCREEN_WIDTH, 5))
                           
        # Create panel
        panel = pygame.Surface((600, 300), pygame.SRCALPHA)
        pygame.draw.rect(panel, (40, 10, 10, 220), (0, 0, 600, 300), border_radius=15)
        pygame.draw.rect(panel, (200, 60, 60, 200), (0, 0, 600, 300), 3, border_radius=15)
        self.screen.blit(panel, (const.SCREEN_WIDTH//2 - 300, const.SCREEN_HEIGHT//2 - 150))
        
        # Title text
        title_shadow = self.fonts['big'].render("GAME OVER", True, (30, 30, 30))
        title = self.fonts['big'].render("GAME OVER", True, (255, 200, 200))
        self.screen.blit(title_shadow, (const.SCREEN_WIDTH//2 - title.get_width()//2 + 2, 202))
        self.screen.blit(title, (const.SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        # Winner text with glow effect
        message_text = f"{winner} Wins!"
        
        for i in range(3):
            offset = 3-i
            shadow = self.fonts['big'].render(message_text, True, (100, 100 + i*50, 100 + i*50))
            self.screen.blit(
                shadow, 
                (const.SCREEN_WIDTH//2 - shadow.get_width()//2 + offset, 
                 const.SCREEN_HEIGHT//2 - shadow.get_height()//2 + offset)
            )
            
        winner_text = self.fonts['big'].render(message_text, True, (255, 255, 100))
        self.screen.blit(
            winner_text, 
            (const.SCREEN_WIDTH//2 - winner_text.get_width()//2, 
             const.SCREEN_HEIGHT//2 - winner_text.get_height()//2)
        )
        
        # Return instruction
        return_text = self.fonts['normal'].render("Press ESC to return to menu", True, (200, 200, 200))
        self.screen.blit(
            return_text,
            (const.SCREEN_WIDTH//2 - return_text.get_width()//2, const.SCREEN_HEIGHT//2 + 80)
        )
    
    def draw_debug_button(self) -> pygame.Rect:
        """Draw debug toggle button with enhanced styling."""
        button_rect = pygame.Rect(const.SCREEN_WIDTH - 100, 20, 80, 30)
        button_surface = pygame.Surface((80, 30), pygame.SRCALPHA)
        
        pygame.draw.rect(button_surface, (40, 40, 70, 200), (0, 0, 80, 30), border_radius=5)
        pygame.draw.rect(button_surface, (100, 100, 180, 200), (0, 0, 80, 30), 1, border_radius=5)
        
        self.screen.blit(button_surface, button_rect)
        
        # Button text
        text = self.fonts['normal'].render("Debug", True, (180, 180, 220))
        self.screen.blit(text, (button_rect.x + 15, button_rect.y + 5))
        
        return button_rect
    
    def draw_debug_info(self, ai_state: str) -> None:
        """Draw debug information panel with enhanced styling."""
        debug_panel = pygame.Surface((200, 100), pygame.SRCALPHA)
        pygame.draw.rect(debug_panel, (0, 0, 0, 180), (0, 0, 200, 100), border_radius=5)
        pygame.draw.rect(debug_panel, (100, 100, 200, 150), (0, 0, 200, 100), 1, border_radius=5)
        self.screen.blit(debug_panel, (20, 20))
        
        debug_title = self.fonts['normal'].render("DEBUG INFO", True, (200, 200, 255))
        self.screen.blit(debug_title, (30, 25))
        
        debug_text = [
            f"AI State: {ai_state}",
            f"AIMING: {ai_state == const.AI_STATE_AIMING}",
            f"SHOOTING: {ai_state == const.AI_STATE_SHOOTING}",
            f"END: {ai_state == const.AI_STATE_END}"
        ]
        
        for i, line in enumerate(debug_text):
            self.screen.blit(self.fonts['normal'].render(line, True, (200, 200, 200)), (30, 50 + i * 20))