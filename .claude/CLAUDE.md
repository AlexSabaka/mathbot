# Mathbot — development guide

Procedural multi-step math word-problem generator. The corpus is a tree of
hand-authored YAML templates rendered with Jinja2 and post-processed by a
small Python sandbox; deterministic from a seed; produces problems with
verifiable answers for K1-K12.

## Quick start

```bash
uv sync                                                 # install deps + .venv (Python 3.12)
uv run pytest                                           # 60 tests
uv run mathbot generate -c 2 -g elementary -t arithmetic -s 42  # one problem
uv run mathbot batch 10 -s 1 -o json                    # 10 problems → stdout
uv run mathbot verify <path/to/template.yaml>           # validate one template
uv run mathbot test    <path/to/template.yaml>          # run its embedded tests
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
  difficulty: easy | medium | hard
  steps: 5                              # number of reasoning steps
  language: en                          # optional, BCP-47 base; drives locale-aware filters
  culture: en-US                        # optional, BCP-47 region; drives Faker locale (names/cities)
  unit_system: mixed_us                 # optional, default mixed_us; metric|imperial|mixed_us
  tags: [list, of, tags]

variables:
  name:           { type: person }
  budget:         { type: integer, choices: [40, 60, 100] }
  price1:         { type: integer, min: 8, max: 18 }
  Answer:         { type: string }

template: |        # Jinja2; rendered to the displayed problem text
  {{name}} walks in with $${{budget}}…

solution: |        # Python; executes after rendering, must assign Answer
  Answer = …

tests:             # 3+ cases recommended; seed is the canonical RNG seed
  - seed: 12345
    expected:
      answer: "bought 5 items, $2 left"
```

### `metadata.topic` ↔ directory invariant

A template under `src/templates/<X>/` must declare `topic: X.<subtopic>`.
Bare topics like `topic: arithmetic` are not allowed; cross-directory topics
(`measurement/k3_easy_area_01.yaml` with `topic: geometry.measurement`) were
harmonized away in v0.1.3. **Enforced** by `YAMLLoader._validate_template`
since Phase 5.1 — a mismatched template fails to load with a clear error.
New top-level dirs require updating `MATH_TOPICS` in `src/constants.py`.

### Variable types (excerpt)

The full set lives in `src/yaml_loader.py:VALID_TYPES`. Most-used:

- numeric: `integer`, `decimal`, `fraction`, `ordinal`
- formatted numeric: `money`, `price`, `percentage`, `length`, `weight`,
  `temperature`, `area`, `volume`, `speed`
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
```

Math primitives are surfaced as a deliberate choice so that templates
write `sin(radians(30))` rather than `math.sin(math.radians(30))`. `sympy`
and `stats` (= `scipy.stats`) are namespaces — call as `sympy.solve(...)`,
`stats.norm.ppf(0.975)`, `stats.binom.pmf(k, n, p)`. **Two perf footguns**
to keep in mind for sympy: (a) `simplify()` blows up on large expressions —
call sparingly; (b) `sympy.Symbol` objects propagate through normal Python
operators, so accidental symbolic/numeric mixing balloons expression trees.

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

The table itself lives in [src/units.py](src/units.py); add a new system
or change a suffix by editing `UNIT_TABLE`. Currency-vs-system coupling
is intentional today (one currency per system); split out later if a
template wants £ on metric or ¥ on its own. **Solutions still compute in
system-native units** — the table only handles display. For
unit-conversion problems (P-M1 family from the K7-K12 proposal),
templates do the conversion arithmetic explicitly in the solution code
with hard-coded factors, then format the result.

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

- `scripts/refresh_test_answers.py [--apply] [--filter '<glob>'] [-v]` —
  surgical regenerator using ruamel.yaml round-trip mode (preserves
  comments, key order, quoting). Run after editing any template's solution
  or after generator changes that affect RNG/output.
- `mathbot verify <path>` — schema validation only; does not run tests.
- `mathbot test <path>` — runs the template's embedded `tests:` block.
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
