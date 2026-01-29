"""Utility functions for the math problem generator."""

import random
from typing import Any, List
from decimal import Decimal, ROUND_HALF_UP


def round_money(value: float) -> str:
    """Round a value to 2 decimal places and format as money."""
    decimal_value = Decimal(str(value))
    rounded = decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"${rounded:.2f}"


def round_to_decimals(value: float, decimals: int = 2) -> float:
    """Round a value to specified decimal places."""
    decimal_value = Decimal(str(value))
    quantizer = Decimal(10) ** -decimals
    return float(decimal_value.quantize(quantizer, rounding=ROUND_HALF_UP))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def generate_price(min_price: float = 0.5, max_price: float = 50.0, step: float = 0.25) -> float:
    """Generate a realistic price with quarter increments."""
    num_steps = int((max_price - min_price) / step)
    random_step = random.randint(0, num_steps)
    return round_to_decimals(min_price + (random_step * step), 2)


def generate_quantity(min_qty: int = 1, max_qty: int = 10) -> int:
    """Generate a random quantity."""
    return random.randint(min_qty, max_qty)


def generate_percentage(min_pct: int = 5, max_pct: int = 50, step: int = 5) -> int:
    """Generate a percentage value."""
    num_steps = (max_pct - min_pct) // step
    return min_pct + (random.randint(0, num_steps) * step)


def apply_percentage_increase(value: float, percentage: float) -> float:
    """Apply a percentage increase to a value."""
    return value * (1 + percentage / 100.0)


def apply_percentage_decrease(value: float, percentage: float) -> float:
    """Apply a percentage decrease to a value."""
    return value * (1 - percentage / 100.0)


def validate_problem_params(complexity: int = None, grade: str = None,
                           math_topic: str = None, problem_family: str = None,
                           num_steps: int = None) -> dict:
    """Validate and normalize problem generation parameters."""
    from .constants import (GRADES, MATH_TOPICS, PROBLEM_FAMILIES,
                           GRADE_MAX_COMPLEXITY, TOPIC_GRADE_COMPATIBILITY)

    params = {}

    # Validate complexity
    if complexity is not None:
        if not isinstance(complexity, int) or complexity < 1 or complexity > 3:
            raise ValueError("Complexity must be an integer between 1 and 3")
        params['complexity'] = complexity

    # Validate grade
    if grade is not None:
        if grade not in GRADES:
            raise ValueError(f"Grade must be one of: {GRADES}")
        params['grade'] = grade

    # Validate math topic
    if math_topic is not None:
        if math_topic not in MATH_TOPICS:
            raise ValueError(f"Math topic must be one of: {MATH_TOPICS}")
        params['math_topic'] = math_topic

    # Validate problem family
    if problem_family is not None:
        if problem_family not in PROBLEM_FAMILIES:
            raise ValueError(f"Problem family must be one of: {PROBLEM_FAMILIES}")
        params['problem_family'] = problem_family

    # Validate num_steps
    if num_steps is not None:
        if not isinstance(num_steps, int) or num_steps < 1 or num_steps > 10:
            raise ValueError("Number of steps must be an integer between 1 and 10")
        params['num_steps'] = num_steps

    # Check topic-grade compatibility
    if math_topic and grade:
        if grade not in TOPIC_GRADE_COMPATIBILITY.get(math_topic, []):
            # Adjust grade to be compatible
            compatible_grades = TOPIC_GRADE_COMPATIBILITY[math_topic]
            params['grade'] = compatible_grades[-1]  # Use highest compatible grade

    return params


def split_by_ratio(total: float, ratios: List[int]) -> List[float]:
    """Split total amount by ratio parts.

    Args:
        total: Total amount to split
        ratios: List of ratio parts (e.g., [2, 3, 5])

    Returns:
        List of amounts corresponding to each ratio part

    Example:
        split_by_ratio(100, [1, 2, 3]) -> [16.67, 33.33, 50.00]
    """
    ratio_sum = sum(ratios)
    return [round_to_decimals(total * r / ratio_sum, 2) for r in ratios]


def split_by_percentage(total: float, percentages: List[float]) -> List[float]:
    """Split total by percentage allocations.

    Args:
        total: Total amount to split
        percentages: List of percentages (e.g., [50, 30, 20])

    Returns:
        List of amounts corresponding to each percentage

    Example:
        split_by_percentage(100, [50, 30, 20]) -> [50.00, 30.00, 20.00]
    """
    return [round_to_decimals(total * p / 100.0, 2) for p in percentages]
