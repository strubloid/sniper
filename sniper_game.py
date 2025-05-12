
import pygame
from dataclasses import dataclass
import os
import sys

# === Init ===
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sniper Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

# === Colors ===
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BLUE = (100, 100, 255, 100)

# === Sniper Types ===
@dataclass
class SniperType:
    name: str
    sprite_path: str
    description: str
    move_limit: int

sprite_dir = os.path.join(os.path.dirname(__file__), 'assets')
sniper_types = [
    SniperType("Ghost", os.path.join(sprite_dir, "ghost.png"), "Fast, high courage", 2),
    SniperType("Juggernaut", os.path.join(sprite_dir, "juggernaut.png"), "Tanky, strong block", 1),
    SniperType("Scout", os.path.join(sprite_dir, "scout.png"), "High mobility, regen", 3),
    SniperType("Shade", os.path.join(sprite_dir, "shade.png"), "Stealthy and tricky", 2),
]

@dataclass
class Character:
    x: int
    y: int
    sniper_type: SniperType
    moves_left: int = 0
    is_player: bool = True
    show_range: bool = False

    def start_turn(self):
        self.moves_left = self.sniper_type.move_limit
        self.show_range = False

    def draw(self, surface):
        sprite = pygame.image.load(self.sniper_type.sprite_path)
        sprite = pygame.transform.scale(sprite, (GRID_SIZE, GRID_SIZE))
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

# === Game State ===
game_state = "menu"
selected_index = 0
player = None
enemy = None
character_select_stage = "player"
player_turn = True
turn_label_timer = 120

# === UI Functions ===
def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_menu():
    screen.fill(BLACK)
    screen.blit(big_font.render("Sniper Game", True, WHITE), (250, 100))
    screen.blit(font.render("Press ENTER to Start", True, YELLOW), (280, 200))

def draw_character_select():
    screen.fill(BLACK)
    title = big_font.render("Select Your Character" if character_select_stage == "player" else "Select AI Opponent", True, WHITE)
    screen.blit(title, (150, 30))
    for i, sniper in enumerate(sniper_types):
        color = YELLOW if i == selected_index else WHITE
        text = font.render(f"{sniper.name}: {sniper.description}", True, color)
        screen.blit(text, (100, 120 + i * 60))
        sprite = pygame.image.load(sniper.sprite_path)
        sprite = pygame.transform.scale(sprite, (32, 32))
        screen.blit(sprite, (450, 115 + i * 60))

def draw_turn_info():
    who = player.sniper_type.name if player_turn else enemy.sniper_type.name
    moves = player.moves_left if player_turn else "AI"
    label = f"{who}'s Turn — {moves} Moves Left"
    text = big_font.render(label, True, YELLOW)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 5))

def handle_mouse_click(pos):
    global player_turn
    if player_turn:
        tile_x, tile_y = pos[0] // GRID_SIZE, pos[1] // GRID_SIZE
        if tile_x == player.x and tile_y == player.y:
            player.show_range = True
        elif player.show_range:
            dist = abs(tile_x - player.x) + abs(tile_y - player.y)
            if dist <= player.moves_left:
                player.x, player.y = tile_x, tile_y
                player.moves_left -= dist
                player.show_range = False
                if player.moves_left <= 0:
                    player_turn = False
                    enemy.start_turn()

# === Main Loop ===
running = True
while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "play":
            handle_mouse_click(pygame.mouse.get_pos())

    if game_state == "menu":
        draw_menu()
        if keys[pygame.K_RETURN]:
            game_state = "select"

    elif game_state == "select":
        draw_character_select()
        if keys[pygame.K_UP]: selected_index = (selected_index - 1) % len(sniper_types)
        if keys[pygame.K_DOWN]: selected_index = (selected_index + 1) % len(sniper_types)
        if keys[pygame.K_RETURN]:
            if character_select_stage == "player":
                player = Character(5, 5, sniper_types[selected_index])
                character_select_stage = "enemy"
            elif character_select_stage == "enemy":
                enemy = Character(10, 10, sniper_types[selected_index], is_player=False)
                game_state = "play"
                player.start_turn()
                turn_label_timer = 120

    elif game_state == "play":
        draw_grid()
        if turn_label_timer > 0:
            draw_turn_info()
            turn_label_timer -= 1
        player.draw_range(screen)
        player.draw(screen)
        enemy.draw(screen)
        if not player_turn:
            if abs(enemy.x - player.x) > abs(enemy.y - player.y):
                enemy.x += 1 if enemy.x < player.x else -1
            else:
                enemy.y += 1 if enemy.y < player.y else -1
            player_turn = True
            player.start_turn()
            turn_label_timer = 120

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
