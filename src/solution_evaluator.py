"""Parse and evaluate solution expressions from YAML template files.

Solution is pure Python code executed in a safe namespace.
The solution must set an 'Answer' variable OR 'Answer1', 'Answer2', etc. for multi-answer problems.
"""

from typing import Dict, Any, Optional, Union
from decimal import Decimal
import math
import inflect
from .yaml_loader import VariableSpec

# Create inflect engine for number-to-words conversion
_inflect_engine = inflect.engine()


def _number_to_words(n: int) -> str:
    """Convert number to words (American English style, no 'and')."""
    return _inflect_engine.number_to_words(n, andword='')


def execute_solution(solution_code: str, context: Dict[str, Any]) -> Union[Any, Dict[str, Any]]:
    """Execute solution Python code and extract Answer(s).
    
    Args:
        solution_code: Python code from YAML solution section
        context: Dictionary of generated variable values
    
    Returns:
        Single answer value OR dict of {1: answer1, 2: answer2, ...} for multi-answer
    """
    if not solution_code:
        raise ValueError("Template has no solution code")
    
    # Create a working context (copy to avoid modifying original)
    working_context = context.copy()
    
    # Convert money strings to floats for computation
    for var_name, value in list(working_context.items()):
        if isinstance(value, str) and value.startswith('$'):
            working_context[var_name] = float(value[1:])
    
    # Create safe evaluation namespace
    safe_globals = {
        '__builtins__': {
            '__import__': __import__,  # Allow from...import statements
        },
        'abs': abs,
        'round': round,
        'str': str,
        'int': int,
        'float': float,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        'len': len,
        'list': list,
        'range': range,
        'sorted': sorted,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'any': any,
        'all': all,
        'math': math,
        'Decimal': Decimal,
        'number_to_words': _number_to_words,
    }
    
    try:
        # Execute solution code with context
        exec(solution_code, safe_globals, working_context)
    except Exception as e:
        raise ValueError(f"Error executing solution: {e}")
    
    # Check for Answer or numbered answers
    if 'Answer' in working_context:
        return working_context['Answer']
    
    # Check for Answer1, Answer2, etc.
    numbered_answers = {}
    i = 1
    while f'Answer{i}' in working_context:
        numbered_answers[i] = working_context[f'Answer{i}']
        i += 1
    
    if numbered_answers:
        return numbered_answers
    
    raise ValueError("Solution did not set 'Answer' or 'Answer1', 'Answer2', etc.")


def format_answer(value: Any, answer_spec: Optional[VariableSpec] = None) -> str:
    """Format answer value according to Answer variable specification.
    
    Args:
        value: Computed answer value
        answer_spec: Answer variable specification from YAML
    
    Returns:
        Formatted answer string
    """
    if answer_spec is None:
        # No spec, try to format intelligently
        if isinstance(value, float):
            return f"{value:.2f}"
        else:
            return str(value)
    
    # Format based on Answer variable type and format
    if answer_spec.format == 'money':
        return f"${float(value):.2f}"
    
    elif answer_spec.format == 'percentage':
        return f"{int(value)}%"
    
    elif answer_spec.format == 'ordinal':
        from .jinja_renderer import ordinal_filter
        return ordinal_filter(int(value))
    
    elif answer_spec.format == 'speed':
        return f"{value:.2f} mph"
    
    elif answer_spec.format == 'length':
        # Length values with units (meters for perimeter, dimensions)
        if isinstance(value, (int, float)):
            if value == int(value):
                return f"{int(value)} meters"
            return f"{float(value):.2f} meters"
        return str(value)
    
    elif answer_spec.format == 'weight':
        return f"{value:.2f} kg"
    
    elif answer_spec.format == 'temperature':
        return f"{value:.1f}°F"
    
    elif answer_spec.format == 'area':
        # Area values with square units
        if isinstance(value, (int, float, Decimal)):
            if value == int(value):
                return f"{int(value)} square meters"
            return f"{float(value):.2f} square meters"
        return str(value)
    
    elif answer_spec.format == 'volume':
        # Volume values with cubic units
        if isinstance(value, (int, float, Decimal)):
            if value == int(value):
                return f"{int(value)} cubic meters"
            return f"{float(value):.2f} cubic meters"
        return str(value)
    
    elif answer_spec.type == 'time':
        # Format time as hours/minutes
        hours = int(value)
        minutes = int((value - hours) * 60)
        
        if hours > 0 and minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minutes"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{minutes} minutes"
    
    elif answer_spec.type == 'fraction':
        return str(value)
    
    elif answer_spec.type == 'integer':
        return str(int(value))
    
    elif answer_spec.type == 'decimal':
        return f"{float(value):.2f}"
    
    elif answer_spec.type == 'string':
        return str(value)
    
    # Default formatting
    elif isinstance(value, float):
        # Round to 2 decimal places for other floats
        return f"{value:.2f}"
    elif isinstance(value, int):
        return str(value)
    else:
        return str(value)
