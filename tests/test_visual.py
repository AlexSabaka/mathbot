"""Visual-layer tests for Phase 5.5.

The `visual:` block in YAML stores canonical SVG source. The generator
renders it through Jinja2 with the same variable context as the problem
template and emits it on the output JSON's `visual` field. PNG
generation is a separate `mathbot rasterize` step (not covered here —
it requires the system `libcairo` library).
"""

from pathlib import Path

import pytest
import yaml

from src.template_generator import TemplateGenerator
from src.yaml_loader import YAMLLoader


def _write_template(path: Path, **overrides):
    """Build a minimal valid template under `path` and write it as YAML.

    `overrides` keys are merged into the top-level YAML (visual=<dict>,
    metadata=<dict>, etc.) before writing.
    """
    base = {
        "metadata": {
            "id": path.stem, "version": "1.0.0", "author": "t",
            "created": "2026-04-26", "grade": 1,
            "topic": "arithmetic.addition", "family": "addition",
            "difficulty": "easy", "steps": 1,
        },
        "variables": {
            "a": {"type": "integer", "min": 3, "max": 5},
            "Answer": {"type": "integer"},
        },
        "template": "{{a}}",
        "solution": "Answer = a",
        "tests": [{"seed": 1, "expected": {"answer": "3"}}],
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = {**base[key], **value}
        else:
            base[key] = value
    path.write_text(yaml.dump(base, sort_keys=False, allow_unicode=True))


class TestVisualSchema:
    """The visual block is optional; presence + format + source are validated."""

    def test_no_visual_loads_fine(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_no_visual_01.yaml"
        _write_template(path)
        result = YAMLLoader().load_template(path)
        assert result is not None
        assert result.visual is None

    def test_valid_svg_visual_parses(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_with_visual_01.yaml"
        _write_template(path, visual={
            "format": "svg",
            "source": "<svg>{{a}}</svg>",
            "alt_text": "Number {{a}}",
        })
        result = YAMLLoader().load_template(path)
        assert result is not None
        assert result.visual is not None
        assert result.visual.format == "svg"
        assert "{{a}}" in result.visual.source
        assert result.visual.alt_text == "Number {{a}}"

    def test_invalid_format_rejected(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_bad_format_01.yaml"
        _write_template(path, visual={
            "format": "matplotlib",  # not yet supported
            "source": "fig, ax = plt.subplots()",
        })
        loader = YAMLLoader()
        result = loader.load_template(path)
        assert result is None
        assert any("visual.format" in e for e in loader.errors)

    def test_missing_source_rejected(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_bad_source_01.yaml"
        _write_template(path, visual={"format": "svg", "source": ""})
        loader = YAMLLoader()
        result = loader.load_template(path)
        assert result is None
        assert any("visual.source" in e for e in loader.errors)

    def test_alt_text_must_be_string(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_bad_alt_01.yaml"
        _write_template(path, visual={
            "format": "svg",
            "source": "<svg/>",
            "alt_text": 42,  # not a string
        })
        loader = YAMLLoader()
        result = loader.load_template(path)
        assert result is None
        assert any("alt_text" in e for e in loader.errors)


class TestVisualRendering:
    """Visual source is Jinja-rendered with the same context as `template:`."""

    def _gen(self, tmp_path, **visual):
        topic = tmp_path / "arithmetic"
        topic.mkdir(exist_ok=True)
        path = topic / "k1_easy_visualgen_01.yaml"
        _write_template(path, visual=visual)
        return TemplateGenerator(templates_dir=tmp_path, seed=1).generate(seed=1)

    def test_variables_substituted_into_source(self, tmp_path):
        out = self._gen(tmp_path, format="svg", source="<svg>{{a}}</svg>")
        assert "visual" in out
        assert out["visual"]["format"] == "svg"
        # The actual generated value of `a` is one of {3, 4, 5}
        assert out["visual"]["source"] in {"<svg>3</svg>", "<svg>4</svg>", "<svg>5</svg>"}

    def test_alt_text_substituted(self, tmp_path):
        out = self._gen(
            tmp_path, format="svg", source="<svg>{{a}}</svg>",
            alt_text="Value: {{a}}",
        )
        assert out["visual"]["alt_text"].startswith("Value: ")
        assert out["visual"]["alt_text"].split(": ")[1] in {"3", "4", "5"}

    def test_no_visual_field_when_template_has_none(self, tmp_path):
        topic = tmp_path / "arithmetic"
        topic.mkdir()
        path = topic / "k1_easy_no_visual_for_gen_01.yaml"
        _write_template(path)  # no visual override
        out = TemplateGenerator(templates_dir=tmp_path, seed=1).generate(seed=1)
        assert "visual" not in out

    def test_render_failure_raises_with_template_id(self, tmp_path):
        # Unknown variable in source → Jinja silently ignores by default;
        # a malformed Jinja statement is the way to force a failure.
        out_path = tmp_path / "arithmetic" / "k1_easy_bad_render_01.yaml"
        out_path.parent.mkdir(exist_ok=True)
        _write_template(out_path, visual={
            "format": "svg",
            "source": "<svg>{% for x in nope %}{% endfor",  # unclosed tag
        })
        gen = TemplateGenerator(templates_dir=tmp_path, seed=1)
        with pytest.raises(ValueError, match="Failed to render visual"):
            gen.generate(seed=1)


class TestExistingVisualAnchor:
    """The seeded k5_easy_square_area_01_anchor template carries a visual."""

    def test_anchor_emits_visual_in_output(self):
        from src.generator import generate_problem
        out = generate_problem(seed=12345, math_topic="geometry")
        # Find a problem from the visual-augmented anchor; if random
        # selection picked a different geometry template, just check the
        # invariant that geometry templates without `visual:` don't emit
        # the field — covered by other tests. So instead, target the
        # visual anchor directly via input.
        from src.template_generator import TemplateGenerator
        gen = TemplateGenerator(seed=12345)
        template = gen.templates["k5_easy_square_area_01"]
        out = gen._generate_from_template(template, seed=12345)
        assert "visual" in out
        v = out["visual"]
        assert v["format"] == "svg"
        assert v["source"].startswith("<svg")
        # The {{side}} variable must have been substituted (no Jinja `{{`
        # left in the rendered SVG).
        assert "{{" not in v["source"]
        assert "alt_text" in v
        assert "{{" not in v["alt_text"]
