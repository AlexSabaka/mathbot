"""Unit-system table for mathbot's display formatters, backed by `pint`.

`pint` provides the canonical Quantity registry. The registry is consulted
at module-load time, where every unit string in `DISPLAY_UNITS` is
validated against `ureg.parse_units()` — typos in unit names fail loudly
rather than silently rendering an empty suffix later. The default display
behavior remains `system-native-internal`: values stored on a `metric`
template's `temperature` variable are already in °C, so no `.to()`
conversion happens at format time. The legacy `mixed_us` system therefore
renders byte-identically to pre-Phase-5.3R.

Stage 2 (this checkpoint) adds compound-unit variable types (`density`,
`energy`, `power`, `pressure`, `force`, `acceleration`) to `DISPLAY_UNITS`
and exposes `ureg`, `Q_`, and `get_pint_unit` in the solution sandbox.
When a solution returns a `pint.Quantity`, `format_answer` calls
`quantity_to_canonical_magnitude` to convert into the canonical unit for
the answer's `(type, system)` and unwrap the magnitude — so a P-G3
template can mix units freely (`Q_(1, 'L') * Q_(750, 'kg/m**3')`) and
hand back a Quantity, and the formatter does the right thing.

Stage 3 (TD-3.6) adds a free-form `unit:` field on `VariableSpec` for
one-off compound units that don't deserve a dedicated type.

Currency stays out of pint — currencies aren't dimensional quantities,
and FX conversion needs out-of-process exchange rates. `CURRENCY_SYMBOL`
is its own dict.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pint


# ---------------------------------------------------------------------------
# Pint registry singleton.
#
# A single registry is shared across the process. Stage 2 will expose
# `ureg` and `Q_` in the solution sandbox via `safe_globals` — a single
# instance keeps Quantity comparisons (`a == b`) sane (mixed registries
# refuse to compare).
# ---------------------------------------------------------------------------

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


# ---------------------------------------------------------------------------
# System / type → display unit mapping.
# Tuple shape: (pint_unit_string, short_suffix_or_None, long_suffix).
#   pint_unit_string — validated at module load via `ureg.parse_units()`.
#   short_suffix     — appended to the value in PROBLEM TEXT (e.g. "5m").
#                      `None` means the type renders unitless in problem
#                      text and the template adds its own (today: speed,
#                      volume).
#   long_suffix      — appended in the ANSWER TEXT (e.g. "5 meters").
# ---------------------------------------------------------------------------

VALID_UNIT_SYSTEMS = {"metric", "imperial", "mixed_us"}

DEFAULT_UNIT_SYSTEM = "mixed_us"


_DisplayEntry = Tuple[str, Optional[str], str]

DISPLAY_UNITS: Dict[str, Dict[str, _DisplayEntry]] = {
    "mixed_us": {
        "length":       ("meter",                 "m",      "meters"),
        "weight":       ("kilogram",              "kg",     "kg"),
        "temperature":  ("degF",                  "°F",     "°F"),
        "speed":        ("mile / hour",           None,     "mph"),
        "area":         ("meter ** 2",            "m²",     "m²"),
        "volume":       ("meter ** 3",            None,     "m³"),
        # Stage 2 compound types. Mixed-US tracks SI for physics quantities —
        # the corpus's "US" tilt is currency / mph / °F, not the rest.
        "density":      ("kilogram / meter ** 3", "kg/m³",  "kg/m³"),
        "energy":       ("joule",                 "J",      "joules"),
        "power":        ("watt",                  "W",      "watts"),
        "pressure":     ("pascal",                "Pa",     "pascals"),
        "force":        ("newton",                "N",      "newtons"),
        "acceleration": ("meter / second ** 2",   "m/s²",   "m/s²"),
    },
    "metric": {
        "length":       ("meter",                 "m",      "meters"),
        "weight":       ("kilogram",              "kg",     "kg"),
        "temperature":  ("degC",                  "°C",     "°C"),
        "speed":        ("km / hour",             None,     "km/h"),
        "area":         ("meter ** 2",            "m²",     "m²"),
        "volume":       ("liter",                 None,     "liters"),
        "density":      ("kilogram / meter ** 3", "kg/m³",  "kg/m³"),
        "energy":       ("joule",                 "J",      "joules"),
        "power":        ("watt",                  "W",      "watts"),
        "pressure":     ("pascal",                "Pa",     "pascals"),
        "force":        ("newton",                "N",      "newtons"),
        "acceleration": ("meter / second ** 2",   "m/s²",   "m/s²"),
    },
    "imperial": {
        "length":       ("foot",                  "ft",     "feet"),
        "weight":       ("pound",                 "lb",     "pounds"),
        "temperature":  ("degF",                  "°F",     "°F"),
        "speed":        ("mile / hour",           None,     "mph"),
        "area":         ("foot ** 2",             "ft²",    "ft²"),
        "volume":       ("gallon",                None,     "gallons"),
        "density":      ("pound / foot ** 3",     "lb/ft³", "lb/ft³"),
        "energy":       ("foot * pound_force",    "ft·lbf", "foot-pounds"),
        "power":        ("horsepower",            "hp",     "horsepower"),
        "pressure":     ("psi",                   "psi",    "psi"),
        "force":        ("pound_force",           "lbf",    "pound-force"),
        "acceleration": ("foot / second ** 2",    "ft/s²",  "ft/s²"),
    },
}


def _validate_display_units(units: Dict[str, Dict[str, _DisplayEntry]]) -> None:
    """Assert every pint unit string in DISPLAY_UNITS parses cleanly.

    Catches typos (`"meeter"`, `"kg/m^"`) at import time rather than at
    the first template render. Raises pint's `UndefinedUnitError` (or
    similar parse error) with the offending entry.
    """
    for system, type_map in units.items():
        for type_, (pint_unit, _short, _long) in type_map.items():
            try:
                ureg.parse_units(pint_unit)
            except Exception as exc:  # pint raises a tower of subclasses
                raise ValueError(
                    f"DISPLAY_UNITS[{system!r}][{type_!r}] has invalid "
                    f"pint unit {pint_unit!r}: {exc}"
                ) from exc


_validate_display_units(DISPLAY_UNITS)


# ---------------------------------------------------------------------------
# Currency. Pint isn't a currency library; conversion needs FX rates which
# are out of scope. One symbol per system, no Quantity wrapping.
# ---------------------------------------------------------------------------

CURRENCY_SYMBOL: Dict[str, str] = {
    "mixed_us": "$",
    "metric":   "€",
    "imperial": "$",
}


# ---------------------------------------------------------------------------
# Helpers consumed by `variable_generator.format_value` and
# `solution_evaluator.format_answer`.
# ---------------------------------------------------------------------------

# Types that have a system-aware suffix in DISPLAY_UNITS.
UNIT_AWARE_TYPES = frozenset(DISPLAY_UNITS["mixed_us"].keys())

# Per-type rule for whether to drop the space between value and suffix.
# Today only temperature ("100.0°F", not "100.0 °F").
_COMPACT_TYPES = frozenset({"temperature"})


def resolve_system(
    var_system: Optional[str],
    template_system: Optional[str],
) -> str:
    """Effective unit system: per-variable override beats template default.

    Falls back to `mixed_us` so existing templates render identically.
    """
    return var_system or template_system or DEFAULT_UNIT_SYSTEM


def get_short_suffix(type_: str, system: str) -> Optional[str]:
    """Suffix appended to the value in problem text (e.g. `"m"` → `"5m"`).

    `None` means the template is responsible for any units (e.g.
    `"{{area}} square units"`).
    """
    entry = DISPLAY_UNITS.get(system, {}).get(type_)
    return entry[1] if entry else None


def get_long_suffix(type_: str, system: str) -> Optional[str]:
    """Suffix appended in the final answer string (e.g. `"meters"` → `"5 meters"`)."""
    entry = DISPLAY_UNITS.get(system, {}).get(type_)
    return entry[2] if entry else None


def is_compact(type_: str, system: str) -> bool:
    """No space between value and suffix when True (temperature uses this)."""
    return type_ in _COMPACT_TYPES


def get_currency_symbol(system: str) -> str:
    """Currency prefix (`$`, `€`, …) for the given unit system."""
    return CURRENCY_SYMBOL.get(system, "$")


def get_pint_unit(type_: str, system: str) -> Optional[str]:
    """Return the pint unit string for (type, system), e.g. `"meter ** 2"`.

    Templates wrap a magnitude in a Quantity via
    `Q_(value, get_pint_unit('density', 'metric'))`. The matching call
    in `format_answer` (`quantity_to_canonical_magnitude`) uses the
    same unit when unwrapping a Quantity Answer.
    """
    entry = DISPLAY_UNITS.get(system, {}).get(type_)
    return entry[0] if entry else None


def quantity_to_canonical_magnitude(value: Any, type_: str, system: str) -> Any:
    """If value is a `pint.Quantity`, convert to the canonical (type, system)
    unit and return the magnitude as a float. Otherwise return value unchanged.

    Lets a solution return a Quantity in any compatible unit and have the
    formatter print it consistently. A P-G3 mass computed as
    `Q_(volume, 'L') * Q_(density, 'kg/m**3')` carries the unit
    `kilogram * liter / meter ** 3` (dimensionally `kg`); calling
    `.to('kilogram').magnitude` collapses it back to the float the formatter
    expects. Templates that already return floats are unaffected.
    """
    if isinstance(value, pint.Quantity):
        canonical = get_pint_unit(type_, system)
        if canonical is not None:
            return float(value.to(canonical).magnitude)
        # Unknown type — return raw magnitude so the formatter still gets
        # a number rather than a Quantity object.
        return float(value.magnitude)
    return value
