import pygame
from sniper.config.constants import const

class UI:
    """UI Manager class for handling all game UI elements."""
    
    def __init__(self, screen, fonts):
        """Initialize the UI manager."""
        self.screen = screen
        self.fonts = fonts
        self.bottom_bar_height = 70
        self.show_info_panel = False
        self.show_movement_overlay = False  # New flag to control movement overlay
        
    def visualize_available_movement_positions(self, player, obstacles, enemy=None):
        """Toggle visualization of available movement positions for the player."""
        self.show_movement_overlay = not self.show_movement_overlay
        return self.show_movement_overlay

    def draw_valid_moves(self, player, obstacles, camera_x, camera_y, enemy=None):
        """Draw valid movement positions for the player character."""
        # Only draw if the movement overlay is active
        if not self.show_movement_overlay:
            return
            
        # Get player's courage points (movement range)
        courage_points = player.courage_points
        
        # Define highlight colors
        valid_move_color = (100, 255, 100, 120)  # Green with some transparency
        
        # Check all positions within the player's movement range
        for dx in range(-courage_points, courage_points + 1):
            for dy in range(-courage_points, courage_points + 1):
                # Calculate total distance (Manhattan distance)
                distance = abs(dx) + abs(dy)
                
                # Skip if beyond movement range or same position as player
                if distance > courage_points or (dx == 0 and dy == 0):
                    continue
                
                # Calculate grid position
                grid_x = player.x + dx
                grid_y = player.y + dy
                
                # Skip if position is out of bounds
                if (grid_x < 0 or grid_x >= const.GRID_WIDTH or
                    grid_y < 0 or grid_y >= const.GRID_HEIGHT):
                    continue
                
                # Skip if position has an obstacle
                is_obstacle = False
                for obstacle in obstacles:
                    if obstacle.collidepoint(grid_x, grid_y):
                        is_obstacle = True
                        break
                if is_obstacle:
                    continue
                
                # Skip if this is enemy position
                if enemy and grid_x == enemy.x and grid_y == enemy.y:
                    continue
                
                # Calculate screen position for valid move
                screen_x = grid_x * const.GRID_SIZE - camera_x
                screen_y = grid_y * const.GRID_SIZE - camera_y
                
                # Create a transparent surface for the highlight
                highlight_surf = pygame.Surface((const.GRID_SIZE, const.GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surf, valid_move_color, (0, 0, const.GRID_SIZE, const.GRID_SIZE))
                
                # Draw the highlight with transparency
                self.screen.blit(highlight_surf, (screen_x, screen_y))
                
                # Draw a border around the highlighted cell
                pygame.draw.rect(
                    self.screen,
                    (50, 200, 50),
                    (screen_x, screen_y, const.GRID_SIZE, const.GRID_SIZE),
                    2
                )

    def draw_return_to_player_button(self) -> pygame.Rect:
        """Draw a button to return camera focus to the player's position."""
        button_rect = pygame.Rect(
            20, 
            self.screen.get_height() - 100,  # Position at bottom left
            150, 
            30
        )
        # Draw the button background
        pygame.draw.rect(self.screen, (50, 100, 200), button_rect)
        # Draw the button border
        pygame.draw.rect(self.screen, (100, 150, 250), button_rect, 2)
        
        # Draw the button text
        text_surf = self.fonts['normal'].render("Return to Player", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return button_rect

    def handle_character_select_click(self, mouse_pos, sniper_types, stage):
        """Handle clicks on the character selection screen."""
        selected_type = None
        
        # Check if any character card was clicked
        for i, sniper_type in enumerate(sniper_types):
            # Calculate the card position
            card_width = 150
            card_height = 200
            card_spacing = 20
            
            total_width = len(sniper_types) * card_width + (len(sniper_types) - 1) * card_spacing
            start_x = (const.SCREEN_WIDTH - total_width) // 2
            
            card_x = start_x + i * (card_width + card_spacing)
            card_y = 150  # Fixed vertical position for all cards
            
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                selected_type = sniper_type
                break
        
        return selected_type
        
    def draw_character_select(self, sniper_types, selected_candidate=None, stage="player"):
        """Draw the character selection screen."""
        # Calculate card dimensions
        card_width = 150
        card_height = 200
        card_spacing = 20
        
        # Calculate total width of all cards and spacing
        total_width = len(sniper_types) * card_width + (len(sniper_types) - 1) * card_spacing
        start_x = (const.SCREEN_WIDTH - total_width) // 2
        
        # Draw header text
        header_text = f"Select {'Your' if stage == 'player' else 'Enemy'} Character"
        header_surface = self.fonts['big'].render(header_text, True, (255, 255, 255))
        header_rect = header_surface.get_rect(center=(const.SCREEN_WIDTH // 2, 80))
        self.screen.blit(header_surface, header_rect)
        
        # Draw each character card
        for i, sniper_type in enumerate(sniper_types):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = 150
            
            # Draw the card background (highlight if selected)
            card_color = (80, 80, 80)
            if selected_candidate and selected_candidate.name == sniper_type.name:
                card_color = (120, 120, 200)  # Highlight selected card
                
            pygame.draw.rect(self.screen, card_color, (card_x, card_y, card_width, card_height))
            pygame.draw.rect(self.screen, sniper_type.color, (card_x, card_y, card_width, card_height), 3)
            
            # Draw character name
            name_surface = self.fonts['normal'].render(sniper_type.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(center=(card_x + card_width // 2, card_y + 30))
            self.screen.blit(name_surface, name_rect)
            
            # Draw character sprite if available
            if sniper_type.sprite:
                # Scale sprite to fit card
                sprite_size = min(card_width - 20, 64)  # Max size with padding
                scaled_sprite = pygame.transform.scale(sniper_type.sprite, (sprite_size, sprite_size))
                self.screen.blit(scaled_sprite, (card_x + (card_width - sprite_size) // 2, card_y + 50))
            
            # Draw character description
            desc_surface = self.fonts['small'].render(sniper_type.description, True, (200, 200, 200))
            desc_rect = desc_surface.get_rect(center=(card_x + card_width // 2, card_y + 130))
            self.screen.blit(desc_surface, desc_rect)
            
            # Draw courage points (movement range)
            courage_text = f"Movement: {sniper_type.courage_limit}"
            courage_surface = self.fonts['small'].render(courage_text, True, (255, 255, 100))
            courage_rect = courage_surface.get_rect(center=(card_x + card_width // 2, card_y + 155))
            self.screen.blit(courage_surface, courage_rect)
            
            # Draw special power
            power_text = f"Power: {sniper_type.power_type}"
            power_surface = self.fonts['small'].render(power_text, True, (100, 255, 255))
            power_rect = power_surface.get_rect(center=(card_x + card_width // 2, card_y + 175))
            self.screen.blit(power_surface, power_rect)
        
        # Draw instruction text
        instruction_text = "Click to select a character"
        if selected_candidate:
            instruction_text = "Press ENTER to confirm selection"
            
        instruction_surface = self.fonts['normal'].render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(const.SCREEN_WIDTH // 2, card_y + card_height + 40))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Draw confirm button if a character is selected
        if selected_candidate:
            button_width = 150
            button_height = 40
            button_rect = pygame.Rect(
                (const.SCREEN_WIDTH - button_width) // 2,
                card_y + card_height + 70,
                button_width, 
                button_height
            )
            pygame.draw.rect(self.screen, (50, 150, 50), button_rect)
            pygame.draw.rect(self.screen, (100, 200, 100), button_rect, 2)
            
            confirm_surface = self.fonts['normal'].render("Confirm", True, (255, 255, 255))
            confirm_rect = confirm_surface.get_rect(center=button_rect.center)
            self.screen.blit(confirm_surface, confirm_rect)
            
            return button_rect
        
        return None