import pygame
import random
from collections import deque
import os

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 400
GRID_SIZE = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 128, 255)
TREASURE_COLOR = (255, 223, 0)
ENEMY_COLOR = (255, 0, 0)
HEALTH_COLOR = (0, 255, 0)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vube")
clock = pygame.time.Clock()

# Global variables
player_pos = [1, 1]
player_stats = {"health": 10, "attack": 3}
level = 1
start_time = 0
elapsed_time = 0
top_score = 0
top_score_time = None
map_layout = []
enemies = []
health_blocks = []
treasure_pos = [0, 0]

HIGH_SCORE_FILE = "high_scores.txt"


# Helper Functions
def adjust_color(color, factor):
    """Adjust the brightness of a color by a given factor."""
    return [max(0, min(255, int(c // factor))) for c in color]


def draw_cube(x, y, color, depth=10, alpha=150, left_wall=False, right_wall=False, top_wall=False):
    """Draw a translucent cube at grid position (x, y) with the given color and depth."""
    cube_surface = pygame.Surface((GRID_SIZE + depth, GRID_SIZE + depth), pygame.SRCALPHA)
    base_x, base_y = depth, depth

    # Front face (always visible)
    front_rect = [
        (base_x, base_y + GRID_SIZE),
        (base_x, base_y),
        (base_x + GRID_SIZE, base_y),
        (base_x + GRID_SIZE, base_y + GRID_SIZE)
    ]
    pygame.draw.polygon(cube_surface, (*color, alpha), front_rect)

    # Top face (only draw if not blocked by a top wall)
    if not top_wall:
        top_rect = [
            (base_x, base_y),
            (base_x + GRID_SIZE, base_y),
            (base_x + GRID_SIZE - depth, base_y - depth),
            (base_x - depth, base_y - depth)
        ]
        pygame.draw.polygon(cube_surface, (*adjust_color(color, 1.2), alpha), top_rect)

    # Left face (only draw if not blocked by a left wall)
    if not left_wall:
        left_rect = [
            (base_x, base_y),
            (base_x - depth, base_y - depth),
            (base_x - depth, base_y + GRID_SIZE - depth),
            (base_x, base_y + GRID_SIZE)
        ]
        pygame.draw.polygon(cube_surface, (*adjust_color(color, 1.5), alpha), left_rect)

    # Right face (only draw if not blocked by a right wall)
    if not right_wall:
        right_rect = [
            (base_x + GRID_SIZE, base_y),
            (base_x + GRID_SIZE + depth, base_y - depth),
            (base_x + GRID_SIZE + depth, base_y + GRID_SIZE - depth),
            (base_x + GRID_SIZE, base_y + GRID_SIZE)
        ]
        pygame.draw.polygon(cube_surface, (*adjust_color(color, 1.3), alpha), right_rect)

    # Blit the cube surface onto the main screen
    screen.blit(cube_surface, (x * GRID_SIZE - depth, y * GRID_SIZE - depth))


def draw_map_with_depth():
    """Draw the map with walls and open spaces."""
    for row in range(len(map_layout)):
        for col in range(len(map_layout[row])):
            if map_layout[row][col] == 1:  # Wall tile
                # Check for adjacent walls
                left_wall = col > 0 and map_layout[row][col - 1] == 1
                right_wall = col < len(map_layout[row]) - 1 and map_layout[row][col + 1] == 1
                top_wall = row > 0 and map_layout[row - 1][col] == 1

                # Debug print for adjacency flags
                print(f"Wall at ({col}, {row}): left_wall={left_wall}, right_wall={right_wall}, top_wall={top_wall}")

                # Pass adjacency information to draw_cube
                draw_cube(col, row, BLACK, left_wall=left_wall, right_wall=right_wall, top_wall=top_wall)
            else:  # Open space
                draw_cube(col, row, WHITE)


def draw_player_with_depth():
    """Draw the player."""
    draw_cube(player_pos[0], player_pos[1], PLAYER_COLOR)


def draw_treasure_with_depth():
    """Draw the treasure."""
    draw_cube(treasure_pos[0], treasure_pos[1], TREASURE_COLOR)


def draw_enemies_with_depth():
    """Draw all enemies."""
    for enemy in enemies:
        draw_cube(enemy["pos"][0], enemy["pos"][1], ENEMY_COLOR)


def draw_health_blocks():
    """Draw health blocks on the map."""
    for health_pos in health_blocks:
        draw_cube(health_pos[0], health_pos[1], HEALTH_COLOR)


def draw_stats():
    """Display the player's health, level, and timer prominently in a horizontal line at the top."""
    font = pygame.font.Font(None, 36)

    # Display health, level, and timer in a horizontal line
    health_text = font.render(f"Health: {player_stats['health']}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    timer_text = font.render(f"Time: {elapsed_time}s", True, WHITE)

    # Adjust the y-position to move the stats higher
    screen.blit(health_text, (10, 5))  # Move up from 10 to 5
    screen.blit(level_text, (150, 5))  # Move up from 10 to 5
    screen.blit(timer_text, (300, 5))  # Move up from 10 to 5


def combat(enemy):
    """Handle combat between the player and an enemy."""
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


def is_path_to_treasure(map_layout, player_pos, treasure_pos):
    """Check if there is a valid path from the player to the treasure using BFS."""
    rows, cols = len(map_layout), len(map_layout[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    queue = deque([player_pos])

    while queue:
        x, y = queue.popleft()

        # If we reach the treasure, a path exists
        if [x, y] == treasure_pos:
            return True

        # Mark the current cell as visited
        visited[y][x] = True

        # Check all four possible directions
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx] and map_layout[ny][nx] == 0:
                queue.append([nx, ny])

    # If we exhaust the queue without finding the treasure, no path exists
    return False


def next_level():
    """Advance to the next level."""
    global map_layout, player_pos, treasure_pos, enemies, health_blocks, level

    level += 1
    map_width, map_height = 12, 10

    # Generate a new map layout
    map_layout = [
        [1 if x == 0 or x == map_width - 1 or y == 0 or y == map_height - 1 else 0
         for x in range(map_width)]
        for y in range(map_height)
    ]

    # Track occupied positions to avoid overlaps
    occupied_positions = set()

    # Place player at a random position
    while True:
        player_x = random.randint(1, map_width - 2)
        player_y = random.randint(1, map_height - 2)
        if map_layout[player_y][player_x] == 0:  # Ensure it's not a wall
            player_pos = [player_x, player_y]
            occupied_positions.add((player_x, player_y))
            break

    # Place treasure
    while True:
        treasure_x = random.randint(1, map_width - 2)
        treasure_y = random.randint(1, map_height - 2)
        if (treasure_x, treasure_y) not in occupied_positions and map_layout[treasure_y][treasure_x] == 0:
            treasure_pos = [treasure_x, treasure_y]
            occupied_positions.add((treasure_x, treasure_y))
            break

    # Place walls
    for _ in range((map_width * map_height) // 8):  # Adjust density of walls
        attempts = 0
        while True:
            wall_x = random.randint(1, map_width - 2)
            wall_y = random.randint(1, map_height - 2)
            if (wall_x, wall_y) not in occupied_positions:
                # Temporarily place the wall
                map_layout[wall_y][wall_x] = 1
                occupied_positions.add((wall_x, wall_y))

                # Validate the path to the treasure
                if is_path_to_treasure(map_layout, player_pos, treasure_pos):
                    break  # Valid placement
                else:
                    # Remove the wall if it blocks the path
                    map_layout[wall_y][wall_x] = 0
                    occupied_positions.remove((wall_x, wall_y))

            attempts += 1
            if attempts > 100:  # Skip this wall if too many attempts
                print("Failed to place a wall after 100 attempts.")
                break

    # Place enemies
    enemies.clear()
    for _ in range(level + 2):  # Increase enemies with level
        attempts = 0
        while True:
            enemy_x = random.randint(1, map_width - 2)
            enemy_y = random.randint(1, map_height - 2)
            if (enemy_x, enemy_y) not in occupied_positions and map_layout[enemy_y][enemy_x] == 0:
                enemies.append({"pos": [enemy_x, enemy_y], "health": 5, "attack": 2})
                occupied_positions.add((enemy_x, enemy_y))
                break
            attempts += 1
            if attempts > 100:
                print("Failed to place an enemy after 100 attempts.")
                break

    # Place health blocks
    health_blocks.clear()
    num_health_blocks = min(3, max(1, len(enemies) // 4))  # Limit to a maximum of 3 health blocks
    for _ in range(num_health_blocks):
        attempts = 0
        while True:
            health_x = random.randint(1, map_width - 2)
            health_y = random.randint(1, map_height - 2)
            if (health_x, health_y) not in occupied_positions and map_layout[health_y][health_x] == 0:
                health_blocks.append([health_x, health_y])
                occupied_positions.add((health_x, health_y))
                break
            attempts += 1
            if attempts > 100:
                print("Failed to place a health block after 100 attempts.")
                break


def reset_game():
    """Reset the game to its initial state."""
    global level, player_stats, player_pos, enemies, treasure_pos, map_layout, start_time

    level = 1
    player_stats = {"health": 10, "attack": 3}
    player_pos = [1, 1]
    start_time = pygame.time.get_ticks()
    next_level()


def game_over():
    """Display the Game Over screen, handle high scores, and allow restart or quit."""
    global top_score, top_score_time, elapsed_time, running

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    high_scores = load_high_scores()
    
    # Define fonts
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 24)
    
    # Check if current score is a high score
    is_high_score = (len(high_scores) < 10 or 
                    any(level > score["level"] or 
                        (level == score["level"] and elapsed_time < score["time"]) 
                        for score in high_scores))

    def draw_game_over_screen():
        """Helper function to redraw the game over screen."""
        screen.fill(BLACK)
        
        # Game Over text
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 10))
        
        # Player's score
        score_text = small_font.render(f"Your Score: Level {level}, Time {elapsed_time}s", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # High scores
        high_scores_title = small_font.render("Top 10 High Scores:", True, WHITE)
        screen.blit(high_scores_title, (SCREEN_WIDTH // 2 - high_scores_title.get_width() // 2, 80))
        
        sorted_scores = sorted(high_scores, key=lambda s: (-s["level"], s["time"]))[:10]
        for i, score in enumerate(sorted_scores):
            score_text = small_font.render(
                f"{i + 1}. {score['initials']} - Level {score['level']}, Time {score['time']}s", 
                True, WHITE
            )
            screen.blit(score_text, (50, 110 + i * 20))
        
        pygame.display.flip()

    # Initial screen draw
    draw_game_over_screen()

    # If it's a high score, prompt for initials
    if is_high_score:
        initials = ""
        instructions = small_font.render("New High Score! Enter your initials (3 letters):", True, WHITE)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 350))
        pygame.display.flip()

        # Handle initials entry
        while len(initials) < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        initials = initials[:-1]
                    elif event.unicode.isalpha() and len(initials) < 3:
                        initials += event.unicode.upper()
                    
                    # Update display
                    draw_game_over_screen()
                    screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 350))
                    current = small_font.render(initials, True, WHITE)
                    screen.blit(current, (SCREEN_WIDTH // 2 - current.get_width() // 2, 380))
                    pygame.display.flip()

        # Save the high score
        high_scores.append({"initials": initials, "level": level, "time": elapsed_time})
        high_scores.sort(key=lambda s: (-s["level"], s["time"]))
        high_scores = high_scores[:10]
        save_high_scores(high_scores)
        draw_game_over_screen()

    # Show restart/quit instructions
    restart_text = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
    pygame.display.flip()

    # Wait for restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()


def draw_bump_animation(player_pos, direction):
    """Create a bump animation when the player hits a wall."""
    bump_offset = 5  # Amount of offset for the bump
    dx, dy = direction

    # Calculate the bumped position
    bumped_x = player_pos[0] + dx * bump_offset / GRID_SIZE
    bumped_y = player_pos[1] + dy * bump_offset / GRID_SIZE

    # Draw the bumped position briefly
    draw_cube(bumped_x, bumped_y, PLAYER_COLOR)
    pygame.display.flip()
    pygame.time.delay(100)  # Delay for the bump effect

    # Redraw the original position
    draw_map_with_depth()
    draw_player_with_depth()
    draw_treasure_with_depth()
    draw_enemies_with_depth()
    draw_health_blocks()
    draw_stats()
    pygame.display.flip()


def load_high_scores():
    """Load high scores from a file."""
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    with open(HIGH_SCORE_FILE, "r") as file:
        scores = []
        valid_scores = []
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 3:  # Ensure the line has exactly three parts
                try:
                    scores.append({"initials": parts[0], "level": int(parts[1]), "time": int(parts[2])})
                except ValueError:
                    print(f"Skipping malformed line: {line.strip()}")
        return scores  # Ensure the function returns the scores list

    return scores  # Ensure the function returns the scores list

def save_high_scores(high_scores):
    """Save high scores to a file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        for score in high_scores:
            file.write(f"{score['initials']},{score['level']},{score['time']}\n")


def display_high_scores():
    """Display the high scores."""
    high_scores = load_high_scores()
    font = pygame.font.Font(None, 36)
    screen.fill(BLACK)

    title_text = font.render("High Scores", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    for i, score in enumerate(high_scores):
        score_text = font.render(
            f"{i + 1}. {score['initials']} - Level {score['level']}, Time {score['time']}s", True, WHITE
        )
        screen.blit(score_text, (50, 100 + i * 40))

    pygame.display.flip()
    pygame.display.flip()
    pygame.display.flip()
    display_start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - display_start_time < 3000:
        pygame.time.wait(100)  # Add a small delay to avoid busy waiting

def start_screen():
    font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 36)
    screen.fill(BLACK)

    title_text = font.render("Vube", True, WHITE)
    instructions_text = small_font.render("Press ENTER to Start", True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, 250))
    pygame.display.flip()

    # Wait for the player to press ENTER
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False  # Exit the loop to begin the game
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return  # Exit the start screen and begin the game


# Main Game Loop
start_screen()  # Display the start screen
reset_game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle movement on key press
        if event.type == pygame.KEYDOWN:
            original_pos = player_pos[:]
            if event.key == pygame.K_LEFT:
                if map_layout[player_pos[1]][player_pos[0] - 1] == 0:
                    player_pos[0] -= 1
                else:
                    draw_bump_animation(player_pos, (-1, 0))
            elif event.key == pygame.K_RIGHT:
                if map_layout[player_pos[1]][player_pos[0] + 1] == 0:
                    player_pos[0] += 1
                else:
                    draw_bump_animation(player_pos, (1, 0))
            elif event.key == pygame.K_UP:
                if map_layout[player_pos[1] - 1][player_pos[0]] == 0:
                    player_pos[1] -= 1
                else:
                    draw_bump_animation(player_pos, (0, -1))
            elif event.key == pygame.K_DOWN:
                if map_layout[player_pos[1] + 1][player_pos[0]] == 0:
                    player_pos[1] += 1
                else:
                    draw_bump_animation(player_pos, (0, 1))

    # Check for combat
    for enemy in enemies[:]:
        if player_pos == enemy["pos"]:
            if not combat(enemy):
                game_over()
            else:
                enemies.remove(enemy)

    # Check for health block interaction
    for health_pos in health_blocks[:]:
        if player_pos == health_pos:
            player_stats["health"] += 5
            health_blocks.remove(health_pos)

    # Check for win condition
    if player_pos == treasure_pos:
        next_level()

    # Draw everything
    screen.fill(WHITE)
    draw_map_with_depth()
    draw_player_with_depth()
    draw_treasure_with_depth()
    draw_enemies_with_depth()
    draw_health_blocks()
    draw_stats()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()