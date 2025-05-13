"""
Game Engine for Sniper Game.
This module contains the core game engine classes that manage the game state and logic.
"""
import random
import pygame
from typing import List, Tuple, Dict, Optional, Any, Callable

from config import GameConfig, GameState, AIState, Debug, StartPositions, Paths
from models import Character, SniperType, Projectile, GameObject, Obstacle


class GameObjectManager:
    """
    Manages collections of game objects and their interactions.
    Provides a structured way to update and handle game objects.
    """
    
    def __init__(self):
        self._obstacles: List[Obstacle] = []
        self._projectiles: List[Projectile] = []
    
    @property
    def obstacles(self) -> List[Obstacle]:
        """Get the list of obstacles."""
        return self._obstacles
        
    @property 
    def projectiles(self) -> List[Projectile]:
        """Get the list of projectiles."""
        return self._projectiles
    
    def clear(self) -> None:
        """Clear all game objects."""
        self._obstacles.clear()
        self._projectiles.clear()
    
    def generate_obstacles(self, count: int, player: Character, enemy: Character) -> None:
        """Generate random obstacles for the game map."""
        self._obstacles.clear()
        
        grid_width = GameConfig.Grid.get_width()
        grid_height = GameConfig.Grid.get_height()
        
        # Character positions to avoid
        occupied_positions = [(player.x, player.y), (enemy.x, enemy.y)]
        
        for _ in range(count):
            # Keep trying until we find a valid position
            while True:
                x = random.randint(0, grid_width - 1)
                y = random.randint(0, grid_height - 1)
                
                if (x, y) not in occupied_positions and not self._is_position_blocked(x, y):
                    self._obstacles.append(Obstacle(x, y))
                    occupied_positions.append((x, y))
                    break
    
    def _is_position_blocked(self, x: int, y: int) -> bool:
        """Check if a position is already blocked by an obstacle."""
        return any(obstacle.x == x and obstacle.y == y for obstacle in self._obstacles)
    
    def update_projectiles(self, player: Character, enemy: Character) -> Optional[str]:
        """
        Update all projectiles and check for hits.
        Returns the winner if a character is defeated, None otherwise.
        """
        projectiles_to_remove = []
        winner = None
        
        for projectile in self._projectiles:
            # Update position
            projectile.update()
            
            # Check for collisions
            if projectile.is_out_of_bounds():
                projectiles_to_remove.append(projectile)
                continue
                
            # Convert to integer grid position for collision detection
            grid_x, grid_y = int(projectile.x), int(projectile.y)
            
            # Check for obstacle collision
            if any(obstacle.x == grid_x and obstacle.y == grid_y for obstacle in self._obstacles):
                projectiles_to_remove.append(projectile)
                continue
                
            # Check for player/enemy collision
            if grid_x == player.x and grid_y == player.y:
                if projectile.owner != player:  # Only take damage from enemy projectiles
                    player.take_damage(GameConfig.Combat.PROJECTILE_DAMAGE)
                    projectiles_to_remove.append(projectile)
                    
                    if not player.is_alive():
                        winner = "AI"
            
            if grid_x == enemy.x and grid_y == enemy.y:
                if projectile.owner != enemy:  # Only take damage from player projectiles
                    enemy.take_damage(GameConfig.Combat.PROJECTILE_DAMAGE)
                    projectiles_to_remove.append(projectile)
                    
                    if not enemy.is_alive():
                        winner = "Player"
        
        # Remove projectiles that hit something
        for projectile in projectiles_to_remove:
            if projectile in self._projectiles:
                self._projectiles.remove(projectile)
                
        return winner


class SniperTypeManager:
    """Manages sniper types available in the game."""
    
    def __init__(self):
        self._sniper_types: List[SniperType] = []
        self._load_default_types()
    
    @property
    def sniper_types(self) -> List[SniperType]:
        """Get the list of available sniper types."""
        return self._sniper_types
    
    def _load_default_types(self) -> None:
        """Load the default set of sniper types."""
        sniper_data = [
            {
                "name": "Ghost",
                "color": (150, 150, 255),
                "description": "Fast, high courage",
                "move_limit": 3,
                "power": "piercing"
            },
            {
                "name": "Juggernaut",
                "color": (255, 100, 100),
                "description": "Tanky, bouncing shots",
                "move_limit": 2,
                "power": "bouncing"
            },
            {
                "name": "Scout",
                "color": (100, 255, 100),
                "description": "Quick & nimble",
                "move_limit": 4,
                "power": "fast"
            },
            {
                "name": "Shade",
                "color": (200, 0, 200),
                "description": "Can freeze enemies",
                "move_limit": 3,
                "power": "freezing"
            }
        ]
        
        for data in sniper_data:
            self._sniper_types.append(SniperType.create_from_dict(data))


class GameEngine:
    """
    Main game engine that handles the game state and logic.
    Uses composition to manage game objects and provide high-level game functionality.
    """
    
    def __init__(self):
        """Initialize the game engine with default state."""
        self._state = GameState.MENU
        self._player: Optional[Character] = None
        self._enemy: Optional[Character] = None
        self._winner: Optional[str] = None
        self._player_turn = True
        self._shoot_mode = False
        self._show_debug = False
        self._ai_state = None
        self._ai_turn_started = False
        self._ai_turn_time = 0
        
        # Character selection state
        self._character_select_stage = "player"
        self._selected_candidate = None
        self._show_confirm_popup = False
        
        # Composition: use other managers for specific functionality
        self._object_manager = GameObjectManager()
        self._sniper_manager = SniperTypeManager()
    
    @property
    def state(self) -> str:
        """Get the current game state."""
        return self._state
    
    @state.setter
    def state(self, value: str) -> None:
        """Set the current game state."""
        self._state = value
    
    @property
    def player(self) -> Optional[Character]:
        """Get the player character."""
        return self._player
    
    @property
    def enemy(self) -> Optional[Character]:
        """Get the enemy character."""
        return self._enemy
    
    @property
    def player_turn(self) -> bool:
        """Check if it's the player's turn."""
        return self._player_turn
    
    @property
    def shoot_mode(self) -> bool:
        """Check if the player is in shooting mode."""
        return self._shoot_mode
    
    @shoot_mode.setter
    def shoot_mode(self, value: bool) -> None:
        """Set whether the player is in shooting mode."""
        self._shoot_mode = value
    
    @property
    def winner(self) -> Optional[str]:
        """Get the winner of the game."""
        return self._winner
    
    @property
    def show_debug(self) -> bool:
        """Check if debug info should be shown."""
        return self._show_debug
    
    @property
    def ai_state(self) -> Optional[str]:
        """Get the current AI state."""
        return self._ai_state
    
    @property
    def character_select_stage(self) -> str:
        """Get the current character selection stage."""
        return self._character_select_stage
    
    @property
    def selected_candidate(self) -> Optional[SniperType]:
        """Get the currently selected sniper type candidate."""
        return self._selected_candidate
    
    @selected_candidate.setter
    def selected_candidate(self, value: Optional[SniperType]) -> None:
        """Set the currently selected sniper type candidate."""
        self._selected_candidate = value
    
    @property
    def show_confirm_popup(self) -> bool:
        """Check if the confirmation popup should be shown."""
        return self._show_confirm_popup
    
    @show_confirm_popup.setter
    def show_confirm_popup(self, value: bool) -> None:
        """Set whether the confirmation popup should be shown."""
        self._show_confirm_popup = value
    
    @property
    def obstacles(self) -> List[Obstacle]:
        """Get the list of obstacles."""
        return self._object_manager.obstacles
    
    @property
    def projectiles(self) -> List[Projectile]:
        """Get the list of projectiles."""
        return self._object_manager.projectiles
    
    @property
    def sniper_types(self) -> List[SniperType]:
        """Get the list of available sniper types."""
        return self._sniper_manager.sniper_types
    
    def start_game(self) -> None:
        """Start a new game with the selected characters."""
        if self._player is None or self._enemy is None:
            Debug.log("Cannot start game: player or enemy is not set.")
            return
            
        self._state = GameState.PLAY
        self._player_turn = True
        self._player.start_turn()
        self._winner = None
        self._shoot_mode = False
        
        # Generate obstacles
        self._object_manager.generate_obstacles(
            GameConfig.Combat.OBSTACLE_COUNT,
            self._player,
            self._enemy
        )
    
    def select_character(self, sniper_type: SniperType) -> None:
        """Select a character for the player or enemy."""
        if self._character_select_stage == "player":
            self._player = Character(
                StartPositions.PLAYER_X,
                StartPositions.PLAYER_Y,
                sniper_type
            )
            self._character_select_stage = "enemy"
            self._selected_candidate = None
        else:
            self._enemy = Character(
                StartPositions.ENEMY_X,
                StartPositions.ENEMY_Y,
                sniper_type,
                is_player=False
            )
            self._selected_candidate = None
            self.start_game()
    
    def handle_player_movement(self, grid_x: int, grid_y: int) -> None:
        """Handle player movement to the specified grid position."""
        if not self._player or not self._player_turn:
            return
            
        if self._player.show_range and self._player.can_move():
            dist = abs(grid_x - self._player.x) + abs(grid_y - self._player.y)
            if dist <= self._player.moves_left:
                # Check if destination has an obstacle
                if not any(o.x == grid_x and o.y == grid_y for o in self._object_manager.obstacles):
                    self._player.move_to(grid_x, grid_y)
                    self._player.show_range = False
                    
                    if not self._player.is_alive():
                        self.end_game("AI")
    
    def handle_player_shooting(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle player shooting at the specified mouse position."""
        if not self._player or not self._player_turn or not self._shoot_mode:
            return
            
        if not self._player.can_shoot():
            self._shoot_mode = False
            return
            
        # Calculate direction based on mouse position relative to player
        player_center = GameConfig.Grid.cell_to_pixels(self._player.x, self._player.y)
        player_center = (
            player_center[0] + GameConfig.Grid.SIZE // 2,
            player_center[1] + GameConfig.Grid.SIZE // 2
        )
        
        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        
        # Normalize and snap to cardinal direction
        length = max(0.001, (dx**2 + dy**2)**0.5)  # Avoid division by zero
        dx, dy = dx / length, dy / length
        
        # Round to the nearest cardinal direction
        if abs(dx) > abs(dy):
            dy = 0
            dx = 1 if dx > 0 else -1
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
            
        # Create the projectile
        projectile = self._player.shoot((dx, dy))
        if projectile:
            self._object_manager.projectiles.append(projectile)
            
        self._shoot_mode = False
    
    def toggle_player_range(self) -> None:
        """Toggle display of the player's movement range."""
        if self._player and self._player_turn:
            self._player.show_range = not self._player.show_range
    
    def end_player_turn(self) -> None:
        """End the player's turn and start the enemy's turn."""
        if self._player and self._player_turn:
            self._player.moves_left = 0
            self._player.shots_left = 0
            self._player_turn = False
            self._ai_turn_started = False
    
    def update_game(self) -> None:
        """Update game state, handle projectile movement and collisions."""
        # Update projectiles and check for hits
        if self._state == GameState.PLAY:
            winner = self._object_manager.update_projectiles(self._player, self._enemy)
            if winner:
                self.end_game(winner)
                
            # Handle AI turn if it's not the player's turn
            if not self._player_turn and self._state == GameState.PLAY:
                self._update_enemy_turn()
    
    def _update_enemy_turn(self) -> None:
        """Update the enemy's turn logic."""
        if not self._ai_turn_started:
            self._ai_turn_started = True
            self._ai_turn_time = pygame.time.get_ticks()
            
            # Reset AI state at the beginning of each turn
            self._ai_state = AIState.THINKING
            
            # Set enemy moves and shots
            if self._enemy:
                self._enemy.moves_left = self._enemy.sniper_type.move_limit
                self._enemy.shots_left = 1  # Default 1 shot per turn
                
                Debug.log(f"Enemy turn started with moves: {self._enemy.moves_left}, shots: {self._enemy.shots_left}")
        
        current_time = pygame.time.get_ticks()
        if current_time - self._ai_turn_time >= GameConfig.Animation.AI_TURN_DELAY:
            self._execute_ai_turn()
    
    def _execute_ai_turn(self) -> None:
        """Execute the enemy's turn using the AI."""
        from ai import AI  # Import here to avoid circular dependency
        
        if self._enemy:
            # This will be passed to the AI to allow it to redraw the screen during its turn
            self._ai_state = AI.take_turn(
                None,  # Surface will be provided by the renderer
                self._enemy, 
                self._player, 
                [(o.x, o.y) for o in self._object_manager.obstacles], 
                self._object_manager.projectiles,
                lambda: None  # Actual redraw callback will be set by the game runner
            )
            
            # Start the player's turn again
            self._player_turn = True
            if self._player:
                self._player.start_turn()
            self._ai_turn_started = False
    
    def end_game(self, winner: str) -> None:
        """End the game with the specified winner."""
        self._state = GameState.GAME_OVER
        self._winner = winner
    
    def toggle_debug(self) -> None:
        """Toggle display of debug information."""
        self._show_debug = not self._show_debug
    
    def reset(self) -> None:
        """Reset the game to the initial state."""
        self._state = GameState.MENU
        self._player = None
        self._enemy = None
        self._winner = None
        self._player_turn = True
        self._shoot_mode = False
        self._object_manager.clear()
        self._character_select_stage = "player"
        self._selected_candidate = None
        self._show_confirm_popup = False