import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 240, 200
GRID_SIZE = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 128, 255)
TREASURE_COLOR = (255, 223, 0)
ENEMY_COLOR = (255, 0, 0)  # Red color for enemies

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minimalist RPG")
clock = pygame.time.Clock()

# Player setup
player_pos = [1, 1]  # Start on grid
player_stats = {"health": 10, "attack": 3}
treasure_pos = [4, 4]  # Example treasure location
enemies = [{"pos": [3, 2], "health": 5, "attack": 2}]

# Map layout: 1 = wall, 0 = open space
map_layout = [
    [1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1]
]

def draw_map():
    for row in range(len(map_layout)):
        for col in range(len(map_layout[row])):
            rect = pygame.Rect(col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if map_layout[row][col] == 1:
                pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)

def draw_player():
    pygame.draw.rect(screen, PLAYER_COLOR, 
                     (player_pos[0] * GRID_SIZE, player_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_treasure():
    pygame.draw.rect(screen, TREASURE_COLOR, 
                     (treasure_pos[0] * GRID_SIZE, treasure_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, 
                         (enemy["pos"][0] * GRID_SIZE, enemy["pos"][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_stats():
    font = pygame.font.Font(None, 24)
    health_text = font.render(f"Health: {player_stats['health']}", True, BLACK)
    screen.blit(health_text, (10, SCREEN_HEIGHT - 30))

def combat(enemy):
    while player_stats["health"] > 0 and enemy["health"] > 0:
        # Player attacks
        enemy["health"] -= player_stats["attack"]
        if enemy["health"] <= 0:
            print("Enemy defeated!")
            return True  # Enemy defeated

        # Enemy attacks
        player_stats["health"] -= enemy["attack"]
        if player_stats["health"] <= 0:
            print("You were defeated!")
            return False  # Player defeated

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and map_layout[player_pos[1]][player_pos[0] - 1] == 0:
        player_pos[0] -= 1
    if keys[pygame.K_RIGHT] and map_layout[player_pos[1]][player_pos[0] + 1] == 0:
        player_pos[0] += 1
    if keys[pygame.K_UP] and map_layout[player_pos[1] - 1][player_pos[0]] == 0:
        player_pos[1] -= 1
    if keys[pygame.K_DOWN] and map_layout[player_pos[1] + 1][player_pos[0]] == 0:
        player_pos[1] += 1

    # Check for combat
    for enemy in enemies:
        if player_pos == enemy["pos"]:
            if not combat(enemy):
                running = False  # End game if player loses
            else:
                enemies.remove(enemy)  # Remove defeated enemy

    # Update game visuals
    screen.fill(WHITE)
    draw_map()
    draw_player()
    draw_treasure()
    draw_enemies()  # Draw enemies
    draw_stats()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()