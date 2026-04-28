# Mathbot — development guide

Procedural multi-step math word-problem generator. The corpus is a tree of
hand-authored YAML templates rendered with Jinja2 and post-processed by a
small Python sandbox; deterministic from a seed; produces problems with
verifiable answers for K1-K12.

## Quick start

```bash
uv sync                                                 # install deps + .venv (Python 3.12)
uv sync --extra png                                     # + cairosvg (for `mathbot rasterize`)
uv run pytest                                           # 93 tests
uv run mathbot generate -c 2 -g elementary -t arithmetic -s 42  # one problem
uv run mathbot batch 10 -s 1 -o json                    # 10 problems → stdout
uv run mathbot verify <path/to/template.yaml>           # validate one template
uv run mathbot test    <path/to/template.yaml>          # run its embedded tests
uv run mathbot rasterize <dataset.json> [--dpi 150]     # SVG → PNG sidecars
```

`uv run` is the blessed entrypoint — the host shell's `VIRTUAL_ENV` may leak
in and trigger a benign warning when invoking `mathbot` directly.

## Repository layout

```text
src/
├── cli.py                  Click commands: generate, batch, verify, test, list, info
├── generator.py            Module API: generate_problem(), generate_problems()
├── template_generator.py   Loads + indexes templates; per-template generation
├── yaml_loader.py          YAMLLoader: schema validation + TemplateDefinition dataclass
├── jinja_renderer.py       Jinja2 env; locale-aware filters dispatch via i18n registry
├── variable_generator.py   Generates random values per VariableSpec.type; Faker locale-aware
├── solution_evaluator.py   Executes solution code in safe sandbox; formats answer
├── providers.py            Thin loader → MathProblemProvider class attributes from data/pools.*.yaml
├── constants.py            MATH_TOPICS, PROBLEM_FAMILIES, GRADES enums
├── data/pools.<lang>.yaml  Per-locale entity pools (items, calendar, contexts) — `en` ships
├── i18n/languages.py       LanguageSpec registry; plural/ordinal/number_to_words per language
└── templates/<topic>/*_anchor.yaml  + variants
scripts/
└── refresh_test_answers.py  Surgical test-answer regenerator (ruamel.yaml)
tests/                       pytest suite for CLI + generator API
MATHBOT_PROBLEMS_PROPOSAL.md K7-K12 expansion research (22 proposed families)
TECHDEBT.md                  Running log of known infrastructure debt and follow-ups
```

## Authoring a new template

1. Pick `(grade, topic, family, difficulty)` and confirm whether an anchor
   already exists at `src/templates/<topic>/k<grade>_<difficulty>_*_anchor.yaml`.
   If yes, follow its style; if not, this template will *be* the anchor —
   suffix the filename `_anchor.yaml`.
2. Write the YAML with `<auto>` placeholders for `tests[].expected.answer`.
3. Verify structurally and semantically:

   ```bash
   uv run mathbot verify <path>
   for s in 12345 42 99 7; do
     uv run mathbot generate --input <path> -s $s -o text | tail -8
   done
   ```

   Manually check the math on each output — generator-correct values aren't
   the same as semantically-correct problems.
4. Populate test answers: `uv run python scripts/refresh_test_answers.py
   --apply --filter '*/<file>.yaml'`.
5. Confirm corpus health: `uv run pytest`.

## YAML template schema

```yaml
metadata:
  id: k7_medium_sequential_budget       # filename stem; required unique
  version: "1.0.0"
  author: Mathbot
  created: 2026-04-22
  grade: 7                              # int, K1-K12
  topic: arithmetic.multi_step          # MUST start with parent dir name (enforced)
  family: sequential_purchase           # see PROBLEM_FAMILIES
  difficulty: easy | medium | hard     # default tier when --complexity unspecified
  difficulty_tiers: [easy, medium, hard]  # optional; see "Multi-tier templates" below
  steps: 5                              # number of reasoning steps
  language: en                          # optional, BCP-47 base; drives locale-aware filters
  culture: en-US                        # optional, BCP-47 region; drives Faker locale (names/cities)
  unit_system: mixed_us                 # optional, default mixed_us; metric|imperial|mixed_us
  tags: [list, of, tags]

variables:
  name:           { type: person }
  budget:         { type: integer, choices: [40, 60, 100] }
  price1:         { type: integer, min: 8, max: 18 }
  acceleration:   { type: decimal, unit: "meter / second ** 2", min: 0.5, max: 9.81 }  # free-form pint unit
  Answer:         { type: string }

template: |        # Jinja2; rendered to the displayed problem text
  {{name}} walks in with $${{budget}}…

solution: |        # Python; executes after rendering, must assign Answer
  Answer = …

tests:             # 3+ cases recommended; seed is the canonical RNG seed
  - seed: 12345
    expected:
      answer: "bought 5 items, $2 left"
    # difficulty: easy   # optional; see "Multi-tier templates"

visual:            # OPTIONAL canonical visual source; see "Visual layer" below
  format: svg      # only `svg` ships in Phase 5.5; `python` (sandbox builders) is roadmap
  alt_text: "A square with each side labeled {{side}} units."
  source: |
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
      <rect x="40" y="40" width="120" height="120" fill="none" stroke="#222"/>
      <text x="100" y="32" text-anchor="middle">{{side}}</text>
    </svg>
```

### `metadata.topic` ↔ directory invariant

A template under `src/templates/<X>/` must declare `topic: X.<subtopic>`.
Bare topics like `topic: arithmetic` are not allowed; cross-directory topics
(`measurement/k3_easy_area_01.yaml` with `topic: geometry.measurement`) were
harmonized away in v0.1.3. **Enforced** by `YAMLLoader._validate_template`
since Phase 5.1 — a mismatched template fails to load with a clear error.
New top-level dirs require updating `MATH_TOPICS` in `src/constants.py`.

### Multi-tier templates (Phase 5.7)

A single YAML template can render at multiple difficulty tiers when its
metadata declares:

```yaml
metadata:
  difficulty: easy                       # default tier
  difficulty_tiers: [easy, medium, hard] # must include `difficulty`

variables:
  num_a:
    type: integer
    ranges:                              # per-tier overrides of min/max/step/choices
      easy:   { min: 30,  max: 50 }
      medium: { min: 150, max: 300 }
      hard:   { min: 250, max: 500 }
  pace:
    type: integer
    ranges:                              # `choices` per tier works too
      easy:   { choices: [10, 100] }
      medium: { choices: [10, 100, 1000] }
```

A variable's `ranges:` entries override the flat `min`/`max`/`step`/`choices`
fields for that tier; tiers without an entry fall back to the flat fields.
The same applies for `string`/`choice` and `decimal` types — `decimal` honors
per-tier `choices` lists too.

The render flow:

1. `mathbot generate -c <N>` (or `mathbot batch -c <N>`) maps complexity
   `1/2/3` → `easy/medium/hard`. If the chosen template lists that tier in
   `difficulty_tiers`, it renders at that tier; otherwise the template falls
   back to its declared `difficulty`.
2. With no `--complexity`, multi-tier templates sample a tier uniformly
   from `difficulty_tiers` so a `mathbot batch` run still spreads across
   tiers within the cell.
3. **`test_id` carries `__<tier>` suffix** for multi-tier renders
   (`math_k2_subtraction_01__easy` / `__medium` / `__hard`). Single-tier
   templates keep the historical `math_<id>` (no suffix) so legacy dataset
   consumers don't see id changes.
4. `task_params.complexity`, `config_name`, and the rendered problem all
   reflect the effective tier.

Test fixtures specify the tier per-row:

```yaml
tests:
  - seed: 12345
    difficulty: easy
    expected: { answer: "37" }
  - seed: 12345
    difficulty: medium
    expected: { answer: "100" }
  - seed: 12345
    difficulty: hard
    expected: { answer: "279" }
```

`difficulty:` on a fixture is optional; when omitted, the runner uses
`metadata.difficulty` (so single-tier templates' fixtures keep working
unchanged).

**When to make a template multi-tier**: the tiers differ only in number
ranges / choice lists, with the same operation, prompt shape, and
solution code. **When to keep tiers as separate templates**: tiers probe
different sub-skills (e.g., `k6.algebra.factoring`: easy = scalar GCF,
medium = variable factor, hard = quadratic) or use structurally different
prompt text (e.g., `k6.fractions.fraction_add_sub`: same-denom vs
different-denom).

Filenames for multi-tier templates drop the difficulty token:
`k2_subtraction_01_anchor.yaml` (not `k2_easy_subtraction_01_anchor.yaml`).
Single-tier filenames keep their historical `_<difficulty>_` token.

### Variable types (excerpt)

The full set lives in `src/yaml_loader.py:VALID_TYPES`. Most-used:

- numeric: `integer`, `decimal`, `fraction`, `ordinal`
- formatted numeric: `money`, `price`, `percentage`, `length`, `weight`,
  `temperature`, `area`, `volume`, `speed`
- compound physics (Stage 2): `density`, `energy`, `power`, `pressure`,
  `force`, `acceleration` — each rendered with a space and the per-system
  canonical suffix (`"750 kg/m³"`, `"1500 joules"`)
- entities: `person`, `name`, `city`, `store`, `restaurant`, `company`, `item`
- choice/string: `choice` (alias of `string`) — requires `choices: [...]`;
  also valid: `integer` with `choices: [...]` to constrain integer values
- time: `weekday`, `month`, `season`, `time`, `duration`

Adding a new variable type requires three changes:

1. Add to `VALID_TYPES` in `src/yaml_loader.py`.
2. Add a branch to `VariableGenerator._generate_value` in
   `src/variable_generator.py`.
3. If it has display formatting, extend `format_value` in the same file.

### Item categories

`{ type: item, category: <X> }` requires `<X>` to be in
`VALID_ITEM_CATEGORIES`. Currently: `grocery`, `electronics`, `clothing`,
`book`, `online`, `school`, `furniture`, `other`. Pools live in
`src/data/pools.<lang>.yaml` (only `pools.en.yaml` ships today; `providers.py`
loads them at import and exposes them as class attributes for backward
compat). To add a new category: add the entries under `items:` in
`pools.en.yaml`, declare a class-attribute alias in `MathProblemProvider`,
add to `VALID_ITEM_CATEGORIES`, and add a branch in
`VariableGenerator._generate_item`.

## Solution sandbox reference

The `solution:` block executes via `exec()` against a restricted
`safe_globals` dict in `src/solution_evaluator.py`. Available without
import:

```text
# builtins
abs round str int float min max sum pow len list range
sorted enumerate zip map filter any all

# math primitives (surfaced from stdlib `math` since Phase 5.1)
math pi e
sqrt exp
sin cos tan asin acos atan atan2
log log2 log10
floor ceil
factorial comb perm
radians degrees
gcd lcm

# numeric / locale
Decimal number_to_words

# symbolic algebra and statistical inference (namespaces)
sympy stats

# pint backbone (Stage 2)
ureg Q_ get_pint_unit
```

Math primitives are surfaced as a deliberate choice so that templates
write `sin(radians(30))` rather than `math.sin(math.radians(30))`. `sympy`
and `stats` (= `scipy.stats`) are namespaces — call as `sympy.solve(...)`,
`stats.norm.ppf(0.975)`, `stats.binom.pmf(k, n, p)`. **Two perf footguns**
to keep in mind for sympy: (a) `simplify()` blows up on large expressions —
call sparingly; (b) `sympy.Symbol` objects propagate through normal Python
operators, so accidental symbolic/numeric mixing balloons expression trees.

`Q_(value, unit)` builds a pint Quantity (`ureg.Quantity`); `ureg` is the
shared registry. `get_pint_unit(type, system)` returns the canonical
unit string from `DISPLAY_UNITS` (e.g. `"kilogram / meter ** 3"` for
`('density', 'metric')`) — the same source of truth the formatter uses,
so authors can never get out of sync. A solution that returns a Quantity
as `Answer` is unwrapped automatically: `format_answer` calls
`pint.Quantity.to(<canonical>)` for the answer's `(type, system)` and
prints the magnitude. This means the solution can mix units freely —
`Q_(1000, 'kg/m**3') * Q_(2, 'liter')` (which carries pint's compound
`kg·L/m³` unit, dimensionally `kg`) renders as `"2.00 kg"` for a metric
weight Answer, no manual `.to('kg')` needed.

`number_to_words` dispatches via the locale registry — for an `en`
template it produces "forty-two", for future languages it returns the
matching word form. `from X import Y` syntax technically works at runtime
but prefer the existing globals; if you need something not listed here,
add it to `safe_globals` rather than importing per-template.

The solution receives the rendered variable context and must assign
`Answer` (single-answer) or `Answer1`/`Answer2`/… (multi-answer). The
generator pipes-joins multi-answers as `"X | Y | Z"` for display.

## Locale and i18n foundation

`metadata.language` (default `en`) drives **language behaviour**:
locale-aware Jinja filters (`plural`, `ordinal`, `number_to_words`) and
the sandbox's `number_to_words`. `metadata.culture` (default `en-US`)
drives **regional behaviour**: it's normalized (`-` → `_`) and passed to
Faker as a locale, so cities/companies/store-names match the region.
The `names` library used for first names is en-only and ignores the
locale — this is a known limitation (see `TECHDEBT.md`).

Adding a language:

1. Copy `src/data/pools.en.yaml` to `pools.<lang>.yaml` and translate the
   entity strings (item names, weekdays, contexts).
2. In `src/i18n/languages.py`, register a `LanguageSpec` with `plural`,
   `ordinal`, and `number_to_words` callables. (English uses `inflect`;
   other languages can use `inflect` locale support, ICU, or hand-rolled
   rules.)
3. Set `language: <lang>` and `culture: <lang>-<REGION>` on the
   templates that should render in the new language.

No renderer, generator, or template-schema changes needed. Filters fall
back to `en` for unknown language codes.

## Unit systems

`metadata.unit_system` (default `mixed_us`) drives display-time unit and
currency choices. Three valid values:

| System     | Money | Length | Weight | Temperature | Speed | Area  | Volume |
| ---------- | ----- | ------ | ------ | ----------- | ----- | ----- | ------ |
| `mixed_us` | `$`   | m      | kg     | °F          | mph   | m²    | m³     |
| `metric`   | `€`   | m      | kg     | °C          | km/h  | m²    | L      |
| `imperial` | `$`   | ft     | lb     | °F          | mph   | ft²   | gal    |

Compound physics quantities (Stage 2) — `mixed_us` and `metric` use SI
across the board; only `imperial` swaps in physics-imperial units:

| System     | Density | Energy | Power | Pressure | Force | Acceleration |
| ---------- | ------- | ------ | ----- | -------- | ----- | ------------ |
| `mixed_us` | kg/m³   | J      | W     | Pa       | N     | m/s²         |
| `metric`   | kg/m³   | J      | W     | Pa       | N     | m/s²         |
| `imperial` | lb/ft³  | ft·lbf | hp    | psi      | lbf   | ft/s²        |

`mixed_us` reproduces pre-Phase-5.3 byte-identical output, so all 640
existing templates continue to render unchanged. New templates set
`unit_system: metric` (or `imperial`) for coherent display.

A variable can override the template default per-spec:

```yaml
metadata:
  unit_system: metric             # template default
variables:
  cost_us:
    type: money
    unit_system: imperial         # → "$" for this var only
  cost_eu:
    type: money                   # → "€" (template default)
```

The table itself lives in [src/units.py](src/units.py): edit `DISPLAY_UNITS`
to add a system or change a suffix. Each entry is
`(pint_unit_string, short_suffix_or_None, long_suffix)`; the pint unit
string is **validated at module load** via the project's `pint.UnitRegistry`
(typos like `"meeter"` fail loudly rather than silently rendering an
empty suffix later). Currency stays out of pint — `CURRENCY_SYMBOL` is a
small dict (`mixed_us` / `imperial` → `$`, `metric` → `€`). Currency
isn't a dimensional quantity and FX conversion needs out-of-process
rates.

**Stage 2 (since [0.2.5])**: solutions can return `pint.Quantity` values
as `Answer`. The formatter unwraps them via
`quantity_to_canonical_magnitude(value, type, system, unit_override=...)` —
pint converts to the canonical `(type, system)` unit (or to
`spec.unit` when set, see Stage 3 below) and the magnitude is printed.
This means a P-G3-shaped solution can do dimensional arithmetic
freely:

```python
density_q = Q_(density, get_pint_unit('density', 'metric'))
volume_q  = Q_(volume,  get_pint_unit('volume',  'metric'))
Answer = density_q * volume_q   # carries kg·L/m³ ≡ kg; formatter prints "2.00 kg"
```

Solutions returning plain floats (the legacy path) still work
unchanged — the conversion is a no-op for non-Quantity values.

**Stage 3 (since [0.2.6])** adds a free-form `unit:` field on
`VariableSpec` for one-off compound units that don't deserve a
dedicated type. The string is parsed via `ureg.parse_units()` at
load time (typos like `'meeter'` reject the template); the formatter
prints with pint's compact pretty form (`~P` → `m/s²`, `kg/m³`,
`mi/gal`). `unit:` always overrides the `(type, system)`-table
lookup, so `{type: weight, unit: 'gram'}` renders `"11 g"` regardless
of the template's `unit_system`.

```yaml
variables:
  acceleration: { type: decimal, unit: 'meter / second ** 2', min: 0.5, max: 9.81 }
  flow_rate:    { type: decimal, unit: 'liter / minute',      min: 1,   max: 20 }
  consumption:  { type: decimal, unit: 'mile / gallon',       choices: [22, 28, 35] }
```

Templates can use `{{<var>_unit}}` in Jinja and `<var>_unit` in the
solution sandbox — both are auto-injected from `spec.unit`:

```python
solution: |
  v_q = Q_(velocity, velocity_unit)               # uses auto-injected `velocity_unit`
  Answer = v_q.to('kilometer / hour').magnitude   # P-M1-style conversion
```

Pint conventions to know: `liter` and `'L'` both render as lowercase
`'l'`; alphabetical ordering applies to compound units (`'newton *
meter'` → `'m·N'`). For unit strings pint can't parse cleanly (e.g.
fuel-economy `'L/100km'` requires a scaling factor pint disallows),
hardcode the math in the solution.

## Visual layer

Templates may include an optional `visual:` block. The YAML stores the
**canonical source** (today: a Jinja2-rendered SVG string); a separate
`mathbot rasterize` step produces PNGs at any DPI. Both ship in the
dataset. Templates **must never write PNG-generation code** — losing
the source means losing the ability to re-render at a different
resolution.

Schema:

```yaml
visual:
  format: svg                                # only svg today; `python` is roadmap
  alt_text: "Plain-language description with {{var}} substitution"
  source: |
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
      <!-- Same Jinja2 context as `template:` — substitute variables here. -->
      <rect width="{{w}}" height="{{h}}" fill="none" stroke="black"/>
    </svg>
```

The renderer ([src/template_generator.py](src/template_generator.py))
adds `output["visual"] = {format, source, alt_text}` to the output JSON.
`output["visual"]["png_path"]` is appended later by `mathbot rasterize`.

`mathbot rasterize <dataset.json|.jsonl>` reads rows with a
`visual.source` SVG, writes one PNG per row to a sidecar directory
(default `<dataset>.pngs/`), and augments each row with `visual.png_path`
(relative path so the dataset stays portable). Re-runnable at any DPI
(`--dpi 300`) or fixed pixel width (`--width 600`) from the same SVG
source.

System dep: requires `libcairo` (macOS: `brew install cairo`,
Debian/Ubuntu: `apt install libcairo2`). The Python wheel `cairosvg`
ships under the `png` optional extra (`uv sync --extra png`); the rest
of mathbot has zero raster dependencies.

Author guidance:
- Keep the SVG schematic, not to scale — show shape, label conveys
  value (e.g. always render a 120-pixel square regardless of `{{side}}`,
  with `{{side}}` in the labels).
- Use `viewBox` (not absolute `width`/`height`) so the rasterizer can
  pick any output size.
- Reference variables with the same `{{var}}` syntax as the problem
  template — the same context dict is passed to both.

Approach B (Python `SVG`/`TreeSVG`/`BarChartSVG` builder classes inside
the solution sandbox, for derived-coordinate cases like probability
trees and bar charts) is roadmap — see TECHDEBT.md TD-3.1b.

## Jinja2 conventions

Solution-defined variables are NOT visible to the template — solution runs
*after* render. To use a derived value in the problem text, compute it via
`{% set %}` at the top of the `template:` block:

```jinja
{% set dividend = (number1 // number2) * number2 %}
{{name}} has {{dividend}} {{object_plural}} to share among {{number2}} friends.
```

Five K3 division templates referenced solution-only variables and rendered
empty whitespace until v0.1.3 fixed them with this pattern.

**Jinja list comprehensions don't work** in `{% set %}`:

```jinja
{# WRONG — Jinja syntax error #}
{% set y_data = [slope * x + intercept for x in x_data] %}

{# RIGHT — inline {% for %} loop #}
{% for x in x_data %}({{x}}, {{slope * x + intercept}}){% if not loop.last %}, {% endif %}{% endfor %}
```

Variables of formatting types (money/percentage/etc.) get an auto-suffixed
`{{<name>_formatted}}` companion at render time (e.g. `total_formatted` =
`"$60.00"` while `total` = `60.0`). Use the `_formatted` form in problem
text and the raw form for math in `{% set %}`.

Variables that declare a free-form `unit:` (Stage 3) similarly get a
`{{<name>_unit}}` companion carrying the raw pint string (e.g.
`velocity_unit` = `"meter / second"`). Available in both Jinja and the
solution sandbox so a template can do `Q_(velocity, velocity_unit)`
without hardcoding the unit twice.

## Anchor convention

Filename suffix `_anchor.yaml` marks the canonical template for a
`(grade, topic, family, difficulty)` quadruplet (358 anchors as of v0.1.3).
When adding a new template to an existing quadruplet:

- if the math operation/step-count differs meaningfully from the anchor,
  it's a non-anchor variant — name it without the suffix
- if it's the same operation/step-count just with different surface (item
  type, person name, number ranges), don't add it — that's the duplication
  pattern Phase 4 cleared out

## Multi-answer tests

Use a single `answer:` field with pipe-joined values:

```yaml
tests:
  - seed: 12345
    expected:
      answer: "73 | 3 | 24 | 1"          # ✓ canonical
      # answer1: "73"                    # ✗ legacy, ignored by `mathbot test`
      # answer2: "3"                     # ✗
```

The CLI test runner reads `expected.answer` only. Legacy `answerN:` keys
were stripped in v0.1.3 by `scripts/refresh_test_answers.py`.

## Tooling

- `mathbot verify <path>` — schema validation only; does not run tests.
- `mathbot test <path>` — runs the template's embedded `tests:` block.
- `mathbot lint [PATH] [--json] [--strict] [-k 4]` — per-template
  audit: schema, render-smoke (K seeds), visual-render smoke, fixture
  drift / coverage, anchor convention, off-anchor divergence (variant's
  variable set / step count vs anchor in same cell), plus rendered-
  output rules (unrendered Jinja, GSM8K saturation patterns, body
  length, unit-form drift, area/volume answer heuristics). With no
  PATH lints the whole corpus in ~5s. JSON to stdout via `--json`,
  one-line stderr summary always, exit 1 on errors. `--strict` treats
  warnings as errors. `--rules a,b,c` runs a subset.
- `mathbot health [--json] [-k 4] [--top-pairs 50]` — corpus-level:
  coverage matrix per `(grade, topic, family, difficulty)` cell,
  density (top over-densified cells, singleton families), within-cell
  near-dupes (SequenceMatcher ≥ 0.85 with `structurally_flat_difficulty`
  flagging for cross-tier ≥ 0.95), cross-template contamination
  (K-shingle Jaccard, max-neighbor per template, top-N pairs).
- `scripts/refresh_test_answers.py [--apply] [--filter '<glob>'] [-v]` —
  surgical regenerator using ruamel.yaml round-trip mode (preserves
  comments, key order, quoting). Run after editing any template's solution
  or after generator changes that affect RNG/output.
- `scripts/gsm8k_contamination.py` — external-corpus check vs the
  GSM8K train split. Stays separate (HF dataset download, network);
  not part of `mathbot health`.
- `migrate_templates.py` was deleted in Phase 5.1 (was broken, lossy);
  use `scripts/refresh_test_answers.py` for any template rewriting.

## Spec-mandated families

Every problem ultimately maps to one of these (or a hybrid):

| Family                  | Pattern                                              |
| ----------------------- | ---------------------------------------------------- |
| `sequential_purchase`   | Multi-step shopping with discounts/budget            |
| `rate_time`             | Distance ↔ speed ↔ time, multi-segment               |
| `compound_growth`       | Interest, percent change chain over N periods        |
| `multi_person_sharing`  | Splitting amounts by ratio, transfer, or constraint  |
| `area_perimeter_chain`  | Geometry with area→side→perimeter or similar         |

K7-K12 expansion is guided by `mathbot-phase4-problem-proposals.md` (root
of repo): a synthesis of K-12 curricula across eight education systems
with 27 concrete proposals, of which the v0.1.3 anchors implement all 27.

## Output format

```json
{
  "test_id": "math_<id>",
  "task_type": "multi_step_math",
  "config_name": "<grade>_<difficulty>_<family>",
  "problem": "Sarah goes shopping…",
  "task_params": {
    "complexity": 1 | 2 | 3,
    "grade": "k<N>",
    "math_topic": ["arithmetic"],
    "problem_family": "sequential_purchase",
    "num_steps": 5,
    "expected_answer": "$6.94",
    "operations": ["multiply", "add"]
  },
  "template_path": "src/templates/arithmetic/k7_medium_sequential_budget_anchor.yaml"
}
```

`expected_answer` is always a string with units/formatting baked in.

## Known quirks

- Some legacy templates have unit-display bugs (e.g. trapezoidal-area
  problem stated in cm with answer in "meters"). Self-tests pass because
  they enshrine the buggy output as ground truth. Fix at the template
  level when you encounter one — don't patch the generator.
- `mathbot batch` retries up to `count * 10` times on no-template-match
  before giving up. If a `(grade, topic, family)` combo is sparse, the
  warning lands on stderr.
- The `.venv` warning about `VIRTUAL_ENV` mismatching is from the host
  shell, not the project — `uv run` works correctly regardless.
