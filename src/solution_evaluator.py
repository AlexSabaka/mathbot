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


def _build_safe_globals(language: str = "en") -> Dict[str, Any]:
    """Construct the shared sandbox namespace.

    Single source of truth for what's exposed to template solution
    code AND the Phase β `format: python` visual.source path. Pulling
    this out into one builder keeps the two surfaces in lockstep — a
    new safe primitive added for solution code is automatically
    available to visuals (and vice versa).
    """
    language_spec = get_language_spec(language)
    return {
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


def build_visual_sandbox(language: str = "en") -> Dict[str, Any]:
    """Phase β (H1). Sandbox for `format: python` visual.source blocks.

    Same surface as the solution sandbox plus the visual builders. A
    visual block is structurally simpler than a solution (no `Answer`
    contract, just a `Visual = ...` binding) but it benefits from the
    same numeric / symbolic primitives so visuals can call sympy or
    pint directly when an author wants e.g. a parametrically-derived
    point on the curve.
    """
    sandbox = _build_safe_globals(language)
    # Lazy import keeps `src.visuals` out of the solution-eval import
    # graph for templates that never use visuals.
    from .visuals import (
        PlotSVG, TreeSVG, MarkovSVG, CircuitSVG, SVGBuilder,
        TableSVG, FunctionValueTable, MatrixTable, DataTable,
        SectorFigure, ConeNetFigure, RiverbankFigure,
        OptimizationRegionFigure, RelatedRatesGeometry,
        FunctionGraphFigure, AxesAnnotation, TriangleFigure,
        ObjectArray, PatternStrip, ClockFace, BalanceScale,
        LinearRuler, glyph_for,
    )
    sandbox.update({
        'PlotSVG': PlotSVG,
        'TreeSVG': TreeSVG,
        'MarkovSVG': MarkovSVG,
        'CircuitSVG': CircuitSVG,
        'SVGBuilder': SVGBuilder,
        # γ.3 (A.1) — table builders. `Visual = TableSVG(...).render()`
        # produces the SVG; templates can also call `to_text` / etc. for
        # cross-format rendering when they author for multi-format
        # output.
        'TableSVG': TableSVG,
        'FunctionValueTable': FunctionValueTable,
        'MatrixTable': MatrixTable,
        'DataTable': DataTable,
        # γ.3 (A.2) — geometric figure builders. Each ships
        # to_svg() / to_text() / to_latex() for multi-format output.
        'SectorFigure': SectorFigure,
        'ConeNetFigure': ConeNetFigure,
        'RiverbankFigure': RiverbankFigure,
        'OptimizationRegionFigure': OptimizationRegionFigure,
        'RelatedRatesGeometry': RelatedRatesGeometry,
        'FunctionGraphFigure': FunctionGraphFigure,
        'AxesAnnotation': AxesAnnotation,
        'TriangleFigure': TriangleFigure,
        # γ.4s — K1-tuned primitives. `glyph_for(item)` returns a
        # callable that renders an item-glyph (apple/book/star/etc.)
        # at given (cx, cy, size, fill) — the dispatcher is the
        # primary K1 author surface.
        'ObjectArray': ObjectArray,
        'PatternStrip': PatternStrip,
        'ClockFace': ClockFace,
        'BalanceScale': BalanceScale,
        'LinearRuler': LinearRuler,
        'glyph_for': glyph_for,
    })
    return sandbox


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
    if not solution_code:
        raise ValueError("Template has no solution code")

    # Create a working context (copy to avoid modifying original)
    working_context = context.copy()

    # Convert money strings to floats for computation
    for var_name, value in list(working_context.items()):
        if isinstance(value, str) and value.startswith('$'):
            working_context[var_name] = float(value[1:])

    safe_globals = _build_safe_globals(language)

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


def _format_sympy_expr(expr: "sympy.Basic", answer_spec: Optional[VariableSpec]) -> str:
    """Canonicalize a symbolic Answer (B1).

    Runs `sympy.simplify` once and emits the result via `sympy.sstr` —
    Python-like syntax that grader-side `sympy.sympify` round-trips
    cleanly. If `simplify` raises (rare; degenerate expression trees),
    fall back to the raw `sstr` of the input. Honors `answer_spec.unit`
    by appending the parsed pint suffix so symbolic ODE / kinematics
    answers can carry units (`"3*cos(omega*t) m"`).
    """
    try:
        canonical = sympy.simplify(expr)
    except Exception:
        canonical = expr
    body = sympy.sstr(canonical)
    if answer_spec is not None and answer_spec.unit:
        # Use pint's compact pretty form to match
        # format_explicit_unit_value's spacing convention.
        from .units import ureg as _ureg  # local to avoid cycle
        try:
            unit_str = f"{_ureg.parse_units(answer_spec.unit):~P}"
        except Exception:
            unit_str = answer_spec.unit
        return f"{body} {unit_str}"
    return body


def _format_sympy_matrix(m: "sympy.MatrixBase") -> str:
    """Format a sympy.Matrix Answer as `[[a, b], [c, d]]` (B1).

    Each entry is rendered via `sympy.sstr` so symbolic entries
    canonicalize the same way as scalar Expr Answers; integer/float
    entries print without sympy's `Rational(1,2)` boxing. Matches the
    canonical form a grader can `sympy.sympify` back to a Matrix.
    """
    rows = []
    for r in range(m.rows):
        row = ", ".join(sympy.sstr(sympy.simplify(m[r, c])) for c in range(m.cols))
        rows.append(f"[{row}]")
    return "[" + ", ".join(rows) + "]"


def _format_complex(z: complex) -> str:
    """Format a Python `complex` Answer as `a + bi` / `a - bi` / `bi` / `a` (B1).

    Real and imaginary parts use the standard 2-decimal display; the
    imaginary unit is `i` (math convention) — N7 templates that prefer
    engineering's `j` should set `unit: 'A'` and post-process in the
    solution block. Pure-real and pure-imaginary cases drop the
    redundant zero term to keep grader output clean.
    """
    re_part, im_part = z.real, z.imag
    if im_part == 0:
        return f"{re_part:.2f}" if re_part != int(re_part) else str(int(re_part))
    if re_part == 0:
        coef = f"{im_part:.2f}" if im_part != int(im_part) else str(int(im_part))
        return f"{coef}i"
    re_s = f"{re_part:.2f}" if re_part != int(re_part) else str(int(re_part))
    if im_part > 0:
        im_s = f"{im_part:.2f}" if im_part != int(im_part) else str(int(im_part))
        return f"{re_s} + {im_s}i"
    abs_im = abs(im_part)
    im_s = f"{abs_im:.2f}" if abs_im != int(abs_im) else str(int(abs_im))
    return f"{re_s} - {im_s}i"


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

    # B1 (Phase α). Symbolic / matrix / complex dispatch happens before
    # the numeric pipeline because `quantity_to_canonical_magnitude` and
    # the `%.2f` branches below assume `value` is a real number. A sympy
    # Expr with no free symbols (`sympy.Integer(5)`, `sympy.sqrt(4)`)
    # *is* numeric and falls through to the numeric branches via
    # `float()` coercion, preserving the legacy formatting for templates
    # that happen to use sympy intermediately.
    if isinstance(value, sympy.MatrixBase):
        return _format_sympy_matrix(value)
    if isinstance(value, sympy.Basic):
        if value.free_symbols or not getattr(value, "is_number", False):
            return _format_sympy_expr(value, answer_spec)
        try:
            value = float(value)
        except (TypeError, ValueError):
            return _format_sympy_expr(value, answer_spec)
    if isinstance(value, complex):
        return _format_complex(value)

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


def compare_answers(
    actual: str,
    expected: str,
    mode: Optional[str] = None,
    tolerance: Optional[float] = None,
    tolerance_rel: Optional[float] = None,
) -> bool:
    """Compare a fixture's `actual` and `expected` answer strings.

    Phase α (B3/B4) shared comparison logic for both the CLI `mathbot
    test` runner and `mathbot lint`'s embedded fixture check. Modes:

    - ``string`` (default): exact-string equality. Preserves the
      legacy behaviour the existing 1278-fixture corpus depends on.
    - ``numeric``: parse both as floats and compare with `tolerance`
      (absolute) and/or `tolerance_rel` (relative). Either threshold
      passing counts as a match. With both unset the parsed floats
      must be exactly equal — typically used to ignore display-only
      formatter differences (e.g. trailing-zero rounding).
    - ``symbolic``: parse both via ``sympy.sympify`` and check
      ``simplify(a - b) == 0`` (with ``equals()`` as a fallback when
      simplify can't decide). Used by N3/N7/N9/N11–N16 templates whose
      canonical answer form is ambiguous up to algebraic
      simplification (``2*sin(x)*cos(x)`` ↔ ``sin(2*x)``).

    Returns True iff the answers match under the chosen mode. Raises
    ValueError on a malformed mode argument; numeric/symbolic parse
    failures fall back to string equality so a buggy fixture surfaces
    as a drift finding rather than a crash.
    """
    if mode in (None, 'string'):
        return actual == expected

    if mode == 'numeric':
        try:
            a = float(actual)
            b = float(expected)
        except (TypeError, ValueError):
            return actual == expected
        if tolerance is None and tolerance_rel is None:
            return a == b
        diff = abs(a - b)
        if tolerance is not None and diff <= tolerance:
            return True
        if tolerance_rel is not None:
            denom = max(abs(a), abs(b))
            if denom == 0:
                return diff == 0
            if diff / denom <= tolerance_rel:
                return True
        return False

    if mode == 'symbolic':
        try:
            a = sympy.sympify(actual)
            b = sympy.sympify(expected)
        except (sympy.SympifyError, SyntaxError, TypeError):
            return actual == expected
        try:
            if sympy.simplify(a - b) == 0:
                return True
        except Exception:
            pass
        try:
            return bool(a.equals(b))
        except Exception:
            return actual == expected

    raise ValueError(
        f"Invalid compare mode {mode!r}. Must be one of: "
        f"string, numeric, symbolic."
    )
