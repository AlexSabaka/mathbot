"""Mathbot evaluator — multiplicity-aware number-presence with substring fallback.

Strategy:
  - If the expected answer contains numeric tokens, every one of them must be
    present (within tolerance) in the parsed answer span. Multiplicity is
    preserved: two `5`s in expected need two `5`s in the parsed value.
  - If the expected answer has no numeric tokens, fall back to a normalized
    substring check.
  - We DO NOT fall back to scanning the full model response when the parser
    returned a non-empty span. That gate prevents crediting numbers that only
    appeared in the chain-of-thought.
"""

import math
import re
from collections import Counter
from typing import Any, Dict, List

from src.plugins.base import EvaluationResult, ParsedAnswer, ResultEvaluator


_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
_THOUSANDS_RE = re.compile(r"(?<=\d),(?=\d{3}\b)")


# ---------------------------------------------------------------------------
# Shape classifier (informational; comparator does not branch on it)
# ---------------------------------------------------------------------------

_RE_NUMERIC_OR_CURRENCY = re.compile(r"^\$?-?\d+(?:\.\d+)?\$?$")
_RE_PERCENT = re.compile(r"^-?\d+(?:\.\d+)?%$")
_RE_FRACTION = re.compile(r"^-?\d+/\d+$")
_RE_NUMERIC_WITH_UNIT = re.compile(r"^-?\d+(?:\.\d+)?\s*[a-zA-Z][\w\s]*\.?$")
_RE_KEY_VALUE = re.compile(
    r"^[a-zA-Z_][\w()]*\s*=\s*[^,]+(?:\s*,\s*[a-zA-Z_][\w()]*\s*=\s*[^,]+)+$"
)
_RE_LETTERED = re.compile(r"\([a-z]\)")
_RE_WORD = re.compile(r"^[a-zA-Z]+(?:\s+[a-zA-Z]+)*$")


def classify_shape(expected: str) -> str:
    s = (expected or "").strip()
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


# ---------------------------------------------------------------------------
# Number extraction + multiplicity-aware presence check
# ---------------------------------------------------------------------------

def extract_numbers(s: str) -> list[float]:
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


def _close(a: float, b: float, rel_tol: float = 1e-3, abs_tol: float = 1e-3) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def _all_present(needed: list[float], haystack: list[float]) -> bool:
    available = list(haystack)
    for n in needed:
        idx = -1
        for i, h in enumerate(available):
            if _close(n, h):
                idx = i
                break
        if idx < 0:
            return False
        available.pop(idx)
    return True


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class MathbotEvaluator(ResultEvaluator):
    def evaluate(
        self,
        parsed_answer: ParsedAnswer,
        expected_answer: Any,
        task_params: Dict[str, Any],
    ) -> EvaluationResult:
        if not parsed_answer.success:
            return EvaluationResult(
                correct=False,
                match_type="parse_error",
                accuracy=0.0,
                error=parsed_answer.error,
                details={"answer_shape": task_params.get("answer_shape")},
            )

        extracted = str(parsed_answer.value)
        expected = str(expected_answer)
        shape = task_params.get("answer_shape") or classify_shape(expected)
        details: Dict[str, Any] = {"answer_shape": shape}

        expected_numbers = extract_numbers(expected)
        if expected_numbers:
            extracted_numbers = extract_numbers(extracted)
            if _all_present(expected_numbers, extracted_numbers):
                return EvaluationResult(
                    correct=True,
                    match_type="numeric_match",
                    accuracy=1.0,
                    details=details,
                )
            details["expected_numbers"] = expected_numbers
            details["extracted_numbers"] = extracted_numbers
            return EvaluationResult(
                correct=False,
                match_type="numeric_missing",
                accuracy=0.0,
                details=details,
            )

        ne = _normalize(expected)
        if ne and ne in _normalize(extracted):
            return EvaluationResult(
                correct=True,
                match_type="substring_match",
                accuracy=1.0,
                details=details,
            )
        return EvaluationResult(
            correct=False,
            match_type="wrong",
            accuracy=0.0,
            details=details,
        )

    def aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        correct = sum(1 for r in results if r.get("correct"))
        match_types: Counter[str] = Counter()
        by_shape: Dict[str, Dict[str, int]] = {}
        by_grade: Dict[str, Dict[str, int]] = {}

        for r in results:
            mt = r.get("match_type", "unknown")
            match_types[mt] += 1

            details = r.get("details") or {}
            shape = details.get("answer_shape", "unknown")
            grade = (
                r.get("task_params", {}).get("mathbot_grade")
                if isinstance(r.get("task_params"), dict)
                else None
            ) or "unknown"

            by_shape.setdefault(shape, {"correct": 0, "total": 0})
            by_shape[shape]["total"] += 1
            if r.get("correct"):
                by_shape[shape]["correct"] += 1

            by_grade.setdefault(grade, {"correct": 0, "total": 0})
            by_grade[grade]["total"] += 1
            if r.get("correct"):
                by_grade[grade]["correct"] += 1

        for bucket in (*by_shape.values(), *by_grade.values()):
            bucket["accuracy"] = (
                bucket["correct"] / bucket["total"] if bucket["total"] else 0.0
            )

        return {
            "accuracy": correct / total if total else 0.0,
            "correct": correct,
            "total": total,
            "match_types": dict(match_types),
            "by_answer_shape": by_shape,
            "by_grade": by_grade,
        }
