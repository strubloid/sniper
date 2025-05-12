"""
Sniper Game - Main Module
A turn-based strategy game where players control snipers on a grid.

This is the main entry point for the game which handles initialization,
the game loop, and coordinating between modules.
"""
import os
import sys
import random
import pygame
from typing import List, Tuple, Dict, Optional, Any

# Import game modules
import constants as const
from constants import debug_print
from models import SniperType, Character, Projectile, Button
from ui import UI
from ai import AI


class GameManager:
    """Main game manager class that coordinates game logic and rendering."""

    def __init__(self):
        """Initialize the game manager and pygame."""
        # Initialize pygame
        pygame.init()
        
        # Set up the screen and clock
        self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        pygame.display.set_caption("Sniper Game")
        self.clock = pygame.time.Clock()
        
        # Set up fonts
        self.fonts = {
            'normal': pygame.font.SysFont(None, 24),
            'big': pygame.font.SysFont(None, 48)
        }
        
        # Create UI manager
        self.ui = UI(self.screen, self.fonts)
        
        # Game state
        self.game_state = const.STATE_MENU
        self.player = None
        self.enemy = None
        self.projectiles = []
        self.character_select_stage = "player"
        self.selected_candidate = None
        self.show_confirm_popup = False
        self.player_turn = True
        self.shoot_mode = False
        self.obstacles = []
        self.winner = None
        self.show_debug = False
        self.ai_state = None
        self.scores = []
        
        # AI turn handling
        self.ai_turn_started = False
        self.ai_turn_time = 0
        
        # Load sniper types
        self.sniper_types = self._load_sniper_types()

    def _load_sniper_types(self) -> List[SniperType]:
        """Load all available sniper types from configuration."""
        sniper_types = []
        for name, desc, color, limit, power in [
            ("Ghost", "Fast, high courage", (150, 150, 255), 3, "piercing"),
            ("Juggernaut", "Tanky, bouncing shots", (255, 100, 100), 2, "bouncing"),
            ("Scout", "Quick & nimble", (100, 255, 100), 4, "fast"),
            ("Shade", "Can freeze enemies", (200, 0, 200), 3, "freezing")
        ]:
            try:
                sprite_path = os.path.join(const.ASSETS_DIR, f"{name.lower()}.png")
                sprite = pygame.image.load(sprite_path).convert_alpha()
                sniper_types.append(SniperType(name, sprite, color, desc, limit, power))
            except pygame.error as e:
                debug_print(f"Error loading sprite for {name}: {e}")
        return sniper_types

    def start_game(self):
        """Start a new game by generating obstacles."""
        self.obstacles = self._generate_obstacles(self.player, self.enemy)

    def _generate_obstacles(self, player: Character, enemy: Character) -> List[Tuple[int, int]]:
        """Generate random obstacles for the game map."""
        obstacles = []
        for _ in range(const.OBSTACLE_COUNT):
            x, y = random.randint(0, const.GRID_WIDTH - 1), random.randint(0, const.GRID_HEIGHT - 1)
            if (x, y) not in [(player.x, player.y), (enemy.x, enemy.y)]:
                obstacles.append((x, y))
        return obstacles

    def handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click events based on current game state."""
        x, y = pos[0] // const.GRID_SIZE, pos[1] // const.GRID_SIZE

        if self.game_state == const.STATE_MENU:
            # Handle menu button clicks
            menu_buttons = self.ui.draw_menu()
            for rect, option in menu_buttons:
                if rect.collidepoint(pos):
                    if option == "Play":
                        self.game_state = const.STATE_SELECT
                    elif option == "Scoreboard":
                        self.game_state = const.STATE_SCOREBOARD
                    elif option == "Quit":
                        pygame.quit()
                        sys.exit()
        
        elif self.game_state == const.STATE_SELECT:
            self._handle_character_select(pos)
        
        elif self.game_state == const.STATE_PLAY and self.player_turn:
            self._handle_gameplay_click(pos, x, y)

    def _handle_character_select(self, pos: Tuple[int, int]) -> None:
        """Handle clicks on the character selection screen."""
        # Get all clickable elements from the UI
        clickable_elements = self.ui.draw_character_select(
            self.character_select_stage, 
            self.selected_candidate, 
            self.sniper_types
        )
        
        # Process element clicks with priority handling
        for element, element_type, element_data in clickable_elements:
            if element.collidepoint(pos):
                if element_type == "character":
                    # Character selection - simply set the selected candidate
                    self.selected_candidate = self.sniper_types[element_data]
                    self._highlight_character_selection()
                    return  # Return early to avoid processing background click
                
                elif element_type == "select_button" and self.selected_candidate:
                    # Select button - immediately create character and advance
                    if self.character_select_stage == "player":
                        self.player = Character(
                            const.PLAYER_START_X, 
                            const.PLAYER_START_Y, 
                            self.selected_candidate
                        )
                        self.character_select_stage = "enemy"
                        self.selected_candidate = None
                    else:
                        self.enemy = Character(
                            const.ENEMY_START_X, 
                            const.ENEMY_START_Y, 
                            self.selected_candidate, 
                            is_player=False
                        )
                        self.game_state = const.STATE_PLAY
                        self.player.start_turn()
                        self.start_game()
                        self.selected_candidate = None
                    return  # Return early after selection is complete
        
        # If we get here, it's a background click - only process if not clicking UI elements
        for element, element_type, element_data in clickable_elements:
            if element.collidepoint(pos) and element_type == "background":
                # Clear selection only if click was on background
                self.selected_candidate = None
                return

    def _highlight_character_selection(self) -> None:
        """Highlight the selected character with a yellow flash effect."""
        # Draw the character selection screen with normal highlight
        self.screen.fill(const.BLACK)
        char_rects = self.ui.draw_character_select(
            self.character_select_stage, 
            self.selected_candidate, 
            self.sniper_types,
            highlight_color=(255, 255, 0)  # Yellow highlight
        )
        pygame.display.flip()
        pygame.time.delay(150)  # Flash duration

    def _handle_gameplay_click(self, pos: Tuple[int, int], grid_x: int, grid_y: int) -> None:
        """Handle clicks during gameplay."""
        if self.shoot_mode and self.player.shots_left > 0:
            self.handle_shooting(pos)
            self.shoot_mode = False
        elif self.shoot_mode:
            # Reset shoot_mode if shooting conditions are not met
            self.shoot_mode = False
        elif grid_x == self.player.x and grid_y == self.player.y:
            # Toggle range display without ending the turn
            self.player.show_range = not self.player.show_range
        elif self.player.show_range and self.player.moves_left > 0:
            dist = abs(grid_x - self.player.x) + abs(grid_y - self.player.y)
            if dist <= self.player.moves_left:
                # Check if destination has an obstacle
                if (grid_x, grid_y) not in self.obstacles:
                    self.player.x, self.player.y = grid_x, grid_y
                    self.player.moves_left -= dist
                    self.player.health -= dist * const.HEALTH_DAMAGE_PER_MOVE
                    self.player.show_range = False

                    if self.player.health <= 0:
                        self.end_game("AI")

    def handle_shooting(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle shooting based on mouse direction."""
        player_center = (
            self.player.x * const.GRID_SIZE + const.GRID_SIZE // 2, 
            self.player.y * const.GRID_SIZE + const.GRID_SIZE // 2
        )
        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        
        # Normalize the direction vector
        length = max(0.001, (dx**2 + dy**2)**0.5)  # Avoid division by zero
        dx = dx / length
        dy = dy / length
        
        # Round to the nearest cardinal direction
        if abs(dx) > abs(dy):
            dy = 0
            dx = 1 if dx > 0 else -1
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
            
        # Create and add the projectile
        self.projectiles.append(Projectile(
            self.player.x, self.player.y, dx, dy, 
            self.player.sniper_type.color, self.player
        ))
        self.player.shots_left -= 1

    def handle_projectile_logic(self) -> None:
        """Update projectile positions and handle collisions."""
        for p in self.projectiles[:]:  # Use a copy for safe modification during iteration
            p.x += p.dx
            p.y += p.dy
            
            # Check for out of bounds
            if not (0 <= p.x < const.GRID_WIDTH and 0 <= p.y < const.GRID_HEIGHT):
                self.projectiles.remove(p)
            # Check for collision with obstacle
            elif (int(p.x), int(p.y)) in self.obstacles:
                self.projectiles.remove(p)
            # Check for hit on enemy
            elif int(p.x) == self.enemy.x and int(p.y) == self.enemy.y:
                self.enemy.health -= const.PROJECTILE_DAMAGE
                self.projectiles.remove(p)
                
                # Check if enemy is defeated
                if self.enemy.health <= 0:
                    self.end_game("Player")
            # Check for hit on player
            elif int(p.x) == self.player.x and int(p.y) == self.player.y:
                self.player.health -= const.PROJECTILE_DAMAGE
                self.projectiles.remove(p)
                
                # Check if player is defeated
                if self.player.health <= 0:
                    self.end_game("AI")

    def enemy_turn(self) -> None:
        debug_print("GameManager.enemy_turn called. player_turn=", self.player_turn)
        debug_print(f"Enemy stats before turn: moves_left={self.enemy.moves_left}, shots_left={self.enemy.shots_left}")
        """Execute the enemy's turn using AI."""
        if not self.ai_turn_started:
            debug_print("Initializing AI turn start")
            self.ai_turn_started = True
            self.ai_turn_time = pygame.time.get_ticks()
            # Reset AI state at the beginning of each turn
            self.ai_state = const.AI_STATE_THINKING
            # Initialize enemy's turn stats so AI has moves and shots
            self.enemy.start_turn()
            debug_print(f"Enemy stats after start_turn: moves_left={self.enemy.moves_left}, shots_left={self.enemy.shots_left}")
        
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_turn_time >= const.AI_TURN_DELAY:
            debug_print("AI turn delay passed, calling AI.take_turn")
            self.ai_state = AI.take_turn(
                self.screen,
                self.enemy, 
                self.player, 
                self.obstacles, 
                self.projectiles,
                self._redraw_during_ai_turn
            )
            debug_print("AI.take_turn returned state=", self.ai_state)
            
            # Start the player's turn again
            self.player_turn = True
            self.player.start_turn()
            self.ai_turn_started = False

    def _redraw_during_ai_turn(self) -> None:
        """Redraw the game state during AI animations."""
        self.screen.fill(const.BLACK)
        self.ui.draw_grid()
        self.ui.draw_obstacles(self.obstacles)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        self.ui.draw_projectiles(self.projectiles)
        self.ui.draw_hud_grid(self.player, self.enemy)
        self.ui.draw_turn_indicator(self.player_turn)
        if self.show_debug:
            self.ui.draw_debug_info(self.ai_state)
        pygame.display.flip()

    def end_game(self, winner: str) -> None:
        """End the game and show the winner."""
        self.game_state = const.STATE_GAME_OVER
        self.winner = winner
        # Save score, update scoreboard etc.
        self.scores.append({
            'winner': winner,
            'player_health': self.player.health,
            'enemy_health': self.enemy.health
        })

    def toggle_debug(self) -> None:
        """Toggle the debug information display."""
        self.show_debug = not self.show_debug

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        
        while running:
            self.screen.fill(const.BLACK)
            
            # Store button rectangles outside the event loop
            end_turn_button_rect = None
            debug_button_rect = None
            if self.game_state == const.STATE_PLAY:
                if self.player_turn:
                    end_turn_button_rect = self.ui.draw_end_turn_button()
                debug_button_rect = self.ui.draw_debug_button()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    # Handle button clicks here (outside of rendering)
                    if self.game_state == const.STATE_PLAY:
                        if (end_turn_button_rect and end_turn_button_rect.collidepoint(mouse_pos) 
                                and self.player_turn):
                            # End Turn button clicked
                            self.player.moves_left = 0
                            self.player.shots_left = 0
                            self.player_turn = False
                            continue  # Skip other click handling
                        
                        if debug_button_rect and debug_button_rect.collidepoint(mouse_pos):
                            # Debug button clicked
                            self.toggle_debug()
                            continue  # Skip other click handling
                    
                    # Handle other mouse clicks
                    self.handle_mouse_click(mouse_pos)
                    
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)

            # Render based on game state
            self._render_current_state()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(const.FPS)

        pygame.quit()

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard events."""
        if event.key == pygame.K_ESCAPE:
            # Cancel actions with ESC key
            if self.game_state == const.STATE_PLAY:
                if self.shoot_mode:
                    self.shoot_mode = False
                elif self.player.show_range:
                    self.player.show_range = False
            elif self.game_state == const.STATE_SCOREBOARD or self.game_state == const.STATE_GAME_OVER:
                self.game_state = const.STATE_MENU
            elif self.game_state == const.STATE_SELECT and self.show_confirm_popup:
                self.show_confirm_popup = False
        elif event.key == pygame.K_SPACE and self.game_state == const.STATE_PLAY and self.player_turn:
            self.shoot_mode = True
        elif event.key == pygame.K_RETURN and self.game_state == const.STATE_MENU:
            self.game_state = const.STATE_SELECT

    def _render_current_state(self) -> None:
        """Render the game based on its current state."""
        if self.game_state == const.STATE_MENU:
            self.ui.draw_menu()
        elif self.game_state == const.STATE_SCOREBOARD:
            self.ui.draw_scoreboard()
        elif self.game_state == const.STATE_SELECT:
            self.ui.draw_character_select(self.character_select_stage, self.selected_candidate, self.sniper_types)
            if self.show_confirm_popup:
                self.ui.draw_confirmation_popup()
        elif self.game_state == const.STATE_PLAY:
            self._render_gameplay()
        elif self.game_state == const.STATE_GAME_OVER:
            self.ui.draw_game_over(self.winner)

    def _render_gameplay(self) -> None:
        """Render the gameplay state."""
        # Draw basic elements
        self.ui.draw_grid()
        self.ui.draw_obstacles(self.obstacles)
        
        # Draw characters and ranges
        if self.player:
            self.player.draw_range(self.screen)
            self.player.draw(self.screen)
        
        if self.enemy:
            self.enemy.draw(self.screen)
            
        # Draw projectiles
        self.ui.draw_projectiles(self.projectiles)
        
        # Draw shooting arrow
        if self.shoot_mode and self.player.shots_left > 0:
            mouse_pos = pygame.mouse.get_pos()
            self.ui.draw_shooting_arrow(self.player.x, self.player.y, mouse_pos)
            
        # Process game logic
        self.handle_projectile_logic()
        
        # Draw HUD elements
        self.ui.draw_hud_grid(self.player, self.enemy)
        self.ui.draw_instructions()
        self.ui.draw_turn_indicator(self.player_turn)
        
        # Draw debug button and info - always draw debug button FIRST before the AI turn logic
        debug_button_rect = self.ui.draw_debug_button()
        if self.show_debug:
            self.ui.draw_debug_info(self.ai_state)
        
        # Draw the End Turn button
        if self.player_turn:
            self.ui.draw_end_turn_button()
            
        # Automatically handle AI turn if it's not the player's turn
        if not self.player_turn:
            self.enemy_turn()


# Entry point
if __name__ == "__main__":
    try:
        game = GameManager()
        game.run()
    except Exception as e:
        debug_print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)
