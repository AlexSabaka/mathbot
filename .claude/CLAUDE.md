# Mathbot — development guide

Procedural multi-step math word-problem generator. The corpus is a tree of
hand-authored YAML templates rendered with Jinja2 and post-processed by a
small Python sandbox; deterministic from a seed; produces problems with
verifiable answers for K1-K12.

## Quick start

```bash
uv sync                                                 # install deps + .venv (Python 3.12)
uv run pytest                                           # 35 tests
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
├── cli.py               Click commands: generate, batch, verify, test, list, info
├── generator.py         Module API: generate_problem(), generate_problems()
├── template_generator.py  Loads + indexes templates; per-template generation
├── yaml_loader.py       YAMLLoader: schema validation + TemplateDefinition dataclass
├── jinja_renderer.py    Jinja2 env with custom choice/plural/format filters
├── variable_generator.py  Generates random values per VariableSpec.type
├── solution_evaluator.py  Executes solution code in safe sandbox; formats answer
├── providers.py         Faker provider: GROCERY_ITEMS, ELECTRONICS_ITEMS, …
├── constants.py         MATH_TOPICS, PROBLEM_FAMILIES, GRADES enums
└── templates/<topic>/*_anchor.yaml  + variants
scripts/
└── refresh_test_answers.py  Surgical test-answer regenerator (ruamel.yaml)
tests/                   pytest suite for CLI + generator API
mathbot-phase4-problem-proposals.md  Curriculum reference for K7-K12 expansion
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
  topic: arithmetic.multi_step          # MUST start with parent dir name
  family: sequential_purchase           # see PROBLEM_FAMILIES
  difficulty: easy | medium | hard
  steps: 5                              # number of reasoning steps
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
harmonized away in v0.1.3. New top-level dirs require updating
`MATH_TOPICS` in `src/constants.py`.

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
`src/providers.py`. To add a new category: add the `*_ITEMS` constant to
the provider, add to `VALID_ITEM_CATEGORIES`, and add a branch in
`VariableGenerator._generate_item`.

## Solution sandbox reference

The `solution:` block executes via `exec()` against a restricted
`safe_globals` dict in `src/solution_evaluator.py`. Available without
import:

```text
abs round str int float min max sum pow len list range
sorted enumerate zip map filter any all
math gcd lcm Decimal number_to_words
```

`gcd` and `lcm` are exposed directly as a deliberate choice — fraction and
divisibility templates use them heavily and forcing per-template imports
is friction. `from X import Y` syntax technically works at runtime but
prefer the existing globals; if you need something not listed here, add
it to `safe_globals` rather than importing per-template.

The solution receives the rendered variable context and must assign
`Answer` (single-answer) or `Answer1`/`Answer2`/… (multi-answer). The
generator pipes-joins multi-answers as `"X | Y | Z"` for display.

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
- **`migrate_templates.py` is broken** — its `--update-tests` is gated on a
  no-longer-firing format→type migration check, and it rewrites with
  `yaml.dump` (lossy). Don't use it; will be removed.

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
