# Tech debt log

A running ledger of known infrastructure debt, intentional shortcuts, and
follow-ups that didn't fit a recent change. New entries land at the top
of their section; resolved entries get a `~~strikethrough~~` and a brief
disposition note before being archived to git history.

Entries note **why** the debt exists (often a deliberate trade-off) and
**what would resolve it**, so future-you can judge whether the shortcut
is still worth carrying.

---

## 1. Active blockers — something downstream wants this fixed

### TD-1.2 — `names` library is en-only and ignores Faker locale

[src/variable_generator.py:62](src/variable_generator.py#L62) calls
`names.get_first_name()` for `person`/`name` types. The `names` library
has no locale parameter — it always returns en-US first names. With M4
(Phase 5.6) the rest of `VariableGenerator` is locale-aware (Faker is
configurable via `template.culture`), but person names are stuck in
English. A `de-DE` template renders "Hans bought…" today only by accident
of Faker's German cities pairing with American first names.

**Resolution**: When the first non-`en` template lands, replace
`names.get_first_name()` with per-locale name pools in
`pools.<lang>.yaml` (`naming.first_names_male`, `..._female`,
`..._neutral`). Drop the `names` dependency. Until then, document the
limitation; current corpus is 100% en-US so it doesn't bite.

---

## 2. Documented intentional limitations

### TD-2.0 — gol_eval plugin generator shells out via `uv run`

[gol_plugin/generator.py](gol_plugin/generator.py) calls
`uv run --project <mathbot_root> mathbot batch …` per `generate_batch`
invocation. Pays one Python interpreter + uv resolution startup
(~1-2s) per call, regardless of `count`. The choice was deliberate:
direct import would require resolving the `src.*` namespace collision
between gol_eval's package and mathbot's (mathbot's `pyproject.toml`
declares `packages = ["src"]`), which is more brittle than a
subprocess.

**Disposition**: Accepted. `generate_batch` is called once per
test-set generation, not per problem — N problems generated in one
batch amortises the startup cost. Only matters for very large N or
many small `generate_batch` calls in a tight loop.

**Resolution path** (deferred): rename mathbot's package from `src`
to `mathbot` (touches every `from src.X import Y` in the codebase
and `[tool.hatch.build.targets.wheel]` in pyproject.toml). Then the
plugin imports `mathbot.generator.generate_problem` directly. Worth
doing if mathbot is ever published to PyPI; not urgent otherwise.

### TD-2.0a — gol_eval plugin auto-detects mathbot root via `__file__` walk-up

[gol_plugin/generator.py:_find_mathbot_root](gol_plugin/generator.py#L36)
resolves symlinks then walks up looking for a `pyproject.toml` with
`name = "mathbot"`. Works for the canonical layout (plugin lives at
`mathbot/gol_plugin/`, symlinked into `gol_eval/src/plugins/mathbot`).
Breaks if the plugin is copied (not symlinked) into gol_eval, or if
the plugin lives outside the mathbot repo entirely.

**Disposition**: The `mathbot_root` config field is the documented
escape hatch — explicit override of the auto-detected path. Acceptable
trade-off: zero-config in the canonical setup, one-line override
otherwise.

### TD-2.0b — Plugin schema fields `grade`/`topic` are single-select

The mathbot CLI takes a single `-g`/`-t`/`-f` value per invocation, so
the plugin's `get_config_schema()` exposes them as `select` (not
`multi-select`). Multi-grade or multi-topic test sets require running
gol_eval's test-set generation multiple times with different config
values.

**Disposition**: Accepted for now. If campaigns repeatedly want
multi-grade sweeps, the generator could be extended to call
`mathbot batch` once per selected value and concatenate results
(losing seed determinism across the union, gaining batch ergonomics).

### TD-2.1 — Solution sandbox `safe_globals` is wide

Phase 5.1 added `sympy` and `scipy.stats` namespaces to the sandbox.
Both are pure-Python with no I/O, but their surface area is enormous
(sympy alone exposes `sympy.utilities.codegen` etc.). A malicious
template could import other modules from those packages.

**Disposition**: Accepted. Templates are first-party content; the sandbox
defends against template-author mistakes (no infinite loops via
allow-listed builtins), not against an attacker supplying templates.
If we ever load templates from untrusted sources, this needs a real
sandbox (`RestrictedPython` or subprocess isolation).

### TD-2.2 — `sympy.simplify()` is expensive; symbolic-numeric mixing balloons trees

When a solution mixes `sympy.Symbol` arithmetic with regular floats,
expression trees grow with each operation. `simplify()` calls have
worst-case cubic complexity. A naive P-A2 (formula-rearrangement)
template that calls `simplify()` after every step can take seconds.

**Disposition**: Documented in CLAUDE.md "Solution sandbox" section.
Authors should call `simplify()` once at the end, not every step. If
this becomes a real problem, add a sandbox timeout (currently none).

### TD-2.3 — RNG double-seeding is intentional but a footgun

Both `TemplateGenerator.generate()` and `VariableGenerator.__init__()`
call `random.seed()` and `Faker.seed()` with the same seed. This
guarantees variable values depend only on the seed (not on which
template was selected — template selection consumes entropy). Comment
added at [src/template_generator.py:186-192](src/template_generator.py#L186-L192).

**The footgun**: introducing any `random.*` or `Faker.*` call between
the two seedings (e.g. logging a Faker-generated debug string) changes
every existing fixture's RNG state silently.

**Resolution path** (deferred): thread an `rng` instance through
`TemplateGenerator` → `VariableGenerator` → `MathProblemProvider` instead
of relying on global state. Touches ~5 files and changes every fixture
output (would require a full `refresh_test_answers.py` regen + manual
review). Not worth doing standalone; bundle with a future fixture-changing
phase.

---

## 3. Future-phase enablers

### TD-3.1b — Visual Approach B: Python builder classes in sandbox

Phase 5.5 shipped Approach A (Jinja-rendered SVG block in YAML), good
for static geometric figures where coordinates are known up front. For
**derived-coordinate visuals** — probability trees with branch counts
chosen at generation time, bar charts whose heights come from a
data_set, scatter plots — Jinja-SVG gets unwieldy fast (every
coordinate is an inline arithmetic expression).

Approach B: an `SVG` / `TreeSVG` / `BarChartSVG` builder family exposed
in `safe_globals`, called from solution code:

```python
solution: |
  tree = TreeSVG()
  tree.branch("D", p=0.04).then("+", p=0.96).then("-", p=0.04)
  tree.branch("~D", p=0.96).then("+", p=0.08).then("-", p=0.92)
  Visual = tree.render()
  Answer = ...
```

Schema reservation already in place: `VALID_VISUAL_FORMATS` is set up
to accept `"python"` as a second format, and the parser would just
need to dispatch on it (eval the source against `safe_globals`,
capture the `Visual` binding, store as SVG in the output).

**Resolution path**: probably ~300 lines of builder classes plus
sandbox wiring. Wait until the first probability-tree (P-S2) or
bar-chart (P-S1) template needs it, so the API is shaped by a real
use case rather than speculation.


### TD-3.1d — Rasterizer not exercised in CI

`tests/test_visual.py` covers schema, rendering, and end-to-end output,
but skips the rasterizer because it requires `libcairo` on the test
runner. End-to-end PNG production was verified manually
(`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run mathbot rasterize
…`). If/when a CI environment with cairo arrives, add a single
integration test that rasterizes one fixture and asserts the PNG is
non-empty / has the expected dimensions.

### TD-3.2 — Multi-lang Stage 2 / Stage 3

Phase 5.6 landed the foundation: `language` field, `LanguageSpec`
registry, locale-aware filters, pools-as-YAML. **Stage 2** (one
non-English POC, ~20 anchor translations, validates the per-language
template-file vs single-file-with-lang-map decision) and **Stage 3**
(multi-cultural pools, currency-by-locale, gender/case inflection for
DE/UA-style languages) are roadmap.

**Decision pending**: when Stage 2 starts, pick language. Recommend ES
(easier) or DE (proves gender/case handling).

### TD-3.3 — Dead `VALID_TYPES` may need re-implementation

Phase 5.6 M1 deleted 33 declared-but-unimplemented types from
[src/yaml_loader.py:66](src/yaml_loader.py#L66) (geometry shapes,
algebra/calculus structures, statistics distributions). The
[proposal](MATHBOT_PROBLEMS_PROPOSAL.md) families P-G2 (trigonometry),
P-S4 (binomial distribution), and others may want some of these back as
proper variable types rather than ad-hoc strings.

**Disposition**: Deliberate clean-slate. Re-add each type alongside the
template that needs it — declare in `VALID_TYPES`, add a generator
branch, add a formatter branch. Don't pre-declare types speculatively
(that's how 33 dead types accumulated).


---

## 4. Doc / version / config drift

### TD-4.1 — `pyproject.toml` version vs CHANGELOG drift

[pyproject.toml:3](pyproject.toml#L3) still reads `version = "0.1.1"`
while CHANGELOG.md has reached `[0.2.0]`. The version bump on
`pyproject.toml` was missed during the v0.1.2 / v0.1.3 / v0.2.0
releases. Bumping breaks nothing, but tools that key off the package
version (PyPI, build metadata) see stale info.

**Resolution**: Bump to `0.2.0` next time someone touches pyproject.toml
for any reason. Or set up a release script that bumps both atomically.

### TD-4.2 — `requires-python = ">=3.9"` is wrong

[pyproject.toml:6](pyproject.toml#L6) declares `>=3.9` but the codebase
uses `math.lcm` (added in 3.9), `dict | dict` syntax (3.9), and now
`math.comb` / `math.perm` (3.8+) and `tuple[bool, str]` annotations in
[src/jinja_renderer.py:139](src/jinja_renderer.py#L139) (3.9+, OK). The
`.venv` is built against 3.12 per CLAUDE.md. Phase 4 plan also flagged
this.

**Resolution**: Tighten to `>=3.10,<3.13` (Phase 4 plan suggestion).
`uv lock --upgrade` after the change.

### TD-4.3 — `src/templates/SPEC.md` not refreshed for Phase 5 schema

The inline schema reference at `src/templates/SPEC.md` doesn't yet
mention `language` (added in 5.6), `unit_system` (5.3 plan), or
`visual:` (5.5 plan). CLAUDE.md is up to date but SPEC.md is the
"source of truth" for template authors.

**Resolution**: Phase 5.7 doc pass; bundled with the lint subcommand.

### TD-4.4 — Stale references to `migrate_templates.py`

[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) (untracked) and
[mathbot-phase4-template-corpus-cleanup.md](mathbot-phase4-template-corpus-cleanup.md)
both reference the now-deleted script. REFACTORING_SUMMARY.md is a
historical artifact (untracked, predates v0.1.3) and probably should be
deleted or moved to a `docs/archive/` folder. The Phase 4 cleanup plan
is a similar artifact.

**Resolution**: User decision — keep as historical record (move to
`docs/archive/`?) or delete.

### TD-4.5 — `culture` vs `language` semantic boundary is fuzzy

Phase 5.6 split the dormant `culture` field into:
- `language: en` → drives Jinja filters (plural, ordinal, number_to_words) and sandbox `number_to_words`
- `culture: en-US` → drives Faker locale (cities, companies)

This is the standard BCP-47 split (language code vs full tag) but the
mapping is not bidirectional: `language: en` + `culture: de-DE` would
produce English problems with German cities — possibly nonsense.

**Disposition**: Document the constraint when Stage 2 of multi-lang
starts. Consider an at-load validation that the `language` matches the
prefix of `culture`.

---

## 5. Low-priority cleanups

### TD-5.1 — `_formatted` companion convention is implicit

[src/template_generator.py:248-249](src/template_generator.py#L248) auto-creates a `{var_name}_formatted` companion for typed variables (e.g.
`total_formatted` = `"$60.00"` while `total` = `60.0`). Documented in
CLAUDE.md but not in `src/templates/SPEC.md`, and no validator catches
templates that try to use a non-existent `_formatted` variable (silent
empty render).

**Resolution**: SPEC.md update + a Jinja undefined-variable mode bump
(currently silent; could be `StrictUndefined`).

### TD-5.2 — `MATH_TOPICS` in `src/constants.py` may be stale

The constant lists 14 top-level topics:
`["numbers", "arithmetic", "percentages", "fractions", "decimals", "ratios", "algebra", "geometry", "measurement", "statistics", "quadratics", "derivatives", "powers_logs"]`.
The corpus has 10 actual topic dirs (the last 3 — `quadratics`,
`derivatives`, `powers_logs` — were on the v0.1.0 spec but no template
ever lived there). Not breaking anything; just dead-code-ish.

**Resolution**: Audit + delete during the next pass on `constants.py`.

### TD-5.3 — `DEPRECIATING_ITEMS` schema is fragile

`src/data/pools.en.yaml` stores depreciating items as
`{name, min_price, max_price, rates: [...]}`; the loader converts to a
4-tuple including the rates list. Awkward shape (tuple-with-embedded-list)
that complicates future refactors. Only used by one provider method
(`depreciating_item()`).

**Resolution**: Migrate consumers to read dicts directly when the next
template uses them. Not worth a standalone refactor.

### TD-5.4 — `inflect` is imported in two places now

Phase 5.6 moved the `_inflect_engine` from `solution_evaluator` to
`src/i18n/languages.py`. The renderer's old `p = inflect.engine()`
module-global was removed entirely (renderer now goes through `LanguageSpec`).
Net: only one place uses `inflect` directly. Cleanup complete; documenting
to track that the dependency could be dropped if a different
pluralization library replaces it.

### TD-5.5 — Run artefacts and ephemeral inputs not in `.gitignore`

`contamination.json`, `coverage.csv`, `sample200.jsonl`, `runs/`,
plus the JSON output of `mathbot lint` / `mathbot health` when
redirected to a tracked path. Land in the working tree as untracked
noise.

**Resolution**: Add a `.gitignore` block for these patterns. None of
them belong in the repo — they're rerun-able outputs sized in the MB.

**Note**: Phase 5.7 deleted the four scripts
(`audit_templates.py`, `scripts/coverage_matrix.py`,
`scripts/internal_contamination.py`, `scripts/dump_all_samples.py`)
that produced most of the historical artefacts mentioned here. The
CLI commands `mathbot lint --json` / `mathbot health --json` now
emit to stdout by default, so authors redirect to whatever path
suits their workflow rather than landing in fixed filenames at the
repo root. `scripts/gsm8k_contamination.py` and
`scripts/refresh_test_answers.py` are the remaining committed
helper scripts.

### TD-5.6 — `cli.py` has 25 tests for 1 entry point

[tests/test_cli.py](tests/test_cli.py) is 25 of the 79 tests. CLI is the
most-tested layer. Possibly over-tested relative to e.g. the renderer
(no dedicated test file). Not actionable until a renderer change reveals
a coverage gap.

---

## Resolved (recent)

(Move entries here with a brief disposition before archiving to git
history.)

- ~~`mathbot lint` subcommand not yet shipped (TD-3.4)~~ — Phase 5.7
  (v0.3.0) shipped `mathbot lint [PATH]` and `mathbot health` plus a
  new `src/audit/` package as the single source of truth. Lint covers
  schema, render-smoke (K seeds), visual-render smoke, fixture drift,
  anchor convention, off-anchor divergence (Phase 4 plan's variant-vs-
  anchor structural drift detector), and the rendered-output rules
  ported from the deleted `audit_templates.py` (unrendered Jinja,
  GSM8K saturation, body length, unit-form drift, area/volume answer
  heuristics). The four standalone scripts (`audit_templates.py`,
  `scripts/coverage_matrix.py`, `scripts/internal_contamination.py`,
  `scripts/dump_all_samples.py`) deleted. JSON to stdout via `--json`,
  one-line stderr summary, exit codes signal CI-actionable state.
  Real corpus: 0 errors / 243 warnings / 84 info. 16 new tests
  (150/150 total); 0 of 1278 fixtures changed.
- ~~`mathbot lint` doesn't pre-render visuals (TD-3.1c)~~ — Phase 5.7
  (v0.3.0) added the `visual_render_crash` rule. `mathbot lint`
  smoke-renders every template's `visual.source` against the same
  variable context the problem text saw and parses the output as XML;
  broken Jinja vars or malformed `<svg>` markup fire as `error`-
  severity findings.
- ~~Free-form `unit:` field on `VariableSpec` (TD-3.6)~~ — Phase 5.3R
  Stage 3 (v0.2.6) shipped the optional `unit:` field on
  `VariableSpec`. The string is validated at load time via
  `ureg.parse_units()` and formatted with pint's compact pretty form
  (`~P` → `m/s²`, `kg/m³`, `mi/gal`). When set, it overrides the
  `(type, system)` table — `{type: weight, unit: 'gram'}` renders
  `"11 g"` regardless of the template's `unit_system`. Pairs with the
  Stage 2 sandbox: a Quantity returned as `Answer` is converted into
  `spec.unit` via the new `unit_override` parameter on
  `quantity_to_canonical_magnitude`. Templates also get an
  auto-injected `<var>_unit` companion so the unit string isn't
  hardcoded in two places. 11 new tests in `TestFreeFormUnit`
  (134/134 total); 0 of 1278 fixtures changed in dry-run. Pint
  refactor is now functionally complete.
- ~~Compound-unit variable types and sandbox `Q_` exposure (TD-3.5)~~
  — Phase 5.3R Stage 2 (v0.2.5) shipped `density`, `energy`, `power`,
  `pressure`, `force`, `acceleration` as compound types in
  `DISPLAY_UNITS` (with `imperial` swapping in lb/ft³, ft·lbf, hp, psi,
  lbf, ft/s²; `mixed_us` and `metric` track SI). The sandbox exposes
  `ureg`, `Q_`, and `get_pint_unit`; `format_answer` now unwraps
  `pint.Quantity` Answer values via the new
  `quantity_to_canonical_magnitude` helper. 19 new tests in
  `TestCompoundTypes` and `TestPintSandbox` (124/124 total). Fixture
  byte-identity preserved (0 of 1278 fixtures changed in dry-run).
- ~~Visual layer (`visual:` block) not yet present~~ — Phase 5.5
  shipped Approach A: optional `visual:` block in YAML with a Jinja-
  rendered SVG `source` and `alt_text`. New `mathbot rasterize`
  subcommand turns dataset SVGs into PNGs at any DPI (lazy `cairosvg`
  via the `png` optional extra; system `libcairo` required at PNG
  time). Output JSON gains `visual: {format, source, alt_text,
  png_path}`. The first anchor with a visual ships in
  `geometry/k5_easy_square_area_01_anchor.yaml`. Approach B (Python
  builder classes for derived-coordinate visuals like prob trees)
  rolls forward as TD-3.1b.
- ~~Mixed-system formatter (USD + mph + meters + kg + °F)~~ — Phase 5.3
  introduced `metadata.unit_system` (`metric`|`imperial`|`mixed_us`,
  default `mixed_us`) plus per-variable override on `VariableSpec`.
  New [src/units.py](src/units.py) holds the `UNIT_TABLE`. Formatters
  in [src/variable_generator.py](src/variable_generator.py) and
  [src/solution_evaluator.py](src/solution_evaluator.py) now consume
  the system through the threading from `template_generator`.
  `mixed_us` reproduces pre-5.3 byte-identical output, verified by
  dry-run `scripts/refresh_test_answers.py` (0 of 1307 fixtures
  changed). 25 new tests in `tests/test_units.py` lock metric/imperial
  divergence and the per-variable override path.
- ~~Sandbox missing `sin/cos/log/factorial/comb/pi/e/sqrt`~~ — landed in
  Phase 5.1; surfaced top-level. See CHANGELOG.
- ~~Topic↔directory invariant documented but not enforced~~ — Phase 5.1
  added the validator; corpus had zero violations.
- ~~`migrate_templates.py` is broken~~ — deleted in Phase 5.1.
- ~~33 declared-but-dead `VALID_TYPES`~~ — deleted in Phase 5.6 M1.
- ~~`culture` field set on 403 templates but never read~~ — Phase 5.6 M2/M4
  wired it up to Faker locale; new sibling `language` field drives filters.
- ~~Entity pools hardcoded in `providers.py`~~ — Phase 5.6 M3 moved to
  `src/data/pools.en.yaml` with a thin loader.
- ~~Sandbox `except Exception as e` shadowed `math.e`~~ — Phase 5.1
  renamed to `as exc`. (Trivial bug, but it bit the very first
  verification of the new sandbox primitives.)
- ~~Bespoke Ollama smoke harness (`scripts/test_model.py`,
  `scripts/_ollama.py`, `scripts/_eval/`, `tests/test_eval.py`)
  reproduces gol_eval infrastructure~~ — retired in v0.2.1; mathbot
  now exposes a gol_eval plugin at `gol_plugin/` that's symlinked
  into gol_eval's plugin tree. The custom parser/comparator logic
  was preserved by porting to the plugin's `parser.py` + `evaluator.py`.
  `httpx` dropped from runtime deps.
- ~~Two near-duplicate templates from the v0.1.3 corpus
  cleanup~~ — `k6_easy_inequalities_02.yaml` (sim 1.000 with
  `_01_anchor`) and `k5_medium_powers_of_10_03.yaml` (sim 0.556
  with `_01_anchor`) deleted in v0.2.1. Surfaced by the new
  [scripts/internal_contamination.py](scripts/internal_contamination.py)
  self-similarity sweep. Anchors preserved.
