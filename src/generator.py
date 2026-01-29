"""Main problem generator API."""

import random
from typing import Dict, List, Optional

from .constants import (
    GRADES, MATH_TOPICS, PROBLEM_FAMILIES,
    COMPLEXITY_STEPS_RANGE, TOPIC_GRADE_COMPATIBILITY,
    FAMILY_TOPIC_SUPPORT
)
from .utils import validate_problem_params
from .families import FAMILY_REGISTRY


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
    
    # Validate parameters
    params = validate_problem_params(complexity, grade, math_topic, problem_family, num_steps)
    
    # Fill in random values for unspecified parameters
    final_complexity = params.get('complexity', random.randint(1, 3))
    final_grade = params.get('grade', random.choice(GRADES))

    # Select compatible math topic first (needed for family selection)
    if 'math_topic' in params:
        final_math_topic = params['math_topic']
    else:
        # Get topics compatible with the grade
        compatible_topics = [
            topic for topic in MATH_TOPICS
            if final_grade in TOPIC_GRADE_COMPATIBILITY[topic]
        ]
        final_math_topic = random.choice(compatible_topics) if compatible_topics else "arithmetic"

    # Select problem family - prefer families that support the topic
    if 'problem_family' in params:
        final_problem_family = params['problem_family']
    else:
        # Find families that support the selected topic
        compatible_families = [
            family for family in PROBLEM_FAMILIES
            if final_math_topic in FAMILY_TOPIC_SUPPORT.get(family, [])
        ]

        # If no families support the topic, fall back to all families
        # (the family will do its best to incorporate the topic)
        if compatible_families:
            final_problem_family = random.choice(compatible_families)
        else:
            final_problem_family = random.choice(PROBLEM_FAMILIES)
    
    # Determine number of steps
    final_num_steps = params.get('num_steps')
    if final_num_steps is None:
        min_steps, max_steps = COMPLEXITY_STEPS_RANGE.get(final_complexity, (3, 5))
        final_num_steps = random.randint(min_steps, max_steps)
    
    # Get the problem family generator
    if final_problem_family not in FAMILY_REGISTRY:
        raise ValueError(f"Problem family '{final_problem_family}' not implemented yet")
    
    family_class = FAMILY_REGISTRY[final_problem_family]
    family_generator = family_class(seed=seed)
    
    # Generate the problem
    problem_data = family_generator.generate(
        complexity=final_complexity,
        grade=final_grade,
        math_topic=final_math_topic,
        num_steps=final_num_steps
    )
    
    # Generate test ID
    test_id = f"math_{random.randint(1000, 9999)}_{final_problem_family}"
    
    # Generate config name
    complexity_names = {1: "easy", 2: "medium", 3: "hard"}
    config_name = f"{final_problem_family}_{complexity_names[final_complexity]}_{final_math_topic}"
    
    # Build final output
    result = {
        "test_id": test_id,
        "task_type": "multi_step_math",
        "config_name": config_name,
        "problem": problem_data["problem"],
        "task_params": {
            "complexity": final_complexity,
            "grade": final_grade,
            "math_topic": [final_math_topic],
            "problem_family": final_problem_family,
            "num_steps": problem_data["num_steps"],
            "expected_answer": problem_data["expected_answer"],
            "operations": problem_data["operations"]
        }
    }
    
    return result


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
