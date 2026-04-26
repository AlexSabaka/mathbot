"""Unit-system table for mathbot's display formatters.

Each `(type, system)` entry specifies how values of that type should be
displayed. `format_value` (in problem text via Jinja) and `format_answer`
(in the final `expected_answer` string) consult this table to thread
metric / imperial / mixed_us conventions through the generator.

The `mixed_us` system is the legacy default and reproduces pre-Phase-5.3
output byte-identically: $ for money, mph for speed, °F for temperature,
m/kg for length/weight, m²/m³ for area/volume. New templates opt into
`metric` (€, km/h, °C, m, kg, m², L) or `imperial` (no conversion of
length/weight/etc, just unit labels — ft, lb, °F, mph, ft², gal).

Solutions store and compute values in **system-native** units — this
table only handles display. Templates that need explicit unit conversion
(e.g. the dimensional-analysis P-M1 family) do the math themselves with
hardcoded factors, then format the result in whichever system the
template is written for.

Per-variable override: a `VariableSpec` may set `unit_system` to escape
the template default for that one variable (e.g. a unit-conversion
problem with one length in m and another in ft).
"""

from __future__ import annotations

from typing import Any, Dict, Optional


VALID_UNIT_SYSTEMS = {"metric", "imperial", "mixed_us"}

DEFAULT_UNIT_SYSTEM = "mixed_us"


# Per (type, system): how the unit displays in problem text and in the answer.
# Each entry is a small dict with one or more of:
#   value_short:   suffix appended to value in PROBLEM TEXT (e.g. "5m" with "m").
#                  Omit for types where templates write the units themselves
#                  (area, volume, speed all fall into this bucket today).
#   value_long:    suffix appended to value in ANSWER TEXT (e.g. "5 meters" with "meters").
#   value_compact: True if no space between value and suffix (temperature uses
#                  this so it renders "100.0°F", not "100.0 °F").
#   symbol:        prefix character (e.g. "$"). Used only for `money`.
UNIT_TABLE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "length": {
        "metric":   {"value_short": "m",  "value_long": "meters"},
        "imperial": {"value_short": "ft", "value_long": "feet"},
        "mixed_us": {"value_short": "m",  "value_long": "meters"},
    },
    "weight": {
        "metric":   {"value_short": "kg", "value_long": "kg"},
        "imperial": {"value_short": "lb", "value_long": "pounds"},
        "mixed_us": {"value_short": "kg", "value_long": "kg"},
    },
    "temperature": {
        "metric":   {"value_short": "°C", "value_long": "°C", "value_compact": True},
        "imperial": {"value_short": "°F", "value_long": "°F", "value_compact": True},
        "mixed_us": {"value_short": "°F", "value_long": "°F", "value_compact": True},
    },
    "speed": {
        "metric":   {"value_long": "km/h"},
        "imperial": {"value_long": "mph"},
        "mixed_us": {"value_long": "mph"},
    },
    "area": {
        "metric":   {"value_long": "square meters"},
        "imperial": {"value_long": "square feet"},
        "mixed_us": {"value_long": "square meters"},
    },
    "volume": {
        "metric":   {"value_long": "liters"},
        "imperial": {"value_long": "gallons"},
        "mixed_us": {"value_long": "cubic meters"},
    },
    "money": {
        "metric":   {"symbol": "€"},
        "imperial": {"symbol": "$"},
        "mixed_us": {"symbol": "$"},
    },
}


def resolve_system(
    var_system: Optional[str],
    template_system: Optional[str],
) -> str:
    """Effective unit system: per-variable override beats template default.

    Falls back to `mixed_us` when neither is set so existing templates
    continue to render identically.
    """
    return var_system or template_system or DEFAULT_UNIT_SYSTEM


def _entry(type_: str, system: str) -> Dict[str, Any]:
    return UNIT_TABLE.get(type_, {}).get(system, {})


def get_short_suffix(type_: str, system: str) -> Optional[str]:
    """Suffix used when the value appears inside problem text. None means
    the template is responsible for any units (e.g. `{{area}} square units`)."""
    return _entry(type_, system).get("value_short")


def get_long_suffix(type_: str, system: str) -> Optional[str]:
    """Suffix used when the value appears in the final answer string."""
    return _entry(type_, system).get("value_long")


def is_compact(type_: str, system: str) -> bool:
    """No space between value and suffix when True (temperature uses this)."""
    return bool(_entry(type_, system).get("value_compact", False))


def get_currency_symbol(system: str) -> str:
    """Currency prefix (`$`, `€`, …) for the given unit system."""
    return _entry("money", system).get("symbol", "$")
