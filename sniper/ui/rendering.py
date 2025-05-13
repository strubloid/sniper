"""
UI Rendering module for the Sniper Game.
"""
import pygame
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
        
    def draw_grid(self) -> None:
        """Draw the game grid."""
        for x in range(0, const.SCREEN_WIDTH, const.GRID_SIZE):
            pygame.draw.line(self.surface, const.GRAY, (x, 0), (x, const.SCREEN_HEIGHT))
        for y in range(0, const.SCREEN_HEIGHT, const.GRID_SIZE):
            pygame.draw.line(self.surface, const.GRAY, (0, y), (const.SCREEN_WIDTH, y))
    
    def draw_obstacles(self, obstacles: List[Tuple[int, int]]) -> None:
        """Draw obstacles on the grid."""
        for x, y in obstacles:
            rect = pygame.Rect(
                x * const.GRID_SIZE, 
                y * const.GRID_SIZE,
                const.GRID_SIZE, 
                const.GRID_SIZE
            )
            pygame.draw.rect(self.surface, const.GRAY, rect)
    
    def draw_projectiles(self, projectiles: List[Projectile]) -> None:
        """Draw active projectiles."""
        for p in projectiles:
            center_x = int((p.x + 0.5) * const.GRID_SIZE)
            center_y = int((p.y + 0.5) * const.GRID_SIZE)
            pygame.draw.circle(self.surface, p.color, (center_x, center_y), const.PROJECTILE_RADIUS)
    
    def draw_hud_grid(self, player: Character, enemy: Character) -> None:
        """Draw HUD with player and enemy info."""
        # Player info
        pygame.draw.rect(self.surface, (50, 50, 50), 
                       pygame.Rect(const.HUD_SPACING, const.HUD_SPACING, 200, 60))
        
        # Player health bar
        health_width = int((player.health / 100) * 180)
        pygame.draw.rect(self.surface, (200, 50, 50), 
                       pygame.Rect(const.HUD_SPACING + 10, const.HUD_SPACING + 10, 180, 15))
        if health_width > 0:
            pygame.draw.rect(self.surface, (50, 200, 50), 
                           pygame.Rect(const.HUD_SPACING + 10, const.HUD_SPACING + 10, health_width, 15))
        
        # Player text
        text = f"Player: {player.sniper_type.name} ({player.moves_left} moves, {player.shots_left} shots)"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        self.surface.blit(text_surf, (const.HUD_SPACING + 10, const.HUD_SPACING + 30))
        
        # Enemy info - right side
        pygame.draw.rect(self.surface, (50, 50, 50), 
                       pygame.Rect(const.SCREEN_WIDTH - 200 - const.HUD_SPACING, 
                                 const.HUD_SPACING, 200, 60))
        
        # Enemy health bar
        health_width = int((enemy.health / 100) * 180)
        pygame.draw.rect(self.surface, (200, 50, 50), 
                       pygame.Rect(const.SCREEN_WIDTH - 190 - const.HUD_SPACING, 
                                 const.HUD_SPACING + 10, 180, 15))
        if health_width > 0:
            pygame.draw.rect(self.surface, (50, 200, 50), 
                           pygame.Rect(const.SCREEN_WIDTH - 190 - const.HUD_SPACING, 
                                     const.HUD_SPACING + 10, health_width, 15))
        
        # Enemy text
        text = f"Enemy: {enemy.sniper_type.name}"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        self.surface.blit(text_surf, (const.SCREEN_WIDTH - 190 - const.HUD_SPACING, 
                                    const.HUD_SPACING + 30))
    
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
        button = Button(
            const.SCREEN_WIDTH - const.BUTTON_WIDTH - const.HUD_SPACING,
            const.SCREEN_HEIGHT - const.BUTTON_HEIGHT - const.HUD_SPACING,
            const.BUTTON_WIDTH, 
            const.BUTTON_HEIGHT,
            "End Turn", 
            (200, 100, 100)
        )
        button.draw(self.surface, self.fonts['normal'])
        return button.rect
    
    def draw_debug_button(self) -> pygame.Rect:
        """Draw the debug toggle button."""
        button = Button(
            const.HUD_SPACING,
            const.SCREEN_HEIGHT - const.BUTTON_HEIGHT - const.HUD_SPACING,
            const.BUTTON_WIDTH // 2, 
            const.BUTTON_HEIGHT,
            "Debug", 
            (100, 100, 200)
        )
        button.draw(self.surface, self.fonts['normal'])
        return button.rect
    
    def draw_debug_info(self, ai_state: Optional[str] = None) -> None:
        """Draw debug information."""
        if not ai_state:
            return
            
        text = f"AI State: {ai_state}"
        text_surf = self.fonts['normal'].render(text, True, const.WHITE)
        self.surface.blit(text_surf, (10, const.SCREEN_HEIGHT - 100))
    
    def draw_instructions(self) -> None:
        """Draw game instructions."""
        instructions = [
            "SPACE - Enter shooting mode",
            "Click - Move / Shoot",
            "ESC - Cancel action"
        ]
        
        y_offset = const.SCREEN_HEIGHT - 160
        for instruction in instructions:
            text_surf = self.fonts['normal'].render(instruction, True, const.WHITE)
            self.surface.blit(text_surf, (10, y_offset))
            y_offset += 20
    
    def draw_menu(self) -> List[Tuple[pygame.Rect, str]]:
        """Draw the main menu and return clickable elements."""
        title_text = self.fonts['big'].render("Sniper Game", True, const.WHITE)
        title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 100))
        self.surface.blit(title_text, title_rect)
        
        buttons = []
        y_offset = 200
        
        for option in ["Play", "Scoreboard", "Quit"]:
            button = Button(
                const.SCREEN_WIDTH // 2 - const.BUTTON_WIDTH // 2,
                y_offset,
                const.BUTTON_WIDTH,
                const.BUTTON_HEIGHT,
                option
            )
            button.draw(self.surface, self.fonts['normal'])
            buttons.append((button.rect, option))
            y_offset += const.BUTTON_HEIGHT + const.BUTTON_SPACING
        
        return buttons
    
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
        title = f"Select {'Player' if stage == 'player' else 'Enemy'} Character"
        title_text = self.fonts['big'].render(title, True, const.WHITE)
        title_rect = title_text.get_rect(center=(const.SCREEN_WIDTH // 2, 50))
        self.surface.blit(title_text, title_rect)
        
        clickable_elements = []
        
        # Draw character options
        x_offset = const.SCREEN_WIDTH // 2 - (len(sniper_types) * 150) // 2
        
        for i, sniper_type in enumerate(sniper_types):
            # Character box
            char_rect = pygame.Rect(x_offset + i * 150, 100, 120, 120)
            color = (200, 200, 200) if selected == sniper_type else (100, 100, 100)
            pygame.draw.rect(self.surface, color, char_rect)
            
            # Character sprite or color
            sprite_rect = pygame.Rect(x_offset + i * 150 + 10, 110, 100, 100)
            if hasattr(sniper_type, 'sprite') and sniper_type.sprite:
                self.surface.blit(pygame.transform.scale(sniper_type.sprite, (100, 100)), sprite_rect)
            else:
                pygame.draw.rect(self.surface, sniper_type.color, sprite_rect)
            
            # Character name
            name_text = self.fonts['normal'].render(sniper_type.name, True, const.WHITE)
            name_rect = name_text.get_rect(center=(x_offset + i * 150 + 60, 240))
            self.surface.blit(name_text, name_rect)
            
            # Character description
            desc_text = self.fonts['normal'].render(sniper_type.description, True, const.WHITE)
            desc_rect = desc_text.get_rect(center=(x_offset + i * 150 + 60, 260))
            self.surface.blit(desc_text, desc_rect)
            
            # Add to clickable elements - (rect, type, index)
            clickable_elements.append((char_rect, "character", i))
        
        # Draw select button if character is selected
        if selected:
            select_button = Button(
                const.SCREEN_WIDTH // 2 - const.BUTTON_WIDTH // 2,
                const.SCREEN_HEIGHT - 100,
                const.BUTTON_WIDTH,
                const.BUTTON_HEIGHT,
                f"Select {selected.name}"
            )
            select_button.draw(self.surface, self.fonts['normal'])
            clickable_elements.append((select_button.rect, "select_button", None))
        
        # Add the background as a clickable element with lowest priority
        background_rect = self.surface.get_rect()
        clickable_elements.append((background_rect, "background", None))
        
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