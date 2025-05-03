from manim import *
import numpy as np
from mytsp import tsp, totalCost
import math


class TSPVisualization(Scene):
    def construct(self):
        # Configuration
        self.city_radius = 0.08  # Smaller dots for better precision
        self.num_cities = 4
        self.wait_time = 0.5
        self.scale_factor = 100  # Scale factor for distance to cost conversion

        # Create coordinate grid first
        self.setup_coordinate_system()

        # Generate precise city positions
        self.city_coords = self.generate_city_positions()
        self.cost_matrix = self.generate_cost_matrix()

        # Create and show city dots with precise positioning
        self.cities = self.create_cities()
        self.city_labels = self.create_city_labels()

        # Show distance scale reference
        self.create_distance_scale()

        # Show initial state with coordinate labels
        self.play(
            *[Create(city) for city in self.cities],
            *[Write(label) for label in self.city_labels],
        )

        # Show coordinate info for each city
        self.show_city_coordinates()

        self.wait(self.wait_time)

        # Run TSP and visualize
        self.visualize_tsp()

        # Show final cost
        final_cost = tsp(self.cost_matrix)
        cost_text = Text(f"Optimal Cost: {final_cost}", font_size=24).to_edge(DOWN)
        self.play(Write(cost_text))
        self.wait(2)

    def setup_coordinate_system(self):
        """Create precise coordinate system with grid"""
        # Create axes with more precise numbering
        self.axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            x_length=10,
            y_length=10,
            # axis_config={
            #     "include_numbers": True,
            #     "include_tip": True,
            #     "numbers_to_exclude": [],
            #     "decimal_number_config": {"num_decimal_places": 1},
            # },
        )

        # Create grid lines for better distance measurement
        grid_lines = VGroup()

        # Add minor grid lines (0.5 units)
        for x in np.arange(-5, 5.1, 0.5):
            if x != 0:  # Skip axis lines
                grid_lines.add(
                    DashedLine(
                        start=np.array([x, -5, 0]),
                        end=np.array([x, 5, 0]),
                        color=GREY_D,
                        stroke_width=0.5,
                        dash_length=0.1,
                    )
                )
        for y in np.arange(-5, 5.1, 0.5):
            if y != 0:  # Skip axis lines
                grid_lines.add(
                    DashedLine(
                        start=np.array([-5, y, 0]),
                        end=np.array([5, y, 0]),
                        color=GREY_D,
                        stroke_width=0.5,
                        dash_length=0.1,
                    )
                )

        # Show coordinate system
        self.play(Create(self.axes), Create(grid_lines))
        self.grid = grid_lines

    def generate_city_positions(self):
        """Generate city positions with precise coordinates"""
        if self.num_cities == 4:
            # Use precise coordinates for better distance representation
            coords = [
                (-2.5, 2.0, 0),  # City 0
                (2.5, 2.0, 0),  # City 1
                (1.5, -2.0, 0),  # City 2
                (-1.5, -2.0, 0),  # City 3
            ]
        else:
            # For other numbers, use calculated positions with exact distances
            coords = []
            radius = 2.5  # Base radius
            for i in range(self.num_cities):
                angle = i * (2 * PI / self.num_cities)
                # Add intentional variation to make distances more interesting
                r = radius * (1 + 0.2 * np.cos(3 * angle))
                x = round(r * np.cos(angle), 3)  # Round to 3 decimal places
                y = round(r * np.sin(angle), 3)
                coords.append((x, y, 0))
        return coords

    def create_distance_scale(self):
        """Create a visual distance scale reference"""
        # Create a 1-unit reference line
        start_point = np.array([3, -3, 0])
        end_point = start_point + np.array([1, 0, 0])

        scale_line = Line(start_point, end_point, color=WHITE)
        scale_ticks = VGroup(
            Line(
                start_point + np.array([0, 0.1, 0]),
                start_point + np.array([0, -0.1, 0]),
                color=WHITE,
            ),
            Line(
                end_point + np.array([0, 0.1, 0]),
                end_point + np.array([0, -0.1, 0]),
                color=WHITE,
            ),
        )

        # Add scale label
        scale_label = Text(f"1 unit = {self.scale_factor} cost", font_size=20).next_to(
            scale_line, DOWN, buff=0.1
        )

        self.play(Create(scale_line), Create(scale_ticks), Write(scale_label))

    def show_city_coordinates(self):
        """Show exact coordinates for each city"""
        coord_labels = []
        for i, (x, y, _) in enumerate(self.city_coords):
            label = Text(
                f"City {i}: ({x:.1f}, {y:.1f})", font_size=16, color=YELLOW
            ).move_to(np.array([x, y + 0.3, 0]))
            coord_labels.append(label)

        self.play(*[Write(label) for label in coord_labels])
        self.wait(1)
        self.play(*[FadeOut(label) for label in coord_labels])

    def generate_cost_matrix(self):
        """Generate precise cost matrix based on exact Euclidean distances"""
        cost = [[0 for _ in range(self.num_cities)] for _ in range(self.num_cities)]
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                if i != j:
                    x1, y1, _ = self.city_coords[i]
                    x2, y2, _ = self.city_coords[j]
                    # Calculate exact distance with higher precision
                    exact_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    # Convert distance to integer cost with higher precision
                    cost[i][j] = int(round(exact_distance * self.scale_factor))
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
        """Draw a path between cities with precise distance information"""
        lines = []
        path_group = VGroup()

        # Groups for different types of labels
        cost_labels = []
        distance_labels = []
        arrow_heads = []

        cumulative_cost = 0

        for i in range(len(path) - 1):
            start = self.city_coords[path[i]]
            end = self.city_coords[path[i + 1]]

            # Create line with proper thickness
            line = Line(
                start=start, end=end, color=color, stroke_width=2 if permanent else 1
            )
            lines.append(line)

            # Calculate precise distance and cost
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            exact_distance = round(math.sqrt(dx**2 + dy**2), 2)
            edge_cost = self.cost_matrix[path[i]][path[i + 1]]
            cumulative_cost += edge_cost

            # Calculate label positions with offset to prevent overlap
            mid_point = np.array([(start[0] + end[0]) / 2, (start[1] + end[1]) / 2, 0])
            direction = np.array([dx, dy, 0])
            perpendicular = np.array([-dy, dx, 0])
            unit_perp = perpendicular / (
                np.linalg.norm(perpendicular)
                if np.linalg.norm(perpendicular) != 0
                else 1
            )

            # Position labels on either side of the line
            cost_offset = unit_perp * 0.4
            dist_offset = -unit_perp * 0.4

            # Create detailed labels
            cost_label = Text(f"Cost: {edge_cost}", font_size=16, color=color).move_to(
                mid_point + cost_offset
            )

            distance_label = Text(
                f"Dist: {exact_distance:.2f}", font_size=16, color=color
            ).move_to(mid_point + dist_offset)

            # Add arrow tip for direction
            if permanent:
                arrow_head = Arrow(
                    start=mid_point - direction * 0.1,
                    end=mid_point + direction * 0.1,
                    color=color,
                    buff=0,
                    tip_length=0.15,
                )
                arrow_heads.append(arrow_head)

            # Add all elements to groups
            cost_labels.append(cost_label)
            distance_labels.append(distance_label)

            path_group.add(line)
            path_group.add(cost_label)
            path_group.add(distance_label)
            if permanent:
                path_group.add(arrow_head)

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

        # Show final optimal path with detailed information
        optimal_path = self.reconstruct_path(1, 0)
        final_path_group = self.draw_path(optimal_path, color=BLUE, permanent=True)

        # Calculate total distance and cost
        total_distance = 0
        total_cost = 0
        segment_distances = []

        for i in range(len(optimal_path) - 1):
            start = self.city_coords[optimal_path[i]]
            end = self.city_coords[optimal_path[i + 1]]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            distance = math.sqrt(dx**2 + dy**2)
            cost = self.cost_matrix[optimal_path[i]][optimal_path[i + 1]]

            total_distance += distance
            total_cost += cost
            segment_distances.append(f"{distance:.2f}")

        # Create detailed summary
        summary_group = VGroup()

        path_text = Text(f"Path: {' → '.join(map(str, optimal_path))}", font_size=24)

        distances_text = Text(
            f"Segment distances: {' + '.join(segment_distances)} = {total_distance:.2f} units",
            font_size=20,
        )

        cost_text = Text(f"Total cost: {total_cost}", font_size=24)

        # Arrange summary texts
        summary_group.add(path_text, distances_text, cost_text)
        summary_group.arrange(DOWN, buff=0.2)
        summary_group.to_edge(UP)

        # Show summary with animation
        self.play(Write(summary_group), run_time=2)

        # Add a final note about scale factor
        scale_note = Text(
            f"(Scale factor: {self.scale_factor} cost units per distance unit)",
            font_size=16,
            color=GREY_A,
        ).next_to(summary_group, DOWN)
        self.play(Write(scale_note))


if __name__ == "__main__":
    # Command to render: manim -pql tsp_manim.py TSPVisualization
    # For high quality: manim -pqh tsp_manim.py TSPVisualization
    pass
