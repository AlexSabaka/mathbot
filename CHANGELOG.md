# Changelog

All notable changes to the Mathbot project are documented in this file.

---

## [0.2.4] - 2026-04-26 - Phase 5.3R: pint backbone for unit conversions

External research-agent feedback called out the v0.2.2 custom `UNIT_TABLE`
as the wrong abstraction for physics families:

> Adopt **pint** for the Quantity class with prefixes, compound units, and
> dimensional analysis. The math module can use a thin pint wrapper that's
> effectively no-op for unitless quantities. Don't build two parallel unit
> systems for math vs physics; build one with pint and have math mostly
> ignore it.

Three of the proposal families ([MATHBOT_PROBLEMS_PROPOSAL.md](MATHBOT_PROBLEMS_PROPOSAL.md))
need quantities the v0.2.2 table cannot represent:

- **P-G3 composite solids**: "grain density 750 kg/m³", "cm³ → litres → kg via density"
- **P-M1 dimensional analysis** (entire family): "kg/L → g/mL → oz/fl-oz; km/h → m/s → ft/s; W·h/day → kW·h/year"
- **P-A2 formula manipulation**: kinetic energy E = ½mv² (J = kg⋅m²/s²), lens equation 1/f = 1/u + 1/v, ideal gas

This release wires up the pint registry as the foundation. **Stage 1 (this
release) is API-compatible and behavior-preserving**: pint validates unit
names at module load, but display still uses the same f-string formatters,
so all 1307 fixtures stay byte-identical. Stage 2 (forthcoming) will add
compound-unit variable types (`density`, `energy`, `power`, `pressure`,
`force`) and expose `Q_` / `ureg` in the solution sandbox.

### What landed

- **`pint>=0.25` runtime dep**.
- **[src/units.py](src/units.py)** rewrite: `ureg = pint.UnitRegistry()`
  and `Q_ = ureg.Quantity` module-level singletons. The legacy
  `UNIT_TABLE` (4-level dict) is replaced by `DISPLAY_UNITS` (3-level
  dict) where each entry is `(pint_unit_string, short_suffix_or_None,
  long_suffix)`. The pint unit string is **validated at module load**
  via `_validate_display_units()` — typos like `"meeter"` raise
  `ValueError` with the offending `(system, type)` cell named, instead
  of silently rendering an empty suffix later.
- **Helper signatures unchanged**: `get_short_suffix`, `get_long_suffix`,
  `is_compact`, `get_currency_symbol`, `resolve_system`. This means
  zero changes to `format_value` ([src/variable_generator.py](src/variable_generator.py))
  and `format_answer` ([src/solution_evaluator.py](src/solution_evaluator.py)) —
  the refactor is purely internal to `src/units.py`.
- **New helper** `get_pint_unit(type, system)` returns the pint unit
  string for callers (Stage 2 sandbox wiring will use it as a
  source-of-truth for wrapping magnitudes in Quantity objects).
- **`CURRENCY_SYMBOL`** kept as its own dict; currency is deliberately
  outside pint (see "Decisions locked" in the plan).
- **Tests** ([tests/test_units.py](tests/test_units.py)) — 3 new cases
  in a new `TestPintBackbone` class:
  - `ureg` is a real `pint.UnitRegistry`; `Q_` is `ureg.Quantity` (same
    identity, not a fresh instance — important for Stage 2 cross-call
    Quantity comparisons)
  - `ureg.parse_units("meter ** 2")` and `kilogram / meter ** 3` (a
    Stage 2 density preview) parse cleanly; `"meeter"` and `"blarghs"`
    raise
  - `_validate_display_units({...with typo...})` raises a `ValueError`
    that names the offending cell

  All 25 existing unit tests still pass byte-identical. Total pytest:
  93/93.

### Backward compatibility

- `pytest`: 93/93 (90 before + 3 new pint-presence tests).
- `scripts/refresh_test_answers.py --dry-run`: **0 of 1307** template
  fixtures changed.
- The byte-identical `mixed_us` invariant from Phase 5.3 is preserved —
  `metric` and `imperial` templates continue to render exactly as they
  did under the v0.2.2 hand-rolled table.

### Decisions locked (per planning Q&A)

- **Value semantics**: `system-native-internal`. A `metric` template's
  `temperature: 100` stays "100 °C" through and through; pint does **not**
  auto-convert at display time. Conversion arithmetic is only invoked
  when a template explicitly calls `Q_(...).to(...)` (Stage 2).
- **Scope**: backbone only. No new variable types, no sandbox exposure
  in this release.
- **Currency**: kept outside pint. Currencies aren't dimensional
  quantities; FX conversion needs out-of-process rates.

### Known follow-ups (TECHDEBT)

- **TD-3.5 (Stage 2)**: Compound-unit variable types + sandbox `Q_` /
  `ureg` exposure. Pairs the registry wired up here with new types
  (`density`, `energy`, `power`, `pressure`, `force`) so P-G3 / P-A2 /
  P-M1 templates can express their physics quantities.
- **TD-3.6 (Stage 3)**: Free-form `unit:` field on `VariableSpec` —
  `{type: decimal, unit: 'meter / second**2'}`. Lets authors declare
  any pint-parseable unit without adding a new variable type.

---

## [0.2.3] - 2026-04-26 - Phase 5.5: visual layer (SVG-source-then-rasterize)

Templates can now ship a canonical visual alongside the problem text. The
YAML stores the SVG source; a separate `mathbot rasterize` step produces
PNGs at any DPI. Both ship in the dataset. The constraint **templates
never write PNG-generation code** is enforced by design: the schema only
accepts source formats (`svg` today, `python` builder roadmap), and the
rasterizer is a one-way SVG→PNG step, never the reverse.

### What landed

- **Schema** ([src/yaml_loader.py](src/yaml_loader.py)) — new optional
  `visual:` block on `TemplateDefinition`. New `VisualSpec` dataclass
  with `format` (validated against `VALID_VISUAL_FORMATS = {"svg"}`),
  `source` (Jinja2 template, must be non-empty string), and optional
  `alt_text` (Jinja2 template, must be string when present). Invalid
  formats and missing/empty sources fail loading with a clear error.
- **Rendering** ([src/template_generator.py](src/template_generator.py))
  — `_generate_from_template` renders both `visual.source` and
  `visual.alt_text` through the same `combined_context` used for
  `template:`, so `{{side}}` in the SVG resolves to the same value as
  `{{side}}` in the problem text. Output JSON gains an optional
  `visual: {format, source, alt_text}` field; templates without a
  `visual:` block emit no field.
- **Rasterizer** ([src/cli.py](src/cli.py) — new `mathbot rasterize`
  subcommand) — reads a JSON or JSONL dataset, finds rows with a
  `visual.source` SVG, writes one PNG per row to a sidecar directory
  (default `<dataset>.pngs/`), and augments each row's `visual` block
  with a `png_path`. Flags: `--dpi N` (default 150), `--width PX`
  (overrides DPI), `--in-place / --write-out` (default in-place). Lazy
  imports `cairosvg` so only PNG-producing workflows incur the
  dependency. Errors clearly when `cairosvg` is missing OR when the
  system `libcairo` library isn't found, with the right install command
  per OS. Preserves dataset shape (single dict in → single dict out).
- **Optional dep** ([pyproject.toml](pyproject.toml)) — `cairosvg>=2.8`
  added under the `png` extra. `uv sync --extra png` installs the wheel;
  system `libcairo` is the user's responsibility (`brew install cairo`
  / `apt install libcairo2`).
- **Example anchor** ([src/templates/geometry/k5_easy_square_area_01_anchor.yaml](src/templates/geometry/k5_easy_square_area_01_anchor.yaml))
  — first template with a `visual:` block: a 200×200 schematic SVG of a
  labeled square, all four sides labeled with `{{side}}` (rendered).
  Schematic-not-to-scale convention: square is fixed size, labels
  convey the value.
- **Tests** ([tests/test_visual.py](tests/test_visual.py), 10 cases) —
  schema validation (4 cases: optional, valid SVG, invalid format,
  missing source, alt_text type), rendering (4 cases: variable
  substitution, alt_text substitution, absent visual, render-failure
  error chain), live anchor (1 case: the seeded square_area template
  emits a clean visual). Pytest total: 70/70.

### Pipeline

```bash
$ mathbot generate --input geometry/k5_easy_square_area_01_anchor.yaml -s 12345 -o json --file out.json
$ mathbot rasterize out.json
Rasterized 1, skipped 0 (no visual), errored 0. PNGs in out.json.pngs/, dataset → out.json.

$ jq '.visual' out.json
{
  "format": "svg",
  "source": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 200 200\">\n  <rect ...>...</svg>",
  "alt_text": "A square with each of its four sides labeled 12 inches.",
  "png_path": "out.json.pngs/math_k5_easy_square_area_01.png"
}
```

Re-running `mathbot rasterize out.json --dpi 300` regenerates the PNG
at higher resolution from the same SVG source.

### Out of scope (roadmap)

- **Approach B**: Python `SVG`/`TreeSVG`/`BarChartSVG` builder classes
  in the solution sandbox for derived-coordinate visuals (probability
  trees, bar charts, scatter plots). The schema slot for `format: python`
  is reserved but not yet implemented. Tracked as TECHDEBT TD-3.1b.
- **Matplotlib path**: another candidate `format` for plotting
  workflows. Heaviest dep, not in Phase 5.5; revisit if grouped-stats
  templates need histograms.
- **Visual lint**: schema validation only checks that source is a
  non-empty string; it does not parse the SVG or run the Jinja
  template ahead of generation. A `mathbot lint` pass that smoke-renders
  visuals at template-load time would catch broken `<svg>` syntax
  earlier.
- **Visual-aware unit tests**: `tests/test_visual.py` doesn't exercise
  the rasterizer (which would require `libcairo` on the test runner).
  End-to-end PNG production was verified manually.

---

## [0.2.2] - 2026-04-26 - Phase 5.3: unit_system (metric / imperial / mixed_us)

Display-time unit and currency choices are now coherent. Templates declare
`metadata.unit_system` (default `mixed_us`); a variable can override the
template default per-spec for unit-conversion problems that mix systems
intentionally. New tech-debt log [TECHDEBT.md](TECHDEBT.md) closes TD-1.1
(mixed-system formatter) with this release.

Solutions still compute in **system-native units** — the table only handles
display. Templates that need explicit unit conversion (e.g. the
dimensional-analysis P-M1 family from
[MATHBOT_PROBLEMS_PROPOSAL.md](MATHBOT_PROBLEMS_PROPOSAL.md)) do the math
themselves with hard-coded factors, then format the result.

### What landed

- **[src/units.py](src/units.py)** (new) — `UNIT_TABLE` keyed by
  `(type, system)` with `value_short` / `value_long` / `value_compact` /
  `symbol` fields. Helpers: `resolve_system`, `get_short_suffix`,
  `get_long_suffix`, `is_compact`, `get_currency_symbol`.
  `VALID_UNIT_SYSTEMS = {metric, imperial, mixed_us}`,
  `DEFAULT_UNIT_SYSTEM = "mixed_us"`.
- **Schema** ([src/yaml_loader.py](src/yaml_loader.py)) — added
  `metadata.unit_system` (default `mixed_us`) and per-`VariableSpec.unit_system`
  override (None → inherit). Both validated against the allow-list at
  load time; invalid values rejected with a clear error.
- **Formatters refactored** — [src/variable_generator.py](src/variable_generator.py)
  `format_value` and [src/solution_evaluator.py](src/solution_evaluator.py)
  `format_answer` both take `template_unit_system` and resolve via
  `(spec.unit_system or template_unit_system)`. Currency, length, weight,
  temperature, area, volume, speed all consume the table.
- **Plumbed** ([src/template_generator.py](src/template_generator.py)) —
  `template.unit_system` flows into both formatters.
- **Tests** ([tests/test_units.py](tests/test_units.py), 25 cases) lock
  mixed_us byte-compat, metric/imperial divergence, per-variable override,
  and schema validation.

### Display divergence

| Type | mixed_us | metric | imperial |
|---|---|---|---|
| length | `m` / `meters` | `m` / `meters` | `ft` / `feet` |
| weight | `kg` / `kg` | `kg` / `kg` | `lb` / `pounds` |
| temperature | `°F` | `°C` | `°F` |
| speed | `mph` | `km/h` | `mph` |
| area | `m²` / `square meters` | `m²` / `square meters` | `ft²` / `square feet` |
| volume | `m³` / `cubic meters` | `L` / `liters` | `gal` / `gallons` |
| money | `$` | `€` | `$` |

### Backward compatibility

- `pytest` — 35 original tests still pass byte-identical (60 total now,
  +25 new in `test_units.py`).
- `scripts/refresh_test_answers.py --dry-run` — **0 of 1307** template
  fixtures changed under default `mixed_us`. Existing corpus continues
  to render exactly as before; opting into `metric` / `imperial` is a
  per-template, per-variable choice.

### Known follow-ups

- Currency is currency-vs-system-coupled today (one currency per system).
  If a template wants £ on metric or ¥ on its own system, currency will
  need to split out as a separate metadata field. Not pressing.
- `mixed_us` `weight` answer always renders 2-decimal (`5.50 kg`, never
  `5 kg`) — preserves a pre-5.3 inconsistency that other types check int
  vs float for.
- Time formatting (`hours / minutes`) is locale-agnostic and not in the
  unit table — F3 Stage 2 will revisit.

---

## [0.2.1] - 2026-04-26 - Eval surface: gol_eval plugin + corpus self-similarity tooling

Two work threads landed this release:

1. **Mathbot is now a first-class gol_eval plugin** via a symlinked
   directory `mathbot/gol_plugin/`. The bespoke Ollama smoke harness
   (`scripts/test_model.py`, `scripts/_ollama.py`, `scripts/_eval/`,
   `tests/test_eval.py`, ~600 LOC + `httpx` dep) is retired. Mathbot now
   piggybacks on gol_eval's prompt-style matrix, 6-language wrappers,
   run orchestration, model fleet, web-UI config schema, and aggregated
   reporting — no eval infrastructure to maintain locally.
2. **Corpus self-similarity tooling** ([scripts/internal_contamination.py](scripts/internal_contamination.py))
   surfaces near-duplicate templates for pruning, alongside the existing
   gsm8k contamination report ([scripts/gsm8k_contamination.py](scripts/gsm8k_contamination.py))
   and coverage matrix ([scripts/coverage_matrix.py](scripts/coverage_matrix.py)).

### gol_eval plugin (`gol_plugin/`)

Six files, ~520 LOC including README. User wires it in once with
`ln -s /path/to/mathbot/gol_plugin /path/to/gol_eval/src/plugins/mathbot`;
gol_eval's `PluginRegistry._auto_discover()` follows the symlink and
registers `task_type="mathbot"`. No gol_eval-side changes required.

- **`generator.py`** — shells out to `uv run --project <auto-detected
  mathbot root> mathbot batch <count> -s <seed> -o jsonl` and parses
  stdout into `TestCase` objects. Subprocess approach was chosen over
  direct import to dodge the `src.*` namespace collision between
  gol_eval's `src/` package and mathbot's (mathbot's pyproject
  declares `packages = ["src"]`). The auto-detect walks up from
  `Path(__file__).resolve()` looking for `pyproject.toml` with
  `name = "mathbot"`, which works through the symlink because `resolve()`
  follows it.
- **`parser.py`** — 4-strategy end-first parser using
  `parse_utils.re_search_last`: `latex_boxed` (0.95), `markdown_bold`
  (0.90, header bolds ending `:` skipped), `answer_label` (0.85, with
  sentence-end truncation to handle "Final answer: $6.94" without
  losing the decimal), `last_line` (0.50, fallback).
- **`evaluator.py`** — multiplicity-aware number-presence comparator
  with substring fallback for string-only expected answers. Crucially
  does **not** fall back to scanning the full model response when the
  parser returned a non-empty span — this prevents crediting numbers
  that only appeared in chain-of-thought reasoning and fixed a real
  false-positive caught during smoke testing (model boxed `\boxed{6}`
  but its reasoning enumerated `8, 2, 13`, the actual expected
  values). Match types: `numeric_match`, `numeric_missing`,
  `substring_match`, `wrong`, `parse_error`.
  `aggregate_results` reports per-shape and per-grade accuracy on top
  of the overall score.
- **`i18n.yaml`** — body + `linguistic`-style override (the explicit
  `\boxed{}` instruction the parser is tuned for). 6-language coverage
  with EN-fallback. The shared `casual`/`minimal` wrappers from
  gol_eval's `src/plugins/i18n/styles.yaml` provide conversational and
  bare framings without per-plugin duplication.
- **Config schema** — `grade` / `complexity` / `topic` (select),
  `family` (text), `num_steps` (number), `mathbot_root` (text override).
  Select fields use `"any"` as a non-empty sentinel for "no filter"
  per gol_eval convention (cf. `measure_comparison`'s `default='all'`)
  — Radix Select disallows empty-string item values, so the original
  `default=""` triggered an `ErrorBoundary` on the gol_eval frontend.

### Smoke verification

End-to-end through the plugin interface (3 problems, seed=1, default
config): generator → parser → evaluator → aggregator round-trip
succeeds (3/3). An adversarial battery (wrong numeric, partial
multipart box, empty response, CoT-leak attempt, word mismatch,
currency-tolerant match) classifies all 6 cases correctly. Plugin
discovery via `PluginRegistry.reload()` lists `mathbot` in
`list_task_types()` with the README's first paragraph correctly
loaded as `description`.

### Corpus self-similarity tooling

[scripts/internal_contamination.py](scripts/internal_contamination.py)
finds near-duplicate templates by rendering each template `K` times
(default 3), unioning the 5-gram shingles per template, and computing
pairwise Jaccard. Same n-gram machinery as
`gsm8k_contamination.py` but with template-vs-template axis. Output:
JSON with summary stats, histogram, per-template max-neighbor view,
and deduplicated top-pairs list.

First sweep on the 642-template corpus (n=5, K=3) found:

| Stat | Value |
|---|---|
| max similarity | 1.000 |
| pairs ≥0.7 | 1 |
| pairs ≥0.5 | 4 |
| mean max-neighbor | 0.046 |

Two clusters cleaned up: `k6_easy_inequalities_02` (sim 1.000 with
`_01_anchor`) and `k5_medium_powers_of_10_03` (sim 0.556 with
`_01_anchor`) deleted as redundant variants. Anchors preserved; each
cell still has the canonical-plus-variant pattern. Post-deletion: max
similarity 0.533, pairs ≥0.7 = 0, pairs ≥0.5 = 2.

### Smoke-harness retirement

| File | Disposition |
|---|---|
| `scripts/test_model.py` | deleted |
| `scripts/_ollama.py` | deleted |
| `scripts/_eval/{__init__,extract,shapes,compare}.py` | deleted |
| `tests/test_eval.py` (44 tests) | deleted |
| `httpx>=0.27.0` dep in `pyproject.toml` | removed |

The custom parser/comparator logic itself was preserved — ported to
`gol_plugin/parser.py` + `gol_plugin/evaluator.py` against gol_eval's
interfaces. The string-only substring fallback also carries over.

### Result

| Metric | After 0.2.1 |
|---|---|
| Templates | 640 (was 642; 2 near-duplicates removed) |
| pytest | 35/35 (was 79/79; the 44 eval tests moved out, no replacement needed because gol_eval has its own plugin test scaffolding) |
| Plugin task_type | `mathbot` registered in gol_eval |
| Eval infrastructure maintained locally | none (was `scripts/_eval/` + `_ollama.py`) |
| New corpus tools | `internal_contamination.py` (was previously absent) |

### Out of scope

- A real model run via gol_eval's pipeline — the plugin delivers the
  integration; running a campaign is the user's call.
- Multilingual problem text — mathbot's templates render English only;
  the plugin's i18n.yaml ships the same EN body for all 6 languages
  with the `linguistic` override translated. Real multilingual support
  follows Phase 5.6 Stage 2 work.
- Multi-grade or multi-topic test sets in one run — the mathbot CLI
  takes a single `-g`/`-t`/`-f` value per invocation, so the plugin's
  generator forwards a single value. Multi-grade campaigns require
  multiple test-set generations.

---

## [0.2.0] - 2026-04-26 - Phase 5.1+5.6: sandbox toolkit & i18n foundation

Strategic roadmap drafted (see `mathbot-phase5-roadmap` plan in claude-plans;
also re-summarised in [`MATHBOT_PROBLEMS_PROPOSAL.md`](MATHBOT_PROBLEMS_PROPOSAL.md)
for the K7-K12 expansion). Two of the seven sub-phases land here: **5.1**
(sandbox + invariants) and **5.6** (i18n foundation). The other sub-phases
(format healing, visual layer, authoring sprints, doc/lint pass) remain on
the roadmap. New running tech-debt log at [`TECHDEBT.md`](TECHDEBT.md).

### Phase 5.1 — sandbox primitives & invariants

The proposal's 22 new families need stdlib math, symbolic algebra, and
statistical inference primitives in the solution sandbox. Added all three
without forcing per-template imports.

- **Solution sandbox** ([src/solution_evaluator.py](src/solution_evaluator.py)) — surfaced top-level: `pi e sqrt exp sin cos tan asin acos atan atan2 log log2 log10 floor ceil factorial comb perm radians degrees`. Added namespaces: `sympy` (full symbolic algebra) and `stats` (= `scipy.stats`; `norm`, `t`, `binom`, `chi2`, `poisson` distributions usable as `stats.norm.ppf(0.975)`).
- **Sandbox bug fix** — the solution-execute `except Exception as e` shadowed the imported `math.e` constant via Python local-binding rules, breaking access to Euler's number anywhere in solution code. Renamed to `as exc`.
- **Topic↔directory invariant enforced** ([src/yaml_loader.py](src/yaml_loader.py)) — `_validate_template` now asserts that a template's parent directory matches its `metadata.topic.split('.')[0]`. Documented in CLAUDE.md as an invariant since v0.1.3 but not previously enforced; current corpus has zero violations.
- **`migrate_templates.py` deleted** — the broken `--update-tests` script flagged for removal in v0.1.3 is now gone. Use `scripts/refresh_test_answers.py`.
- **RNG double-seed clarified** ([src/template_generator.py](src/template_generator.py)) — both `TemplateGenerator.generate()` and `VariableGenerator.__init__()` call `random.seed()` and `Faker.seed()` with the same seed. This is intentional (variable values must depend only on the seed, not on which template was selected) but easily mistaken for a bug; added a comment explaining the contract. Single-RNG-instance refactor deferred (would change every fixture; see `TECHDEBT.md`).

New runtime deps: `scipy>=1.17` and `sympy>=1.14` (added via `uv add`).

### Phase 5.6 — i18n foundation

Wired up the previously-dormant `culture` field, added a sibling `language`
field, and refactored the renderer + provider stack so that adding a new
language is one YAML file plus one `register_language(...)` call. No
behavioural change for the existing en corpus.

- **VALID_TYPES cleanup** ([src/yaml_loader.py:66](src/yaml_loader.py#L66)) — removed 33 declared-but-never-implemented types (`vector_2d/3d`, `point_2d/3d`, `circle`, `ellipse`, all triangle/prism/sphere variants, `data_set`, `distribution`, `equation`, `function`, `polynomial`, `expression`, `matrix`, `vector`, `set`, `sequence`, `series`, `limit`, `derivative`, `integral`). The remaining 25 types each have a `_generate_value` branch and a `format_value` rule. Re-add as proposal families need them, with an implementation alongside.
- **`language` metadata field** ([src/yaml_loader.py:45-50](src/yaml_loader.py#L45)) — new `language: en` (default) sits alongside `culture: en-US`. `language` drives locale-aware Jinja filters and sandbox `number_to_words`; `culture` drives Faker locale (cities/companies). Defaults preserve current behaviour.
- **`LanguageSpec` registry** ([src/i18n/languages.py](src/i18n/languages.py), new) — bundles `plural`, `ordinal`, `number_to_words` callables per language. English spec built from `inflect`. Filters look up the spec at render time via the `language` context variable; unknown codes fall back to en.
- **Locale-aware Jinja filters** ([src/jinja_renderer.py](src/jinja_renderer.py)) — `plural`, `ordinal`, `number_to_words` are now `@pass_context` and dispatch via `LanguageSpec`. The locale-agnostic filters (`choice`, `list_and`, `format_money`, `capitalize`) unchanged.
- **Solution sandbox `number_to_words`** ([src/solution_evaluator.py](src/solution_evaluator.py)) — `execute_solution` now takes a `language` param (default `en`); `number_to_words` in `safe_globals` is the active spec's. `template_generator` plumbs `template.language` through.
- **Entity pools as data** ([src/data/pools.en.yaml](src/data/pools.en.yaml), new; [src/providers.py](src/providers.py) refactored) — all locale-specific pools (8 item categories, weekdays/months/seasons/times-of-day, store/restaurant suffixes, 7 context lists, depreciating-items) extracted to YAML; `MathProblemProvider` is now a thin loader that exposes the data as class attributes for backward compat. Adding `pools.es.yaml` is one file.
- **Configurable Faker locale** ([src/variable_generator.py:16-32](src/variable_generator.py#L16)) — `VariableGenerator.__init__()` accepts a `locale` param (default `en_US`), accepts both BCP-47 `en-US` and Faker `en_US` forms. `template_generator` passes `template.culture` through. Verified: `de-DE` → German cities, `es-ES` → Spanish cities. The `names` library remains en-only and ignores locale (see TECHDEBT.md).

### Ergonomics

- **Schema doc** ([.claude/CLAUDE.md](.claude/CLAUDE.md)) refreshed: stale test-count fixed (35 → 79), sandbox primitives table updated, providers description corrected, new Locale & i18n section, broken `migrate_templates.py` reference removed, repo-layout includes `data/`, `i18n/`, `MATHBOT_PROBLEMS_PROPOSAL.md`, `TECHDEBT.md`.

### Result

| Metric | After 5.1+5.6 |
|---|---|
| Sandbox primitives (top-level) | 27 (was 4) + 2 namespaces |
| Symbolic algebra in sandbox | sympy (1.14) |
| Stat-inference in sandbox | scipy.stats (1.17) |
| Declared variable types | 25 (was 47; 22 of those actively used) |
| Topic↔dir invariant | enforced (was documented-only) |
| Locale dispatch surface | `language` field + `LanguageSpec` registry |
| Faker locale | configurable (was hard-coded en_US) |
| Pool data location | `src/data/pools.<lang>.yaml` (was Python tuples in providers.py) |
| pytest | 79/79 |

### Deferred to later Phase 5 sub-phases

- **5.2 / 5.4** — authoring sprints for the 22 proposal families (~135 templates total). Better as an interactive cycle than autonomous bulk.
- **5.3** — multi-unit `unit_system` schema + formatter refactor (F2). Will break every existing template's expected-answer string and require a `refresh_test_answers.py` regen + manual review pass.
- **5.5** — visual layer (F1): `visual:` block in YAML, Jinja-SVG (Approach A) then `SVG`/`TreeSVG`/`BarChartSVG` builders in sandbox (Approach B).
- **5.7** — `mathbot lint` subcommand and `src/templates/SPEC.md` schema doc refresh.
- **F3 Stage 2/3** — first non-English language POC and multi-cultural pool extensions.

---

## [0.1.3] - 2026-04-22 - Corpus cleanup, anchor convention, K7-K12 seeding

### Phase 1-3 — restore working state after the schema refactor

A previous session migrated variable schema from `{type, format}` to a single
`type` field, but the migration landed incompletely — the CLI was wired to a
nonexistent method, the loader rejected several valid template constructs,
and embedded test cases held stale expected values across ~80% of the corpus.
This release fixes the regressions:

- **CLI generate** — was calling `TemplateGenerator.generate_problem` which
  doesn't exist; now routes through `src/generator.py:generate_problem` for
  the default path and `TemplateGenerator.generate` for `--template-dir`.
- **YAMLLoader** — added `choice` to `VALID_TYPES`; added `school`, `furniture`,
  `other` to `VALID_ITEM_CATEGORIES`; relaxed `min > max` (was `min >= max`)
  to allow fixed-value ranges; routed load-failure messages to stderr.
- **VariableGenerator** — wired `choice` type (alias of `string` with choices);
  honored `choices` list on `integer` type; mapped new item categories to pools.
- **MathProblemProvider** — added `SCHOOL_ITEMS`, `FURNITURE_ITEMS`,
  `OTHER_ITEMS`; extended `WEEKDAYS` to include weekends; added `MONTHS` list.
- **Solution sandbox** — exposed `gcd` and `lcm` directly so 31 fraction and
  divisibility templates execute without per-template imports.
- **Batch CLI** — `--file` is now optional (stdout default); added `-s/--seed`
  for reproducibility; per-item retry on no-template-match instead of fatal.

### Phase 4 — corpus cleanup, anchor convention, K7-K12 expansion

**Stage 1: 278 deletions and topic harmonization.** Six sub-agents reviewed
the 892-template corpus by topic slice. Deleted templates fell into three
buckets: trivial range-variation duplicates (same operation, same step count,
only `min/max` ranges differ), off-grade content (45 K6 statistics templates
that were really K3-K4 arithmetic), and three structurally-unrecoverable
files (mislabeled rectangle area, missing variable, non-existent Jinja
filter). 51 surviving templates had bare or directory-mismatched topic
metadata (e.g. `topic: arithmetic` with no subtopic, or `topic: geometry.measurement`
in `measurement/`); now harmonized to `topic: <dir>.<subtopic>`.

**Stage 2: surgical test-answer regeneration.** Wrote
`scripts/refresh_test_answers.py` using `ruamel.yaml` round-trip mode (preserves
comments, key order, quoting). Replaces the broken
`migrate_templates.py --update-tests` (which gates on a no-longer-firing
format→type migration check and uses lossy `yaml.dump`). Multi-answer
templates were normalized: legacy `answer1/answer2/...` keys removed in favor
of a single pipe-joined `answer:` field (the only field the CLI test runner
actually reads).

**Stage 4.1: anchor convention.** Designated 330 lead variants as anchors via
`*_anchor.yaml` filename suffix — one per (grade, topic, family, difficulty)
quadruplet. Anchors are the canonical pattern for their quadruplet; new
templates added there should follow the anchor's style.

**Stage 4.2: 27 hand-authored seed templates.** Closed the K7-K12 coverage
gap and seeded all five spec-mandated families (`sequential_purchase`,
`rate_time`, `compound_growth`, `multi_person_sharing`, `area_perimeter_chain`).
Each template hand-authored against the patterns in
`mathbot-phase4-problem-proposals.md` (Singapore P5/P6 bar models, RME
contextual chains, CCSS multistep ratio/percent), parameterized so generated
values yield clean integer or 2-decimal answers. New domains seeded:
geometric series, calculus optimization, hypothesis testing, exponential
decay, linear regression, mathematical induction, vector geometry,
probability tree, geometric proof chains.

### Result

| Metric                            | Before | After             |
| --------------------------------- | ------ | ----------------- |
| Templates                         | 892    | 642               |
| Anchor templates                  | 0      | 358               |
| Templates that throw exceptions   | 15     | 0                 |
| Template self-test pass rate      | ~14%   | 100% (1311/1311)  |
| pytest                            | 28/35  | 35/35             |
| K7-K12 templates                  | 14     | 39+               |

### Tooling added

- `scripts/refresh_test_answers.py` — surgical test-answer regenerator
- `ruamel.yaml` added to dev deps for format-preserving YAML rewrites

### Tooling deprecated

- `migrate_templates.py --update-tests` — broken (no-op gate + lossy dump);
  will be removed in a future release. Use `scripts/refresh_test_answers.py`.

### Historical context — pre-alpha spec

The `.claude/CLAUDE.md` shipped with v0.1.0 contained the original
implementation specification: 9 math topics, 5 problem families, package
layout under `families/*.py`, and the "5-10 templates per family" target.
That spec served its purpose during initial implementation and the
subsequent Mustache → YAML+Jinja2 migration. As of v0.1.3 it is replaced
with a development guide describing the actual implementation —
templates live in `src/templates/<topic>/*.yaml` (not `families/*.py`),
the math-topic taxonomy is dotted (e.g. `arithmetic.addition`,
`geometry.area_composite`), and grades use the K1-K12 schema rather than
elementary/middle/high/college. The five spec-mandated families remain
the intent.

---

## [0.1.2] - 2026-01-30 - YAML+Jinja2 Migration Complete

### 🎉 Complete Migration to YAML+Jinja2 Template System

Full architectural migration from Mustache to YAML+Jinja2 with comprehensive template specification.

#### System Overhaul

- **YAML Template Format** - Structured metadata, variables, template, solution, and tests sections
- **Jinja2 Rendering** - Powerful template engine with filters and logic support
- **Multi-Answer Support** - Answer1, Answer2, Answer3 for problems with multiple outputs
- **Template Path Tracking** - All generated problems include source template path
- **Format System** - 9 format types: money, percentage, ordinal, length, weight, temperature, area, volume, speed

#### New Core Infrastructure

| Module | Purpose |
|--------|----------|
| `src/yaml_loader.py` | YAML parsing and validation with TemplateDefinition dataclass |
| `src/jinja_renderer.py` | Jinja2 environment with custom filters (choice, plural, format_money, etc.) |
| `src/variable_generator.py` | Type-aware value generation with format constraints |
| `src/solution_evaluator.py` | Python solution execution with multi-answer support |
| `src/template_generator.py` | Core generator with template discovery and path tracking |

#### Template Structure (v2.0)

```yaml
metadata:
  id: k6_medium_shopping_01
  grade: 6
  topic: arithmetic.shopping
  family: shopping
  difficulty: medium
  steps: 3

variables:
  name:
    type: person
  price:
    type: decimal
    format: money
    min: 5.0
    max: 20.0
  Answer:
    type: decimal
    format: money

template: |
  {{name}} bought items for {{price}}.
  Please solve this problem and provide your final answer.

solution: |
  Answer = price * 2

tests:
  - seed: 12345
    expected:
      answer: "$24.50"
```

#### Key Features

- **Template Specification** - Complete format documentation in `src/templates/SPEC.md` (source of truth)
- **Variable System** - 14 types: integer, decimal, fraction, person, location, store, restaurant, company, weekday, season, time, item, boolean, string
- **Format Constraints** - Automatic unit formatting (e.g., "45m", "$12.50", "15%")
- **Multi-Answer** - Problems can return multiple answers formatted as "Answer1 | Answer2 | Answer3"
- **CLI Options** - Added `--input` flag for generating from specific template file
- **Context Handling** - Templates have access to both raw values (for logic) and formatted values (for display)

#### Migration Summary

- **33 YAML templates** migrated from 33 Mustache templates
- **All 5 topics** converted: arithmetic (10), geometry (5), measurement (7), percentages (6), ratios (5)
- **Infrastructure modules** created: yaml_loader, jinja_renderer, variable_generator (6 new files)
- **Old modules removed** - variable_parser.py, template_helpers.py, template_loader.py (Mustache-specific)
- **Dependencies updated** - Removed chevron, added jinja2>=3.1.0, pyyaml>=6.0
- **Cleanup** - Removed 7 temporary test/verification scripts

#### Test Coverage

- **35/35 tests passing** (100% success rate)
- All templates validated and tested
- Multi-answer problems verified
- Format system tested (money, time, area, perimeter, speed)

#### Breaking Changes

- Template format changed from `.mustache` to `.yaml`
- Variable syntax changed from `{{name_person}}` to YAML structure
- Solution section now uses Python expressions instead of Mustache variables

#### Documentation

- **src/templates/SPEC.md** - Complete template format specification (moved from docs/INDEX.md)
- **Updated copilot-instructions.md** - Reflects new YAML+Jinja2 system
- **Grade-level examples** - docs/K1_PROBLEMS.md through docs/K12_PROBLEMS.md

---

## [0.1.1] - 2026-01-30 - Template-Driven Architecture

### 🚀 Major Refactoring: Pure Template-Driven Generation

Complete architectural shift from Python family classes to self-describing Mustache templates.

#### New System Overview

- **No more Python family classes** - All problem generation driven by `.mustache` templates
- **Self-describing variables** - Metadata embedded in variable names (e.g., `{{price_decimal_money_min_5_max_20}}`)
- **Computed answers** - Solution expressions evaluated from template's `---` section
- **Template helpers** - 8 Mustache lambdas for text formatting

#### New Core Modules

| Module | Purpose |
|--------|---------|
| `src/variable_parser.py` | Parses variable metadata from template names |
| `src/template_helpers.py` | Mustache helper functions (choice, plural, etc.) |
| `src/solution_evaluator.py` | Evaluates solution expressions for answers |
| `src/template_generator.py` | Main generator class, discovers and renders templates |

#### Template Format

```mustache
{{name_person}} bought {{qty_integer_min_2_max_5}} items for {{price_decimal_money_min_5_max_20}}.
---
total = {{qty}} * {{price}}
Answer = total
```

#### Migration Summary

- **30 templates migrated** from old structure to new naming convention
- **5 directories reorganized** by topic (arithmetic, geometry, measurement, percentages, ratios)
- **Old family directories removed** (sequential_purchase, rate_time, compound_growth, etc.)
- **Old Python family files deleted** (5 files in `src/families/`)

#### Backward Compatibility

- Family name aliases: `sequential_purchase` → `shopping`, `rate_time` → `travel`, etc.
- Grade mapping: `elementary` → k1-k5, `middle` → k6-k8, `high` → k9-k12
- Legacy variable inference for templates without metadata

#### Test Results

- **51/52 tests passing** (98% success rate)
- 1 known issue: `test_avoid_duplicates` needs more template variety

---

## [0.1.0] - 2026-01-28 - Initial Implementation

### 🎉 Project Setup Complete

Fully functional Python library for generating procedurally-created, multi-step math word problems.

#### Features Implemented

**Core Functionality:**
- Single problem generation with `generate_problem()`
- Batch generation with `generate_problems()`
- Available options query with `get_available_options()`
- Seed-based reproducibility
- Duplicate avoidance in batch mode

**Problem Families (5):**
1. `sequential_purchase` - Shopping scenarios with discounts
2. `rate_time` - Distance/speed/time problems
3. `compound_growth` - Interest/investment problems
4. `multi_person_sharing` - Ratio/splitting problems
5. `area_perimeter_chain` - Geometry problems

**Math Topics (9):**
arithmetic, percentages, fractions, ratios, algebra, geometry, quadratics, derivatives, powers_logs

**Configuration Parameters:**
- `complexity` (1-3)
- `grade` (elementary, middle, high, college, university)
- `math_topic` (9 topics)
- `problem_family` (5 families)
- `num_steps` (1-10)
- `seed` (for reproducibility)

#### Output Format

```json
{
  "test_id": "math_7912_sequential_purchase",
  "task_type": "multi_step_math",
  "config_name": "sequential_purchase_medium_arithmetic",
  "problem": "Natural language problem text...",
  "task_params": {
    "complexity": 2,
    "grade": "middle",
    "math_topic": ["arithmetic"],
    "problem_family": "sequential_purchase",
    "num_steps": 6,
    "expected_answer": "$37.20",
    "operations": ["multiply", "add"]
  }
}
```

#### Dependencies

- `faker>=20.0.0` - Realistic fake data
- `names>=0.3.0` - Person name generation
- `chevron>=0.14.0` - Mustache template rendering
- `inflect>=7.0.0` - Pluralization (added in v2.0)

---

## Project Structure

```
mathbot/
├── src/
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point
│   ├── cli_formatters.py       # Output formatters
│   ├── constants.py            # Configuration constants
│   ├── generator.py            # Public API
│   ├── providers.py            # MathProblemProvider (Faker)
│   ├── template_generator.py   # Template-driven generator
│   ├── template_helpers.py     # Mustache helpers
│   ├── template_loader.py      # Template loading utilities
│   ├── solution_evaluator.py   # Answer computation
│   ├── variable_parser.py      # Variable metadata parsing
│   ├── utils.py                # Utility functions
│   └── templates/              # Mustache templates
│       ├── arithmetic/         # Shopping problems
│       ├── geometry/           # Shape problems
│       ├── measurement/        # Travel problems
│       ├── percentages/        # Growth problems
│       └── ratios/             # Sharing problems
├── tests/
│   ├── test_cli.py
│   └── test_generator.py
├── docs/
│   ├── INDEX.md               # Template reference
│   └── K1-K12_PROBLEMS.md     # Grade-level examples
└── pyproject.toml
```

---

## Quick Start

```bash
# Install
uv sync

# Generate a problem
mathbot generate --grade middle --complexity 2 --topic arithmetic

# With seed for reproducibility
mathbot generate --seed 42

# Run tests
pytest
```

---

## Future Improvements

- [ ] Add more templates for broader coverage
- [ ] Implement template validation tool
- [ ] Add more variable types (date, temperature, weight)
- [ ] Support for symbolic algebra (SymPy integration)
- [ ] Multilingual template support
