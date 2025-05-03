from manim import *
import numpy as np
from mytsp import tsp, totalCost
import math


class TSPVisualization(Scene):
    def construct(self):
        # Configuration
        self.city_radius = 0.2
        self.num_cities = 4
        self.wait_time = 0.5

        # Generate city positions in a circle for better visualization
        self.city_coords = self.generate_city_positions()
        self.cost_matrix = self.generate_cost_matrix()

        # Create city dots
        self.cities = self.create_cities()
        self.city_labels = self.create_city_labels()

        # Show initial state
        self.play(
            *[Create(city) for city in self.cities],
            *[Write(label) for label in self.city_labels],
        )
        self.wait(self.wait_time)

        # Run TSP and visualize
        self.visualize_tsp()

        # Show final cost
        final_cost = tsp(self.cost_matrix)
        cost_text = Text(f"Optimal Cost: {final_cost}", font_size=24).to_edge(DOWN)
        self.play(Write(cost_text))
        self.wait(2)

    def generate_city_positions(self):
        """Generate city positions in a circle"""
        coords = []
        radius = 3  # Manim uses a larger coordinate system
        for i in range(self.num_cities):
            angle = i * (2 * PI / self.num_cities)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            coords.append((x, y, 0))  # Manim uses 3D coordinates
        return coords

    def generate_cost_matrix(self):
        """Generate cost matrix based on Euclidean distances"""
        cost = [[0 for _ in range(self.num_cities)] for _ in range(self.num_cities)]
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                if i != j:
                    x1, y1, _ = self.city_coords[i]
                    x2, y2, _ = self.city_coords[j]
                    distance = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * 10)
                    cost[i][j] = distance
        return cost

    def create_cities(self):
        """Create city dots"""
        return [
            Dot(point=coord, radius=self.city_radius, color=BLUE)
            for coord in self.city_coords
        ]

    def create_city_labels(self):
        """Create city labels"""
        return [
            Text(str(i), font_size=24).move_to(coord)
            for i, coord in enumerate(self.city_coords)
        ]

    def draw_path(self, path, color=RED, permanent=False):
        """Draw a path between cities"""
        lines = []
        path_group = VGroup()
        cost_labels = []
        cumulative_cost = 0

        for i in range(len(path) - 1):
            start = self.city_coords[path[i]]
            end = self.city_coords[path[i + 1]]
            line = Line(start=start, end=end, color=color)
            lines.append(line)

            # Add cost label
            edge_cost = self.cost_matrix[path[i]][path[i + 1]]
            cumulative_cost += edge_cost
            mid_point = np.array([(start[0] + end[0]) / 2, (start[1] + end[1]) / 2, 0])
            cost_label = Text(str(edge_cost), font_size=20, color=color).move_to(
                mid_point
            )
            cost_labels.append(cost_label)

            path_group.add(line)
            path_group.add(cost_label)

        # Show the path
        if permanent:
            # For final path, show with more emphasis
            self.play(Create(path_group), run_time=2)
            return path_group
        else:
            # For exploration paths, show quickly and fade out
            self.play(Create(path_group), run_time=0.5)
            self.wait(0.3)
            self.play(FadeOut(path_group), run_time=0.3)

    def reconstruct_path(self, curr_mask, curr_city):
        """Reconstruct the optimal path from the current state"""
        path = [curr_city]
        mask = curr_mask

        while mask != (1 << self.num_cities) - 1:
            next_city = -1
            min_cost = float("inf")

            for city in range(self.num_cities):
                if (mask & (1 << city)) == 0:
                    curr_cost = self.cost_matrix[curr_city][city] + totalCost(
                        mask | (1 << city),
                        city,
                        self.num_cities,
                        self.cost_matrix,
                        [[-1] * (1 << self.num_cities) for _ in range(self.num_cities)],
                    )
                    if curr_cost < min_cost:
                        min_cost = curr_cost
                        next_city = city

            path.append(next_city)
            mask |= 1 << next_city
            curr_city = next_city

        path.append(0)  # Return to start
        return path

    def visualize_tsp(self):
        """Visualize the TSP algorithm"""
        # Initialize dp table
        n = self.num_cities
        dp = [[-1] * (1 << n) for _ in range(n)]

        def visualize_recursive(mask, curr):
            if dp[curr][mask] != -1:
                return dp[curr][mask]

            if mask == (1 << n) - 1:
                # Show return to start
                return_path = [curr, 0]
                self.draw_path(return_path)
                return self.cost_matrix[curr][0]

            min_cost = float("inf")
            best_path = None

            for next_city in range(n):
                if (mask & (1 << next_city)) == 0:
                    # Visualize trying this city
                    current_path = self.reconstruct_path(mask, curr) + [next_city]
                    self.draw_path(current_path)

                    cost = self.cost_matrix[curr][next_city] + visualize_recursive(
                        mask | (1 << next_city), next_city
                    )

                    if cost < min_cost:
                        min_cost = cost
                        best_path = current_path

            dp[curr][mask] = min_cost
            return min_cost

        # Start the visualization
        visualize_recursive(1, 0)  # Start with city 0 visited

        # Show final optimal path
        optimal_path = self.reconstruct_path(1, 0)
        final_path = self.draw_path(optimal_path, color=BLUE, permanent=True)

        # Add arrows to show direction
        arrows = []
        for i in range(len(optimal_path) - 1):
            start = self.city_coords[optimal_path[i]]
            end = self.city_coords[optimal_path[i + 1]]
            arrow = Arrow(
                start=np.array(start),
                end=np.array(end),
                buff=self.city_radius,
                color=BLUE,
            )
            arrows.append(arrow)

        self.play(*[GrowArrow(arrow) for arrow in arrows], run_time=2)

        # Show path sequence
        path_text = Text(
            f"Path: {' → '.join(map(str, optimal_path))}", font_size=24
        ).to_edge(UP)
        self.play(Write(path_text))


if __name__ == "__main__":
    # Command to render: manim -pql tsp_manim.py TSPVisualization
    # For high quality: manim -pqh tsp_manim.py TSPVisualization
    pass
