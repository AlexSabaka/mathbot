"""Parse and evaluate solution expressions from YAML template files.

Solution is pure Python code executed in a safe namespace.
The solution must set an 'Answer' variable OR 'Answer1', 'Answer2', etc. for multi-answer problems.
"""

from typing import Dict, Any, Optional, Union
from decimal import Decimal
import math
from math import (
    gcd, lcm, pi, e, sqrt, exp,
    sin, cos, tan, asin, acos, atan, atan2,
    log, log2, log10,
    floor, ceil, factorial, comb, perm,
    radians, degrees,
)
import sympy
from scipy import stats
from .i18n import get_language_spec
from .units import ureg, Q_, get_pint_unit
from .yaml_loader import VariableSpec


def execute_solution(
    solution_code: str,
    context: Dict[str, Any],
    language: str = "en",
) -> Union[Any, Dict[str, Any]]:
    """Execute solution Python code and extract Answer(s).

    Args:
        solution_code: Python code from YAML solution section
        context: Dictionary of generated variable values
        language: Template language code; controls locale-sensitive
            sandbox callables such as `number_to_words`. Defaults to 'en'.

    Returns:
        Single answer value OR dict of {1: answer1, 2: answer2, ...} for multi-answer
    """
    language_spec = get_language_spec(language)
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
        # math module + commonly-used math primitives surfaced top-level
        'math': math,
        'pi': pi, 'e': e,
        'sqrt': sqrt, 'exp': exp,
        'sin': sin, 'cos': cos, 'tan': tan,
        'asin': asin, 'acos': acos, 'atan': atan, 'atan2': atan2,
        'log': log, 'log2': log2, 'log10': log10,
        'floor': floor, 'ceil': ceil,
        'factorial': factorial, 'comb': comb, 'perm': perm,
        'radians': radians, 'degrees': degrees,
        'gcd': gcd, 'lcm': lcm,
        # symbolic algebra + statistical inference (use as namespaces)
        'sympy': sympy,
        'stats': stats,
        # pint backbone (Stage 2). Solutions can wrap magnitudes in
        # Quantity objects for dimensional arithmetic and return them
        # as `Answer`; format_answer unwraps to the canonical
        # (type, system) unit. Use `Q_(value, get_pint_unit(type, system))`
        # to build a Quantity from a generated variable.
        'ureg': ureg,
        'Q_': Q_,
        'get_pint_unit': get_pint_unit,
        # numeric utilities
        'Decimal': Decimal,
        'number_to_words': language_spec.number_to_words,
    }
    
    try:
        # Execute solution code with context
        exec(solution_code, safe_globals, working_context)
    except Exception as exc:
        raise ValueError(f"Error executing solution: {exc}")
    
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


def format_answer(
    value: Any,
    answer_spec: Optional[VariableSpec] = None,
    template_unit_system: Optional[str] = None,
) -> str:
    """Format answer value according to Answer variable specification.

    Args:
        value: Computed answer value
        answer_spec: Answer variable specification from YAML (None → best-effort)
        template_unit_system: metadata.unit_system default (overridden by
            answer_spec.unit_system if set). Defaults to `mixed_us` to
            preserve pre-Phase-5.3 byte-identical output.

    Returns:
        Formatted answer string with units/currency baked in.
    """
    from .units import (
        resolve_system, get_long_suffix, is_compact, get_currency_symbol,
        quantity_to_canonical_magnitude, format_explicit_unit_value,
    )

    if answer_spec is None:
        # No spec, try to format intelligently
        if isinstance(value, float):
            return f"{value:.2f}"
        else:
            return str(value)

    system = resolve_system(answer_spec.unit_system, template_unit_system)

    # Unwrap pint Quantity values into the canonical (type, system) magnitude,
    # or into `answer_spec.unit` when the spec declares an explicit free-form
    # unit (Stage 3). No-op when the solution returned a plain number.
    value = quantity_to_canonical_magnitude(
        value, answer_spec.type, system, unit_override=answer_spec.unit,
    )

    # Free-form `unit:` (Stage 3) wins over the type-specific branches
    # below — author has declared the exact unit they want printed.
    if answer_spec.unit:
        return format_explicit_unit_value(value, answer_spec.unit)

    # Format based on Answer variable type and unit system
    if answer_spec.type == 'money':
        return f"{get_currency_symbol(system)}{float(value):.2f}"

    elif answer_spec.type == 'percentage':
        return f"{int(value)}%"

    elif answer_spec.type == 'ordinal':
        return get_language_spec('en').ordinal(int(value))

    elif answer_spec.type == 'speed':
        return f"{value:.2f} {get_long_suffix('speed', system)}"

    elif answer_spec.type == 'length':
        suffix = get_long_suffix('length', system)
        if isinstance(value, (int, float)):
            if value == int(value):
                return f"{int(value)} {suffix}"
            return f"{float(value):.2f} {suffix}"
        return str(value)

    elif answer_spec.type == 'weight':
        # Pre-5.3 mixed_us was always 2-decimal regardless of int-ness.
        return f"{value:.2f} {get_long_suffix('weight', system)}"

    elif answer_spec.type == 'temperature':
        suffix = get_long_suffix('temperature', system)
        sep = '' if is_compact('temperature', system) else ' '
        return f"{value:.1f}{sep}{suffix}"

    elif answer_spec.type == 'area':
        suffix = get_long_suffix('area', system)
        if isinstance(value, (int, float, Decimal)):
            if value == int(value):
                return f"{int(value)} {suffix}"
            return f"{float(value):.2f} {suffix}"
        return str(value)

    elif answer_spec.type == 'volume':
        suffix = get_long_suffix('volume', system)
        if isinstance(value, (int, float, Decimal)):
            if value == int(value):
                return f"{int(value)} {suffix}"
            return f"{float(value):.2f} {suffix}"
        return str(value)

    elif answer_spec.type in ('density', 'energy', 'power', 'pressure', 'force', 'acceleration'):
        suffix = get_long_suffix(answer_spec.type, system)
        if isinstance(value, (int, float, Decimal)):
            if value == int(value):
                return f"{int(value)} {suffix}"
            return f"{float(value):.2f} {suffix}"
        return str(value)

    elif answer_spec.type == 'time':
        # Format time as hours/minutes (locale-agnostic for now)
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
        return f"{value:.2f}"
    elif isinstance(value, int):
        return str(value)
    else:
        return str(value)
