"""Unit-system formatter tests for Phase 5.3.

`mixed_us` (default) must be byte-identical to pre-Phase-5.3 output.
`metric` and `imperial` swap suffixes and currency where applicable.
Per-variable `unit_system` overrides the template's metadata default.
"""

from src.solution_evaluator import format_answer
from src.variable_generator import VariableGenerator
from src.yaml_loader import VariableSpec


class TestMixedUsBackwardCompat:
    """mixed_us must reproduce the pre-Phase-5.3 byte-identical output."""

    def setup_method(self):
        self.g = VariableGenerator(seed=1)

    def test_money_value(self):
        spec = VariableSpec(name="p", type="money")
        assert self.g.format_value(12.5, spec, template_unit_system="mixed_us") == "$12.50"

    def test_length_value_int(self):
        spec = VariableSpec(name="d", type="length")
        assert self.g.format_value(7, spec, template_unit_system="mixed_us") == "7m"

    def test_length_value_float(self):
        spec = VariableSpec(name="d", type="length")
        assert self.g.format_value(7.25, spec, template_unit_system="mixed_us") == "7.25m"

    def test_weight_value(self):
        spec = VariableSpec(name="w", type="weight")
        assert self.g.format_value(5, spec, template_unit_system="mixed_us") == "5kg"

    def test_temperature_value(self):
        spec = VariableSpec(name="t", type="temperature")
        assert self.g.format_value(72, spec, template_unit_system="mixed_us") == "72.0°F"

    def test_length_answer_int(self):
        spec = VariableSpec(name="Answer", type="length")
        assert format_answer(12, spec, template_unit_system="mixed_us") == "12 meters"

    def test_speed_answer(self):
        spec = VariableSpec(name="Answer", type="speed")
        assert format_answer(45.0, spec, template_unit_system="mixed_us") == "45.00 mph"

    def test_volume_answer(self):
        spec = VariableSpec(name="Answer", type="volume")
        assert format_answer(8, spec, template_unit_system="mixed_us") == "8 cubic meters"

    def test_money_answer(self):
        spec = VariableSpec(name="Answer", type="money")
        assert format_answer(6.94, spec, template_unit_system="mixed_us") == "$6.94"


class TestMetricSystem:
    """`metric` swaps °F→°C, mph→km/h, cubic meters→liters, $→€."""

    def setup_method(self):
        self.g = VariableGenerator(seed=1)

    def test_money_uses_euro(self):
        spec = VariableSpec(name="p", type="money")
        assert self.g.format_value(12.5, spec, template_unit_system="metric") == "€12.50"

    def test_money_answer_uses_euro(self):
        spec = VariableSpec(name="Answer", type="money")
        assert format_answer(6.94, spec, template_unit_system="metric") == "€6.94"

    def test_speed_answer_uses_kmh(self):
        spec = VariableSpec(name="Answer", type="speed")
        assert format_answer(45.0, spec, template_unit_system="metric") == "45.00 km/h"

    def test_temperature_uses_celsius(self):
        spec = VariableSpec(name="t", type="temperature")
        assert self.g.format_value(20, spec, template_unit_system="metric") == "20.0°C"

    def test_volume_answer_uses_liters(self):
        spec = VariableSpec(name="Answer", type="volume")
        assert format_answer(8, spec, template_unit_system="metric") == "8 liters"


class TestImperialSystem:
    """`imperial` swaps m→ft, kg→pounds, m²→ft², m³→gallons."""

    def setup_method(self):
        self.g = VariableGenerator(seed=1)

    def test_length_uses_feet(self):
        spec = VariableSpec(name="d", type="length")
        assert self.g.format_value(7, spec, template_unit_system="imperial") == "7ft"

    def test_length_answer_uses_feet(self):
        spec = VariableSpec(name="Answer", type="length")
        assert format_answer(12, spec, template_unit_system="imperial") == "12 feet"

    def test_weight_uses_pounds(self):
        spec = VariableSpec(name="w", type="weight")
        assert self.g.format_value(5, spec, template_unit_system="imperial") == "5lb"

    def test_weight_answer_uses_pounds(self):
        spec = VariableSpec(name="Answer", type="weight")
        assert format_answer(5.5, spec, template_unit_system="imperial") == "5.50 pounds"

    def test_area_answer_uses_square_feet(self):
        spec = VariableSpec(name="Answer", type="area")
        assert format_answer(20, spec, template_unit_system="imperial") == "20 square feet"

    def test_volume_answer_uses_gallons(self):
        spec = VariableSpec(name="Answer", type="volume")
        assert format_answer(8, spec, template_unit_system="imperial") == "8 gallons"


class TestPerVariableOverride:
    """Per-variable `unit_system` overrides the template default."""

    def setup_method(self):
        self.g = VariableGenerator(seed=1)

    def test_var_imperial_overrides_template_metric(self):
        # Template defaults to metric (€), but this variable forces imperial ($).
        spec = VariableSpec(name="p", type="money", unit_system="imperial")
        assert self.g.format_value(12.5, spec, template_unit_system="metric") == "$12.50"

    def test_var_metric_overrides_template_imperial(self):
        # Template defaults to imperial (ft), but this variable forces metric (m).
        spec = VariableSpec(name="d", type="length", unit_system="metric")
        assert self.g.format_value(7, spec, template_unit_system="imperial") == "7m"

    def test_answer_var_override(self):
        # Answer variable can override too.
        spec = VariableSpec(name="Answer", type="length", unit_system="imperial")
        assert format_answer(12, spec, template_unit_system="metric") == "12 feet"


class TestSchemaValidation:
    """Loader rejects invalid unit_system values."""

    def test_invalid_metadata_unit_system(self, tmp_path):
        import yaml
        from src.yaml_loader import YAMLLoader

        topic_dir = tmp_path / "arithmetic"
        topic_dir.mkdir()
        path = topic_dir / "k1_easy_bad_01.yaml"
        path.write_text(yaml.dump({
            "metadata": {
                "id": "k1_easy_bad_01", "version": "1.0.0", "author": "t",
                "created": "2026-04-26", "grade": 1, "topic": "arithmetic.addition",
                "family": "addition", "difficulty": "easy", "steps": 1,
                "unit_system": "imperial_si",  # invalid
            },
            "variables": {"a": {"type": "integer", "min": 1, "max": 2},
                          "Answer": {"type": "integer"}},
            "template": "{{a}}",
            "solution": "Answer = a",
            "tests": [{"seed": 1, "expected": {"answer": "1"}}],
        }))
        loader = YAMLLoader()
        result = loader.load_template(path)
        assert result is None
        assert any("unit_system" in e for e in loader.errors)

    def test_invalid_variable_unit_system(self, tmp_path):
        import yaml
        from src.yaml_loader import YAMLLoader

        topic_dir = tmp_path / "arithmetic"
        topic_dir.mkdir()
        path = topic_dir / "k1_easy_bad_02.yaml"
        path.write_text(yaml.dump({
            "metadata": {
                "id": "k1_easy_bad_02", "version": "1.0.0", "author": "t",
                "created": "2026-04-26", "grade": 1, "topic": "arithmetic.addition",
                "family": "addition", "difficulty": "easy", "steps": 1,
            },
            "variables": {
                "a": {"type": "integer", "min": 1, "max": 2,
                      "unit_system": "metricnope"},  # invalid
                "Answer": {"type": "integer"},
            },
            "template": "{{a}}",
            "solution": "Answer = a",
            "tests": [{"seed": 1, "expected": {"answer": "1"}}],
        }))
        loader = YAMLLoader()
        result = loader.load_template(path)
        assert result is None
        assert any("unit_system" in e for e in loader.errors)
