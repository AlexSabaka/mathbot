"""Compare an extracted/raw model response against the expected answer.

Strategy:
  - Pull all numeric tokens from the expected answer.
  - If expected has numbers: every expected number must appear (with tolerance)
    in either the extracted span or, failing that, the full response. Multiplicity
    is preserved (two `5`s in expected need two `5`s in haystack).
  - If expected has no numbers: substring match in normalized form.
"""

import math
import re

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
_THOUSANDS_RE = re.compile(r"(?<=\d),(?=\d{3}\b)")


def extract_numbers(s: str) -> list[float]:
    """Pull numeric tokens from a string. Strips thousands separators (1,234 → 1234)."""
    if not s:
        return []
    cleaned = _THOUSANDS_RE.sub("", s)
    out: list[float] = []
    for m in _NUMBER_RE.finditer(cleaned):
        try:
            out.append(float(m.group()))
        except ValueError:
            pass
    return out


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _close(a: float, b: float, rel_tol: float = 1e-3, abs_tol: float = 1e-3) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def _all_present(needed: list[float], haystack: list[float]) -> bool:
    """Multiplicity-preserving check: each `needed` must consume one match from haystack."""
    available = list(haystack)
    for n in needed:
        match_idx = -1
        for i, h in enumerate(available):
            if _close(n, h):
                match_idx = i
                break
        if match_idx < 0:
            return False
        available.pop(match_idx)
    return True


def compare(
    extracted: str | None,
    expected: str,
    response: str,
) -> tuple[bool, str]:
    """Return (correct, reason).

    Only falls back to scanning the full response when `extracted` is None/empty.
    If the extractor returned a non-empty span, that's the model's final answer —
    don't credit numbers that only appeared in the chain-of-thought.
    """
    expected_numbers = extract_numbers(expected)
    haystack_text = extracted if extracted else response
    haystack_label = "extracted" if extracted else "full_response"

    if expected_numbers:
        haystack_numbers = extract_numbers(haystack_text)
        if _all_present(expected_numbers, haystack_numbers):
            return True, f"numeric_match_{haystack_label}"
        return False, "numeric_missing"

    ne = normalize(expected)
    if ne in normalize(haystack_text):
        return True, f"substring_match_{haystack_label}"
    return False, "string_mismatch"
