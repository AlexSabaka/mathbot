"""Essential tests for the YAML+Jinja2 math problem generator."""

import pytest
from src import generate_problem, generate_problems, get_available_options
from src.constants import MATH_TOPICS, PROBLEM_FAMILIES, GRADES


class TestBasicGeneration:
    """Test core problem generation functionality."""
    
    def test_basic_structure(self):
        """Test that generated problems have correct structure."""
        problem = generate_problem(
            complexity=2,
            grade='elementary',
            math_topic='arithmetic',
            seed=42
        )
        
        # Verify output structure
        assert 'test_id' in problem
        assert 'task_type' in problem
        assert 'config_name' in problem
        assert 'problem' in problem
        assert 'task_params' in problem
        
        # Verify task_type
        assert problem['task_type'] == 'multi_step_math'
        
        # Verify task_params structure
        params = problem['task_params']
        assert 'complexity' in params
        assert 'grade' in params
        assert 'math_topic' in params
        assert 'problem_family' in params
        assert 'num_steps' in params
        assert 'expected_answer' in params
        assert 'operations' in params
    
    def test_reproducibility(self):
        """Test that same seed produces identical problems."""
        problem1 = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='arithmetic',
            seed=12345
        )
        problem2 = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='arithmetic',
            seed=12345
        )
        
        # Entire problem should be identical
        assert problem1 == problem2
    
    def test_different_seeds_differ(self):
        """Test that different seeds produce different problems."""
        problem1 = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='arithmetic',
            seed=100
        )
        problem2 = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='arithmetic',
            seed=200
        )
        
        # At minimum, values should differ
        assert problem1['task_params']['expected_answer'] != \
               problem2['task_params']['expected_answer']


class TestParameterValidation:
    """Test parameter validation."""
    
    def test_invalid_math_topic(self):
        """Test that invalid math topic results in no templates."""
        with pytest.raises(ValueError, match="No templates found"):
            generate_problem(math_topic='quantum_physics')
    
    def test_invalid_problem_family(self):
        """Test that invalid problem family results in no templates."""
        with pytest.raises(ValueError, match="No templates found"):
            generate_problem(problem_family='nonexistent')


class TestBatchGeneration:
    """Test batch generation."""
    
    def test_batch_count(self):
        """Test generating correct number of problems."""
        problems = generate_problems(
            n=3,
            complexity=2,
            grade='elementary',
            math_topic='arithmetic'
        )
        
        assert len(problems) == 3
        assert all('test_id' in p for p in problems)


class TestMultiAnswer:
    """Test multi-answer problem support."""
    
    def test_multi_answer_geometry(self):
        """Test geometry problems with multiple answers."""
        problem = generate_problem(
            complexity=2,
            grade='elementary',
            math_topic='geometry',
            seed=12345
        )
        
        answer = problem['task_params']['expected_answer']
        
        # Multi-answer problems use | separator
        if '|' in answer:
            parts = answer.split(' | ')
            assert len(parts) >= 2
            # Each part should be a valid answer
            assert all(len(p.strip()) > 0 for p in parts)


class TestAnswerFormats:
    """Test answer formatting for different problem types."""
    
    def test_money_format(self):
        """Test money answers are properly formatted."""
        problem = generate_problem(
            complexity=2,
            grade='elementary',
            math_topic='arithmetic',
            problem_family='shopping',
            seed=42
        )
        
        answer = problem['task_params']['expected_answer']
        # Money answers should start with $
        assert answer.startswith('$')
    
    def test_time_format(self):
        """Test time answers include units."""
        problem = generate_problem(
            complexity=2,
            grade='middle',
            math_topic='measurement',
            problem_family='travel',
            seed=42
        )
        
        answer = problem['task_params']['expected_answer']
        # Time answers should have time units
        assert any(unit in answer.lower() for unit in ['hour', 'minute', 'second'])


class TestAvailableOptions:
    """Test configuration options."""
    
    def test_get_options(self):
        """Test getting available options."""
        options = get_available_options()
        
        assert 'math_topics' in options
        assert 'problem_families' in options
        assert 'grades' in options
        assert 'complexity_levels' in options
        
        # Verify types
        assert isinstance(options['math_topics'], list)
        assert isinstance(options['problem_families'], list)
        assert isinstance(options['grades'], list)
        assert options['complexity_levels'] == [1, 2, 3]
