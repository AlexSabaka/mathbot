"""Output formatting for CLI."""

import json
import click
from typing import Dict, Optional


# Descriptions for topics and families
TOPIC_DESCRIPTIONS = {
    'arithmetic': 'Basic arithmetic operations (add, subtract, multiply, divide)',
    'percentages': 'Percentage calculations, increases, and decreases',
    'fractions': 'Fraction operations',
    'ratios': 'Ratios and proportions',
    'algebra': 'Linear equations and simple expressions',
    'geometry': 'Area, perimeter, and volume calculations',
    'quadratics': 'Quadratic equations and parabolas',
    'derivatives': 'Basic derivatives and rates of change',
    'powers_logs': 'Exponents, roots, and logarithms'
}

FAMILY_DESCRIPTIONS = {
    'sequential_purchase': 'Shopping scenarios with multiple purchases and discounts',
    'rate_time': 'Distance, speed, and time problems with multiple segments',
    'compound_growth': 'Interest, investment, and growth over time periods',
    'multi_person_sharing': 'Splitting amounts among multiple people using ratios or percentages',
    'area_perimeter_chain': 'Geometry problems with shape calculations and transformations'
}


def format_pretty(problem: Dict, show_answer: bool = True) -> str:
    """Format problem in human-readable pretty format with colors.

    Args:
        problem: Problem dictionary with structure from generator
        show_answer: Whether to include answer in output

    Returns:
        Formatted string with ANSI colors
    """
    output = []

    # Header
    output.append(click.style("=" * 80, fg='blue'))
    output.append(click.style(f"Problem: {problem['test_id']}", fg='cyan', bold=True))
    output.append(click.style(f"Family: {problem['task_params']['problem_family']}", fg='cyan'))
    output.append(click.style(f"Complexity: {problem['task_params']['complexity']}", fg='cyan'))
    output.append(click.style(f"Grade: {problem['task_params']['grade']}", fg='cyan'))

    # Handle math_topic as list or string
    math_topic = problem['task_params']['math_topic']
    if isinstance(math_topic, list):
        topic_str = ', '.join(math_topic)
    else:
        topic_str = math_topic
    output.append(click.style(f"Topic: {topic_str}", fg='cyan'))
    output.append(click.style("=" * 80, fg='blue'))
    output.append("")

    # Problem text
    output.append(problem['problem'])
    output.append("")

    # Answer (if requested)
    if show_answer:
        output.append(click.style("-" * 80, fg='green'))
        output.append(click.style(f"Answer: {problem['task_params']['expected_answer']}", fg='green', bold=True))
        output.append(click.style(f"Steps: {problem['task_params']['num_steps']}", fg='green'))
        output.append(click.style(f"Operations: {', '.join(problem['task_params']['operations'])}", fg='green'))
        output.append(click.style("-" * 80, fg='green'))

    return '\n'.join(output)


def format_json(problem: Dict, show_answer: bool = True) -> str:
    """Format problem as JSON.

    Args:
        problem: Problem dictionary
        show_answer: Whether to include answer fields

    Returns:
        JSON string
    """
    if not show_answer:
        # Remove answer-related fields
        problem_copy = problem.copy()
        problem_copy['task_params'] = {
            k: v for k, v in problem['task_params'].items()
            if k not in ['expected_answer', 'operations']
        }
        return json.dumps(problem_copy, indent=2)
    return json.dumps(problem, indent=2)


def format_text(problem: Dict, show_answer: bool = True) -> str:
    """Format as plain text (just problem, optionally with answer).

    Args:
        problem: Problem dictionary
        show_answer: Whether to include answer

    Returns:
        Plain text string
    """
    output = [problem['problem']]
    if show_answer:
        output.append(f"\nAnswer: {problem['task_params']['expected_answer']}")
    return '\n'.join(output)


def format_list(options: Dict, category: Optional[str], verbose: bool) -> str:
    """Format the list command output.

    Args:
        options: Dictionary from get_available_options()
        category: Optional category filter (topics|families|grades|all)
        verbose: Whether to show descriptions

    Returns:
        Formatted string for display
    """
    output = []

    if category in ['topics', 'all', None]:
        output.append(click.style("Math Topics:", fg='blue', bold=True))
        for topic in options['math_topics']:
            if verbose:
                desc = TOPIC_DESCRIPTIONS.get(topic, '')
                output.append(f"  {topic:20} {desc}")
            else:
                output.append(f"  {topic}")
        output.append("")

    if category in ['families', 'all', None]:
        output.append(click.style("Problem Families:", fg='blue', bold=True))
        for family in options['problem_families']:
            if verbose:
                desc = FAMILY_DESCRIPTIONS.get(family, '')
                output.append(f"  {family:25} {desc}")
            else:
                output.append(f"  {family}")
        output.append("")

    if category in ['grades', 'all', None]:
        output.append(click.style("Grade Levels:", fg='blue', bold=True))
        output.append(f"  {', '.join(options['grades'])}")
        output.append("")

    if category in ['all', None]:
        output.append(click.style("Complexity Levels:", fg='blue', bold=True))
        output.append(f"  {', '.join(map(str, options['complexity_levels']))} (1=easy, 2=medium, 3=hard)")

    return '\n'.join(output)


def format_info(name: str, options: Dict) -> str:
    """Format detailed info about a topic or family.

    Args:
        name: Name of topic or family
        options: Dictionary from get_available_options()

    Returns:
        Formatted info string
    """
    output = []

    # Check if it's a topic
    if name in options['math_topics']:
        output.append(click.style(f"Topic: {name}", fg='cyan', bold=True))
        output.append(click.style("=" * 60, fg='blue'))
        output.append(f"Description: {TOPIC_DESCRIPTIONS.get(name, 'No description available')}")
        output.append(f"Type: Math Topic")
        output.append(f"\nAvailable in problem families:")
        for family in options['problem_families']:
            output.append(f"  - {family}")

    # Check if it's a family
    elif name in options['problem_families']:
        output.append(click.style(f"Problem Family: {name}", fg='cyan', bold=True))
        output.append(click.style("=" * 60, fg='blue'))
        output.append(f"Description: {FAMILY_DESCRIPTIONS.get(name, 'No description available')}")
        output.append(f"Type: Problem Family")
        output.append(f"Template Variations: 5")
        output.append(f"\nCompatible with topics:")
        for topic in options['math_topics']:
            output.append(f"  - {topic}")

    else:
        return click.style(f"Error: '{name}' is not a valid topic or family", fg='red')

    return '\n'.join(output)
