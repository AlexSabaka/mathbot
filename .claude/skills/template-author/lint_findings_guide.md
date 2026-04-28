# Lint findings remediation guide

Every finding `mathbot lint` can emit, what triggers it, and how to fix it. SPEC.md §17 lists the findings; this file is the "what do I actually do" companion.

`mathbot lint <path>` runs all rules; `--strict` treats warnings as errors; `--rules a,b,c` runs a subset. The full corpus lints in ~5s, so when iterating, run on the whole `src/templates/` after each individual fix.

## Errors (must fix before shipping)

### `render_crash`

All K render attempts threw an exception (default K=4). Usually means:

- A variable referenced in the template doesn't exist in `variables:` — typo or missed declaration
- The solution code raises an exception (zero-division, type mismatch, undefined variable)
- A Jinja filter is misapplied (e.g. `{{x | ordinal}}` on a non-integer)

Fix: run `uv run mathbot generate --input <path> -s 12345 -o text` to see the actual exception. The traceback points at the line.

### `unrendered_jinja`

The rendered output contains literal `{{...}}` or `{% ... %}` tokens. Causes:

- **Solution-only variable referenced in template.** Solution runs *after* render. If `dividend` is set in `solution:`, you can't write `{{dividend}}` in `template:`. Fix: compute the value in the template via `{% set %}` at the top.
- **Typo in variable name** — `{{prince}}` instead of `{{price}}`. Jinja's default behavior is silent, so it renders empty. Fix the typo.
- **Filter typo** — `{{n | plurla("apple")}}` doesn't match the registered filter; renders as literal. Fix the spelling.

### `empty_answer`

The rendered answer is an empty string. Causes:

- Solution didn't assign `Answer` (or `Answer1`/`Answer2`/...)
- Solution assigned `None`, `""`, or a value that formats to empty
- Multi-answer template using `Answer1`, `Answer2` but the CLI is reading `Answer` (or vice versa)

Fix: print the assigned value at the end of the solution to inspect:

```yaml
solution: |
  Answer = whatever
  print(f"DEBUG: Answer = {Answer!r}", file=__import__('sys').stderr)
```

(Remove the print before committing.)

### `visual_render_crash`

The `visual.source` failed to render — Jinja error or malformed XML. Fix: render the visual standalone:

```bash
uv run mathbot generate --input <path> -s 12345 -o json | jq -r '.visual.source'
```

If the output is broken, the bug is in your SVG. Common causes: unclosed tags, attribute values without quotes, Jinja inside attribute values that produces invalid XML when rendered.

### `fixture_drifted`

The fixture's `expected.answer` doesn't match what the generator produces for that seed. Causes:

- You changed the solution code or variable spec without regenerating fixtures
- You changed generator-engine code (anywhere in `src/`) that affects RNG draws or formatting

Fix: regenerate fixtures.

```bash
uv run python scripts/refresh_test_answers.py --apply --filter '*/<file>.yaml'
```

The script is surgical (preserves comments, quoting, key order). Always use it instead of hand-editing answers.

### `fixture_crashed`

A fixture's seed causes generation to throw. Same diagnosis as `render_crash` but specific to the seed. Fix: render with that seed, see the exception, fix the underlying bug. If the bug is a parameter range that produces a degenerate case at that specific seed, tighten the range or add a `step:` constraint.

### `schema_invalid`

A load-time error surfaced as a finding. The error message identifies the field. Common cases:

- `topic` parent doesn't match the directory (`src/templates/algebra/...` with `topic: arithmetic.X`)
- Variable type not in `VALID_TYPES`
- `item` `category:` not in `VALID_ITEM_CATEGORIES`
- `min > max` on a numeric variable
- No `Answer` variable declared
- Solution has Python syntax error
- `difficulty_tiers` doesn't include the declared `difficulty`

Fix: read the error, fix the field. SPEC.md §17 has the full load-time-error list.

## Warnings (concerning, fix unless you can defend keeping them)

### `off_anchor_divergence`

The variant's variable set or step count differs from the cell's anchor. The Phase 4 cleanup intentionally surfaces these.

Decisions:

1. **Align with anchor** (preferred for true variants). Bring the variant's variable shape and step count back in line. Surface differences (item type, person name, number ranges) are fine; structural differences need to go.
2. **Refactor the anchor** if your variant is exposing a richer shape and the anchor is the simpler outlier. Move anchor → variant, your template → anchor. Update the filename suffixes.
3. **Promote to a new cell** if the variant probes a structurally different sub-skill. Add a new family in `PROBLEM_FAMILIES` if needed.
4. **Document as accepted divergence** by adding `notes:` in metadata explaining why. Use sparingly — accumulating "acceptable divergence" defeats the rule.

The corpus baseline has 236 of these as of v0.3.0 — they're known author-decisions to resolve, not blocking.

### `anchor_filename_mismatch`

Two `_anchor.yaml` files in the same `(grade, topic, family, difficulty)` cell. Each cell allows exactly one anchor.

Fix: pick the canonical one (the cleaner, more representative shape). Rename the other to remove `_anchor`. If the other is actually a different-cell template (different family or sub-skill), move it.

### `body_too_long`

Rendered body > 800 characters. The template is producing prose too long for a benchmark item. Fix: tighten the wording. If the problem genuinely needs that much context (multi-stage, conditional branches), consider whether the structural twist is doing too much; sometimes a 5-step problem that becomes a 9-step problem with extra prose is worse, not better.

### `fixture_missing`

No fixtures, or a multi-tier template missing a fixture for a declared tier. Fix: add fixtures with `<auto>` answers, then run `refresh_test_answers.py --apply`.

```yaml
tests:
  - { seed: 12345, difficulty: easy,   expected: { answer: "<auto>" } }
  - { seed: 12345, difficulty: medium, expected: { answer: "<auto>" } }
  - { seed: 12345, difficulty: hard,   expected: { answer: "<auto>" } }
```

### `slug_noncanonical`

The `family` slug needs renaming. Mathbot has canonical slug forms (lowercase, underscore-separated, matches `PROBLEM_FAMILIES`). Fix: rename to the canonical form.

### `unit_spelled_squared` / `unit_spelled_cubic`

Drift on `m²` / `m³` — the rendered output has "m squared" or "m cubed" as text instead of the proper symbol. Causes:

- Manually templating "m squared" instead of using the area/volume formatted output
- Pint compound unit being printed as words rather than symbols

Fix: use `Answer: { type: area }` (formats as `"X m²"`) or `Answer: { type: volume }` (formats as `"X m³"`). Don't hand-render the unit suffix.

### `zero_steps_with_ops`

`metadata.steps: 0` but the solution performs operations. Fix: set `steps:` to the actual reasoning step count.

### `very_high_step_count`

`metadata.steps:` is unrealistically large (>15ish). Causes: confusing the number of solution-code lines with reasoning steps. The step count is what a *solver* would walk through, not the line count.

Fix: re-count. A 5-step problem usually means: read prose → identify variables → set up equation → solve → state answer.

## Info (heuristic, not blocking)

### `gsm8k_money_change` / `gsm8k_with_tax` / `gsm8k_items_at_price_each`

The rendered text matches a GSM8K-saturated surface pattern. *Not bad in isolation*, but concentration within a cell is a smell.

The patterns:

- `gsm8k_money_change` — the "$X bill, find change" frame. Per `MATHBOT_PROBLEMS_PROPOSAL.md` §6, this is a hard rejection: rewrite the problem so the change-making frame doesn't appear.
- `gsm8k_with_tax` — "plus N% tax" added to a purchase total. OK if the structural twist is elsewhere; reject if the template is "buy items + tax" with no other structure.
- `gsm8k_items_at_price_each` — "X items at $Y each" then sum. The most-saturated GSM8K template; only acceptable with a tier crossing, conditional branch, or chained dependency.

Fix: rewrite the problem to use a different surface form, or add the missing structural twist.

### `area_no_squared_unit` / `volume_no_cubed_unit`

The template's family ends in `_area` or `_volume`, but the answer's unit isn't squared/cubed. Often false positives for perimeter or linear-derived answers in geometry templates that are filed under area/volume topics. If your template legitimately has a linear answer despite the area family slug, document in `notes:` and accept the finding.

If the answer should be area or volume and isn't formatted that way, fix the `Answer:` type:

```yaml
Answer: { type: area }      # formats as "X m²"
Answer: { type: volume }    # formats as "X m³"
```

## Iteration discipline

After every fix:

1. Re-run `mathbot verify` (catches syntax/schema issues fast)
2. Re-run `mathbot generate` with multiple seeds (catches regressions in problem text)
3. Re-run `refresh_test_answers.py` if the solution or any variable spec changed
4. Re-run `mathbot lint --strict` on the file
5. Re-run `mathbot test` to confirm fixtures pass

Skipping verify after editing the YAML is the most common way to land schema regressions. The whole pipeline takes a few seconds.

When fixing `off_anchor_divergence` or `anchor_filename_mismatch` (cell-wide concerns), re-lint the whole topic dir:

```bash
uv run mathbot lint src/templates/<topic-dir> --strict
```

These findings can cascade — fixing one variant might surface a new divergence on a sibling.
