"""Rate/Time problem family implementation."""

import random
from typing import Dict
from faker import Faker
import names

from ..utils import round_to_decimals


class RateTimeFamily:
    """Generate rate/time distance problems."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.fake = Faker()

    def generate(self, complexity: int = 2, grade: str = 'middle',
                 math_topic: str = 'arithmetic', num_steps: int = None) -> Dict:
        """Generate a rate/time problem."""

        # Determine number of steps based on complexity if not specified
        if num_steps is None:
            step_ranges = {1: (1, 2), 2: (2, 4), 3: (4, 6)}
            min_steps, max_steps = step_ranges.get(complexity, (2, 4))
            num_steps = random.randint(min_steps, max_steps)

        # Choose template based on math topic if applicable
        if 'derivatives' in math_topic or 'algebra' in math_topic:
            # Road trip template handles derivatives and algebra best
            template_func = self._road_trip_template
        else:
            # Choose randomly for other topics
            templates = [
                self._road_trip_template,
                self._public_transit_template,
                self._cycling_template,
                self._airplane_template,
                self._delivery_route_template,
            ]
            template_func = random.choice(templates)

        return template_func(complexity, grade, math_topic, num_steps)

    def _road_trip_template(self, complexity: int, grade: str,
                            math_topic: str, num_steps: int) -> Dict:
        """Generate a road trip problem with multiple legs."""
        person_name = names.get_first_name()
        city1 = self.fake.city()
        city2 = self.fake.city()

        operations = []
        total_time = 0.0

        # Handle derivatives topic - acceleration/rate of change
        if 'derivatives' in math_topic and grade in ['high', 'college', 'university']:
            initial_speed = random.randint(40, 60)
            acceleration = random.choice([2, 3, 4, 5])
            time = random.randint(2, 4)

            final_speed = initial_speed + acceleration * time
            avg_speed = (initial_speed + final_speed) / 2
            distance = avg_speed * time

            problem_text = f"{person_name} begins a road trip from {city1} to {city2}. "
            problem_text += f"Starting at {initial_speed} mph, they gradually accelerate at a constant rate of "
            problem_text += f"{acceleration} mph per hour over the next {time} hours. "
            problem_text += f"What is their final speed, and how far did they travel during this time?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = f"Final speed: {final_speed} mph, Distance: {round_to_decimals(distance, 2)} miles"
            operations = ["multiply", "add", "add", "divide", "multiply"]

        # Handle algebra topic - set up equations
        elif 'algebra' in math_topic and complexity >= 2:
            speed1 = random.randint(40, 60)
            speed2 = random.randint(30, 50)
            total_distance = random.randint(200, 400)

            # Time for each segment
            time1 = random.randint(2, 4)
            distance1 = speed1 * time1
            distance2 = total_distance - distance1
            time2 = distance2 / speed2
            total_time = time1 + time2

            problem_text = f"{person_name} is driving from {city1} to {city2}, a total distance of {total_distance} miles. "
            problem_text += f"They drive the first part at {speed1} mph for {time1} hours, then reduce their speed "
            problem_text += f"to {speed2} mph for the remainder of the trip. How long does the entire journey take?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = f"{round_to_decimals(total_time, 2)} hours"
            operations = ["multiply", "subtract", "divide", "add"]

        else:
            # Default: Natural narrative for arithmetic/fractions
            num_segments = min(complexity + 1, 3)

            problem_text = f"{person_name} embarks on a road trip from {city1} to {city2}. "

            for i in range(num_segments):
                distance = random.randint(30, 100)
                speed = random.choice([30, 40, 50, 60])
                segment_time = distance / speed
                total_time += segment_time

                if i == 0:
                    problem_text += f"The first leg covers {distance} miles at {speed} mph. "
                elif i == num_segments - 1:
                    problem_text += f"Finally, they drive the last {distance} miles at {speed} mph. "
                else:
                    problem_text += f"Then they continue for {distance} miles at {speed} mph. "

                operations.append("divide")
                operations.append("add")

            # Add break time for higher complexity
            if complexity >= 2:
                break_time = random.choice([0.5, 1.0, 1.5])
                total_time += break_time
                break_hours = int(break_time)

                if break_time == 0.5:
                    problem_text += f"They stop for a 30-minute break along the way. "
                else:
                    problem_text += f"They stop for a {break_hours}-hour break along the way. "

                operations.append("add")

            problem_text += f"What's the total travel time?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            time_rounded = round_to_decimals(total_time, 2)
            answer = f"{time_rounded} hours"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _public_transit_template(self, complexity: int, grade: str,
                                 math_topic: str, num_steps: int) -> Dict:
        """Generate a public transit commute problem."""
        person_name = names.get_first_name()
        start_location = random.choice(["home", "their apartment", "the office", "school"])
        destination = random.choice(["work", "downtown", "the university", "the mall"])

        operations = []
        total_time = 0.0

        day = random.choice(["Monday morning", "Tuesday afternoon", "Wednesday evening", "Thursday"])
        problem_text = f"On {day}, {person_name} takes public transit from {start_location} to {destination}. "

        # Walking to station
        walk_time = random.choice([0.1, 0.15, 0.2, 0.25])
        total_time += walk_time
        walk_minutes = int(walk_time * 60)
        problem_text += f"After a {walk_minutes}-minute walk to the station, "
        operations.append("add")

        # First transit segment
        distance1 = random.randint(5, 15)
        speed1 = random.randint(20, 35)
        transit_time1 = distance1 / speed1
        total_time += transit_time1
        transit_type = random.choice(["bus", "train", "subway"])
        problem_text += f"they board a {transit_type} that travels {distance1} miles at {speed1} mph. "
        operations.append("divide")
        operations.append("add")

        # Transfer for complexity 2+
        if complexity >= 2:
            wait_time = random.choice([0.1, 0.15, 0.2])
            total_time += wait_time
            wait_minutes = int(wait_time * 60)
            problem_text += f"After waiting {wait_minutes} minutes for a connection, "
            operations.append("add")

            # Second transit segment
            distance2 = random.randint(5, 12)
            speed2 = random.randint(20, 30)
            transit_time2 = distance2 / speed2
            total_time += transit_time2
            transit_type2 = random.choice(["bus", "train"])
            problem_text += f"{person_name} takes another {transit_type2} for {distance2} miles at {speed2} mph. "
            operations.append("divide")
            operations.append("add")

        problem_text += f"How long is the entire commute?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        time_rounded = round_to_decimals(total_time, 2)
        answer = f"{time_rounded} hours"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _cycling_template(self, complexity: int, grade: str,
                         math_topic: str, num_steps: int) -> Dict:
        """Generate a cycling journey problem."""
        person_name = names.get_first_name()
        city = self.fake.city()

        operations = []
        total_time = 0.0

        season = random.choice(["spring", "summer", "fall"])
        time_of_day = random.choice(["morning", "afternoon", "evening"])

        problem_text = f"On a {season} {time_of_day}, {person_name} goes cycling through {city}. "

        # Flat terrain segment
        distance1 = random.randint(3, 8)
        speed1 = random.randint(12, 16)
        time1 = distance1 / speed1
        total_time += time1
        problem_text += f"They start on flat terrain, cycling {distance1} miles at {speed1} mph. "
        operations.append("divide")
        operations.append("add")

        # Uphill segment for complexity 2+
        if complexity >= 2:
            distance2 = random.randint(2, 5)
            speed2 = random.randint(6, 10)
            time2 = distance2 / speed2
            total_time += time2
            problem_text += f"Hitting some hills, they slow to {speed2} mph for the next {distance2} miles. "
            operations.append("divide")
            operations.append("add")

        # Downhill segment for complexity 3
        if complexity >= 3:
            distance3 = random.randint(3, 6)
            speed3 = random.randint(18, 24)
            time3 = distance3 / speed3
            total_time += time3
            problem_text += f"On the downhill stretch, they pick up speed to {speed3} mph over {distance3} miles. "
            operations.append("divide")
            operations.append("add")

            # Rest break
            rest_time = random.choice([0.15, 0.25])
            total_time += rest_time
            rest_minutes = int(rest_time * 60)
            problem_text += f"They take a {rest_minutes}-minute rest break to catch their breath. "
            operations.append("add")

        problem_text += f"What's the total time for the cycling trip?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        time_rounded = round_to_decimals(total_time, 2)
        answer = f"{time_rounded} hours"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _airplane_template(self, complexity: int, grade: str,
                          math_topic: str, num_steps: int) -> Dict:
        """Generate an airplane travel problem."""
        person_name = names.get_first_name()
        city1 = self.fake.city()
        city2 = self.fake.city()
        city3 = self.fake.city() if complexity >= 3 else None

        operations = []
        total_time = 0.0

        reason = random.choice(["a business trip", "vacation", "visiting family", "a conference"])
        problem_text = f"{person_name} is flying from {city1} to {city2} for {reason}. "

        # First flight
        distance1 = random.randint(400, 1200)
        speed1 = random.randint(450, 550)
        flight_time1 = distance1 / speed1
        total_time += flight_time1
        problem_text += f"The flight covers {distance1} miles at a cruising speed of {speed1} mph. "
        operations.append("divide")
        operations.append("add")

        # Layover for complexity 2+
        if complexity >= 2:
            layover = random.choice([1.0, 1.5, 2.0])
            total_time += layover
            layover_hours = layover if layover == int(layover) else layover
            problem_text += f"With a {layover_hours}-hour layover in {city2}, "
            operations.append("add")

            # Second flight
            if complexity >= 3 and city3:
                distance2 = random.randint(300, 800)
                speed2 = random.randint(450, 550)
                flight_time2 = distance2 / speed2
                total_time += flight_time2
                problem_text += f"{person_name} then flies to {city3}, covering another {distance2} miles at {speed2} mph. "
                operations.append("divide")
                operations.append("add")

        problem_text += f"What's the total travel time?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        time_rounded = round_to_decimals(total_time, 2)
        answer = f"{time_rounded} hours"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _delivery_route_template(self, complexity: int, grade: str,
                                 math_topic: str, num_steps: int) -> Dict:
        """Generate a delivery route problem."""
        person_name = names.get_first_name()
        city = self.fake.city()

        operations = []
        total_time = 0.0

        company = self.fake.company()
        problem_text = f"{person_name} works as a delivery driver for {company} in {city}. "

        # Number of delivery stops
        num_stops = complexity + 1

        if num_stops == 2:
            problem_text += f"Today's route has two stops. "
        elif num_stops == 3:
            problem_text += f"Today's route takes them to three different locations. "
        else:
            problem_text += f"Their schedule includes {num_stops} deliveries across town. "

        for i in range(num_stops):
            # Drive to stop
            distance = random.randint(2, 8)
            speed = random.randint(25, 40)
            drive_time = distance / speed
            total_time += drive_time

            if i == 0:
                problem_text += f"The first stop is {distance} miles away at {speed} mph. "
            elif i == num_stops - 1:
                problem_text += f"The final stop is {distance} miles away at {speed} mph. "
            else:
                problem_text += f"Then {distance} miles to the next stop at {speed} mph. "

            operations.append("divide")
            operations.append("add")

            # Delivery time
            delivery_time = random.choice([0.1, 0.15, 0.2])
            total_time += delivery_time
            delivery_minutes = int(delivery_time * 60)
            problem_text += f"Each delivery takes about {delivery_minutes} minutes. "
            operations.append("add")

        problem_text += f"How long does the entire delivery route take?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        time_rounded = round_to_decimals(total_time, 2)
        answer = f"{time_rounded} hours"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }
