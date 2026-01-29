"""Sequential purchase problem family implementation."""

import random
from typing import Dict, List, Tuple
from faker import Faker
import names

from ..utils import (
    generate_price, generate_quantity, generate_percentage,
    apply_percentage_decrease, round_money, round_to_decimals
)


class SequentialPurchaseFamily:
    """Generate sequential purchase problems with shopping scenarios."""

    def __init__(self, seed: int = None):
        """Initialize with optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.fake = Faker()

    def generate(self, complexity: int = 2, grade: str = 'middle',
                 math_topic: str = 'arithmetic', num_steps: int = None) -> Dict:
        """Generate a sequential purchase problem."""

        # Determine number of steps based on complexity if not specified
        if num_steps is None:
            step_ranges = {1: (2, 3), 2: (3, 5), 3: (4, 6)}
            min_steps, max_steps = step_ranges.get(complexity, (3, 5))
            num_steps = random.randint(min_steps, max_steps)

        # Choose a template
        templates = [
            self._grocery_shopping_template,
            self._online_order_template,
            self._electronics_template,
            self._clothing_store_template,
            self._bookstore_template,
        ]

        template_func = random.choice(templates)
        return template_func(complexity, grade, math_topic, num_steps)

    def _grocery_shopping_template(self, complexity: int, grade: str,
                                   math_topic: str, num_steps: int) -> Dict:
        """Generate a grocery shopping problem."""
        person_name = names.get_first_name()
        city = self.fake.city()

        # Grocery items with realistic prices
        grocery_items = [
            ("apples", 0.50, 2.00), ("oranges", 0.60, 2.50), ("bananas", 0.30, 1.50),
            ("milk", 2.50, 5.00), ("bread", 2.00, 4.00), ("eggs", 2.50, 6.00),
            ("cheese", 3.00, 8.00), ("chicken", 5.00, 12.00), ("tomatoes", 0.75, 2.50),
            ("lettuce", 1.50, 3.50),
        ]

        # Select items
        num_items = min(num_steps, 4)
        selected_items = random.sample(grocery_items, num_items)

        operations = []
        running_total = 0.0

        # Generate narrative based on math topic
        if 'algebra' in math_topic and complexity >= 2:
            # Algebra: Solve for unknown quantity or price
            item1_name, min1, max1 = selected_items[0]
            item2_name, min2, max2 = selected_items[1]

            qty1 = generate_quantity(2, 5)
            price1 = generate_price(min1, max1, 0.10)
            qty2 = generate_quantity(2, 4)
            price2 = generate_price(min2, max2, 0.10)

            total = qty1 * price1 + qty2 * price2

            problem_text = f"At a grocery store in {city}, {person_name} is planning a shopping trip. "
            problem_text += f"They want to buy {item1_name} and {item2_name}. "
            problem_text += f"Each {item1_name.rstrip('s')} costs {round_money(price1)}, and each "
            problem_text += f"{item2_name.rstrip('s')} costs {round_money(price2)}. "
            problem_text += f"If {person_name} buys {qty1} {item1_name} and {qty2} {item2_name}, "
            problem_text += f"how much will they spend in total?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = round_money(total)
            operations = ["multiply", "multiply", "add"]

        elif 'fractions' in math_topic:
            # Fractions: Buying fractional quantities
            item1_name, min1, max1 = selected_items[0]
            item2_name, min2, max2 = selected_items[1]

            price1 = generate_price(min1, max1, 0.10)
            price2 = generate_price(min2, max2, 0.10)

            # Use fractional quantities
            frac1_num, frac1_den = random.choice([(1,2), (3,4), (2,3), (1,4)])
            frac2_num, frac2_den = random.choice([(1,2), (3,4), (1,3)])

            total = (frac1_num/frac1_den) * price1 + (frac2_num/frac2_den) * price2

            problem_text = f"{person_name} stops by a market in {city} after work. "
            problem_text += f"They notice {item1_name} are priced at {round_money(price1)} per pound, "
            problem_text += f"and {item2_name} cost {round_money(price2)} per pound. "
            problem_text += f"{person_name} picks up {frac1_num}/{frac1_den} pound of {item1_name} "
            problem_text += f"and {frac2_num}/{frac2_den} pound of {item2_name}. "
            problem_text += f"What's the total cost of these items?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = round_money(total)
            operations = ["multiply", "multiply", "add"]

        else:
            # Default: arithmetic with natural narrative
            problem_text = f"On a busy Saturday morning, {person_name} heads to the local grocery store in {city}. "

            # Build shopping scenario with connected narrative
            for i, (item_name, min_price, max_price) in enumerate(selected_items):
                quantity = generate_quantity(1, 6)
                price = generate_price(min_price, max_price, 0.10)
                item_total = quantity * price
                running_total += item_total

                if i == 0:
                    problem_text += f"While browsing the produce section, they pick up {quantity} {item_name} "
                    problem_text += f"priced at {round_money(price)} each. "
                elif i == 1:
                    problem_text += f"Moving to the dairy aisle, {person_name} grabs {quantity} {item_name} "
                    problem_text += f"at {round_money(price)} each. "
                elif i == 2:
                    problem_text += f"Before checking out, they remember to get {quantity} {item_name}, "
                    problem_text += f"which cost {round_money(price)} each. "
                else:
                    problem_text += f"Finally, they add {quantity} {item_name} "
                    problem_text += f"({round_money(price)} each) to their cart. "

                operations.append("multiply")
                operations.append("add")

            # Add discount scenario if percentages and complexity allows
            if "percentages" in math_topic and complexity >= 2:
                discount_pct = generate_percentage(10, 25, 5)
                running_total = apply_percentage_decrease(running_total, discount_pct)
                problem_text += f"At checkout, {person_name} applies a {discount_pct}% off coupon they had saved. "
                operations.append("percentage_decrease")

            problem_text += f"How much does {person_name} spend in total?\n\n"
            problem_text += "Please solve this problem and provide your final answer."

            answer = round_money(running_total)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _online_order_template(self, complexity: int, grade: str,
                               math_topic: str, num_steps: int) -> Dict:
        """Generate an online shopping problem."""
        person_name = names.get_first_name()
        store = self.fake.company()

        online_items = [
            ("books", 8.00, 25.00), ("notebooks", 3.00, 8.00), ("pens", 1.00, 5.00),
            ("headphones", 15.00, 50.00), ("phone case", 10.00, 30.00),
            ("water bottle", 8.00, 20.00), ("backpack", 20.00, 60.00),
        ]

        num_items = min(num_steps, 3)
        selected_items = random.sample(online_items, num_items)

        operations = []
        running_total = 0.0

        # Natural narrative opening
        day = random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        problem_text = f"It's {day} evening, and {person_name} is browsing {store}'s website looking for supplies. "

        # Build cart with storytelling
        for i, (item_name, min_price, max_price) in enumerate(selected_items):
            quantity = generate_quantity(1, 4)
            price = generate_price(min_price, max_price, 0.50)
            item_total = quantity * price
            running_total += item_total

            if i == 0:
                problem_text += f"They start by adding {quantity} {item_name} to their cart at {round_money(price)} each. "
            elif i == len(selected_items) - 1:
                problem_text += f"As a final item, they add {quantity} {item_name} priced at {round_money(price)} each. "
            else:
                problem_text += f"They also need {quantity} {item_name}, which are {round_money(price)} each. "

            operations.append("multiply")
            operations.append("add")

        # Add shipping cost
        if complexity >= 2:
            shipping = generate_price(5.00, 15.00, 1.00)
            running_total += shipping
            problem_text += f"Shipping to their address costs {round_money(shipping)}. "
            operations.append("add")

        # Add tax if higher complexity
        if complexity >= 3 and "percentages" in math_topic:
            tax_pct = generate_percentage(5, 10, 1)
            running_total = running_total * (1 + tax_pct / 100.0)
            problem_text += f"Sales tax of {tax_pct}% is applied to the entire order. "
            operations.append("percentage_increase")

        problem_text += f"What's {person_name}'s final total?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(running_total)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _electronics_template(self, complexity: int, grade: str,
                             math_topic: str, num_steps: int) -> Dict:
        """Generate an electronics store problem."""
        person_name = names.get_first_name()
        city = self.fake.city()

        electronics = [
            ("laptop", 400.00, 1200.00), ("tablet", 200.00, 600.00),
            ("mouse", 15.00, 50.00), ("keyboard", 30.00, 100.00),
            ("monitor", 150.00, 400.00), ("webcam", 40.00, 120.00),
        ]

        num_items = min(num_steps - 1, 3)
        selected_items = random.sample(electronics, num_items)

        operations = []
        running_total = 0.0

        problem_text = f"{person_name} visits an electronics store in {city} to upgrade their home office setup. "

        for i, (item_name, min_price, max_price) in enumerate(selected_items):
            quantity = 1 if "laptop" in item_name or "tablet" in item_name else generate_quantity(1, 2)
            price = generate_price(min_price, max_price, 5.00)
            item_total = quantity * price
            running_total += item_total

            if quantity == 1:
                problem_text += f"They decide on a {item_name} priced at {round_money(price)}. "
                operations.append("add")
            else:
                problem_text += f"They pick up {quantity} {item_name}s at {round_money(price)} each. "
                operations.append("multiply")
                operations.append("add")

        # Add discount
        if complexity >= 2 and "percentages" in math_topic:
            discount_pct = generate_percentage(10, 30, 5)
            running_total = apply_percentage_decrease(running_total, discount_pct)
            problem_text += f"The store is running a {discount_pct}% off promotion on all items. "
            operations.append("percentage_decrease")

        problem_text += f"How much does {person_name} pay after all discounts?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(running_total)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _clothing_store_template(self, complexity: int, grade: str,
                                math_topic: str, num_steps: int) -> Dict:
        """Generate a clothing store problem."""
        person_name = names.get_first_name()
        store = self.fake.company() + " Boutique"

        clothing_items = [
            ("shirts", 15.00, 40.00), ("pants", 25.00, 60.00),
            ("shoes", 40.00, 100.00), ("socks", 5.00, 15.00),
            ("jackets", 50.00, 150.00), ("sweaters", 30.00, 70.00),
        ]

        num_items = min(num_steps, 3)
        selected_items = random.sample(clothing_items, num_items)

        operations = []
        running_total = 0.0

        season = random.choice(["spring", "summer", "fall", "winter"])
        problem_text = f"With {season} approaching, {person_name} goes shopping at {store}. "

        for i, (item_name, min_price, max_price) in enumerate(selected_items):
            quantity = generate_quantity(1, 3)
            price = generate_price(min_price, max_price, 1.00)
            item_total = quantity * price
            running_total += item_total

            if i == 0:
                problem_text += f"They find {quantity} {item_name} on sale for {round_money(price)} each. "
            else:
                problem_text += f"They also grab {quantity} {item_name} at {round_money(price)} each. "

            operations.append("multiply")
            operations.append("add")

        # Member discount
        if complexity >= 2 and "percentages" in math_topic:
            discount_pct = generate_percentage(15, 25, 5)
            running_total = apply_percentage_decrease(running_total, discount_pct)
            problem_text += f"With their loyalty card, {person_name} gets {discount_pct}% off the entire purchase. "
            operations.append("percentage_decrease")

        problem_text += f"What's the final bill?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(running_total)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }

    def _bookstore_template(self, complexity: int, grade: str,
                           math_topic: str, num_steps: int) -> Dict:
        """Generate a bookstore problem."""
        person_name = names.get_first_name()
        city = self.fake.city()

        book_types = [
            ("novels", 12.00, 25.00), ("textbooks", 40.00, 100.00),
            ("comic books", 5.00, 15.00), ("magazines", 4.00, 10.00),
            ("cookbooks", 20.00, 40.00),
        ]

        num_items = min(num_steps, 3)
        selected_items = random.sample(book_types, num_items)

        operations = []
        running_total = 0.0

        problem_text = f"During a weekend trip to {city}, {person_name} discovers a cozy bookstore. "

        for i, (item_name, min_price, max_price) in enumerate(selected_items):
            quantity = generate_quantity(1, 5)
            price = generate_price(min_price, max_price, 1.00)
            item_total = quantity * price
            running_total += item_total

            if i == 0:
                problem_text += f"They're drawn to a shelf of {item_name} and select {quantity} at {round_money(price)} each. "
            else:
                problem_text += f"Before leaving, they pick up {quantity} {item_name} priced at {round_money(price)} each. "

            operations.append("multiply")
            operations.append("add")

        # Student discount
        if complexity >= 2 and "percentages" in math_topic:
            discount_pct = generate_percentage(10, 20, 5)
            running_total = apply_percentage_decrease(running_total, discount_pct)
            problem_text += f"The bookstore offers a {discount_pct}% student discount, which {person_name} happily uses. "
            operations.append("percentage_decrease")

        problem_text += f"How much does {person_name} spend?\n\n"
        problem_text += "Please solve this problem and provide your final answer."

        answer = round_money(running_total)

        return {
            "problem": problem_text,
            "expected_answer": answer,
            "operations": operations,
            "num_steps": len(operations)
        }
