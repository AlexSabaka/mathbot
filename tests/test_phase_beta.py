"""Phase β (H1–H4) infrastructure tests.

Covers the visual + structural-tag + noop + direction work landed
between Phase α (foundation) and the P0 mass-build cycle:

- H2: `structural_tags:` schema array + closed enum (T1–T17).
- H4: `direction:` schema field (`forward` / `inverse`).
- H3: `noop_clauses:` schema field + Jinja-rendered injection through
  `inject_noop=True` + `noop_clauses_no_slot` lint rule.
- H1: `src/visuals/` builder package (PlotSVG / TreeSVG / MarkovSVG)
  + `visual.format = "python"` end-to-end pipeline with
  output-format normalisation to `svg`.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import yaml

from src.audit import lint_path
from src.template_generator import TemplateGenerator
from src.visuals import MarkovSVG, PlotSVG, SVGBuilder, TreeSVG
from src.yaml_loader import YAMLLoader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_template(
    tmp_path: Path,
    *,
    metadata_overrides=None,
    body: str = "{{a}} + {{b}} = ?",
    solution: str = "Answer = a + b",
    visual=None,
    expected_answer: str = "3",
    variables=None,
):
    """Drop a tiny addition template into tmp_path/arithmetic/.

    Defaults yield a=1, b=2 → Answer=3 deterministically so the
    embedded fixture matches without seed-tuning.
    """
    topic_dir = tmp_path / "arithmetic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": "k9_easy_addition_01",
        "version": "1.0.0",
        "author": "t",
        "created": "2026-04-28",
        "grade": 9,
        "topic": "arithmetic.addition",
        "family": "addition",
        "difficulty": "easy",
        "steps": 1,
    }
    if metadata_overrides:
        metadata.update(metadata_overrides)
    payload = {
        "metadata": metadata,
        "variables": variables or {
            "a": {"type": "integer", "min": 1, "max": 1},
            "b": {"type": "integer", "min": 2, "max": 2},
            "Answer": {"type": "integer"},
        },
        "template": body,
        "solution": solution,
        "tests": [{"seed": 1, "expected": {"answer": expected_answer}}],
    }
    if visual is not None:
        payload["visual"] = visual
    path = topic_dir / f"{metadata['id']}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


# ---------------------------------------------------------------------------
# H2 — structural_tags
# ---------------------------------------------------------------------------

class TestH2StructuralTags:
    def test_default_empty(self, tmp_path):
        path = _write_template(tmp_path)
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None
        assert tpl.structural_tags == []

    def test_t13_t17_loaded(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "structural_tags": [
                "T13_symbolic_chain",
                "T15_method_selection",
                "T17_inverse_query",
            ],
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert "T13_symbolic_chain" in tpl.structural_tags
        assert "T15_method_selection" in tpl.structural_tags
        assert "T17_inverse_query" in tpl.structural_tags

    def test_original_t1_t12_loaded(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "structural_tags": ["running_total", "compound_growth"],
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.structural_tags == ["running_total", "compound_growth"]

    def test_invalid_tag_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "structural_tags": ["T99_made_up"],
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("structural_tags" in e for e in loader.errors)

    def test_non_list_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "structural_tags": "T13_symbolic_chain",  # bare string, not list
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("structural_tags" in e for e in loader.errors)


# ---------------------------------------------------------------------------
# H4 — direction
# ---------------------------------------------------------------------------

class TestH4Direction:
    @pytest.mark.parametrize("direction", ["forward", "inverse"])
    def test_valid_direction_loads(self, tmp_path, direction):
        path = _write_template(tmp_path, metadata_overrides={"direction": direction})
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.direction == direction

    def test_default_none(self, tmp_path):
        path = _write_template(tmp_path)
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl.direction is None

    def test_invalid_direction_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={"direction": "sideways"})
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("direction" in e for e in loader.errors)


# ---------------------------------------------------------------------------
# H3 — noop_clauses
# ---------------------------------------------------------------------------

class TestH3NoopClauses:
    def _setup_noop_template(self, tmp_path: Path, with_slot: bool = True):
        body = (
            "{{ noop_clause }} {{a}} + {{b}} = ?"
            if with_slot else "{{a}} + {{b}} = ?"
        )
        return _write_template(tmp_path, body=body, metadata_overrides={
            "noop_clauses": [
                "Earlier in the day, {{a}} was a popular topic.",
                "Note that {{b}} is divisible by 1.",
                "Pay no attention to the value 42.",
            ],
        })

    def test_default_render_unchanged_when_inject_off(self, tmp_path):
        self._setup_noop_template(tmp_path)
        gen = TemplateGenerator(templates_dir=tmp_path)
        p = gen.generate(seed=1, inject_noop=False)
        assert p["problem"] == "1 + 2 = ?"

    def test_injection_inserts_a_clause(self, tmp_path):
        self._setup_noop_template(tmp_path)
        gen = TemplateGenerator(templates_dir=tmp_path)
        p = gen.generate(seed=1, inject_noop=True)
        # The body must now be longer than the no-noop base render.
        assert len(p["problem"]) > len("1 + 2 = ?")
        # And the chosen clause must appear in the body.
        assert any(
            phrase in p["problem"]
            for phrase in ("popular topic", "divisible by 1", "value 42")
        )

    def test_injection_is_deterministic_per_seed(self, tmp_path):
        self._setup_noop_template(tmp_path)
        gen = TemplateGenerator(templates_dir=tmp_path)
        a = gen.generate(seed=42, inject_noop=True)["problem"]
        b = gen.generate(seed=42, inject_noop=True)["problem"]
        assert a == b

    def test_lint_errors_when_pool_set_without_slot(self, tmp_path):
        self._setup_noop_template(tmp_path, with_slot=False)
        findings = lint_path(tmp_path)
        no_slot = [f for f in findings if f.rule == "noop_clauses_no_slot"]
        assert len(no_slot) == 1
        assert no_slot[0].severity == "error"

    def test_lint_silent_when_pool_set_with_slot(self, tmp_path):
        self._setup_noop_template(tmp_path, with_slot=True)
        findings = lint_path(tmp_path)
        no_slot = [f for f in findings if f.rule == "noop_clauses_no_slot"]
        assert no_slot == []

    def test_lint_silent_when_no_pool(self, tmp_path):
        # No noop_clauses, no slot, no finding — most templates today.
        _write_template(tmp_path)
        findings = lint_path(tmp_path)
        no_slot = [f for f in findings if f.rule == "noop_clauses_no_slot"]
        assert no_slot == []


# ---------------------------------------------------------------------------
# H1 — visual builders
# ---------------------------------------------------------------------------

class TestH1PlotSVG:
    def test_basic_render_is_valid_xml(self):
        plot = PlotSVG(x_range=(-3, 3), title="parabola")
        plot.plot(lambda x: x * x, label="f")
        plot.point(0, 0, label="min")
        svg = plot.render()
        ET.fromstring(svg)  # raises if malformed
        assert "polyline" in svg
        assert "parabola" in svg
        assert "min" in svg

    def test_singularity_splits_polyline(self):
        # 1/x with bounded y_range — values near 0 leave the plot box,
        # forcing a polyline split rather than a spurious vertical line.
        plot = PlotSVG(x_range=(-2, 2), y_range=(-3, 3))
        plot.plot(lambda x: 1.0 / x if x != 0 else float("inf"))
        svg = plot.render()
        ET.fromstring(svg)
        assert svg.count("<polyline") >= 2

    def test_domain_break_splits_polyline(self):
        # sqrt raises for x<0; sampler should drop those points so the
        # polyline only covers the right half.
        import math

        plot = PlotSVG(x_range=(-2, 2))
        plot.plot(lambda x: math.sqrt(x))
        svg = plot.render()
        ET.fromstring(svg)
        # All x<0 samples become None → exactly one polyline (right half).
        assert svg.count("<polyline") == 1

    def test_horizontal_line(self):
        plot = PlotSVG(x_range=(0, 10), y_range=(-1, 1))
        plot.horizontal_line(0.5, label="threshold")
        svg = plot.render()
        ET.fromstring(svg)
        assert "threshold" in svg
        # The dashed style is the asymptote signature.
        assert "stroke-dasharray" in svg

    def test_deterministic(self):
        a = PlotSVG(x_range=(-3, 3))
        a.plot(lambda x: x * x)
        b = PlotSVG(x_range=(-3, 3))
        b.plot(lambda x: x * x)
        assert a.render() == b.render()

    def test_label_escapes_xml(self):
        plot = PlotSVG()
        plot.plot(lambda x: x, label="<script>alert(1)</script>")
        svg = plot.render()
        ET.fromstring(svg)  # would raise on raw <script>
        assert "<script>" not in svg
        assert "&lt;script&gt;" in svg


class TestH1TreeSVG:
    def test_basic_branch_render(self):
        tree = TreeSVG()
        yes = tree.branch("Yes", p="0.7")
        no = tree.branch("No", p="0.3")
        yes.then("Pass", p="0.9")
        yes.then("Fail", p="0.1")
        no.then("Pass", p="0.4")
        no.then("Fail", p="0.6")
        svg = tree.render()
        ET.fromstring(svg)
        for token in ("Yes", "No", "Pass", "Fail", "0.7", "0.9"):
            assert token in svg, f"missing token: {token}"

    def test_chained_then(self):
        # depth-3 chain through `.then(...).then(...)`.
        tree = TreeSVG()
        a = tree.branch("A")
        b = a.then("B")
        c = b.then("C")
        c.then("D")
        svg = tree.render()
        ET.fromstring(svg)
        assert all(label in svg for label in ("A", "B", "C", "D"))

    def test_empty_tree_renders(self):
        # Edge case: render() should not crash on an empty tree.
        svg = TreeSVG().render()
        ET.fromstring(svg)


class TestH1MarkovSVG:
    def test_basic_two_state(self):
        m = MarkovSVG()
        m.transition("Sunny", "Sunny", p="0.7")
        m.transition("Sunny", "Rainy", p="0.3")
        m.transition("Rainy", "Sunny", p="0.4")
        m.transition("Rainy", "Rainy", p="0.6")
        svg = m.render()
        ET.fromstring(svg)
        for token in ("Sunny", "Rainy", "0.7", "0.3", "0.4", "0.6"):
            assert token in svg
        # Self-loop + bidirectional edges → arrowhead marker present.
        assert 'id="arrow"' in svg

    def test_auto_state_registration(self):
        # transition(...) auto-registers states without explicit state(...).
        m = MarkovSVG()
        m.transition("A", "B", p="1.0")
        svg = m.render()
        ET.fromstring(svg)
        assert "A" in svg and "B" in svg

    def test_curved_arrows_for_bidirectional(self):
        m = MarkovSVG()
        m.transition("A", "B", p="0.5")
        m.transition("B", "A", p="0.5")
        svg = m.render()
        ET.fromstring(svg)
        # Bidirectional → quadratic Bezier curve (Q).
        assert "Q " in svg


class TestSVGBuilderBase:
    def test_render_must_be_overridden(self):
        with pytest.raises(NotImplementedError):
            SVGBuilder().render()


# ---------------------------------------------------------------------------
# H1 — format=python end-to-end pipeline
# ---------------------------------------------------------------------------

class TestH1VisualFormatPython:
    def _write_with_visual(self, tmp_path: Path, source: str, alt_text=None):
        visual = {"format": "python", "source": source}
        if alt_text:
            visual["alt_text"] = alt_text
        return _write_template(tmp_path, visual=visual)

    def test_format_python_loads(self, tmp_path):
        path = self._write_with_visual(
            tmp_path,
            "plot = PlotSVG()\nplot.plot(lambda x: x)\nVisual = plot.render()\n",
        )
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.visual is not None
        assert tpl.visual.format == "python"

    def test_invalid_format_rejected(self, tmp_path):
        path = _write_template(tmp_path, visual={
            "format": "rust", "source": "// noop",
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("visual.format" in e for e in loader.errors)

    def test_python_end_to_end_normalises_format_to_svg(self, tmp_path):
        # Closure binding (`lambda x: a*x*x`) verifies the merged-namespace
        # exec wiring — without it the lambda would NameError on `a`.
        self._write_with_visual(
            tmp_path,
            "plot = PlotSVG(x_range=(-2, 4))\n"
            "plot.plot(lambda x: a*x + b, label='f')\n"
            "Visual = plot.render()\n",
            alt_text="Linear plot with slope {{a}}.",
        )
        gen = TemplateGenerator(templates_dir=tmp_path)
        p = gen.generate(seed=1)
        v = p["visual"]
        assert v["format"] == "svg", "output must normalise to svg"
        ET.fromstring(v["source"])
        assert "polyline" in v["source"], "lambda closure failed"
        assert v["alt_text"] == "Linear plot with slope 1."

    def test_missing_visual_binding_raises(self, tmp_path):
        self._write_with_visual(
            tmp_path,
            "x = 1  # source never sets Visual\n",
        )
        gen = TemplateGenerator(templates_dir=tmp_path)
        with pytest.raises(ValueError, match="Visual"):
            gen.generate(seed=1)

    def test_non_string_visual_raises(self, tmp_path):
        self._write_with_visual(
            tmp_path,
            "plot = PlotSVG()\nVisual = plot  # binder, not str\n",
        )
        gen = TemplateGenerator(templates_dir=tmp_path)
        with pytest.raises(ValueError, match="expected str"):
            gen.generate(seed=1)

    def test_source_exception_raises(self, tmp_path):
        self._write_with_visual(
            tmp_path,
            "raise RuntimeError('boom')\n",
        )
        gen = TemplateGenerator(templates_dir=tmp_path)
        with pytest.raises(ValueError, match="boom"):
            gen.generate(seed=1)

    def test_format_svg_still_works(self, tmp_path):
        # Approach A regression check — the format-extension diff
        # must not break Jinja-rendered SVG visuals.
        _write_template(tmp_path, visual={
            "format": "svg",
            "source": '<svg xmlns="http://www.w3.org/2000/svg"><rect x="{{a}}" y="0" width="10" height="10"/></svg>',
        })
        p = TemplateGenerator(templates_dir=tmp_path).generate(seed=1)
        v = p["visual"]
        assert v["format"] == "svg"
        assert 'x="1"' in v["source"]
