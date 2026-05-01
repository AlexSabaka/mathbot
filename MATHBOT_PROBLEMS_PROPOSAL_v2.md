# MATHBOT_PROBLEMS_PROPOSAL.md — v2 (April 2026)

*A merge of the January roadmap with the K7–K12 curriculum scope docs, refreshed against the April 2026 corpus state, and extended with a K9+ symbolic-saturation antipattern set.*

---

## 1. Bottom line up front

**The January roadmap was right about K1–K6 and undersized for K9–K12.** Three months of build work landed five of the six spec-mandated families that were missing in January (multi-person sharing, sequential purchase, rate-time, area-perimeter chain, compound growth), reduced cross-template similarity in K6 algebra to a manageable level, and held the GSM8K-contamination floor (mean max-neighbor sim 0.04, p99 0.33, only one pair ≥0.5). **What did not move is the upper-grade gap.** K7–K12 still holds 6.2% of the corpus (39 templates over six grade-bands), K9 has four templates total, K10 has two, K12 has one. The merge with Alex's K7–K12 scope docs surfaces sixteen new structural families the original 22-entry roadmap did not enumerate — most of them in the K10–K12 calculus / linear algebra / ODE / conics / vectors / complex-numbers / sequences territory that the January work treated as out-of-scope.

**The merge changes priorities, not the foundation.** The original P-A1..P-SP5 entries remain valid; eight of them gain new sub-cells from the K-doc cross-walk, three are partially shipped and demote to P1 fill-in work, and four extend cleanly into K9–K11 by adding upper-grade variants rather than new templates. The novel material is concentrated in §5 of this document: **N1–N16, sixteen new family proposals**, of which N9–N16 cover K12 first-year-university content (calculus, linear algebra, vector calc, ODEs).

**The antipattern story is also bifurcated.** The §6 "don't build this" rules from January remain correct for K1–K6 — they target the GSM8K-shaped failure mode of arithmetic-word-problem saturation. K9+ has a different failure mode: symbolic memorization, contest-problem leakage, and formula-substitution shortcuts. Recent eval literature (GSM-Symbolic NoOp drops up to 65 pp; MathArena AIME-2024 contamination inflation of 10–20 pp; Putnam-AXIOM Variation drops of 19.6 pp; MATH-P-Hard drops 10–25 pp; HARP showing MATH saturated at 90%+ but contest tail at 9.6–41.1%; Compositional GSM showing 2–12× compositional reasoning gap) supports a parallel set of seven K9+ antipattern rules. These are added in §6, not as replacement of the K1–K6 rules but alongside them.

**One curricular caveat to call out before the body.** A cross-walk of the K-docs against eight reference systems (Singapore H2/H3, Japan Math I/II/III/A/B/C, Finland LOPS MAA1–13, Norway LK20 R1/R2, Sweden Mat 1a/b/c–4–5, Estonia gümnaasium I–VIII, Netherlands HAVO/VWO wiskunde A/B/C/D, US CCSS HSA/HSF/HSG/HSN/HSS) flags that **the K12 doc is internationally aggressive**. Single-year compression of limits→derivatives→integrals→ODEs exceeds the Japan/Finland/Norway/Sweden 2-year norm; eigenvalues, matrix rank, and 2nd-order linear ODEs are first-year-tertiary content in most systems and CCSS-(+) optional or absent. Per Alex's directive, K12 is in scope and we propose families for all of it — but we tag each family with its international position so the coding agent can mark the resulting templates with appropriate `track:` metadata and the eval can be sliced to a CCSS-core view if needed.

---

## 2. Coverage data — what changed since January

The corpus has grown from approximately 540 templates to **633 (356 anchors, 277 variants across 353 cells)**. Distribution by grade:

| Grade | Count | Share | Δ from January roadmap baseline |
|-------|------:|------:|----:|
| K1 | 36 | 5.7% | small +
| K2 | 100 | 15.8% | +
| K3 | 60 | 9.5% | small +
| K4 | 65 | 10.3% | +
| K5 | 110 | 17.4% | +
| K6 | 213 | 33.6% | + (still dominant; cap holds)
| K7 | 13 | 2.1% | + (was ~5)
| K8 | 11 | 1.7% | + (was ~3)
| K9 | 4 | 0.6% | flat
| K10 | 2 | 0.3% | flat
| K11 | 8 | 1.3% | +5
| K12 | 1 | 0.2% | flat |

**K1–K6 holds 92.7%; K7–K12 holds 6.2%.** The skew is materially the same as January despite the build work — K6 absorbed roughly half the recent additions, and the spec-mandated families landed across K3/K5/K6/K7/K8/K10/K11 rather than concentrating in the upper bands where the cell count is smallest. **This was correct triage at the time** (spec families were the highest-value missing structural patterns regardless of where they landed) but it leaves the K9–K12 gap unaddressed. K9 in particular — algebra/sequences/quadratics/polynomial-ops/abs-value/function-transformations/sets/permutations — has four templates total against a curriculum scope of 73 K-doc subsections, none of which has more than zero–one templates today.

**Spec-mandated family progress — what landed.** Tracking against the §3 list from the January proposal:

- `multi_person_sharing` (P-S2 family): 5 templates landed across K3/K5/K6. **Shipped, marginal fill-in only.**
- `sequential_purchase` (P-A1 family): 2 templates at K7. **Partially shipped; K8 and K11 variants still missing.**
- `rate_time` (P-A2 family): 2 templates at K7. **Partially shipped; K9 with-acceleration and K11 parametric-time variants still missing.**
- `area_perimeter_chain` (P-G1 family): 3 templates across K7/K8/K10. **Partially shipped; K9 coordinate-plane variant and K10 with-circle variant still missing.**
- `compound_growth` (P-A5 family): 6 templates across K8/K10/K11. **Largely shipped at the standard tier; K11 logarithmic-inversion variants still sparse, K12 continuous-compounding-with-ODE not yet built.**

**What did not progress.** Twelve of the original 22 P-XX entries have zero templates against their target cells: P-A3 (polynomial / system-of-equations algebra at K8/K9), P-A4 (inequality reasoning at K7/K9), P-G2 (volume composite at K8/K10), P-G3 (similar-figure scaling at K7/K8), P-G4 (coordinate proof at K9/K10), P-N1 (combinatorial counting at K9/K11), P-N2 (probability-with-conditional at K9/K11), P-M1 (unit-conversion-with-rate-chain at K7/K8), P-SP1 (mean/median with adversarial change at K8), P-SP3 (regression interpretation at K11), P-SP4 (sampling distribution at K11), P-SP5 (hypothesis-test reasoning at K11). These are the highest-value targets for the next build cycle because the spec demands them, the K-doc cross-walk confirms them as universal, and the corpus has zero coverage.

**Top-overdensified cells (where to NOT add templates):**

| Cell | Count | Verdict |
|------|------:|---------|
| k6.fractions.operations | 22 | **Saturated. Block.** |
| k2.geometry.shapes | 18 | Saturated. Block unless distinct sub-pattern. |
| k2.arithmetic.addition | 17 | Saturated. Block. |
| k5.algebra.expressions | 16 | Saturated; near-dupe risk. |
| k5.decimals.powers_of_10 | 16 | Saturated. |
| k6.arithmetic.number_theory | 14 | Saturated. |
| k2.arithmetic.subtraction | 14 | Saturated. |
| k4.fractions.operations | 12 | Saturated. |
| k4.geometry.symmetry | 12 | Saturated. |
| k6.ratios.proportions | 12 | Saturated. **No more K6 ratios.** |

**Notable within-cell duplication.** K6 algebra cells (equations, factoring, inequalities, simplify, variables, equivalent_expressions) show several cross-template similarity pairs ≥0.9. This is concentration, not contamination — they don't match GSM8K, they match each other. **The K6 cap from §6 of the January proposal holds: no new K6 templates unless filling a structural gap.**

**Singletons with no spec mandate** (`hypothesis_test`, `induction`, `mean_median_mode`, `probability`, `regression`, `variance`, `vectors`): leave alone. None are in the K-doc P0 set; six of seven appear in P1/P2 entries below where they get developed properly rather than extended ad-hoc.

**Contamination floor.** Mean max-neighbor sim against GSM8K = 0.04, p95 = 0.18, p99 = 0.33, max = 0.57; only 7 pairs ≥0.3 and one ≥0.5. **The corpus is structurally GSM8K-novel** and the perturbation-resistance work below should preserve that as we build into K9+.

---

## 3. Ranked empty-cell table — the brutal gaps

The table below is the prioritized work surface. Cells are tagged with the family that targets them (existing P-XX or new N-XX) and a structural justification.

| Rank | Empty cell | Templates | Owning family | Why this matters |
|---:|---|---:|---|---|
| 1 | k9.algebra.systems | 0 | P-A3-extended | CCSS HSA-REI core; Universal across all 8 ref systems |
| 2 | k9.algebra.quadratics | 0 | N3 (new) | Universal; canonical method-selection target |
| 3 | k9.sequences.arithmetic | 0 | N4 (new) | Σ-notation foundation; CCSS HSF-LE; missing entirely |
| 4 | k9.sequences.geometric | 0 | N4 (new) | Annuity/depreciation prerequisite |
| 5 | k9.functions.transformations | 0 | N1 (new) | HSF-BF.B.3 core; LLM-eval interesting |
| 6 | k9.algebra.polynomial_ops | 0 | N2 (new) | HSA-APR core |
| 7 | k9.algebra.absolute_value | 0 | N5 (new) | HSF-IF.C.7b core; piecewise extension |
| 8 | k9.statistics.combinatorics | 0 | P-N1-extended | HSS-CP core |
| 9 | k10.geometry.conic_sections | 0 | N6 (new) | US/Anglo-flagged but in spec |
| 10 | k10.geometry.circles | 0 | P-G1-extended | HSG-C universal |
| 11 | k10.geometry.coord_geometry | 0 | P-G4-extended | HSG-GPE universal |
| 12 | k10.algebra.logarithms | 0 | N8 (new) | Inversion of P-A5 |
| 13 | k10.numbers.complex | 0 | N7 (new) | HSN-CN core (basic ops) |
| 14 | k10.geometry.vectors_2d | 0 | N10 (new) | HSN-VM (+); universal advanced-track |
| 15 | k11.trigonometry.identities | 0 | N11 (new) | HSF-TF universal advanced |
| 16 | k11.trigonometry.law_sines_cosines | 0 | P-G3-extended | HSG-SRT core |
| 17 | k11.algebra.rational_functions | 0 | N2-extended | HSA-APR.D advanced |
| 18 | k11.statistics.distributions | 0 | P-SP4 | HSS-IC; spec-mandated, no movement |
| 19 | k11.statistics.hypothesis_test | 1 | P-SP5 | Spec-mandated; one template = no coverage |
| 20 | k11.statistics.regression | 1 | P-SP3 | Spec-mandated; one template = no coverage |
| 21 | k11.functions.inverse | 0 | N1-extended | HSF-BF.B.4 |
| 22 | k11.algebra.piecewise | 0 | N5-extended | HSF-IF.C.7b |
| 23 | k12.linear_algebra.matrices | 0 | N9 (new) | HSN-VM(+); CCSS-optional |
| 24 | k12.linear_algebra.eigenvalues | 0 | N9-extended | Beyond CCSS; tertiary-flagged |
| 25 | k12.calculus.limits | 0 | N12 (new) | Universal advanced-track |
| 26 | k12.calculus.derivatives | 0 | N13 (new) | Universal advanced-track |
| 27 | k12.calculus.optimization | 0 | N13-extended | Saturated in MATH; needs novelty |
| 28 | k12.calculus.related_rates | 0 | N13-extended | Saturated in MATH; needs novelty |
| 29 | k12.calculus.integrals | 0 | N14 (new) | Universal advanced-track |
| 30 | k12.calculus.applications | 0 | N14-extended | Work, surplus, FTC |
| 31 | k12.differential_equations.first_order | 0 | N15 (new) | Universal advanced-track |
| 32 | k12.differential_equations.second_order | 0 | N16 (new) | Tertiary-flagged |
| 33 | k12.linear_algebra.vectors_3d | 0 | N10-extended | Cross product, planes |

**Reading the table.** K9 is the most brutal gap by template-per-spec-cell ratio: nine empty cells in the top 10. K12 has the highest absolute number of empty cells (eight in the table; many more in the K-doc decomposition), but several of those are tertiary-flavored and will need narrower template counts. K10 is mid-priority: two templates today, four to seven empty cells worth filling, but the conic sections and complex numbers entries should be capped because they are over-represented in the K-docs relative to international norms.

---

## 4. Merge analysis — the original 22 P-XX entries cross-walked against the K-docs

For each January entry, this section reports: (a) which K-doc topics it now covers / partly covers, (b) which K-doc topics surfaced gaps the original missed, (c) priority change.

**P-A1 (sequential purchase / running total with twist).** Covers K7 §ratios, §percentages-with-discount, K8 §unitary-method, K8 §mixed-word-problems. K-doc surfaces a new sub-pattern not in the original: multi-store comparison with currency conversion, which appears in K7 §ratios. **Status: 2 templates shipped at K7; needs 3 more (K7 multi-store, K8 unitary-method-with-tax, K11 financial-decision-with-discount-stack). Priority unchanged at P0.**

**P-A2 (single-leg D=RT with structural twist).** Covers K7 §rates, K8 §proportions, K9 §slope-as-rate. K-doc surfaces a missing K9 variant: motion-graph-interpretation-then-compute, which is not in the original. **Status: 2 templates shipped at K7; K8 average-speed-with-stoppage and K9 motion-graph variants still empty. Priority unchanged at P0.**

**P-A3 (polynomial / two-equation system).** Covers K8 §equations, K9 §polynomials, K9 §systems-of-equations, K11 §polynomial-equations. K-doc surfaces three missing sub-patterns: K9 polynomial-arithmetic-from-area-model, K9 factoring-by-grouping in a context, K11 rational-function-zeros-and-asymptotes. **Status: zero templates at K8/K9. Priority RAISED to P0 (was P1).** The K-doc K9 polynomial section is large (six subsections) and entirely uncovered.

**P-A4 (inequality reasoning).** Covers K7 §inequalities, K9 §inequalities, K9 §absolute-value-inequalities, K11 §systems-of-inequalities. K-doc surfaces K9 absolute-value-inequalities as a distinct sub-pattern (now N5). **Status: zero templates. Priority unchanged at P1.** K7 simple-inequality is shippable in P0; K9 absolute-value subsumes into N5.

**P-A5 (compound growth — multi-period, non-trivial base).** Covers K8 §percentages, K10 §sequences-and-series, K11 §exponentials, K11 §logs. K-doc surfaces K11 logarithmic-inversion (solving for time given target value) and K12 continuous-compounding-as-ODE — both deserve own entries, now N8 and N15 respectively. **Status: 6 templates shipped at K8/K10/K11. Priority DEMOTED to P1 for the standard tier; logarithmic-inversion variants split out to N8 at P0.**

**P-G1 (composite area / perimeter chain).** Covers K7 §area, K8 §area-perimeter, K10 §surface-area, K10 §circles. K-doc surfaces K10 circle-area-with-inscribed-polygon as an unbuilt sub-pattern. **Status: 3 templates shipped; K9 coordinate-plane-area variant and K10 circle-with-inscribed-polygon empty. Priority DEMOTED to P1.**

**P-G2 (volume composite, including frustum / hemisphere).** Covers K8 §volume, K10 §surface-area-and-volume, K12 §integral-applications-volume-of-revolution. K-doc surfaces K10 cone-frustum, K10 hemisphere-with-cylinder, and K12 volume-of-revolution-with-method-selection. **Status: zero templates at K8/K10; K12 volume-of-revolution subsumes into N14. Priority unchanged at P1.**

**P-G3 (similar figures / scaling / law of sines-cosines).** Covers K7 §ratios, K8 §proportions, K10 §triangles, K11 §law-of-sines-cosines. K-doc surfaces K11 ambiguous-case-of-law-of-sines as a distinct sub-pattern requiring case analysis. **Status: zero templates. Priority unchanged at P1.** Adding ambiguous case is benchmark-valuable because it requires a case discrimination step that pure formula-substitution fails on.

**P-G4 (coordinate-geometry proof / property verification).** Covers K9 §coord-plane, K10 §coord-geometry, K11 §conic-sections. K-doc surfaces K11 conic-from-coordinates as a coordinate-proof sub-pattern. **Status: zero templates. Priority unchanged at P1.** Note: avoid two-column proof format per cross-curriculum verification — paragraph-form deductive justification is internationally standard, two-column is US-idiosyncratic.

**P-S1 (multi-step shopping / change-making with twist).** Covers K7 §percentages, K8 §percentages-with-tax-tip-discount-stacked. K-doc surfaces K8 tax-tip-discount-order-of-application as a distinct sub-pattern (matters because the order changes the answer). **Status: 1 template at K7. Priority DEMOTED to P2.**

**P-S2 (multi-person fair-sharing / division-with-remainder-context).** Covers K3/K5/K6 §division, K7 §rational-numbers. **Status: 5 templates shipped. Priority CLOSED — no further work needed.**

**P-S3 (multi-stage cooking / recipe scaling).** Covers K5 §fractions, K6 §ratios, K7 §unit-rates. **Status: was P2; remains P2.**

**P-S4 (work-rate combined / multi-worker).** Covers K6 §ratios, K7 §rates, K8 §systems, K11 §rational-equations. K-doc surfaces K11 work-rate-as-rational-equation as a clean sub-pattern. **Status: zero templates. Priority unchanged at P1.**

**P-S5 (mixture / weighted average / alloy).** Covers K7 §percentages, K8 §systems, K11 §matrix-form-of-systems. **Status: zero templates. Priority unchanged at P1.**

**P-N1 (counting / combinatorial reasoning).** Covers K9 §permutations-combinations, K11 §probability. K-doc surfaces K11 conditional-and-Bayesian-counting as a distinct sub-pattern beyond the original scope. **Status: zero templates. Priority RAISED to P0 (was P1)** — high LLM-eval discriminative value per Omni-MATH finding that "discrete mathematics" is the worst-performing subdomain.

**P-N2 (probability with conditional / dependence).** Covers K9 §probability-basics, K11 §conditional-probability. **Status: 1 K8 template (singleton). Priority unchanged at P1.**

**P-M1 (unit conversion + rate chain + dimensional analysis).** Covers K7 §rates, K8 §scientific-notation, K8 §unitary-method, K11 §dimensional-analysis-in-physics-applied. **Status: zero templates. Priority unchanged at P1.** Rich LLM-eval target because dimension-tracking is a known weak point.

**P-SP1 (descriptive stats with adversarial change — outliers, missing data).** Covers K8 §statistics-introduction, K9 §statistics, K11 §descriptive-stats. **Status: zero templates. Priority unchanged at P1.**

**P-SP2 (data display interpretation — multi-chart cross-reference).** Covers K7 §data-displays, K9 §statistics. **Status: zero templates. Priority unchanged at P2.**

**P-SP3 (regression interpretation — slope/intercept-in-context, residuals).** Covers K11 §inferential-stats, K11 §correlation-and-regression. **Status: 1 template at K11 (singleton). Priority unchanged at P1.**

**P-SP4 (sampling distribution / CLT-applied / confidence interval).** Covers K11 §inferential-stats. K-doc places CI at K11; cross-curriculum verification flags this as **timing-aggressive** (most international systems place CI at grade 12). **Status: zero templates. Priority unchanged at P1.**

**P-SP5 (hypothesis-test reasoning — type I/II error in context).** Covers K11 §inferential-stats. **Status: 1 template at K11 (singleton). Priority unchanged at P1.** Same timing caveat as P-SP4.

**Summary of merge-induced re-prioritization.** P-S2 closes (shipped). P-A3 and P-N1 are raised to P0 because of the K9 gap and the eval discriminative value. P-A5 standard-tier and P-G1 demote to P1 because they are largely shipped at the standard difficulty. P-S1 demotes to P2. The remaining entries hold their January priorities. **Twelve of 22 still have zero templates against target cells; those plus N1–N16 are the build queue.**

---

## 5. New family proposals (N1–N16)

Each entry follows the same structure as the original P-XX entries: target cells, structural skeleton, source curriculum, step structure, difficulty tier, examples, parameterisation hints, why it matters for AI benchmarking, GSM8K / symbolic-overlap prediction.

### N1. Function transformations and inverse functions

**Target cells:** k8.functions.intro, k9.functions.transformations, k11.functions.inverse, k11.functions.composition.

**Structural skeleton.** A real-world function f is given as a verbal description, table, or algebraic form, embedded in a context (e.g., temperature conversion, currency exchange, dosage scaling, fuel-economy mapping). The student must (a) identify or construct f, (b) apply a transformation — vertical/horizontal shift, stretch, reflection — that corresponds to a real-world change (taxes, calibration offset, unit change, time delay), (c) compute the transformed function's value at a stated input, (d) optionally invert and compute the pre-image of a target output. The trick is that the transformation is described in domain terms, not algebraic terms.

**Source curriculum.** CCSS HSF-BF.B.3 (transformations), HSF-BF.B.4 (inverse). Universal across the 8 reference systems at K9–K11 (Japan Math II, Singapore O-level §functions, Finland MAA4, Norway 1T/R1).

**Step structure.** 3–5 steps: identify f from prose; translate the verbal transformation to an algebraic operation (the discriminative step); apply; interpret answer in context.

**Difficulty tier.** Easy: single shift. Medium: shift + scale, with one of them domain-side. Hard: composition of f with its inverse plus a linear adjustment, asking for a quantity defined implicitly.

**Example.** "A currency exchange office converts dollars to euros via E(d) = 0.92d − 5 (the −5 is a fixed processing fee). A new branch advertises 'no fee, but our rate is 3% worse.' Write the new function E_new(d). For what dollar amount do the two services yield the same euros?" Answer: E_new(d) = 0.892d; equality at d = 192.31.

**Parameterisation.** Function form (linear, affine, power, exponential), transformation type (shift / scale / reflect), domain-side vs. range-side, single vs. composite, inversion required vs. not. Avoid f(x) = 2x + 3 numerical reskins; vary the *structure* of the transformation across template instances per the Putnam-AXIOM lesson.

**Why it matters.** Function transformations are a known LLM weak spot when stated verbally rather than algebraically — this is precisely the GSM-NoOp / MATH-P-Hard failure mode where the surface form of the problem disguises the standard procedure. CCSS-core; aligns with HSF-BF.B.3 at every reference system.

**GSM8K / symbolic-overlap prediction.** LOW overlap with GSM8K (no shopping-money structure). MEDIUM overlap with MATH §intermediate-algebra subset, mitigated by the verbal-transformation requirement.

### N2. Polynomial operations and factoring in context

**Target cells:** k9.algebra.polynomial_ops, k9.algebra.factoring, k11.algebra.rational_functions.

**Structural skeleton.** A geometric, financial, or physical context yields a polynomial expression naturally (e.g., area of a rectangle with side x and (x+3); volume of a box with cuts; revenue as price × quantity where price depends linearly on quantity). The student must (a) construct the polynomial from the prose, (b) perform an operation — multiply two factors, factor out a common term, factor a quadratic / cubic, perform polynomial long division — and (c) extract a quantity (root, coefficient, value at a specific input). For K11 rational variants, the student divides one polynomial by another and interprets the remainder or asymptote in context.

**Source curriculum.** CCSS HSA-APR. Universal at K9 (Japan §中3 多項式, Singapore Sec 3 factorisation, Finland MAA2, Norway 1T, Sweden Mat 2c, Estonia kursus II).

**Step structure.** Setup polynomial from prose (1 step); choose operation and execute (1–2 steps); extract and interpret result (1 step).

**Difficulty tier.** Easy: factor a quadratic with integer roots from area context. Medium: polynomial long division with remainder interpretation. Hard: rational-function asymptote analysis from a cost-per-unit context, with both vertical and horizontal asymptote required.

**Example (medium).** "A box is built from a 12×8 cardboard sheet by cutting equal squares of side x from corners and folding. Express the volume V(x) as a polynomial. Without expanding, factor V(x) and identify the roots. Which roots are physically meaningful?" Answer: V(x) = x(12−2x)(8−2x); roots 0, 4, 6; only 0 < x < 4 physical.

**Parameterisation.** Box dimensions, polynomial degree (2 / 3 / 4), operation type (multiply / divide / factor), root multiplicity, integer vs. rational coefficients, physical vs. financial wrapping.

**Why it matters.** Polynomial operations are over-represented as pure-symbolic in MATH; embedding them in physical setups with feasibility constraints (root rejection) defends against pure-substitution shortcuts.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM with MATH §algebra; mitigated by feasibility-region requirement.

### N3. Quadratic equations — method selection in context

**Target cells:** k9.algebra.quadratics, k11.algebra.quadratic_functions.

**Structural skeleton.** A context generates a quadratic equation (projectile motion, area, profit-maximizing price, geometry-with-Pythagoras). The student must select a method — factoring, completing the square, quadratic formula, graphical inspection — and justify it before solving. Critically, the parameterisation must vary across template instances such that *different* methods are best for different parameter draws (a discriminant that's a perfect square favours factoring; one that isn't favours the formula; a vertex query favours completing the square). This is the MATH-P-Hard mitigation: parameter changes change the method, not just the numbers.

**Source curriculum.** Universal at K9. CCSS HSA-REI.B.4.

**Step structure.** Set up quadratic from context (1–2 steps); identify which method is most efficient (1 step — the discriminative step); execute (1–2 steps); interpret in context including domain restriction and unit assignment (1 step).

**Difficulty tier.** Easy: factorable quadratic from area. Medium: completing-the-square for vertex-form interpretation (max profit, max height of projectile). Hard: discriminant analysis to determine number of real solutions in a feasibility context (e.g., does the projectile reach height h at all?).

**Example.** "A rectangular garden has a perimeter of 40 m and an area of 91 m². Find its dimensions." Answer: x + y = 20, xy = 91 → x²−20x+91 = 0 → x = 7 or 13; dimensions 7×13.

**Parameterisation.** Discriminant sign and squareness, context (projectile / area / profit / Pythagoras), single-solution vs. two-feasible vs. one-feasible-one-rejected, vertex-form vs. root-form interpretation. The randomization MUST sometimes select parameter draws where factoring is intractable, forcing the formula.

**Why it matters.** Method selection (rather than method application) is precisely what UGMathBench, MATH-P-Hard, and Putnam-AXIOM identify as the genuine reasoning signal. Parameter ranges that change which method applies are the central design lesson from this literature.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. HIGH with MATH §algebra unless method-varying parameterisation is enforced. The mitigation is explicit and structural.

### N4. Sequences and series — arithmetic, geometric, recursive

**Target cells:** k9.sequences.arithmetic, k9.sequences.geometric, k11.sequences_series, k12.sequences_series.

**Structural skeleton.** A real-world iterative process generates a sequence: repeated savings deposit (arithmetic), depreciating value or compound dose (geometric), Fibonacci-like recursion (rabbit population, tile-laying patterns). The student must (a) identify the type from the prose, (b) write the closed form or recurrence, (c) compute either a specific term or a partial sum (Σ-notation), and (d) for K11+, decide convergence in the case of an infinite series.

**Source curriculum.** Universal at K9 (CCSS HSF-LE, HSF-BF), with Σ-notation and convergence at K11 (CCSS HSA-SSE.B.4 — limited; Singapore H2, Japan Math B, Finland MAA9, Norway R1). **Cross-curriculum note:** induction proofs of summation formulas are universal at the K11 advanced track in Norway R2, Finland MAA11, Singapore H2, Estonia, but absent from CCSS — include induction-light variants only as a P2 sub-tier.

**Step structure.** Type identification (1 step — discriminative); closed form or recurrence (1 step); compute term or sum (1–2 steps); convergence check for infinite case (1 step).

**Difficulty tier.** Easy: arithmetic sequence sum (savings). Medium: geometric depreciation with target-year inversion (when does asset value drop below threshold?). Hard: convergent geometric in physics context (bouncing ball total distance with rebound ratio) with answer requiring the closed form S = a/(1−r); harder still: recursive sequence requiring 4–6 iterations before pattern stabilises.

**Example (medium).** "A car loses 18% of its value each year. Initial value \$28,500. After how many full years does its value first drop below \$10,000?" Answer: 0.82ⁿ < 10000/28500 ≈ 0.351; n > log(0.351)/log(0.82) ≈ 5.27; **n = 6 full years**.

**Parameterisation.** Sequence type, first term, common difference / ratio, query type (n-th term / partial sum / convergence / inversion), context.

**Why it matters.** Sequences are foundation for compound-growth, calculus limits, and series-as-approximation. Currently zero templates against four target cells. The recursive variant tests genuine multi-step reasoning per the Compositional GSM finding.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM with MATH §intermediate-algebra. The bouncing-ball geometric is heavily saturated in textbook corpora — vary the geometry (Koch-snowflake-like, three-vehicle pursuit) for novelty.

### N5. Absolute value equations and piecewise functions

**Target cells:** k9.algebra.absolute_value, k11.functions.piecewise.

**Structural skeleton.** A real-world quantity is defined with a tolerance, threshold, or regime change: |measured − target| ≤ ε for tolerance; piecewise pricing (different per-unit cost above a threshold); piecewise tax brackets; absolute-value distance on a number line. The student must (a) translate the prose to an absolute-value or piecewise expression, (b) solve an equation or inequality involving it, requiring case analysis, (c) interpret the solution as a feasible region or threshold.

**Source curriculum.** CCSS HSF-IF.C.7b (piecewise), HSA-REI.D.11 (abs-value). **Cross-curriculum caveat:** piecewise and absolute-value emphasis is US-overweight relative to Finland, Sweden, Norway. Include in benchmark but tag templates with `track:US-emphasized` so non-US slices can deprioritize.

**Step structure.** Translate prose to symbolic form (1 step); split into cases (1 step — discriminative); solve each case (1–2 steps); union or intersect feasibility regions and interpret (1 step).

**Difficulty tier.** Easy: |x − 5| < 2 from prose tolerance. Medium: piecewise tax with two-bracket calculation backwards (given total tax, find income). Hard: nested absolute value in inequality, e.g., ||x−3|−2| < 1, with feasibility interpretation.

**Example.** "A 3D-printer's nozzle temperature should be 215°C ± 4°C. The thermometer reads T. For what range of T is the printer in spec? If the thermometer has a calibration offset of −2°C (reads 2 below true), what reading-range is acceptable?" Answer: 211 ≤ T ≤ 219; with offset, reading 209 ≤ R ≤ 217.

**Parameterisation.** Tolerance value, target, calibration-offset presence, single vs. nested abs-value, piecewise breakpoints (1 vs. 2 vs. 3), forward vs. inverse query.

**Why it matters.** Case discrimination is a known LLM weak point (GSM-Symbolic on logical case-splits). Tolerance / specification language is industrial-context realistic.

**GSM8K / symbolic-overlap prediction.** LOW. MEDIUM with MATH §algebra; mitigated by the calibration-offset / inverse twists.

### N6. Conic sections — applied (parabola, ellipse, hyperbola)

**Target cells:** k10.geometry.conic_sections, k11.geometry.conic_sections.

**Structural skeleton.** A physical setup yields a conic naturally: parabolic reflector or suspension cable; elliptical orbit, whispering gallery, lithotripsy; hyperbolic LORAN navigation. The student must (a) identify which conic the setup produces, (b) extract the defining parameters from the prose (focal distance, semi-major, eccentricity), (c) write the equation in standard form, (d) compute a query — height at a given horizontal distance, focus location, period via Kepler, ship position from time-difference.

**Source curriculum.** CCSS HSG-GPE.A.2 (parabola, core), HSG-GPE.A.3 (ellipse/hyperbola, "(+)" advanced). **Cross-curriculum verification flagged this as US/Anglo-overweight** — Finland, Sweden, Norway, Estonia treat the parabola algebraically and largely skip ellipse/hyperbola. Cap at 4–6 templates total; tag as `track:US-Singapore-Japan`. **Critical content note:** for suspension-bridge problems, distinguish parabola (uniform horizontal load on deck) from catenary (free-hanging cable) — getting this wrong is itself a known LLM error.

**Step structure.** Identify conic from prose (1 step — discriminative); extract parameters (1–2 steps); write equation (1 step); compute query (1–2 steps).

**Difficulty tier.** Easy: parabolic dish focal-length given diameter and depth. Medium: elliptical orbit period from perihelion/aphelion. Hard: LORAN three-station fix from time-differences requiring intersection of two hyperbolas.

**Example.** "A whispering gallery is elliptical, 24 m long and 16 m wide. Two people stand at the foci. How far is each from the centre? If sound travels at 343 m/s, how long does it take a whisper to travel from one focus to the other via reflection?" Answer: a = 12, b = 8, c = √(144−64) ≈ 8.94 m; reflection-path length 2a = 24 m; time ≈ 0.070 s.

**Parameterisation.** Conic type, parameters (extracted from physical context), query type (parameter / point on curve / focal property / period / location). Vary the *physical context* across instances — bridge, dish, orbit, gallery, navigation — not just the numbers.

**Why it matters.** Conic-from-physical-setup tests the modelling step that pure-symbolic conic problems do not. The parabola-vs-catenary distinction in particular is a clean discriminator.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM-HIGH with MATH on satellite-dish and whispering-gallery (saturated). LOW on LORAN, lithotripsy, parabola-vs-catenary disambiguation.

### N7. Complex numbers — operations, polar form, applications

**Target cells:** k10.numbers.complex, k11.numbers.complex.

**Structural skeleton.** Three application contexts dominate: (a) AC-circuit phasor arithmetic with impedance, (b) polar-form rotation as 2D transformation (robotic arm, navigation), (c) De Moivre roots-of-unity applied to phased-array antennas, gear-tooth spacing, or DFT-bin frequencies. The student converts between rectangular and polar, performs an operation, and interprets the result physically.

**Source curriculum.** CCSS HSN-CN.A.1–2 core; HSN-CN.A.3, B.4–6 are "(+)" advanced. Universal at advanced track (Singapore H2, Japan Math II/C, Finland MAA7, Norway R2, Sweden Mat 4, NL wiskunde B).

**Step structure.** Identify representation needed (1 step); convert form (1 step); perform op (1 step); convert back and interpret in physical units (1 step).

**Difficulty tier.** Easy: rectangular ↔ polar conversion with magnitude/phase interpretation. Medium: AC-impedance series-RL with phasor current calculation. Hard: cube roots of unity applied to a 6-tooth gear with one tooth replaced by a smaller-spacing one — find new spacings.

**Example.** "A 120 V (rms), 60 Hz source drives a 50 Ω resistor in series with a 0.1 H inductor. Find the impedance, the rms current magnitude, and the phase angle by which current lags voltage." Answer: Z = 50 + j(2π·60·0.1) = 50 + j37.7 ≈ 62.6 ∠ 37.0° Ω; I = 120/62.6 ≈ 1.92 A rms; lag 37.0°.

**Parameterisation.** Rectangular vs. polar input, op type (add / multiply / power / nth root), context (circuit / rotation / roots-of-unity), engineering-j vs. math-i convention. Standardise on math-i for the benchmark to avoid notational confusion as a separate failure mode.

**Why it matters.** AC-impedance setups are not in the MATH benchmark canon (which prefers pure-algebraic complex problems like "|z+1/z| = 1"); they offer real novelty. Rotation-as-multiplication ties to N1 transformations.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. LOW with MATH for AC-impedance; MEDIUM for nth-roots-of-unity.

### N8. Logarithm equations — inversion in context

**Target cells:** k10.algebra.logarithms, k11.functions.logarithmic.

**Structural skeleton.** A logarithmic-scale quantity (pH, dB, Richter, half-life, stellar magnitude, neural-net loss-decay) is given alongside a target value, and the student must invert the relation to find the parameter (concentration, intensity, time, dosage). Variants chain logs with another concept: "police siren is 110 dB at 5 m; using inverse-square intensity falloff, at what distance is 70 dB heard?" — couples log-equation inversion with 1/r² physics.

**Source curriculum.** CCSS HSF-LE.A.4. Universal at K10/K11 advanced track (Japan Math II 対数, Singapore O-level/H1, Finland MAA8 historical, Norway R1, Sweden Mat 3c, NL wiskunde B).

**Step structure.** Recognise log-scale relation (1 step); set up equation (1 step); invert via log-properties (1–2 steps); interpret in physical units, sometimes including a unit-conversion or a coupled physical law (1 step).

**Difficulty tier.** Easy: pH-to-concentration single inversion. Medium: time-to-target via continuous compounding inversion. Hard: dB-distance with inverse-square coupling; or carbon-14 dating with measurement uncertainty propagation.

**Example.** "A radioactive sample contains 27% of its original ¹⁴C. Carbon-14 has a half-life of 5730 years. How old is the sample?" Answer: t = ln(0.27)/(−ln 2 / 5730) ≈ 10 820 years.

**Parameterisation.** Log scale (pH / dB / Richter / decay), forward vs. inverse, single-quantity vs. coupled-with-physics (inverse-square / Beer-Lambert), uncertainty propagation present or absent.

**Why it matters.** This is the canonical inversion-direction extension of P-A5 (compound growth). LLMs are reasonably good at applying log identities forward and weaker at inverting in physical context. The coupled-physics variants are LOW-saturation per the literature scan.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. HIGH with MATH on bare pH/dB calculations; mitigation is the coupled-physics or measurement-uncertainty wrapping.

### N9. Matrix operations and applications

**Target cells:** k12.linear_algebra.matrices, k12.linear_algebra.systems, k12.linear_algebra.eigenvalues.

**Structural skeleton.** Four families of contexts: (a) Ax = b as resource allocation, alloy mixing, or network flow; (b) Leontief input-output for sector economies; (c) Markov-chain transition with stationary-distribution-as-eigenvector; (d) determinant as area/volume scaling, possibly applied to least-squares regression. The student must construct A and b (or P, π₀, etc.) from the prose, perform the operation, and interpret.

**Source curriculum.** CCSS HSN-VM.C "(+)" advanced (matrices) — eigenvalues are NOT in CCSS at all. Universal at the elite advanced track only: Singapore H2 (matrices yes, eigenvalues only in Further Math), Japan Math C (matrices/vectors yes, eigenvalues no), NL wiskunde D (matrices and 2×2 eigen-analysis), Finland (not in MAA1–12, only in optional applied modules). **Tag the eigenvalue variants with `track:tertiary` — they are first-year university material in most international systems.**

**Step structure.** Construct A and b from prose (1–2 steps); identify operation (1 step); execute matrix algebra (1–2 steps); interpret in context including units and meaning of long-run / equilibrium quantity (1 step).

**Difficulty tier.** Easy: 2×2 system as Ax=b for two-product factory. Medium: 2×2 Markov-chain stationary distribution from weather or brand-switching. Hard: 3×3 Leontief with non-trivial sparsity; or 2×2 eigen-analysis of a structural-vibration matrix.

**Example.** "In Sunnyville, if it's sunny today the probability of sun tomorrow is 0.7; if rainy, 0.4. Find the long-run fraction of sunny days." Answer: stationary distribution from P π = π gives π_sunny = 4/7, π_rainy = 3/7; long-run sunny fraction ≈ 57.1%.

**Parameterisation.** Matrix size (2×2 vs. 3×3 vs. 4×4), context (allocation / Leontief / Markov / regression), eigen vs. systems vs. determinant, conditioning (well- vs. ill-conditioned for randomization stability).

**Why it matters.** Linear algebra is currently zero in the corpus. The Markov stationary-distribution-as-eigenvector setup is structurally unlike anything in MATH and reasonably tractable for benchmarking. UGMathBench reports "Abstract Algebra" and "Differential Equations" both <10% — matrix problems specifically discriminate well.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM with MATH §linear-algebra subset (mostly determinant / inverse drills) — mitigation is the applied wrapping.

### N10. Vector operations — 2D and 3D, dot and cross product

**Target cells:** k10.geometry.vectors_2d, k12.linear_algebra.vectors_3d.

**Structural skeleton.** Three sub-patterns: (a) dot product as work, projection, or angle between forces; (b) cross product as torque, area of parallelogram/triangle, or normal-to-plane through three points; (c) lines and planes in 3D from real geometry — intersection of two roads as parametric lines, plane through three GPS points, distance from a drone to a terrain plane.

**Source curriculum.** CCSS HSN-VM all "(+)" advanced; cross product not even explicitly in CCSS. Universal at advanced track in Singapore H2, Japan Math C, Finland MAA4/MAA10, Norway R2, Estonia VIII, NL wiskunde D.

**Step structure.** Set up vectors from prose (1–2 steps); choose operation (1 step); compute (1 step); interpret in physical units, including direction not just magnitude (1 step).

**Difficulty tier.** Easy: 2D dot product as work in physics. Medium: 3D cross product as torque, with both magnitude and direction (right-hand rule). Hard: distance from point to plane via projection, where the plane is constructed from three points first.

**Example.** "A wrench applies a force of 40 N at 20° above the horizontal at a distance of 0.25 m from the bolt axis (along x). Find the torque vector and its magnitude about the bolt." Answer: r = (0.25, 0, 0); F = (0, 40 cos 20°, 40 sin 20°); τ = r × F ≈ (0, −3.42, 9.40) N·m; |τ| ≈ 10.0 N·m about the z-axis (and a y-tilt component).

**Parameterisation.** Dimension (2D vs. 3D), op (dot / cross / projection / equilibrium-of-three-forces / line-plane intersection), context (work / torque / navigation / structural).

**Why it matters.** Direction-with-vector reasoning (not just magnitude) is a discriminative LLM target. Right-hand-rule errors are well documented. Connects N9 (matrices) at K12 via plane-from-three-points → linear-system.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM with MATH §precalculus vectors; mitigated by 3D + applied-physics framing.

### N11. Trigonometric identities — applied, not symbolic-verify

**Target cells:** k11.trigonometry.identities, k11.trigonometry.functions.

**Structural skeleton.** **Critical: avoid pure "verify identity" templates.** Instead, embed identity-application in a physical setup: (a) beat frequency from superposition of two near-frequency tones using sum-to-product; (b) rewriting A cos ωt + B sin ωt as C cos(ωt − φ) for amplitude/phase of a single sinusoid; (c) projectile range R = (v²/g) sin 2θ using double-angle; (d) Snell-law or vector-decomposition requiring sum-of-angles identity. The identity is the *tool*, not the *target*.

**Source curriculum.** CCSS HSF-TF.C. Universal at advanced track (Japan Math II, Singapore H2, Finland MAA7, Sweden Mat 4 explicit "bevis av trigonometriska formler", NL wiskunde B). Note Sweden does emphasise formal proof of identities; for benchmark portability we still keep these as application not proof.

**Step structure.** Recognise the physical situation (1 step); identify which identity reduces it (1 step — discriminative); apply (1 step); extract numerical or interpretive answer (1 step).

**Difficulty tier.** Easy: rewrite a cos + b sin as single cosine, get amplitude. Medium: piano-tuning beat frequency from two pitches, find envelope period. Hard: projectile range with launch from elevated platform, requiring sum-of-angles AND domain analysis to find max range.

**Example.** "A 440 Hz tuning fork is sounded with an out-of-tune piano string vibrating at 443 Hz. Using sum-to-product, find the envelope (beat) frequency heard by a listener." Answer: y = 2A sin(2π · 441.5 t) cos(2π · 1.5 t); beat frequency = |443−440| = 3 Hz; envelope period 1/3 s.

**Parameterisation.** Identity used (sum-to-product, double-angle, sum-of-angles, Pythagorean), context, what's queried, single vs. coupled with another concept.

**Why it matters.** Pure identity-verify problems are saturated in MATH and are exactly the symbolic-memorisation failure mode the K9+ antipattern set targets. Application-in-context is genuinely discriminative.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. LOW–MEDIUM with MATH (most MATH trig is symbolic-verify, which we are explicitly not building).

### N12. Limit evaluation — applied, not symbolic identity

**Target cells:** k12.calculus.limits.

**Structural skeleton.** Three sub-patterns: (a) asymptotic behavior of an applied function — long-run cost-per-unit, terminal velocity, drug steady-state; (b) marginal-quantity-as-Δ→0 limit-definition setup, where the student must construct [f(a+h)−f(a)]/h and take h→0; (c) indeterminate-form L'Hôpital from a physical/economic setup — damped-driven amplitude as ω→ω₀, marginal revenue at supply-demand equilibrium, terminal-velocity limit as drag-coefficient→0.

**Source curriculum.** Universal at advanced track. Japan Math III, Singapore H2, Finland MAA6, Norway R2, Sweden Mat 3c, NL wiskunde B. CCSS does NOT include L'Hôpital — tag those variants as `track:advanced`.

**Step structure.** Identify limit form (1 step); recognise indeterminate form if any (1 step — discriminative); evaluate (1 step); interpret in units (1 step).

**Difficulty tier.** Easy: asymptote of rational cost function. Medium: limit definition of derivative for marginal cost. Hard: L'Hôpital twice with physical context (e.g., (1−cos kt)/t² as k→0).

**Example.** "A factory's average cost per unit at production level q is C(q) = (500 + 3q + 0.01q²)/q dollars. What is the long-run behavior of average cost as q → ∞? Interpret." Answer: lim_{q→∞} C(q) = lim (500/q + 3 + 0.01q) = ∞ — average cost grows linearly; minimum average cost is at finite q, found via dC/dq=0 → q = √50000 ≈ 223.6 → C_min ≈ 7.47 \$/unit.

**Parameterisation.** Function form, limit point (∞ vs. finite vs. 0+), indeterminate form (0/0, ∞/∞, ∞·0), interpretation required.

**Why it matters.** Pure-symbolic L'Hôpital identities are MATH/AIME staples and benchmark-saturated; physical/economic asymptote problems are LOW-saturation per the literature scan.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. HIGH with MATH for symbolic-L'Hôpital; LOW for asymptote-of-applied-function.

### N13. Derivatives — applications (optimization, related rates, MVT, linear approximation)

**Target cells:** k12.calculus.derivatives, k12.calculus.optimization, k12.calculus.related_rates.

**Structural skeleton.** Five sub-patterns: optimization (max/min in real context with closed-form check), related rates (two geometrically linked quantities both depending on t), linear approximation for error propagation, Newton's method for applied transcendental equation, mean-value-theorem embedded in a "must have been speeding" or "average growth achieved at some instant" setup.

**Source curriculum.** Universal at advanced track. Japan Math III, Singapore H2, Norway R2, Sweden Mat 3c–4, Finland MAA7, NL wiskunde B. MVT not in CCSS but is in AP Calc BC; tag MVT variants as `track:advanced`.

**Step structure.** Set up function from prose (1–2 steps); choose technique (1 step — discriminative); execute differentiation and solve f'=0 or apply rate-equation (1–2 steps); verify (sign / endpoint / second-derivative) (1 step); interpret in units (1 step).

**Difficulty tier.** Easy: max area for given fence length. Medium: conical-tank related-rate. Hard: optimization with cost asymmetry (top of can costs 2× sides) plus closed-form interpretation.

**Example.** "A cylindrical can of volume 355 mL is to be made. The top costs \$0.04/cm² and the side costs \$0.02/cm². What dimensions minimize total cost? (Bottom is free.)" Answer: r* = ∛(355·c_side / (π · c_top))^(1/3) ... compute: r* ≈ 3.34 cm, h* ≈ 10.13 cm.

**Parameterisation.** Sub-pattern (optimization / related-rates / linear-approx / Newton / MVT), specific geometry and constraint, parameter axes that change which method applies.

**Why it matters.** Optimization (cans, fencing) and related rates (ladder, cone) are heavily saturated in MATH and AP archives. Mitigation per the literature scan: novel constraint structures (multi-period revenue, dosage with renal clearance), unusual geometries, non-standard cost asymmetries. The MATH-P-Hard finding that 10–25 pp drops occur when the solution method changes under perturbation drives the parameter design.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. **VERY HIGH with MATH/AP** unless mitigation is enforced. This family MUST use the Putnam-AXIOM Variation methodology — every template randomization should sometimes change which technique applies.

### N14. Integration — applications (work, surplus, FTC, average value, improper)

**Target cells:** k12.calculus.integrals, k12.calculus.applications.

**Structural skeleton.** Five sub-patterns: (a) accumulated quantity from a rate (water-flow, traffic, oil-leak); (b) work / pumping / hydrostatic pressure; (c) consumer/producer surplus, present-value-of-income-stream, Gini; (d) average value or center of mass; (e) improper integrals as decay tails or probability.

**Source curriculum.** Universal at advanced track. Japan Math III, Singapore H2, Norway R2, Sweden Mat 3c, Finland MAA7, NL wiskunde B.

**Step structure.** Set up integrand from prose (1–2 steps — the modelling step); choose integration technique (1 step); evaluate (1–2 steps); interpret with units (1 step).

**Difficulty tier.** Easy: accumulated quantity from rate over interval. Medium: pump-water-out-of-cylindrical-tank work integral. Hard: present-value of variable income stream with discount integral, or improper integral evaluation with convergence check.

**Example.** "Water leaks from a tank at rate r(t) = 100 e^{−0.05t} L/hr starting at t=0. Total leakage in the first 10 hours? In the first 100 hours? Does the total ever exceed 2000 L?" Answer: ∫_0^10 = 2000(1−e^{−0.5}) ≈ 786.9 L; ∫_0^100 ≈ 1986.5 L; ∫_0^∞ = 2000 L (asymptotic max).

**Parameterisation.** Sub-pattern, integrand form, interval (finite vs. improper), context.

**Why it matters.** Integration-applications are the Stewart-canon. Saturation risk is HIGH on spring-work, pumping cylindrical tanks, basic CS/PS. Use frustum / hemispherical tanks, present-value coupling, multi-period setups for novelty.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. HIGH with MATH/AP; mitigation via Skeleton C (economic accumulation) and unusual tank geometries.

### N15. First-order ODE word problems

**Target cells:** k12.differential_equations.first_order.

**Structural skeleton.** Five sub-patterns: (a) exponential growth/decay (Newton's-cooling, single-isotope decay, drug elimination, continuous compounding revisited); (b) RC / RL circuit charging or discharging (linear first-order); (c) mixing / tank with inflow and outflow, equal- or unequal-rate; (d) logistic population, possibly with harvest; (e) falling object with linear or quadratic drag.

**Source curriculum.** Universal at advanced track in Singapore H2 explicit, Finland MAA12, Sweden Mat 5, NL wiskunde D, Norway R2 (added in LK20). Not in CCSS core.

**Step structure.** Identify ODE type from prose (1 step — discriminative); separate variables or apply integrating factor (1–2 steps); apply initial / boundary condition (1 step); answer query, possibly inverting for time (1 step); interpret (1 step).

**Difficulty tier.** Easy: Newton's cooling with target-temperature inversion. Medium: single-tank mixing with target-concentration inversion. Hard: logistic with harvest, requiring stability analysis of equilibria; or unequal-rate mixing with overflow-time computation.

**Example.** "A 600-gallon tank initially contains 40 lb of salt dissolved in water. Brine of concentration 0.5 lb/gal flows in at 4 gal/min and the well-stirred mixture flows out at the same rate. Find Q(t) and the equilibrium salt mass." Answer: dQ/dt = 2 − Q/150; Q(t) = 300 − 260 e^{−t/150}; equilibrium 300 lb.

**Parameterisation.** Sub-pattern, parameter values (rate constants, initial values, ambient), query (concentration at time / time to reach target / equilibrium / overflow time), equal vs. unequal mixing rates.

**Why it matters.** ODE word problems are zero in the corpus. The Compositional GSM finding suggests multi-phase ODE setups (heat from hot to ambient, then ambient becomes function of time) are exactly where compositional reasoning fails.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. HIGH with MATH/AP/Boyce-DiPrima for vanilla Newton-cooling and single-tank mixing. Mitigation: time-varying parameters, multi-phase setups, harvest terms.

### N16. Second-order linear ODE — homogeneous and non-homogeneous

**Target cells:** k12.differential_equations.second_order.

**Structural skeleton.** Three sub-patterns: (a) free spring-mass system (homogeneous mx" + bx' + kx = 0) classified into overdamped / critically-damped / underdamped via discriminant; (b) RLC series circuit (same math, different physical letters); (c) driven oscillator with method of undetermined coefficients — forcing function constant / polynomial / exponential / sinusoidal, including resonance case where trial form must be multiplied by t.

**Source curriculum.** **Cross-curriculum verification flagged this as NOT internationally standard at secondary**. Confirmed at secondary only in Sweden Mat 5, Singapore H3 / Further Math, Finland MAA13 (optional), NL wiskunde D (optional). **Tag all N16 templates with `track:tertiary` — first-year-university content in most reference systems and absent from CCSS entirely.**

**Step structure.** Recognise 2nd-order linear form (1 step); compute characteristic equation (1 step); classify discriminant case (1 step — discriminative); construct homogeneous solution (1 step); for non-homogeneous, propose particular-solution trial form and solve coefficients (1–2 steps); apply initial conditions (1 step); interpret (1 step).

**Difficulty tier.** Easy: homogeneous critically damped, find x(t). Medium: non-homogeneous with sinusoidal forcing off-resonance. Hard: resonance case requiring trial-form modification; or RLC step-response with non-trivial initial charge and current.

**Example.** "A mass of 1 kg hangs from a spring with k = 4 N/m and damping b = 4 N·s/m. Released from rest 0.5 m below equilibrium. Classify the motion and find x(t)." Answer: characteristic r² + 4r + 4 = (r+2)² → critically damped; x(t) = (0.5 + t·v_implied) e^{−2t}; with v(0)=0, x(t) = 0.5(1+2t) e^{−2t}.

**Parameterisation.** Mass / damping / stiffness chosen to land in a target damping regime; forcing type; resonance presence; initial conditions; query (closed form / overshoot / settling time).

**Why it matters.** This family is included per Alex's K12-in-scope directive but tagged tertiary. The damping-regime discrimination is exactly the case-selection step that LLMs handle inconsistently. The resonance-needs-tx-trial detail is a frequent symbolic-shortcut failure point.

**GSM8K / symbolic-overlap prediction.** LOW with GSM8K. MEDIUM-HIGH with first-year-university ODE textbook corpora; mitigation via realistic engineering-physics framings (car shock absorber, seismograph, RLC step response with anomalous initial conditions).

---

## 6. Updated structural-tag taxonomy

The original 12 patterns from January are retained. Five K9+-relevant patterns are added below. Coding-agent should treat these tags as orthogonal to grade and cell — a single template can carry multiple structural tags.

**Original 12 (retained, abbreviated):** running_total, multi_person_sharing, sequential_purchase, rate_time, area_perimeter_chain, compound_growth, mixture_alloy, multi_step_purchase, division_with_remainder, fraction_of_a_quantity, percentage_change, unit_conversion_chain.

**T13. symbolic_manipulation_chain.** Multi-step symbolic transformations where each step's output feeds the next; structurally a derivation rather than a substitution. Targets: N2 (polynomial ops), N5 (abs-value cases), N11 (trig identity-application), N13 (derivatives by chain rule), N14 (integration by parts). The Compositional GSM finding (2–12× compositional gap) directly motivates this tag.

**T14. formula_recall_then_apply.** Templates that explicitly require selecting which formula applies before substitution, with parameters that change which formula is correct. Target: N3 (quadratic methods), N6 (conic types), N15 (ODE classification), N16 (damping regimes). The MATH-P-Hard finding (10–25 pp drops when method changes under perturbation) drives this.

**T15. method_selection_under_parameter_variation.** A specialisation of T14 where the parameter randomisation is *required* to sometimes change the optimal method. The Putnam-AXIOM lesson: random numerical reskins do not test reasoning, but random reskins that change which technique is best do. Target: N3 quadratics, N13 derivatives (some optimization problems become trivial under specific parameter draws — exclude those draws or include them with different ranges).

**T16. selective_attention_required.** Templates with embedded irrelevant information ("noop clauses") that must be ignored. The GSM-NoOp 65% drop finding directly motivates this. Target: every K9+ template SHOULD support a noop variant; explicitly tagged for the N1, N3, N5, N13, N15 families where the noop is most natural (e.g., a quadratic word problem that mentions the painter's age, irrelevant to the area computation).

**T17. inverse_direction_query.** Forward computation is "given parameters, find the answer"; inverse direction is "given the answer / target, find the parameter that produces it." Target: N1 (inverse functions), N4 (year-to-target in geometric sequence), N8 (log-equation inversion), N13 (Newton's method as inverse for equation roots), N15 (time-to-target in ODE). The literature on calculus reasoning shows forward problems are far more saturated than inverse ones.

---

## 7. Updated P0 / P1 / P2 priority list

**P0 — build first cycle (~70–90 templates).** The K9 brutal-gap fill plus partially-shipped spec families plus the highest-eval-discriminative new families.

| Family | Target cells | Est. templates |
|---|---|---:|
| P-A1 fill (sequential purchase) | k7/k8/k11 | 6 |
| P-A2 fill (rate-time) | k8/k9 motion-graph | 4 |
| P-A3 (polynomial / systems) | k8/k9 | 8 |
| P-N1 (combinatorial counting) | k9/k11 | 6 |
| N1 (function transformations) | k8/k9/k11 | 7 |
| N2 (polynomial ops) | k9/k11 | 6 |
| N3 (quadratic method-selection) | k9/k11 | 8 |
| N4 (sequences) | k9/k11/k12 | 8 |
| N5 (absolute value / piecewise) | k9/k11 | 5 |
| N8 (log-equation inversion) | k10/k11 | 5 |
| N12 (limits — applied) | k12 | 4 |
| N13 (derivatives applications) | k12 | 8 |
| N15 (first-order ODE) | k12 | 6 |
| N16 (second-order ODE — minimum viable) | k12 | 4 |
| **P0 total** | | **~85** |

After P0, K9 moves from 4 templates to ~38; K12 moves from 1 to ~22. K6 cap holds; no K6 work is in P0.

**P1 — second cycle (~60–80 templates).** Original P-XX entries with structure clearly mapped, plus K10 conics/vectors/complex.

| Family | Target cells | Est. templates |
|---|---|---:|
| P-A4 (inequalities) | k7/k9 | 5 |
| P-A5 fill (compound growth advanced) | k11/k12 | 4 |
| P-G1 fill (composite area, K10 inscribed) | k9/k10 | 4 |
| P-G2 (volume composite) | k8/k10 | 5 |
| P-G3 (similar / law-of-sines incl. ambiguous case) | k7/k8/k11 | 6 |
| P-G4 (coord proof — paragraph-form, not 2-column) | k9/k10/k11 | 5 |
| P-S4 (work-rate combined) | k8/k11 | 4 |
| P-S5 (mixture / matrix-form) | k7/k8/k11 | 4 |
| P-N2 (probability conditional) | k9/k11 | 6 |
| P-M1 (unit conversion + rate chain) | k7/k8/k11 | 6 |
| P-SP1 (descriptive stats with adversarial change) | k8/k9 | 4 |
| P-SP3 (regression interpretation) | k11 | 5 |
| P-SP4 (sampling / CI) | k11 | 5 |
| P-SP5 (hypothesis test) | k11 | 5 |
| N6 (conic sections — applied, capped at 6) | k10/k11 | 6 |
| N7 (complex numbers) | k10/k11 | 6 |
| N9 (matrices — basic + Markov) | k12 | 6 |
| N10 (vectors 2D and 3D) | k10/k12 | 6 |
| N11 (trig identities — applied) | k11 | 5 |
| N14 (integration applications) | k12 | 6 |
| **P1 total** | | **~103** |

**P2 — third cycle (~40–60 templates).** Lower-priority entries; structural-tag broadening; second-order-ODE non-homogeneous variants; eigenvalue applications; advanced SPxx.

- P-S1 (multi-step shopping, K8 advanced) — 3 templates
- P-S3 (multi-stage cooking) — 3 templates
- P-SP2 (data display interpretation) — 4 templates
- N9 fill (eigenvalues, structural-vibration applications) — 5 templates
- N10 fill (3D plane equations from real geometry) — 4 templates
- N16 fill (non-homogeneous second-order driven, including resonance) — 5 templates
- T16 noop variants for highest-coverage families (broadcast across P0/P1) — ~15 templates as variants
- T17 inverse-direction variants for highest-coverage families — ~10 templates

**Cumulative-effect table (refreshed for April 2026 baseline):**

| Phase | Total templates | K7–K12 share | K12 templates | Largest gap closed |
|---|---:|---:|---:|---|
| Current (Apr 2026) | 633 | 6.2% | 1 | (baseline) |
| After P0 | ~720 | 16% | ~22 | K9 algebra+functions+sequences |
| After P0+P1 | ~825 | 26% | ~34 | K10 conics/vectors/complex; K11 stats |
| After full plan | ~885 | 31% | ~50 | K12 calculus / linear algebra core |

**The K6 cap remains. No new K6 templates unless filling a structural gap not addressed by an existing K6 cell.** Specifically, P0 / P1 / P2 add zero K6 templates by design.

---

## 8. Don't build this — refreshed

The original §6 hard rejections from January remain in force for K1–K6. Seven K9+ symbolic-saturation rules are added alongside, motivated by the literature scan in the appendix.

**Original K1–K6 rejections (retained, condensed):**

1. No "$X bill paid for items totaling $Y, find change" without a non-trivial twist (overlapping-discount, multi-currency, context-shift).
2. No basic proportion problems ("if 3 apples cost $2, what do 7 cost") — saturated in GSM8K.
3. No single-mover D = R · T problems without acceleration, multi-leg, or motion-graph component.
4. No "N items at $P each, plus tax/shipping" without a multi-stage discount-stack or comparison.
5. No new K6 templates unless filling a structural gap (K6 cap).

**New K9+ symbolic-saturation rejections:**

6. **No contest-problem-style "find a clever trick" problems unless deliberately tagged for olympiad-overlap evaluation.** Justified by MathArena's finding that AIME-2024 inflation reaches 10–20 pp above the trend line (with QwQ-Preview-32B at "extreme contamination" levels) and HARP showing MATH median saturated at 90%+ but contest tail at 9.6–41.1%. Olympiad-style problems are heavily contaminated and do not test the procedural reasoning we want.

7. **No symbolic identity verifications that just substitute and check.** "Show that sin²θ + cos²θ = 1" or "verify (a+b)(a−b) = a² − b²" are pure-symbolic and dominated by MATH/textbook saturation. N11 takes the alternative path of identity-application-in-context.

8. **No "compute this integral" / "solve this ODE" / "find the eigenvalues of this matrix" templates without a real-world or applied wrapping.** Pure-symbolic computation of standard-form problems is what the MATH benchmark already saturates and what Putnam-AXIOM and UGMathBench show evaporates under variable-swap. Every K12 template must include a modelling step.

9. **No problems that test only formula memorization.** Templates whose entire solution path is "recall formula F, substitute given numbers, report" — including bare "apply the quadratic formula," "compute the determinant," "use the chain rule on this expression" — are prohibited. The MathBench theory-application gap and UGMathBench's Arithmetic-62.8% vs. Abstract-Algebra-<10% subdomain heterogeneity are the direct evidence: formula application is saturated, method selection is not.

10. **No K12 problems that admit a single canned procedure from a textbook section without a parameter that varies the procedural choice.** This is the operational form of the MATH-P-Hard finding (10–25 pp drops when perturbation changes method). Concretely: a related-rates template must have parameter ranges where for some draws the "canonical" approach is not the best, OR the parameter range must change which underlying geometry rule applies.

11. **No multi-step word problems where intermediate sub-problems are independently solvable in a way that lets a model decompose without genuine forward chaining.** The Compositional GSM finding (2–12× reasoning gap, monotonic decline with chain length even for o1-preview) shows that genuinely chained problems where step 2 depends on step 1's numerical answer discriminate strongly. Templates structured as "(a) compute X. (b) compute Y. (c) compute Z." where each is independent are not what we want — we want "use the result from step 1 as an input to step 2's setup."

12. **No K9+ template without irrelevant-clause-injection support.** Per the GSM-NoOp finding (up to 65 pp drop when an irrelevant but plausible clause is added), every K9+ template should support a `+noop` variant where a parameter family allows injecting structurally-plausible-but-logically-irrelevant text. This is not all built immediately but the template schema must permit it.

**One more soft guidance, not a hard rejection:** symbolic answers should be scored via tree-edit distance / sympy-equivalence (the PHYBench EED methodology), not exact string match. Equivalent symbolic forms — `2 sin x cos x` vs. `sin(2x)`, `(a+b)²` vs. `a² + 2ab + b²` — must be treated as correct. This is a benchmark-tooling guideline rather than a template-design rule, but the templates must produce ground-truth answers in a sympy-canonicalisable form.

---

## Appendix A — Cross-curriculum verification summary

The K-docs were verified against eight reference systems. Verdicts at topic level:

**Universal at K7–K8 across all 8 systems:** integer/rational arithmetic, exponent laws, percentages, ratios, linear equations one-variable, Pythagoras, basic coordinate geometry, slope, scientific notation, polygon area/volume, parallel-line angle relationships.

**Universal at K9–K10:** quadratic equations and formula, systems of linear equations, polynomial arithmetic, factoring, integer/rational exponents, basic right-triangle trig, Pythagorean identity, circle geometry, surface area / volume of solids, basic probability, descriptive statistics, arithmetic and geometric sequences.

**Universal at advanced track only (K11–K12):** function families and transformations, trigonometric identities and equations, sequences and series with Σ-notation, single-variable calculus core (limits / derivatives / integrals).

**Track-dependent / advanced-only (tag templates accordingly):** conic sections beyond circle (US/Singapore/Japan-leaning); 3D vectors with cross product (Singapore H2, Japan Math C, Finland MAA10, NL wiskunde D — all advanced track); complex numbers full polar/De-Moivre treatment (Japan Math II, Finland MAA7, Norway R2, Sweden Mat 4 advanced-only); inferential statistics at K11 (timing-aggressive — most international placements at K12).

**Tertiary / first-year-university in most international systems (CCSS-(+) or absent from CCSS):** matrix eigenvalues / eigenvectors / rank, second-order linear ODEs (homogeneous and non-homogeneous), brief PDE intro, MVT and L'Hôpital (in CCSS only via AP Calc BC). Templates targeting these MUST carry `track:tertiary`.

**US-specific in form, not in content:** two-column geometry proofs (deductive geometry universal, two-column form is US-idiosyncratic — N6 / P-G4 use paragraph-form justification); "unitary method" as a named procedure (cosmetic naming only); piecewise-functions and absolute-value-equations as named major topics (US-overweight pedagogically though topic exists everywhere).

**Missing from K-docs but standard internationally (worth flagging for future scope, not in P0/P1/P2):** elementary number theory and modular arithmetic (Japan Math A, Finland MAA11, Norway R1, Estonia, Sweden Mat 5 explicit); proof by induction (Norway R2, Finland MAA11, Singapore H2, Estonia); direct and contrapositive proof writing as named competency; parametric equations; polar coordinates (Japan Math III, Finland MAA10, Singapore H2, NL wiskunde B/D). **Recommend adding these as a future N17–N20 set after P2 if the corpus is to be defensibly internationally portable.**

---

## Appendix B — LLM-eval literature evidence pointers

The K9+ antipattern rules are backed by the following 2024–2026 findings. Each cited at minimum to the level needed to defend a specific rule.

**MathArena** (Balunović et al., arXiv 2505.23281, NeurIPS 2025 D&B; matharena.ai). On AIME 2024 (likely contaminated training data), models score 10–20 pp above the trend line predicted by uncontaminated competitions; QwQ-Preview-32B flagged at "extreme contamination." On IMO 2025 proof problems, top models reach <40%. **Justifies rule #6 (no contest-problem-style without explicit tagging).**

**GSM-Symbolic / GSM-NoOp** (Mirzadeh, Alizadeh, Shahrokhi, Tuzel, Bengio, Farajtabar — Apple, arXiv 2410.05229, Oct 2024; ICLR 2025). Adding a single seemingly-relevant but logically-irrelevant clause caused performance drops up to 65 pp; e.g., Phi-3-mini fell 88.0% → 22.4%. Resampling proper names produces σ ≈ 2–6 pp variance, numerical-value resampling σ ≈ 3–8 pp, mean drops 5–12 pp. **Justifies rule #12 (every K9+ template supports noop injection) and tag T16.**

**MATH-Perturb** (Huang, Yang et al., arXiv 2502.06453, ICML 2025). MATH-P-Simple (numerical-only perturbations preserving solution method) yields small drops; MATH-P-Hard (perturbations changing the problem nature so original method fails) yields 10–25 pp drops across 18 LLMs, including o1-mini −16.49% and gemini-2.0-flash-thinking −12.9%. The paper identifies a failure mode where models "blindly apply learned problem-solving skills." **Justifies rule #10 (no canned-procedure-only templates) and tag T15.**

**Putnam-AXIOM** (Gulati, Miranda, Chen, et al., arXiv 2508.08292, ICML 2025). 522 Putnam problems plus a Variation set generated by programmatic variable/constant perturbation. o1-preview scores 41.9% on originals but drops 19.6 pp (46.8% relative) on paired variations; 18 of 19 evaluated models show the same downward trend with 10 having non-overlapping 95% CIs. **Justifies rule #6 and the parameter-must-vary-method design pattern.**

**Compositional GSM** (Hosseini, Sordoni, Toyama, Courville, Agarwal, arXiv 2410.01748, Oct 2024). Chaining two GSM8K problems so Q1's answer becomes a variable in Q2 yields a "reasoning gap": GPT-4o-mini and similar models show a 2–12× larger gap than the predicted S₁·S₂ baseline. Qwen2.5-MATH-7B-IT (>80% on competition problems) drops to <60% on chained grade-school pairs. **Justifies rule #11 (intermediate values must feed forward).**

**HARP** (Yue, Madaan, Moskovitz, Strouse, Singh, arXiv 2412.08819, Dec 2024). MATH median saturated: o1-mini 90.0%, Gemini 1.5 Pro 86.5%. On HARP's hardest 197-problem bracket from AMC/AIME/USAMO, accuracy collapses to o1-mini 41.1% and Gemini 1.5 Pro 9.6%. **Justifies the framing that MATH is saturated and that contest-tail problems are exactly the leakage-suspect content rule #6 excludes.**

**UGMathBench** (Xu et al., arXiv 2501.13766, Jan 2025). 3-version randomized undergraduate problem set with Effective Accuracy across all 3 versions. Top model: o1-mini at 56.3% EAcc. Subject heterogeneity: Arithmetic 62.8% vs. Abstract Algebra, Differential Equations, Financial Mathematics all <10%. **Justifies rule #9 (no formula-memorization-only) and the special caution on N15 / N16 ODE families.**

**PHYBench** (Qiu et al., arXiv 2504.16074, Apr 2025; NeurIPS 2025 D&B). 500 original physics problems. Best model Gemini 2.5 Pro reaches 36.9% vs. human experts 61.9%. Introduces Expression Edit Distance (EED) Score using sympy + Zhang-Shasha tree edit distance; improves sample efficiency 204% over binary scoring. **Justifies the soft guidance on symbolic-equivalence scoring.**

**Omni-MATH** (Gao et al., arXiv 2410.07985, Oct 2024). 4,428 olympiad-level problems across 33+ sub-domains. o1-mini 60.54%, o1-preview 52.55%; "LLMs show marginally greater aptitude for solving algebra, while struggling significantly with discrete mathematics." Best-of-N test-time scaling reported as ineffective at olympiad level. **Justifies the priority raise on P-N1 (combinatorial counting) per its discriminative power.**

**MathBench** (Liu et al., ACL 2024 Findings, arXiv 2405.12209). Five-stage benchmark separates theory (concept/definition) from application problems and uses Circular Evaluation (shuffled-option re-ask) to detect order-cheating. Empirical evidence that models pass application problems via memorized templates while failing the underlying theory questions in the same stage. **Justifies rule #9.**

**FrontierMath** (Glazer et al., Epoch AI, arXiv 2411.04872, Nov 2024; Tier 4 expansion 2025). On Tier 4 research-level problems, o4-mini achieves 6.3%; Claude Sonnet 4, Grok-3, GPT-4.1 score 0%. On Tiers 1–3, top models reach ~47.6%. **Justifies the framing that the genuine-reasoning frontier is far from solved while contest-style problems are gameable.**

---

*End of MATHBOT_PROBLEMS_PROPOSAL.md v2. Document length: ~720 lines. Replacement for or v2-alongside the January roadmap, at Alex's discretion. Implementation queue is the P0 table in §7; the coding agent should treat each new family entry's structural-skeleton + parameterisation + GSM8K-overlap-prediction as the targeting brief for YAML template authoring.*