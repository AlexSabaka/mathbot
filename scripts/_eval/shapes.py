"""Classify expected_answer strings into shapes — used for reporting accuracy breakdowns.

The comparator does not branch on shape; this is informational only.
"""

import re

_NUM = r"-?\d+(?:\.\d+)?"
_RE_NUMERIC_OR_CURRENCY = re.compile(rf"^\$?{_NUM}\$?$")
_RE_PERCENT = re.compile(rf"^{_NUM}%$")
_RE_FRACTION = re.compile(rf"^-?\d+/\d+$")
_RE_NUMERIC_WITH_UNIT = re.compile(rf"^{_NUM}\s*[a-zA-Z][\w\s]*\.?$")
_RE_KEY_VALUE = re.compile(
    r"^[a-zA-Z_][\w()]*\s*=\s*[^,]+(?:\s*,\s*[a-zA-Z_][\w()]*\s*=\s*[^,]+)+$"
)
_RE_LETTERED = re.compile(r"\([a-z]\)")
_RE_WORD = re.compile(r"^[a-zA-Z]+(?:\s+[a-zA-Z]+)*$")


def classify_shape(expected: str) -> str:
    """Return one of: numeric, currency, percent, fraction, numeric_with_unit,
    pipe_joined, lettered_parts, key_value, word, string_other."""
    s = expected.strip()
    if "|" in s:
        return "pipe_joined"
    if _RE_LETTERED.search(s):
        return "lettered_parts"
    if _RE_KEY_VALUE.match(s):
        return "key_value"
    if _RE_NUMERIC_OR_CURRENCY.match(s):
        return "currency" if "$" in s else "numeric"
    if _RE_PERCENT.match(s):
        return "percent"
    if _RE_FRACTION.match(s):
        return "fraction"
    if _RE_NUMERIC_WITH_UNIT.match(s):
        return "numeric_with_unit"
    if _RE_WORD.match(s):
        return "word"
    return "string_other"
