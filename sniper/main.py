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
        
        # Set scaling to fill the entire screen width and height
        self.scale_x = self.screen_width / const.SCREEN_WIDTH
        self.scale_y = self.screen_height / const.SCREEN_HEIGHT
        
        # Set up fonts
        self.fonts = {
            'normal': pygame.font.SysFont(None, 24),
            'big': pygame.font.SysFont(None, 48)
        }
        
        # Create UI manager
        self.ui = UI(self.virtual_screen, self.fonts)
        
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
        """Start a new game by generating obstacles."""
        self.obstacles = self._generate_obstacles(self.player, self.enemy)
        
    def _generate_obstacles(self, player: Character, enemy: Character) -> list:
        """Generate random obstacles for the game map."""
        obstacles = []
        for _ in range(const.OBSTACLE_COUNT):
            x, y = random.randint(0, const.GRID_WIDTH - 1), random.randint(0, const.GRID_HEIGHT - 1)
            if (x, y) not in [(player.x, player.y), (enemy.x, enemy.y)]:
                obstacles.append((x, y))
        return obstacles

    def handle_mouse_click(self, pos):
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
    
    def _handle_character_select(self, pos):
        """Handle clicks in character selection screen."""
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
    
    def _handle_gameplay_click(self, pos, grid_x, grid_y):
        """Handle clicks during gameplay."""
        if self.shoot_mode and self.player.shots_left > 0:
            self._handle_shooting(pos)
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
                        self._end_game("AI")
    
    def _handle_shooting(self, mouse_pos):
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

    def handle_projectile_logic(self):
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
                    self._end_game("Player")
            # Check for hit on player
            elif int(p.x) == self.player.x and int(p.y) == self.player.y:
                self.player.health -= const.PROJECTILE_DAMAGE
                self.projectiles.remove(p)
                
                # Check if player is defeated
                if self.player.health <= 0:
                    self._end_game("AI")

    def enemy_turn(self):
        """Execute the enemy's turn using the AI controller."""
        # Initialize the turn if not already started
        if not self.ai_turn_started:
            self._initialize_enemy_turn()
        
        # Check if the delay has passed before executing AI logic
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_turn_time >= const.AI_TURN_DELAY:
            self._execute_ai_turn()
            self._finalize_enemy_turn()

    def _initialize_enemy_turn(self):
        """Initialize the enemy turn state and prepare for AI execution."""
        self.ai_turn_started = True
        self.ai_turn_time = pygame.time.get_ticks()
        
        # Reset AI state
        self.ai_state = const.AI_STATE_THINKING
        
        # Reset enemy's actions based on character type
        self._reset_enemy_actions()
        
        debug_print(f"Enemy turn started with moves: {self.enemy.moves_left}, shots: {self.enemy.shots_left}")

    def _reset_enemy_actions(self):
        """Reset enemy actions based on their character type and abilities."""
        if self.enemy and self.enemy.sniper_type:
            self.enemy.moves_left = self.enemy.sniper_type.move_limit
            self.enemy.shots_left = 1  # Default 1 shot per turn
            
            # Future extension point: Add special abilities or bonuses here
            # Example: if self.enemy.sniper_type.name == "Scout":
            #     self.enemy.moves_left += 1  # Scout gets extra movement

    def _execute_ai_turn(self):
        """Execute the AI turn logic with proper rendering updates."""
        try:
            # Pass game state to AI controller and get updated AI state
            self.ai_state = AI.take_turn(
                self.virtual_screen,
                self.enemy, 
                self.player, 
                self.obstacles, 
                self.projectiles,
                self._redraw_during_ai_turn
            )
        except Exception as e:
            debug_print(f"Error during AI turn execution: {e}")
            import traceback
            debug_print(traceback.format_exc())
            self.ai_state = const.AI_STATE_END

    def _finalize_enemy_turn(self):
        """Clean up after AI turn and prepare for player's turn."""
        # Start the player's turn again
        self.player_turn = True
        self.player.start_turn()
        self.ai_turn_started = False

    def _redraw_during_ai_turn(self):
        """Redraw the game state during AI animations."""
        # Fill screens
        self.screen.fill(const.BLACK)
        self.virtual_screen.fill(const.BLACK)
        
        # Draw game elements on virtual screen
        self.ui.draw_grid()
        self.ui.draw_obstacles(self.obstacles)
        if self.player:
            self.player.draw(self.virtual_screen)
        if self.enemy:
            self.enemy.draw(self.virtual_screen)
        self.ui.draw_projectiles(self.projectiles)
        self.ui.draw_hud_grid(self.player, self.enemy)
        self.ui.draw_turn_indicator(self.player_turn)
        if self.show_debug:
            self.ui.draw_debug_info(self.ai_state)
            
        # Scale and display
        scaled_surface = pygame.transform.scale(
            self.virtual_screen, (self.screen_width, self.screen_height)
        )
        
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def _end_game(self, winner):
        """End the game and show the winner."""
        self.game_state = const.STATE_GAME_OVER
        self.winner = winner
        # Save score data
        self.scores.append({
            'winner': winner,
            'player_health': self.player.health if self.player else 0,
            'enemy_health': self.enemy.health if self.enemy else 0
        })

    def toggle_debug(self):
        """Toggle the debug information display."""
        self.show_debug = not self.show_debug

    def run(self):
        """Run the main game loop."""
        running = True
        
        while running:
            # Fill the screens
            self.screen.fill(const.BLACK)
            self.virtual_screen.fill(const.BLACK)
            
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
                    # Convert actual mouse position to virtual screen coordinates
                    actual_mouse_pos = event.pos
                    virtual_mouse_pos = (
                        actual_mouse_pos[0] * (const.SCREEN_WIDTH / self.screen_width),
                        actual_mouse_pos[1] * (const.SCREEN_HEIGHT / self.screen_height)
                    )
                    
                    # Only process clicks if they're within the virtual screen bounds
                    if (0 <= virtual_mouse_pos[0] < const.SCREEN_WIDTH and 
                        0 <= virtual_mouse_pos[1] < const.SCREEN_HEIGHT):
                        
                        # Handle button clicks
                        if self.game_state == const.STATE_PLAY:
                            if (end_turn_button_rect and end_turn_button_rect.collidepoint(virtual_mouse_pos) 
                                    and self.player_turn):
                                # End Turn button clicked
                                self.player.moves_left = 0
                                self.player.shots_left = 0
                                self.player_turn = False
                                continue  # Skip other click handling
                            
                            if debug_button_rect and debug_button_rect.collidepoint(virtual_mouse_pos):
                                # Debug button clicked
                                self.toggle_debug()
                                continue  # Skip other click handling
                        
                        # Handle other mouse clicks
                        self.handle_mouse_click(virtual_mouse_pos)
                    
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)

            # Render based on game state
            self._render_current_state()
            
            # Scale the virtual screen to the display size
            scaled_surface = pygame.transform.scale(
                self.virtual_screen, (self.screen_width, self.screen_height)
            )
            
            # Display the scaled surface
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(const.FPS)

        pygame.quit()

    def _handle_keydown(self, event):
        """Handle keyboard input events."""
        if event.key == pygame.K_ESCAPE:
            # Cancel actions with ESC key
            if self.game_state == const.STATE_PLAY:
                if self.shoot_mode:
                    self.shoot_mode = False
                elif self.player.show_range:
                    self.player.show_range = False
            elif self.game_state in (const.STATE_SCOREBOARD, const.STATE_GAME_OVER):
                self.game_state = const.STATE_MENU
            elif self.game_state == const.STATE_SELECT and self.show_confirm_popup:
                self.show_confirm_popup = False
        elif event.key == pygame.K_SPACE and self.game_state == const.STATE_PLAY and self.player_turn:
            self.shoot_mode = True
        elif event.key == pygame.K_RETURN and self.game_state == const.STATE_MENU:
            self.game_state = const.STATE_SELECT

    def _render_current_state(self):
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

    def _render_gameplay(self):
        """Render the gameplay state."""
        # Draw basic elements
        self.ui.draw_grid()
        self.ui.draw_obstacles(self.obstacles)
        
        # Draw characters
        if self.player:
            self.player.draw_range(self.virtual_screen)
            self.player.draw(self.virtual_screen)
        
        if self.enemy:
            self.enemy.draw(self.virtual_screen)
            
        # Draw projectiles
        self.ui.draw_projectiles(self.projectiles)
        
        # Draw shooting arrow
        if self.shoot_mode and self.player.shots_left > 0:
            # Get actual mouse position and convert to virtual screen coordinates
            actual_mouse_pos = pygame.mouse.get_pos()
            virtual_mouse_pos = (
                actual_mouse_pos[0] * (const.SCREEN_WIDTH / self.screen_width),
                actual_mouse_pos[1] * (const.SCREEN_HEIGHT / self.screen_height)
            )
            
            # Only draw the arrow if the mouse is within the virtual screen
            if (0 <= virtual_mouse_pos[0] < const.SCREEN_WIDTH and 
                0 <= virtual_mouse_pos[1] < const.SCREEN_HEIGHT):
                self.ui.draw_shooting_arrow(self.player.x, self.player.y, virtual_mouse_pos)
            
        # Process projectile logic
        self.handle_projectile_logic()
        
        # Draw HUD elements
        self.ui.draw_hud_grid(self.player, self.enemy)
        self.ui.draw_instructions()
        self.ui.draw_turn_indicator(self.player_turn)
        
        # Draw debug button and info
        debug_button_rect = self.ui.draw_debug_button()
        if self.show_debug:
            self.ui.draw_debug_info(self.ai_state)
        
        # Draw the End Turn button
        if self.player_turn:
            self.ui.draw_end_turn_button()
            
        # Handle AI turn when it's not the player's turn
        if not self.player_turn:
            self.enemy_turn()


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