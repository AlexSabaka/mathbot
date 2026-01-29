#!/usr/bin/env python3
"""Test script to verify the math problem generator works."""

import json
from src import generate_problem, generate_problems, get_available_options


def test_single_problem():
    """Test generating a single problem."""
    print("=" * 80)
    print("TEST 1: Single Problem Generation")
    print("=" * 80)
    
    problem = generate_problem(
        complexity=2,
        grade='middle',
        math_topic='arithmetic',
        problem_family='sequential_purchase',
        num_steps=3,
        seed=42
    )
    
    print(json.dumps(problem, indent=2))
    print("\n✓ Single problem generated successfully!\n")


def test_multiple_problems():
    """Test generating multiple problems."""
    print("=" * 80)
    print("TEST 2: Multiple Problems Generation")
    print("=" * 80)
    
    problems = generate_problems(
        n=3,
        complexity=2,
        grade='middle',
        avoid_duplicates=True
    )
    
    print(f"Generated {len(problems)} problems:\n")
    for i, problem in enumerate(problems, 1):
        print(f"Problem {i}:")
        print(f"  ID: {problem['test_id']}")
        print(f"  Family: {problem['task_params']['problem_family']}")
        print(f"  Answer: {problem['task_params']['expected_answer']}")
        print(f"  Steps: {problem['task_params']['num_steps']}")
        print()
    
    print("✓ Multiple problems generated successfully!\n")


def test_random_problem():
    """Test generating a completely random problem."""
    print("=" * 80)
    print("TEST 3: Random Problem (No Parameters)")
    print("=" * 80)
    
    problem = generate_problem(seed=999)
    
    print("Problem Text:")
    print("-" * 80)
    print(problem['problem'])
    print("-" * 80)
    print(f"\nExpected Answer: {problem['task_params']['expected_answer']}")
    print(f"Complexity: {problem['task_params']['complexity']}")
    print(f"Grade: {problem['task_params']['grade']}")
    print(f"Operations: {', '.join(problem['task_params']['operations'])}")
    print("\n✓ Random problem generated successfully!\n")


def test_available_options():
    """Test getting available options."""
    print("=" * 80)
    print("TEST 4: Available Options")
    print("=" * 80)
    
    options = get_available_options()
    
    print("Available Options:")
    print(json.dumps(options, indent=2))
    print("\n✓ Options retrieved successfully!\n")


def test_reproducibility():
    """Test that same seed produces same problem."""
    print("=" * 80)
    print("TEST 5: Reproducibility (Same Seed)")
    print("=" * 80)
    
    problem1 = generate_problem(seed=12345)
    problem2 = generate_problem(seed=12345)
    
    match = problem1['task_params']['expected_answer'] == problem2['task_params']['expected_answer']
    
    print(f"Problem 1 Answer: {problem1['task_params']['expected_answer']}")
    print(f"Problem 2 Answer: {problem2['task_params']['expected_answer']}")
    print(f"Match: {match}")
    
    if match:
        print("\n✓ Reproducibility test passed!\n")
    else:
        print("\n✗ Reproducibility test failed!\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MATH PROBLEM GENERATOR - TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_single_problem()
        test_multiple_problems()
        test_random_problem()
        test_available_options()
        test_reproducibility()
        
        print("=" * 80)
        print("ALL TESTS PASSED! 🎉")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
