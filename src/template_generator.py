"""YAML-based template problem generator for mathbot v2.0."""

import random
from pathlib import Path
from typing import Dict, List, Optional
from faker import Faker

from .yaml_loader import YAMLLoader, TemplateDefinition, discover_yaml_templates
from .variable_generator import VariableGenerator
from .jinja_renderer import JinjaRenderer
from .solution_evaluator import execute_solution, format_answer
from .constants import PROBLEM_FAMILIES


# Grade mapping for compatibility
GRADE_MAP = {
    'elementary': ['k1', 'k2', 'k3', 'k4', 'k5'],
    'middle': ['k6', 'k7', 'k8'],
    'high': ['k9', 'k10', 'k11', 'k12'],
}

# Family aliases for backward compatibility
FAMILY_ALIASES = {
    'sequential_purchase': 'shopping',
    'rate_time': 'travel',
    'compound_growth': 'growth',
    'multi_person_sharing': 'sharing',
    'area_perimeter_chain': 'geometry',
}

# Reverse mapping (new → old) for output
FAMILY_REVERSE_ALIASES = {v: k for k, v in FAMILY_ALIASES.items()}


class TemplateGenerator:
    """Generates math problems from YAML templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None, seed: Optional[int] = None):
        """Initialize generator.
        
        Args:
            templates_dir: Path to templates directory (default: src/templates/)
            seed: Random seed for reproducibility
        """
        if templates_dir is None:
            # Default to src/templates/
            current_dir = Path(__file__).parent
            templates_dir = current_dir / 'templates'
        
        self.templates_dir = templates_dir
        self.seed = seed
        
        # Initialize components
        self.loader = YAMLLoader()
        self.renderer = JinjaRenderer()
        
        # Set random seeds if provided
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        # Load all templates
        self._load_templates()
    
    def _load_templates(self):
        """Discover and load all YAML templates."""
        self.templates: Dict[str, TemplateDefinition] = {}
        self.template_paths: Dict[str, Path] = {}  # Store paths by template ID
        self.templates_by_criteria: Dict[str, List[TemplateDefinition]] = {}
        
        yaml_files = discover_yaml_templates(self.templates_dir)
        
        for file_path in yaml_files:
            template = self.loader.load_template(file_path)
            if template:
                self.templates[template.id] = template
                self.template_paths[template.id] = file_path  # Store the path
                
                # Index by various criteria for filtering
                self._index_template(template)
            else:
                # Print validation errors
                errors, warnings = self.loader.get_validation_results()
                if errors:
                    print(f"Failed to load {file_path}:")
                    for error in errors:
                        print(f"  ERROR: {error}")
    
    def _index_template(self, template: TemplateDefinition):
        """Index template by various criteria for fast filtering."""
        # Index by grade
        grade_key = f"grade_{template.grade}"
        self.templates_by_criteria.setdefault(grade_key, []).append(template)
        
        # Index by difficulty
        diff_key = f"difficulty_{template.difficulty}"
        self.templates_by_criteria.setdefault(diff_key, []).append(template)
        
        # Index by family
        family_key = f"family_{template.family}"
        self.templates_by_criteria.setdefault(family_key, []).append(template)
        
        # Index by topic
        topic_key = f"topic_{template.topic}"
        self.templates_by_criteria.setdefault(topic_key, []).append(template)
        
        # Index by steps
        steps_key = f"steps_{template.steps}"
        self.templates_by_criteria.setdefault(steps_key, []).append(template)
    
    def _filter_templates(
        self,
        complexity: Optional[int] = None,
        grade: Optional[str] = None,
        math_topic: Optional[str] = None,
        problem_family: Optional[str] = None,
        num_steps: Optional[int] = None
    ) -> List[TemplateDefinition]:
        """Filter templates by criteria."""
        candidates = list(self.templates.values())
        
        # Filter by complexity (maps to difficulty)
        if complexity is not None:
            difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
            difficulty = difficulty_map.get(complexity)
            if difficulty:
                candidates = [t for t in candidates if t.difficulty == difficulty]
        
        # Filter by grade
        if grade is not None:
            # Map grade names to k-grades
            if grade in GRADE_MAP:
                k_grades = GRADE_MAP[grade]
                # Extract grade number (k4 → 4)
                candidates = [t for t in candidates if f"k{t.grade}" in k_grades]
            elif grade.startswith('k'):
                grade_num = int(grade[1:])
                candidates = [t for t in candidates if t.grade == grade_num]
            else:
                # Try direct number
                try:
                    grade_num = int(grade)
                    candidates = [t for t in candidates if t.grade == grade_num]
                except ValueError:
                    pass
        
        # Filter by math topic
        if math_topic is not None:
            candidates = [t for t in candidates if math_topic in t.topic]
        
        # Filter by problem family (handle aliases)
        if problem_family is not None:
            # Map old names to new
            family = FAMILY_ALIASES.get(problem_family, problem_family)
            candidates = [t for t in candidates if t.family == family]
        
        # Filter by num_steps
        if num_steps is not None:
            candidates = [t for t in candidates if t.steps == num_steps]
        
        return candidates
    
    def generate(
        self,
        complexity: Optional[int] = None,
        grade: Optional[str] = None,
        math_topic: Optional[str] = None,
        problem_family: Optional[str] = None,
        num_steps: Optional[int] = None,
        seed: Optional[int] = None
    ) -> Dict:
        """Generate a single problem.
        
        Args:
            complexity: Difficulty level (1=easy, 2=medium, 3=hard)
            grade: Grade level ('elementary', 'middle', 'high', or 'k1'-'k12')
            math_topic: Math topic filter
            problem_family: Problem family filter
            num_steps: Number of steps filter
            seed: Random seed for this problem
        
        Returns:
            Problem dictionary with standard structure
        """
        # Set seed if provided
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        elif self.seed is not None:
            random.seed(self.seed)
            Faker.seed(self.seed)
        
        # Filter templates
        candidates = self._filter_templates(
            complexity=complexity,
            grade=grade,
            math_topic=math_topic,
            problem_family=problem_family,
            num_steps=num_steps
        )
        
        if not candidates:
            raise ValueError(
                f"No templates found matching criteria: "
                f"complexity={complexity}, grade={grade}, topic={math_topic}, "
                f"family={problem_family}, steps={num_steps}"
            )
        
        # Select random template
        template = random.choice(candidates)
        
        # Get template path
        template_path = self.template_paths.get(template.id)
        
        # Generate problem from template
        return self._generate_from_template(template, seed=seed, template_path=template_path)
    
    def _generate_from_template(
        self,
        template: TemplateDefinition,
        seed: Optional[int] = None,
        template_path: Optional[Path] = None
    ) -> Dict:
        """Generate problem from a specific template."""
        # Initialize variable generator with seed
        var_gen = VariableGenerator(seed=seed)
        
        # Generate variable values
        context = var_gen.generate_context(template.variables)
        
        # Create display context with formatted values for template rendering
        display_context = {}
        for var_name, value in context.items():
            if var_name in template.variables:
                spec = template.variables[var_name]
                # Format for display (adds $, %, etc.)
                display_context[var_name] = var_gen.format_value(value, spec)
            else:
                display_context[var_name] = value
        
        # Create combined context with both raw and formatted values
        # Raw values for calculations, formatted for display
        combined_context = context.copy()
        for var_name, formatted_value in display_context.items():
            # Only override if formatting changed the value (i.e., it's a string now)
            if isinstance(formatted_value, str) and not isinstance(context[var_name], str):
                # Keep raw value, formatted will be in {var_name}_formatted
                combined_context[f"{var_name}_formatted"] = formatted_value
            else:
                combined_context[var_name] = formatted_value
        
        # Render template with Jinja2 (using combined context with both raw and formatted values)
        try:
            problem_text = self.renderer.render(template.template, combined_context)
        except Exception as e:
            raise ValueError(f"Failed to render template {template.id}: {e}")
        
        # Execute solution to compute answer (using raw numeric context)
        try:
            answer_value = execute_solution(template.solution, context)
        except Exception as e:
            raise ValueError(f"Failed to execute solution for {template.id}: {e}")
        
        # Format answer(s) based on Answer variable spec(s)
        if isinstance(answer_value, dict):
            # Multi-answer problem
            formatted_answers = []
            for i in sorted(answer_value.keys()):
                answer_spec = template.variables.get(f'Answer{i}')
                formatted = format_answer(answer_value[i], answer_spec)
                formatted_answers.append(formatted)
            expected_answer = " | ".join(formatted_answers)
        else:
            # Single answer
            answer_spec = template.variables.get('Answer')
            expected_answer = format_answer(answer_value, answer_spec)
        
        # Extract math topic (use first part before dot)
        math_topic = template.topic.split('.')[0] if '.' in template.topic else template.topic
        
        # Map family name back to old name for compatibility
        family_name = FAMILY_REVERSE_ALIASES.get(template.family, template.family)
        
        # Extract operations from solution (basic heuristic)
        operations = self._extract_operations(template.solution)
        
        # Build standard output structure
        output = {
            "test_id": f"math_{template.id}",
            "task_type": "multi_step_math",
            "config_name": f"{template.grade}_{template.difficulty}_{template.family}",
            "problem": problem_text.strip(),
            "task_params": {
                "complexity": {'easy': 1, 'medium': 2, 'hard': 3}[template.difficulty],
                "grade": f"k{template.grade}",
                "math_topic": [math_topic],
                "problem_family": family_name,
                "num_steps": template.steps,
                "expected_answer": expected_answer,
                "operations": operations,
            }
        }
        
        # Add template path if provided
        if template_path:
            try:
                rel_path = template_path.relative_to(self.templates_dir.parent.parent)
                output["template_path"] = str(rel_path)
            except ValueError:
                # Path is not relative to templates_dir, use absolute
                output["template_path"] = str(template_path)
        
        return output
    
    def _extract_operations(self, solution_code: str) -> List[str]:
        """Extract mathematical operations from solution code."""
        operations = []
        
        if '+' in solution_code:
            operations.append('addition')
        if '-' in solution_code:
            operations.append('subtraction')
        if '*' in solution_code:
            operations.append('multiplication')
        if '/' in solution_code:
            operations.append('division')
        if '**' in solution_code or 'pow(' in solution_code:
            operations.append('exponentiation')
        if '%' in solution_code:
            operations.append('modulo')
        
        return operations if operations else ['arithmetic']
    
    def get_available_options(self) -> Dict[str, List[str]]:
        """Get available filtering options."""
        families = set()
        topics = set()
        grades = set()
        
        for template in self.templates.values():
            families.add(template.family)
            # Add original family name for compatibility
            original = FAMILY_REVERSE_ALIASES.get(template.family, template.family)
            families.add(original)
            
            topics.add(template.topic.split('.')[0])
            grades.add(f"k{template.grade}")
        
        return {
            "problem_families": sorted(families),
            "math_topics": sorted(topics),
            "grades": sorted(grades),
            "complexity_levels": [1, 2, 3],
        }
