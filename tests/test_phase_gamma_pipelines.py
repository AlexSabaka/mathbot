"""Phase γ.2 rendering pipeline tests (B.1–B.4, B.6 CLI).

Exercises the four output pipelines against a stable problem-dict
fixture and the CLI multi-format dispatcher. PDF (B.4) is tested
indirectly: the rendering pipeline up to ``render_pdf`` is exercised
without invoking tectonic so the suite still passes on machines
without the binary; tectonic-specific behaviour gets a separate
skip-on-missing test.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from src.cli import cli
from src.render import (
    MathExpr,
    latex_escape,
    render_latex,
    render_markdown,
    render_pdf,
    render_text,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def basic_problem():
    """Problem dict with body + numeric answer; no visual."""
    return {
        'test_id': 'math_k7_easy_addition_01',
        'task_type': 'multi_step_math',
        'problem': "Maria buys 3 apples for $1.50 each. How much did she pay?",
        'task_params': {'expected_answer': '$4.50'},
    }


@pytest.fixture
def visual_problem():
    """Problem dict with body + visual + symbolic answer."""
    return {
        'test_id': 'math_k12_rlc_critical_damping__hard',
        'task_type': 'multi_step_math',
        'problem': "Solve the RLC ODE for q(t).",
        'task_params': {'expected_answer': '(t + 1)*exp(-t)'},
        'visual': {
            'format': 'svg',
            'source': '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="white"/></svg>',
            'alt_text': 'RLC schematic, R = 2 Ohm, L = 1 H, C = 1 F.',
        },
    }


@pytest.fixture
def special_chars_problem():
    """Body with LaTeX-special characters that must be escaped."""
    return {
        'test_id': 'math_k4_easy_money',
        'problem': "John has $5 and 50% of it is in his wallet & pocket.",
        'task_params': {'expected_answer': '$2.50'},
    }


# ---------------------------------------------------------------------------
# B.1 text
# ---------------------------------------------------------------------------

class TestB1RenderText:
    def test_basic_problem(self, basic_problem):
        out = render_text(basic_problem)
        assert basic_problem['problem'] in out
        assert "Answer: $4.50" in out

    def test_no_answer_when_disabled(self, basic_problem):
        out = render_text(basic_problem, show_answer=False)
        assert "Answer" not in out
        assert basic_problem['problem'] in out

    def test_visual_alt_as_placeholder(self, visual_problem):
        out = render_text(visual_problem)
        assert "[Figure: RLC schematic, R = 2 Ohm, L = 1 H, C = 1 F.]" in out

    def test_no_figure_marker_when_no_visual(self, basic_problem):
        out = render_text(basic_problem)
        assert "[Figure" not in out

    def test_symbolic_answer_passthrough(self, visual_problem):
        out = render_text(visual_problem)
        assert "(t + 1)*exp(-t)" in out

    def test_no_unicode_lift_for_powers(self):
        # γ.2 review: the Unicode lift (``**2`` → ``²``) diverges from
        # the SVG composite, which splices the answer string verbatim.
        # All formats agree on the formatter's plain string until the
        # KaTeX-based typesetting pipeline lands.
        problem = {
            'problem': 'Find x.',
            'task_params': {'expected_answer': 'x**2 + 1'},
        }
        out = render_text(problem)
        assert "Answer: x**2 + 1" in out
        assert "x²" not in out

    def test_numeric_answer_passthrough(self):
        problem = {
            'problem': 'After how many minutes?',
            'task_params': {'expected_answer': '21.64'},
        }
        out = render_text(problem)
        assert "Answer: 21.64" in out
        assert "21.6400000000000" not in out


# ---------------------------------------------------------------------------
# B.2 markdown
# ---------------------------------------------------------------------------

class TestB2RenderMarkdown:
    def test_basic_problem(self, basic_problem):
        out = render_markdown(basic_problem)
        assert basic_problem['problem'] in out
        assert "**Answer:** $4.50" in out

    def test_data_uri_for_visual(self, visual_problem):
        out = render_markdown(visual_problem, embed_images=True)
        assert "data:image/svg+xml;base64," in out
        # Alt text in the markdown link
        assert "RLC schematic" in out

    def test_sidecar_image_path(self, visual_problem):
        out = render_markdown(
            visual_problem, embed_images=False, image_path=Path("fig.svg"),
        )
        assert "(fig.svg)" in out
        assert "data:image" not in out

    def test_visual_dropped_when_no_path_no_embed(self, visual_problem):
        # No data URI, no path → the visual is silently omitted.
        out = render_markdown(visual_problem, embed_images=False)
        assert "data:image" not in out
        assert ".svg" not in out

    def test_symbolic_answer_plain_text(self, visual_problem):
        # γ.2 review fix: until KaTeX integration lands, all output
        # formats use the formatter's canonical plain-string answer.
        # Wrapping in $...$ would diverge from the SVG composite path.
        out = render_markdown(visual_problem)
        assert "**Answer:** (t + 1)*exp(-t)" in out
        # No LaTeX-wrapped form
        assert r"\left(t + 1\right)" not in out

    def test_numeric_answer_plain_text(self, basic_problem):
        # `$4.50` would render badly inside $...$ (italic 4 . 50)
        out = render_markdown(basic_problem)
        assert "**Answer:** $4.50" in out

    def test_no_answer_when_disabled(self, basic_problem):
        out = render_markdown(basic_problem, show_answer=False)
        assert "Answer" not in out

    def test_alt_text_brackets_escaped(self):
        problem = {
            'problem': 'P.',
            'task_params': {'expected_answer': '5'},
            'visual': {
                'format': 'svg',
                'source': '<svg/>',
                'alt_text': 'A figure with [brackets] in the name',
            },
        }
        out = render_markdown(problem, embed_images=True)
        # `]` inside markdown alt syntax must be escaped
        assert r"[brackets\]" in out


# ---------------------------------------------------------------------------
# B.3 LaTeX
# ---------------------------------------------------------------------------

class TestB3RenderLatex:
    def test_full_document_has_preamble(self, basic_problem):
        out = render_latex(basic_problem)
        assert r"\documentclass" in out
        assert r"\begin{document}" in out
        assert r"\end{document}" in out

    def test_fragment_omits_preamble(self, basic_problem):
        out = render_latex(basic_problem, fragment=True)
        assert r"\documentclass" not in out
        assert r"\begin{document}" not in out
        # Body still present (the $ in "$1.50" gets escaped to \$ — check
        # for the escaped form, which is what a reader sees in the .tex).
        assert "Maria buys 3 apples" in out
        assert r"\$1.50" in out

    def test_special_chars_escaped(self, special_chars_problem):
        out = render_latex(special_chars_problem, fragment=True)
        # The body has $5, 50%, and & — all of which must be escaped.
        assert r"\$5" in out
        assert r"50\%" in out
        assert r" \& " in out

    def test_underscore_escaped(self):
        # `T_ambient` in the body should escape to `T\_ambient`.
        problem = {
            'problem': 'dT/dt = -k(T - T_ambient).',
            'task_params': {'expected_answer': '5'},
        }
        out = render_latex(problem, fragment=True)
        assert r"T\_ambient" in out

    def test_inline_math_passthrough(self):
        # Author-supplied \(...\) math must NOT be escaped.
        problem = {
            'problem': r"Find x given \(x^2 + 1 = 0\). Compute.",
            'task_params': {'expected_answer': '5'},
        }
        out = render_latex(problem, fragment=True)
        # The math span survives untouched
        assert r"\(x^2 + 1 = 0\)" in out

    def test_image_path_emits_includegraphics(self, visual_problem):
        out = render_latex(visual_problem, fragment=True, image_path="fig.png")
        assert r"\includegraphics" in out
        assert "fig.png" in out
        assert r"\caption*" in out

    def test_no_image_path_omits_figure(self, visual_problem):
        out = render_latex(visual_problem, fragment=True)
        assert r"\includegraphics" not in out
        assert r"\begin{figure}" not in out

    def test_symbolic_answer_plain_text(self, visual_problem):
        # γ.2 review fix: plain text everywhere, escaped for LaTeX.
        # The SVG-composite path can't typeset math today (KaTeX is
        # γ.3+), so the .tex output stays in lockstep with it.
        out = render_latex(visual_problem, fragment=True)
        assert r"(t + 1)*exp(-t)" in out
        assert r"\left(t + 1\right)" not in out

    def test_numeric_answer_escaped_not_in_math(self, basic_problem):
        out = render_latex(basic_problem, fragment=True)
        # `$4.50` should be escaped to `\$4.50`, NOT in \(...\)
        assert r"\$4.50" in out
        assert r"\(\$4.50\)" not in out


class TestB3LatexEscape:
    def test_no_escape_when_no_specials(self):
        assert latex_escape("Hello world 123") == "Hello world 123"

    def test_dollar_escape(self):
        assert latex_escape("$5") == r"\$5"

    def test_percent_escape(self):
        assert latex_escape("50%") == r"50\%"

    def test_ampersand_escape(self):
        assert latex_escape("X & Y") == r"X \& Y"

    def test_underscore_escape(self):
        assert latex_escape("T_ambient") == r"T\_ambient"

    def test_backslash_escape(self):
        assert latex_escape(r"a\b") == r"a\textbackslash{}b"

    def test_braces_escape(self):
        assert latex_escape("{x}") == r"\{x\}"

    def test_empty_string(self):
        assert latex_escape("") == ""


# ---------------------------------------------------------------------------
# B.4 PDF
# ---------------------------------------------------------------------------

class TestB4RenderPdf:
    def test_no_tectonic_raises_clear_error(self):
        if shutil.which("tectonic") is not None:
            pytest.skip("tectonic is installed; this test verifies the missing-binary path")
        with pytest.raises(RuntimeError, match="tectonic binary not found"):
            render_pdf({'problem': 'P', 'task_params': {'expected_answer': '5'}})

    @pytest.mark.skipif(
        shutil.which("tectonic") is None,
        reason="tectonic not installed",
    )
    def test_compile_smoke(self, basic_problem):
        # Only runs when tectonic is on PATH; verifies the LaTeX
        # compiles end-to-end and we get PDF bytes.
        pdf_bytes = render_pdf(basic_problem)
        assert pdf_bytes.startswith(b"%PDF-")
        # PDFs always end with %%EOF, possibly with trailing newline
        assert b"%%EOF" in pdf_bytes[-50:]


# ---------------------------------------------------------------------------
# B.6 CLI
# ---------------------------------------------------------------------------

@pytest.fixture
def tiny_template(tmp_path):
    """Drop a minimal template into tmp_path/arithmetic/ and return its path."""
    topic_dir = tmp_path / "arithmetic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        'metadata': {
            'id': 'k7_easy_addition_smoke',
            'version': '1.0.0',
            'author': 't',
            'created': '2026-04-29',
            'grade': 7,
            'topic': 'arithmetic.addition',
            'family': 'addition',
            'difficulty': 'easy',
            'steps': 1,
        },
        'variables': {
            'a': {'type': 'integer', 'min': 1, 'max': 1},
            'b': {'type': 'integer', 'min': 2, 'max': 2},
            'Answer': {'type': 'integer'},
        },
        'template': "What is {{a}} + {{b}}?",
        'solution': "Answer = a + b",
        'tests': [{'seed': 1, 'expected': {'answer': '3'}}],
    }
    path = topic_dir / "k7_easy_addition_smoke.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


class TestB6CliSingleFormat:
    def test_markdown_output(self, tiny_template):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '-o', 'markdown',
        ])
        assert result.exit_code == 0, result.output
        assert "**Answer:**" in result.output

    def test_latex_fragment(self, tiny_template):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '-o', 'latex', '--fragment',
        ])
        assert result.exit_code == 0, result.output
        assert r"\section*{Problem}" in result.output
        assert r"\documentclass" not in result.output

    def test_latex_full(self, tiny_template):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '-o', 'latex',
        ])
        assert result.exit_code == 0, result.output
        assert r"\documentclass" in result.output
        assert r"\end{document}" in result.output

    def test_pdf_requires_file(self, tiny_template):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1', '-o', 'pdf',
        ])
        assert result.exit_code != 0
        assert "requires --file" in result.output


class TestB6CliMultiFormat:
    def test_text_md_latex_to_dir(self, tiny_template, tmp_path):
        out_dir = tmp_path / "out"
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '--formats', 'text,markdown,latex',
            '--output-dir', str(out_dir),
        ])
        assert result.exit_code == 0, result.output
        assert (out_dir / "k7_easy_addition_smoke.txt").exists()
        assert (out_dir / "k7_easy_addition_smoke.md").exists()
        assert (out_dir / "k7_easy_addition_smoke.tex").exists()

    def test_requires_output_dir(self, tiny_template):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '--formats', 'text,markdown',
        ])
        assert result.exit_code != 0
        assert "requires --output-dir" in result.output

    def test_invalid_format_rejected_with_listing(self, tiny_template, tmp_path):
        out_dir = tmp_path / "out"
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '--formats', 'text,xml,markdown',
            '--output-dir', str(out_dir),
        ])
        assert result.exit_code != 0
        assert "unknown formats" in result.output
        assert "xml" in result.output

    def test_stem_strips_math_prefix(self, tiny_template, tmp_path):
        # test_id is "math_<id>"; stem should be just "<id>".
        out_dir = tmp_path / "out"
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', '--input', str(tiny_template), '-s', '1',
            '--formats', 'text',
            '--output-dir', str(out_dir),
        ])
        assert result.exit_code == 0, result.output
        # No file with `math_` prefix
        files = list(out_dir.iterdir())
        assert len(files) == 1
        assert not files[0].name.startswith("math_")
