---
name: template-author
description: Author and iterate on YAML templates in the mathbot corpus — picking the right (grade, topic, family, difficulty) cell, writing the metadata/variables/template/solution/tests blocks, running the lint+verify loop, and resolving findings. Use this skill whenever the work touches `src/templates/`, including implementing a P-XX entry from `MATHBOT_PROBLEMS_PROPOSAL.md`, filling an empty corpus cell, fixing a failing `mathbot lint` or `mathbot test` finding, or adding a new anchor or variant. Use it even when the user is informal ("add a K7 algebra problem", "do P-SP1", "this template is broken") or describes the work without naming templates explicitly. Covers math (populated), physics (stub), and chemistry (stub) domains via `references/domains/<domain>.md` — read the relevant domain file before authoring in that domain.
---

# Template author

This is the procedural playbook for authoring mathbot YAML templates. `src/templates/SPEC.md` is the single source of truth for everything reference-y — schema, fields, sandbox builtins, units, i18n, multi-tier rules, validation, CLI flags. `.claude/CLAUDE.md` (auto-loaded each turn) is now slim orientation + pointers only; don't expect schema or sandbox detail there. This skill encodes the things SPEC.md doesn't: the cell-selection procedure, the iteration loop, the antipattern catalog, and copy-paste recipes for solution patterns.

## Reference layout

Read on demand based on the task:

- `references/yaml_authoring.md` — the things every template author forgets (the `_formatted` companion convention, when filenames drop the difficulty token, the `<auto>` placeholder pattern). Pointer back to specific SPEC.md sections for full schema.
- `references/sandbox_recipes.md` — copy-paste-able solution patterns: pint dimensional arithmetic, sympy quadratic with root rejection, multi-answer pipe-join, conditional-branch logic, working-backwards inverse problems.
- `references/lint_findings_guide.md` — every finding `mathbot lint` emits, with the cause and the fix. Read this when iterating on a failing template.
- `references/domains/math.md` — math antipatterns (GSM8K saturation, the "don't build this" list from `MATHBOT_PROBLEMS_PROPOSAL.md`), structural-tag taxonomy, and how to map a P-XX entry to one or more cells.
- `references/domains/physics.md`, `references/domains/chemistry.md` — currently stubs. When the first physics or chemistry template is authored, populate from the SPEC + the authored exemplar. Until then, they note infra readiness and the load-bearing decisions (units, rendering, sandbox).

## When this skill applies

Trigger on any of:

- "Implement P-A1 at K7", "do P-SP1", "fill the K9 algebra.equations cell", "author N templates for compound_growth"
- "This template fails `mathbot lint`", "fixture drifted on `<id>`", "off_anchor_divergence on this variant"
- Bulk authoring sessions: working through a P0/P1/P2 list from `MATHBOT_PROBLEMS_PROPOSAL.md`
- Physics or chemistry templates (load `references/domains/<domain>.md` first)

Don't use for: schema engine changes (`src/yaml_loader.py`, `src/variable_generator.py`), generator changes, corpus-wide audits beyond a single template's findings, or pool/data file updates (`src/data/pools.<lang>.yaml`). Those are infra concerns; this skill is corpus-content concerns.

## The five-step authoring loop

Each step has a failure mode that justifies its existence. Don't skip steps because the template "looks fine"; the cost of a bad template entering the corpus is propagation — variants get authored against a flawed anchor.

### Step 1: Read the proposal entry fully (not just the title)

If the task references a P-XX entry, open `MATHBOT_PROBLEMS_PROPOSAL.md` and read the *entire* entry — structural skeleton, examples, parameterisation hints, "Predicted GSM8K overlap", and any "Twist required" language. Pull these into a working understanding before touching YAML:

- **Target cells** — the (grade, topic, family) tuple(s) the entry calls out. Some entries target multiple cells; treat each cell as a separate authoring task.
- **Step structure** — the entry specifies a step count range (e.g. 5–7 steps). Your `metadata.steps` should land in that range. `mathbot lint` flags `zero_steps_with_ops` and `very_high_step_count` if you stray.
- **Difficulty tier** — the entry specifies which tiers the family supports. Don't author "hard" if the entry says "medium only".
- **Twist requirement** — for `sequential_purchase`, `compound_growth`, and other GSM8K-saturated families, the proposal mandates a structural twist. **A template missing the required twist is rejected at review even if it lints clean.** See `references/domains/math.md` for the per-family twist catalog.
- **Don't-build list** — `MATHBOT_PROBLEMS_PROPOSAL.md` §6 is the most important page in that doc. Re-read it for every authoring session. The hard rejections (no $X-bill change, no basic proportion, no single-mover D=RT, no "X items at $Y each + tax" without a twist) apply regardless of which P-XX entry you're working from.

If the task doesn't reference a P-XX entry but is a free-form "add a template for X", still ground the work in the proposal's antipattern list and structural-tag taxonomy. A new template with zero structural tags from §4 of the proposal is a smell.

### Step 2: Pick the cell and decide anchor vs. variant

The cell is `(grade, topic, family, difficulty)`. Filename convention: `src/templates/<topic-dir>/k<grade>_<difficulty>_<descriptor>_anchor.yaml` for anchors, same minus `_anchor` for variants. Multi-tier templates drop the `<difficulty>_` token entirely.

Decision procedure:

```bash
# 1. Does the topic directory exist? If not, the topic is new — needs a constants.py update.
ls src/templates/<topic-dir>/ 2>/dev/null || echo "NEW TOPIC — update src/constants.py MATH_TOPICS"

# 2. Does an anchor already exist for this cell?
ls src/templates/<topic-dir>/k<grade>_<difficulty>_*_anchor.yaml 2>/dev/null

# 3. If a multi-tier candidate, anchor file lacks the difficulty token:
ls src/templates/<topic-dir>/k<grade>_*_anchor.yaml 2>/dev/null
```

Then apply the rule from SPEC.md §15:

- **No anchor in the cell** → your template *is* the anchor. Filename ends `_anchor.yaml`.
- **Anchor exists, you're authoring something with the same operation, step count, and variable shape** → variant. Same filename pattern, no `_anchor` suffix. *But:* if it differs only in surface (item type, person name, number range), don't add it. That's the duplication pattern Phase 4 cleared. Either rework into a meaningfully different shape or skip.
- **Anchor exists, your template has a structurally different sub-skill** → consider whether it deserves its own family slug (or even its own anchor in a sub-cell). Better to introduce a new family in `PROBLEM_FAMILIES` than to silently let an off-anchor variant live in a cell with a misleading anchor.

The family is one of `PROBLEM_FAMILIES` from `src/constants.py`. If your work is the first instance of a spec-mandated family that doesn't exist yet (e.g. `multi_person_sharing`, `rate_time`), add it to `PROBLEM_FAMILIES` as part of this same change.

### Step 3: Decide multi-tier vs. separate-templates

This is the decision SPEC.md §7 governs, but the *judgment* call is worth restating:

- **Multi-tier** when easy/medium/hard differ only in **number ranges or choice lists** with the same operation, prompt shape, and solution code. Example: same "add three integers" problem, easy `min:1, max:9`, hard `min:100, max:999`.
- **Separate templates** when tiers probe **different sub-skills**. Example: `algebra.factoring` easy = scalar GCF, medium = variable factor, hard = quadratic. The math you write in `solution:` is genuinely different per tier.

Multi-tier is cheaper to maintain (one solution, one prompt) but only correct for shape-preserving difficulty. When in doubt, do separate — refactoring three templates into one multi-tier later is easier than splitting a forced multi-tier.

Multi-tier filename: `k2_subtraction_01_anchor.yaml` (no `_easy_` token). Single-tier: `k2_easy_subtraction_01_anchor.yaml`.

### Step 4: Write the YAML, with `<auto>` fixtures

Schema details: SPEC.md §3 onward. CLAUDE.md "YAML template schema" has the same in shorter form. Don't re-derive from memory — open SPEC.md when the task involves anything outside the basics (multi-tier `ranges:`, free-form `unit:`, compound physics types, visual blocks).

Authoring discipline:

- **Variables before template before solution.** If you find yourself writing `{{x}}` in the template before deciding what `x` is, stop. The variables block is the contract; the template and solution code consume it.
- **Use `_formatted` companions in problem text, raw form in `{% set %}` math.** `total_formatted` = `"$60.00"`, `total` = `60.0`. Forgetting this gives you `"You have 60 in your wallet"` instead of `"You have $60 in your wallet"`. See `references/yaml_authoring.md`.
- **Solution variables aren't visible in the template.** The solution runs *after* render. To use a derived value in problem text, compute it via `{% set %}` at the top of the template. Five K3 division templates rendered empty whitespace until v0.1.3 fixed this; don't recreate the bug.
- **Jinja list comprehensions don't work in `{% set %}`.** Use an inline `{% for %}` loop instead. See `references/yaml_authoring.md`.
- **Author `<auto>` for `tests[].expected.answer` while drafting.** You'll populate it in step 5 via `scripts/refresh_test_answers.py`. Don't hand-compute fixture answers — the generator's RNG state and formatter together produce the canonical value, and hand-computed values drift.
- **Recommend ≥3 fixtures per template / per tier.** SPEC.md §11. Single-fixture templates are too easy to overfit.

For solution code, see `references/sandbox_recipes.md` for canonical patterns. The sandbox has `sympy`, `scipy.stats`, full `math` primitives surfaced top-level, and the pint backbone (`Q_`, `ureg`, `get_pint_unit`). Don't import per-template; use the sandbox globals.

### Step 5: Verify, render-smoke, populate fixtures, lint, test

This sequence is the validation pipeline. Do it in order — earlier failures invalidate later steps.

```bash
# 5a. Schema validation (fast, no math).
uv run mathbot verify <path>

# 5b. Render-smoke across multiple seeds.
# This is where you MANUALLY VERIFY THE MATH. Generator-correct
# does not mean semantically-correct. Read each output, redo the
# arithmetic on paper, confirm the answer matches.
for s in 12345 42 99 7; do
  echo "=== seed $s ===" && uv run mathbot generate --input <path> -s $s -o text | tail -8
done

# 5c. Populate <auto> fixture answers.
uv run python scripts/refresh_test_answers.py --apply --filter '*/<file>.yaml'

# 5d. Run the embedded tests.
uv run mathbot test <path>

# 5e. Lint with strict mode.
uv run mathbot lint <path> --strict

# 5f. Confirm corpus health hasn't regressed.
uv run mathbot lint --strict
```

The non-obvious step is **5b**. Step-by-step:

1. Pick 4 seeds (the `12345 42 99 7` set is a reasonable default; vary if you want).
2. Render each. Read the problem text out loud — does it parse as English? Does it specify all the quantities the solver needs? Are there ambiguous referents ("the bag" when there are two bags)?
3. Solve the problem yourself, on paper or in your head. Compare to the rendered answer.
4. If the answer matches but the problem reads weirdly, fix the prose — fluency matters for benchmark validity.
5. If the answer doesn't match, the bug is in the solution code or in unstated parameter constraints (e.g. division producing non-integer when the prompt implies integer items).

CLAUDE.md "Authoring a new template" says explicitly: "Manually check the math on each output — generator-correct values aren't the same as semantically-correct problems." Take it seriously.

When `mathbot lint --strict` reports findings, work through them using `references/lint_findings_guide.md`. Common cases:

- `unrendered_jinja` → solution-only variable referenced in template; add `{% set %}` at top
- `off_anchor_divergence` → variant's variable set or step count drifted from the cell's anchor; either align with anchor, refactor anchor, or promote to a new cell
- `gsm8k_money_change` → "$X bill, find change" antipattern; rewrite the problem to remove the change-making frame

## Iteration loop (when things break)

Most failures are surface bugs (typos, missing `_formatted`) caught in step 5a or 5b. Deep failures fall into a few classes:

1. **Math wrong** — the solution computes the wrong value. Re-derive on paper, fix solution, re-run 5c (refresh fixtures), then 5d/5e.
2. **Constraints too loose** — the parameter ranges produce degenerate cases (zero, negative remainder, non-integer where integer is implied). Tighten variable `min`/`max` or add a `step` to enforce alignment. The proposal's "Parameterisation" hints often spell out the constraints needed.
3. **Drift from anchor** — your variant ended up too different. Either pull it back in line (preferred — variants should mirror anchor shape) or accept the divergence finding and document why in `notes:`.
4. **Antipattern flagged** — `gsm8k_money_change`, `gsm8k_with_tax`, `gsm8k_items_at_price_each` are info-level, but concentration within a cell is a smell. If three of your five P0 templates flag, you're under-twisting. Re-read the family's twist requirement.

After every fixing edit, re-run the full pipeline from 5a. Skipping verify after editing the YAML is how schema regressions land.

## Campaign mode (multiple templates from one P-XX)

Most P-XX entries target multiple cells (e.g. P-A1 covers K7, K8, K9, K10 — and explicitly says "12–18 templates" as a target). When working through a campaign:

1. Build the anchor for each (grade, difficulty) cell first. Anchors set the shape; variants follow.
2. Within a cell, author the anchor before any variants. The variant authoring discipline (matching shape, only surface change) needs the anchor as reference.
3. Review the structural-tag distribution across the set. If all 12 P-A1 templates are pure linear-system-solve, you've under-explored the proposal's structural axis. The proposal's structural-tags table lists 12 patterns; aim for ≥3 distinct tags across a campaign of 8+ templates.
4. Run `mathbot lint <topic-dir> --strict` after each cell's worth of templates lands. Catching `off_anchor_divergence` after 12 templates is more painful than after 2.

## Anchor authoring vs. variant authoring

Anchors get more care because variants will be modeled on them. When authoring an anchor:

- Pick the *median* shape for the cell, not an extreme. The anchor is the reference; if it's an unusual sub-pattern, every later variant looks like off-anchor divergence.
- Document any non-obvious choices in `metadata.notes:`. Future you (or the next agent) reads these.
- Ensure the solution code is the cleanest pattern available. Variants will copy the structure.

When authoring a variant:

- Match the anchor's variable set and step count. Surface differences (item type, person name, number ranges) are fine; structural differences require either anchor refactor or new-cell promotion.
- Don't introduce new sandbox patterns the anchor doesn't use. If the anchor solves with arithmetic and the variant uses sympy, that's a smell.

## What this skill doesn't cover

- **Schema engine changes** — adding a new variable type, new pint unit, new locale — touches `src/yaml_loader.py`, `src/variable_generator.py`, `src/units.py`, or `src/i18n/`. Different concern.
- **Pool data updates** — adding new item categories, locales, or context strings touches `src/data/pools.<lang>.yaml`. Different concern, though template authoring may surface the need.
- **Corpus-level analysis** — `mathbot health`, contamination scoring, coverage matrix work. Different concern; consult the project's audit tooling docs.
- **Visual-builder development** — TD-3.1b "Approach B" (Python `TreeSVG`/`BarChartSVG` builders) is roadmap. Until it lands, visuals use Jinja-rendered SVG only (SPEC.md §12).

When a template-authoring task surfaces one of these, flag it for the user and proceed with the template work that doesn't depend on it; don't try to land schema and corpus changes in the same session.
