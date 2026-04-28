# Math domain

The math-specific knowledge for template authoring: GSM8K antipatterns, the structural-tag taxonomy, and how to read a P-XX proposal entry into one or more templates.

The canonical proposal source is `MATHBOT_PROBLEMS_PROPOSAL.md` at the project root. Read the entry you're implementing, end to end, before authoring. This file is the meta-guidance — what to watch for across all entries.

## Hard rejections (the "don't build this" list)

From `MATHBOT_PROBLEMS_PROPOSAL.md` §6 — this section is non-negotiable. A template that violates any of these is rejected at review even if it lints clean.

### Surface-form rejections

1. **No money-change-with-$X-bill anywhere.** "She paid with a $20 bill, find change" is the canonical highest-similarity-to-GSM8K pattern. If the natural framing of your problem ends with a change-making step, reframe it: ask for the total cost, the unit price, the discount applied, anything but change.

2. **No basic-proportion templates** ("if 3 lbs cost $9, how much for 7 lbs"). Ratios already has the highest GSM8K similarity (0.044 mean). New ratio templates should be bar-model invariants (P-SP1) or compound-rate (P-SP3), not basic proportionality.

3. **No single-mover distance = rate × time.** GSM8K saturates this. Replace with multi-rate `rate_time` content (P-SP3): two agents combining, mid-task rate change, relative motion.

4. **No "X items at $Y each, plus tax" without a structural twist.** The top GSM8K template by frequency. Allowed only if the template includes a tier crossing, conditional branch, or chained dependency that meaningfully changes the structure.

### Cell rejections

5. **No new templates at K6 unless filling a structural gap.** K6 is 33% of the corpus. Hard cap: +5 K6 templates across the entire P0-P2 plan. If your task lands you at K6, ask whether it should actually be K7 or K8 — most P0 work belongs at the K7-K10 bridge.

6. **No new `fractions.operations` templates anywhere.** Already the largest single bucket (36 templates). Fractions arithmetic should be incidental to other topics (a percentages problem that uses fractions in computation), not the topic itself.

7. **No new `geometry.shapes` templates at K2 or K6.** Saturated.

8. **No new `arithmetic.*` at K3-K6 unless filling a specific structural gap** (NoOp distractor, working-backwards, constraint-satisfaction). Arithmetic is mature.

### Two cheap pre-commit checks

Before committing a template, run mentally:

1. **Jaccard 5-gram similarity to GSM8K**: would the rendered prose look familiar to someone who's read 100 GSM8K problems? If yes, you need a structural twist regardless of cell coverage.
2. **Structural-tag count**: does the template exercise at least one structural pattern from §"Structural-tag taxonomy" below? If zero, you're authoring a saturation-equivalent template that fills a heatmap cell without adding benchmark value.

## Structural-tag taxonomy

These are reasoning patterns that cut across topics. The proposal §4 lists 12; every new template should exercise at least one. Across a campaign of 8+ templates, aim for ≥3 distinct tags.

| Tag | Description | GSM8K coverage | Canonical families |
| --- | --- | --- | --- |
| `invariant_tracking` | A quantity is conserved across a transformation; recognizing it is the key step | Excluded | P-SP1, P-G3 (water transfer), bar-model |
| `working_backwards` | Final state given; reconstruct initial via chained inverse operations | Largely excluded | P-A2, P-SP1 (fraction-of-remainder), P-A5 (find n) |
| `inverse_problem` | Given f(x), find x | Largely excluded | P-A2, P-G4, P-SP4 (find rate) |
| `conditional_case_split` | Solution depends on which interval a parameter lies in | Excluded | P-A4 (break-even), P-SP2 (tier crossing), P-S2 (Bayes branches) |
| `optimization` | Find max/min subject to constraints | Excluded | P-A3 (vertex), P-S3 (combinatorial max) |
| `constraint_satisfaction` | Find values satisfying multiple simultaneous conditions | Mostly excluded | P-A1 (linear systems), P-N1 (CRT), Diophantine |
| `comparison_decision` | Which option is better, by how much, under what conditions | Sometimes single-shot, never break-even | P-A4, P-SP2, P-SP4 (compare investments) |
| `multi_rate_combination` | Two or more rates combine reciprocally | Almost absent | P-SP3 |
| `mixture_conservation` | Concentration changes via mixing/evaporation/replacement; mass conserved | Almost absent | P-G3, new mixture sub-family |
| `state_tracking_n_stages` | Update through 4+ transactions, each depending on previous | Limited | P-SP2, P-SP4 (annuity), P-SP5 |
| `boundary_off_by_one` | Fence-post errors, train-length passing, equally-spaced stations | Rarely tested | One per spec-mandated family |
| `distractor_robustness` | Problem contains an irrelevant-but-plausible sentence | Mostly absent | 10-15% sample of all new templates |
| `under_specification` | Missing info; correct answer is "cannot determine" or requires assumption | Excluded | 5% explicit "trick" set per family |

When authoring, surface the structural tags in `metadata.tags`:

```yaml
metadata:
  tags: [invariant_tracking, bar_model, multi_person_sharing]
```

This is `tags`, not a dedicated `structural_tags:` field — the proposal describes one but the schema currently uses the generic `tags:` list (SPEC.md §4). When `structural_tags:` lands as a first-class field, the migration will be mechanical.

## Two specific structural-axis recommendations

From the proposal §4, both apply to every campaign:

1. **Add a NoOp distractor variant to ~10% of new templates.** One irrelevant clause per template ("the bus has 40 seats" when bus capacity is irrelevant). Mirzadeh et al. 2024 showed 30-65 pp accuracy drops from this. Cheapest possible robustness intervention; tag with `distractor_robustness`.

2. **Add paired counterfactual instances for ~20% of new templates.** Two instances of the same template differing by one numerical or structural change; correctness on both should correlate. RV-Bench shows pass@1 vs all-of-5 diverges sharply for current models. Implementation: add a sibling template in the same cell with the same shape but a deliberate twist (e.g. flip the constraint direction).

## Reading a P-XX entry into templates

A P-XX entry usually targets multiple cells and mandates several sub-patterns. Mapping to actual templates is a fan-out exercise.

### Example: P-SP1 `multi_person_sharing`

The entry:

- Target cells: K6-K10, plus secondary fill of ratios K7-K10
- Sub-patterns: constant-total / constant-difference / one-party-constant / units-and-parts / repeated-fraction-of-remainder
- Recommended count: 12-18 templates

Fan-out:

| Sub-pattern | Cells | Template count | Anchor or variant? |
| --- | --- | --- | --- |
| constant-total (two-party transfer) | K6 medium, K7 medium, K8 medium | 3 | K6 anchor; K7/K8 either anchors or variants depending on shape preservation |
| constant-difference | K7 medium, K8 hard | 2 | K7 anchor; K8 variant if same shape |
| one-party-constant | K7 medium, K8 medium | 2 | K7 anchor |
| units-and-parts | K8 hard, K9 hard, K10 hard | 3 | K8 anchor |
| repeated-fraction-of-remainder | K7 medium, K8 hard, K9 hard | 3 | K7 anchor; K8/K9 variants/anchors per shape |

That's 13 templates across 5 sub-patterns. The discipline:

- Each sub-pattern gets at least one anchor, even if the anchor is a low-grade variant.
- The K6 cell hosts the simplest sub-pattern (constant-total), bridging from K6 arithmetic into K7+ algebra.
- K10 is the hardest, hosting only the units-and-parts variant (the most algebraically complex).

### Example: P-SP2 `sequential_purchase` with structural twist

The entry mandates: every template includes a tier crossing, conditional branch, or chained dependency. No flat "buy A, buy B, buy C, find total" templates.

Fan-out by twist type:

| Twist | Cells | Anchor focus |
| --- | --- | --- |
| Tier crossing (price changes mid-purchase) | K5 medium, K6 hard, K7 medium | Bulk-discount, volume-pricing |
| Conditional branch (if budget ≥ X then) | K6 medium, K7 hard, K8 medium | Coupon-eligibility, free-shipping |
| Chained dependency (stage k+1 depends on stage k outcome) | K7 hard, K8 hard, K9 medium | Inventory-replenish, savings-target |

9-10 templates total, 3 per twist type.

## When a family doesn't exist yet

Two of the spec-mandated families (`multi_person_sharing`, `rate_time`) didn't exist in `PROBLEM_FAMILIES` as of the proposal writing. When you author the first template for a non-existent family:

1. Add the slug to `PROBLEM_FAMILIES` in `src/constants.py`
2. Run `mathbot list families` to confirm it's registered
3. Author the anchor template
4. The first template in a new family is *always* an anchor (the cell is empty by definition)

Don't author into an undefined family — you'll get a `slug_noncanonical` finding.

## Family-by-family twist requirements

Quick reference of which families need a structural twist and what counts:

| Family | Twist required? | What counts |
| --- | --- | --- |
| `sequential_purchase` | **Yes** | Tier crossing, conditional branch, OR chained dependency. Flat purchases rejected. |
| `compound_growth` | **Yes** | Variable rate per period, conditional event mid-growth, OR inequality-on-n (find the period when X). Constant-positive-rate compounding rejected. |
| `rate_time` | No (the multi-rate combination is itself the twist) | Combined rates, mid-task changes, relative motion, train-length |
| `multi_person_sharing` | No (the invariant requirement is the twist) | Any of the 5 sub-patterns |
| `area_perimeter_chain` | Soft yes | Composite shapes preferred; single-shape area is the saturated form |
| `algebra.*` | No (variable-setup is the twist) | Any problem requiring an explicit equation is GSM8K-novel by design |

For families not listed (numbers, statistics, geometry sub-topics, percentages), apply the structural-tag check: every template needs ≥1 tag from the taxonomy.

## Topic, family, and structural-tag relationships

These three axes are orthogonal:

- **Topic** is the curricular bucket (`algebra.equations`, `geometry.right_triangle`, `statistics.dispersion`).
- **Family** is the structural pattern (`sequential_purchase`, `compound_growth`, `rate_time`).
- **Structural tags** are the reasoning patterns (`invariant_tracking`, `working_backwards`, `conditional_case_split`).

A single template has one topic, one family, and 1-3 structural tags. The corpus is healthy when:

- Every cell `(grade, topic, family, difficulty)` has ≥1 anchor for the most relevant family
- Every family has templates spanning ≥3 grades
- Every structural tag appears in ≥3 distinct families

`mathbot health` reports topic/family coverage. Structural-tag coverage isn't yet first-class (it lives in `tags:` and isn't aggregated); when it becomes first-class, the audit will include it.

## When in doubt about a P-XX entry

Re-read the proposal entry's "Predicted GSM8K overlap" line. If it says "Low," you can author with confidence. If it says "Medium" with a "Twist required," you must add the specified twist. If you're unsure whether your draft satisfies the twist requirement, render it and ask: would a GSM8K-trained model recognize this immediately as a familiar pattern? If yes, the twist isn't strong enough.

The proposal §6 is the highest-leverage page in the doc. Re-read it for every authoring session.
