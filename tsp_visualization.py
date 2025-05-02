import pygame
import sys
import math
import time
from typing import List, Tuple
from mytsp import tsp, totalCost


def tsp_with_visualization(cost, city_positions):
    """TSP with visualization - calls the recursive function with visualization"""
    n = len(cost)
    dp = [[-1] * (1 << n) for _ in range(n)]
    current_path = [0]  # Start at city 0

    # Draw initial state
    screen.fill(WHITE)
    draw_cities(city_positions)
    pygame.display.flip()
    time.sleep(1.0)  # Increased initial delay

    result = total_cost_with_visualization(
        1, 0, n, cost, dp, city_positions, current_path
    )

    # Show final path
    optimal_path = reconstruct_path(cost, dp)
    screen.fill(WHITE)
    draw_cities(city_positions)
    draw_path(city_positions, optimal_path)

    # Display dp table state (simplified)
    table_surf = pygame.Surface((300, 200))
    table_surf.fill(GRAY)
    for i in range(min(5, n)):
        for j in range(min(8, (1 << n))):
            if dp[i][j] != -1:
                cell_text = font.render(f"dp[{i}][{j:b}]={dp[i][j]}", True, BLACK)
                table_surf.blit(cell_text, (10 + j * 35, 10 + i * 20))

    screen.blit(table_surf, (WIDTH - 320, 20))
    pygame.display.flip()
    # Show final optimal path with emphasis
    draw_final_path(city_positions, optimal_path)
    pygame.display.flip()
    time.sleep(2)  # Longer pause to see final result

    return result


def total_cost_with_visualization(
    mask, curr, n, cost, dp, city_positions, current_path
):
    """Modified totalCost function with visualization"""
    if dp[curr][mask] != -1:
        return dp[curr][mask]

    if mask == (1 << n) - 1:
        # Draw return to origin
        next_path = current_path + [0]
        screen.fill(WHITE)
        draw_cities(city_positions)
        draw_path(city_positions, next_path)
        pygame.display.flip()
        time.sleep(0.5)  # Increased delay for return to origin

        return cost[curr][0]

    min_cost = sys.maxsize

    for i in range(n):
        if (mask & (1 << i)) == 0:
            # Visualize trying this city
            next_path = current_path + [i]
            screen.fill(WHITE)
            draw_cities(city_positions)
            draw_path(city_positions, next_path)
            pygame.display.flip()
            time.sleep(0.4)  # Increased delay for trying cities

            cost_through_i = cost[curr][i] + total_cost_with_visualization(
                mask | (1 << i), i, n, cost, dp, city_positions, next_path
            )

            if cost_through_i < min_cost:
                min_cost = cost_through_i

    dp[curr][mask] = min_cost
    return min_cost


def reconstruct_path(cost, dp):
    """Reconstruct the optimal path from the dp table"""
    n = len(cost)
    mask = 1  # Start with just city 0 visited
    curr = 0  # Start at city 0
    path = [0]

    while mask != (1 << n) - 1:
        next_city = -1
        min_cost = sys.maxsize

        for i in range(n):
            if (mask & (1 << i)) == 0:
                if cost[curr][i] + dp[i][mask | (1 << i)] < min_cost:
                    min_cost = cost[curr][i] + dp[i][mask | (1 << i)]
                    next_city = i

        path.append(next_city)
        mask |= 1 << next_city
        curr = next_city

    path.append(0)  # Return to starting city
    return path


# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP Algorithm Visualization")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# City positions (will be generated randomly)
city_positions = []

# Font
font = pygame.font.SysFont("Arial", 15)


def generate_city_positions(n: int) -> List[Tuple[int, int]]:
    """Generate random positions for cities"""
    positions = []
    for _ in range(n):
        x = 100 + (WIDTH - 200) * (0.2 + 0.6 * len(positions) / max(1, n - 1))
        y = 100 + (HEIGHT - 300) * (
            0.3 + 0.4 * math.sin(len(positions) * math.pi / max(1, n - 1))
        )
        positions.append((int(x), int(y)))
    return positions


def draw_cities(positions):
    """Draw cities as circles"""
    for i, (x, y) in enumerate(positions):
        pygame.draw.circle(screen, BLACK, (x, y), 10)
        text = font.render(str(i), True, WHITE)
        screen.blit(text, (x - 5, y - 8))


def draw_path(positions, path):
    """Draw the current path between cities"""
    if not path:
        return

    for i in range(len(path) - 1):
        start_pos = positions[path[i]]
        end_pos = positions[path[i + 1]]
        pygame.draw.line(screen, RED, start_pos, end_pos, 2)


def draw_final_path(positions, path):
    """Draw the final optimal path with emphasis"""
    if not path:
        return

    # Draw bold blue line for the optimal path
    for i in range(len(path) - 1):
        start_pos = positions[path[i]]
        end_pos = positions[path[i + 1]]
        # Draw a thicker line in blue
        pygame.draw.line(screen, BLUE, start_pos, end_pos, 4)

        # Add direction arrows
        mid_x = (start_pos[0] + end_pos[0]) // 2
        mid_y = (start_pos[1] + end_pos[1]) // 2

        # Calculate direction for arrow
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            udx = dx / length * 15  # Arrow size
            udy = dy / length * 15

            # Draw arrow head
            pygame.draw.polygon(
                screen,
                BLUE,
                [
                    (mid_x, mid_y),
                    (mid_x - udx + udy * 0.5, mid_y - udy - udx * 0.5),
                    (mid_x - udx - udy * 0.5, mid_y - udy + udx * 0.5),
                ],
            )


def visualize_tsp():
    # Generate a cost matrix based on Euclidean distances
    cost = [[0 for _ in range(len(city_positions))] for _ in range(len(city_positions))]

    for i in range(len(city_positions)):
        for j in range(len(city_positions)):
            if i != j:
                # Calculate Euclidean distance between cities
                x1, y1 = city_positions[i]
                x2, y2 = city_positions[j]
                distance = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
                cost[i][j] = distance

    # Modified TSP function (you'll need to create this)
    result = tsp_with_visualization(cost, city_positions)
    return result


# Main function
def main():
    global city_positions

    city_count = 4  # Start with 4 cities
    city_positions = generate_city_positions(city_count)

    running = True
    result = None
    optimal_path = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not result:
            result = visualize_tsp()
            # After visualization is complete, get the optimal path
            optimal_path = reconstruct_path(
                [[int(math.sqrt((city_positions[i][0] - city_positions[j][0]) ** 2 + 
                               (city_positions[i][1] - city_positions[j][1]) ** 2))
                  for j in range(len(city_positions))]
                 for i in range(len(city_positions))],
                [[-1] * (1 << len(city_positions)) for _ in range(len(city_positions))]
            )
        
        # Keep showing the final state
        screen.fill(WHITE)
        draw_cities(city_positions)
        if optimal_path:
            draw_final_path(city_positions, optimal_path)
        
        # Display final result
        result_text = font.render(f"Optimal Cost: {result}", True, BLACK)
        screen.blit(result_text, (20, HEIGHT - 50))
        
        # Display path sequence
        if optimal_path:
            path_text = font.render(f"Path: {' → '.join(map(str, optimal_path))}", True, BLACK)
            screen.blit(path_text, (20, HEIGHT - 80))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
