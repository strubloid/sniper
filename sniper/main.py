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
from sniper.models import SniperType, Character, Projectile, ScenarioManager
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
            'big': pygame.font.SysFont(None, 48),
            'huge': pygame.font.SysFont(None, 96)  # For round transition countdown
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
        self.scenario = None  # ScenarioManager instance
        self.round_number = 1  # Track the current round number
        self.in_round_transition = False  # Track if we're in a round transition
        self.winner = None
        self.show_debug = False
        self.ai_state = None
        self.scores = []
        
        # AI turn handling
        self.ai_turn_started = False
        self.ai_turn_time = 0
        
        # Round transition countdown
        self.round_transition_start_time = 0
        self.show_countdown = False
        
        # Post-enemy turn delay tracking
        self.post_enemy_delay = False
        self.post_enemy_delay_start = 0
        
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
        """Start a new game by initializing the scenario."""
        # Initialize scenario with default population
        self.scenario = ScenarioManager(const.SCENARIO_POPULATION)
        
        # Generate initial scenario with blocks
        if self.player and self.enemy:
            self.scenario.generate_scenario((self.player.x, self.player.y), (self.enemy.x, self.enemy.y))
            self.round_number = 1
            self.in_round_transition = False
    
    def start_round_transition(self):
        """Start the transition animation between rounds."""
        if not self.in_round_transition:
            self.in_round_transition = True
            self.round_number += 1
            self.round_transition_start_time = pygame.time.get_ticks()
            self.show_countdown = True
            debug_print(f"Starting Round {self.round_number}")
            
            # Explicitly force a round transition with new asteroid positions
            if self.scenario:
                self.scenario.start_round_transition()
                # Force the round transition to be active
                self.scenario.round_transition_active = True
                # Reset the phase for proper transition
                self.scenario.fade_phase_complete = False
                
            debug_print("Round transition started - asteroids will regenerate")
    
    def update_round_transition(self):
        """Update the round transition animation and return True when complete."""
        if not self.in_round_transition:
            return True
            
        # Update the transition animation
        transition_complete = self.scenario.update_round_transition(
            (self.player.x, self.player.y),
            (self.enemy.x, self.enemy.y)
        )
        
        if transition_complete:
            self.in_round_transition = False
            self.show_countdown = False
            debug_print(f"Round {self.round_number} started")
            
            # Start the player's turn when the transition is complete
            self.player_turn = True
            self.player.start_turn()
            return True
            
        return False

    def handle_mouse_click(self, pos):
        """Handle mouse click events based on current game state."""
        x, y = pos[0] // const.GRID_SIZE, pos[1] // const.GRID_SIZE

        if self.game_state == const.STATE_MENU:
            # Handle menu button clicks
            menu_buttons = self.ui.draw_menu()
            for rect, option in menu_buttons:
                if rect.collidepoint(pos):
                    if option == "PLAY":
                        # Show play submenu instead of going directly to character select
                        self.ui.toggle_play_submenu(True)
                    elif option == "PLAYER VS AI":
                        # Start a new Player vs AI game
                        self.game_state = const.STATE_SELECT
                        self.game_mode = "ai"
                        self.ui.toggle_play_submenu(False)
                    elif option == "PLAYER VS PLAYER":
                        # Start a new Player vs Player game (to be implemented)
                        self.game_state = const.STATE_SELECT
                        self.game_mode = "pvp"
                        self.ui.toggle_play_submenu(False)
                    elif option == "BACK_TO_MENU":
                        # Return to main menu from submenu
                        self.ui.toggle_play_submenu(False)
                    elif option == "OPTIONS":
                        # Show options menu (placeholder)
                        debug_print("Options selected")
                        # Future: self.game_state = const.STATE_OPTIONS
                    elif option == "LEADERBOARD":
                        self.game_state = const.STATE_SCOREBOARD
                    elif option == "EXIT":
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
                has_obstacle = (self.scenario and self.scenario.is_obstacle(grid_x, grid_y))
                if not has_obstacle:  # Only move if there's no obstacle
                    self.player.x, self.player.y = grid_x, grid_y
                    self.player.moves_left -= dist
                    self.player.health -= dist * const.HEALTH_DAMAGE_PER_MOVE
                    self.player.show_range = False

                    # Ensure health is not negative
                    if self.player.health <= 0:
                        self.player.health = 0  # Clamp health to zero
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
            elif self.scenario and self.scenario.handle_projectile_collision(int(p.x), int(p.y)):
                self.projectiles.remove(p)
            # Check for hit on enemy
            elif int(p.x) == self.enemy.x and int(p.y) == self.enemy.y:  # Fixed critical parenthesis bug
                self.enemy.health -= const.PROJECTILE_DAMAGE
                self.projectiles.remove(p)
                
                # Check if enemy is defeated - ensure health is not negative
                if self.enemy.health <= 0:
                    self.enemy.health = 0  # Clamp health to zero
                    self._end_game("Player")
            # Check for hit on player
            elif int(p.x) == self.player.x and int(p.y) == self.player.y:
                self.player.health -= const.PROJECTILE_DAMAGE
                self.projectiles.remove(p)
                
                # Check if player is defeated - ensure health is not negative
                if self.player.health <= 0:
                    self.player.health = 0  # Clamp health to zero
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
            # Make sure we pass obstacles in the correct format (simple list of position tuples)
            obstacles = self.scenario.obstacles if self.scenario else []
            
            # More visible debug messages
            print("=============================================")
            print(f"AI TURN STARTED - Round {self.round_number}")
            print(f"AI enemy position: {self.enemy.x},{self.enemy.y}")
            print(f"AI moves available: {self.enemy.moves_left}")
            print(f"AI shots available: {self.enemy.shots_left}")
            print(f"Player position: {self.player.x},{self.player.y}")
            print(f"Obstacles count: {len(obstacles)}")
            
            # Debug the obstacles being passed to the AI
            debug_print(f"AI obstacles: {obstacles}")
            
            self.ai_state = AI.take_turn(
                self.virtual_screen,
                self.enemy, 
                self.player, 
                obstacles,  # Use the obstacles property which returns position tuples
                self.projectiles,
                self._redraw_during_ai_turn,
                game_manager=self  # Pass self as game_manager
            )
            
            print(f"AI TURN COMPLETED - Final position: {self.enemy.x},{self.enemy.y}")
            print("=============================================")
            
        except Exception as e:
            print(f"ERROR during AI turn execution: {e}")
            import traceback
            print(traceback.format_exc())
            self.ai_state = const.AI_STATE_END

    def _finalize_enemy_turn(self):
        """Clean up after AI turn and prepare for player's turn."""
        # Reset AI turn state
        self.ai_turn_started = False
        
        # Start post-enemy turn delay
        self.post_enemy_delay = True
        self.post_enemy_delay_start = pygame.time.get_ticks()
        
        debug_print(f"AI turn finalized. Starting post-enemy turn delay.")

    def _redraw_during_ai_turn(self):
        """Redraw the game state during AI animations."""
        # Fill screens
        self.screen.fill(const.BLACK)
        
        # Draw space background with stars
        self.ui.draw_space_background()
        
        # Draw grid on top of space background
        self.ui.draw_grid()
        
        # Draw scenario objects with health and animations
        self.ui.draw_scenario(self.scenario)
        
        # Draw characters
        if self.player:
            self.player.draw(self.virtual_screen)
        
        if self.enemy:
            self.enemy.draw(self.virtual_screen)
            # Draw enemy info box above enemy
            self.ui.draw_enemy_info_box(self.enemy)
        
        # Draw projectiles
        self.ui.draw_projectiles(self.projectiles)
        
        # Draw round info
        self.ui.draw_round_info(self.round_number)
        
        # Draw new UI elements based on the mockup
        # 1. Game header with turn and moves/shots
        self.ui.draw_game_header(self.player, self.player_turn)
        
        # 2. Player stats panel at the bottom
        self.ui.draw_player_stats_panel(self.player)
        
        # Draw debug info if enabled
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

    def toggle_commands(self):
        """Toggle the command instructions display."""
        self.ui.show_commands = not self.ui.show_commands

    def check_character_health(self) -> bool:
        """Check if any character has reached 0 health and end the game if so.
        Returns True if the game ended, False otherwise."""
        if self.player and self.player.health <= 0:
            self.player.health = 0  # Ensure health is not negative
            self._end_game("AI")
            return True
        
        if self.enemy and self.enemy.health <= 0:
            self.enemy.health = 0  # Ensure health is not negative
            self._end_game("Player")
            return True
            
        return False

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
            show_commands_button_rect = None
            
            if self.game_state == const.STATE_PLAY:
                if self.player_turn:
                    end_turn_button_rect = self.ui.draw_end_turn_button()
                debug_button_rect = self.ui.draw_debug_button()
                # Add Show Commands button
                show_commands_button_rect = self.ui.draw_show_commands_button()
            
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
                                
                                # Set player's turn to false so AI can take its turn
                                self.player_turn = False
                                print("Player turn ended. Switching to AI turn.")
                                
                                # No need to start round transition here - that happens after AI's turn
                                continue  # Skip other click handling
                            
                            if debug_button_rect and debug_button_rect.collidepoint(virtual_mouse_pos):
                                # Debug button clicked
                                self.toggle_debug()
                                continue  # Skip other click handling
                            
                            if show_commands_button_rect and show_commands_button_rect.collidepoint(virtual_mouse_pos):
                                # Show Commands button clicked
                                self.toggle_commands()
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
        # Fill background with space theme
        self.ui.draw_space_background()
        
        # Draw grid on top of space background
        self.ui.draw_grid()
        
        # Update asteroid animations - add this line to continuously update animations
        if self.scenario:
            self.scenario.update_animations()
        
        # Draw scenario objects (asteroids) with health and animations
        self.ui.draw_scenario(self.scenario)
        
        # Draw round info
        self.ui.draw_round_info(self.round_number)
        
        # Draw characters
        if self.player:
            self.player.draw_range(self.virtual_screen)
            self.player.draw(self.virtual_screen)
        
        if self.enemy:
            self.enemy.draw(self.virtual_screen)
            # Draw enemy info box above enemy
            self.ui.draw_enemy_info_box(self.enemy)
            
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
        
        # Draw new UI elements based on the mockup
        # 1. Game header with turn and moves/shots
        self.ui.draw_game_header(self.player, self.player_turn)
        
        # 2. Player stats panel at the bottom
        self.ui.draw_player_stats_panel(self.player)
        
        # Draw instructions (only if toggled on)
        self.ui.draw_instructions()
        
        # Draw buttons
        debug_button_rect = self.ui.draw_debug_button()
        show_commands_button_rect = self.ui.draw_show_commands_button()
        
        if self.show_debug:
            self.ui.draw_debug_info(self.ai_state)
        
        # Draw the End Turn button
        if self.player_turn:
            end_turn_button_rect = self.ui.draw_end_turn_button()
        
        # Update round transition animation if active
        if self.in_round_transition:
            transition_complete = self.update_round_transition()
            if self.show_countdown:
                elapsed_time = pygame.time.get_ticks() - self.round_transition_start_time
                countdown_value = max(1, const.ROUND_TRANSITION_COUNTDOWN - elapsed_time // 1000)
                self.ui.draw_countdown(self.round_number)
            
        # Handle AI turn when it's not the player's turn and we're not in round transition
        elif not self.player_turn and not self.in_round_transition:
            if self.post_enemy_delay:
                current_time = pygame.time.get_ticks()
                if current_time - self.post_enemy_delay_start >= const.POST_ENEMY_DELAY:
                    # After the delay, start the round transition
                    self.post_enemy_delay = False
                    # Start round transition with new round number
                    self.start_round_transition()
                    debug_print(f"Post-enemy delay complete. Starting round transition to Round {self.round_number}")
            else:
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