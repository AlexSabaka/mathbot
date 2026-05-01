# Mathbot Template Specification

> **Version**: 3.0
> **Last Updated**: 2026-04-27
> **Audience**: Template authors and maintainers
> **Companion**: [.claude/CLAUDE.md](../../.claude/CLAUDE.md) — developer / project guide

This is the formal reference for the YAML template format. CLAUDE.md
covers the project from a developer's perspective; this document is
the authoring spec — the contract between a template file and the
generator.

---

## 1. Quick start

A minimal valid template:

```yaml
metadata:
  id: k1_easy_addition_01
  version: "1.0.0"
  author: Your Name
  created: 2026-04-27
  grade: 1
  topic: arithmetic.addition
  family: addition
  difficulty: easy
  steps: 1

variables:
  a:      { type: integer, min: 1, max: 9 }
  b:      { type: integer, min: 1, max: 9 }
  Answer: { type: integer }

template: |
  What is {{a}} + {{b}}?

solution: |
  Answer = a + b

tests:
  - seed: 12345
    expected:
      answer: "7"
```

After authoring, populate the test answer with
`uv run python scripts/refresh_test_answers.py --apply --filter '*/<file>.yaml'`,
then run `uv run mathbot lint <path>` and `uv run mathbot test <path>`
to verify.

---

## 2. File layout & naming

Templates live under `src/templates/<topic>/<filename>.yaml`. Two
filename conventions:

- `<id>_anchor.yaml` — the **canonical anchor** for a `(grade, topic,
  family, difficulty)` cell. Each cell allows exactly one anchor;
  authors look at it as the reference shape when adding variants.
- `<id>.yaml` — a **non-anchor variant** in the same cell. Should
  share the operation/step-count/variable-shape of its anchor; only
  the surface (item names, number ranges, prompt phrasing) varies.

The `metadata.topic` field must start with the parent directory's
name. A template under `src/templates/arithmetic/` with
`topic: geometry.shapes` is rejected at load time. New top-level
topics require an entry in `MATH_TOPICS` in
[src/constants.py](../constants.py).

Multi-tier templates (see §7) drop the difficulty token from the
filename: `k2_subtraction_01_anchor.yaml`, not
`k2_easy_subtraction_01_anchor.yaml`.

---

## 3. Top-level structure

```yaml
metadata: { ... }      # required
variables: { ... }     # required, must include Answer or Answer1/Answer2…
template: |            # required, Jinja2
solution: |            # required, Python
tests: [ ... ]         # recommended, ≥1 fixture
visual: { ... }        # optional, Phase 5.5
```

`metadata`, `variables`, `template`, `solution` are required.
`tests` is technically optional but `mathbot lint` flags
`fixture_missing` when absent, and the corpus enforces ≥1 fixture
per template (per tier for multi-tier — see §7).

---

## 4. `metadata` reference

### Required fields

| Field        | Type   | Constraint / example                                              |
| ------------ | ------ | ----------------------------------------------------------------- |
| `id`         | string | Unique. Must match the filename stem minus `_anchor`.             |
| `version`    | string | Semver string in quotes: `"1.0.0"`.                               |
| `author`     | string | Free-form name.                                                   |
| `created`    | date   | `YYYY-MM-DD`.                                                     |
| `grade`      | int    | 1–12.                                                             |
| `topic`      | string | `<dir>.<subtopic>` (e.g. `arithmetic.multi_step`). Top-level dir must match the file's parent directory. |
| `family`     | string | One of [`PROBLEM_FAMILIES`](../constants.py).                     |
| `difficulty` | string | `easy` \| `medium` \| `hard`.                                     |
| `steps`      | int    | Number of solution steps (used by `mathbot lint` step-count drift detection). |

### Optional fields

| Field              | Type         | Default       | Notes                                                   |
| ------------------ | ------------ | ------------- | ------------------------------------------------------- |
| `language`         | string       | `en`          | BCP-47 base. Drives locale-aware Jinja filters and sandbox `number_to_words`. See §10. |
| `culture`          | string       | `en-US`       | BCP-47 region. Drives Faker locale (cities, companies, store names). |
| `unit_system`      | string       | `mixed_us`    | `mixed_us` \| `metric` \| `imperial`. See §8.            |
| `difficulty_tiers` | list[string] | none          | When set, template renders at multiple tiers. Must include `difficulty`. See §7. |
| `tags`             | list[string] | `[]`          | Free-form keywords.                                     |
| `notes`            | string       | none          | Free-form internal documentation.                       |
| `track`            | string       | none          | Curriculum track for eval slicing: `core` \| `advanced` \| `tertiary` \| `US-emphasized`. K9+ templates without it get a `track_missing` info finding from `mathbot lint`. See §4.1. |
| `structural_tags`  | list[string] | `[]`          | Cross-cutting structural-pattern tags. T1–T12 cover surface skeletons (running_total, multi_person_sharing, …); T13–T17 target K9+ LLM-eval failure modes (compositional chain, formula recall, method selection, selective attention to noop clauses, inverse query). See §4.2. |
| `direction`        | string       | none          | `forward` \| `inverse`. Optional toggle for templates that render in two query directions (N1 inverse functions, N4 year-to-target, N8 log inversion, N15 time-to-target ODE). The solution sandbox can branch on it. |
| `noop_clauses`     | list[string] | `[]`          | **DEPRECATED in Phase γ.** Superseded by `simplifications:` + `T18_assumption_omission`. Still works through 0.6.x; removal scheduled for 0.7.0 (γ.5). See §4.3 and §11. |
| `simplifications`  | list[obj]    | `[]`          | Stated simplifying assumptions with per-tier suppression. Each entry: `{text: <jinja-string>, omit_at: [tier...]}`. Renderer concatenates active entries (those whose `omit_at` doesn't include the active tier) into the `{{ simplifications }}` Jinja variable. K12-appropriate replacement for noop injection. See §4.4. |
| `figure_load`      | string \| dict | none        | How load-bearing the visual is for solving: `none` \| `decorative` \| `partial` \| `load_bearing`. Either a single value (every tier) or a `{tier: value}` mapping. Used by `mathbot lint`'s `figure_load_inconsistent` warning to flag prose ↔ figure mismatches. See §4.5. |

### 4.1 Track values

`track:` tags a template with its position relative to the eight
cross-curriculum reference systems (CCSS HSA/HSF/HSG/HSN/HSS, Singapore
H2/H3, Japan Math I–III/A/B/C, Finland LOPS MAA1–13, Norway LK20
R1/R2, Sweden Mat 1a–5, Estonia gümnaasium, NL HAVO/VWO wiskunde
A–D). Use it so eval pipelines can carve a CCSS-core view out of the
internationally-aggressive K12 material.

| Value | When to use |
| --- | --- |
| `core` | Universal across the 8 references. Most K1–K8 plus quadratics, basic statistics, polynomial arithmetic at K9, etc. |
| `advanced` | Advanced/optional track in most references — CCSS-(+), Singapore H2, Japan Math III, Finland MAA7+, Norway R2. Trig identities, basic conic sections, single-variable calculus. |
| `tertiary` | First-year-university material in most references — eigenvalues, second-order ODEs, L'Hôpital's rule, multivariable / vector calc. CCSS-absent. |
| `US-emphasized` | Topics over-weighted in CCSS relative to international norms — piecewise functions, conic sections beyond circle, two-column proofs. Not wrong, just a US-pedagogical accent. |

### 4.2 Structural-tag taxonomy

Tags are orthogonal to `family:` — a single template carries multiple
when more than one pattern applies. T13–T17 are motivated by the
literature pointers in MATHBOT_PROBLEMS_PROPOSAL_v2.md §6 and Appendix
B; the closed set is enforced at load time.

| Tag | Meaning |
| --- | --- |
| `running_total` | Multi-step accumulation; each step adds to / subtracts from a running quantity. |
| `multi_person_sharing` | Splitting amounts by ratio, transfer, or constraint across N people. |
| `sequential_purchase` | Buy A, then B with the change, possibly with discounts. |
| `rate_time` | Distance ↔ speed ↔ time, multi-segment / acceleration / motion-graph. |
| `area_perimeter_chain` | Area → side → perimeter or analogous geometric chains. |
| `compound_growth` | Repeated percent change / interest / depreciation. |
| `mixture_alloy` | Weighted average of two or more streams. |
| `multi_step_purchase` | Multi-stage shopping with stacked discounts/taxes. |
| `division_with_remainder` | Quotient + remainder where the remainder carries semantic meaning. |
| `fraction_of_a_quantity` | "(p/q) of N" with multi-step prerequisite. |
| `percentage_change` | "X% increase / decrease" possibly chained. |
| `unit_conversion_chain` | Dimensional analysis with two or more conversions. |
| `T13_symbolic_chain` | Multi-step symbolic transformation; each step's output feeds the next. Compositional-GSM motivation. |
| `T14_formula_recall` | Selecting which formula applies before substitution. MATH-P-Hard / UGMathBench motivation. |
| `T15_method_selection` | Specialisation of T14 where parameter randomisation is *required* to sometimes change the optimal method. Putnam-AXIOM motivation. |
| `T16_selective_attention` | Templates supporting `+noop` injection of irrelevant text. GSM-NoOp motivation. |
| `T17_inverse_query` | Inverse-direction of a forward problem (given output, find parameter). Pairs with `direction:`. |
| `T18_assumption_omission` | Multi-tier templates whose hard-tier suppresses a stated simplifying assumption from easy/medium. Pairs with `simplifications:`. K12 replacement for the retired `T16_selective_attention` (which was grade-school-flavoured GSM-NoOp). |

### 4.3 Noop-clause mechanism (DEPRECATED — Phase γ)

> **Deprecated in 0.6.0 (Phase γ.1).** Superseded by §4.4
> `simplifications:` + `T18_assumption_omission`. The K12 analog of
> the GSM-NoOp perturbation isn't *injecting* irrelevant prose
> (grade-school surface noise) but *suppressing* a stated
> simplifying assumption. New templates should use `simplifications:`;
> existing `noop_clauses:` keep working through the 0.6.x cycle and
> the field is scheduled for removal in 0.7.0 (γ.5).

`noop_clauses:` is the GSM-NoOp perturbation hook. The pool entries
are themselves Jinja templates that share the variable context with
the body, so a clause can reference template variables for plausibility
("Earlier in the day, {{person}} was browsing for shoes."). The
`{{ noop_clause }}` Jinja variable defaults to an empty string so a
template that ships a pool stays byte-identical when rendered without
`inject_noop`.

```yaml
metadata:
  noop_clauses:
    - "Earlier in the day, {{person}} was browsing for shoes."
    - "Note that {{store}} also sells umbrellas."
template: |
  {{ noop_clause }} {{person}} bought {{count}} apples for {{price}} each.
  How much did they pay?
```

`mathbot lint` errors with `noop_clauses_no_slot` if the pool is
non-empty but `template:` lacks a `{{ noop_clause }}` reference.

### 4.4 Simplifying-assumption mechanism

`simplifications:` is the K12-appropriate replacement for noop
injection. Each entry is a stated modeling assumption; `omit_at`
lists the tiers where the entry is *suppressed* from the rendered
prose. At easy tier the template tells the solver "treat the cup as
a perfect cone"; at hard tier the same line disappears and the
solver has to recognise the modeling step on their own. The
substantive difficulty axis is *which assumptions are stated*, not
which numbers are bigger.

```yaml
metadata:
  difficulty: easy
  difficulty_tiers: [easy, medium, hard]
  structural_tags: [T18_assumption_omission]
  simplifications:
    - text: "Treat the cup as a perfect cone."
      omit_at: [hard]
    - text: "Assume the speed of the water is negligible."
      omit_at: [medium, hard]   # only stated at easy
    - text: "Take {{g}} = 9.81 m/s² for gravity."
      # omit_at omitted → always stated
template: |
  A circular sheet of paper… {{ simplifications }}
  Find the height of the cup.
```

The `{{ simplifications }}` Jinja variable expands to the active
entries, space-joined, each rendered against the same context as
`template:`. Empty when nothing is active for the current tier.

Pairs with `T18_assumption_omission`. `mathbot lint` warns when a
multi-tier template carrying `simplifications:` has no entry whose
`omit_at` differs across tiers — a flat pool defeats the
"suppression-as-difficulty" purpose.

### 4.5 Figure load

`figure_load:` declares how load-bearing a visual is for solving the
problem. Four values, ordered by how much information lives in the
figure rather than the prose:

| Value          | Meaning |
| -------------- | --- |
| `none`         | Template has no `visual:` block. |
| `decorative`   | Figure illustrates but the prose is sufficient — solver could ignore the figure and still solve. |
| `partial`      | Figure carries some quantities; prose carries the rest. |
| `load_bearing` | Figure is **required** — quantities only appear on it. |

A single value applies at every tier; per-tier mapping varies the
load by difficulty (a riverbank diagram might be `decorative` at easy
and `load_bearing` at hard once the prose is stripped of widths).

```yaml
metadata:
  figure_load: load_bearing            # all tiers

# or:
metadata:
  figure_load:
    easy: decorative
    medium: partial
    hard: load_bearing
```

`mathbot lint` flags `figure_load_inconsistent` when prose and
declared load disagree (e.g. prose says "as shown in the figure" but
`figure_load: decorative`).

### Validation rules

- `topic` parent must equal the file's containing directory.
- `unit_system` must be one of the three valid values.
- `difficulty_tiers` (if set) must be a list of valid tier names that
  contains `difficulty`.
- `track` (if set) must be one of `core` / `advanced` / `tertiary` /
  `US-emphasized`. Unset is allowed at K1–K8; K9+ templates without it
  surface as `track_missing` info findings.
- `structural_tags` (if set) must be a list drawn from the closed set
  in §4.2.
- `direction` (if set) must be `forward` or `inverse`.
- `noop_clauses` (if set, deprecated) must be a list of strings;
  pairs with a `{{ noop_clause }}` slot in `template:`.
- `simplifications` (if set) must be a list of `{text, omit_at}`
  mappings; each `omit_at` entry must name a valid difficulty tier.
- `figure_load` (if set) must be a single value from
  `{none, decorative, partial, load_bearing}` or a `{tier: value}`
  mapping over those values.
- `T18_assumption_omission` is the structural tag that goes with
  `simplifications:`; it's a regular member of `VALID_STRUCTURAL_TAGS`
  and not separately required.

---

## 5. `variables` reference

Every variable definition is `{ type: <type>, ... }`. Type is
required; remaining fields depend on the type.

### Active types

The full list is in [`VALID_TYPES`](../yaml_loader.py). Grouped:

#### Numeric integer

- `integer` — int with `min`/`max`/`step` or `choices`.
- `ordinal` — int rendered as `"3rd"` / `"21st"` (locale-aware).

#### Numeric decimal

- `decimal` — generic float; `min`/`max`/`step` or `choices`.
- `money`, `price` — currency-aware (`$` / `€` per `unit_system`).
  2-decimal display by convention.
- `percentage` — int formatted without `%` in problem text (the
  template adds it: `"{{rate}}%"`); answer renders with `%`.

#### Unit-aware (system-specific suffix)

`length`, `weight`, `temperature`, `area`, `volume`, `speed` — each
generates a number; the formatter appends a system-aware suffix
(see §8 for the table).

- Problem-text format ("short suffix"): `"5m"`, `"5kg"`,
  `"72.0°F"`, `"5 m²"`. Speed and volume return bare numbers in
  problem text and let the template phrase the unit.
- Answer-text format ("long suffix"): `"12 meters"`, `"5.50 kg"`,
  `"45.00 mph"`, `"8 cubic meters"` (etc).

#### Compound physics quantities (Stage 2)

`density`, `energy`, `power`, `pressure`, `force`, `acceleration`
— rendered with a space and the per-system canonical suffix:
`"750 kg/m³"`, `"1500 joules"`, `"9.81 m/s²"`. See §8.

These pair with the sandbox `Q_` / `ureg` / `get_pint_unit` (see §9.2)
for dimensional-arithmetic solutions.

#### Entity (string-typed)

- `person`, `name` — first names via `names` library (en-US only;
  ignores `culture`).
- `location`, `city` — Faker cities for `culture`.
- `store`, `restaurant`, `company` — Faker fakers for `culture`.
- `item` — picks from a category pool (see §5.3).

#### Time / date

- `weekday`, `month`, `season` — picks from per-locale calendar in
  `src/data/pools.<lang>.yaml`.
- `time` — float hours; rendered as `"2 hours 30 minutes"`.
- `duration` — alias.

#### Other

- `boolean` — `True` / `False`; optional `probability` in [0, 1]
  (default 0.5).
- `string`, `choice` — picks from `choices: [...]` (required).

### Common fields

| Field            | Applies to                | Notes                                                                                |
| ---------------- | ------------------------- | ------------------------------------------------------------------------------------ |
| `min`            | numeric / time            | inclusive lower bound                                                                |
| `max`            | numeric / time            | inclusive upper bound                                                                |
| `step`           | numeric / time            | grid step (e.g. 0.25). `(max-min)` should be divisible by `step` (warning otherwise) |
| `choices`        | numeric / string / choice | enumeration; takes priority over `min`/`max` for numeric types                       |
| `category`       | item                      | one of [`VALID_ITEM_CATEGORIES`](../yaml_loader.py): `grocery`, `electronics`, `clothing`, `book`, `online`, `school`, `furniture`, `other` |
| `singular`       | item                      | `true` returns `"apple"`, `false` (default) returns `"apples"`                        |
| `probability`    | boolean                   | 0.0–1.0 (default 0.5)                                                                |
| `unit_system`    | any                       | per-variable override of the template's `metadata.unit_system`                       |
| `unit`           | numeric                   | free-form pint unit string (Stage 3 — see §8.3)                                       |
| `ranges`         | any                       | per-difficulty overrides for multi-tier templates (see §7)                            |

### Item categories

`{ type: item, category: <cat> }` requires `cat` to be in
`VALID_ITEM_CATEGORIES`. Pools live in `src/data/pools.<lang>.yaml`.

To add a new category: add the entries under `items:` in
`pools.en.yaml`, declare a class-attribute alias in
`MathProblemProvider`, add the category to `VALID_ITEM_CATEGORIES`,
and add a branch in `VariableGenerator._generate_item`.

### `Answer` is required

Every template must declare an answer variable:

- **Single-answer**: `Answer: { type: <type> }`.
- **Multi-answer**: `Answer1`, `Answer2`, … (no `Answer` in this case).
  The generator pipes-joins formatted answers as `"X | Y | Z"` for the
  rendered `expected_answer`.

Answer variables follow the same type rules as inputs — `Answer:
{ type: money }` formats as currency, `Answer: { type: weight }`
formats with the system-aware long suffix.

---

## 6. `template` (Jinja2)

The `template:` block is rendered with Jinja2 against the variable
context. It produces the problem text shown to the model.

### Math notation in body prose

Use **plain Unicode** (`x²`, `∫`, `≤`, `π`) or descriptive prose
("the integral of f(x) = x² + 1 from x = 0 to x = 2"). Do **not**
use LaTeX delimiters (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`).

Why: the body string is rendered identically across all output
formats. The text / SVG / PNG paths can't typeset LaTeX — they
splice the string verbatim into a `<text>` element or terminal
output, so `$$\int_0^2 (x^2+1)dx$$` shows up as raw `$$\int_0^2…$$`
text. The markdown / LaTeX / PDF paths *would* typeset it, but
that breaks the cross-format consistency invariant Phase γ
requires (review feedback during gold-standard #4 surfaced this).

KaTeX integration (deferred) will let the SVG composite typeset
math too; at that point, LaTeX delimiters in body prose become
safe across every format. Until then, stick to plain Unicode.

### Auto-injected companions

For every variable of a unit-aware / formatted type, the renderer
injects a `<name>_formatted` companion carrying the display string
(`{{total_formatted}}` = `"$60.00"` while `total` = `60.0`).
Use `_formatted` in problem text and the raw form in `{% set %}` math.

For variables that declare a free-form `unit:`, the renderer injects
`<name>_unit` carrying the raw pint string. Available in both Jinja
and the solution sandbox so you don't hardcode the unit twice.

### Solution-derived values

Solution variables are NOT visible in the template — solution runs
*after* render. To use a derived value in the problem text, compute
it via `{% set %}` at the top of the `template:` block:

```jinja
{% set dividend = (number1 // number2) * number2 %}
{{name}} has {{dividend}} {{object_plural}} to share among {{number2}} friends.
```

### Caveats

- **Jinja list comprehensions don't work** in `{% set %}`:

  ```jinja
  {# WRONG — Jinja syntax error #}
  {% set y_data = [slope * x + intercept for x in x_data] %}

  {# RIGHT — inline {% for %} loop #}
  {% for x in x_data %}({{x}}, {{slope * x + intercept}}){% if not loop.last %}, {% endif %}{% endfor %}
  ```

- **No literal `{{...}}` in rendered output**. `mathbot lint` flags
  `unrendered_jinja` (error) when the renderer emits something that
  still looks like a template directive — usually a sign that a
  solution-only variable was referenced without a `{% set %}`.

### Locale-aware filters

Three filters dispatch via `metadata.language` (defaults to `en`):

- `{{n | plural("apple")}}` → `"apples"` for n≠1, `"apple"` for n=1.
- `{{n | ordinal}}` → `"3rd"` (en); locale-specific for other languages.
- `{{n | number_to_words}}` → `"forty-two"` (en).

Other filters: `choice`, `list_and`, `format_money`, `capitalize`.
See [src/jinja_renderer.py](../jinja_renderer.py) for the registered set.

---

## 7. Multi-tier templates

A single YAML can render at multiple difficulty tiers when its
metadata declares:

```yaml
metadata:
  difficulty: easy                       # default tier
  difficulty_tiers: [easy, medium, hard] # must include `difficulty`

variables:
  num_a:
    type: integer
    ranges:                              # per-tier min/max/step/choices overrides
      easy:   { min: 30,  max: 50 }
      medium: { min: 150, max: 300 }
      hard:   { min: 250, max: 500 }
  pace:
    type: integer
    ranges:                              # per-tier choices lists
      easy:   { choices: [10, 100] }
      medium: { choices: [10, 100, 1000] }
```

A variable's `ranges:` entry overrides the flat `min`/`max`/`step`/
`choices` for that tier; tiers without an entry fall back to the flat
fields. Same applies for `string`/`choice` and `decimal` types.

### Render flow

1. `mathbot generate -c <N>` (or `mathbot batch -c <N>`) maps
   complexity 1/2/3 → easy/medium/hard. If the template lists that
   tier in `difficulty_tiers`, it renders at that tier; otherwise it
   falls back to `metadata.difficulty`.
2. With no `--complexity`, multi-tier templates sample a tier
   uniformly from `difficulty_tiers`.
3. **`test_id` carries `__<tier>` suffix** (`math_<id>__easy` /
   `__medium` / `__hard`). Single-tier templates keep historical
   `math_<id>` (no suffix).

### Multi-tier fixtures

Each fixture row may declare its tier:

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
`metadata.difficulty`. `mathbot lint` flags `fixture_missing` if a
multi-tier template lacks a fixture for any declared tier.

### When to use multi-tier vs separate templates

- **Multi-tier**: same operation, prompt shape, and solution code;
  tiers differ only in number ranges or choice lists.
- **Separate templates**: tiers probe different sub-skills (e.g.
  k6.algebra.factoring: easy = scalar GCF, medium = variable factor,
  hard = quadratic) or use structurally different prompt text.

Filenames for multi-tier templates drop the difficulty token:
`k2_subtraction_01_anchor.yaml`, not
`k2_easy_subtraction_01_anchor.yaml`.

---

## 8. Unit systems

`metadata.unit_system` (default `mixed_us`) drives display-time unit
and currency choices. Three valid values:

| System     | Money | Length | Weight | Temperature | Speed | Area  | Volume |
| ---------- | ----- | ------ | ------ | ----------- | ----- | ----- | ------ |
| `mixed_us` | `$`   | m      | kg     | °F          | mph   | m²    | m³     |
| `metric`   | `€`   | m      | kg     | °C          | km/h  | m²    | L      |
| `imperial` | `$`   | ft     | lb     | °F          | mph   | ft²   | gal    |

### 8.1 Compound physics types

`mixed_us` and `metric` use SI for compound types; only `imperial`
swaps in physics-imperial units:

| System     | Density | Energy | Power | Pressure | Force | Acceleration |
| ---------- | ------- | ------ | ----- | -------- | ----- | ------------ |
| `mixed_us` | kg/m³   | J      | W     | Pa       | N     | m/s²         |
| `metric`   | kg/m³   | J      | W     | Pa       | N     | m/s²         |
| `imperial` | lb/ft³  | ft·lbf | hp    | psi      | lbf   | ft/s²        |

### 8.2 Per-variable override

A variable can override the template default:

```yaml
metadata:
  unit_system: metric
variables:
  cost_us:  { type: money, unit_system: imperial }   # → "$" for this var
  cost_eu:  { type: money }                          # → "€" (template default)
```

### 8.3 Free-form `unit:` (Stage 3)

For one-off compound units that don't deserve a dedicated type, set
an explicit pint unit string. Validated at load time via
`ureg.parse_units()`; rendered with pint's compact pretty form
(`~P` → `m/s²`, `kg/m³`, `mi/gal`):

```yaml
variables:
  acceleration: { type: decimal, unit: 'meter / second ** 2', min: 0.5, max: 9.81 }
  flow_rate:    { type: decimal, unit: 'liter / minute',      min: 1,   max: 20 }
  consumption:  { type: decimal, unit: 'mile / gallon',       choices: [22, 28, 35] }
  Answer:       { type: decimal, unit: 'kilometer / hour' }
```

`unit:` always wins over the `(type, system)`-table lookup. The
companion `<name>_unit` is auto-injected for both Jinja and the
solution sandbox.

### 8.4 Pint conventions to know

- `liter` and `'L'` both render as lowercase `'l'` — pint's convention.
- Alphabetical ordering applies to compound units (`'newton * meter'`
  → `'m·N'`).
- Pint disallows scaling factors in unit strings, so fuel-economy
  units like `'L/100km'` won't parse — author the math directly in
  the solution for those edge cases.

---

## 9. `solution` (Python sandbox)

The solution executes via `exec()` against a restricted
[`safe_globals`](../solution_evaluator.py) dict. Must assign `Answer`
(single-answer) or `Answer1`/`Answer2`/… (multi-answer).

### 9.1 Available without import

```text
# builtins
abs round str int float min max sum pow len list range
sorted enumerate zip map filter any all

# math primitives (surfaced from stdlib `math`)
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

# pint backbone
ureg Q_ get_pint_unit
```

Math primitives are surfaced top-level so templates write
`sin(radians(30))` rather than `math.sin(math.radians(30))`. `sympy`
and `stats` (= `scipy.stats`) are namespaces — call as
`sympy.solve(...)`, `stats.norm.ppf(0.975)`, `stats.binom.pmf(k, n, p)`.

### 9.2 Pint usage

```python
solution: |
  density_q = Q_(density, get_pint_unit('density', 'metric'))   # kg/m³
  volume_q  = Q_(volume,  get_pint_unit('volume',  'metric'))   # liter
  Answer = density_q * volume_q   # carries kg·L/m³ ≡ kg; formatter prints "2.00 kg"
```

A `Quantity` returned as `Answer` is unwrapped automatically: the
formatter calls `.to(<canonical unit for type+system>)` and prints
the magnitude. When the answer spec carries `unit:`, the Quantity is
converted to that unit instead.

### 9.3 sympy / scipy.stats footguns

- `sympy.simplify()` blows up on large expressions — call sparingly,
  ideally once at the end.
- `sympy.Symbol` objects propagate through normal Python operators,
  so accidental symbolic/numeric mixing balloons expression trees.
- `scipy.stats` distributions are pure-Python wrappers; safe to use.

### 9.4 What's NOT available

`from X import Y` works at runtime but **prefer the existing globals**.
Filesystem, network, subprocess, and most stdlib modules outside
`math` / `Decimal` are not exposed. If you need something new, add
it to `safe_globals` in [src/solution_evaluator.py](../solution_evaluator.py)
rather than importing per-template.

### 9.5 Multi-answer

```python
solution: |
  total = subtotal + tax
  refund = total - paid
  Answer1 = total
  Answer2 = refund
```

The CLI joins formatted answers with `" | "` for the `expected_answer`
field.

---

## 10. Locale and i18n

`metadata.language` (default `en`) drives **language behaviour**:

- Locale-aware Jinja filters (`plural`, `ordinal`, `number_to_words`).
- Sandbox `number_to_words(n)`.

`metadata.culture` (default `en-US`) drives **regional behaviour**:

- Faker locale (cities, companies, store names).

The two are independent — `language: en` + `culture: en-GB` produces
English problems with British city names. Currency and unit-system
defaults are NOT tied to locale; set `unit_system` explicitly.

The `names` library (used for `person`/`name` variables) is en-only
and ignores `culture`. Documented in [TECHDEBT.md](../../TECHDEBT.md)
TD-1.2 — when the first non-`en` template lands, replace with
per-locale name pools in `pools.<lang>.yaml`.

---

## 11. `tests` (fixtures)

Each fixture is a `(seed, expected.answer)` pair (plus optional
`difficulty` for multi-tier, `notes`, and the comparison overrides
below). The runner reads `expected.answer` only — legacy `answerN:`
keys are ignored.

```yaml
tests:
  - seed: 12345
    expected:
      answer: "73 | 3 | 24 | 1"     # multi-answer pipe-joined
  - seed: 67890
    expected:
      answer: "$35.75"
    notes: "edge case: max values"
  - seed: 11111
    difficulty: hard                 # multi-tier template
    expected:
      answer: "279"
  - seed: 22222
    expected:
      answer: "10820"
    compare: numeric                 # B4: tolerance-based numeric match
    tolerance: 1.0
  - seed: 33333
    expected:
      answer: "sin(2*x)"
    compare: symbolic                # B3: sympy equivalence (sin(2*x) ~= 2*sin(x)*cos(x))
```

**Recommended**: ≥3 fixtures per template / per tier.

### Comparison modes (B3/B4)

The runner defaults to exact-string equality, which preserves the
byte-for-byte stability of the existing fixture corpus. K9+ templates
that produce decimals or symbolic answers can opt into the alternative
modes below.

| Field           | Type    | Default  | Notes |
| --------------- | ------- | -------- | ----- |
| `compare`       | string  | `string` | `string` (exact) \| `numeric` (parses both as float) \| `symbolic` (parses both via `sympy.sympify` and checks `simplify(a-b)==0` or `equals()`). |
| `tolerance`     | number  | none     | Absolute tolerance for `compare: numeric`. |
| `tolerance_rel` | number  | none     | Relative tolerance for `compare: numeric` — `abs(a-b) / max(abs(a), abs(b))`. Combined with `tolerance` via OR. |

When `compare` is `numeric` or `symbolic` and parsing fails on either
side, the runner falls back to string-equality so that a malformed
fixture surfaces as `fixture_drifted`, not `fixture_crashed`.

### Auto-population

Use `<auto>` in `expected.answer` while drafting:

```yaml
tests:
  - seed: 12345
    expected:
      answer: "<auto>"
```

Then run `uv run python scripts/refresh_test_answers.py --apply
--filter '*/<file>.yaml'` to populate. The script is surgical
(ruamel.yaml round-trip) — preserves comments, key order, quoting.

Run again whenever you change the solution code or any RNG-affecting
generator code.

---

## 12. `visual` (optional)

Templates may include a canonical visual source. The dataset stores
the **source** (an SVG string); a separate `mathbot rasterize` step
produces PNGs at any DPI. **Never write PNG-generation code in
templates** — losing the source means losing the ability to re-render
at a different resolution.

Two formats are supported. The output dataset row always carries
`visual.format = "svg"` regardless of which authoring path produced
it, so downstream consumers (rasterizer, dataset readers,
multi-modal evals) stay format-agnostic.

### 12.1 `format: svg` (Approach A — Jinja-rendered SVG)

`source` is a Jinja2 template that shares the variable context with
the problem body. Use this when geometry is static and coordinates
are known up front.

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

### 12.2 `format: python` (Approach B — builder-class sandbox)

`source` is Python code executed against the solution sandbox plus
the visual builders (`PlotSVG`, `TreeSVG`, `MarkovSVG` —
[src/visuals/](../visuals/)). The source must bind `Visual` to an SVG
string. Use this for derived-coordinate visuals: function plots
where coordinates come from sampling, probability trees with
generation-time-chosen branch counts, Markov diagrams with
parametric transition probabilities.

```yaml
visual:
  format: python
  alt_text: "Parabola y = x² - 2x - 3 crossing the x-axis at -1 and 3."
  source: |
    plot = PlotSVG(x_range=(-2, 4), title="y = x² - 2x - 3")
    plot.plot(lambda x: a*x*x + b*x + c, label="f(x)")
    plot.point(-1, 0, label="root")
    plot.point( 3, 0, label="root")
    Visual = plot.render()
```

The builder library is intentionally small — Approach B targets the
P0 P-N1 / N9 / N12–N14 cells. New shape families (force diagrams,
conic plots, vector arrows) are added in
[src/visuals/](../visuals/) as the first template that needs them
lands.

### 12.3 Output-row contract

The renderer adds `output["visual"] = {format: "svg", source,
alt_text?}` to the dataset row regardless of authoring format.
`mathbot rasterize <dataset>` augments rows with `visual.png_path`.
`mathbot lint` smoke-renders every visual at lint time and fails on
broken Jinja, builder errors, or malformed XML.
(`visual_render_crash`).

### Author guidance

- Keep the SVG **schematic, not to scale** — show shape, label conveys
  value (always render a 120-pixel square regardless of `{{side}}`,
  with `{{side}}` in the labels).
- Use `viewBox` (not absolute `width`/`height`) so the rasterizer can
  pick any output size.
- Reference variables with the same `{{var}}` syntax as the problem
  template — same Jinja context.

System dep for rasterization: `libcairo` (macOS:
`brew install cairo`; Debian/Ubuntu: `apt install libcairo2`).
The Python wheel ships under `uv sync --extra png`.

---

## 13. Output format

A rendered problem JSON:

```json
{
  "test_id": "math_<id>",
  "task_type": "multi_step_math",
  "config_name": "<grade>_<difficulty>_<family>",
  "problem": "Sarah goes shopping…",
  "task_params": {
    "complexity": 1,
    "grade": "k4",
    "math_topic": ["arithmetic"],
    "problem_family": "sequential_purchase",
    "num_steps": 5,
    "expected_answer": "$6.94",
    "operations": ["multiply", "add"]
  },
  "template_path": "src/templates/arithmetic/k4_easy_shopping_01_anchor.yaml",
  "visual": {
    "format": "svg",
    "source": "<svg…",
    "alt_text": "…",
    "png_path": "<dataset>.pngs/math_k4_easy_shopping_01.png"
  }
}
```

`expected_answer` is always a string with units / formatting baked in.
Multi-answer is `"X | Y | Z"` pipe-joined. Multi-tier templates carry
`__<tier>` on `test_id`.

---

## 14. CLI commands

| Command                                | Purpose                                              |
| -------------------------------------- | ---------------------------------------------------- |
| `mathbot generate [opts]`              | Generate a single problem                            |
| `mathbot batch <count> [opts]`         | Batch-generate problems                              |
| `mathbot verify <path>`                | Schema validation only                               |
| `mathbot test <path> [-v]`             | Run the template's embedded `tests:` block          |
| `mathbot lint [path] [--json] [--strict] [-k 4]` | Per-template audit (schema, render-smoke, fixture drift, anchor convention, off-anchor divergence, etc.) |
| `mathbot health [--json] [-k 4]`       | Corpus-level: coverage matrix, density, dupes, contamination |
| `mathbot rasterize <dataset> [--dpi 150]` | SVG → PNG sidecar generation                      |
| `mathbot list [topics\|families\|grades]` | List filter options                              |
| `mathbot info <name>`                  | Show details about a topic or family                 |

Examples:

```bash
mathbot lint                                                # whole corpus
mathbot lint src/templates/algebra --strict                 # subdir, fail on warnings
mathbot lint <path> --rules render_crash,empty_answer       # subset of rules
mathbot health > /tmp/health.json
mathbot rasterize dataset.json --dpi 300 --output-dir pngs/
```

---

## 15. Anchor convention

Filename suffix `_anchor.yaml` marks the **canonical template** for a
`(grade, topic, family, difficulty)` quadruplet. Each cell allows
exactly one anchor. When adding a new template to an existing
quadruplet:

- if the math operation / step-count / variable-shape differs
  meaningfully from the anchor, this is a **non-anchor variant** —
  name it without the suffix
- if it's the same shape just with different surface (item type,
  person name, number ranges), don't add it — that's the duplication
  pattern Phase 4 cleared out
- if it probes a structurally-different sub-skill, consider whether
  it deserves its own family / its own anchor

`mathbot lint` flags drift via `off_anchor_divergence` (variable set
or step-count differs from the cell's anchor) and `anchor_filename_mismatch`
(two `_anchor.yaml` files in one cell).

---

## 16. Authoring workflow

1. **Pick the cell**. `(grade, topic, family, difficulty)`. If an
   anchor exists at `src/templates/<topic>/k<grade>_<difficulty>_*_anchor.yaml`,
   read it as your reference. Otherwise this template will *be* the
   anchor — name it `_anchor.yaml`.

2. **Write the YAML** with `<auto>` placeholders for `tests[].expected.answer`.

3. **Verify and smoke-test**:

   ```bash
   uv run mathbot verify <path>                            # schema
   for s in 12345 42 99 7; do
     uv run mathbot generate --input <path> -s $s -o text | tail -8
   done
   uv run mathbot lint <path>                              # render + drift
   ```

   Manually check the math on each output — generator-correct values
   aren't the same as semantically-correct problems.

4. **Populate test answers**:
   `uv run python scripts/refresh_test_answers.py --apply --filter '*/<file>.yaml'`

5. **Run the full test suite**:
   ```bash
   uv run pytest
   uv run mathbot test <path>
   ```

6. **Confirm corpus health hasn't regressed**:
   ```bash
   uv run mathbot lint --strict
   ```

---

## 17. Validation reference

### Load-time errors (template fails to load)

- Missing required `metadata` field.
- Invalid `difficulty` (not in `{easy, medium, hard}`).
- Invalid `unit_system` (not in `{mixed_us, metric, imperial}`).
- Invalid `unit:` (pint can't parse).
- Invalid `language` filter dispatch (template still loads; filter falls back to `en`).
- `topic` parent doesn't match the file's parent directory.
- Variable type not in `VALID_TYPES`.
- `item` category not in `VALID_ITEM_CATEGORIES`.
- `min > max`.
- No `Answer` / `Answer1` / `Answer2` … variable defined.
- Solution has Python syntax error.
- Solution doesn't reference `Answer`.
- `difficulty_tiers` doesn't include `difficulty`.

### Lint-time findings (template loads, `mathbot lint` flags it)

#### Errors

- `render_crash` — all K render attempts threw.
- `unrendered_jinja` — literal `{{...}}` in rendered output.
- `empty_answer` — rendered answer is empty.
- `visual_render_crash` — visual.source Jinja or XML failed.
- `fixture_drifted` / `fixture_crashed` — embedded `tests:` doesn't match generator output.
- `schema_invalid` — load-time error surfaced as a finding.

#### Warnings

- `off_anchor_divergence` — variant's variable set / step count diverges from anchor.
- `anchor_filename_mismatch` — two `_anchor.yaml` files in one cell.
- `body_too_long` — rendered body > 800 chars.
- `fixture_missing` — no fixtures, or multi-tier missing a tier.
- `slug_noncanonical` — `family` slug needs renaming.
- `unit_spelled_squared` / `unit_spelled_cubic` — drift on `m²` / `m³` etc.
- `zero_steps_with_ops` / `very_high_step_count` — sanity bounds on `metadata.steps`.

#### Info

- `gsm8k_money_change`, `gsm8k_with_tax`, `gsm8k_items_at_price_each` —
  GSM8K-saturation patterns. Not bad in isolation; concentration
  within a cell is a smell.
- `area_no_squared_unit` / `volume_no_cubed_unit` — heuristic
  answer-units-match-topic flags. Often false-positives for
  perimeter / linear-derived answers in geometry templates.

---

## Appendix: spec-mandated families

Every problem ultimately maps to one of these (or a hybrid). Listed
in [src/constants.py](../constants.py) as `PROBLEM_FAMILIES`.

| Family                  | Pattern                                              |
| ----------------------- | ---------------------------------------------------- |
| `sequential_purchase`   | Multi-step shopping with discounts / budget          |
| `rate_time`             | Distance ↔ speed ↔ time, multi-segment               |
| `compound_growth`       | Interest / percent change chain over N periods       |
| `multi_person_sharing`  | Splitting amounts by ratio, transfer, or constraint  |
| `area_perimeter_chain`  | Geometry with area → side → perimeter or similar     |

Plus topic-specific families (`addition`, `factoring`, `quadratic`,
`shapes_2d`, `shapes_3d`, etc.) — see `PROBLEM_FAMILIES` for the full
list. K7-K12 expansion is guided by
[MATHBOT_PROBLEMS_PROPOSAL.md](../../MATHBOT_PROBLEMS_PROPOSAL.md):
22 proposed families synthesized from K-12 curricula across eight
education systems.

---
