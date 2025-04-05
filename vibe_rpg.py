import pygame
import random  # Import random for generating new levels

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

# Map layout: 1 = wall, 0 = open space
map_layout = [
    [1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1]
]

# Reposition the treasure to a valid open space
while True:
    treasure_pos = [random.randint(1, len(map_layout[0]) - 2), random.randint(1, len(map_layout) - 2)]
    if map_layout[treasure_pos[1]][treasure_pos[0]] == 0:  # Ensure it's not a wall
        break

enemies = [{"pos": [3, 2], "health": 5, "attack": 2}]

def draw_cube(x, y, color, depth=10, alpha=150):
    """Draw a translucent cube at grid position (x, y) with the given color and depth."""
    # Create a temporary surface with transparency
    cube_surface = pygame.Surface((GRID_SIZE + depth, GRID_SIZE + depth), pygame.SRCALPHA)
    
    # Coordinates for the base of the cube
    base_x = depth
    base_y = depth

    # Front face
    front_rect = [
        (base_x, base_y + GRID_SIZE),
        (base_x, base_y),
        (base_x + GRID_SIZE, base_y),
        (base_x + GRID_SIZE, base_y + GRID_SIZE)
    ]
    pygame.draw.polygon(cube_surface, (*color, alpha), front_rect)  # Add alpha to the color

    # Top face
    top_rect = [
        (base_x, base_y),
        (base_x + GRID_SIZE, base_y),
        (base_x + GRID_SIZE - depth, base_y - depth),
        (base_x - depth, base_y - depth)
    ]
    pygame.draw.polygon(cube_surface, (*[c // 1.2 for c in color], alpha), top_rect)

    # Left face
    left_rect = [
        (base_x, base_y),
        (base_x - depth, base_y - depth),
        (base_x - depth, base_y + GRID_SIZE - depth),
        (base_x, base_y + GRID_SIZE)
    ]
    pygame.draw.polygon(cube_surface, (*[c // 1.5 for c in color], alpha), left_rect)

    # Right face
    right_rect = [
        (base_x + GRID_SIZE, base_y),
        (base_x + GRID_SIZE - depth, base_y - depth),
        (base_x + GRID_SIZE - depth, base_y + GRID_SIZE - depth),
        (base_x + GRID_SIZE, base_y + GRID_SIZE)
    ]
    pygame.draw.polygon(cube_surface, (*[c // 1.3 for c in color], alpha), right_rect)

    # Blit the translucent cube surface onto the main screen
    screen.blit(cube_surface, (x * GRID_SIZE - depth, y * GRID_SIZE - depth))

def draw_map_with_depth():
    for row in range(len(map_layout)):
        for col in range(len(map_layout[row])):
            if (map_layout[row][col] == 1):
                draw_cube(col, row, BLACK)
            else:
                draw_cube(col, row, WHITE)

def draw_player_with_depth():
    draw_cube(player_pos[0], player_pos[1], PLAYER_COLOR)

def draw_treasure_with_depth():
    draw_cube(treasure_pos[0], treasure_pos[1], TREASURE_COLOR)

def draw_enemies_with_depth():
    for enemy in enemies:
        draw_cube(enemy["pos"][0], enemy["pos"][1], ENEMY_COLOR)

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

def next_level():
    global map_layout, player_pos, treasure_pos, enemies

    # Generate a new random map layout (simple example)
    map_layout = [
        [1 if x == 0 or x == len(map_layout[0]) - 1 or y == 0 or y == len(map_layout) - 1 else 0
         for x in range(len(map_layout[0]))]
        for y in range(len(map_layout))
    ]

    # Reposition the player
    player_pos = [1, 1]  # Reset player to starting position

    # Reposition the treasure to a valid open space
    while True:
        treasure_pos = [random.randint(1, len(map_layout[0]) - 2), random.randint(1, len(map_layout) - 2)]
        if map_layout[treasure_pos[1]][treasure_pos[0]] == 0:  # Ensure it's not a wall
            break

    print(f"Treasure placed at: {treasure_pos}")

    # Add new enemies (increase difficulty by adding more enemies)
    enemies = [{"pos": [random.randint(1, len(map_layout[0]) - 2), random.randint(1, len(map_layout) - 2)],
                "health": 5, "attack": 2} for _ in range(len(enemies) + 1)]  # Add one more enemy per level

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

    # Check for win condition (player reaches treasure)
    if player_pos == treasure_pos:
        print("You found the treasure! Advancing to the next level...")
        next_level()

    # Inside the main game loop
    print(f"Player position: {player_pos}, Treasure position: {treasure_pos}")

    # Update game visuals
    screen.fill(WHITE)
    draw_map_with_depth()
    draw_player_with_depth()
    draw_treasure_with_depth()
    draw_enemies_with_depth()
    draw_stats()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()