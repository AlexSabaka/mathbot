"""Main problem generator API."""

import random
from typing import Dict, List, Optional

from .constants import (
    GRADES, MATH_TOPICS, PROBLEM_FAMILIES,
    COMPLEXITY_STEPS_RANGE, TOPIC_GRADE_COMPATIBILITY,
    FAMILY_TOPIC_SUPPORT
)
from .utils import validate_problem_params
from .template_generator import TemplateGenerator


def generate_problem(
    complexity: Optional[int] = None,
    grade: Optional[str] = None,
    math_topic: Optional[str] = None,
    problem_family: Optional[str] = None,
    num_steps: Optional[int] = None,
    seed: Optional[int] = None
) -> Dict:
    """
    Generate a single math problem.
    
    Args:
        complexity: Difficulty level (1-3), default random
        grade: Educational level, default random
        math_topic: Primary math concept, default random
        problem_family: Problem template category, default random
        num_steps: Number of operations (1-10), default based on complexity
        seed: Random seed for reproducibility
        
    Returns:
        Dict with problem specification including:
        - test_id: Unique identifier
        - task_type: "multi_step_math"
        - config_name: Configuration description
        - problem: The problem text
        - task_params: Problem parameters and metadata
    """
    # Set seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Use new template-based generator
    template_gen = TemplateGenerator(seed=seed)
    
    # Get available options from actual templates
    available_options = template_gen.get_available_options()
    
    # Map high-level grades to actual k-grades
    if grade in ['elementary', 'middle', 'high']:
        # Let template generator handle it
        final_grade = grade
    elif grade and grade in available_options['grades']:
        final_grade = grade
    else:
        # Select from available grades
        final_grade = random.choice(available_options['grades']) if not grade else grade
    
    # Use available topics
    if math_topic and math_topic in available_options['math_topics']:
        final_math_topic = math_topic
    else:
        final_math_topic = random.choice(available_options['math_topics']) if not math_topic else math_topic
    
    # Generate the problem
    problem_data = template_gen.generate(
        complexity=complexity,
        grade=final_grade,
        math_topic=final_math_topic,
        problem_family=problem_family,
        num_steps=num_steps,
        seed=seed
    )
    
    # Template generator returns complete structure
    return problem_data


def generate_problems(
    n: int = 10,
    complexity: Optional[int] = None,
    grade: Optional[str] = None,
    math_topic: Optional[str] = None,
    problem_family: Optional[str] = None,
    num_steps: Optional[int] = None,
    avoid_duplicates: bool = True
) -> List[Dict]:
    """
    Generate multiple math problems.
    
    Args:
        n: Number of problems to generate
        complexity: Difficulty level (1-3), default random for each
        grade: Educational level, default random for each
        math_topic: Primary math concept, default random for each
        problem_family: Problem template category, default random for each
        num_steps: Number of operations (1-10), default based on complexity
        avoid_duplicates: Try to generate unique problems (varies seeds)
        
    Returns:
        List of problem dictionaries
    """
    problems = []
    
    for i in range(n):
        # Use different seeds if avoiding duplicates
        seed = i if avoid_duplicates else None
        
        problem = generate_problem(
            complexity=complexity,
            grade=grade,
            math_topic=math_topic,
            problem_family=problem_family,
            num_steps=num_steps,
            seed=seed
        )
        
        problems.append(problem)
    
    return problems


def get_available_options() -> Dict[str, List[str]]:
    """
    Get all available configuration options.
    
    Returns:
        Dictionary with available math topics, problem families, and grades
    """
    return {
        "math_topics": MATH_TOPICS,
        "problem_families": PROBLEM_FAMILIES,
        "grades": GRADES,
        "complexity_levels": [1, 2, 3]
    }
