"""YAML template loader and validator for mathbot v2.0."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml

from .units import VALID_UNIT_SYSTEMS, DEFAULT_UNIT_SYSTEM


@dataclass
class VariableSpec:
    """Specification for a single variable."""
    name: str
    type: str
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    category: Optional[str] = None
    singular: Optional[bool] = None
    probability: Optional[float] = None
    choices: Optional[List[str]] = None
    # Per-variable override of the template's unit system. None means
    # "inherit from metadata.unit_system". See `src.units`.
    unit_system: Optional[str] = None


@dataclass
class TestCase:
    """Test case for template validation."""
    seed: int
    expected: Dict[str, Any]
    notes: Optional[str] = None


@dataclass
class TemplateDefinition:
    """Complete YAML template definition."""
    # Metadata
    id: str
    version: str
    author: str
    created: str
    grade: int
    topic: str
    family: str
    difficulty: str
    steps: int
    # `language` is the BCP-47 language tag used for locale-aware filters
    # (plural, ordinal, number-to-words) and translated entity pools.
    # `culture` is a regional hint (BCP-47 region tag) used to drive Faker
    # locale (cities/companies). It does not drive language behavior.
    language: str = "en"
    culture: str = "en-US"
    # Display-time unit system: "metric" | "imperial" | "mixed_us" (default).
    # Solutions still compute in system-native units; this only controls
    # what the formatter prints. Per-variable override available on
    # VariableSpec. See `src.units`.
    unit_system: str = "mixed_us"
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    # Core sections
    variables: Dict[str, VariableSpec] = field(default_factory=dict)
    template: str = ""
    solution: str = ""
    tests: List[TestCase] = field(default_factory=list)
    
    # Source file path
    file_path: Optional[Path] = None

class YAMLLoader:
    """Loads and validates YAML template files."""
    
    REQUIRED_METADATA = {
        'id', 'version', 'author', 'created', 'grade', 
        'topic', 'family', 'difficulty', 'steps'
    }
    
    # Active types: every entry here has a generation branch in
    # VariableGenerator._generate_value and at least one corresponding
    # format rule in format_value / format_answer.
    VALID_TYPES = {
        # numeric integer types
        'integer', 'ordinal',
        # fractions
        'fraction',
        # numeric decimal types
        'decimal', 'volume', 'area', 'length', 'weight', 'temperature',
        'speed', 'acceleration', 'money', 'price', 'percentage',
        # entity types
        'person', 'name', 'location', 'city',
        'store', 'restaurant', 'company', 'item',
        # date/time types
        'weekday', 'month', 'season', 'time', 'duration',
        # other types
        'boolean', 'string', 'choice',
    }
    
    VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}
    
    VALID_ITEM_CATEGORIES = {
        'grocery', 'electronics', 'clothing', 'book', 'online',
        'school', 'furniture', 'other'
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_template(self, file_path: Path) -> Optional[TemplateDefinition]:
        """Load and validate a YAML template file."""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse YAML: {e}")
            return None
        
        if not isinstance(data, dict):
            self.errors.append("YAML root must be a dictionary")
            return None
        
        # Validate structure
        if not self._validate_structure(data):
            return None
        
        # Parse metadata
        metadata = data.get('metadata', {})
        
        # Parse variables
        variables = {}
        for var_name, var_spec in data.get('variables', {}).items():
            variables[var_name] = self._parse_variable(var_name, var_spec)
        
        # Parse tests
        tests = []
        for test_data in data.get('tests', []):
            tests.append(TestCase(
                seed=test_data['seed'],
                expected=test_data['expected'],
                notes=test_data.get('notes')
            ))
        
        # Create template definition
        template_def = TemplateDefinition(
            id=metadata['id'],
            version=metadata['version'],
            author=metadata['author'],
            created=metadata['created'],
            grade=metadata['grade'],
            topic=metadata['topic'],
            family=metadata['family'],
            difficulty=metadata['difficulty'],
            steps=metadata['steps'],
            language=metadata.get('language', 'en'),
            culture=metadata.get('culture', 'en-US'),
            unit_system=metadata.get('unit_system', DEFAULT_UNIT_SYSTEM),
            tags=metadata.get('tags', []),
            notes=metadata.get('notes'),
            variables=variables,
            template=data.get('template', ''),
            solution=data.get('solution', ''),
            tests=tests,
            file_path=file_path
        )
        
        # Validate template
        self._validate_template(template_def)
        
        return template_def if not self.errors else None
    
    def _validate_structure(self, data: Dict) -> bool:
        """Validate overall YAML structure."""
        # Check required sections
        if 'metadata' not in data:
            self.errors.append("Missing required section: metadata")
            return False
        
        if 'variables' not in data:
            self.errors.append("Missing required section: variables")
            return False
        
        if 'template' not in data:
            self.errors.append("Missing required section: template")
            return False
        
        if 'solution' not in data:
            self.errors.append("Missing required section: solution")
            return False
        
        # Check metadata fields
        metadata = data['metadata']
        missing_fields = self.REQUIRED_METADATA - set(metadata.keys())
        if missing_fields:
            self.errors.append(f"Missing required metadata fields: {missing_fields}")
            return False
        
        # Validate difficulty
        if metadata['difficulty'] not in self.VALID_DIFFICULTIES:
            self.errors.append(
                f"Invalid difficulty '{metadata['difficulty']}'. "
                f"Must be one of: {self.VALID_DIFFICULTIES}"
            )

        # Validate unit_system if present (None/missing → DEFAULT_UNIT_SYSTEM)
        meta_us = metadata.get('unit_system')
        if meta_us is not None and meta_us not in VALID_UNIT_SYSTEMS:
            self.errors.append(
                f"Invalid metadata.unit_system '{meta_us}'. "
                f"Must be one of: {sorted(VALID_UNIT_SYSTEMS)}"
            )
        
        # Check for Answer variable (or Answer1, Answer2, etc.)
        variables = data.get('variables', {})
        has_answer = 'Answer' in variables
        has_numbered_answers = any(key.startswith('Answer') and key[6:].isdigit() for key in variables)
        
        if not has_answer and not has_numbered_answers:
            self.errors.append(
                "Missing required answer variable: must have 'Answer' or 'Answer1', 'Answer2', etc."
            )
        
        # Warn about missing tests
        if 'tests' not in data or not data['tests']:
            self.warnings.append(
                "No tests defined. Recommended: 2-3 test cases for validation."
            )
        
        return not self.errors
    
    def _parse_variable(self, name: str, spec: Dict) -> VariableSpec:
        """Parse a variable specification."""
        var_type = spec.get('type')
        
        if var_type not in self.VALID_TYPES:
            self.errors.append(
                f"Invalid type '{var_type}' for variable '{name}'. "
                f"Must be one of: {self.VALID_TYPES}"
            )
        
        # Validate item category
        if var_type == 'item':
            category = spec.get('category')
            if category and category not in self.VALID_ITEM_CATEGORIES:
                self.errors.append(
                    f"Invalid item category '{category}' for variable '{name}'. "
                    f"Must be one of: {self.VALID_ITEM_CATEGORIES}"
                )
        
        # Validate constraints
        min_val = spec.get('min')
        max_val = spec.get('max')
        step = spec.get('step')
        
        if min_val is not None and max_val is not None:
            if min_val > max_val:
                self.errors.append(
                    f"Variable '{name}': min ({min_val}) must not exceed max ({max_val})"
                )
            
            if step is not None:
                range_val = max_val - min_val
                if range_val % step > 0.0001:  # Floating-point tolerance
                    self.warnings.append(
                        f"Variable '{name}': step ({step}) does not evenly divide "
                        f"range ({range_val}). May cause uneven distribution."
                    )
        
        # Validate per-variable unit_system override (if present)
        var_unit_system = spec.get('unit_system')
        if var_unit_system is not None and var_unit_system not in VALID_UNIT_SYSTEMS:
            self.errors.append(
                f"Variable '{name}': invalid unit_system '{var_unit_system}'. "
                f"Must be one of: {sorted(VALID_UNIT_SYSTEMS)}"
            )

        return VariableSpec(
            name=name,
            type=var_type,
            min=min_val,
            max=max_val,
            step=step,
            category=spec.get('category'),
            singular=spec.get('singular'),
            probability=spec.get('probability'),
            choices=spec.get('choices'),
            unit_system=var_unit_system,
        )
    
    def _validate_template(self, template_def: TemplateDefinition) -> None:
        """Validate template content and solution."""
        # Check solution sets Answer
        if 'Answer' not in template_def.solution:
            self.errors.append(
                "Solution must set the Answer variable"
            )

        # Validate solution is valid Python
        try:
            compile(template_def.solution, '<solution>', 'exec')
        except SyntaxError as e:
            self.errors.append(f"Solution has syntax error: {e}")

        # Enforce topic ↔ directory invariant: a template under
        # src/templates/<X>/ must declare topic: X.<subtopic>.
        if template_def.file_path is not None:
            parent_dir = template_def.file_path.parent.name
            top_topic = template_def.topic.split('.')[0]
            if top_topic != parent_dir:
                self.errors.append(
                    f"Topic '{template_def.topic}' does not match parent "
                    f"directory '{parent_dir}'. Top-level topic must equal "
                    f"the directory name (or move the file)."
                )
    
    def get_validation_results(self) -> Tuple[List[str], List[str]]:
        """Get validation errors and warnings."""
        return self.errors, self.warnings


def discover_yaml_templates(base_path: Path) -> List[Path]:
    """Discover all YAML template files recursively."""
    return sorted(base_path.rglob("*.yaml"))


def load_all_templates(base_path: Path) -> Dict[str, TemplateDefinition]:
    """Load all YAML templates from a directory."""
    loader = YAMLLoader()
    templates = {}
    
    for file_path in discover_yaml_templates(base_path):
        template = loader.load_template(file_path)
        if template:
            templates[template.id] = template
        else:
            print(f"Failed to load {file_path}:", file=sys.stderr)
            for error in loader.errors:
                print(f"  ERROR: {error}", file=sys.stderr)
            for warning in loader.warnings:
                print(f"  WARNING: {warning}", file=sys.stderr)
    
    return templates
