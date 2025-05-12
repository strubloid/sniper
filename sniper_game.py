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
    screen.blit(font.render("Press ENTER to Start", True, WHITE), (360, 180))
    try:
        banner = pygame.image.load(os.path.join(ASSETS_DIR, "title_characters.png"))
        screen.blit(banner, (320, 250))
    except:
        pass

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

    def start_game(self):
        self.obstacles = generate_obstacles(self.player, self.enemy)

    def handle_mouse_click(self, pos):
        x, y = pos[0] // GRID_SIZE, pos[1] // GRID_SIZE

        if self.game_state == "select":
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
        elif self.game_state == "play":
            if self.shoot_mode and self.player.shots_left > 0:
                dx, dy = x - self.player.x, y - self.player.y
                if abs(dx) + abs(dy) == 1:
                    self.projectiles.append(Projectile(self.player.x, self.player.y, dx, dy, self.player.sniper_type.color, self.player))
                    self.player.shots_left -= 1
                    self.shoot_mode = False
            elif self.shoot_mode:
                # Reset shoot_mode if shooting conditions are not met
                self.shoot_mode = False
            elif x == self.player.x and y == self.player.y:
                self.player.show_range = True
            elif self.player.show_range and self.player.moves_left > 0:
                dist = abs(x - self.player.x) + abs(y - self.player.y)
                if dist <= self.player.moves_left:
                    self.player.x, self.player.y = x, y
                    self.player.moves_left -= dist
                    self.player.show_range = False
                    if self.player.moves_left <= 0 and self.player.shots_left <= 0:
                        self.player_turn = False
                        self.enemy.start_turn()

    def enemy_turn(self):
        # AI logic for the enemy to attack the player
        dx, dy = self.player.x - self.enemy.x, self.player.y - self.enemy.y
        move_limit = self.enemy.sniper_type.move_limit

        if abs(dx) + abs(dy) == 1 and self.enemy.shots_left > 0:  # If the player is adjacent and shots are available
            self.player.health -= 20  # Attack the player
            self.enemy.shots_left -= 1
        else:
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
                self.enemy.moves_left -= abs(best_move[0] - self.enemy.x) + abs(best_move[1] - self.enemy.y)
                self.enemy.x, self.enemy.y = best_move

        # End the enemy's turn if no moves or shots are left
        if self.enemy.moves_left <= 0 and self.enemy.shots_left <= 0:
            self.enemy.moves_left = 0
            self.enemy.shots_left = 0
            self.player.start_turn()

    def draw_obstacles(self):
        for x, y in self.obstacles:
            pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def handle_shooting(self, direction):
        # Shooting logic for all directions
        directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        dx, dy = directions[direction]
        self.projectiles.append(Projectile(self.player.x, self.player.y, dx, dy, self.player.sniper_type.color, self.player))
        self.player.shots_left -= 1

    def draw_shooting_arrow(self, mouse_pos):
        # Draw an arrow pointing in the direction of the mouse
        player_center = (self.player.x * GRID_SIZE + GRID_SIZE // 2, self.player.y * GRID_SIZE + GRID_SIZE // 2)
        pygame.draw.line(screen, YELLOW, player_center, mouse_pos, 3)

# Update the main loop to use the Game class
if __name__ == "__main__":
    game = Game()

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_mouse_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_state == "play":
                    game.shoot_mode = True
                if event.key == pygame.K_RETURN and game.game_state == "menu":
                    game.game_state = "select"

        if game.game_state == "menu":
            draw_menu()
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
            end_turn_button = draw_end_turn_button()
            if end_turn_button and event.type == pygame.MOUSEBUTTONDOWN and end_turn_button.collidepoint(event.pos):
                game.player_turn = False
                game.enemy_turn()
            handle_projectile_logic()

            if game.shoot_mode and game.player.shots_left > 0:
                mouse_pos = pygame.mouse.get_pos()
                game.draw_shooting_arrow(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Determine direction based on mouse position
                    player_center = (game.player.x * GRID_SIZE + GRID_SIZE // 2, game.player.y * GRID_SIZE + GRID_SIZE // 2)
                    dx, dy = mouse_pos[0] - player_center[0], mouse_pos[1] - player_center[1]
                    if abs(dx) > abs(dy):
                        direction = "right" if dx > 0 else "left"
                    else:
                        direction = "down" if dy > 0 else "up"
                    game.handle_shooting(direction)
                    game.shoot_mode = False

            if not game.player_turn:
                game.enemy_turn()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
