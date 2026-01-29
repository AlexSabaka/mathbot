#!/usr/bin/env python3
"""
Example usage of the math problem generator library.
"""

from src import generate_problem, generate_problems, get_available_options
import json


def example_basic_usage():
    """Basic example: Generate a single problem."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Usage - Single Problem")
    print("=" * 80 + "\n")
    
    problem = generate_problem(
        complexity=2,
        grade='middle',
        math_topic='arithmetic',
        problem_family='sequential_purchase',
        seed=42
    )
    
    print(problem['problem'])
    print(f"\nExpected Answer: {problem['task_params']['expected_answer']}")


def example_batch_generation():
    """Generate multiple problems for a test set."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Batch Generation - Create a Test Set")
    print("=" * 80 + "\n")
    
    problems = generate_problems(
        n=5,
        complexity=2,
        grade='middle',
        avoid_duplicates=True
    )
    
    print(f"Generated {len(problems)} problems:\n")
    for i, problem in enumerate(problems, 1):
        print(f"{i}. {problem['task_params']['problem_family']} problem")
        print(f"   Answer: {problem['task_params']['expected_answer']}")
        print(f"   Steps: {problem['task_params']['num_steps']}")
        print()


def example_different_topics():
    """Show problems from different math topics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Different Math Topics")
    print("=" * 80 + "\n")
    
    topics = ['arithmetic', 'percentages', 'geometry']
    
    for topic in topics:
        problem = generate_problem(
            math_topic=topic,
            grade='middle',
            seed=100 + topics.index(topic)
        )
        
        print(f"Topic: {topic.upper()}")
        print("-" * 80)
        print(problem['problem'][:200] + "...\n")  # First 200 chars
        print(f"Answer: {problem['task_params']['expected_answer']}\n")


def example_complexity_levels():
    """Show problems at different complexity levels."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Different Complexity Levels")
    print("=" * 80 + "\n")
    
    for complexity in [1, 2, 3]:
        problem = generate_problem(
            complexity=complexity,
            problem_family='sequential_purchase',
            seed=200 + complexity
        )
        
        complexity_names = {1: "Easy", 2: "Medium", 3: "Hard"}
        print(f"Complexity: {complexity_names[complexity]} ({complexity})")
        print(f"Steps: {problem['task_params']['num_steps']}")
        print(f"Operations: {', '.join(problem['task_params']['operations'][:3])}...")
        print()


def example_export_json():
    """Export problems to JSON format."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Export to JSON")
    print("=" * 80 + "\n")
    
    problems = generate_problems(
        n=3,
        complexity=2,
        grade='high',
        problem_family='compound_growth'
    )
    
    # Save to file
    with open('sample_problems.json', 'w') as f:
        json.dump(problems, f, indent=2)
    
    print("✓ Exported 3 problems to 'sample_problems.json'")
    print("\nFirst problem preview:")
    print(json.dumps(problems[0], indent=2)[:500] + "...")


def example_reproducibility():
    """Demonstrate reproducible generation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Reproducibility with Seeds")
    print("=" * 80 + "\n")
    
    seed = 12345
    
    print(f"Generating two problems with seed={seed}...\n")
    
    problem1 = generate_problem(seed=seed)
    problem2 = generate_problem(seed=seed)
    
    print(f"Problem 1 ID: {problem1['test_id']}")
    print(f"Problem 2 ID: {problem2['test_id']}")
    print(f"\nProblems identical: {problem1 == problem2}")
    print("✓ Same seed produces identical problems!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MATH PROBLEM GENERATOR - EXAMPLES")
    print("=" * 80)
    
    example_basic_usage()
    example_batch_generation()
    example_different_topics()
    example_complexity_levels()
    example_export_json()
    example_reproducibility()
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE!")
    print("=" * 80 + "\n")
