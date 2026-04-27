"""Unit-system formatter tests for Phase 5.3 (and 5.3R pint backbone).

`mixed_us` (default) must be byte-identical to pre-Phase-5.3 output.
`metric` and `imperial` swap suffixes and currency where applicable.
Per-variable `unit_system` overrides the template's metadata default.

Phase 5.3R wired the pint registry as a module-load validator. Stage 2
(this checkpoint) adds compound-unit types — `density`, `energy`,
`power`, `pressure`, `force`, `acceleration` — and exposes `Q_` /
`ureg` / `get_pint_unit` in the solution sandbox. `TestCompoundTypes`
locks down the per-system display; `TestPintSandbox` proves the
sandbox accepts Quantity Answer values and converts them to the
canonical unit before formatting.
"""

import pytest

from src.solution_evaluator import execute_solution, format_answer
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
        assert format_answer(8, spec, template_unit_system="mixed_us") == "8 m³"

    def test_money_answer(self):
        spec = VariableSpec(name="Answer", type="money")
        assert format_answer(6.94, spec, template_unit_system="mixed_us") == "$6.94"


class TestMetricSystem:
    """`metric` swaps °F→°C, mph→km/h, m³→liters, $→€."""

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
        assert format_answer(20, spec, template_unit_system="imperial") == "20 ft²"

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


class TestPintBackbone:
    """Phase 5.3R: pint registry is wired and DISPLAY_UNITS is validated.

    Stage 1 doesn't use pint at runtime — these tests assert the registry
    is reachable from a single source-of-truth and that typos in unit
    names fail loudly at module load.
    """

    def test_pint_registry_singleton_is_reachable(self):
        from src.units import ureg, Q_
        import pint

        assert isinstance(ureg, pint.UnitRegistry)
        # Q_ should be the registry's Quantity class — same identity, not a fresh one.
        assert Q_ is ureg.Quantity

    def test_pint_parses_known_units_and_rejects_typos(self):
        from src.units import ureg

        # Real units round-trip through the registry
        ureg.parse_units("meter ** 2")
        ureg.parse_units("kilogram / meter ** 3")  # density (Stage 2 preview)
        ureg.parse_units("mile / hour")
        # Typos raise (some pint subclass of pint errors / undefined unit)
        with pytest.raises(Exception):
            ureg.parse_units("meeter")
        with pytest.raises(Exception):
            ureg.parse_units("blarghs")

    def test_module_load_validator_rejects_a_bad_display_units_entry(self):
        """Manually invoke the validator with a corrupt entry — it must
        complain with the offending (system, type, unit) referenced."""
        from src.units import _validate_display_units

        bad = {
            "mixed_us": {
                "length": ("meeter", "m", "meters"),  # typo
            },
        }
        with pytest.raises(ValueError, match=r"DISPLAY_UNITS\['mixed_us'\]\['length'\].*'meeter'"):
            _validate_display_units(bad)


class TestCompoundTypes:
    """Stage 2: density / energy / power / pressure / force / acceleration.

    Compound types render with a space between value and suffix
    ("750 kg/m³"), unlike length / weight ("5kg"). Imperial uses the
    physics-imperial canonical units (lb/ft³, ft·lbf, hp, psi, lbf,
    ft/s²); mixed_us tracks SI for compound types — its US tilt is
    only currency / mph / °F.
    """

    def setup_method(self):
        self.g = VariableGenerator(seed=1)

    # --- problem-text formatting (short suffix) ---

    def test_density_value_metric(self):
        spec = VariableSpec(name="rho", type="density")
        assert self.g.format_value(750, spec, template_unit_system="metric") == "750 kg/m³"

    def test_density_value_imperial(self):
        spec = VariableSpec(name="rho", type="density")
        assert self.g.format_value(46, spec, template_unit_system="imperial") == "46 lb/ft³"

    def test_energy_value_mixed_us(self):
        spec = VariableSpec(name="E", type="energy")
        assert self.g.format_value(1500, spec, template_unit_system="mixed_us") == "1500 J"

    def test_acceleration_value_metric_float(self):
        spec = VariableSpec(name="a", type="acceleration")
        assert self.g.format_value(9.81, spec, template_unit_system="metric") == "9.81 m/s²"

    # --- answer formatting (long suffix) ---

    def test_density_answer_metric(self):
        spec = VariableSpec(name="Answer", type="density")
        assert format_answer(7850, spec, template_unit_system="metric") == "7850 kg/m³"

    def test_energy_answer_metric(self):
        spec = VariableSpec(name="Answer", type="energy")
        assert format_answer(1500, spec, template_unit_system="metric") == "1500 joules"

    def test_energy_answer_imperial(self):
        spec = VariableSpec(name="Answer", type="energy")
        assert format_answer(1500, spec, template_unit_system="imperial") == "1500 foot-pounds"

    def test_power_answer_imperial(self):
        spec = VariableSpec(name="Answer", type="power")
        assert format_answer(150, spec, template_unit_system="imperial") == "150 horsepower"

    def test_pressure_answer_metric(self):
        spec = VariableSpec(name="Answer", type="pressure")
        assert format_answer(101325, spec, template_unit_system="metric") == "101325 pascals"

    def test_pressure_answer_imperial(self):
        spec = VariableSpec(name="Answer", type="pressure")
        assert format_answer(14.7, spec, template_unit_system="imperial") == "14.70 psi"

    def test_force_answer_metric(self):
        spec = VariableSpec(name="Answer", type="force")
        assert format_answer(9.81, spec, template_unit_system="metric") == "9.81 newtons"

    def test_force_answer_imperial(self):
        spec = VariableSpec(name="Answer", type="force")
        assert format_answer(2.2, spec, template_unit_system="imperial") == "2.20 pound-force"

    def test_acceleration_answer_imperial(self):
        spec = VariableSpec(name="Answer", type="acceleration")
        assert format_answer(32.2, spec, template_unit_system="imperial") == "32.20 ft/s²"

    def test_compound_var_unit_system_override(self):
        # Template default metric; force this density variable to imperial.
        spec = VariableSpec(name="Answer", type="density", unit_system="imperial")
        assert format_answer(46, spec, template_unit_system="metric") == "46 lb/ft³"


class TestPintSandbox:
    """Stage 2: solutions can use `Q_` / `ureg` / `get_pint_unit`.

    A solution that returns a pint Quantity must be unwrapped to the
    canonical (type, system) magnitude before display. Conversion runs
    via `pint.Quantity.to()` so a Quantity in any compatible unit
    formats identically.
    """

    def test_q_and_ureg_available_in_sandbox(self):
        ctx = execute_solution(
            "Answer = float(Q_(5, 'kilogram').to('gram').magnitude)",
            context={},
            language="en",
        )
        # 5 kg → 5000 g
        assert ctx == 5000.0

    def test_get_pint_unit_helper_available(self):
        ctx = execute_solution(
            "Answer = get_pint_unit('density', 'metric')",
            context={},
            language="en",
        )
        assert ctx == "kilogram / meter ** 3"

    def test_quantity_answer_unwraps_to_canonical_unit(self):
        # Solution returns a mass Quantity in pounds; Answer is a metric
        # weight, so the formatter must convert to kg before printing.
        spec = VariableSpec(name="Answer", type="weight")
        from src.units import Q_  # noqa: F401 — used in exec'd solution
        ctx = execute_solution(
            "Answer = Q_(2.20462, 'pound')",
            context={},
            language="en",
        )
        assert format_answer(ctx, spec, template_unit_system="metric") == "1.00 kg"

    def test_density_volume_quantity_arithmetic(self):
        # P-G3-shaped: density (kg/m³) × volume (L) = mass (kg). Pint
        # handles the L → m³ conversion implicitly during multiplication.
        ctx = execute_solution(
            "density_q = Q_(1000, 'kilogram / meter ** 3')\n"
            "volume_q = Q_(2, 'liter')\n"
            "Answer = density_q * volume_q",
            context={},
            language="en",
        )
        spec = VariableSpec(name="Answer", type="weight")
        # 1000 kg/m³ × 2 L = 2 kg (water).
        assert format_answer(ctx, spec, template_unit_system="metric") == "2.00 kg"

    def test_quantity_answer_for_compound_type(self):
        # Energy in joules, requested as imperial (foot-pounds). 1 J ≈ 0.7376 ft·lbf.
        ctx = execute_solution(
            "Answer = Q_(1356, 'joule')",
            context={},
            language="en",
        )
        spec = VariableSpec(name="Answer", type="energy")
        # 1356 J × 0.737562… ≈ 1000 ft·lbf
        out = format_answer(ctx, spec, template_unit_system="imperial")
        assert out.endswith(" foot-pounds")
        magnitude = float(out.split()[0])
        assert abs(magnitude - 1000.0) < 0.5
