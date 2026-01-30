"""Parse and evaluate solution expressions from template files.

Solution section format (after --- separator):
    variable1 = expression1
    variable2 = expression2
    Answer = final_expression
"""

import re
from typing import Dict, Any, Tuple
from decimal import Decimal
import math


def split_template(template_content: str) -> Tuple[str, str]:
    """Split template into problem and solution sections.
    
    Args:
        template_content: Full template content
    
    Returns:
        Tuple of (problem_section, solution_section)
    """
    if '---' in template_content:
        parts = template_content.split('---', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
    else:
        return template_content.strip(), ''


def parse_solution_expressions(solution_section: str) -> list:
    """Parse solution section into list of (variable, expression) tuples.
    
    Args:
        solution_section: Solution section content
    
    Returns:
        List of (var_name, expression_string) tuples
    """
    if not solution_section:
        return []
    
    expressions = []
    lines = solution_section.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('{{!--'):
            continue
        
        # Match: variable = expression
        match = re.match(r'(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(1)
            expression = match.group(2).strip()
            expressions.append((var_name, expression))
    
    return expressions


def evaluate_expression(expression: str, context: Dict[str, Any]) -> Any:
    """Safely evaluate a mathematical expression with given context.
    
    Args:
        expression: Mathematical expression string (e.g., "{{price}} * {{quantity}}")
        context: Dictionary of variable values
    
    Returns:
        Evaluated result
    """
    # Create working context with numeric values (strip $ from money)
    working_context = {}
    for var_name, value in context.items():
        if isinstance(value, str) and value.startswith('$'):
            # Convert money string to float
            working_context[var_name] = float(value[1:])
        elif isinstance(value, (int, float)):
            working_context[var_name] = value
        else:
            # Keep non-numeric values for reference
            working_context[var_name] = value
    
    # Replace {{variable}} with context values
    for var_name, value in working_context.items():
        if isinstance(value, (int, float)):
            expression = expression.replace(f"{{{{{var_name}}}}}", str(value))
    
    # Handle exponentiation (^)
    expression = expression.replace('^', '**')
    
    # Create safe evaluation namespace
    safe_dict = {
        '__builtins__': {},
        'abs': abs,
        'round': round,
        'str': str,
        'int': int,
        'float': float,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        'math': math,
        'Decimal': Decimal,
    }
    
    # Add numeric context variables
    for key, val in working_context.items():
        if isinstance(val, (int, float)):
            safe_dict[key] = val
    
    try:
        result = eval(expression, safe_dict)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expression}': {e}")


def compute_answer(template_content: str, context: Dict[str, Any]) -> str:
    """Compute the expected answer from template solution section.
    
    Args:
        template_content: Full template content (with problem and solution)
        context: Dictionary of generated variable values
    
    Returns:
        Computed answer as string
    """
    _, solution_section = split_template(template_content)
    
    if not solution_section:
        raise ValueError("Template has no solution section (missing --- separator)")
    
    expressions = parse_solution_expressions(solution_section)
    
    if not expressions:
        raise ValueError("Solution section has no valid expressions")
    
    # Create a working context (copy to avoid modifying original)
    working_context = context.copy()
    
    # Evaluate expressions in order
    answer = None
    for var_name, expression in expressions:
        result = evaluate_expression(expression, working_context)
        working_context[var_name] = result
        
        # Track the Answer variable
        if var_name == 'Answer' or var_name == 'answer':
            answer = result
    
    if answer is None:
        # If no explicit Answer variable, use last evaluated expression
        if expressions:
            _, last_expr = expressions[-1]
            answer = evaluate_expression(last_expr, context)
        else:
            raise ValueError("Could not determine answer from solution section")
    
    # Format answer appropriately
    return format_answer(answer, context)


def format_answer(value: Any, context: Dict[str, Any]) -> str:
    """Format answer value as string with appropriate units/formatting.
    
    Args:
        value: Computed answer value
        context: Original context (to infer units/format)
    
    Returns:
        Formatted answer string
    """
    # Check if any money variables in context
    has_money = any('price' in k or 'cost' in k or 'dollar' in k for k in context.keys())
    
    if has_money and isinstance(value, (int, float, Decimal)):
        # Format as money
        return f"${float(value):.2f}"
    elif isinstance(value, float):
        # Round to 2 decimal places for other floats
        return f"{value:.2f}"
    elif isinstance(value, int):
        return str(value)
    else:
        return str(value)
