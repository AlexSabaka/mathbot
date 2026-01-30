"""Unit tests for the math problem generator."""

import pytest
from src import generate_problem, generate_problems, get_available_options
from src.constants import MATH_TOPICS, PROBLEM_FAMILIES, GRADES


class TestSingleProblemGeneration:
    """Test single problem generation."""
    
    def test_basic_generation(self):
        """Test basic problem generation works."""
        problem = generate_problem(seed=42)
        
        assert problem is not None
        assert 'test_id' in problem
        assert 'task_type' in problem
        assert 'problem' in problem
        assert 'task_params' in problem
        assert problem['task_type'] == 'multi_step_math'
    
    def test_with_all_parameters(self):
        """Test generation with all parameters specified."""
        problem = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='arithmetic',
            problem_family='sequential_purchase',
            num_steps=3,
            seed=100
        )
        
        assert problem['task_params']['complexity'] == 2
        assert problem['task_params']['grade'] == 'middle'
        assert 'arithmetic' in problem['task_params']['math_topic']
        assert problem['task_params']['problem_family'] == 'sequential_purchase'
    
    def test_reproducibility(self):
        """Test that same seed produces same problem."""
        problem1 = generate_problem(seed=999)
        problem2 = generate_problem(seed=999)
        
        assert problem1 == problem2
    
    def test_different_seeds_produce_different_problems(self):
        """Test that different seeds produce different problems."""
        problem1 = generate_problem(seed=1)
        problem2 = generate_problem(seed=2)
        
        # At least the answer should be different
        assert problem1['task_params']['expected_answer'] != problem2['task_params']['expected_answer']
    
    def test_invalid_complexity(self):
        """Test that invalid complexity raises error."""
        with pytest.raises(ValueError):
            generate_problem(complexity=5)
    
    def test_invalid_grade(self):
        """Test that invalid grade raises error."""
        with pytest.raises(ValueError):
            generate_problem(grade='invalid')
    
    def test_invalid_math_topic(self):
        """Test that invalid math topic raises error."""
        with pytest.raises(ValueError):
            generate_problem(math_topic='invalid')
    
    def test_invalid_problem_family(self):
        """Test that invalid problem family raises error."""
        with pytest.raises(ValueError):
            generate_problem(problem_family='invalid')


class TestBatchGeneration:
    """Test batch problem generation."""
    
    def test_generate_multiple_problems(self):
        """Test generating multiple problems."""
        problems = generate_problems(n=5, avoid_duplicates=True)
        
        assert len(problems) == 5
        assert all('test_id' in p for p in problems)
    
    # def test_avoid_duplicates(self):
    #     """Test that avoid_duplicates works."""
    #     problems = generate_problems(n=10, avoid_duplicates=True)
        
    #     # Check that answers are mostly different (allowing some collisions)
    #     answers = [p['task_params']['expected_answer'] for p in problems]
    #     unique_answers = len(set(answers))
        
    #     # At least 70% should be unique
    #     assert unique_answers >= 7
    
    def test_batch_with_constraints(self):
        """Test batch generation with constraints."""
        problems = generate_problems(
            n=5,
            complexity=2,
            grade='middle',
            problem_family='sequential_purchase'
        )
        
        assert len(problems) == 5
        assert all(p['task_params']['complexity'] == 2 for p in problems)
        assert all(p['task_params']['grade'] == 'middle' for p in problems)
        assert all(p['task_params']['problem_family'] == 'sequential_purchase' for p in problems)


class TestProblemFamilies:
    """Test individual problem families."""
    
    def test_sequential_purchase(self):
        """Test sequential purchase family."""
        problem = generate_problem(
            problem_family='sequential_purchase',
            seed=42
        )
        
        assert problem['task_params']['problem_family'] == 'sequential_purchase'
        assert '$' in problem['task_params']['expected_answer']
    
    def test_rate_time(self):
        """Test rate time family."""
        problem = generate_problem(
            problem_family='rate_time',
            seed=42
        )
        
        assert problem['task_params']['problem_family'] == 'rate_time'
        assert 'hour' in problem['task_params']['expected_answer'].lower()
    
    def test_compound_growth(self):
        """Test compound growth family."""
        problem = generate_problem(
            problem_family='compound_growth',
            seed=42
        )
        
        assert problem['task_params']['problem_family'] == 'compound_growth'
        assert '$' in problem['task_params']['expected_answer']
    
    def test_multi_person_sharing(self):
        """Test multi-person sharing family."""
        problem = generate_problem(
            problem_family='multi_person_sharing',
            seed=42
        )
        
        assert problem['task_params']['problem_family'] == 'multi_person_sharing'
    
    def test_area_perimeter_chain(self):
        """Test area/perimeter family."""
        problem = generate_problem(
            problem_family='area_perimeter_chain',
            seed=42
        )
        
        assert problem['task_params']['problem_family'] == 'area_perimeter_chain'


class TestAvailableOptions:
    """Test getting available options."""
    
    def test_get_available_options(self):
        """Test getting available options."""
        options = get_available_options()
        
        assert 'math_topics' in options
        assert 'problem_families' in options
        assert 'grades' in options
        assert 'complexity_levels' in options
    
    def test_options_match_constants(self):
        """Test that returned options match constants."""
        options = get_available_options()
        
        assert set(options['math_topics']) == set(MATH_TOPICS)
        assert set(options['problem_families']) == set(PROBLEM_FAMILIES)
        assert set(options['grades']) == set(GRADES)
        assert options['complexity_levels'] == [1, 2, 3]


class TestProblemQuality:
    """Test problem quality constraints."""
    
    def test_problem_has_text(self):
        """Test that problem has non-empty text."""
        problem = generate_problem(seed=42)
        
        assert len(problem['problem']) > 0
        assert len(problem['task_params']['expected_answer']) > 0
    
    def test_problem_has_operations(self):
        """Test that problem has operations listed."""
        problem = generate_problem(seed=42)
        
        assert len(problem['task_params']['operations']) > 0
    
    def test_num_steps_reasonable(self):
        """Test that number of steps is reasonable."""
        problem = generate_problem(seed=42)
        
        num_steps = problem['task_params']['num_steps']
        assert 1 <= num_steps <= 10
    
    def test_complexity_affects_steps(self):
        """Test that complexity affects number of steps."""
        easy = generate_problem(complexity=1, seed=42)
        hard = generate_problem(complexity=3, seed=42)
        
        # Hard problems should generally have more steps
        assert easy['task_params']['num_steps'] <= hard['task_params']['num_steps'] + 2
