"""Compound growth problem family implementation."""

import random
from typing import Dict
from faker import Faker
import names

from ..utils import (
    apply_percentage_increase, apply_percentage_decrease,
    round_money, round_to_decimals
)


class CompoundGrowthFamily:
    """Generate compound growth/interest problems."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.fake = Faker()

    def generate(self, complexity: int = 2, grade: str = 'high',
                 math_topic: str = 'percentages', num_steps: int = None) -> Dict:
        """Generate a compound growth problem."""

        # Determine number of steps based on complexity if not specified
        if num_steps is None:
            step_ranges = {1: (1, 2), 2: (2, 3), 3: (3, 5)}
            min_steps, max_steps = step_ranges.get(complexity, (2, 3))
            num_steps = random.randint(min_steps, max_steps)

        # Choose template based on math topic
        if 'powers_logs' in math_topic:
            # Powers/logs best fits with compound interest
            template_func = self._compound_interest_template
        else:
            # Choose randomly for other topics
            templates = [
                self._compound_interest_template,
                self._investment_with_transactions_template,
                self._population_growth_template,
                self._business_revenue_template,
                self._depreciation_template,
            ]
            template_func = random.choice(templates)

        return template_func(complexity, grade, math_topic, num_steps)

    def _compound_interest_template(self, complexity: int, grade: str,
                                    math_topic: str, num_steps: int) -> Dict:
        """Generate a basic compound interest problem."""
        person_name = names.get_first_name()

        principal = random.choice([500, 1000, 1500, 2000, 2500])
        rate = random.choice([3, 4, 5, 6, 7])

        # Handle powers_logs topic - ask about time to reach a goal
        if 'powers_logs' in math_topic and grade in ['high', 'college', 'university']:
            import math
            target_multiple = random.choice([2, 3, 4])
            target_amount = principal * target_multiple

            # Calculate years using logarithm: t = log(target/principal) / log(1 + r)
            years_exact = math.log(target_amount / principal) / math.log(1 + rate / 100.0)
            years_rounded = round_to_decimals(years_exact, 2)

            problem_text = f"{person_name} invests {round_money(principal)} in an account earning {rate}% annual interest, compounded yearly. "
            problem_text += f"They want to know how long it will take for their investment to reach {round_money(target_amount)}. "
            problem_text += f"Using the formula t = log(A/P) / log(1 + r), where A is the target amount, P is the principal, "
            problem_text += f"and r is the rate (as a decimal), how many years will it take?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = f"{years_rounded} years"
            operations = ["log", "log", "divide"]

        else:
            # Standard compound interest
            years = min(complexity + 1, num_steps)
            amount = principal
            operations = []

            for _ in range(years):
                amount = apply_percentage_increase(amount, rate)
                operations.append("percentage_increase")

            year_desc = f"{years} year" if years == 1 else f"{years} years"
            problem_text = f"{person_name} opens a savings account with an initial deposit of {round_money(principal)}. "
            problem_text += f"The account earns {rate}% interest per year, compounded annually. "
            problem_text += f"After leaving the money untouched for {year_desc}, {person_name} checks the balance. "
            problem_text += f"How much money does {person_name} have in the account?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = round_money(amount)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _investment_with_transactions_template(self, complexity: int, grade: str,
                                               math_topic: str, num_steps: int) -> Dict:
        """Generate an investment problem with deposits and withdrawals."""
        person_name = names.get_first_name()

        principal = random.choice([1000, 1500, 2000, 2500, 3000])
        rate1 = random.choice([4, 5, 6])

        amount = principal
        operations = []

        problem_text = f"{person_name} opens a savings account with an initial deposit of {round_money(principal)}. "

        # Year 1: Interest
        amount = apply_percentage_increase(amount, rate1)
        problem_text += f"During the first year, the account earns {rate1}% interest. "
        operations.append("percentage_increase")

        # Year 2: Interest + deposit/withdrawal
        if complexity >= 2:
            rate2 = random.choice([4, 5, 6, 7])
            amount = apply_percentage_increase(amount, rate2)
            problem_text += f"In the second year, the interest rate is {rate2}%, which is applied to the balance. "
            operations.append("percentage_increase")

            # Add transaction
            transaction_type = random.choice(["deposit", "withdraw"])
            transaction_amount = random.choice([200, 300, 400, 500])

            if transaction_type == "deposit":
                amount += transaction_amount
                problem_text += f"After receiving the second year's interest, {person_name} adds {round_money(transaction_amount)} to the account. "
                operations.append("add")
            else:
                amount -= transaction_amount
                problem_text += f"Following the second year's interest payment, {person_name} makes a withdrawal of {round_money(transaction_amount)}. "
                operations.append("subtract")

        # Year 3: For complexity 3
        if complexity >= 3:
            rate3 = random.choice([4, 5, 6, 7])
            amount = apply_percentage_increase(amount, rate3)
            problem_text += f"The third year brings {rate3}% interest on the current balance. "
            operations.append("percentage_increase")

        problem_text += f"What is the total amount in {person_name}'s account?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(amount)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _population_growth_template(self, complexity: int, grade: str,
                                    math_topic: str, num_steps: int) -> Dict:
        """Generate a population growth problem."""
        city = self.fake.city()

        initial_pop = random.choice([10000, 15000, 20000, 25000, 30000])
        rate = random.choice([2, 3, 4, 5])
        years = min(complexity + 1, 3)

        population = initial_pop
        operations = []

        year_desc = f"{years} year" if years == 1 else f"{years} consecutive years"
        problem_text = f"The city of {city} has a population of {initial_pop:,} people. "
        problem_text += f"Over the next {year_desc}, the city experiences steady growth at {rate}% per year. "

        for year in range(years):
            population = apply_percentage_increase(population, rate)
            operations.append("percentage_increase")

        # Add migration for complexity 3
        if complexity >= 3:
            migration = random.choice([1000, 1500, 2000, 2500])
            migration_type = random.choice(["in", "out"])

            if migration_type == "in":
                population += migration
                problem_text += f"Additionally, {migration:,} people relocate to {city} from other areas. "
                operations.append("add")
            else:
                population -= migration
                problem_text += f"However, {migration:,} residents move away to other cities. "
                operations.append("subtract")

        problem_text += f"What is the current population of {city}?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = f"{int(round(population)):,}"

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _business_revenue_template(self, complexity: int, grade: str,
                                   math_topic: str, num_steps: int) -> Dict:
        """Generate a business revenue growth problem."""
        company = self.fake.company()

        initial_revenue = random.choice([50000, 75000, 100000, 150000])
        rate1 = random.choice([10, 12, 15, 18, 20])

        revenue = initial_revenue
        operations = []

        problem_text = f"{company} starts with annual revenue of {round_money(initial_revenue)}. "

        # Year 1
        revenue = apply_percentage_increase(revenue, rate1)
        problem_text += f"In the first year, the company experiences {rate1}% revenue growth. "
        operations.append("percentage_increase")

        # Year 2 for complexity 2+
        if complexity >= 2:
            rate2 = random.choice([10, 12, 15, 18, 20])
            revenue = apply_percentage_increase(revenue, rate2)
            problem_text += f"The following year brings another {rate2}% increase in revenue. "
            operations.append("percentage_increase")

        # Year 3 for complexity 3
        if complexity >= 3:
            rate3 = random.choice([8, 10, 12, 15])
            revenue = apply_percentage_increase(revenue, rate3)
            problem_text += f"In the third year, revenue continues growing at {rate3}%. "
            operations.append("percentage_increase")

            # Add expense
            expense = random.choice([10000, 15000, 20000])
            revenue -= expense
            problem_text += f"However, the company must cover {round_money(expense)} in one-time acquisition costs. "
            operations.append("subtract")

        problem_text += f"What is {company}'s net revenue after these changes?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(revenue)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _depreciation_template(self, complexity: int, grade: str,
                               math_topic: str, num_steps: int) -> Dict:
        """Generate a depreciation problem."""
        person_name = names.get_first_name()

        # Choose item type
        item_types = [
            ("car", 25000, 35000, [10, 12, 15]),
            ("laptop", 1200, 2000, [20, 25, 30]),
            ("machinery", 50000, 80000, [10, 12, 15])
        ]

        item_type, min_price, max_price, dep_rates = random.choice(item_types)
        initial_value = random.randint(min_price // 100, max_price // 100) * 100
        rate = random.choice(dep_rates)
        years = min(complexity + 1, 3)

        value = initial_value
        operations = []

        year_desc = f"{years} year" if years == 1 else f"{years} years"
        problem_text = f"{person_name} purchases a {item_type} for {round_money(initial_value)}. "
        problem_text += f"Over the next {year_desc}, the {item_type} depreciates at {rate}% per year. "

        for year in range(years):
            value = apply_percentage_decrease(value, rate)
            operations.append("percentage_decrease")

        # Add resale or trade-in for complexity 3
        if complexity >= 3 and years >= 2:
            resale_bonus = random.choice([500, 1000, 1500])
            value += resale_bonus
            problem_text += f"When {person_name} decides to sell, the dealer offers a {round_money(resale_bonus)} trade-in bonus on top of the depreciated value. "
            operations.append("add")

        problem_text += f"What is the final value of the {item_type}?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(value)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }
