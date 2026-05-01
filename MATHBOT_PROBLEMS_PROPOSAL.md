# Filling the K7–K12 hole: 22 problem families that target real empty cells

## Bottom line up front

**The mathbot corpus has a structural problem, not a contamination problem.** Of 642 templates, 605 sit at K1–K6 and only 37 cover K7–K12 across 34 cells — roughly one template per upper-grade cell. The GSM8K analysis is reassuring (mean max-similarity 0.0079, p99 0.077, only 25 templates above 0.05), so contamination is *not* the bottleneck for new authoring. The bottleneck is **upper-grade coverage and structural diversity**: the corpus replicates GSM8K's forward-arithmetic shape almost everywhere it has mass, and is empty almost everywhere it should differentiate.

This artifact proposes **22 new problem families** specifically targeted at empty (grade, topic) triplets, with explicit emphasis on reasoning patterns GSM8K underweights — Singapore bar-model invariants, Japanese tokushuzan, Dutch RME chains, and work-backwards / constraint-satisfaction structures. Every proposal cites the empty cell it fills, the source curriculum, the predicted GSM8K overlap, and a structural twist where overlap risk is non-trivial. The priority ordering (P0/P1/P2) is grounded in coverage data, not curricular intuition: P0 items either fill spec-mandated family stubs or unlock K7–K10 bridge cells; P1 items extend into K11–K12 specialist content; P2 items are valuable but lower-leverage given current state.

The "don't build this" section at the end is the most important single page in this report. The temptation will be to keep authoring at K6 — please resist it.

---

## 1. What the coverage data actually says

### 1.1 The shape of the gap

The corpus is a pyramid balanced on its apex. K6 alone holds 33% of templates; K1–K6 holds 94%; K7–K12 holds 5.8%. Within K7–K12, the 37 templates cluster on **percentages.growth (8)**, **measurement.time (7 across grades)**, **statistics specialty stubs (3)**, and a smattering of one-template cells. Whole topic columns are blank from K7 upward: algebra.expressions, algebra.exponents, algebra.factoring, algebra.inequalities, algebra.simplify, algebra.variables, geometry.surface_area, geometry.perimeter, geometry.right_triangle/Pythagoras, geometry.trigonometry, statistics.median, statistics.mode, statistics.dispersion (except K9 stub), statistics.combinatorics, statistics.distributions, decimals.*, fractions.* (all subtopics K7+), measurement.unit_conversion (K7+), numbers.* (K3+), ratios.* (K9+).

### 1.2 The contamination data, read honestly

Mean max-Jaccard 0.0079 with p95 0.042 means the corpus is genuinely *not* a GSM8K reskin. The single contaminated template (`k6_medium_decimals_add_sub_01`, the canonical "paid with $20, find change" pattern) is doing what every GSM8K problem does. The high-similarity *domains* — ratios (0.044), decimals (0.034), geometry (0.033), algebra (0.031) — are exactly the domains where GSM8K saturates: shopping-with-prices, basic-proportion, and rate-time-distance. The low-similarity domains (fractions 0.018, percentages 0.021) are low not because they're more original but because GSM8K barely covers them.

**The implication for new authoring is structural.** Adding more "person buys items" templates at any grade re-creates GSM8K's saturation pattern even if the surface tokens differ. New proposals need to explicitly avoid: (a) money-change-with-$20, (b) "X items at $Y each, plus tax", (c) basic-proportion ("if 3 lbs cost $9, how much for 7 lbs"), (d) single-mover distance = rate × time, (e) percent-off-then-tax sequences. Conversely, structural patterns that GSM8K's authoring guidelines actively excluded — invariants under transfer, work-backwards from final state, reciprocal-rate combination, mixture/concentration with mass conservation, integer-constraint enumeration, conditional/case-split — are wide-open territory and the corpus should lean into them.

### 1.3 The five spec-mandated families don't exist

The user's prior spec calls out `area_perimeter_chain`, `compound_growth`, `multi_person_sharing`, `sequential_purchase`, and `rate_time` as required topics. Coverage status is brutal: `area_perimeter_chain` has 4 templates loosely under `geometry.area_composite` (none above K7); `compound_growth` exists only as 8 thin `percentages.growth` templates; `multi_person_sharing` and `sequential_purchase` **do not exist as topic names**; `rate_time` is conflated with `measurement.time`, which is mostly clock-reading. Any priority list has to put these first.

---

## 2. Highest-leverage empty cells, ranked

The ranking criterion combines four signals: (i) curricular weight in the prior 8-system research, (ii) step-count yield (5–7+ steps without contrivance), (iii) predicted GSM8K novelty, (iv) bridge value between the K6 mass and the thin K7+ tail.

| Rank | Empty cell zone | Curricular weight | Step yield | GSM8K novelty | Bridge value |
|---|---|---|---|---|---|
| 1 | K7–K9 algebra.equations from word problems (currently 1+1+0 templates at K7,K8,K9) | All 8 systems | 5–8 | High (forces variable-setting; GSM8K's "no variable" rule excluded this) | Critical — connects K6 arithmetic to K10+ |
| 2 | K7–K10 ratios with bar-model invariants | Singapore, Japan, Estonia, Finland | 6–10 | Very high (bar-model invariants excluded by GSM8K) | High |
| 3 | K8–K10 geometry.right_triangle / Pythagoras / trigonometry | All 8 (Japan, Singapore especially) | 5–8 | High | High — currently zero coverage |
| 4 | K7–K10 statistics.probability with conditional/tree structure | CCSS HSS-CP, Singapore 4052 §S2, Estonia IV kursus | 4–7 | Very high (probability fractions excluded by GSM8K) | High |
| 5 | K8–K11 percentages.compound_growth (real compound interest, not "+5% twice") | Finland MAA9, Estonia VIII kursus, Norway 1P, CCSS HSF-LE.A.4 | 5–8 | Medium — needs structural twist | High — bridges thin K7–K11 percent stub |
| 6 | K7–K10 multi_person_sharing as a named family | Singapore P5–P6, Japan 倍数算 | 6–10 | Very high | Critical — spec-mandated, doesn't exist |
| 7 | K7–K10 rate_time (work, pipes, relative motion) as a named family | Japan 仕事算/旅人算/流水算, Singapore O-level | 5–8 | Very high (work-rate largely absent from GSM8K) | Critical — spec-mandated |
| 8 | K7–K10 sequential_purchase as a named family | Netherlands RME, CCSS modeling | 6–10 | Medium-high — must avoid simple "buy items" | Critical — spec-mandated |
| 9 | K7–K10 area_perimeter_chain | Singapore 4052 §G3, Japan Math I, CCSS HSG-MG | 6–9 | High — composite solids underweighted by GSM8K | Critical — spec-mandated |
| 10 | K7–K9 numbers (modular, GCD/LCM word problems, Diophantine) | Japan Math A, Finland MAA11 | 4–8 | Very high (modular/Diophantine forbidden by GSM8K rules) | Medium — creates new topic axis |
| 11 | K8–K11 statistics.dispersion (variance, SD, IQR from grouped data) | Singapore 4052 §S1, Finland MAA8, Sweden Mat 2 | 5–8 | Very high | Medium |
| 12 | K11–K12 percentages.compound_growth → annuities/loan amortization | Finland MAA9, Singapore 9758 §2 | 7–12 | Medium — annuity recurrence is novel structure | Medium |
| 13 | K11–K12 statistics.distributions (binomial, normal) | Singapore 9758 §6.2-6.3, Finland MAA12, Estonia VI kursus | 5–7 | Very high | Low — small grade band |
| 14 | K11–K12 statistics.hypothesis_testing | Singapore 9758 §6.5, Netherlands wiskunde A E6, Norway S2 | 6–9 | Very high | Low |
| 15 | K10–K12 measurement.dimensional_analysis / density | CCSS HSN-Q, HSG-MG.A, Norway 1P | 4–7 | High | Medium — entirely empty currently |

Ranks 1–9 anchor the P0 list. Ranks 10–11 anchor P1. Ranks 12–15 anchor P2 along with optimization and combinatorics families introduced below.

---

## 3. Twenty-two new problem-family proposals

Proposals are grouped by the mathbot taxonomy axis they target. Each entry names the empty cell(s) it fills, gives the structural skeleton, the source-curriculum hook, two or three context examples, parameterisation hints, the AI-benchmarking rationale, and the predicted GSM8K-overlap call with a structural twist where overlap risk exists. Where a prior-report proposal partially overlaps, it's noted; otherwise the proposal is fully new.

### Proposals targeting algebra.* (K7–K12 currently near-empty)

#### P-A1. Linear-system word problems with two unknowns from purchase combinations
**Target cells.** algebra.equations K7 (currently 1), K8 (currently 1), K9 (empty), K10 (empty); secondary fill of `multi_person_sharing` at K7–K8.

**Structural skeleton.** Two purchases at known total cost, each combining two item types in different quantities. Solve the 2×2 system. Variant: three purchases with three item types (3×3). This is the Japanese 消去算 (shoukyo-zan) pattern.

**Source.** Japan Course of Study 2017, 中学校 §数と式 (grade 8 simultaneous equations from word problems); Estonia põhikool §72 ("lineaarvõrrandid tekstülesannetest"); Singapore 4052 §N4; Norway LK20 grade 10 algebra.

**Step structure.** 5–7 steps: identify variables, write two equations, eliminate, solve, back-substitute, sanity-check non-negative integers, answer. State tracked: two unknowns plus their per-item prices.

**Difficulty tier.** Medium (K7–K8), hard (K9–K10 with three-variable extension).

**Examples.** (1) "A school orders 3 calculators and 2 protractors for €47.50, and 2 calculators and 5 protractors for €40.25. Find each price." (2) "At a Tartu market: 4 kg apples + 3 kg pears costs €11.10; 7 kg apples + 2 kg pears costs €13.65. Cost of 5 kg of each?" (3) Three-variable: "A bakery sells boxes of 2 croissants + 1 brioche + 3 pains au chocolat for €8.40; 1+2+2 for €7.10; 3+1+1 for €6.85. Each price?"

**Parameterisation.** Coefficient matrices with integer determinant in {±1, ±2, ±3} to keep arithmetic clean; total prices chosen to yield rational unit prices ending in .00, .25, .50, or .75.

**Why it matters for AI benchmarking.** GSM8K's "vast majority solvable without defining a variable" guideline systematically excluded systems-of-equations word problems. Models that pattern-match GSM8K will try to chain forward arithmetic and fail. The 3×3 variant (Diophantine-flavored when integer constraints apply) is essentially absent from any open benchmark.

**Predicted GSM8K overlap.** **Low.** Surface tokens look like "buy items at price each" — which is high-overlap territory — but the structural requirement to write and solve a 2×2 system is the exact thing GSM8K's guidelines forbade. No structural twist needed; the 2-variable requirement *is* the twist.

---

#### P-A2. Algebraic-expression manipulation with substitution chains
**Target cells.** algebra.expressions K6+ (entire column empty above K5); algebra.simplify K7+ (empty); algebra.equivalent_expressions K7+ (empty).

**Structural skeleton.** Given a multi-term expression in two or three variables, simplify, substitute given values, evaluate. Variant: change-of-subject — given a formula relating three quantities, rearrange to isolate a target variable, then substitute.

**Source.** Singapore 4052 §N3 ("change of subject"); Norway LK20 1T (transform formulas); CCSS HSA-CED.A.4; Sweden Mat 1c (factoring/multiplying); Finland MAA2.

**Step structure.** 4–6 steps: distribute, collect like terms, factor where applicable, isolate target, substitute, evaluate.

**Difficulty tier.** Easy (K7), medium (K8–K9), hard with rational expressions (K10).

**Examples.** (1) "Surface area of a cylinder is S = 2πr(r + h). Solve for h, then find h when S = 264 cm² and r = 4 cm. Use π = 22/7." (2) "Given E = ½mv² + mgh, isolate v; compute v when E = 245 J, m = 2 kg, g = 9.8 m/s², h = 5 m." (3) "Simplify (3a²b − 6ab²)/(3ab) + (a + 2b), then evaluate at a = 4, b = −1."

**Parameterisation.** Choose constants so that the simplified expression evaluates to a small integer or simple fraction. Use physics-style formulas (kinetic energy, lens equation 1/f = 1/u + 1/v, ideal gas with two states) to bring in genuinely multi-step rearrangement.

**Why it matters.** Formula manipulation is a core engineering-mathematical skill that GSM8K never tests. LLMs frequently mis-rearrange formulas with denominators or signed terms.

**Predicted GSM8K overlap.** **Low.** Formula rearrangement is structurally absent from GSM8K. No twist needed.

---

#### P-A3. Quadratic word problems via factoring or completing the square
**Target cells.** algebra.equations K9 (empty), K10 (empty); algebra.factoring K7+ (empty); secondary fill of geometry.area at K9–K10.

**Structural skeleton.** Set up a quadratic from a geometric or kinematic context, solve, reject the non-physical root, answer. Contexts: rectangular field with a constraint, projectile height, area of a frame around a picture.

**Source.** Singapore 4049 §A1; Norway LK20 1T (quadratic from contexts); CCSS HSA-REI.B.4; Japan Math I §3; Sweden Mat 2c (completing the square).

**Step structure.** 6–8 steps: define variable, express constrained quantity, set up quadratic, factor or complete the square, find both roots, reject non-physical, state answer with units, verify by substitution.

**Difficulty tier.** Medium (factorable integer roots), hard (irrational roots requiring exact form a + b√c).

**Examples.** (1) "A rectangular garden 3 m longer than wide has area 70 m². Find dimensions." (2) "A picture 20 × 30 cm is mounted in a frame of uniform width. Total framed area is 1064 cm². Find frame width." (3) "A ball thrown upward at 24 m/s from height 1.5 m has h(t) = 1.5 + 24t − 4.9t². When does it hit the ground? Give exact and 2-dp."

**Parameterisation.** Choose dimensions and constants so that the quadratic factors over ℤ at "medium" tier; use discriminant ≠ perfect square at "hard" tier to force the quadratic formula.

**Why it matters.** Tests the rejection-of-non-physical-root step that LLMs frequently skip, and the "exact form" requirement that GSM8K's integer-answer rule excluded.

**Predicted GSM8K overlap.** **Low.** Quadratic word problems are absent from GSM8K by design (no exponents). No twist needed.

---

#### P-A4. Inequality word problems with constraint reasoning
**Target cells.** algebra.inequalities K7+ (empty); algebra.equations K11 (boost from 4).

**Structural skeleton.** Given a linear constraint with a parameter, find the range of values satisfying the constraint, or the integer count of solutions. Variant: compound inequality with an "at least … and at most …" structure leading to an interval.

**Source.** Singapore 4052 §N4; Estonia gümnaasium I kursus; Sweden Lgr22 algebra (förändringsfaktor + olikheter); CCSS HSA-CED.A.3.

**Step structure.** 5–7 steps: translate prose to inequality, isolate variable, identify integer / continuous solution set, count or describe interval, state in context.

**Difficulty tier.** Medium (single inequality), hard (compound or with absolute value).

**Examples.** (1) "A ferry can carry up to 1800 kg. Cars weigh 1100 kg each, motorcycles 220 kg. With 1 car already loaded, what's the maximum motorcycles?" (2) "An online plan charges €15 base plus €0.40 per GB; a competitor charges €25 flat for unlimited. For what range of monthly GB usage is the first plan cheaper?" (3) "A mover charges €60 + €25/hour. A budget of €200 leaves how many full hours of work, and how much is unused?"

**Parameterisation.** Constants chosen so that the boundary case is non-integer, forcing students to apply ⌊ ⌋ or ⌈ ⌉ reasoning. The break-even crossover variant doubles as a `sequential_purchase` decision problem (see P-S2).

**Why it matters.** The break-even/decision case-split is one of the missing-from-GSM8K reasoning patterns identified in the GSM-Plus *Critical Thinking* category and Mirzadeh et al. 2024. Tests case-split reasoning over a continuous parameter.

**Predicted GSM8K overlap.** **Medium-low for the case-split variant** — the surface form looks like "two-plan comparison" which has occasional GSM8K analogues. **Twist:** require an *interval* or *integer count* answer rather than a single number, which GSM8K's integer-final-answer rule excludes.

---

#### P-A5. Exponential and logarithmic equations from compound-growth contexts
**Target cells.** algebra.exponents K7+ (empty); percentages.growth K10–K12 (thin, 1+2+1); secondary fill of `compound_growth` family.

**Structural skeleton.** Given a quantity following A·b^t with two known data points, solve for the unknown parameter (a, b, or t). Often requires logarithms at K10+.

**Source.** Singapore 4052 §N2 (indices and exponentials); CCSS HSF-LE.A.4 (solve a·b^t = c); Finland MAA9 / MAB6; Estonia VIII kursus (eksponent- ja logaritmfunktsioon); Japan Math II §10.

**Step structure.** 5–8 steps: identify the model, substitute the two known points to set up a system, divide to isolate b, solve for a, take logs to find t for a target value, sanity-check growth direction.

**Difficulty tier.** Medium (find b given two consecutive periods), hard (find t requiring log_b operations or natural-log conversion).

**Examples.** (1) "A bacterial culture grows 14% per hour. Mass at 09:00 is 3.2 g; when does it first exceed 50 g?" (2) "A radioactive isotope has half-life 28 years. Starting at 200 g, when does it drop below 5 g?" (3) "A car's value depreciates by a constant factor each year; €24 000 new, €15 360 after 2 years. Find the annual factor and value after 5 years."

**Parameterisation.** Choose b ∈ {0.85, 0.90, 1.05, 1.08, 1.12, 1.15, etc.} and time-points so the system has clean log answers, or so the exact answer is rational.

**Why it matters.** Compound-growth is spec-mandated and currently thin. The log-solution step is structurally novel against GSM8K (no exponents, no logs).

**Predicted GSM8K overlap.** **Low.** Exponential equations are excluded by GSM8K's operation-restriction rule.

---

### Proposals targeting geometry.* (K9+ near-empty, several spec-mandated gaps)

#### P-G1. Right-triangle and Pythagoras word problems with indirect measurement
**Target cells.** geometry.right_triangle K8+ (empty); geometry.area K9+ (empty); secondary fill of measurement.scale (entirely empty).

**Structural skeleton.** A real-world configuration (ladder, flagpole, surveying baseline) reduces to a right triangle whose hypotenuse or leg is the unknown. Two-stage variants chain a Pythagoras computation into an area or perimeter follow-up.

**Source.** Japan Course of Study 中学校 §図形 (Pythagorean theorem with applications, grade 9); Singapore 4052 §G4; CCSS HSG-SRT.B.4; Norway LK20 grade 10 (Pythagoras + trig in real contexts).

**Step structure.** 5–7 steps: parse geometric configuration, identify right triangle, label sides, apply Pythagoras, take a square root (typically irrational), use the result in a follow-up area/perimeter computation, state with appropriate precision.

**Difficulty tier.** Medium, hard for chained two-triangle or 3-D variants.

**Examples.** (1) "A 5 m ladder leans against a wall with foot 1.4 m out. Slid to 2.1 m out — how far did the top descend?" (Two-Pythagoras chain.) (2) "A rectangular plot 60 × 80 m has a diagonal path. To pave the path 1.2 m wide, what area of paving is needed?" (Pythagoras → rectangle area.) (3) "A flagpole's shadow is 8 m on level ground. From a window 6 m above ground, the angle of depression to the shadow tip is 30°. Pole height?" (3-D variant, K10.)

**Parameterisation.** Use Pythagorean triples (3-4-5, 5-12-13, 8-15-17) for "medium"; force irrational results √k requiring expression as a√b for "hard." The two-state-ladder variant is a particularly nice "before/after" structural pattern.

**Why it matters.** Square roots, irrational intermediate results, and geometric reasoning are all GSM8K-excluded. The ladder slide variant tests *change* in a Pythagoras quantity, which is structurally distinct from a single Pythagoras application.

**Predicted GSM8K overlap.** **Low.** Geometry beyond simple area/perimeter is nearly absent from GSM8K.

---

#### P-G2. Trigonometry and angles of elevation/depression with bearings
**Target cells.** geometry.trigonometry (entirely empty across all grades); geometry.right_triangle K10–K11.

**Structural skeleton.** Given two angles of elevation from two points to a fixed target, find the target's height. Variant: bearings problem where two distances and an included angle yield a third by law of cosines.

**Source.** Singapore 4052 §G4 (sine rule, cosine rule, bearings, 3-D problems); CCSS HSG-SRT.D.10–11; Estonia gümnaasium II kursus; Norway LK20 1T trigonometry.

**Step structure.** 6–8 steps: draw the configuration, identify the two triangles (or the single oblique triangle), apply tan/sin/cos or the law of sines/cosines, solve a small system if both unknowns are coupled, evaluate, state with units.

**Difficulty tier.** Medium (right-triangle elevation with one unknown), hard (oblique triangle requiring law of cosines).

**Examples.** (1) "From a point 80 m from a tower's base, angle of elevation to the top is 32°. From a second point 30 m further away, angle is 22°. Tower height?" (Two-triangle, two unknowns; solve for height and check consistency.) (2) "Ship sails 40 km on bearing 060°, then 25 km on bearing 150°. Distance and bearing from start?" (3) "An observer 1.6 m tall sees the top of a building at 45° elevation; walks 20 m closer, sees it at 60°. Building height?"

**Parameterisation.** Use angles {30°, 45°, 60°} for exact-form variants; use other angles requiring calculator with answer to 1 dp for applied variants.

**Why it matters.** Trigonometric word problems are universally tested in upper secondary worldwide and entirely absent from current corpus. They test the parse-the-configuration step that LLMs notably struggle with on geometry problems.

**Predicted GSM8K overlap.** **Very low.** Trig is excluded by GSM8K rules.

---

#### P-G3. Composite-solid volume with unit-conversion and conservation
**Target cells.** geometry.volume K7–K9 (empty), K11+ (empty); geometry.surface_area K7+ (empty); `area_perimeter_chain` family at K8–K10.

**Structural skeleton.** A solid is built from two or three primitives (cylinder + hemisphere; cone + cylinder; rectangular box minus cylindrical hole). Compute volume or surface area; secondary stage involves filling/draining the solid (water transferred between two vessels — *conservation* invariant) or finding mass via density.

**Source.** Singapore 4052 §G3 (mensuration, composite solids, water transferred between vessels); Japan Course of Study 中学校 §図形; Estonia põhikool §73; CCSS HSG-GMD.A.3 + HSG-MG.A.2 (density); Norway LK20 1P dimensional analysis.

**Step structure.** 6–9 steps: decompose the solid, compute volumes/surface areas of each primitive, sum, convert units (e.g., cm³ → litres → kg via density), apply conservation if water is transferred, answer.

**Difficulty tier.** Medium (two-primitive composite without conservation), hard (three-primitive with conservation and unit chain).

**Examples.** (1) "A grain silo is a cylinder 12 m tall, 3 m radius, topped by a hemisphere. Total grain capacity in tonnes if grain density is 750 kg/m³?" (2) "A cone-shaped funnel (height 18 cm, top radius 6 cm) drains into a cylinder (radius 5 cm, height 24 cm) at 40 cm³/s. Time to fill cylinder, given funnel starts full?" (3) "A rectangular tank 80 × 60 × 50 cm contains water to depth 30 cm. A solid metal cylinder (radius 8 cm, height 50 cm) is fully submerged. New water depth?"

**Parameterisation.** Choose dimensions so that volumes evaluate to clean numbers using π = 22/7 or π = 3.14; use density values matching real materials (water 1000, steel 7850, oil 920) to keep contexts realistic.

**Why it matters.** Multi-primitive volume + conservation + unit conversion is a 3-axis composition that GSM8K cannot test (one-step at most). Density problems in particular are flagged in CCSS HSG-MG as a modeling priority and are entirely empty in mathbot.

**Predicted GSM8K overlap.** **Low.** No structural analogue in GSM8K.

---

#### P-G4. Coordinate geometry with multi-constraint point-finding
**Target cells.** geometry.coordinate_plane K7–K10, K12 (empty); secondary fill of algebra.equations K9–K12.

**Structural skeleton.** Given two or three geometric constraints (point on a line, equidistant from two points, on the perpendicular bisector, etc.), find the point's coordinates. Variant: find the equation of the circle through three given points.

**Source.** Singapore 4052 §G1 (coordinate geometry); Singapore 4049 §G2 (circle equation); Japan Math II §9 (図形と方程式); Estonia gümnaasium III kursus; CCSS HSG-GPE.

**Step structure.** 6–8 steps: write each constraint as an equation, solve the system, verify with the unused constraint, answer.

**Difficulty tier.** Medium (linear constraints), hard (one quadratic — circle through three points).

**Examples.** (1) "Find the point on y = 2x − 3 equidistant from A(1,5) and B(7,1)." (2) "Find the equation of the circle passing through (0,0), (4,0), and (0,6); state center and radius." (3) "Triangle has vertices A(2,1), B(8,3), C(5,7). Find the circumcenter, then the circumradius."

**Parameterisation.** Choose coordinates yielding integer or half-integer answers; ensure the three constraint equations are independent.

**Why it matters.** Tests system-of-equations setup combined with geometric interpretation. The triangle-circumcenter variant exercises the algebra→geometry translation that LLMs typically execute poorly.

**Predicted GSM8K overlap.** **Very low.** Coordinate-pair answers were excluded from GSM8K.

---

### Proposals targeting statistics.* and probability.* (currently nearly empty K6+)

#### P-S1. Mean, median, and dispersion from grouped frequency data
**Target cells.** statistics.mean K6–K12 (empty), statistics.median K6+ (empty), statistics.dispersion K10–K12 (empty); secondary statistics.mode K6+.

**Structural skeleton.** Given a grouped frequency table (class intervals + frequencies), compute the estimated mean using midpoints, the modal class, and either the standard deviation or the IQR via cumulative frequency. Variant: compare two distributions on the same scale.

**Source.** Singapore 4052 §S1 (mean/median/mode for grouped data, quartiles, IQR, SD, box plot, cumulative frequency); Sweden Mat 2a/2b (percentile, SD); Finland MAA8; Japan Course of Study 中学校 grade 8 (representative values + dispersion).

**Step structure.** 6–8 steps: compute midpoints, multiply by frequencies, sum, divide by total → mean; identify modal class; build cumulative frequency, locate median and quartile positions, interpolate; compute IQR or use Σf(x−x̄)² for variance and SD.

**Difficulty tier.** Medium (estimated mean + modal class + median), hard (full dispersion comparison of two distributions).

**Examples.** (1) "Test scores of 50 students grouped in 10-point intervals from 30–39 to 90–99 with frequencies 2, 5, 9, 14, 11, 6, 3. Estimate mean and median; identify modal class." (2) "Two factories' bolt diameters in mm, grouped. Compute and compare means and SDs; comment on which is more consistent." (3) "Cumulative frequency of monthly rainfall over 60 months, grouped in 20 mm intervals. Find median, IQR, and the percentage of months with rainfall above 80 mm."

**Parameterisation.** Use ~5–7 class intervals; choose frequencies summing to 50 or 100 to keep arithmetic clean; ensure a unique modal class.

**Why it matters.** Grouped-data statistics is standard at K8–K10 internationally and entirely absent from current corpus. Tests the *interpolation* step (median position within a class), which LLMs frequently mis-execute by treating the position-statistic as a direct table lookup.

**Predicted GSM8K overlap.** **Very low.** Grouped statistics is excluded from GSM8K.

---

#### P-S2. Probability with two-stage trees and conditional structure
**Target cells.** statistics.probability all grades except K8=1 (essentially empty); secondary fill of statistics.combinatorics K7+.

**Structural skeleton.** Given two sequential events with stated probabilities (with or without replacement), find P(specific outcome), P(at least one), or P(A | observed B). The Bayes-lite variant gives base rates and test sensitivity/specificity, asks for posterior probability.

**Source.** Singapore 4052 §S2; CCSS HSS-CP.A.3 + B.6; Estonia IV kursus (classical, geometric, conditional); Netherlands wiskunde A vwo Domein E; Japan Math A §5; Norway LK20 (uavhengige hendelser).

**Step structure.** 5–7 steps: draw or enumerate the tree, multiply along branches for joint probabilities, sum the relevant branches for the marginal, divide for conditional, simplify the fraction.

**Difficulty tier.** Medium (independent events with replacement), hard (without replacement; conditional / Bayes).

**Examples.** (1) "A bag contains 5 red, 3 blue, 2 green marbles. Two are drawn without replacement. P(both same color)?" (2) "A diagnostic test has 96% sensitivity and 92% specificity; the disease prevalence is 4%. Given a positive test, P(disease)?" (3) "A factory has two machines: A produces 60% of items with 2% defect rate; B produces 40% with 5% defect rate. A random item is defective. P(it came from B)?"

**Parameterisation.** Choose probabilities yielding clean fractional answers with denominators in {10, 20, 25, 50, 100, 200}; use percentages convertible to ratios for the Bayes variants.

**Why it matters.** Conditional probability and Bayes-style problems are flagged in the GSM-Plus literature as a hard category; LLMs frequently confuse P(A|B) with P(B|A) or with P(A∩B). GSM8K excludes probability fractions by its integer-answer rule.

**Predicted GSM8K overlap.** **Very low.** Probability-fraction answers are forbidden by GSM8K's authoring guidelines.

---

#### P-S3. Counting and combinatorics with restrictions
**Target cells.** statistics.combinatorics (empty across all grades).

**Structural skeleton.** Arrange or select from a set with one or two structural restrictions (e.g., "no two girls adjacent", "at least one of X", "first letter must be a vowel"). Inclusion-exclusion variant: count items satisfying at least one of three sets given pairwise and triple-overlap counts.

**Source.** Singapore 4052 §S2 / 9758 §6.1; CCSS HSS-CP.B.9 (+); Japan Math A §5; Norway LK20 grade 10 (kombinatorikk); Estonia IV kursus.

**Step structure.** 4–7 steps: identify the structure (arrangement vs selection, with vs without restrictions), choose the right counting technique (gap method, complement, inclusion-exclusion), execute, simplify.

**Difficulty tier.** Easy (basic permutations/combinations, K7–K8), medium (gap method, K9–K10), hard (inclusion-exclusion with three sets, K10–K11).

**Examples.** (1) "Five boys and three girls stand in a line. How many arrangements have no two girls adjacent?" (2) "From a class of 10 boys and 8 girls, choose a 5-person committee with at least 2 girls. How many ways?" (3) "In a survey of 120 students, 70 study French, 60 Spanish, 50 German; 30 French and Spanish, 25 French and German, 20 Spanish and German; 10 study all three. How many study none?"

**Parameterisation.** Use small set sizes (n ≤ 10) for hand-computable answers; ensure the restricted-arrangement formula (e.g., 5! · C(6,3)) yields a recognizable integer.

**Why it matters.** Combinatorics is the largest single content gap in LLM math benchmarks (CombiBench, arXiv 2505.03171). The "complement vs direct" reasoning and inclusion-exclusion structure are uniquely combinatorial.

**Predicted GSM8K overlap.** **Very low.** Factorials and combinations are excluded by GSM8K's operation rules.

---

#### P-S4. Binomial-distribution applications
**Target cells.** statistics.distributions K11–K12 (empty); statistics.probability K11–K12.

**Structural skeleton.** Given a Bernoulli trial with success probability p over n trials, compute P(X = k), P(X ≥ k), or P(a ≤ X ≤ b). Variant: find n such that P(X ≥ 1) ≥ 0.95 ("at least one success").

**Source.** Singapore 9758 §6.2; Estonia VI kursus; Finland MAA12 / MAB5; Netherlands wiskunde A vwo Domein E (binomial); CCSS HSS-MD; Sweden Mat 2c.

**Step structure.** 5–7 steps: identify the distribution as B(n, p), write the relevant probability expression, expand the sum, use the complement when k is small or n − k is small, evaluate.

**Difficulty tier.** Medium (single P(X = k) or P(X ≥ k) for small n), hard (find n given a probability bound, which yields an inequality in n).

**Examples.** (1) "A vaccine is 88% effective; 25 people are vaccinated. Find P(at most 2 fail)." (2) "A basketball player scores free-throws with probability 0.75. How many attempts to be at least 95% confident of scoring at least one?" (3) "A multiple-choice test has 12 questions, each with 4 options. A student guesses; passing requires at least 6 correct. Pass probability?"

**Parameterisation.** n ∈ [10, 30]; p ∈ {0.1, 0.2, 0.25, 0.3, 0.5, 0.7, 0.75, 0.8, 0.9}.

**Why it matters.** Binomial reasoning is universally tested in upper-secondary statistics; entirely empty in current corpus. The "find n such that P(X ≥ 1) ≥ threshold" variant exercises the inequality-on-discrete-parameter pattern.

**Predicted GSM8K overlap.** **Very low.**

---

#### P-S5. Hypothesis testing on means and proportions
**Target cells.** statistics.inference K11 (1 stub), K12 (empty); secondary fill of statistics.dispersion K11–K12.

**Structural skeleton.** Given a sample mean (or proportion) and population parameters, perform a one- or two-tailed z-test or t-test at a stated significance level, compute the test statistic, compare with critical value or compute p-value, state the conclusion in context.

**Source.** Singapore 9758 §6.5; Netherlands wiskunde A vwo Domein E6 (verklarende statistiek); Norway S2; Finland MAA12 / MAB5; Sweden Mat 2c (regression + correlation).

**Step structure.** 7–9 steps: state H₀ and H₁, identify test type, compute SE, compute test statistic, find critical value or p-value, compare, state decision and contextual conclusion.

**Difficulty tier.** Hard (this is upper-secondary specialty content).

**Examples.** (1) "A factory claims its bolts have mean diameter 10.0 mm with SD 0.15. A sample of 36 bolts has mean 10.06. Test at α = 0.05 (two-tailed) whether the claim is consistent." (2) "Historically 30% of voters support a policy. A poll of 250 yields 87 supporters. Test at α = 0.05 (one-tailed) for an increase." (3) "Two teaching methods produce sample means 72 and 76 with SDs 8 and 10 over n₁ = 40, n₂ = 35 students. Test at α = 0.05 whether the methods differ."

**Parameterisation.** Choose statistics so that the z- or t-value falls clearly inside or outside the critical region (avoid borderline cases that obscure the decision step).

**Why it matters.** Hypothesis testing is an end-of-curriculum topic worldwide and almost wholly absent. The interpretation step ("state in context") is reliably mishandled by LLMs that compute correctly but then phrase conclusions about α/p-values incoherently.

**Predicted GSM8K overlap.** **Very low.** Beyond GSM8K's grade-school scope.

---

### Proposals targeting numbers.* and measurement.*

#### P-N1. Modular arithmetic and remainder word problems
**Target cells.** numbers.modular_arithmetic K7+ (empty); numbers.gcd_lcm K7+ (empty above K6).

**Structural skeleton.** Find a positive integer satisfying simultaneous remainder conditions; find the next time two periodic events coincide; find a day of the week N days after a given date. Includes Chinese-Remainder-style "smallest n with n ≡ a (mod p) and n ≡ b (mod q)".

**Source.** Japan Math A §6 (Euclidean algorithm, linear Diophantine, base-n); Finland MAA11 (lukuteoria); Estonia gümnaasium I kursus; Norway LK20 grade 10 (number patterns); CCSS HSF-BF.A.

**Step structure.** 4–7 steps: write the modular conditions, find LCM of moduli, search or apply CRT for the smallest solution, state.

**Difficulty tier.** Medium (single LCM, two events coinciding), hard (CRT-style two-condition problem).

**Examples.** (1) "Bus A leaves the station every 18 min; bus B every 24 min. Both leave at 07:00. Next simultaneous departure?" (2) "A batch of marbles can be grouped exactly into piles of 6, 8, or 10 with 3 left over each time. Smallest possible batch size?" (3) "Today is Tuesday. What day of the week is in 1 000 days?"

**Parameterisation.** Choose moduli with LCM ∈ [50, 500]; offsets that yield clean answers.

**Why it matters.** Modular reasoning is forbidden by GSM8K's operation rules and is structurally distinct from forward arithmetic. Day-of-week problems specifically exercise the periodicity-and-mod-arithmetic insight.

**Predicted GSM8K overlap.** **Very low.**

---

#### P-N2. GCD/LCM applied to tiling, packaging, and rhythm problems
**Target cells.** numbers.gcd_lcm K7+ (empty above K6); secondary fill of geometry.area_composite K7–K8.

**Structural skeleton.** Find the largest square tile that fits an a × b rectangle exactly (GCD); find the smallest square that can be tiled by a × b rectangles (LCM); find when two periodic events with periods p and q coincide. Variant: minimize tiles needed to cover a region.

**Source.** Estonia põhikool; Japan Course of Study 中学校 (number theory introduction); CCSS 6.NS.B.4 extended to applications.

**Step structure.** 3–5 steps: identify whether GCD or LCM applies, factorize, compute, interpret in context.

**Difficulty tier.** Easy (single GCD or LCM), medium (chained — find GCD then count tiles).

**Examples.** (1) "A rectangular floor 144 × 180 cm is to be tiled with congruent square tiles, no cutting. Largest tile size and number of tiles needed?" (2) "Three friends jog laps of 240 m, 320 m, and 400 m on the same track at the same speed. After how many metres do they meet at the start again?" (3) "Boxes of 14 pencils and 21 pens are to be packed identically with the same number of pencils and pens per box, all items used. Most boxes possible?"

**Parameterisation.** Choose pairs (a, b) with non-trivial GCD (GCD ≥ 2), avoiding co-prime cases that give trivial answers.

**Why it matters.** Connects K6 GCD/LCM mass to K7+ word problems and tests the "which operation does this context call for" decision that LLMs occasionally invert.

**Predicted GSM8K overlap.** **Low.** Some basic LCM problems exist in GSM8K but the tiling/rectangle framing is structurally different.

---

#### P-M1. Multi-step unit conversion and dimensional analysis
**Target cells.** measurement.unit_conversion K7+ (empty); measurement.dimensional_analysis (entirely empty).

**Structural skeleton.** Convert a quantity through three or more unit-system transitions (e.g., kg/L → g/mL → oz/fl-oz; km/h → m/s → ft/s; W·h/day → kW·h/year → energy bill in €). Variant: density problem combining unit conversion with a volume/mass computation.

**Source.** Norway LK20 1P (sammensatte enheter); CCSS HSN-Q.A.1 (modeling standard); CCSS HSG-MG.A.2 (density modeling); Singapore 4052 §G3 (mensuration with units).

**Step structure.** 4–7 steps: identify the source and target units, write the conversion factors, multiply through, evaluate, round to appropriate precision, state with units.

**Difficulty tier.** Medium (3-step single-quantity conversion), hard (combined-unit conversions like km/h → m/s with simultaneous mass/volume conversion).

**Examples.** (1) "A car consumes 6.4 L/100 km. Convert to km per US gallon (1 gal ≈ 3.785 L)." (2) "A power plant produces 850 MW. How many MW·h per day, and what is the annual revenue at €0.12 per kW·h?" (3) "Concrete has density 2400 kg/m³. A column 0.4 × 0.4 × 3.0 m has mass how many tonnes, and what is its mass per linear metre in kg/m?"

**Parameterisation.** Use realistic unit-conversion constants (km↔mi 1.609, kg↔lb 2.205, L↔gal 3.785) and multi-stage densities so the chain has 3+ multiplicative steps.

**Why it matters.** Dimensional analysis is the hidden multi-step skill of applied math and is entirely empty in mathbot. Tests the *unit-bookkeeping* discipline that LLMs frequently break (the "multiply by km/m and end up with km²/m" failure mode).

**Predicted GSM8K overlap.** **Low.** Single-step unit conversions appear; multi-step chains do not.

---

### Proposals targeting the spec-mandated families

These five families are top priority because (i) they are user-required, (ii) two of them don't exist as topic names yet, and (iii) all five admit structural twists that make them low-overlap with GSM8K.

#### P-SP1. `multi_person_sharing` — bar-model invariant problems
**Target cells.** New family `multi_person_sharing` at K6–K10 (does not exist); secondary fill of ratios K7–K10.

**Structural skeleton.** Three or more parties share a quantity in a stated ratio. A transformation occurs (transfer between parties, all spend the same, one party doubles holdings, etc.). The problem requires identifying the *invariant* (constant total, constant difference, one party constant) before back-solving. This is the Singapore "model method" combined with Japanese 倍数算 and 年齢算.

**Source.** Singapore Math P5–P6 challenging word problems; Japan tokushuzan (倍数算, 年齢算, 和差算, 分配算); Estonia põhikool (proportional division). Strongly represented in the prior research artifact (Singapore section).

**Step structure.** 6–10 steps: identify the conservation law, rescale ratios so the conserved quantity has a common unit count, equate units to numbers, back-solve, sanity-check.

**Difficulty tier.** Medium (two-party transfer, constant-total), hard (three-party with chained transfers, or the units-and-parts pattern requiring two simultaneous unit systems).

**Examples.** (1) **Constant total / two-party transfer:** "Anna and Ben have stickers in ratio 5:3. After Anna gives 18 to Ben, the ratio is 1:1. How many did each have originally?" (2) **Constant difference:** "Mary saved €117 and Suzanne €36. After both earned the same amount, Mary's savings doubled Suzanne's. Each earning?" (3) **Three-party constant total:** "Three siblings share 240 sweets in ratio 5:3:2. The eldest gives 1/5 of his to the middle, who gives 1/4 of his (new total) to the youngest. Final counts?" (4) **Units and parts:** "Ali:Billy money = 2:1. After Ali saves €60 more and Billy spends €150, ratio becomes 4:1. Ali's original amount?"

**Parameterisation.** Two parameter axes: (a) initial ratio in lowest terms, (b) transfer amount or new ratio chosen so that the unit value is a positive integer. The structural-pattern tag (constant-total / constant-difference / one-party-constant / units-and-parts) should be a discriminator in the YAML so each pattern can be sampled deliberately.

**Why it matters for AI benchmarking.** This is the single highest-value family in this report. The Singapore bar-model invariant pattern is the canonical example of reasoning that GSM8K's "no variable required" rule excluded — it requires *recognizing* a conservation law before any computation. Mirzadeh et al.'s NoOp results, Hosseini et al.'s Compositional-GSM, and Yan's blog analyses all converge on this pattern as a reliable LLM weakness. Models routinely treat each transfer as independent and lose conservation. Five sub-patterns (constant-total, constant-difference, one-party-constant, units-and-parts, repeated-fraction-of-remainder) each test a distinct invariant-identification skill.

**Predicted GSM8K overlap.** **Low.** Surface tokens (people sharing money, marbles, stickers) overlap heavily with GSM8K, but the structural requirement to identify and exploit an invariant is precisely what GSM8K excluded. **No twist needed; the invariant requirement is the twist.**

---

#### P-SP2. `sequential_purchase` — multi-stage purchase with state changes
**Target cells.** New family `sequential_purchase` at K5–K10 (does not exist); secondary fill of decimals K7+, percentages K7–K10.

**Structural skeleton.** A buyer makes a sequence of 3–5 purchases. Each purchase modifies a budget, a remaining count, or a discount tier eligibility. Includes tier crossings (e.g., bulk discount kicks in after N items), conditional branches (if remaining > X then buy variant A else variant B), and end-state queries (final budget, total items, was the discount tier reached).

**Source.** Netherlands wiskunde A (Realistic Mathematics Education chained-context problems); CCSS HSA-CED + modeling; Singapore O-level real-world contexts; Sweden Mat 1a (vocational financial reasoning).

**Step structure.** 7–10 steps: track budget after each transaction, check tier conditions, adjust per-unit price when tier crossed, sum totals, answer multi-part query.

**Difficulty tier.** Medium (3-stage linear chain), hard (4–5 stages with tier crossing or conditional branch).

**Examples.** (1) "A shopper has €120. Stage 1: buys 3 shirts at €18.50 each. Stage 2: with remaining budget, buys jeans at €34, then a belt at €12. Stage 3: at checkout, discount of 8% applies if total before discount exceeds €100. Final amount paid; remaining budget?" (2) "A school orders supplies. First 50 notebooks cost €1.20 each; 51st through 100th cost €1.05 each; from 101st onward €0.90. Total cost for 130 notebooks?" (3) "A family books a trip: flights €230 each for 4 people; hotel €85/night for 6 nights with a 12% discount if booked together with flights; meals budgeted at €40/day total. Total cost? If a 5th person joins, how much extra?"

**Parameterisation.** Three structural axes: (a) number of stages (3–5), (b) presence of a tier crossing, (c) presence of a conditional branch. Numbers chosen so that the tier-crossing is a meaningful event, not always triggered.

**Why it matters.** Tests *state-tracking across many transactions* — the closest GSM8K-style pattern made significantly harder by tier-crossings and conditional logic. Hosseini et al. (Compositional-GSM) showed that chained problems collapse LLM accuracy even when each step is solvable individually. The tier-crossing variant in particular is structurally absent from GSM8K's "buy X items at $Y each" template.

**Predicted GSM8K overlap.** **Medium.** Surface form is recognizable shopping-arithmetic territory. **Twist required:** every `sequential_purchase` template must include at least one of (i) a tier crossing where per-unit price changes mid-purchase, (ii) a conditional branch ("if budget ≥ X then …"), or (iii) a dependency where stage k+1's parameters are derived from stage k's outcome (chained like Scheherazade). Templates that are simply "buy A, buy B, buy C, find total" should be rejected as GSM8K-equivalent. Crucially, **avoid the "$20 change" anti-pattern**: never let a sequential_purchase end with "she paid with a $X bill, find change" — that is the single highest-similarity pattern in the corpus already.

---

#### P-SP3. `rate_time` — work, pipes, and relative motion
**Target cells.** New family `rate_time` at K6–K10 (does not exist); secondary fill of measurement.time K7–K10 with non-clock-reading content.

**Structural skeleton.** Two or more agents operate at different rates on the same task. Find combined time, time at which one overtakes the other, time at which a pipe-fed tank fills/empties given simultaneous inflow and outflow, distance or time before two travellers meet. The Japanese 仕事算 / 旅人算 / 流水算 pattern.

**Source.** Japan Course of Study (旅人算, 仕事算, 流水算, 通過算 traditions); Singapore 4052 §N4 (rate-of-work, simultaneous equations); Indian aptitude tradition; Russian olympiad. Confirmed absent from GSM8K by the structural-gap analysis.

**Step structure.** 5–8 steps: convert each rate to a per-unit-time fraction (1/T form), add for combined operation or subtract for opposing, set up an equation in time, solve, interpret. Mid-task variants ("worker A starts alone for 2 h, then B joins") add 2–3 steps.

**Difficulty tier.** Medium (two agents, combined rate), hard (three agents with one negative rate; or mid-task rate change reducing to a tsurukame on time).

**Examples.** (1) **Pipes:** "Pipe A fills a tank in 12 h, pipe B in 9 h, pipe C drains it in 18 h. With all three open, time to fill from empty?" (2) **Workers, mid-task:** "Anna can paint a fence in 6 h, Ben in 4 h. Anna starts alone; Ben joins after 1 h. Total time to finish?" (3) **Relative motion (旅人算):** "Two cyclists start 36 km apart, riding toward each other at 14 km/h and 22 km/h. When and where do they meet? If the slower one had a 30-min head-start, how does the meeting point shift?" (4) **Train passing (通過算):** "A 120 m train travels at 72 km/h. Time to fully pass a 480 m platform?"

**Parameterisation.** Choose rates whose reciprocals share a small LCM (e.g., 4 and 6 → LCM 12 → combined rate 5/12). The Japanese-source variants (mid-task rate change, opposing direction with current, train length) provide structural diversity beyond simple combined-rate.

**Why it matters.** Reciprocal-rate addition is excluded by GSM8K's mental-arithmetic constraint and is identified across multiple analyses (the Japanese tokushuzan tradition; Indian aptitude texts; Mirzadeh et al.) as a reliably hard pattern for LLMs. The 通過算 (train-length) variant in particular tests the "extent of moving object" insight that GSM8K never invokes.

**Predicted GSM8K overlap.** **Low.** GSM8K's distance = rate × time is single-mover; combined-rate problems (especially with negative rates or train length) are essentially absent.

---

#### P-SP4. `compound_growth` — recursive percentage change with conditional events
**Target cells.** Existing thin family `compound_growth` (8 templates K7–K11), needs structural expansion at K8–K12; secondary fill of percentages.compound_interest at K10–K12 (currently nonexistent).

**Structural skeleton.** A quantity changes by a stated rate per period over multiple periods. Variants: (i) constant rate over n periods (geometric), (ii) varying rates per period (e.g., +5%, then +3%, then −2%), (iii) compound interest with a recurring deposit (annuity), (iv) "find the period after which the quantity exceeds/falls below a threshold" (inequality on n).

**Source.** Finland MAA9 (talousmatematiikka) and MAB6/MAB7; Estonia VIII kursus (liitprotsent); Norway LK20 1P personlig økonomi; Sweden Mat 1a (förändringsfaktor); CCSS HSA-SSE.B.4 (geometric series for mortgage / annuity); Singapore 9758 §2 (loan amortization); Japan Math II §10.

**Step structure.** 6–10 steps: identify the rate(s) per period, write the multiplicative factor (or sum of factors for annuity), apply over n periods, solve for the unknown (could be the final amount, the rate, the period count via logs, or the deposit size).

**Difficulty tier.** Medium (constant rate, find final), hard (variable rates; annuity recurrence; period-count via log inequality).

**Examples.** (1) "A €5 000 deposit earns 3.4% annual interest compounded quarterly. Balance after 5 years?" (2) "A car loses 18% of its value the first year, then 12% each subsequent year. After how many years does it first drop below half its original value?" (3) **Annuity:** "An investor deposits €200 at the start of each month into an account paying 0.4% per month, compounded monthly. Balance after 10 years?" (4) **Inflation chain:** "A salary rose 6%, 4%, then 3% over three years. By how much above pre-raise has it grown overall? What is the equivalent constant annual rate?"

**Parameterisation.** Rates and periods chosen so that key answers are clean: e.g., compound factor 1.05 over 10 years yields ≈ 1.62889; annuity formulas can be parameterised with monthly rate i and n months chosen to give round-number future values.

**Why it matters.** Compound growth over many periods exercises the multiplicative composition skill that single-step percentage problems do not. The variable-rate and annuity variants force the model away from the "+r% three times means +3r%" misconception. The "find n such that A·b^n > T" variant demands log-and-inequality reasoning, doubly absent from GSM8K.

**Predicted GSM8K overlap.** **Medium for the constant-rate single-period variant** — that pattern resembles GSM8K compound-interest problems. **Twist required:** every compound_growth template at K8+ must include at least one of (a) variable rate per period, (b) recurring deposit (annuity), (c) inequality "find n such that …", or (d) a non-monetary domain (population, radioactive decay, drug elimination half-life). Reject straight "P(1+r)^n find A" templates as too GSM8K-adjacent.

---

#### P-SP5. `area_perimeter_chain` — composite shapes with multi-step area/perimeter/volume reasoning
**Target cells.** New named family `area_perimeter_chain` (currently exists only as the misnamed `geometry.area_composite`, 4 templates); fills geometry.perimeter K7+ (essentially empty), geometry.area K7 + K9–K12.

**Structural skeleton.** A composite figure is built from rectangles, triangles, semicircles, and circular sectors. Compute (i) total area, (ii) perimeter, and (iii) one chained quantity such as cost of fencing, cost of paving, or volume when extruded. Variant: an inverse problem — given the area or perimeter, find the unknown dimension.

**Source.** Singapore 4052 §G3; Japan Course of Study 中学校 §図形 (extended); CCSS HSG-GMD + HSG-MG modeling; Estonia põhikool §73; Norway LK20 grade 10.

**Step structure.** 6–9 steps: decompose, compute each region's area, sum (subtracting any cut-outs), compute the boundary perimeter (which is *not* the sum of all boundaries, since interior segments cancel), apply the chained step (cost, volume, scale), state.

**Difficulty tier.** Medium (rectangle + semicircle, or L-shape), hard (rectangle with circular cutouts, or composite with sector and tangent-line constraints).

**Examples.** (1) "A garden is shaped as a 24 × 18 m rectangle with two semicircular bays of diameter 6 m on the long sides. Area? Perimeter? Cost of paving at €38 per m²?" (2) "An L-shaped patio measures 12 m along the front, 9 m along one side, with a 5 × 4 m corner missing. Compute area and total perimeter; cost of fencing the perimeter at €22/m." (3) **Inverse:** "A composite figure of a square topped by a semicircle has total perimeter 8π + 24 m. Find the square's side length and total area in exact form."

**Parameterisation.** Use π = 22/7 or a rational approximation for "medium" tier; require exact form involving π for "hard." Carefully parameterise the inverse variant so that the inversion yields a clean answer.

**Why it matters.** The perimeter-of-a-composite is the canonical insight problem — students who add all boundary lengths get the wrong answer because internal segments don't bound the exterior. This *recognition* step is distinct from arithmetic. The chained step (cost, volume) ensures the problem is multi-stage. CCSS HSG-MG.A explicitly flags this density-and-modeling axis as priority modeling content.

**Predicted GSM8K overlap.** **Low.** Composite geometry is largely absent from GSM8K.

---

## 4. Structural diversity beyond topic coverage

The taxonomy axes above are necessary but not sufficient. The corpus also needs to test reasoning *patterns* that cut across topics. The structural patterns below should be tagged as orthogonal attributes on every new template (a `structural_tags` field in YAML), so that coverage can be measured along the structural axis as well as the (grade × topic) axis.

### Structural patterns to require across the new corpus

| Pattern | Description | GSM8K coverage | Priority families |
|---|---|---|---|
| **Invariant tracking** | A quantity (total, difference, one party's amount) is conserved across a transformation; recognizing this is the key step | Excluded by guidelines | P-SP1, P-G3 (water transfer) |
| **Working backwards** | Final state given; reconstruct initial. Operations chained including additive offsets ("spent 1/3, then $20 more, then 1/4 of remainder") | Largely excluded | P-A2 (formula inversion), P-SP1 (repeated fraction-of-remainder), P-A5 (find n) |
| **Inverse problems** | Given the output of a function, find the input | Largely excluded | P-A2, P-G4 (find point given constraints), P-SP4 (find rate) |
| **Conditional / case-split** | Solution depends on which interval a parameter lies in | Excluded by guidelines | P-A4 (break-even), P-SP2 (tier crossing), P-S2 (Bayes branches) |
| **Optimization** | Find max/min subject to constraints | Excluded | P-A3 (vertex of parabola), P-G3 (cone-funnel timing), P-S3 (combinatorial max) |
| **Constraint satisfaction** | Find values satisfying multiple simultaneous conditions; possibly enumerate all | Mostly excluded | P-A1 (linear systems), P-N1 (CRT), the いもづる Diophantine variant |
| **Comparison / decision** | Which option is cheaper / faster / better, by how much, under what conditions | Sometimes single-shot, never break-even | P-A4, P-SP2 (compare two purchase paths), P-SP4 (compare investment options) |
| **Multi-rate combination** | Two or more rates combine reciprocally (work, pipes, currents) | Almost absent | P-SP3 |
| **Mixture / mass conservation** | Concentration changes via mixing, evaporation, or replacement; salt mass conserved | Almost absent | P-G3 (water transfer); add new sub-family `mixture` under arithmetic.* or numbers.* |
| **State tracking across N stages** | Budget, inventory, position updated through 4+ transactions, each depending on previous | Limited (GSM8K problems max ~8 steps with no real state-coupling) | P-SP2, P-SP4 (annuity recurrence), P-SP5 (chained area/cost/volume) |
| **Off-by-one / boundary** | Fence-post errors, train-length passing, equally-spaced stations | Rarely tested | One template per spec-mandated family with this structural tag |
| **Distractor robustness** | Problem contains an irrelevant-but-plausible sentence ("the bus has 40 seats" when bus capacity is irrelevant) | Mostly absent | A 10–15% sample of all new templates should include a NoOp distractor variant |
| **Under-specification** | Problem has missing information; correct answer is "cannot be determined" or requires a reasonable assumption | Excluded entirely | A small (5%) explicit set of "trick" templates per family |

### Two specific recommendations on the structural axis

**Add a NoOp distractor variant to ~10% of new templates.** Mirzadeh et al. 2024 showed that one irrelevant clause causes 30–65 pp accuracy drops on frontier models. This is the single highest-leverage structural intervention available: it's cheap to add (one extra clause per template), it dramatically increases discriminative power, and it tests a robustness property GSM8K wholly lacks. The clause should be plausible-but-irrelevant (e.g., in a pipe-filling problem: "The tank is painted blue and was installed in 2018"), not obviously off-topic.

**Add paired counterfactual instances for ~20% of new templates.** Two instances of the same template with one numerical or structural difference; correctness on both should correlate. RV-Bench (arXiv 2501.11790) shows pass@1 vs all-of-5 random instances diverges sharply for current models. This is the best available signal that a model has learned the *structure* rather than memorised one instance.

---

## 5. Priority recommendations for the coding agent

Given the user's coding agent will produce YAML templates from this artifact plus the prior 8-curriculum research, the priority ordering should be driven by the coverage data (where the holes are biggest and bridge value highest), not by curricular intuition (which would tend to over-emphasize K11–K12 specialty content).

### P0 — build first, in this order

1. **P-SP1 `multi_person_sharing`** (12–18 templates across K6–K10, four sub-patterns). This is the single highest-leverage proposal: spec-mandated, structurally novel against GSM8K, fills a missing topic axis, bridges the K6 mass to the thin K7+ tail, and exercises invariant-recognition reasoning that no other family tests as cleanly.
2. **P-SP3 `rate_time`** (10–15 templates across K6–K10, three sub-patterns: combined work, mid-task rate change, relative motion). Spec-mandated, currently nonexistent as a topic, and Japanese 仕事算/旅人算 patterns are confirmed absent from GSM8K.
3. **P-SP5 `area_perimeter_chain`** (10–14 templates across K5–K10). Spec-mandated, the existing 4 templates are misnamed and incomplete; bridges to the K9–K12 geometry desert.
4. **P-A1 linear-systems word problems** (8–12 templates across K7–K10). Fills the most critical algebra empty cell (K9/K10 algebra.equations entirely empty); the 2-variable requirement is GSM8K-novel by design.
5. **P-G1 right-triangle / Pythagoras** (8–10 templates across K8–K10). Fills the entire K8+ geometry.right_triangle column, which is currently empty.
6. **P-SP2 `sequential_purchase` with mandated structural twist** (8–12 templates across K5–K9). Spec-mandated; must include tier crossing, conditional branch, or chained dependency in every template — *not* a flat "buy A, buy B, find total" pattern. Reject any template that resembles "$20 change" anti-pattern.

P0 yields ~56–81 templates. Combined with P0–P0 structural-tag discipline (require `structural_tags` field; require ~10% NoOp variants), this alone meaningfully changes the corpus shape: K7–K10 templates roughly double, three of five spec-mandated families come into existence properly, and structural diversity gets explicit measurement.

### P1 — build next

7. **P-SP4 `compound_growth` with structural twists** (8–12 templates K8–K12). Spec-mandated; the existing 8 templates are thin and need variable-rate, annuity, inequality-on-n, and non-monetary-domain variants.
8. **P-S2 conditional probability and Bayes-lite** (8–10 templates K7–K11). Fills the probability column which is essentially empty across the entire corpus.
9. **P-A3 quadratic word problems** (6–8 templates K9–K10). Fills algebra.equations K9/K10 emptiness with structurally novel content.
10. **P-A2 algebraic-expression manipulation with formula change-of-subject** (8–10 templates K7–K10).
11. **P-G3 composite-solid volume with conservation** (6–8 templates K7–K10). Tests the water-transfer conservation pattern, structurally distinct from area_perimeter_chain.
12. **P-S1 grouped-data statistics** (6–8 templates K8–K11). Fills the median/mean/dispersion empty columns.
13. **P-A4 inequality word problems / break-even decisions** (6–8 templates K7–K10). Tests case-split reasoning.

P1 yields a further ~48–64 templates and brings statistics, probability, and percentages into a defensible state.

### P2 — build last

14. **P-G2 trigonometry** (6–8 templates K10–K11).
15. **P-S4 binomial distribution** (5–7 templates K11–K12).
16. **P-S5 hypothesis testing** (5–7 templates K11–K12).
17. **P-G4 coordinate geometry** (5–7 templates K9–K11).
18. **P-N1 modular arithmetic** (5–6 templates K7–K10).
19. **P-N2 GCD/LCM applied** (4–5 templates K7–K9).
20. **P-A5 exponential and log equations** (5–7 templates K10–K12).
21. **P-S3 combinatorics** (5–7 templates K8–K11).
22. **P-M1 multi-step unit conversion / dimensional analysis** (5–6 templates K7–K11).

P2 fills out the long tail and pushes K11–K12 from 12 templates to ~35–40, making upper-grade evaluation actually feasible.

### Cumulative effect if the full P0–P2 list is built

| Grade | Current | After P0 | After P0+P1 | After full plan |
|---|---|---|---|---|
| K6 | 210 | 215 (+5 cap) | 218 | 220 |
| K7 | 12 | 32 | 45 | 55 |
| K8 | 9 | 28 | 42 | 56 |
| K9 | 4 | 20 | 33 | 46 |
| K10 | 3 | 18 | 30 | 44 |
| K11 | 8 | 11 | 22 | 35 |
| K12 | 1 | 2 | 8 | 18 |

Targeting roughly 150–180 new templates total across the plan, with the K7–K10 bridge cells getting most of the new mass. Note the deliberate cap of +5 templates at K6 — see §6.

---

## 6. Don't build this

This section is the most important page in the report. The largest risk in the next authoring sprint is *not* under-building — the coding agent can grind out templates fast — it is mis-allocating the new templates to the easy zones and leaving the upper-grade hole intact. The coverage data already tells us where the temptations are.

### Hard rejections — do not author any of the following

**No new templates at K6 unless they introduce a structural tag absent at K6.** The corpus is 33% K6. K6 is the largest single grade by 81 templates. Any new K6 template that is "another fraction operation, another decimal arithmetic, another simple ratio, another shape area" is wasted authoring time. The only K6 additions worth making are templates that fill structural gaps at that grade — e.g., a K6 NoOp distractor variant, a K6 working-backwards problem, a K6 invariant problem that bridges into K7 algebra. Plain "more of the same" K6 content should be rejected at template-review time. Hard cap: +5 K6 templates across the entire P0–P2 plan.

**No new fractions.operations templates anywhere.** This is already the largest single bucket (36 templates). Adding more does not address any empty cell. If a problem requires fractions arithmetic, it should be tagged under another topic where the fraction operation is incidental (e.g., a percentages or ratios problem that happens to use fractions in computation).

**No new geometry.shapes templates at K2 or K6.** K2 has 18 templates and K6 has 9 templates in this topic. Both are saturated.

**No new arithmetic.* templates at K3–K6 unless filling a specific structural gap (NoOp, working-backwards, constraint-sat).** Arithmetic is mature in the corpus.

**No money-change-with-$X-bill templates anywhere in the new authoring.** This is the canonical highest-similarity-to-GSM8K pattern. The single contaminated template (`k6_medium_decimals_add_sub_01`) is exactly this. Templates ending with "she paid with a $X bill, find change" should be rejected on contamination grounds even at low Jaccard — the structural template is what GSM8K saturates.

**No basic-proportion templates ("if 3 lbs cost $9, how much for 7 lbs") at any grade.** This is the second-highest GSM8K pattern; ratios.* already has a 0.044 mean similarity score, which is the highest of any domain. The new ratio templates should be bar-model-invariant or compound-rate problems (P-SP1, P-SP3), not basic proportionality.

**No single-mover distance = rate × time templates at any grade.** Replace with multi-rate `rate_time` content under P-SP3.

**No "X items at $Y each, plus tax" templates without a structural twist.** This is the top GSM8K template by frequency. If the new template would resemble it, it must include either a tier crossing, a chained dependency, or a non-money domain.

### Resist the temptation pattern

The temptation, when looking at the heatmap, will be to fill cells that *look* easy to fill — K6 percentages, K6 ratios, K7 algebra equations with the simplest possible word problem, K8 geometry with another rectangle area. These cells will look "filled" on the heatmap but will not improve the corpus's value as a benchmark, and may actively *raise* the GSM8K-overlap mean by adding more shopping-arithmetic surface tokens.

The right mental model is: **for every new template, the question to ask is not "does this fill a cell?" but "does this exercise a reasoning pattern the corpus does not yet test, at a grade where the corpus is thin?"** A K9 algebra.equations template that is just "John bought 3 apples and 2 oranges for $7" is not progress. A K9 algebra.equations template that is the bar-model invariant variant from P-SP1, with a tier-crossing structural twist, is.

### One quantitative check

Before each new template is committed, run two cheap metrics:

1. **Jaccard 5-gram similarity to GSM8K.** Reject if max-sim > 0.10. Flag for review if > 0.06.
2. **Structural-tag count.** Reject if the template has zero structural tags from the §4 list. The structural tags are the load-bearing axis of corpus value.

These two checks alone would prevent the most likely failure mode of the next authoring sprint.

---

## 7. Where the proposals might fail

Three honest concerns about this plan, in decreasing severity.

**The bar-model invariant family (P-SP1) is hard to author well at scale.** The structural variety within P-SP1 (constant-total, constant-difference, one-party-constant, units-and-parts, repeated-fraction-of-remainder) is wide, and templates that don't carefully control the invariant tend to collapse into trivial linear-systems problems. The coding agent should be given concrete invariant-tagged sub-templates per pattern, not a single P-SP1 template that tries to cover all variants. If only one pattern is built well, prioritize *constant-total transfer between two parties* — that's the highest-frequency Singapore pattern and the one most directly absent from GSM8K.

**The "structural twist" requirement on P-SP2 and P-SP4 creates authoring overhead.** It would be faster to write straight "buy A, buy B, find total" templates and straight "principal × (1+r)^n" templates. The cost discipline (mandate a structural twist on every template in these families, reject simple variants) should be enforced by the review pipeline, not left to the coding agent's judgment, because a coding agent optimizing for coverage will tend to take the shorter path. If review enforcement is impossible, drop P-SP4 from P0 entirely — better to have zero compound_growth templates than 12 GSM8K-equivalent ones.

**Hypothesis testing and binomial distribution (P-S4, P-S5) require numerical-table or function-evaluation steps that may not fit the corpus's text-only template format.** If z-tables or normal-CDF evaluation is not supported by the YAML / generator, these P2 items become harder to author and may need to be replaced by inference-and-interpretation templates that give the test statistic and ask only for the conclusion. Confirm template-format support for these computations before scheduling P2.

---

## 8. Conclusion

The GSM8K contamination data is a green light, not a finding to debate further: the corpus is genuinely low-overlap and the only contaminated template is the canonical money-change pattern, which simply needs to be removed or restructured. The real question is whether the next authoring sprint pulls the corpus *up* into K7–K12 with structurally diverse content, or *out* sideways into more K6 mass. The coverage data is unambiguous about which is needed.

The five spec-mandated families (P-SP1 through P-SP5) carry the largest single share of value. Three of the five don't exist as topic names yet, and the two that do exist (`compound_growth`, `area_perimeter_chain`) are misnamed or thin. Building these well — particularly `multi_person_sharing` with the bar-model invariant pattern and `rate_time` with the Japanese tokushuzan reciprocal-rate pattern — would simultaneously fill empty cells, satisfy the spec, raise the corpus's K7–K10 density by ~3×, and exercise reasoning patterns that frontier LLMs reliably fail.

The structural-tag discipline (§4) and the rejection rules (§6) matter as much as the proposals themselves. A version of this plan executed without the "no new K6 templates" rule and the "structural twist required" rule would yield 150 new templates that look great on a heatmap and barely move the corpus's actual benchmark value. A version executed *with* those rules yields a corpus that can credibly distinguish a model that has learned grade-school math reasoning from one that has memorized GSM8K.

Two final quantitative targets to anchor against: by the end of the P0 sprint, K7–K10 should hold ≥100 templates (currently 28), and ≥30% of all new templates should carry at least one of the structural tags {invariant, working-backwards, conditional, multi-rate, mass-conservation, NoOp distractor}. These two numbers, if hit, would represent a corpus that is meaningfully ahead of the current state and meaningfully ahead of GSM8K's structural footprint.