"""Tests for scripts/_eval/{extract,shapes,compare}.py."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pytest

from _eval.compare import compare, extract_numbers
from _eval.extract import extract_answer
from _eval.shapes import classify_shape


# ---- extract_answer ---------------------------------------------------------

@pytest.mark.parametrize(
    "response,expected_value,expected_strategy",
    [
        ("The answer is \\boxed{42}.", "42", "latex_boxed"),
        ("\\boxed{27}", "27", "latex_boxed"),
        ("foo \\boxed{1/2} bar \\boxed{3/4}", "3/4", "latex_boxed"),
        ("Step 1: x. Step 2: y. **27**", "27", "md_bold"),
        ("So the **final answer** is **42 dollars**.", "42 dollars", "md_bold"),
        ("Reasoning... Answer: 13", "13", "answer_label"),
        ("Final answer: $6.94", "$6.94", "answer_label"),
        ("The answer is 42 cm", "42 cm", "answer_label"),
        ("just a number\n42", "42", "last_line"),
        ("", None, "empty"),
        ("   ", None, "empty"),
    ],
)
def test_extract_strategies(response, expected_value, expected_strategy):
    val, strategy = extract_answer(response)
    assert val == expected_value
    assert strategy == expected_strategy


# ---- classify_shape ---------------------------------------------------------

@pytest.mark.parametrize(
    "expected,shape",
    [
        ("32.50", "numeric"),
        ("897122", "numeric"),
        ("$15.32", "currency"),
        ("32.50%", "percent"),
        ("3/11", "fraction"),
        ("10 meters", "numeric_with_unit"),
        ("$18000.00 | $18000.00 | $24000.00", "pipe_joined"),
        ("(a) 1/3, (b) 5/9", "lettered_parts"),
        ("mean=82.00, variance=56.00, sd=7.48", "key_value"),
        ("pencil", "word"),
        ("balance: $6571.54, interest: $171.54", "string_other"),
        ("(29, 5)", "string_other"),
        ("1:2", "string_other"),
    ],
)
def test_classify_shape(expected, shape):
    assert classify_shape(expected) == shape


# ---- extract_numbers --------------------------------------------------------

def test_extract_numbers_strips_thousands():
    assert extract_numbers("$1,234.56 paid, balance $7,890") == [1234.56, 7890.0]


def test_extract_numbers_handles_negative():
    assert extract_numbers("change of -3 dollars") == [-3.0]


def test_extract_numbers_empty():
    assert extract_numbers("") == []


# ---- compare ---------------------------------------------------------------

# Positive cases: model answer should match expected
@pytest.mark.parametrize(
    "extracted,expected,response",
    [
        # Plain number — extracted exactly
        ("42", "42", "Step 1... \\boxed{42}"),
        # Currency — model dropped $ sign
        ("6.94", "$6.94", "The total is 6.94 dollars."),
        # Percent — model added % vs expected
        ("32.5", "32.5%", "It's 32.5%"),
        # Pipe-joined: all parts in extracted
        (
            "$18000, $18000, $24000",
            "$18000.00 | $18000.00 | $24000.00",
            "Three cohorts: $18000, $18000, $24000.",
        ),
        # Lettered parts: numbers present in any order
        (
            "(a) 1/3 (b) 5/9",
            "(a) 1/3, (b) 5/9",
            "Calculations show: (a) 1/3 and (b) 5/9.",
        ),
        # Key-value: all numeric values present
        (
            "mean is 82, variance 56, standard deviation 7.48",
            "mean=82.00, variance=56.00, sd=7.48",
            "Computed: mean is 82, variance 56, standard deviation 7.48.",
        ),
        # Numeric with unit
        ("10 meters", "10 meters", "Distance: 10 meters"),
        # Tuple-style
        ("(29, 5)", "(29, 5)", "The intersection is at (29, 5)."),
        # Numeric in extracted is missing but full response has it
        (None, "42", "Long reasoning leading to \\boxed{42}."),
        # Thousands separator
        ("$1,234.56", "1234.56", "Total: $1,234.56"),
    ],
)
def test_compare_positive(extracted, expected, response):
    correct, reason = compare(extracted, expected, response)
    assert correct, f"expected match for ({extracted!r}, {expected!r}), got reason={reason}"


# Negative cases
@pytest.mark.parametrize(
    "extracted,expected,response",
    [
        ("41", "42", "Reasoning... 41 is the answer."),
        ("$6.95", "$6.94", "Total: $6.95"),
        # Pipe-joined: missing one component
        ("$18000, $24000", "$18000.00 | $18000.00 | $24000.00", "Got $18000 and $24000."),
        # Lettered: missing (b)
        ("(a) 1/3", "(a) 1/3, (b) 5/9", "Only (a) was solved: 1/3."),
        # Different number entirely
        ("100", "42", "Final: 100"),
    ],
)
def test_compare_negative(extracted, expected, response):
    correct, _ = compare(extracted, expected, response)
    assert not correct, f"unexpected match for ({extracted!r}, {expected!r})"


# String-only (no numbers) cases
def test_compare_string_only_match():
    correct, reason = compare("pencil", "pencil", "It's a pencil.")
    assert correct
    assert reason.startswith("substring_match")


def test_compare_string_only_mismatch():
    correct, _ = compare("pen", "pencil", "It's a pen.")
    assert not correct
