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
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        self.fake = Faker()
        self.fake.add_provider(MathProblemProvider)
    
    def generate_context(self, variables: Dict[str, VariableSpec]) -> Dict[str, Any]:
        """Generate values for all variables.
        
        Args:
            variables: Dictionary of variable specifications
        
        Returns:
            Dictionary of variable names to generated values
        """
        context = {}
        
        for var_name, spec in variables.items():
            # Skip Answer variable - it's set by solution
            if var_name == 'Answer':
                continue
            
            value = self._generate_value(spec)
            context[var_name] = value
        
        return context
    
    def _generate_value(self, spec: VariableSpec) -> Any:
        """Generate a single value based on variable specification."""
        var_type = spec.type
        
        # Numeric types
        if var_type == 'integer':
            return self._generate_integer(spec)
        
        elif var_type == 'decimal':
            return self._generate_decimal(spec)
        
        elif var_type == 'fraction':
            return self._generate_fraction(spec)
        
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
        
        elif var_type == 'season':
            return random.choice(MathProblemProvider.SEASONS)
        
        elif var_type == 'time':
            return self._generate_time(spec)
        
        # Item type
        elif var_type == 'item':
            return self._generate_item(spec)
        
        # Boolean
        elif var_type == 'boolean':
            probability = spec.probability if spec.probability is not None else 0.5
            return random.random() < probability
        
        # String with choices
        elif var_type == 'string':
            if spec.choices:
                return random.choice(spec.choices)
            else:
                raise ValueError(f"String variable requires 'choices' list")
        
        else:
            raise ValueError(f"Unknown variable type: {var_type}")
    
    def _generate_integer(self, spec: VariableSpec) -> int:
        """Generate an integer value."""
        min_val = int(spec.min) if spec.min is not None else 1
        max_val = int(spec.max) if spec.max is not None else 10
        step = int(spec.step) if spec.step is not None else 1
        
        # Generate values in steps
        values = list(range(min_val, max_val + 1, step))
        return random.choice(values)
    
    def _generate_decimal(self, spec: VariableSpec) -> float:
        """Generate a decimal value."""
        min_val = float(spec.min) if spec.min is not None else 1.0
        max_val = float(spec.max) if spec.max is not None else 10.0
        step = float(spec.step) if spec.step is not None else 0.01
        
        # Use generate_price for money format
        if spec.format == 'money':
            return generate_price(min_val, max_val, step)
        
        # Use generate_percentage for percentage format
        elif spec.format == 'percentage':
            return generate_percentage(int(min_val), int(max_val), int(step))
        
        # General decimal
        else:
            num_steps = int((max_val - min_val) / step) + 1
            step_index = random.randint(0, num_steps - 1)
            return round(min_val + (step_index * step), 2)
    
    def _generate_fraction(self, spec: VariableSpec) -> str:
        """Generate a fraction like '3/4'."""
        min_val = int(spec.min) if spec.min is not None else 1
        max_val = int(spec.max) if spec.max is not None else 8
        
        numerator = random.randint(min_val, max_val)
        denominator = random.randint(numerator + 1, max_val + 2)
        
        return f"{numerator}/{denominator}"
    
    def _generate_time(self, spec: VariableSpec) -> float:
        """Generate a time duration in hours."""
        min_val = float(spec.min) if spec.min is not None else 0.25
        max_val = float(spec.max) if spec.max is not None else 8.0
        step = float(spec.step) if spec.step is not None else 0.25
        
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
        else:
            items = MathProblemProvider.GROCERY_ITEMS  # Default
        
        # Pick random item
        item = random.choice(items)
        plural_name, singular_name, min_price, max_price = item
        
        return singular_name if singular else plural_name
    
    def format_value(self, value: Any, spec: VariableSpec) -> str:
        """Format a value according to its specification.
        
        Used for displaying values in the rendered problem text.
        NOTE: For percentages, returns just the number (not with %)
        since templates typically write {{var}}% themselves.
        """
        if spec.format == 'money':
            return f"${value:.2f}"
        
        elif spec.format == 'percentage':
            return str(int(value))  # Don't add %, template will have {{var}}%
        
        elif spec.format == 'ordinal':
            from .jinja_renderer import ordinal_filter
            return ordinal_filter(int(value))
        
        elif spec.format == 'length':
            # Length values with units (meters for input, miles for Answer)
            if isinstance(value, (int, float)):
                if value == int(value):
                    return f"{int(value)}m"
                return f"{float(value):.2f}m"
            return str(value)
        
        elif spec.format == 'weight':
            # Weight values with units
            if isinstance(value, (int, float)):
                if value == int(value):
                    return f"{int(value)}kg"
                return f"{float(value):.2f}kg"
            return str(value)
        
        elif spec.format == 'temperature':
            # Temperature values with units
            if isinstance(value, (int, float)):
                return f"{float(value):.1f}°F"
            return str(value)
        
        elif spec.format == 'area':
            # Area values (display without units in template, units added in Answer)
            if isinstance(value, (int, float)):
                if value == int(value):
                    return int(value)
                return float(value)
            return value
        
        elif spec.format == 'volume':
            # Volume values (display without units in template, units added in Answer)
            if isinstance(value, (int, float)):
                if value == int(value):
                    return int(value)
                return float(value)
            return value
        
        elif spec.type == 'time':
            # Format time as hours/minutes
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
            # This allows them to be used in Jinja2 logic
            return value
