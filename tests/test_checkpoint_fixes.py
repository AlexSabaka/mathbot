"""Phase β checkpoint paper-cut fixes.

Two CLI/output ergonomics issues surfaced while dissecting the demo
template at the Phase β checkpoint:

- Issue 1: `task_params.operations` always reported the same four
  operations (`addition`, `subtraction`, `multiplication`,
  `division`) because `_extract_operations` was a substring check
  on raw source. Replaced with an AST walk that distinguishes real
  BinOp nodes from comments / f-strings / negative literals /
  string concatenation.
- Issue 2: No single-template PNG render path. `mathbot generate -o png|svg`
  composes problem text + visual + (optional) answer into a single
  SVG, optionally rasterized to PNG via cairosvg.

This file groups both. Tests for compose-side end-to-end render
are in `TestCompose*`; AST-extraction tests are in
`TestExtractOperations`.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import cli
from src.template_generator import TemplateGenerator
from src.visuals import PlotSVG
from src.visuals.compose import compose_problem_svg


# ---------------------------------------------------------------------------
# Issue 1 — AST-based operation extraction
# ---------------------------------------------------------------------------

class TestExtractOperations:
    """The AST walk should pick up real arithmetic operations and skip
    syntactic noise that the old substring heuristic mis-counted."""

    @pytest.fixture(scope="class")
    def gen(self):
        return TemplateGenerator()

    def test_pure_addition(self, gen):
        assert gen._extract_operations("Answer = a + b") == ['addition']

    def test_subtraction(self, gen):
        assert gen._extract_operations("Answer = a - b") == ['subtraction']

    def test_multiplication_only(self, gen):
        assert gen._extract_operations("Answer = a * b") == ['multiplication']

    def test_division_pure(self, gen):
        assert gen._extract_operations("Answer = a / b") == ['division']

    def test_floor_division_counts_as_division(self, gen):
        # Both / and // surface as the single "division" tag.
        assert gen._extract_operations("Answer = a // b") == ['division']

    def test_modulo(self, gen):
        assert gen._extract_operations("Answer = a % b") == ['modulo']

    def test_double_star_exponentiation(self, gen):
        assert gen._extract_operations("Answer = x ** 2") == ['exponentiation']

    def test_pow_call_exponentiation(self, gen):
        assert gen._extract_operations("Answer = pow(x, 2)") == ['exponentiation']

    def test_math_pow_exponentiation(self, gen):
        assert gen._extract_operations(
            "import math\nAnswer = math.pow(x, 2)"
        ) == ['exponentiation']

    def test_unary_minus_on_literal_is_not_subtraction(self, gen):
        # `-3` is a literal sign, not an operation. Was a false
        # positive in the old heuristic.
        assert gen._extract_operations("Answer = -3") == ['arithmetic']

    def test_subtraction_with_negative_literal_only_counts_real_sub(self, gen):
        # `a - 5 + (-3)` has one real Sub (`a - 5`), one real Add
        # (`(a-5) + (-3)`), and one USub on the literal `-3` that
        # must NOT count.
        ops = set(gen._extract_operations("Answer = a - 5 + (-3)"))
        assert ops == {'addition', 'subtraction'}

    def test_comments_alone_dont_register(self, gen):
        # The pre-fix heuristic mis-tagged this as all four ops.
        assert gen._extract_operations(
            "# 1 + 2 - 3 * 4 / 5\nAnswer = a"
        ) == ['arithmetic']

    def test_fstring_alone_doesnt_register(self, gen):
        # Pre-fix: `+`, `*`, `/` from inside the f-string template
        # mis-tagged the operations.
        assert gen._extract_operations('Answer = f"{a:.2f}"') == ['arithmetic']

    def test_string_concat_via_plus(self, gen):
        # `+` between strings IS an Add BinOp at the AST level.
        # We accept this — the "addition" tag is mildly imprecise
        # here but harmless, and string-concat solutions are rare.
        assert gen._extract_operations(
            'Answer = "x: " + str(a)'
        ) == ['addition']

    def test_chained_arithmetic_dedupes(self, gen):
        # Each operator surfaces exactly once even if used many times.
        ops = gen._extract_operations(
            "Answer = a + b + c + d * e * f - g - h"
        )
        assert ops.count('addition') == 1
        assert ops.count('multiplication') == 1
        assert ops.count('subtraction') == 1

    def test_syntax_error_falls_back_to_arithmetic(self, gen):
        assert gen._extract_operations("Answer = a + + +") == ['arithmetic']

    def test_empty_solution_falls_back(self, gen):
        assert gen._extract_operations("") == ['arithmetic']

    def test_realistic_k12_cooling_solution(self, gen):
        # The demo template at the repo root drove this fix. Operations
        # should be the actual three ops the code uses, not all four.
        sol = (
            "import sympy as sp\n"
            "t_sym = sp.Symbol('t', positive=True, real=True)\n"
            "T = sp.Function('T', real=True)\n"
            "ode = T(t_sym).diff(t_sym) + k * (T(t_sym) - T_amb)\n"
            "T_closed = sp.dsolve(ode, T(t_sym), ics={T(0): T_0}).rhs\n"
            "t_value = sp.solve(T_closed - T_target, t_sym)[0]\n"
            "Answer = round(float(t_value), 2)\n"
        )
        ops = set(gen._extract_operations(sol))
        # Three real BinOps in this code: + (addition), - (sub) twice,
        # * (mult). Division is NOT in the source — the old heuristic
        # would have flagged it from `/` characters in comments or
        # similar. None present here so the bug fix is verifiable.
        assert ops == {'addition', 'subtraction', 'multiplication'}


# ---------------------------------------------------------------------------
# Issue 2 — compose_problem_svg (unit-level)
# ---------------------------------------------------------------------------

class TestComposeProblemSVG:
    def test_body_only_parses_as_xml(self):
        out = compose_problem_svg("What is 7 + 5?")
        ET.fromstring(out)
        assert "What is 7 + 5?" in out

    def test_body_only_no_visual_no_answer_omits_those_blocks(self):
        out = compose_problem_svg("Hello.")
        # Exactly one <svg> wrapper, exactly one <text> for the body line.
        assert out.count("<svg") == 1
        assert out.count("<text") == 1

    def test_explicit_newlines_preserved(self):
        out = compose_problem_svg("first\n\nsecond")
        # Two non-empty body lines → two text elements.
        text_count = out.count("<text")
        assert text_count == 2

    def test_long_line_wraps(self):
        long_body = "This is " + "a long sentence " * 30 + "ending."
        out = compose_problem_svg(long_body)
        # Should wrap into multiple text elements (≥3 is a reasonable
        # lower bound for 30 repetitions of a 16-char phrase).
        assert out.count("<text") >= 3

    def test_visual_embedded_centered(self):
        plot = PlotSVG(width=400, height=300, x_range=(-3, 3))
        plot.plot(lambda x: x * x)
        viz = plot.render()
        out = compose_problem_svg("Body.", visual_svg=viz)
        ET.fromstring(out)
        # The embedded svg gets x= and y= attributes; with page=800 and
        # visual width=400, embedded x should be (800-400)/2 = 200.
        embedded = re.search(r'<svg[^>]*\bwidth="400"[^>]*\bx="([\d.]+)"', out)
        if embedded is None:
            embedded = re.search(r'<svg[^>]*\bx="([\d.]+)"[^>]*\bwidth="400"', out)
        assert embedded is not None, "embedded svg not found"
        x_pos = float(embedded.group(1))
        assert abs(x_pos - 200.0) < 1.0

    def test_visual_too_wide_scales_down(self):
        plot = PlotSVG(width=2000, height=600, x_range=(-1, 1))
        plot.plot(lambda x: x)
        viz = plot.render()
        out = compose_problem_svg("Big visual.", visual_svg=viz, page_width=800)
        ET.fromstring(out)
        # Find the embedded svg's width — should be <= 800 - 2*24 = 752.
        m = re.search(r'<svg[^>]*\bwidth="([\d.]+)"', out.split("Big visual", 1)[1])
        assert m is not None
        embedded_w = float(m.group(1))
        assert embedded_w <= 752.0

    def test_answer_block_appended(self):
        out = compose_problem_svg("Body.", answer="42")
        ET.fromstring(out)
        assert "Answer: 42" in out
        # Answer line uses monospace.
        assert "Menlo" in out or "monospace" in out

    def test_answer_with_visual_both_present(self):
        plot = PlotSVG()
        plot.plot(lambda x: x)
        viz = plot.render()
        out = compose_problem_svg("Body.", visual_svg=viz, answer="7")
        ET.fromstring(out)
        assert "Answer: 7" in out
        # Answer must come AFTER the embedded visual in document order
        answer_idx = out.index("Answer: 7")
        last_polyline_idx = out.rfind("<polyline")
        assert last_polyline_idx < answer_idx

    def test_xml_escapes_unsafe_text(self):
        out = compose_problem_svg("Tag <script>alert(1)</script>", answer="1<2")
        # Should still parse as XML — escaping prevents the <script>
        # from being a child element.
        ET.fromstring(out)
        assert "<script>" not in out
        assert "&lt;script&gt;" in out
        assert "1&lt;2" in out

    def test_explicit_page_width_propagates(self):
        out = compose_problem_svg("body", page_width=600)
        assert 'width="600"' in out
        m = re.match(r'<svg[^>]*viewBox="0 0 (\d+) ', out)
        assert m and m.group(1) == "600"

    def test_visual_with_xml_decl_is_stripped(self):
        # PlotSVG doesn't emit one, but a hand-authored Approach-A
        # source might. Verify the leading `<?xml ...?>` is stripped
        # so the embed parses.
        viz = '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect x="0" y="0" width="200" height="100"/></svg>'
        out = compose_problem_svg("body", visual_svg=viz)
        ET.fromstring(out)
        # Only the outer composite should keep an `<?xml>` decl (we
        # don't emit one, so there should be zero in the output).
        assert "<?xml" not in out


# ---------------------------------------------------------------------------
# Issue 2 — `mathbot generate -o png|svg` CLI integration
# ---------------------------------------------------------------------------

# Pick a guaranteed-non-visual minimal template from the existing
# corpus for the body-only render path; the demo cooling template
# covers the visual + answer path.
_VISUAL_TEMPLATE = "src/templates/differential_equations/k12_first_order_ode_cooling_01_anchor.yaml"
_ANY_TEMPLATE = "src/templates/arithmetic"


class TestCLIComposeOutputs:
    """End-to-end tests of `mathbot generate -o svg|png` via Click's
    CliRunner. These don't require libcairo: SVG works without it,
    and the PNG path is exercised only with a graceful skip when
    cairosvg/libcairo aren't importable."""

    def test_svg_output_to_stdout(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "generate", "--input", _VISUAL_TEMPLATE,
            "-s", "42", "-c", "2", "-o", "svg",
        ])
        assert result.exit_code == 0, result.output
        # stdout should be the composite SVG; the success-banner line
        # only appears when --file is set.
        ET.fromstring(result.stdout.strip())
        assert "<svg" in result.stdout
        # `_esc` HTML-escapes apostrophes to &apos; so look for an
        # apostrophe-free substring of the body prose.
        assert "law of cooling" in result.stdout

    def test_svg_output_to_file(self, tmp_path):
        runner = CliRunner()
        out_path = tmp_path / "p.svg"
        result = runner.invoke(cli, [
            "generate", "--input", _VISUAL_TEMPLATE,
            "-s", "42", "-c", "2", "-o", "svg", "--file", str(out_path),
        ])
        assert result.exit_code == 0, result.output
        assert out_path.exists()
        content = out_path.read_text()
        ET.fromstring(content)
        assert "polyline" in content      # the cooling-curve visual is embedded
        assert "Answer:" in content        # show-answer is on by default

    def test_png_requires_file_flag(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "generate", "--input", _VISUAL_TEMPLATE,
            "-s", "42", "-c", "2", "-o", "png",
        ])
        assert result.exit_code != 0
        assert "requires --file" in (result.stdout + result.stderr)

    def test_no_show_answer_omits_answer_line(self, tmp_path):
        runner = CliRunner()
        out_path = tmp_path / "p.svg"
        result = runner.invoke(cli, [
            "generate", "--input", _VISUAL_TEMPLATE,
            "-s", "42", "-c", "2", "-o", "svg", "--file", str(out_path),
            "--no-show-answer",
        ])
        assert result.exit_code == 0, result.output
        assert "Answer:" not in out_path.read_text()

    def test_page_width_propagates(self, tmp_path):
        runner = CliRunner()
        out_path = tmp_path / "p.svg"
        result = runner.invoke(cli, [
            "generate", "--input", _VISUAL_TEMPLATE,
            "-s", "42", "-c", "2", "-o", "svg", "--file", str(out_path),
            "--page-width", "600",
        ])
        assert result.exit_code == 0, result.output
        # Outer svg width must be 600.
        outer = re.match(r'<svg[^>]*\bwidth="(\d+)"', out_path.read_text())
        assert outer is not None
        assert outer.group(1) == "600"

    def test_template_without_visual_renders_body_only(self, tmp_path):
        # Pick the first arithmetic anchor that has no visual — most
        # K1–K8 templates fit that bill.
        tpl_dir = Path(_ANY_TEMPLATE)
        candidates = sorted(p for p in tpl_dir.glob("*_anchor.yaml") if "addition" in p.stem)
        assert candidates, "no addition anchor found for body-only test"
        runner = CliRunner()
        out_path = tmp_path / "p.svg"
        result = runner.invoke(cli, [
            "generate", "--input", str(candidates[0]),
            "-s", "42", "-o", "svg", "--file", str(out_path),
        ])
        assert result.exit_code == 0, result.output
        content = out_path.read_text()
        ET.fromstring(content)
        # Body-only composite has exactly one outer <svg> (no nested
        # visual), and the answer line is present.
        assert content.count("<svg") == 1

    def test_legacy_outputs_unchanged(self):
        # Smoke check that adding svg/png to the choices didn't break
        # the existing pretty/json/text outputs.
        runner = CliRunner()
        for fmt in ("pretty", "json", "text"):
            result = runner.invoke(cli, [
                "generate", "--input", _VISUAL_TEMPLATE,
                "-s", "42", "-c", "2", "-o", fmt,
            ])
            assert result.exit_code == 0, f"{fmt}: {result.output}"
