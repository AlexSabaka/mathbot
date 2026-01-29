"""Multi-person sharing problem family implementation."""

import random
from typing import Dict, List
from faker import Faker
import names

from ..utils import round_money, split_by_ratio, split_by_percentage


class MultiPersonSharingFamily:
    """Generate multi-person sharing problems."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.fake = Faker()

    def generate(self, complexity: int = 2, grade: str = 'middle',
                 math_topic: str = 'ratios', num_steps: int = None) -> Dict:
        """Generate a multi-person sharing problem."""

        # Determine number of steps based on complexity if not specified
        if num_steps is None:
            step_ranges = {1: (1, 2), 2: (2, 3), 3: (3, 5)}
            min_steps, max_steps = step_ranges.get(complexity, (2, 3))
            num_steps = random.randint(min_steps, max_steps)

        # Choose a template
        templates = [
            self._equal_split_template,
            self._ratio_split_template,
            self._proportional_sharing_template,
            self._percentage_split_template,
            self._partnership_template,
        ]

        template_func = random.choice(templates)
        return template_func(complexity, grade, math_topic, num_steps)

    def _equal_split_template(self, complexity: int, grade: str,
                               math_topic: str, num_steps: int) -> Dict:
        """Generate a simple equal split problem."""
        num_people = 2 if complexity == 1 else random.choice([2, 3, 4])
        names_list = [names.get_first_name() for _ in range(num_people)]

        total = random.choice([60, 90, 120, 150, 180])

        # Generate simple equal split
        per_person = total / num_people

        restaurant = self.fake.company().replace("Inc", "Restaurant").replace("LLC", "Cafe").replace("Ltd", "Bistro")
        problem_text = f"A group of {num_people} friends finish dinner at {restaurant}. "
        problem_text += f"The total bill comes to {round_money(total)}, and they decide to split it equally among themselves. "
        problem_text += f"How much does each person pay?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(per_person)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": ["divide"],
            "num_steps": 1
        }

    def _ratio_split_template(self, complexity: int, grade: str,
                              math_topic: str, num_steps: int) -> Dict:
        """Generate a ratio split problem."""
        num_people = 2 if complexity == 1 else (3 if complexity == 2 else 4)
        names_list = [names.get_first_name() for _ in range(num_people)]

        total = random.choice([120, 150, 180, 200, 240])

        # Generate ratios
        if num_people == 2:
            ratios = [1, 2] if random.random() < 0.5 else [2, 3]
        elif num_people == 3:
            ratios = random.choice([[1, 2, 3], [2, 3, 4], [1, 1, 2]])
        else:
            ratios = random.choice([[1, 2, 3, 4], [1, 1, 2, 2], [2, 3, 3, 4]])

        # Calculate shares
        shares = split_by_ratio(total, ratios)

        operations = ["ratio_split"]

        city = self.fake.city()
        ratio_str = ":".join(map(str, ratios))

        people_str = ", ".join(names_list[:-1]) + f" and {names_list[-1]}" if num_people > 1 else names_list[0]
        problem_text = f"After a meal together in {city}, {people_str} receive a bill totaling {round_money(total)}. "
        problem_text += f"They agree to split the cost in the ratio {ratio_str} based on what each person ordered. "
        problem_text += f"How much does each person pay?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        # Format answer
        answer_parts = [f"{names_list[i]}: {round_money(shares[i])}" for i in range(num_people)]
        answer = ", ".join(answer_parts)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _proportional_sharing_template(self, complexity: int, grade: str,
                                       math_topic: str, num_steps: int) -> Dict:
        """Generate a proportional sharing problem based on hours worked."""
        num_people = 2 if complexity == 1 else (3 if complexity == 2 else 4)
        names_list = [names.get_first_name() for _ in range(num_people)]

        total_prize = random.choice([1000, 1500, 2000, 2500, 3000])

        # Generate hours worked
        hours = [random.randint(10, 30) for _ in range(num_people)]

        # Calculate shares based on proportions (same as ratios)
        shares = split_by_ratio(total_prize, hours)

        operations = ["proportional_split"]

        project_type = random.choice(["a community project", "a hackathon", "a research project", "a startup"])
        problem_text = f"A team working on {project_type} wins a prize of {round_money(total_prize)}. "

        hours_desc = []
        for i in range(num_people):
            hours_desc.append(f"{names_list[i]} contributed {hours[i]} hours")

        problem_text += ", ".join(hours_desc[:-1]) + f", and {hours_desc[-1]}. "
        problem_text += f"The team decides to split the prize proportionally based on hours worked. "
        problem_text += f"How much does each person receive?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        # Format answer
        answer_parts = [f"{names_list[i]}: {round_money(shares[i])}" for i in range(num_people)]
        answer = ", ".join(answer_parts)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _percentage_split_template(self, complexity: int, grade: str,
                                   math_topic: str, num_steps: int) -> Dict:
        """Generate a percentage-based split problem."""
        num_people = 2 if complexity == 1 else (3 if complexity == 2 else 4)
        names_list = [names.get_first_name() for _ in range(num_people)]

        total = random.choice([10000, 15000, 20000, 25000, 30000])

        # Generate percentages that sum to 100
        if num_people == 2:
            pct1 = random.choice([40, 50, 60])
            percentages = [pct1, 100 - pct1]
        elif num_people == 3:
            pct1 = random.choice([40, 50])
            pct2 = random.choice([25, 30])
            percentages = [pct1, pct2, 100 - pct1 - pct2]
        else:
            pct1 = random.choice([30, 35])
            pct2 = random.choice([25, 30])
            pct3 = random.choice([15, 20])
            percentages = [pct1, pct2, pct3, 100 - pct1 - pct2 - pct3]

        # Calculate shares
        shares = split_by_percentage(total, percentages)

        operations = ["percentage_split"]

        relation = random.choice(["family estate", "trust fund", "will"])
        problem_text = f"A {relation} worth {round_money(total)} is divided among {num_people} heirs according to specific percentages. "

        pct_desc = []
        for i in range(num_people):
            pct_desc.append(f"{names_list[i]} receives {percentages[i]}%")

        problem_text += ", ".join(pct_desc[:-1]) + f", and {pct_desc[-1]}. "
        problem_text += f"How much does each heir receive?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        # Format answer
        answer_parts = [f"{names_list[i]}: {round_money(shares[i])}" for i in range(num_people)]
        answer = ", ".join(answer_parts)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _partnership_template(self, complexity: int, grade: str,
                             math_topic: str, num_steps: int) -> Dict:
        """Generate an investment partnership problem."""
        num_people = 2 if complexity == 1 else (3 if complexity == 2 else 3)
        names_list = [names.get_first_name() for _ in range(num_people)]

        company = self.fake.company()

        # Generate investments
        if num_people == 2:
            investments = [random.choice([5000, 10000, 15000]),
                          random.choice([5000, 10000, 15000, 20000])]
        else:
            investments = [random.choice([5000, 10000]),
                          random.choice([10000, 15000]),
                          random.choice([15000, 20000])]

        total_profit = random.choice([6000, 8000, 10000, 12000])

        operations = ["proportional_split"]

        # Calculate profit shares based on investment proportions
        shares = split_by_ratio(total_profit, investments)

        problem_text = f"A group of {num_people} entrepreneurs form a partnership to launch {company}. "

        invest_desc = []
        for i in range(num_people):
            invest_desc.append(f"{names_list[i]} invests {round_money(investments[i])}")

        problem_text += ", ".join(invest_desc[:-1]) + f", and {invest_desc[-1]}. "
        problem_text += f"After their first quarter, the business generates a profit of {round_money(total_profit)}. "
        problem_text += f"The partners agree to split the profit proportionally based on their initial investments. "

        # Add operating cost for complexity 3
        if complexity >= 3:
            operating_cost = random.choice([1000, 1500, 2000])
            remaining_profit = total_profit - operating_cost
            shares = split_by_ratio(remaining_profit, investments)
            problem_text += f"However, they first need to pay {round_money(operating_cost)} in operating costs before distributing the remaining profit. "
            problem_text += f"How much does each partner receive?\n\n"
            operations.append("subtract")
            operations.append("proportional_split")
        else:
            problem_text += f"How much profit does each partner receive?\n\n"

        problem_text += "Please solve this problem and provide your final answer."

        # Format answer
        answer_parts = [f"{names_list[i]}: {round_money(shares[i])}" for i in range(num_people)]
        answer = ", ".join(answer_parts)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }
