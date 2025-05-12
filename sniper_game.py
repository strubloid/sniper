import pygame
from dataclasses import dataclass
import os

# === Setup ===
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 720
GRID_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sniper Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
RED = (200, 50, 50)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255, 100)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

@dataclass
class SniperType:
    name: str
    sprite: pygame.Surface
    color: tuple
    description: str
    move_limit: int
    power: str
    projectiles_per_turn: int = 1

@dataclass
class Character:
    x: int
    y: int
    sniper_type: SniperType
    health: int = 100
    max_health: int = 100
    is_player: bool = True
    moves_left: int = 0
    shots_left: int = 0
    show_range: bool = False

    def start_turn(self):
        self.moves_left = self.sniper_type.move_limit
        self.shots_left = self.sniper_type.projectiles_per_turn
        self.show_range = False

    def draw(self, surface):
        sprite = pygame.transform.scale(self.sniper_type.sprite, (GRID_SIZE, GRID_SIZE))
        surface.blit(sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def draw_range(self, surface):
        if not self.show_range or self.moves_left == 0:
            return
        for dx in range(-self.moves_left, self.moves_left + 1):
            for dy in range(-self.moves_left, self.moves_left + 1):
                if abs(dx) + abs(dy) <= self.moves_left:
                    tx, ty = self.x + dx, self.y + dy
                    if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                        s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                        s.fill(BLUE)
                        surface.blit(s, (tx * GRID_SIZE, ty * GRID_SIZE))

@dataclass
class Projectile:
    x: int
    y: int
    dx: int
    dy: int
    color: tuple
    owner: Character

# === Load Sniper Types ===
sniper_types = []
for name, desc, color, limit, power in [
    ("Ghost", "Fast, high courage", (150, 150, 255), 3, "piercing"),
    ("Juggernaut", "Tanky, bouncing shots", (255, 100, 100), 2, "bouncing"),
    ("Scout", "Quick & nimble", (100, 255, 100), 4, "fast"),
    ("Shade", "Can freeze enemies", (200, 0, 200), 3, "freezing")
]:
    sprite_path = os.path.join(ASSETS_DIR, f"{name.lower()}.png")
    sprite = pygame.image.load(sprite_path).convert_alpha()
    sniper_types.append(SniperType(name, sprite, color, desc, limit, power))

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_menu():
    screen.fill(BLACK)
    screen.blit(big_font.render("SNIPER GAME", True, YELLOW), (300, 100))
    
    # Draw menu options
    menu_options = ["Play", "Scoreboard", "Quit"]
    button_height = 50
    button_width = 200
    button_spacing = 20
    button_rects = []
    
    for i, option in enumerate(menu_options):
        button_y = 250 + i * (button_height + button_spacing)
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, button_y, button_width, button_height)
        pygame.draw.rect(screen, GRAY, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        
        text = font.render(option, True, WHITE)
        text_x = button_rect.x + (button_rect.width - text.get_width()) // 2
        text_y = button_rect.y + (button_rect.height - text.get_height()) // 2
        screen.blit(text, (text_x, text_y))
        button_rects.append((button_rect, option))
    
    try:
        banner = pygame.image.load(os.path.join(ASSETS_DIR, "title_characters.png"))
        screen.blit(banner, (320, 170))
    except:
        pass
    
    return button_rects

def draw_scoreboard():
    screen.fill(BLACK)
    screen.blit(big_font.render("SCOREBOARD", True, YELLOW), (300, 100))
    
    # In a real implementation, you'd load scores from a file
    # For now, we'll just display placeholder text
    screen.blit(font.render("No scores yet! Play a game to record your score.", True, WHITE), (250, 200))
    screen.blit(font.render("Press ESC to return to menu", True, WHITE), (300, 400))

def draw_character_select():
    title = "Select Your Character" if game.character_select_stage == "player" else "Select AI Opponent"
    screen.blit(big_font.render(title, True, WHITE), (250, 30))
    for i, sniper in enumerate(sniper_types):
        rect = pygame.Rect(100, 100 + i * 60, 400, 50)
        pygame.draw.rect(screen, GRAY if sniper == game.selected_candidate else BLACK, rect)
        text = font.render(f"{sniper.name}: {sniper.description}", True, WHITE)
        screen.blit(text, (110, 110 + i * 60))
        sprite = pygame.transform.scale(sniper.sprite, (32, 32))
        screen.blit(sprite, (450, 105 + i * 60))

    if game.selected_candidate:
        pygame.draw.rect(screen, GRAY, (100, 400, 600, 100))
        info = [
            f"Name: {game.selected_candidate.name}",
            f"Power: {game.selected_candidate.power}",
            f"Move Limit: {game.selected_candidate.move_limit}"
        ]
        for i, line in enumerate(info):
            screen.blit(font.render(line, True, WHITE), (110, 410 + i * 20))

def draw_confirmation_popup():
    pygame.draw.rect(screen, BLACK, (200, 250, 400, 150))
    pygame.draw.rect(screen, WHITE, (200, 250, 400, 150), 2)
    txt = big_font.render("Are you sure?", True, YELLOW)
    screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 270))
    yes_rect = pygame.Rect(240, 320, 100, 40)
    no_rect = pygame.Rect(460, 320, 100, 40)
    pygame.draw.rect(screen, (0, 255, 0), yes_rect)
    pygame.draw.rect(screen, (255, 0, 0), no_rect)
    screen.blit(font.render("Yes", True, BLACK), (270, 330))
    screen.blit(font.render("No", True, BLACK), (490, 330))
    return yes_rect, no_rect

def draw_turn_info():
    txt = f"{game.player.sniper_type.name}'s Turn — Moves: {game.player.moves_left} | Shots: {game.player.shots_left}"
    text = font.render(txt, True, YELLOW)
    screen.blit(text, (20, 50))  # Adjusted position to avoid overlap

def draw_instructions():
    text = font.render("Click your character to move | Press SPACE to shoot | Click a tile to fire", True, WHITE)
    screen.blit(text, (20, SCREEN_HEIGHT - 50))  # Adjusted position to avoid overlap

def draw_hud_grid():
    # Draw HUD elements in a grid layout with 10px spacing
    hud_x, hud_y = 20, SCREEN_HEIGHT - 150
    spacing = 10

    # Player health
    pygame.draw.rect(screen, RED, (hud_x, hud_y, 200, 20))
    pygame.draw.rect(screen, GREEN, (hud_x, hud_y, 200 * (game.player.health / game.player.max_health), 20))
    screen.blit(font.render(f"Player HP: {game.player.health}", True, WHITE), (hud_x + 210, hud_y))

    # Enemy health
    hud_y += 30 + spacing
    pygame.draw.rect(screen, RED, (hud_x, hud_y, 200, 20))
    pygame.draw.rect(screen, GREEN, (hud_x, hud_y, 200 * (game.enemy.health / game.enemy.max_health), 20))
    screen.blit(font.render(f"Enemy HP: {game.enemy.health}", True, WHITE), (hud_x + 210, hud_y))

    # Player moves and shots
    hud_y += 30 + spacing
    screen.blit(font.render(f"Moves Left: {game.player.moves_left}", True, WHITE), (hud_x, hud_y))
    screen.blit(font.render(f"Shots Left: {game.player.shots_left}", True, WHITE), (hud_x + 150, hud_y))

    # Turn indicator
    hud_y += 30 + spacing
    turn_text = "Your Turn" if game.player_turn else "AI's Turn"
    screen.blit(font.render(turn_text, True, GREEN if game.player_turn else RED), (hud_x, hud_y))

def draw_projectiles():
    for p in game.projectiles:
        pygame.draw.circle(screen, p.color, (p.x * GRID_SIZE + GRID_SIZE // 2, p.y * GRID_SIZE + GRID_SIZE // 2), 6)

def handle_projectile_logic():
    for p in game.projectiles[:]:
        p.x += p.dx
        p.y += p.dy
        if not (0 <= p.x < GRID_WIDTH and 0 <= p.y < GRID_HEIGHT):
            game.projectiles.remove(p)
        elif p.x == game.enemy.x and p.y == game.enemy.y:
            game.enemy.health -= 20
            game.projectiles.remove(p)
            
            # Check if enemy is defeated
            if game.enemy.health <= 0:
                game.end_game("Player")
        elif p.x == game.player.x and p.y == game.player.y:
            game.player.health -= 20
            game.projectiles.remove(p)
            
            # Check if player is defeated
            if game.player.health <= 0:
                game.end_game("AI")

def draw_turn_indicator():
    if game.game_state == "play":
        if game.player_turn:
            text = big_font.render("Your Turn", True, GREEN)
        else:
            text = big_font.render("AI's Turn", True, RED)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 20))

def draw_end_turn_button():
    if game.game_state == "play" and game.player_turn:
        button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 120, 40)
        pygame.draw.rect(screen, GRAY, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        text = font.render("End Turn", True, WHITE)
        screen.blit(text, (button_rect.x + 10, button_rect.y + 10))
        return button_rect
    return None

def generate_obstacles(player, enemy):
    import random
    obstacles = []
    for _ in range(20):  # Generate 20 random obstacles
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in [(player.x, player.y), (enemy.x, enemy.y)]:
            obstacles.append((x, y))
    return obstacles

class Game:
    def __init__(self):
        self.game_state = "menu"
        self.player = None
        self.enemy = None
        self.projectiles = []
        self.character_select_stage = "player"
        self.selected_candidate = None
        self.show_confirm_popup = False
        self.player_turn = True
        self.shoot_mode = False
        self.obstacles = []  # Initialize as empty
        self.winner = None
        self.show_debug = False
        self.ai_state = None
        self.scores = []  # Store game scores

    def start_game(self):
        self.obstacles = generate_obstacles(self.player, self.enemy)

    def handle_mouse_click(self, pos):
        x, y = pos[0] // GRID_SIZE, pos[1] // GRID_SIZE

        if self.game_state == "menu":
            # Handle menu button clicks
            menu_buttons = draw_menu()
            for rect, option in menu_buttons:
                if rect.collidepoint(pos):
                    if option == "Play":
                        self.game_state = "select"
                    elif option == "Scoreboard":
                        self.game_state = "scoreboard"
                    elif option == "Quit":
                        pygame.quit()
                        import sys
                        sys.exit()
        elif self.game_state == "select":
            if self.show_confirm_popup:
                yes, no = draw_confirmation_popup()
                if yes.collidepoint(pos):
                    if self.character_select_stage == "player":
                        self.player = Character(5, 5, self.selected_candidate)
                        self.character_select_stage = "enemy"
                    else:
                        self.enemy = Character(15, 5, self.selected_candidate, is_player=False)
                        self.game_state = "play"
                        self.player.start_turn()
                        self.start_game()
                    self.selected_candidate = None
                    self.show_confirm_popup = False
                elif no.collidepoint(pos):
                    self.show_confirm_popup = False
            else:
                for i, sniper in enumerate(sniper_types):
                    rect = pygame.Rect(100, 100 + i * 60, 400, 50)
                    if rect.collidepoint(pos):
                        self.selected_candidate = sniper
                        self.show_confirm_popup = True
        elif self.game_state == "play" and self.player_turn:  # Only process game clicks if it's the player's turn
            if self.shoot_mode and self.player.shots_left > 0:
                game.handle_shooting(pos)
                self.shoot_mode = False
            elif self.shoot_mode:
                # Reset shoot_mode if shooting conditions are not met
                self.shoot_mode = False
            elif x == self.player.x and y == self.player.y:
                # Toggle range display without ending the turn
                self.player.show_range = not self.player.show_range
            elif self.player.show_range and self.player.moves_left > 0:
                dist = abs(x - self.player.x) + abs(y - self.player.y)
                if dist <= self.player.moves_left:
                    self.player.x, self.player.y = x, y
                    self.player.moves_left -= dist
                    self.player.health -= dist * 5  # Lose health for each tile moved
                    self.player.show_range = False

                    if self.player.health <= 0:
                        self.end_game("AI")

    def enemy_turn(self):
        # AI logic for the enemy to attack the player
        dx, dy = self.player.x - self.enemy.x, self.player.y - self.enemy.y
        move_limit = self.enemy.sniper_type.move_limit

        # Display AI state
        self.ai_state = "AIMING"
        pygame.time.delay(500)  # Delay to simulate aiming

        # Check if player is in line of sight (same row or column) and shoot if possible
        if self.enemy.shots_left > 0:
            if dx == 0 or dy == 0:  # Player is in same row or column
                self.ai_state = "SHOOTING"
                pygame.time.delay(500)  # Delay to simulate shooting
                
                # Determine shooting direction
                shoot_dx, shoot_dy = 0, 0
                if dx == 0:  # Same column
                    shoot_dy = 1 if dy > 0 else -1
                else:  # Same row
                    shoot_dx = 1 if dx > 0 else -1
                
                # Create projectile
                self.projectiles.append(Projectile(self.enemy.x, self.enemy.y, shoot_dx, shoot_dy, self.enemy.sniper_type.color, self.enemy))
                self.enemy.shots_left -= 1
                
                # After shooting, redraw
                screen.fill(BLACK)
                draw_grid()
                self.draw_obstacles()
                self.player.draw(screen)
                self.enemy.draw(screen)
                draw_projectiles()
                draw_hud_grid()
                draw_turn_indicator()
                self.draw_debug_info()
                pygame.display.flip()
                pygame.time.delay(500)  # Delay so we can see the projectile
            elif abs(dx) + abs(dy) == 1 and self.enemy.shots_left > 0:  # If the player is adjacent
                self.ai_state = "SHOOTING"
                pygame.time.delay(500)  # Delay to simulate shooting
                self.player.health -= 20  # Attack the player
                self.enemy.shots_left -= 1

        # If we didn't shoot or need to move closer
        if self.enemy.moves_left > 0:
            # Calculate possible moves within the move limit
            possible_moves = []
            for mx in range(-move_limit, move_limit + 1):
                for my in range(-move_limit, move_limit + 1):
                    if abs(mx) + abs(my) <= move_limit:
                        new_x, new_y = self.enemy.x + mx, self.enemy.y + my
                        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                            if (new_x, new_y) not in self.obstacles and (new_x, new_y) != (self.player.x, self.player.y):
                                possible_moves.append((new_x, new_y))

            # Choose the move that gets closest to the player
            best_move = min(possible_moves, key=lambda pos: abs(pos[0] - self.player.x) + abs(pos[1] - self.player.y), default=None)

            if best_move:
                distance_moved = abs(best_move[0] - self.enemy.x) + abs(best_move[1] - self.enemy.y)
                if distance_moved <= self.enemy.moves_left:  # Ensure the move is within the remaining moves
                    # Move tile by tile with animation
                    path = self.calculate_path(self.enemy.x, self.enemy.y, best_move[0], best_move[1])
                    for path_x, path_y in path:
                        # Move one tile at a time
                        self.enemy.x, self.enemy.y = path_x, path_y
                        
                        # Redraw the screen to show movement
                        screen.fill(BLACK)
                        draw_grid()
                        self.draw_obstacles()
                        self.player.draw(screen)
                        self.enemy.draw(screen)
                        draw_projectiles()
                        draw_hud_grid()
                        draw_turn_indicator()
                        self.draw_debug_info()
                        pygame.display.flip()
                        
                        # Delay between each tile movement
                        pygame.time.delay(300)
                        
                    self.enemy.moves_left -= distance_moved

        # Ensure the AI ends its turn if no moves or shots are left
        self.ai_state = "END"
        pygame.time.delay(500)  # Delay to simulate end of turn
        self.enemy.moves_left = 0
        self.enemy.shots_left = 0
        self.player_turn = True  # Automatically pass the turn back to the player
        self.player.start_turn()  # Reset player moves and shots for the next turn

    def calculate_path(self, start_x, start_y, end_x, end_y):
        """Calculate a path from start to end position, moving one tile at a time"""
        path = []
        current_x, current_y = start_x, start_y
        
        while (current_x, current_y) != (end_x, end_y):
            # Move horizontally or vertically (whichever is larger)
            if abs(end_x - current_x) > abs(end_y - current_y):
                current_x += 1 if end_x > current_x else -1
            else:
                current_y += 1 if end_y > current_y else -1
            
            path.append((current_x, current_y))
            
            # If we've somehow reached an obstacle, stop
            if (current_x, current_y) in self.obstacles:
                path.pop()  # Remove the last move (which was into an obstacle)
                break
                
        return path

    def end_game(self, winner):
        self.game_state = "game_over"
        self.winner = winner

    def draw_obstacles(self):
        for x, y in self.obstacles:
            pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def handle_shooting(self, mouse_pos):
        # Shooting logic based on mouse direction
        player_center = (self.player.x * GRID_SIZE + GRID_SIZE // 2, self.player.y * GRID_SIZE + GRID_SIZE // 2)
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
        self.projectiles.append(Projectile(self.player.x, self.player.y, dx, dy, self.player.sniper_type.color, self.player))
        self.player.shots_left -= 1

    def draw_shooting_arrow(self, mouse_pos):
        # Draw an arrow pointing in the direction of the mouse
        player_center = (self.player.x * GRID_SIZE + GRID_SIZE // 2, self.player.y * GRID_SIZE + GRID_SIZE // 2)
        pygame.draw.line(screen, YELLOW, player_center, mouse_pos, 3)

    def draw_game_over(self):
        if self.game_state == "game_over":
            screen.fill(BLACK)
            text = big_font.render(f"Game Over! {self.winner} Wins!", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

    def draw_debug_info(self):
        if self.show_debug:
            debug_text = [
                f"AI State: {self.ai_state}",
                f"AIMING: {self.ai_state == 'AIMING'}",
                f"SHOOTING: {self.ai_state == 'SHOOTING'}",
                f"END: {self.ai_state == 'END'}"
            ]
            for i, line in enumerate(debug_text):
                screen.blit(font.render(line, True, WHITE), (20, 20 + i * 20))

    def toggle_debug(self):
        self.show_debug = not self.show_debug

# Add a button to toggle debug info
def draw_debug_button():
    button_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 120, 40)
    pygame.draw.rect(screen, GRAY, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    text = font.render("Debug", True, WHITE)
    screen.blit(text, (button_rect.x + 10, button_rect.y + 10))
    return button_rect

# Update the main loop to use the Game class
if __name__ == "__main__":
    game = Game()

    running = True
    end_turn_clicked = False
    debug_button_clicked = False
    
    while running:
        screen.fill(BLACK)
        
        # Store button rectangles outside the event loop
        end_turn_button_rect = None
        debug_button_rect = None
        if game.game_state == "play":
            end_turn_button_rect = draw_end_turn_button()
            debug_button_rect = draw_debug_button()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Handle button clicks here (outside of rendering)
                if game.game_state == "play":
                    if end_turn_button_rect and end_turn_button_rect.collidepoint(mouse_pos) and game.player_turn:
                        # End Turn button clicked
                        game.player.moves_left = 0
                        game.player.shots_left = 0
                        game.player_turn = False
                        game.enemy.start_turn()
                        continue  # Skip other click handling
                        
                    if debug_button_rect and debug_button_rect.collidepoint(mouse_pos):
                        # Debug button clicked
                        game.toggle_debug()
                        continue  # Skip other click handling
                
                # Handle other mouse clicks
                game.handle_mouse_click(mouse_pos)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Cancel actions with ESC key
                    if game.game_state == "play":
                        if game.shoot_mode:
                            game.shoot_mode = False
                        elif game.player.show_range:
                            game.player.show_range = False
                    elif game.game_state == "scoreboard" or game.game_state == "game_over":
                        game.game_state = "menu"
                    elif game.game_state == "select" and game.show_confirm_popup:
                        game.show_confirm_popup = False
                elif event.key == pygame.K_SPACE and game.game_state == "play":
                    game.shoot_mode = True
                elif event.key == pygame.K_RETURN and game.game_state == "menu":
                    game.game_state = "select"

        # Render the game based on its state
        if game.game_state == "menu":
            draw_menu()
        elif game.game_state == "scoreboard":
            draw_scoreboard()
        elif game.game_state == "select":
            draw_character_select()
            if game.show_confirm_popup:
                draw_confirmation_popup()
        elif game.game_state == "play":
            draw_grid()
            game.draw_obstacles()
            game.player.draw_range(screen)
            game.player.draw(screen)
            game.enemy.draw(screen)
            draw_projectiles()
            draw_hud_grid()
            draw_instructions()
            draw_turn_indicator()
            
            # Draw buttons (but handle clicks in event section)
            draw_end_turn_button()
            draw_debug_button()
            
            game.draw_debug_info()
            handle_projectile_logic()

            if game.shoot_mode and game.player.shots_left > 0:
                mouse_pos = pygame.mouse.get_pos()
                game.draw_shooting_arrow(mouse_pos)
                
            # Process AI turn if it's not the player's turn
            if not game.player_turn:
                game.enemy_turn()
                
        elif game.game_state == "game_over":
            game.draw_game_over()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
