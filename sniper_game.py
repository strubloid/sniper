"""
Sniper Game - Main Entry Point

This is the main entry module for the Sniper Game which initializes and starts
the game loop, handling basic initialization and error management.
"""
import os
import sys
import random
import pygame
import importlib

# Try to import game modules, if not found create a stub import
try:
    from sniper.config.constants import const
    from sniper.models.characters import Character, SniperType
    from sniper.models.projectiles import Projectile
    from sniper.ui.rendering import UI
except ImportError:
    # Use importlib for more robust imports
    const = importlib.import_module("sniper.config.constants").const
    Character = importlib.import_module("sniper.models.characters").Character
    SniperType = importlib.import_module("sniper.models.characters").SniperType
    Projectile = importlib.import_module("sniper.models.projectiles").Projectile
    UI = importlib.import_module("sniper.ui.rendering").UI

def debug_print(msg):
    """Print debug messages when debugging is enabled."""
    if getattr(const, "DEBUG", False):
        print(f"[DEBUG] {msg}")

def main():
    """Main entry point of the game."""
    # Initialize pygame
    pygame.init()
    
    # Create the game window
    screen_width, screen_height = const.SCREEN_WIDTH, const.SCREEN_HEIGHT
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Sniper Game")
    
    # Set up the clock
    clock = pygame.time.Clock()
    
    # Load fonts
    fonts = {
        'normal': pygame.font.SysFont(None, 24),
        'big': pygame.font.SysFont(None, 48),
        'small': pygame.font.SysFont(None, 18)
    }
    
    # Create UI manager
    ui_renderer = UI(screen, fonts)
    
    # Initialize character types
    sniper_types = _load_sniper_types()
    
    # Game state variables
    game_state = const.STATE_MENU
    player = None
    enemy = None
    projectiles = []
    character_select_stage = "player"
    selected_candidate = None
    player_turn = True
    shooting_mode = False
    obstacles = []
    show_movement_overlay = False  # Add this flag to control movement overlay
    
    # Camera system
    camera_x = 0
    camera_y = 0
    is_camera_dragging = False
    camera_drag_start = (0, 0)
    
    # Define map boundaries
    max_camera_x = const.GRID_SIZE * const.GRID_WIDTH
    max_camera_y = const.GRID_SIZE * const.GRID_HEIGHT
    
    # Main game loop
    running = True
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If in game, return to menu
                    if game_state == const.STATE_PLAY:
                        game_state = const.STATE_MENU
                    else:
                        running = False
                
                # Toggle movement overlay with M key
                if event.key == pygame.K_m and game_state == const.STATE_PLAY and player_turn:
                    show_movement_overlay = ui_renderer.visualize_available_movement_positions(player, obstacles, enemy)
                        
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle click based on game state
                if game_state == const.STATE_MENU:
                    # Check for button clicks in menu
                    if ui_renderer.menu_start_button_rect and ui_renderer.menu_start_button_rect.collidepoint(mouse_pos):
                        game_state = const.STATE_SELECT
                    elif ui_renderer.menu_exit_button_rect and ui_renderer.menu_exit_button_rect.collidepoint(mouse_pos):
                        running = False
                        
                elif game_state == const.STATE_SELECT:
                    # Handle character selection
                    # Check for sniper type selection
                    selected = ui_renderer.handle_character_select_click(mouse_pos, sniper_types, character_select_stage)
                    if selected:
                        selected_candidate = selected
                        
                    # Check for confirm button
                    confirm_button_rect = ui_renderer.draw_character_select(sniper_types, selected_candidate, character_select_stage)
                    if selected_candidate and confirm_button_rect and confirm_button_rect.collidepoint(mouse_pos):
                        if character_select_stage == "player":
                            # Set player's character type
                            player = Character(const.GRID_WIDTH // 4, const.GRID_HEIGHT // 2, selected_candidate)
                            character_select_stage = "enemy"
                            selected_candidate = None
                        else:
                            # Set enemy's character type
                            enemy = Character((const.GRID_WIDTH * 3) // 4, const.GRID_HEIGHT // 2, selected_candidate)
                            game_state = const.STATE_PLAY
                            # Generate map obstacles
                            obstacles = _generate_obstacles(player, enemy)
                            # Center camera on player
                            camera_x = max(0, player.x * const.GRID_SIZE - screen_width // 2)
                            camera_y = max(0, player.y * const.GRID_SIZE - screen_height // 2)
                
                elif game_state == const.STATE_PLAY:
                    # Check for UI button clicks
                    info_button_rect = ui_renderer.draw_info_button()
                    if info_button_rect and info_button_rect.collidepoint(mouse_pos):
                        ui_renderer.toggle_info_panel()
                        
                    # Check for center view button
                    center_button_rect = ui_renderer.draw_return_to_player_button()
                    if center_button_rect and center_button_rect.collidepoint(mouse_pos):
                        # Center camera on player
                        if player:
                            camera_x = player.x * const.GRID_SIZE - (screen_width // 2) + (const.GRID_SIZE // 2)
                            camera_y = player.y * const.GRID_SIZE - (screen_height // 2) + (const.GRID_SIZE // 2)
                            # Keep camera within map boundaries
                            camera_x = max(0, min(camera_x, max_camera_x - screen_width))
                            camera_y = max(0, min(camera_y, max_camera_y - screen_height))
                    
                    # Toggle movement overlay when clicking on player character
                    if player_turn and player:
                        grid_x = (mouse_pos[0] + camera_x) // const.GRID_SIZE
                        grid_y = (mouse_pos[1] + camera_y) // const.GRID_SIZE
                        
                        if grid_x == player.x and grid_y == player.y:
                            # Toggle movement overlay when clicking on player
                            show_movement_overlay = ui_renderer.visualize_available_movement_positions(player, obstacles, enemy)
                            continue  # Skip rest of click handling
                    
                    # Handle grid click for player movement or shooting
                    if player_turn and event.button == 1:  # Left mouse button
                        # Convert screen coordinates to grid coordinates
                        grid_x = (mouse_pos[0] + camera_x) // const.GRID_SIZE
                        grid_y = (mouse_pos[1] + camera_y) // const.GRID_SIZE
                        
                        # Check if grid position is within bounds
                        if (0 <= grid_x < const.GRID_WIDTH and 
                            0 <= grid_y < const.GRID_HEIGHT):
                            
                            if shooting_mode:
                                # Process shooting
                                _process_shooting(player, grid_x, grid_y, projectiles)
                                shooting_mode = False
                                player_turn = False
                            else:
                                # Process movement if valid
                                if _is_valid_move(grid_x, grid_y, player, obstacles, enemy):
                                    # Calculate distance to move
                                    distance = abs(player.x - grid_x) + abs(player.y - grid_y)
                                    
                                    # Check if player has enough courage points
                                    if distance <= player.courage_points:
                                        # Update player position
                                        player.x = grid_x
                                        player.y = grid_y
                                        # Reduce courage points
                                        player.courage_points -= distance
                                        
                                        # Update camera to center on new position
                                        camera_x = player.x * const.GRID_SIZE - (screen_width // 2) + (const.GRID_SIZE // 2)
                                        camera_y = player.y * const.GRID_SIZE - (screen_height // 2) + (const.GRID_SIZE // 2)
                                        # Keep camera within map boundaries
                                        camera_x = max(0, min(camera_x, max_camera_x - screen_width))
                                        camera_y = max(0, min(camera_y, max_camera_y - screen_height))
                                        
                                        # Hide movement overlay after moving
                                        show_movement_overlay = False
                                        ui_renderer.show_movement_overlay = False
                
                # Handle camera dragging with right mouse button
                if event.button == 3:  # Right mouse button
                    is_camera_dragging = True
                    camera_drag_start = mouse_pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Right mouse button
                    is_camera_dragging = False
                    
            # Handle camera dragging while mouse is moving
            if event.type == pygame.MOUSEMOTION and is_camera_dragging:
                dx = camera_drag_start[0] - event.pos[0]
                dy = camera_drag_start[1] - event.pos[1]
                camera_drag_start = event.pos
                
                # Update camera position
                camera_x += dx
                camera_y += dy
                
                # Keep camera within map boundaries
                camera_x = max(0, min(camera_x, max_camera_x - screen_width))
                camera_y = max(0, min(camera_y, max_camera_y - screen_height))
            
            # Handle space key to toggle shooting mode
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state == const.STATE_PLAY:
                if player_turn:
                    shooting_mode = not shooting_mode
        
        # Clear the screen
        screen.fill(const.BG_COLOR)
        
        # Render based on game state
        if game_state == const.STATE_MENU:
            ui_renderer.draw_menu()
            
        elif game_state == const.STATE_SELECT:
            confirm_button_rect = ui_renderer.draw_character_select(sniper_types, selected_candidate, character_select_stage)
            
        elif game_state == const.STATE_PLAY:
            # Draw game grid
            ui_renderer.draw_grid(camera_x, camera_y)
            
            # Draw obstacles
            ui_renderer.draw_obstacles(obstacles, camera_x, camera_y)
            
            # Draw valid movement positions when overlay is active
            if show_movement_overlay and player_turn and player:
                ui_renderer.draw_valid_moves(player, obstacles, camera_x, camera_y, enemy)
            
            # Draw characters
            if player:
                ui_renderer.draw_character(player, is_player=True, is_turn=player_turn, 
                                        camera_x=camera_x, camera_y=camera_y)
            if enemy:
                ui_renderer.draw_character(enemy, is_player=False, is_turn=not player_turn, 
                                        camera_x=camera_x, camera_y=camera_y)
                
            # Draw projectiles
            for proj in projectiles:
                ui_renderer.draw_projectile(proj, camera_x, camera_y)
            
            # Draw UI elements
            ui_renderer.draw_hud_grid(player, enemy)
            ui_renderer.draw_turn_indicator(player_turn)
            ui_renderer.draw_info_button()
            ui_renderer.draw_debug_button()
            ui_renderer.draw_return_to_player_button()
            
            # Draw shooting arrow if in shooting mode
            if shooting_mode and player_turn:
                mouse_pos = pygame.mouse.get_pos()
                ui_renderer.draw_shooting_arrow(
                    player.x, player.y, mouse_pos, camera_x, camera_y)
            
            # Draw info panel if active
            if ui_renderer.info_panel_active:
                game_info = [
                    f"Player: {player.sniper_type.name}",
                    f"Health: {player.health}/{player.max_health}",
                    f"Courage: {player.courage_points}/{player.max_courage}",
                    "",
                    f"Enemy: {enemy.sniper_type.name}",
                    f"Health: {enemy.health}/{enemy.max_health}",
                    f"Turn: {'Player' if player_turn else 'Enemy'}"
                ]
                ui_renderer.draw_info_panel(game_info)
                
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(const.FPS)
        
        # Simple AI logic when it's enemy's turn
        if game_state == const.STATE_PLAY and not player_turn:
            # Wait a moment before AI moves to make it feel more natural
            pygame.time.wait(300)
            
            # Simple AI: move toward player if possible, or shoot if in line of sight
            _process_enemy_turn(player, enemy, obstacles, projectiles)
            
            # Reset player turn
            player_turn = True
            
        # Update projectiles
        if game_state == const.STATE_PLAY:
            _update_projectiles(projectiles, player, enemy, obstacles)
            
    # Quit pygame
    pygame.quit()

def _load_sniper_types():
    """Load available sniper types."""
    from sniper.utils.helpers import load_image
    
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

def _generate_obstacles(player, enemy):
    """Generate obstacles for the map."""
    obstacles = []
    
    # Create some random obstacles
    for _ in range(30):
        obstacle_width = random.randint(1, 3)
        obstacle_height = random.randint(1, 2)
        
        ox = random.randint(0, const.GRID_WIDTH - obstacle_width)
        oy = random.randint(0, const.GRID_HEIGHT - obstacle_height)
        
        # Don't place obstacles too close to players
        if ((abs(ox - player.x) < 3 and abs(oy - player.y) < 3) or
            (abs(ox - enemy.x) < 3 and abs(oy - enemy.y) < 3)):
            continue
        
        obstacles.append(pygame.Rect(ox, oy, obstacle_width, obstacle_height))
    
    return obstacles

def _is_valid_move(grid_x, grid_y, player, obstacles, enemy):
    """Check if the move to the given grid position is valid.""" 
    # Check if position is within grid bounds
    if (grid_x < 0 or grid_x >= const.GRID_WIDTH or
        grid_y < 0 or grid_y >= const.GRID_HEIGHT):
        return False
        
    # Check if position is occupied by an obstacle
    for obstacle in obstacles:
        if obstacle.collidepoint(grid_x, grid_y):
            return False
            
    # Check if position is occupied by enemy
    if grid_x == enemy.x and grid_y == enemy.y:
        return False
        
    # Check if the move is within the allowed range based on courage points
    distance = abs(player.x - grid_x) + abs(player.y - grid_y)
    if distance > player.courage_points:
        # Move is valid but will be rejected in _process_movement due to courage points
        return False
        
    return True

def _process_shooting(shooter, target_x, target_y, projectiles):
    """Process shooting action towards the target coordinates."""
    # Calculate direction vector from shooter to target
    dx = target_x - shooter.x
    dy = target_y - shooter.y
    
    # Normalize the vector to get a unit direction
    length = max(0.01, (dx**2 + dy**2)**0.5)
    dx /= length
    dy /= length
    
    # Create projectile
    projectile = Projectile(
        x=float(shooter.x) + 0.5,  # Start from center of player cell
        y=float(shooter.y) + 0.5,
        dx=dx * const.PROJECTILE_SPEED,
        dy=dy * const.PROJECTILE_SPEED,
        owner=shooter
    )
    
    # Add projectile to game
    projectiles.append(projectile)
    
    debug_print(f"Shot at ({target_x}, {target_y})")
    
    return True

def _update_projectiles(projectiles, player, enemy, obstacles):
    """Update all projectiles in the game, handling movement and collisions."""
    # Process each projectile
    for projectile in list(projectiles):  # Create a copy of the list to safely remove items
        # Update projectile position
        projectile.x += projectile.dx
        projectile.y += projectile.dy
        
        # Convert to grid coordinates for collision detection
        grid_x = int(projectile.x)
        grid_y = int(projectile.y)
        
        # Check if projectile is out of bounds
        if (grid_x < 0 or grid_x >= const.GRID_WIDTH or 
            grid_y < 0 or grid_y >= const.GRID_HEIGHT):
            projectiles.remove(projectile)
            continue
            
        # Check collision with obstacles
        for obstacle in obstacles:
            if obstacle.collidepoint(grid_x, grid_y):
                # Handle collision with obstacle
                projectiles.remove(projectile)
                break
                
        # Check if projectile was already removed
        if projectile not in projectiles:
            continue
            
        # Check collision with player
        if (grid_x == player.x and grid_y == player.y and
            projectile.owner != player):
            player.health -= 1  # Decrease player health
            projectiles.remove(projectile)
            continue
            
        # Check collision with enemy
        if (grid_x == enemy.x and grid_y == enemy.y and
            projectile.owner != enemy):
            enemy.health -= 1  # Decrease enemy health
            projectiles.remove(projectile)

def _process_enemy_turn(player, enemy, obstacles, projectiles):
    """Implement the enemy's movement and shooting logic."""
    # Check if enemy can see player
    can_shoot = _can_shoot(enemy, player, obstacles)
    
    if can_shoot:
        # Enemy can see player, shoot at them
        _process_shooting(enemy, player.x, player.y, projectiles)
    else:
        # Enemy can't see player, try to move toward them
        # Calculate direction toward player
        dx = 1 if player.x > enemy.x else -1 if player.x < enemy.x else 0
        dy = 1 if player.y > enemy.y else -1 if player.y < enemy.y else 0
        
        # Try to move in x direction first if possible
        if dx != 0:
            new_x = enemy.x + dx
            if _is_valid_move(new_x, enemy.y, enemy, obstacles, player):
                enemy.x = new_x
                enemy.courage_points -= 1
                return
                
        # Try to move in y direction if x movement wasn't possible
        if dy != 0:
            new_y = enemy.y + dy
            if _is_valid_move(enemy.x, new_y, enemy, obstacles, player):
                enemy.y = new_y
                enemy.courage_points -= 1
                return
                
        # If neither direction works, try diagonal movement
        if dx != 0 and dy != 0:
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            if _is_valid_move(new_x, new_y, enemy, obstacles, player):
                enemy.x = new_x
                enemy.y = new_y
                enemy.courage_points -= 2  # Diagonal movement costs 2 courage points
                return

def _can_shoot(shooter, target, obstacles):
    """Check if there's a clear line of sight from shooter to target."""
    # Simple line-of-sight check
    # Get positions
    x0, y0 = shooter.x, shooter.y
    x1, y1 = target.x, target.y
    
    # Use Bresenham's line algorithm to check line of sight
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while x0 != x1 or y0 != y1:
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
            
        # If we hit an obstacle before reaching the target, no line of sight
        if (x0 == x1 and y0 == y1):  # We've reached the target
            return True
            
        # Check if current position has an obstacle
        for obstacle in obstacles:
            if obstacle.collidepoint(x0, y0):
                return False
                
    return True

if __name__ == "__main__":
    main()
