"""Area/Perimeter chain problem family implementation."""

import random
import math
from typing import Dict
from faker import Faker

from ..utils import round_to_decimals, round_money


class AreaPerimeterChainFamily:
    """Generate area/perimeter chain geometry problems."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.fake = Faker()

    def generate(self, complexity: int = 2, grade: str = 'middle',
                 math_topic: str = 'geometry', num_steps: int = None) -> Dict:
        """Generate an area/perimeter problem."""

        # Determine number of steps based on complexity if not specified
        if num_steps is None:
            step_ranges = {1: (1, 2), 2: (2, 3), 3: (3, 5)}
            min_steps, max_steps = step_ranges.get(complexity, (2, 3))
            num_steps = random.randint(min_steps, max_steps)

        # Choose a template
        templates = [
            self._rectangle_area_perimeter_template,
            self._garden_fence_template,
            self._shape_transformation_template,
            self._floor_tiling_template,
            self._circle_template,
        ]

        template_func = random.choice(templates)
        return template_func(complexity, grade, math_topic, num_steps)

    def _rectangle_area_perimeter_template(self, complexity: int, grade: str,
                                          math_topic: str, num_steps: int) -> Dict:
        """Generate a basic rectangle area and perimeter problem."""
        length = random.randint(5, 20)
        width = random.randint(5, 20)

        area = length * width
        perimeter = 2 * (length + width)

        operations = ["multiply", "multiply", "add"]

        location = random.choice(["backyard", "community park", "rooftop", "neighborhood"])
        problem_text = f"A {location} features a rectangular garden measuring {length}m in length and {width}m in width. "
        problem_text += f"The gardener needs to know both the area for planting and the perimeter for installing a border. "
        problem_text += f"What are the area and perimeter of the garden?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = f"Area: {area}m², Perimeter: {perimeter}m"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _garden_fence_template(self, complexity: int, grade: str,
                              math_topic: str, num_steps: int) -> Dict:
        """Generate a garden fence cost problem."""
        shape = random.choice(["rectangular", "square"])

        operations = []

        if shape == "square":
            side = random.randint(8, 20)
            perimeter = 4 * side
            problem_text = f"A homeowner plans to fence their square garden, which has sides measuring {side}m each. "
            operations.extend(["multiply"])
        else:
            length = random.randint(10, 25)
            width = random.randint(5, 15)
            perimeter = 2 * (length + width)
            problem_text = f"A homeowner wants to install fencing around their rectangular garden measuring {length}m by {width}m. "
            operations.extend(["multiply", "add"])

        # Add fence cost
        cost_per_meter = random.choice([5, 10, 15, 20])
        total_cost = perimeter * cost_per_meter
        problem_text += f"The fencing material costs {round_money(cost_per_meter)} per meter. "
        operations.append("multiply")

        # Add gate deduction for complexity 3
        if complexity >= 3:
            gate_width = random.choice([2, 3, 4])
            gate_savings = gate_width * cost_per_meter
            total_cost -= gate_savings
            problem_text += f"However, there's already a {gate_width}m-wide gate installed, so no fencing is needed for that section. "
            operations.extend(["multiply", "subtract"])

        problem_text += f"What is the total cost of the fencing project?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(total_cost)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _shape_transformation_template(self, complexity: int, grade: str,
                                      math_topic: str, num_steps: int) -> Dict:
        """Generate a shape transformation problem."""
        length = random.randint(8, 20)
        width = random.randint(6, 15)

        # Calculate area
        area = length * width

        operations = ["multiply"]

        field_type = random.choice(["athletic", "farming", "community", "recreational"])
        problem_text = f"A {field_type} field has a rectangular shape measuring {length}m by {width}m. "

        if complexity >= 2:
            # Transform to square with same area
            square_side = math.sqrt(area)
            square_side_rounded = round_to_decimals(square_side, 2)
            problem_text += f"The owner wants to redesign it as a square field with the same area. "
            operations.append("sqrt")

            if complexity >= 3:
                # Calculate perimeter of square
                square_perimeter = 4 * square_side
                square_perimeter_rounded = round_to_decimals(square_perimeter, 2)
                problem_text += f"They need to know both the side length of the new square and its perimeter for planning the boundary. "
                operations.append("multiply")

                problem_text += f"What are the side length and perimeter of the square field?\n\n"
                problem_text += "Please solve this problem and provide your final answer."
                answer = f"Side: {square_side_rounded}m, Perimeter: {square_perimeter_rounded}m"
            else:
                problem_text += f"What is the side length of the square field?\n\n"
                problem_text += "Please solve this problem and provide your final answer."
                answer = f"{square_side_rounded}m"
        else:
            problem_text += f"What is the area of the field?\n\n"
            problem_text += "Please solve this problem and provide your final answer."
            answer = f"{area}m²"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _floor_tiling_template(self, complexity: int, grade: str,
                               math_topic: str, num_steps: int) -> Dict:
        """Generate a floor tiling problem."""
        room_length = random.randint(6, 15)
        room_width = random.randint(4, 12)

        # Room area
        room_area = room_length * room_width

        # Tile dimensions (in meters)
        tile_size = random.choice([0.5, 1.0])
        tile_area = tile_size * tile_size

        operations = ["multiply", "multiply", "divide"]

        room_type = random.choice(["living room", "kitchen", "bathroom", "bedroom"])
        problem_text = f"A homeowner is renovating their {room_type}, which measures {room_length}m by {room_width}m. "
        problem_text += f"They've chosen square tiles that are {tile_size}m × {tile_size}m. "

        # Calculate number of tiles
        tiles_needed = room_area / tile_area

        if complexity >= 2:
            # Add waste factor
            waste_percent = random.choice([10, 15])
            tiles_with_waste = tiles_needed * (1 + waste_percent / 100.0)
            problem_text += f"The contractor recommends ordering {waste_percent}% extra tiles to account for cuts and breakage. "
            operations.append("percentage_increase")

            problem_text += f"How many tiles should be ordered in total?\n\n"
            problem_text += "Please solve this problem and provide your final answer."
            answer = f"{int(math.ceil(tiles_with_waste))} tiles"
        else:
            problem_text += f"How many tiles are needed to cover the floor?\n\n"
            problem_text += "Please solve this problem and provide your final answer."
            answer = f"{int(tiles_needed)} tiles"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _circle_template(self, complexity: int, grade: str,
                        math_topic: str, num_steps: int) -> Dict:
        """Generate a circle problem."""
        context = random.choice([
            ("circular pool", "pool"),
            ("circular garden", "garden"),
            ("pizza", "pizza")
        ])
        context_name, item_name = context

        operations = []

        if random.random() < 0.5:
            # Given radius
            radius = random.randint(3, 12)
            problem_text = f"A {context_name} has a radius of {radius}m. "

            circumference = 2 * math.pi * radius
            circumference_rounded = round_to_decimals(circumference, 2)
            operations.append("multiply")

            if complexity >= 2:
                area = math.pi * radius * radius
                area_rounded = round_to_decimals(area, 2)
                problem_text += f"The owner needs to know both the circumference for installing edging and the area for material coverage. "
                problem_text += f"Using π = 3.14, what are the circumference and area?\n\n"
                operations.extend(["multiply", "multiply"])

                problem_text += "Please solve this problem and provide your final answer."
                answer = f"Circumference: {circumference_rounded}m, Area: {area_rounded}m²"
            else:
                problem_text += f"Using π = 3.14, what is the circumference?\n\n"
                problem_text += "Please solve this problem and provide your final answer."
                answer = f"{circumference_rounded}m"
        else:
            # Given diameter
            diameter = random.randint(6, 20)
            radius = diameter / 2.0
            problem_text = f"A {context_name} has a diameter of {diameter}m. "

            area = math.pi * radius * radius
            area_rounded = round_to_decimals(area, 2)
            operations.extend(["divide", "multiply", "multiply"])

            if complexity >= 3:
                # Add cost calculation
                cost_per_sqm = random.choice([10, 15, 20, 25])
                total_cost = area * cost_per_sqm
                problem_text += f"The project requires materials that cost {round_money(cost_per_sqm)} per square meter. "
                problem_text += f"Using π = 3.14, what is the total cost to cover the area?\n\n"
                operations.append("multiply")

                problem_text += "Please solve this problem and provide your final answer."
                answer = round_money(total_cost)
            else:
                problem_text += f"Using π = 3.14, what is the area?\n\n"
                problem_text += "Please solve this problem and provide your final answer."
                answer = f"{area_rounded}m²"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }
