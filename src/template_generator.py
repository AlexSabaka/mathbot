"""Unified template-driven problem generator.

Replaces family-based generation with template parsing and rendering.
"""

import os
import random
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from faker import Faker
import names
import chevron

from .variable_parser import parse_variable_name, parse_template_variables
from .template_helpers import get_all_helpers
from .solution_evaluator import split_template, compute_answer
from .providers import MathProblemProvider
from .utils import round_money, generate_price, generate_quantity


class TemplateInfo:
    """Metadata about a template file."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = Path(filepath).name
        
        # Parse filename: {grade}_{complexity}_{family}_{variant}.mustache
        parts = self.filename.replace('.mustache', '').split('_', 3)
        
        if len(parts) >= 4:
            self.grade = parts[0]  # e.g., "k3"
            self.complexity = parts[1]  # e.g., "easy", "medium", "hard"
            self.family = parts[2]  # e.g., "sequential"
            self.variant = parts[3]  # e.g., "01", "grocery"
        else:
            # Fallback for old template structure
            self.grade = 'k5'
            self.complexity = 'medium'
            self.family = Path(filepath).parent.name
            self.variant = '01'
        
        # Map complexity words to numbers
        complexity_map = {'easy': 1, 'medium': 2, 'hard': 3}
        self.complexity_num = complexity_map.get(self.complexity, 2)
        
        # Extract math topic from parent directory
        parent_dir = Path(filepath).parent.name
        self.math_topic = parent_dir if parent_dir != 'templates' else 'arithmetic'
    
    def __repr__(self):
        return f"TemplateInfo({self.grade}, {self.complexity}, {self.family}, {self.variant})"


class TemplateGenerator:
    """Generate math problems from Mustache templates with embedded metadata."""
    
    # Map general grade levels to specific K-levels
    GRADE_MAP = {
        'elementary': ['k1', 'k2', 'k3', 'k4', 'k5'],
        'middle': ['k6', 'k7', 'k8'],
        'high': ['k9', 'k10', 'k11', 'k12'],
        'college': ['k12'],  # Reuse advanced templates
        'university': ['k12'],
    }
    
    # Map old family names to new family names for backward compatibility
    FAMILY_ALIASES = {
        'sequential_purchase': 'shopping',
        'rate_time': 'travel',
        'compound_growth': 'growth',
        'multi_person_sharing': 'sharing',
        'area_perimeter_chain': 'geometry',
    }
    
    # Reverse mapping for output
    FAMILY_REVERSE_ALIASES = {
        'shopping': 'sequential_purchase',
        'travel': 'rate_time',
        'growth': 'compound_growth',
        'sharing': 'multi_person_sharing',
        'geometry': 'area_perimeter_chain',
        'sequential': 'sequential_purchase',  # Also map our new hand-crafted ones
    }
    
    def __init__(self, templates_dir: str = None, seed: int = None):
        """Initialize template generator.
        
        Args:
            templates_dir: Path to templates directory (default: src/templates)
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        self.seed = seed
        self.fake = Faker()
        self.fake.add_provider(MathProblemProvider)
        
        # Set templates directory
        if templates_dir is None:
            src_dir = Path(__file__).parent
            templates_dir = src_dir / 'templates'
        self.templates_dir = Path(templates_dir)
        
        # Discover all templates
        self.templates = self._discover_templates()
    
    def _discover_templates(self) -> List[TemplateInfo]:
        """Scan templates directory and load all .mustache files.
        
        Returns:
            List of TemplateInfo objects
        """
        templates = []
        
        if not self.templates_dir.exists():
            return templates
        
        # Recursively find all .mustache files
        for mustache_file in self.templates_dir.rglob('*.mustache'):
            templates.append(TemplateInfo(str(mustache_file)))
        
        return templates
    
    def _generate_value(self, var_metadata):
        """Generate a value based on variable metadata.
        
        Args:
            var_metadata: VariableMetadata object
        
        Returns:
            Generated value
        """
        var_type = var_metadata.var_type
        constraints = var_metadata.constraints
        
        # Handle different types
        if var_type == 'integer':
            min_val = constraints.get('min', 1)
            max_val = constraints.get('max', 100)
            return random.randint(min_val, max_val)
        
        elif var_type in ['decimal', 'decimal_money', 'money']:
            min_val = constraints.get('min', 1.0)
            max_val = constraints.get('max', 100.0)
            step = constraints.get('step', 0.25)
            
            num_steps = int((max_val - min_val) / step)
            value = min_val + (random.randint(0, num_steps) * step)
            
            if 'money' in var_type:
                return round_money(value)
            return round(value, 2)
        
        elif var_type == 'person' or var_type == 'name':
            return names.get_first_name()
        
        elif var_type == 'location' or var_type == 'city':
            return self.fake.city()
        
        elif var_type == 'store':
            return self.fake.store_name()
        
        elif var_type == 'restaurant':
            return self.fake.restaurant_name()
        
        elif var_type == 'company':
            return self.fake.company()
        
        elif var_type == 'weekday':
            return self.fake.weekday()
        
        elif var_type == 'season':
            return self.fake.season()
        
        elif var_type == 'time':
            return self.fake.time_of_day()
        
        elif var_type == 'item':
            subtype = constraints.get('subtype', 'grocery')
            count = constraints.get('count', 1)
            
            if subtype == 'grocery':
                items = self.fake.grocery_items(count=count)
            elif subtype == 'online':
                items = self.fake.online_items(count=count)
            elif subtype == 'electronics':
                items = self.fake.electronics_items(count=count)
            elif subtype == 'clothing':
                items = self.fake.clothing_items(count=count)
            elif subtype == 'book':
                items = self.fake.book_items(count=count)
            else:
                items = self.fake.grocery_items(count=count)
            
            # Return first item's plural name
            if items:
                return items[0][0]  # plural name
            return 'items'
        
        elif var_type == 'fraction':
            frac = self.fake.fraction()
            return f"{frac[0]}/{frac[1]}"
        
        elif var_type == 'percentage':
            min_val = constraints.get('min', 5)
            max_val = constraints.get('max', 50)
            step = constraints.get('step', 5)
            
            num_steps = (max_val - min_val) // step
            return min_val + (random.randint(0, num_steps) * step)
        
        elif var_type == 'choices':
            choices = constraints.get('choices', [])
            return random.choice(choices) if choices else ''
        
        elif var_type == 'simple':
            # Old template format - infer from variable name
            name = var_metadata.name
            
            # Common patterns in old templates
            if name in ['name', 'name1', 'name2', 'person1', 'person2']:
                return names.get_first_name()
            elif name in ['city', 'location', 'destination']:
                return self.fake.city()
            elif name == 'company':
                return self.fake.company()
            elif name == 'store':
                return self.fake.store_name()
            elif name == 'restaurant':
                return self.fake.restaurant_name()
            elif 'price' in name or 'cost' in name:
                return round_money(random.uniform(5, 50))
            elif 'quantity' in name or 'count' in name:
                return random.randint(1, 10)
            elif 'rate' in name or 'percentage' in name or 'discount' in name:
                return random.randint(5, 25)
            elif 'year' in name:
                return random.randint(1, 10)
            elif name == 'principal':
                return round_money(random.uniform(500, 5000))
            elif 'item' in name:
                items = self.fake.grocery_items(count=1)
                return items[0][0] if items else 'items'
            else:
                # Return placeholder
                return f"[{name}]"
        
        else:
            # Unknown type, return placeholder
            return f"[{var_metadata.name}]"
    
    def generate(self, grade: str = None, complexity: int = None, 
                 math_topic: str = None, problem_family: str = None) -> Dict:
        """Generate a problem from a random matching template.
        
        Args:
            grade: Grade level (e.g., 'k3', 'k5', 'elementary', 'middle', 'high')
            complexity: 1 (easy), 2 (medium), 3 (hard)
            math_topic: Math topic (e.g., 'arithmetic', 'geometry')
            problem_family: Problem family (e.g., 'sequential_purchase')
        
        Returns:
            Problem dictionary with structure matching original system
        """
        # Map old family names to new ones
        if problem_family and problem_family in self.FAMILY_ALIASES:
            problem_family = self.FAMILY_ALIASES[problem_family]
        
        # Map general grade to K-grades if needed
        k_grades = None
        if grade and grade in self.GRADE_MAP:
            k_grades = self.GRADE_MAP[grade]
        elif grade:
            k_grades = [grade]  # Already a K-grade
        
        # Filter templates based on criteria
        matching_templates = self.templates
        
        if k_grades:
            matching_templates = [t for t in matching_templates if t.grade in k_grades]
        
        if complexity:
            matching_templates = [t for t in matching_templates if t.complexity_num == complexity]
        
        if math_topic:
            matching_templates = [t for t in matching_templates if t.math_topic == math_topic]
        
        if problem_family:
            matching_templates = [t for t in matching_templates if t.family == problem_family]
        
        # If no exact match, try relaxing constraints progressively
        if not matching_templates:
            # Try without complexity constraint
            matching_templates = self.templates
            if k_grades:
                matching_templates = [t for t in matching_templates if t.grade in k_grades]
            if math_topic:
                matching_templates = [t for t in matching_templates if t.math_topic == math_topic]
            if problem_family:
                matching_templates = [t for t in matching_templates if t.family == problem_family]
        
        if not matching_templates:
            # Try without topic constraint
            matching_templates = self.templates
            if k_grades:
                matching_templates = [t for t in matching_templates if t.grade in k_grades]
            if problem_family:
                matching_templates = [t for t in matching_templates if t.family == problem_family]
        
        if not matching_templates:
            # Try without grade constraint
            matching_templates = self.templates
            if problem_family:
                matching_templates = [t for t in matching_templates if t.family == problem_family]
        
        if not matching_templates:
            # Last resort: use any template
            matching_templates = self.templates
        
        if not matching_templates:
            raise ValueError(f"No templates available in templates directory")
        
        # Pick random template
        template_info = random.choice(matching_templates)
        
        # Load template content
        with open(template_info.filepath, 'r') as f:
            template_content = f.read()
        
        # Split into problem and solution
        problem_template, solution_section = split_template(template_content)
        
        # Parse variables from template
        variables = parse_template_variables(problem_template)
        
        # Generate values for all variables
        # Use full name for Chevron rendering, short name for solution evaluation
        chevron_context = {}
        short_context = {}
        
        for var_meta in variables:
            value = self._generate_value(var_meta)
            chevron_context[var_meta.full_name] = value  # Full name for template
            short_context[var_meta.short_name] = value   # Short name for solution
        
        # Add template helpers
        helpers = get_all_helpers(seed=self.seed)
        chevron_context.update(helpers)
        
        # Render problem text using full variable names
        problem_text = chevron.render(problem_template, chevron_context)
        
        # Compute answer from solution section using short names
        try:
            answer = compute_answer(template_content, short_context)
        except Exception as e:
            # Fallback if solution computation fails
            answer = "[Answer computation failed]"
        
        # Determine operations and steps from solution section
        operations = self._extract_operations(solution_section)
        num_steps = len(operations) if operations else 1
        
        # Map internal family name back to old name for backward compatibility
        output_family = self.FAMILY_REVERSE_ALIASES.get(template_info.family, template_info.family)
        
        # Build result matching original structure
        return {
            "problem": problem_text.strip(),
            "expected_answer": answer,
            "operations": operations,
            "num_steps": num_steps,
            "template": template_info.filename,
            "grade": template_info.grade,
            "complexity": template_info.complexity_num,
            "math_topic": template_info.math_topic,
            "problem_family": output_family,
        }
    
    def _extract_operations(self, solution_section: str) -> List[str]:
        """Extract operation types from solution expressions.
        
        Args:
            solution_section: Solution section content
        
        Returns:
            List of operation strings
        """
        operations = []
        
        if not solution_section:
            return operations
        
        # Look for common operation patterns
        if '*' in solution_section or '×' in solution_section:
            operations.append('multiply')
        if '+' in solution_section:
            operations.append('add')
        if '-' in solution_section:
            operations.append('subtract')
        if '/' in solution_section or '÷' in solution_section:
            operations.append('divide')
        if '^' in solution_section or '**' in solution_section:
            operations.append('power')
        if '%' in solution_section or 'percentage' in solution_section.lower():
            operations.append('percentage')
        
        return operations if operations else ['compute']
