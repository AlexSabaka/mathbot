# YAML authoring quickref

Things every template author has gotten wrong at least once. SPEC.md is the canonical schema; this file is the "what bites you" companion.

## Filename conventions (the #1 source of confusion)

| Template kind | Filename pattern | Difficulty token? |
| --- | --- | --- |
| Single-tier anchor | `k<grade>_<difficulty>_<descriptor>_anchor.yaml` | Yes |
| Single-tier variant | `k<grade>_<difficulty>_<descriptor>.yaml` | Yes |
| Multi-tier anchor | `k<grade>_<descriptor>_anchor.yaml` | **No** |
| Multi-tier variant | `k<grade>_<descriptor>.yaml` | **No** |

Multi-tier templates dropping the `_<difficulty>_` token catches everyone the first time. SPEC.md §15 has the rule. The reason: the same file renders at all declared `difficulty_tiers`, so embedding one tier in the filename would lie.

The `metadata.id` field must equal the filename stem **minus** `_anchor`. So `k7_medium_pythagoras_01_anchor.yaml` has `id: k7_medium_pythagoras_01`.

## The `topic` invariant

`metadata.topic` must start with the parent directory name. SPEC.md §4 enforces this at load time.

```yaml
# File: src/templates/algebra/k7_medium_two_var_system_anchor.yaml
metadata:
  topic: algebra.equations         # ✓ starts with "algebra"
  # topic: equations               # ✗ rejected — no parent prefix
  # topic: arithmetic.equations    # ✗ rejected — wrong parent
```

If you need a new top-level topic, add it to `MATH_TOPICS` in `src/constants.py`. Don't try to file the template under an existing dir with a topic that doesn't match.

## `Answer` is required, and you should declare its formatting

Every template must declare an answer variable. The formatting rules in SPEC.md §5 apply equally to `Answer`:

```yaml
variables:
  Answer: { type: money }            # → renders as "$12.50"
  Answer: { type: weight }           # → renders as "12 kilograms" (long suffix)
  Answer: { type: percentage }       # → renders as "15%"
  Answer: { type: integer }          # → renders as "42"
  Answer: { type: string }           # → renders as whatever the solution assigns
```

The solution code assigns to `Answer` (a Python variable name); the formatter consults the spec to format the assigned value.

For multi-answer, declare `Answer1`, `Answer2`, ... (no `Answer`). The CLI joins formatted values with `" | "`.

## `_formatted` companions

For variables with a formatted type (`money`, `percentage`, `length`, etc.), the renderer auto-injects a `<name>_formatted` companion. Use it in problem text; use the raw form in math.

```jinja
{# raw form for math, formatted for display #}
{% set total = price * quantity %}
{{name}} pays {{price_formatted}} for {{quantity}} items, totaling {{total}}.
```

This is implicit (TECHDEBT TD-5.1) — there's no validator that catches a typo like `{{prince_formatted}}`. Spell carefully; render-smoke (step 5b in SKILL.md) catches the silent-empty result.

For variables with a free-form `unit:`, the renderer also injects `<name>_unit` carrying the raw pint string. Available in both Jinja and the solution sandbox:

```yaml
variables:
  velocity: { type: decimal, unit: 'meter / second', min: 5, max: 25 }
solution: |
  v_q = Q_(velocity, velocity_unit)        # uses auto-injected `velocity_unit`
  Answer = v_q.to('kilometer / hour').magnitude
```

## Solution-only variables can't be referenced in `template:`

The solution runs *after* the template renders. If the template needs a derived value, compute it via `{% set %}` at the top:

```jinja
{# WRONG — `dividend` is set in solution, template can't see it #}
{{name}} has {{dividend}} apples to share.

{# RIGHT — compute in template via {% set %} #}
{% set dividend = (number1 // number2) * number2 %}
{{name}} has {{dividend}} apples to share among {{number2}} friends.
```

`mathbot lint` flags `unrendered_jinja` (error) when the rendered output contains literal `{{...}}` — this is usually the cause.

## Jinja list comprehensions: don't

Jinja's `{% set %}` directive doesn't support Python list comprehensions. Use an inline `{% for %}` loop:

```jinja
{# WRONG — Jinja syntax error #}
{% set y_data = [slope * x + intercept for x in x_data] %}

{# RIGHT — inline for loop #}
{% for x in x_data %}({{x}}, {{slope * x + intercept}}){% if not loop.last %}, {% endif %}{% endfor %}
```

## `<auto>` placeholders for fixtures

Author `tests[].expected.answer` as `"<auto>"` while drafting. Then run:

```bash
uv run python scripts/refresh_test_answers.py --apply --filter '*/<file>.yaml'
```

The script is surgical (ruamel.yaml round-trip) — preserves comments, key order, and quoting. Hand-computing fixture answers is wrong because the formatter's specifics (decimal places, currency symbol, unit suffix) are determined by the variable spec; you'll drift.

Re-run `refresh_test_answers.py` after **any** change to:

- The solution code (different math → different answer)
- A variable's `min`/`max`/`step`/`choices` (different RNG draws → different values)
- The template prose (no, doesn't affect answers, but get in the habit)
- Generator-engine code (any change to `src/variable_generator.py`, `src/jinja_renderer.py`, etc.)

## Multi-tier `ranges:`

For multi-tier templates, the per-tier `ranges:` overrides flat `min`/`max`/`step`/`choices`:

```yaml
metadata:
  difficulty: easy
  difficulty_tiers: [easy, medium, hard]

variables:
  num_a:
    type: integer
    ranges:
      easy:   { min: 30,  max: 50 }
      medium: { min: 150, max: 300 }
      hard:   { min: 250, max: 500 }
  pace:
    type: integer
    ranges:
      easy:   { choices: [10, 100] }
      medium: { choices: [10, 100, 1000] }
      # `hard` not listed → falls back to flat fields (none here, so error)
```

If `hard` is in `difficulty_tiers` but a variable's `ranges:` skips it without flat fallback fields, generation will fail at hard tier. Either provide a `hard:` entry or set flat `min`/`max` as fallback.

Test fixtures specify their tier:

```yaml
tests:
  - { seed: 12345, difficulty: easy,   expected: { answer: "37" } }
  - { seed: 12345, difficulty: medium, expected: { answer: "100" } }
  - { seed: 12345, difficulty: hard,   expected: { answer: "279" } }
```

`mathbot lint` flags `fixture_missing` if a multi-tier template lacks a fixture for any declared tier.

## Unit system selection

Default `unit_system: mixed_us`. Set explicitly to `metric` or `imperial` for new templates with coherent display:

| System | Money | Length | Weight | Temperature | Speed | Area | Volume |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mixed_us` | $ | m | kg | °F | mph | m² | m³ |
| `metric` | € | m | kg | °C | km/h | m² | L |
| `imperial` | $ | ft | lb | °F | mph | ft² | gal |

Compound physics types (density, energy, power, pressure, force, acceleration) are SI for `mixed_us` and `metric`; only `imperial` swaps in physics-imperial. SPEC.md §8 has the table.

For one-off compound units (`m/s²`, `mi/gal`, `liter/minute`), use the free-form `unit:` field on the variable spec instead of inventing a new type. SPEC.md §8.3.

## Visual blocks (when applicable)

Optional `visual:` block for geometry, schematic, or diagram problems. Source is Jinja-rendered SVG; PNG production happens later via `mathbot rasterize`.

```yaml
visual:
  format: svg
  alt_text: "A square with each side labeled {{side}} units."
  source: |
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
      <rect x="40" y="40" width="120" height="120" fill="none" stroke="#222"/>
      <text x="100" y="32" text-anchor="middle">{{side}}</text>
    </svg>
```

Three rules:

1. **Schematic, not to scale.** Always render a 120-pixel square regardless of `{{side}}`; let the label convey the value.
2. **Use `viewBox`, not absolute `width`/`height`.** The rasterizer picks the output size.
3. **Never write PNG-generation code in templates.** PNGs are derived from the SVG source; losing the source means losing the ability to re-render at different DPI.

For derived-coordinate visuals (probability trees, bar charts), Approach B (Python builders in the sandbox) is roadmap (TECHDEBT TD-3.1b). Until it ships, fall back to Jinja-SVG with arithmetic in the SVG attributes — gets unwieldy fast, but it works.

## What `mathbot lint` actually checks

For the full list and how to fix each finding, see `lint_findings_guide.md`. Quick summary:

- **Errors** (block the template from shipping): `render_crash`, `unrendered_jinja`, `empty_answer`, `visual_render_crash`, `fixture_drifted`, `fixture_crashed`, `schema_invalid`
- **Warnings** (concerning, may indicate drift): `off_anchor_divergence`, `anchor_filename_mismatch`, `body_too_long`, `fixture_missing`, `slug_noncanonical`, `unit_spelled_squared`/`_cubic`, `zero_steps_with_ops`, `very_high_step_count`
- **Info** (heuristic, not blocking): `gsm8k_money_change`, `gsm8k_with_tax`, `gsm8k_items_at_price_each`, `area_no_squared_unit`, `volume_no_cubed_unit`

`--strict` treats warnings as errors. Use it.
