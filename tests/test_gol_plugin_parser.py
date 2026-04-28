"""Regression tests for gol_plugin/parser.py.

Cases mirror the failure modes surfaced by the v0.2.1 annotation report and the
3 confirmed responses from `results_gemma3_1b_20260426_172648.json.gz`:
- `final_answer_block` strategy (multi-line content under `**N. Output:**`).
- `markdown_bold` skips bolds where `:` follows the closing `**`.
- end-of-turn tokenizer artifacts pre-stripped.

Plus the original adversarial battery (boxed, inline label, last-line) to guard
against regression in the existing strategies.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GOL_EVAL_ROOT = Path("/Volumes/2TB/repos/gol_eval")

# `gol_plugin/parser.py` imports `from src.plugins.base import …`, which
# resolves against gol_eval's `src/` package. Mathbot also has a top-level
# `src/` (its CLI lives at `src.cli`), so when pytest's other test modules
# load mathbot's `src` first, Python caches that and gol_eval's `src.plugins`
# becomes unreachable. Bust the cache and re-resolve via gol_eval first.
if not GOL_EVAL_ROOT.is_dir():
    pytest.skip(
        f"gol_eval not found at {GOL_EVAL_ROOT}; gol_plugin tests require it",
        allow_module_level=True,
    )

# Stash mathbot's `src.*` modules, briefly swap in gol_eval's `src.plugins`,
# import the parser/evaluator (which bind ParsedAnswer/ResponseParser via the
# gol_eval-side import), then restore mathbot's modules so the other test
# files (test_cli, test_units, test_visual, …) keep loading mathbot's `src`.
_saved_src_modules = {
    k: v for k, v in sys.modules.items() if k == "src" or k.startswith("src.")
}
for k in _saved_src_modules:
    sys.modules.pop(k, None)
sys.path.insert(0, str(REPO_ROOT / "gol_plugin"))
sys.path.insert(0, str(GOL_EVAL_ROOT))
try:
    from parser import MathbotParser  # noqa: E402
    from evaluator import MathbotEvaluator  # noqa: E402  (used by one test)
finally:
    sys.path.remove(str(REPO_ROOT / "gol_plugin"))
    sys.path.remove(str(GOL_EVAL_ROOT))
    for k in [k for k in sys.modules if k == "src" or k.startswith("src.")]:
        sys.modules.pop(k, None)
    sys.modules.update(_saved_src_modules)


@pytest.fixture(scope="module")
def parser():
    return MathbotParser()


# ---------------------------------------------------------------------------
# Strategy selection (extracted text + winning strategy)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "label,response,expected_value,expected_strategy",
    [
        # ---- latex_boxed (existing, no regression) ----
        ("boxed_simple", r"Reasoning... \boxed{42}", "42", "latex_boxed"),
        (
            "boxed_last_wins",
            r"foo \boxed{1/2} bar \boxed{3/4}",
            "3/4",
            "latex_boxed",
        ),

        # ---- final_answer_block (NEW, dominant failure mode) ----
        (
            "block_wednesday_double_anchor",
            "**5. Final Answer:**\n\nWednesday.\n\n**6. Output:**\n\nWednesday.",
            "Wednesday.",
            "final_answer_block",
        ),
        (
            "block_jumps_real_response",
            (
                "Cross-multiply: 3 * 4 = 1 * x\n12 = x\n\n"
                "**6. Final Answer:**\n\nPoint A is 12 jumps from 0.\n\n"
                "**7.  Output:**\n\n12"
            ),
            "12",
            "final_answer_block",
        ),
        (
            "block_marble_list_with_eot",
            (
                "**Final Answer:**\n*   **Leslie:** 20 marbles\n"
                "*   **Robert:** 10 marbles\n*   **Jessica:** 17 marbles<turn|>"
            ),
            "*   **Leslie:** 20 marbles\n*   **Robert:** 10 marbles\n*   **Jessica:** 17 marbles",
            "final_answer_block",
        ),
        (
            "block_cascades_to_next_anchor",
            (
                "Reasoning…\n\n**Final Answer:**\n\n42\n\n"
                "**Verification:**\n\n42 is correct because 6*7=42."
            ),
            "42",
            "final_answer_block",
        ),
        (
            "block_terminated_by_horizontal_rule",
            "**Final Answer:**\n\n42\n\n---\n\nMore prose follows.",
            "42",
            "final_answer_block",
        ),
        (
            "block_handles_step_number_prefix",
            "**5. Final Answer:**\n\nIsosceles trapezoid",
            "Isosceles trapezoid",
            "final_answer_block",
        ),

        # ---- markdown_bold (Fix 2: colon-outside detection) ----
        (
            "bold_colon_outside_falls_to_label",
            "Reasoning... **Answer**: 3 jumps.",
            "3 jumps",
            "answer_label",
        ),
        (
            "bold_clean_value",
            "Step 1: x. Step 2: y. **27**",
            "27",
            "markdown_bold",
        ),

        # ---- answer_label (existing, inline) ----
        (
            "label_inline_currency",
            "Final answer: $6.94",
            "$6.94",
            "answer_label",
        ),
        (
            "label_inline_with_unit",
            "The answer is 720°",
            "720°",
            "answer_label",
        ),

        # ---- last_line fallback ----
        (
            "last_line_bare_answer",
            "Reasoning that has no anchor or bold.\nWednesday",
            "Wednesday",
            "last_line",
        ),

        # ---- pre-processing: EOT markers stripped before strategies run ----
        (
            "eot_marker_qwen",
            "**Final Answer:** 720°<|im_end|>",
            "720°",
            "answer_label",
        ),
        (
            "eot_marker_llama",
            "**Final Answer:**\n\n42<|eot_id|>",
            "42",
            "final_answer_block",
        ),

        # ---- empty / negative ----
        (
            "empty_response_returns_none",
            "",
            None,
            "empty",
        ),
        (
            "whitespace_only_returns_none",
            "   \n\n  ",
            None,
            "empty",
        ),
    ],
)
def test_parser_strategy(parser, label, response, expected_value, expected_strategy):
    parsed = parser.parse(response, task_params={})
    assert parsed.parse_strategy == expected_strategy, (
        f"{label}: expected strategy={expected_strategy!r}, "
        f"got {parsed.parse_strategy!r} with value={parsed.value!r}"
    )
    assert parsed.value == expected_value, (
        f"{label}: expected value={expected_value!r}, got {parsed.value!r}"
    )


# ---------------------------------------------------------------------------
# Real-response regression: 3 confirmed failures from gemma3_1b
# ---------------------------------------------------------------------------

REAL_GEMMA3_1B_42_0001_TAIL = (
    "on & Refinement:**\n\n"
    "While Wednesday is the obvious answer, let's verify this with a slightly "
    "more detailed analysis.  If we consider the cycle of days, Wednesday is "
    "the *next* day after Tuesday.\n\n"
    "**5. Final Answer:**\n\n"
    "Wednesday.\n\n"
    "**6.  Justification (Brief):**  The question asks for the *next* day "
    "*after* Tuesday.  Wednesday is the logical and straightforward next day.\n\n"
    "**7.  Output:**\n\n"
    "Wednesday."
)

REAL_GEMMA3_1B_42_0003_TAIL = (
    " Cross-multiply: 3 * 4 = 1 * x\n*   12 = x\n\nTherefore, x = 12\n\n"
    "**5. Verification:**\n\n"
    "To confirm our answer, let's consider the total length of the number line.  "
    "Since there are four equal parts, each part represents 1/4 of the total "
    "length.  The total length is 1.  Therefore, the total length of the number "
    "line is 4 * 1/4 = 1.\n\n"
    "**6. Final Answer:**\n\n"
    "Point A is 12 jumps from 0.\n\n"
    "**7.  Output:**\n\n"
    "12"
)


def test_real_42_0001_picks_last_anchor_block(parser):
    """The model's last anchor (`**7. Output:**`) wins; content is `Wednesday.`."""
    parsed = parser.parse(REAL_GEMMA3_1B_42_0001_TAIL, task_params={})
    assert parsed.parse_strategy == "final_answer_block"
    assert parsed.value == "Wednesday."


def test_real_42_0003_picks_last_anchor_block(parser):
    """Last anchor is `**7. Output:**`, content is the bare `12`."""
    parsed = parser.parse(REAL_GEMMA3_1B_42_0003_TAIL, task_params={})
    assert parsed.parse_strategy == "final_answer_block"
    assert parsed.value == "12"


# ---------------------------------------------------------------------------
# End-to-end with the evaluator: the parser fix makes evaluation correct
# ---------------------------------------------------------------------------

def test_real_42_0001_evaluator_correct():
    """With the new parser, model's `Wednesday` matches expected `Wednesday`."""
    parser = MathbotParser()
    evaluator = MathbotEvaluator()
    parsed = parser.parse(REAL_GEMMA3_1B_42_0001_TAIL, {"answer_shape": "word"})
    result = evaluator.evaluate(parsed, "Wednesday", {"answer_shape": "word"})
    assert result.correct
    assert result.match_type == "substring_match"
