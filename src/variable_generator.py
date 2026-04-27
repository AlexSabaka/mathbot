"""Variable value generator for YAML template system."""

import random
import names
from decimal import Decimal
from faker import Faker
from typing import Any, Dict, Optional
from .providers import MathProblemProvider
from .yaml_loader import VariableSpec
from .utils import generate_price, generate_percentage


class VariableGenerator:
    """Generates values for YAML template variables."""

    def __init__(self, seed: Optional[int] = None, locale: str = 'en_US'):
        """Initialize generator.

        Args:
            seed: Random seed for reproducibility.
            locale: Faker locale (e.g., 'en_US', 'es_ES', 'de_DE'). Controls
                the distribution of names, cities, and company names. The
                `names` library used for first-name generation is en-only;
                non-en locales fall back to it until per-locale name pools
                land. Pass either underscore form ('en_US') or BCP-47 hyphen
                form ('en-US') — both are accepted.
        """
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)

        self.locale = locale.replace('-', '_') if locale else 'en_US'
        self.fake = Faker(self.locale)
        self.fake.add_provider(MathProblemProvider)
    
    def generate_context(
        self,
        variables: Dict[str, VariableSpec],
        difficulty: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate values for all variables.

        Args:
            variables: Dictionary of variable specifications.
            difficulty: When set, variables that declare per-tier `ranges:`
                use the matching entry's min/max/step/choices instead of the
                flat fields. Variables without `ranges:` are unaffected.

        Returns:
            Dictionary of variable names to generated values
        """
        context = {}

        for var_name, spec in variables.items():
            # Skip Answer variables - they're set by solution (Answer, Answer1, Answer2, etc.)
            if var_name == 'Answer' or (var_name.startswith('Answer') and var_name[6:].isdigit()):
                continue

            value = self._generate_value(spec, difficulty=difficulty)
            context[var_name] = value

        return context

    def _generate_value(
        self,
        spec: VariableSpec,
        difficulty: Optional[str] = None,
    ) -> Any:
        """Generate a single value based on variable specification."""
        var_type = spec.type

        # Numeric integer types
        if var_type in ('integer', 'ordinal'):
            return self._generate_integer(spec, difficulty=difficulty)

        elif var_type in (
            'decimal', 'volume', 'area', 'length', 'weight', 'temperature',
            'speed', 'acceleration', 'money', 'price', 'percentage',
            'density', 'energy', 'power', 'pressure', 'force',
        ):
            return self._generate_decimal(spec, difficulty=difficulty)

        elif var_type == 'fraction':
            return self._generate_fraction(spec, difficulty=difficulty)
        
        # Name/location types
        elif var_type in ('person', 'name'):
            return names.get_first_name()
        
        elif var_type in ('location', 'city'):
            return self.fake.city()
        
        elif var_type == 'store':
            return self.fake.store_name()
        
        elif var_type == 'restaurant':
            return self.fake.restaurant_name()
        
        elif var_type == 'company':
            return self.fake.company()
        
        # Time/context types
        elif var_type == 'weekday':
            return random.choice(MathProblemProvider.WEEKDAYS)
        
        elif var_type == 'month':
            return random.choice(MathProblemProvider.MONTHS)
        
        elif var_type == 'season':
            return random.choice(MathProblemProvider.SEASONS)
        
        elif var_type == 'time':
            return self._generate_time(spec, difficulty=difficulty)
        
        # Item type
        elif var_type == 'item':
            return self._generate_item(spec)
        
        # Boolean
        elif var_type == 'boolean':
            probability = spec.probability if spec.probability is not None else 0.5
            return random.random() < probability
        
        # String with choices (and 'choice' alias)
        elif var_type in ('string', 'choice'):
            r = self._resolve_range(spec, difficulty)
            if r['choices']:
                return random.choice(r['choices'])
            else:
                raise ValueError(f"'{var_type}' variable requires 'choices' list")

        else:
            raise ValueError(f"Unknown variable type: {var_type}")
    
    @staticmethod
    def _resolve_range(spec: VariableSpec, difficulty: Optional[str]) -> Dict[str, Any]:
        """Return effective min/max/step/choices for the given difficulty.

        If `spec.ranges` is set and contains `difficulty`, that tier's entries
        override the flat fields. Otherwise the flat fields apply unchanged.
        Always returns a dict with keys min/max/step/choices (any can be None).
        """
        base = {
            'min': spec.min,
            'max': spec.max,
            'step': spec.step,
            'choices': spec.choices,
        }
        if spec.ranges and difficulty and difficulty in spec.ranges:
            tier = spec.ranges[difficulty]
            for key in ('min', 'max', 'step', 'choices'):
                if key in tier:
                    base[key] = tier[key]
        return base

    def _generate_integer(
        self,
        spec: VariableSpec,
        difficulty: Optional[str] = None,
    ) -> int:
        """Generate an integer value."""
        r = self._resolve_range(spec, difficulty)
        if r['choices']:
            return int(random.choice(r['choices']))

        min_val = int(r['min']) if r['min'] is not None else 1
        max_val = int(r['max']) if r['max'] is not None else 10
        step = int(r['step']) if r['step'] is not None else 1

        # Generate values in steps
        values = list(range(min_val, max_val + 1, step))
        return random.choice(values)

    def _generate_decimal(
        self,
        spec: VariableSpec,
        difficulty: Optional[str] = None,
    ) -> float:
        """Generate a decimal value."""
        r = self._resolve_range(spec, difficulty)

        # Choice list takes priority for decimal types when supplied — used
        # by multi-tier templates that need a small enumerated set of
        # divisors / multipliers per tier rather than a continuous range.
        if r['choices']:
            return float(random.choice(r['choices']))

        min_val = float(r['min']) if r['min'] is not None else 1.0
        max_val = float(r['max']) if r['max'] is not None else 10.0
        step = float(r['step']) if r['step'] is not None else 0.01

        # Use generate_price for money/price types
        if spec.type in ('money', 'price'):
            return generate_price(min_val, max_val, step)

        # Use generate_percentage for percentage type
        elif spec.type == 'percentage':
            return generate_percentage(int(min_val), int(max_val), int(step))

        # General decimal
        else:
            num_steps = int((max_val - min_val) / step) + 1
            step_index = random.randint(0, num_steps - 1)
            return round(min_val + (step_index * step), 2)

    def _generate_fraction(
        self,
        spec: VariableSpec,
        difficulty: Optional[str] = None,
    ) -> str:
        """Generate a fraction like '3/4'."""
        r = self._resolve_range(spec, difficulty)
        min_val = int(r['min']) if r['min'] is not None else 1
        max_val = int(r['max']) if r['max'] is not None else 8

        numerator = random.randint(min_val, max_val)
        denominator = random.randint(numerator + 1, max_val + 2)

        return f"{numerator}/{denominator}"

    def _generate_time(
        self,
        spec: VariableSpec,
        difficulty: Optional[str] = None,
    ) -> float:
        """Generate a time duration in hours."""
        r = self._resolve_range(spec, difficulty)
        min_val = float(r['min']) if r['min'] is not None else 0.25
        max_val = float(r['max']) if r['max'] is not None else 8.0
        step = float(r['step']) if r['step'] is not None else 0.25

        num_steps = int((max_val - min_val) / step) + 1
        step_index = random.randint(0, num_steps - 1)
        return min_val + (step_index * step)
    
    def _generate_item(self, spec: VariableSpec) -> str:
        """Generate an item name based on category."""
        category = spec.category or 'grocery'
        singular = spec.singular or False
        
        # Get items from provider - access via MathProblemProvider class
        if category == 'grocery':
            items = MathProblemProvider.GROCERY_ITEMS
        elif category == 'electronics':
            items = MathProblemProvider.ELECTRONICS_ITEMS
        elif category == 'clothing':
            items = MathProblemProvider.CLOTHING_ITEMS
        elif category == 'book':
            items = MathProblemProvider.BOOK_ITEMS
        elif category == 'online':
            items = MathProblemProvider.ONLINE_ITEMS
        elif category == 'school':
            items = MathProblemProvider.SCHOOL_ITEMS
        elif category == 'furniture':
            items = MathProblemProvider.FURNITURE_ITEMS
        elif category == 'other':
            items = MathProblemProvider.OTHER_ITEMS
        else:
            items = MathProblemProvider.GROCERY_ITEMS  # Default
        
        # Pick random item
        item = random.choice(items)
        plural_name, singular_name, min_price, max_price = item
        
        return singular_name if singular else plural_name
    
    def format_value(
        self,
        value: Any,
        spec: VariableSpec,
        template_unit_system: Optional[str] = None,
    ) -> Any:
        """Format a value for display in the rendered problem text.

        Variables of `length`, `weight`, `temperature`, `money` types get
        a system-aware unit suffix (or currency prefix) appended. `area`,
        `volume`, `speed`, `percentage` return raw numbers — templates
        write the unit text themselves around `{{var}}`.

        `template_unit_system` is the metadata default; the spec's own
        `unit_system` overrides it per-variable. `mixed_us` (default)
        reproduces the pre-Phase-5.3 byte-identical output.
        """
        from .units import (
            resolve_system, get_short_suffix, is_compact, get_currency_symbol,
            format_explicit_unit_value,
        )

        system = resolve_system(spec.unit_system, template_unit_system)

        # Free-form `unit:` (Stage 3) wins over the (type, system)-table
        # lookup — author has declared the exact unit they want printed.
        if spec.unit:
            return format_explicit_unit_value(value, spec.unit)

        if spec.type in ('money', 'price'):
            return f"{get_currency_symbol(system)}{value:.2f}"

        elif spec.type == 'percentage':
            return str(int(value))  # Don't add %, template will have {{var}}%

        elif spec.type == 'ordinal':
            from .i18n import get_language_spec
            return get_language_spec('en').ordinal(int(value))

        elif spec.type in ('length', 'weight'):
            suffix = get_short_suffix(spec.type, system)
            if isinstance(value, (int, float)):
                if value == int(value):
                    return f"{int(value)}{suffix}"
                return f"{float(value):.2f}{suffix}"
            return str(value)

        elif spec.type == 'temperature':
            if isinstance(value, (int, float)):
                suffix = get_short_suffix('temperature', system)
                sep = '' if is_compact('temperature', system) else ' '
                return f"{float(value):.1f}{sep}{suffix}"
            return str(value)

        elif spec.type in ('area', 'volume'):
            # Area/volume display the bare number in problem text;
            # templates add their own unit phrasing (e.g. "{{area}} square units").
            if isinstance(value, (int, float)):
                if value == int(value):
                    return int(value)
                return float(value)
            return value

        elif spec.type in ('density', 'energy', 'power', 'pressure', 'force', 'acceleration'):
            # Compound physics types render with a space between value and
            # suffix ("750 kg/m³"), unlike length/weight which are compact
            # ("5kg"). Int-or-2-decimal precision matches the existing
            # length/area/volume convention.
            suffix = get_short_suffix(spec.type, system)
            if isinstance(value, (int, float)):
                if value == int(value):
                    return f"{int(value)} {suffix}"
                return f"{float(value):.2f} {suffix}"
            return str(value)

        elif spec.type == 'time':
            # Format time as hours/minutes (locale-agnostic for now)
            hours = int(value)
            minutes = int((value - hours) * 60)

            if hours > 0 and minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minutes"
            elif hours > 0:
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return f"{minutes} minutes"

        else:
            # For values without specific formatting, return raw value
            # so it remains usable in Jinja2 logic / `{% set %}`.
            return value
