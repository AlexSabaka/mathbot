# Mathbot Phase 4 Plan — Template Corpus Cleanup & Seeding

## Context

The mathbot infrastructure (CLI, loader, generator, batch) is now working — Phases 1-3 from the previous plan are landed. What remains is the **template corpus**: 892 YAML files where 79.5% have stale embedded `tests:` expected answers, 1.7% throw exceptions, and a substantial fraction are clear duplicates introduced by an over-zealous initial generation pass. The user's goal: **strip the trash, leave a clean high-quality seed, then grow back from there with discipline**.

This plan is a four-stage roadmap with all preparatory research done. **No deletions or rewrites have been executed yet** — every recommendation below is a proposal awaiting approval.

Five sub-agents reviewed the corpus by topic slice. Their detailed reports are at `/tmp/mathbot_review_{arithmetic,algebra,geometry,fractions_decimals,stats_ratios}.md`. Agent recommendations are not uniformly calibrated — see "Agent calibration note" in Stage 1.

---

## Stage 1 — Templates recommended for deletion

### Aggregate counts

| Slice                        | Files | Agent DELETE | Confidence |
|------------------------------|-------|--------------|------------|
| arithmetic + percentages     | 233   | 104          | high       |
| algebra + numbers + measurement | 198 | 2          | high (lenient — see note) |
| geometry                     | 204   | 89           | high       |
| fractions + decimals         | 162   | 0            | low (lenient — see note) |
| statistics + ratios          | 95    | 51           | high       |
| **total**                    | **892** | **246** (~28%) | mixed |

### Agent calibration note

The **arithmetic** and **geometry** agents flagged any `_01/_02/_03` triplet whose variants differ only in number ranges or surface context as duplicates. They were strict.

The **algebra** agent was correct to be lenient — spot-checked [src/templates/algebra/k5_easy_expressions_intro_01.yaml](src/templates/algebra/k5_easy_expressions_intro_01.yaml), [_02.yaml](src/templates/algebra/k5_easy_expressions_intro_02.yaml), [_03.yaml](src/templates/algebra/k5_easy_expressions_intro_03.yaml) and they really do test addition / subtraction / multiplication respectively, distinct skills.

The **fractions** agent was too lenient — spot-checked [src/templates/fractions/k5_medium_fractions_mult_whole_01.yaml](src/templates/fractions/k5_medium_fractions_mult_whole_01.yaml), [_02.yaml](src/templates/fractions/k5_medium_fractions_mult_whole_02.yaml), [_03.yaml](src/templates/fractions/k5_medium_fractions_mult_whole_03.yaml) — same math (fraction × whole), different surface context (days/students/weeks). These are the same kind of duplicate the arithmetic agent flagged. **Recommend a strict re-pass on fractions** before executing deletions.

### Confirmed-unrecoverable templates (3, delete outright)

These have hard structural bugs the agents flagged independently:

- [src/templates/algebra/k5_hard_expressions_intro_03.yaml](src/templates/algebra/k5_hard_expressions_intro_03.yaml) — references `{{name}}` which is never declared in `variables:`
- [src/templates/numbers/k1_hard_counting_01.yaml](src/templates/numbers/k1_hard_counting_01.yaml) — uses non-existent Jinja2 `repeat` filter
- [src/templates/geometry/k5_easy_rectangle_area_02.yaml](src/templates/geometry/k5_easy_rectangle_area_02.yaml) — labelled `family: rectangle_area` but the problem text and solution compute *perimeter*

### Deletion list categories (post-agent-aggregation, post-pattern-expansion)

- **Trivial range-variation duplicates** (~120-150 files): same template, same math, different `min/max` ranges. Best examples: `k4_easy_division_basic_{01,02,03}`, `k5_easy_rectangle_area_{01,02,03}`. Keep `_01`, delete `_02/_03`.
- **Context-only variants** (~50 files): same template, different domain words (apples vs oranges, days vs students). Most arise in arithmetic/shopping families.
- **Off-grade triviality at K6** (~45 files in statistics): `bar_graphs`, `histograms`, `frequency_tables`, `range`. Per stats agent, all are K3-K4 arithmetic dressed up as K6 statistics.
- **Mislabeled / unrecoverable** (3 files above).

### Recommended Stage 1 actions

1. **Run a strict re-pass** on `fractions/` (and possibly `algebra/`, `decimals/`) with the same calibration as the arithmetic/geometry agents — count fractions/decimals likely doubles to ~30-50 deletions. Use the same Explore-agent pattern with explicit "if same math + same step count, even with different surface, treat as duplicate" rule.
2. **Materialize the explicit deletion list**: aggregate from agent reports + pattern expansion into a single `/tmp/mathbot_deletions_final.txt`. The current best-effort expansion is at `/tmp/mathbot_deletions_expanded.json`.
3. **Have me show you the deletion list before executing**. Spot-check 20 random entries to validate.
4. **Execute deletion in a single git commit** ("delete N duplicate/unrecoverable templates"). Reversible via `git revert`.

**Estimated final deletion count after re-pass**: ~280-330 templates (out of 892), leaving ~560-610 survivors.

---

## Stage 2 — Bug fixes for survivors

### Bug class A: missing `gcd`/`lcm` in solution sandbox

**Root cause** — confirmed by inspecting [src/solution_evaluator.py](src/solution_evaluator.py): the `safe_globals` dict provides `math` and `Decimal` but NOT `gcd`, `lcm`, or other math top-level functions. Templates that say `gcd(a, b)` directly (vs `math.gcd(a, b)`) error out.

**Affected templates** (per fractions/decimals agent):
- 12 BROKEN K4/K6 fraction add/sub/simplify templates
- 18 latent K5 fraction mult/mixed templates (use `math.gcd` without `import math` — works for the ones that have `math` in globals, fails for the ones missing it)
- 1 BROKEN [src/templates/arithmetic/k4_hard_divisibility_rules_01.yaml](src/templates/arithmetic/k4_hard_divisibility_rules_01.yaml)

**Fix** — single edit, covers all 31:
```python
# src/solution_evaluator.py: extend safe_globals
from math import gcd, lcm  # at top of file
safe_globals = {
    ...,
    'gcd': gcd,
    'lcm': lcm,
}
```

This is a 3-line change to [src/solution_evaluator.py](src/solution_evaluator.py) and resolves all 31 templates without touching a single YAML.

### Bug class B: stale `tests:` expected values

**Scale**: 709 of 892 templates (79.5%). After Stage 1 deletions, perhaps 500-550 templates need this.

**Root cause**: refactor changed seed→variable mapping. Templates generate correct math, but recorded `expected.answer` values are now wrong.

**Existing tooling is broken**: [migrate_templates.py](migrate_templates.py:87) only updates tests when a `format:` → `type:` migration triggers (`if update_tests and changes_made:`). Since all templates already migrated, `changes_made` is always false → no-op. It also rewrites with `yaml.dump`, destroying comments and key order across all 892 files.

**Recommended fix** — write a small surgical regenerator at `scripts/refresh_test_answers.py`:
- Use `ruamel.yaml` (preserves comments, key order, quoting) — add it to dev deps
- For each template with at least one stale test:
  1. Load via `YAMLLoader` (validate)
  2. For each `tests[i].seed`, run `TemplateGenerator._generate_from_template(t, seed=tc.seed)`
  3. If `actual_answer != tests[i].expected.answer`, rewrite ONLY the `expected.answer` field
  4. Write file with `ruamel.yaml.YAML(typ='rt').dump(data, f)` to preserve formatting
- CLI: `--dry-run` (default), `--apply`, `--filter <glob>` for partial runs
- Print a summary: `N updated, M unchanged, K errored`

This script also lets you re-validate answers any time the generator changes — much more robust than the current `migrate_templates.py`.

### Bug class C: real generator inconsistencies (small but present)

A few templates flagged STALE may actually have generator bugs that *changed semantics*, not just RNG mapping. To avoid blindly enshrining incorrect answers as ground truth:

- Before bulk-running the regenerator, **spot-check 20 STALE templates manually**. Read the problem, mentally compute the answer, compare to the generator's new output. If 19/20 are correct, regenerate. If e.g. 5/20 are wrong, halt — there's a generator regression to find first.

### Recommended Stage 2 actions

1. Land the 3-line `gcd`/`lcm` fix to [src/solution_evaluator.py](src/solution_evaluator.py). This unblocks 31 templates immediately.
2. Add `ruamel.yaml` to `[dependency-groups.dev]` in [pyproject.toml](pyproject.toml).
3. Write `scripts/refresh_test_answers.py` (~150 lines, no external dependencies beyond ruamel).
4. Run `python scripts/refresh_test_answers.py --filter 'arithmetic/k3*'` (small slice) — manually verify 20 randomly-sampled rewrites.
5. Run full corpus with `--dry-run`, eyeball stats, then `--apply` and commit.

---

## Stage 3 — Distribution analysis post-deletion

Computed against the expanded deletion list (~245 deletions). Final numbers will shift after the strict fractions re-pass.

### Files per grade — current vs proposed

| Grade | Current | After deletions | Notes |
|-------|---------|-----------------|-------|
| K1    | 51      | 51              | no deletions |
| K2    | 96      | 96              | no deletions |
| K3    | 46      | 46              | no deletions |
| K4    | 72      | 72              | a few unrecoverable losses |
| **K5** | **201** | **133**       | -68 (geometry shape duplicates, stats triplets) |
| **K6** | **307** | **238**       | -69 (stats off-grade, factors/lcm/gcd/order_ops triplets) |
| K7    | 6       | 6               | already thin |
| K8    | 3       | 3               | already thin |
| K9    | 3       | 3               | already thin |
| K11   | 1       | 1               | singleton |
| K12   | 1       | 1               | singleton |

**Key finding**: K7-K12 has only **14 files combined** — barely covered. Most of the corpus weight is concentrated in K5-K6 (371 files post-deletion = 65% of the surviving corpus). K1-K3 has 193 files but skewed heavily to K2 addition.

### Files per top-level topic — post-deletion

| Topic         | sub-topics | files | density (files/sub) |
|---------------|------------|-------|---------------------|
| geometry      | 27         | 209   | 7.7                 |
| arithmetic    | 33         | 126   | 3.8                 |
| algebra       | 10         | 89    | 8.9                 |
| fractions     | 12         | 81    | 6.8                 |
| decimals      | 11         | 81    | 7.4                 |
| statistics    | 8          | 72    | 9.0 (skewed; will drop heavily after K6 stats deletion) |
| measurement   | 11         | 50    | 4.5                 |
| numbers       | 7          | 42    | 6.0                 |
| ratios        | 9          | 23    | 2.6                 |
| percentages   | 9          | 14    | 1.6                 |

After the K6 stats deletion lands, statistics will collapse to ~9 files. Percentages and ratios are already thin. **Spec-mandated families** from `.claude/CLAUDE.md` (`sequential_purchase`, `rate_time`, `compound_growth`, `multi_person_sharing`, `area_perimeter_chain`) are barely present:
- `sequential_purchase` exists in arithmetic (~10 templates pre-deletion, ~5 post)
- `rate_time` → maps to `travel`/`measurement.time` family (~5 templates)
- `compound_growth` → `percentages.growth` (5 templates)
- `multi_person_sharing` → `ratios.sharing` (~7 templates)
- `area_perimeter_chain` → no exact match; closest is `geometry.area_composite` (3-4 templates post-deletion)

### Coverage gaps to address in Stage 4

**Empty/extinct triplets** (deletions wipe these out completely):
- (K6, percentages.comparison, percentage)
- (K6, statistics.bar_graphs)
- (K6, statistics.frequency_tables)
- (K6, statistics.histograms)
- (K6, statistics.range)

Of these, only `percentages.comparison` is clearly worth recovering — the K6 stats families can stay deleted (off-grade per stats agent).

**Critically sparse triplets** (1-2 templates after deletion, likely 31 such triplets):
- All K7-K12 triplets except `arithmetic.multi_step` → essentially the entire upper grade band
- (K3, arithmetic.addition, sequential) — only 1 template
- (K6, ratios.proportions, sharing) — only 1
- (K8, geometry.area, geometry) — only 1

**Conceptual gaps the spec calls out but doesn't have**:
- K3-K5 word problems for `multi_person_sharing` family
- K7-K10 `compound_growth` problems beyond the single per-grade
- K9-K12 `area_perimeter_chain` (currently missing entirely)
- Statistics K7+ (variance, std deviation) — non-existent
- Pre-algebra → algebra bridge (K6→K7) — thin

### Proposed topic taxonomy fixups

The current corpus uses a mix of topic names: `arithmetic.fractions`, `fractions.multiplication`, `algebra.expressions`, etc. There's drift between the manifest topics and the spec's MATH_TOPICS list. Recommended:
- **No taxonomy renames in this phase** — too risky, would invalidate every template's metadata
- **Document the canonical topic list** in [src/constants.py](src/constants.py) (already present at MATH_TOPICS) and add a validation step in `YAMLLoader._validate_structure` that warns if `metadata.topic` doesn't match a known topic-or-subtopic
- **Future cleanup**: a separate pass to harmonize `arithmetic.fractions` (under arithmetic) vs `fractions.*` (top-level)

---

## Stage 4 — Seed templates per (grade, topic, family) triplet

Goal: from the post-deletion survivors, identify the ~50-70 *anchor* templates that define what "high quality" looks like for this corpus, and seed any critical missing triplets with new hand-crafted templates.

### What "high quality" means here (criteria)

A seed template should:
1. Generate a coherent, grammatically correct word problem regardless of seed
2. Use realistic values (no $7.33 prices, no 47 minutes for a school day)
3. Have a multi-step solution that exercises stated `family` (e.g., `sequential_purchase` actually has multiple sequential purchases)
4. Include 3+ test cases with seeds covering edge cases (boundary values, plural/singular, etc.)
5. Have non-trivial difficulty matching the grade (no K9 doing K3 addition)
6. Use Faker / providers correctly (no hardcoded names, locations)
7. Solution code is readable, has no magic numbers, uses the helpers in [src/utils.py](src/utils.py)

### Recommended anchors (one per high-priority triplet)

For triplets that survive Stage 1 with ≥2 templates, **promote one to "anchor" status** (rename to `*_anchor.yaml` or add a `metadata.is_anchor: true` field, TBD). The anchor is the canonical pattern; future additions in that triplet should follow its style.

Selection rule: pick the variant the agent recommended `KEEP` first; if multiple OK, prefer the one with richest natural-language context (real-world scenario over bare-formula).

Examples (from agent reports, ~30 anchors total — full list to be enumerated post-deletion):
- `arithmetic/k1_easy_addition_01.yaml` → anchor for (K1, arithmetic.addition, addition)
- `arithmetic/k5_medium_shopping_01.yaml` → anchor for (K5, arithmetic, shopping)
- `geometry/k5_easy_rectangle_area_01.yaml` → anchor for (K5, geometry.area, rectangle_area)
- `statistics/k5_medium_statistics_mean_01.yaml` → anchor (sports context, richest of the K5 mean group)
- `ratios/k4_easy_sharing_01.yaml` → anchor for (K4, ratios.division, sharing) — only one passing tests
- `algebra/k5_easy_expressions_intro_01.yaml` → anchor for (K5, algebra.expressions, expressions_intro:addition)

### New seed templates to add (priority list)

**P0 — fill spec-mandated families that are bare**:
| New template | Rationale |
|---|---|
| `area_perimeter_chain/k5_medium_garden_chain_01.yaml` | K5 garden: area → side length → perimeter (matches spec example exactly) |
| `area_perimeter_chain/k7_hard_room_chain_01.yaml` | K7 multi-step chain with floor/wall area + paint cost |
| `multi_person_sharing/k5_medium_bill_split_01.yaml` | Bridge K4 sharing → K6 sharing |
| `compound_growth/k7_easy_savings_01.yaml` | Simple 3-year compound interest |

**P1 — extend K7-K12 (currently 14 files total)**:
- One template per (K7-K9) × {arithmetic.multi_step, percentages.growth, ratios.sharing, geometry.area_composite, algebra.equations}
- That's ~15 new templates, addressing the largest coverage gap

**P2 — fill statistics post-stats-deletion**:
- (K4, statistics, mean) — basic mean of 3 numbers, age-appropriate
- (K7, statistics, variance) — introduce variance with small dataset
- (K8, statistics, stddev) — extend to standard deviation

**P3 — replace deleted (K6, percentages.comparison) with one quality template**:
- (K6, percentages.comparison, percentage) — comparing percentages of different totals (e.g., "60% of 50 vs 40% of 80, which is bigger?")

### Anchor-and-seed workflow

For each new template (P0-P3, ~22 total):
1. Draft the YAML (variables, template text, solution, ≥3 test cases)
2. Run `mathbot verify <path>` and `mathbot test <path>` — must pass before commit
3. Run `mathbot generate --input <path>` with 5 different seeds — manually read each, confirm coherent
4. Add to a **seed manifest** `src/templates/SEEDS.md` listing all anchor templates by triplet, so future contributors know the pattern

### Recommended Stage 4 actions

1. Build the anchor list (one per surviving triplet with ≥2 templates) — script-generatable from `/tmp/mathbot_manifest.json` after deletions land
2. Write the 4 P0 templates (spec-mandated families)
3. Write 15 P1 templates (K7-K12 fill)
4. Write 4 P2-P3 templates (stats + percentages.comparison)
5. Add `src/templates/SEEDS.md` documenting anchors
6. Add a `mathbot lint` CLI subcommand that flags non-anchor templates in a triplet whose math-step-count or variable-set diverges from the anchor (to keep future additions consistent)

---

## .venv fix (from Phase 5 carryover)

Current state: `[pyproject.toml](pyproject.toml)` declares `requires-python = ">=3.9"`. Project's `.venv` was built against some older Python; the user's shell `VIRTUAL_ENV` points to Homebrew Python 3.14 — `uv run` warns and ignores it.

### Fix

```bash
# from project root
rm -rf .venv
uv venv --python 3.12              # 3.12 is the highest version with broad lib support
uv sync --all-extras                # rehydrate from uv.lock
uv run pytest                      # confirm all 35 tests pass on the fresh env
```

### Optionally pin Python version

Add to `[pyproject.toml]` for stricter reproducibility:
```toml
[project]
requires-python = ">=3.10,<3.13"   # current code uses Decimal, math.lcm (3.9+), but type union syntax may fail on 3.9
```

Run `uv lock --upgrade` after the bound change to refresh `uv.lock`.

---

## Execution order summary

| Step | Action | Reversible? |
|---|---|---|
| 0 | Re-review fractions slice with strict criteria (sub-agent) | n/a |
| 1 | Show consolidated deletion list to user, spot-check 20 entries | yes |
| 2 | Land `gcd`/`lcm` fix in solution_evaluator (3 lines) | trivial |
| 3 | Execute deletions in one commit (~280-330 files) | `git revert` |
| 4 | Add `ruamel.yaml` dep + write `scripts/refresh_test_answers.py` | yes |
| 5 | Run regenerator on small slice; manually verify 20 outputs | yes |
| 6 | Run regenerator on full corpus, commit | `git revert` |
| 7 | Promote ~30 surviving templates to anchor status | trivial |
| 8 | Write 22 new seed templates (P0/P1/P2/P3) | yes |
| 9 | Add `SEEDS.md` and `mathbot lint` subcommand | yes |
| 10 | Rebuild `.venv` against Python 3.12 | yes |

**End state**: ~580-630 high-quality templates organized by (grade, topic, family) triplet, each triplet anchored by one canonical pattern, all `mathbot test` runs passing, .venv clean.

## Open questions for the user

1. **Strict re-pass on fractions/decimals?** The fractions agent's "no duplicates" claim doesn't survive scrutiny on at least one family I spot-checked. Agree to dispatch one more agent with the strict rule?
2. **K7-K12 expansion scope**: P1 calls for ~15 new templates. Is that sufficient, or do you want broader upper-grade coverage (e.g., 5 per grade × 5 grades = 25)?
3. **Anchor mechanism**: rename to `*_anchor.yaml`, add `metadata.is_anchor: true`, or keep a separate registry in `SEEDS.md`? Recommend `metadata.is_anchor` for machine-readability.
4. **Topic-name harmonization**: punt to a future phase, or fold into Stage 1?
