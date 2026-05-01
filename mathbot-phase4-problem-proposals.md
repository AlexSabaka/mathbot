# International curricula and problem proposals for mathbot

This report has two parts. **Part 1** synthesises K-12 mathematics curricula across eight education systems (Finland, Norway, Sweden, Estonia, Singapore, Japan, Netherlands, US Common Core), focused on grades 7–12 and the K6→K7 bridge. **Part 2** translates that into concrete, prioritised problem-family proposals for mathbot, organised by grade band, topic family, and the spec-mandated families (`sequential_purchase`, `rate_time`, `compound_growth`, `multi_person_sharing`, `area_perimeter_chain`).

The headline finding: **Singapore's bar-model problem types and Japan's G8 proof chains together cover ~80% of the multi-step reasoning territory mathbot needs at K7-K10**, and the Finland/Norway/Estonia upper-secondary syllabi map almost 1-to-1 onto K11-K12 needs (financial math, sequences/series, intro calculus, statistics with variance/SD). US Common Core is the right baseline taxonomy to anchor against, but its multi-step problems are systematically *shorter* than what mathbot needs — RME and Singapore are the better depth references.

---

# Part 1 — Curriculum overview and comparative analysis

## 1.1 Finland — POPS 2014 / LOPS 2019

**Headline:** Late but compact algebra entry, phenomenon-based learning, **financial math added as a compulsory module in 2019**, and almost no formal statistics dispersion until upper secondary.

Finland operates two stacked national curricula: **POPS 2014** for basic education (grades 1–9) and **LOPS 2019** for *lukio* (general upper secondary, grades 10–12, in force from 2021). Both are issued by the Finnish National Agency for Education (Opetushallitus). The pedagogical signature is **phenomenon-based learning** and seven cross-cutting **transversal competences**, plus a requirement that every school deliver at least one **multidisciplinary learning module (MLM)** per pupil per year. Programming is a curriculum strand from grade 1 onward.

**Scope and sequence — when topics enter:** Symbolic algebra is introduced in **grade 7**, about a year later than US/UK norms, but consolidated quickly: linear equations, **incomplete quadratic equations**, **systems of two equations** (graphical and algebraic), and **linear inequalities** are all in place by grade 9. Geometry by grade 9 includes similarity, congruence, the Pythagorean theorem, **right-triangle trigonometry**, **Thales's theorem**, and volumes of sphere/cylinder/cone. Statistics in basic education stops at "the concept of dispersion" — variance and standard deviation by name appear only in *lukio* MAA8 (long syllabus) or MAB5 (short syllabus).

**Lukio modules of interest:** *MAA9 Financial Mathematics* (NEW in 2019) explicitly covers arithmetic and geometric sequences, **compound interest**, and **loans (principal, instalment, annuity)**. *MAA8 Statistics & Probability* covers mean, variance, standard deviation, correlation, and linear regression. Calculus is delivered as a single compact module **MAA6 Derivative** rather than spiralled — a deliberate change from LOPS 2016 to free time for conceptual work.

**Multi-step emphasis:** Modest in the curriculum text itself; the heavy lifting happens in MLMs and textbooks. The curriculum is goal-oriented and terse, leaving substantial latitude to publishers (Otava, Sanoma Pro). For mathbot, Finland's *content list* is the cleanest grade-banded scope reference among Nordic systems, but its multi-step reasoning template comes more from Singapore/Japan/RME than from POPS itself.

## 1.2 Norway — LK20 (Kunnskapsløftet 2020)

**Headline:** Verb-driven, exploration-first curriculum where **multi-step reasoning is structurally embedded in the competence aims**; personal finance is pervasive from grade 10; calculus is restricted to the science (R) and social-science (S) tracks.

LK20, in force since August 2020, is built around six **kjerneelementer** (core elements): exploration & problem-solving, modelling & applications, reasoning & argumentation, representation & communication, abstraction & generalisation, and fields of mathematical knowledge. The defining shift from LK06 is **dybdelæring** (deep learning) — fewer, more-connected aims, with computational thinking and programming integrated from grade 5.

**Verb structure as a generator template:** A typical grade-10 aim reads "extract and interpret relevant information from texts related to **purchases, sales and different types of loans**, and use this to formulate and solve problems." The verb chain *extract → interpret → formulate → solve → evaluate* literally defines a 5-step word-problem template — and is one of the cleanest matches to mathbot's spec-mandated `sequential_purchase` and `compound_growth` families.

**Track structure:** Upper secondary branches into 1P (practical) / 1T (theoretical) at vg1, then practical (2P), social-science (S1/S2), or science (R1/R2). **The vocational 1P-Y track is differentiated by industry** — healthcare, construction, naturbruk, restaurant, technical/industrial — with the same math core wrapped in domain-specific contexts. This is a direct model for mathbot's "context-injection axis" over a fixed math kernel.

**Topic timing:** Variance and standard deviation enter as *spredningsmål* in **grade 8**, formalised in 2P and S1. Compound interest is explicit in the **grade-10 loans aim** and elaborated in 1P-Y, 2P, and S1. **Calculus first appears only in R1 (vg2 = grade 12)** for science track; practical-track students can finish school without ever meeting the derivative. Proof by induction lives in R2.

## 1.3 Sweden — Lgr22 / Gy11

**Headline:** The "five förmågor" framework foregrounds problem-solving and reasoning, but research shows ~79% of textbook tasks remain imitative; **standard deviation arrives late** (gymnasium Mat 2b/2c, age 16), and there is no dedicated financial-math course.

Sweden's compulsory-school curriculum **Lgr22** organises content into six recurring strands: number, algebra, geometry, probability & statistics, relationships & change, and problem-solving. The five competences (problem-solving, concept, method, reasoning, communication) are assessed across all grade levels — a clean rubric for benchmark tagging.

**When topics appear:** Algebra is introduced "functionally" (less symbol-manipulation-heavy than Estonia or Russia); polynomial manipulation and quadratics with discriminant are deferred to gymnasium **Mat 2**. Statistics in grades 7–9 stops at descriptive level (range, quartile, informal correlation). **Variance, standard deviation, and the normal distribution all enter at Mat 2b/2c**, later than Estonia (grade 9) or Norway (grade 8 informal).

**Gymnasium course track:** Mat 1a/1b/1c → 2a/2b/2c → 3b/3c → 4 → 5. Calculus introduction in Mat 3; trig identities, complex numbers, and integration techniques in Mat 4; discrete maths, induction, graph theory in Mat 5. **Index measures (CPI, growth factor)** are uniquely emphasised — a Sweden-specific multi-step template worth replicating.

**Critical gap:** Skolverket explicitly aspires to non-routine reasoning, but the Lithner / Bergqvist body of research finds Swedish textbooks dominated by procedure-copying. **Mathbot can directly fill this gap** for Swedish-aligned content by generating the multi-step reasoning items the textbooks underweight.

## 1.4 Estonia — Põhikooli / Gümnaasiumi riiklik õppekava

**Headline:** Estonia leads European PISA mathematics (510, 2022) on the back of **Davydov-school algebraic rigor introduced in grade 7**, mandatory master's-degree teachers, and judicious tech use; it is the most procedurally demanding curriculum in this set.

Estonia's structure is põhikool grades 1–9 + gümnaasium grades 10–12 with a **kitsas (narrow, 8 courses) vs lai (wide, 14 courses) matemaatika** split. Lesson allocation is among Europe's highest at 13 weekly math lessons in grades 7–9. PISA 2022 placed Estonia #1–2 in Europe, #7–8 worldwide, with the smallest socioeconomic-attainment gap in the OECD.

**Distinctively early formal algebra:** Following the Russian Davydov tradition, grade 7 covers polynomial arithmetic, identities, linear equations, and proportions; **grade 8 introduces quadratic equations with the discriminant, algebraic fractions, square roots, and systems of linear equations**; grade 9 brings linear/quadratic/inverse-proportion functions, circle geometry, **and variance and standard deviation**. By the end of basic school, an Estonian 9th-grader has covered material a Swedish student does not see until gymnasium Mat 2 (age 16).

**Lai matemaatika sequence (gümnaasium):** Number sets → equations and word problems → trigonometry → vectors → stereometry I → sequences and **mathematical induction** → exponential/logarithmic → **limits and derivative** → applications of derivative → **integral with applications** → stereometry II → **probability with binomial/normal distributions and hypothesis testing** → modelling. The wide track is one of the most demanding K-12 profiles in Europe.

**Pedagogical surprise:** Estonia ranks 72/79 in OECD frequency of teachers asking students to "interpret math in real-life contexts," yet outperforms heavily contextualised systems. The lesson: **rigorous symbol-manipulation foundations + judicious tech + olympiad culture** beats constant contextualisation. For mathbot, this argues for keeping a meaningful share of *abstract symbolic* multi-step problems alongside the contextualised ones.

## 1.5 Singapore — MOE Mathematics Framework

**Headline:** The single richest source of deterministic multi-step word-problem templates in this study. The **Pentagon framework + CPA progression + bar-model method** produces canonical problem types with explicit hidden-state representations that map almost 1-to-1 onto mathbot's needs.

The MOE Mathematics Framework places **problem-solving at the centre**, supported by Concepts, Skills, Processes, Metacognition, and Attitudes. The 2021 Primary syllabus organises around six "Big Ideas": Equivalence, Diagrams, Invariance, Measures, Notations, Proportionality — themselves a useful cross-topic tagging taxonomy. The pedagogy is **Concrete-Pictorial-Abstract (CPA)**: physical manipulatives → bar models → symbolic notation, iteratively per concept.

**The bar model as state representation:** Developed by Kho Tek Hong at CDIS in the 1980s. Introduced informally at P1–P2 (part-whole and comparison bars), formalised at P3 for two-step word problems, extended at P4 to fractions and four-operation chains, and at **P5–P6 becomes a full state-tracking diagram** — multiple bars represent before/after across transactions, with shading marking what has changed. By Sec 1 (G7), algebra takes over and bars are phased out, though strong students retain them as planning tools.

**Canonical multi-step problem types (these become mathbot templates directly):**
- **Fraction-of-Remainder** (P5/P6): spend f₁ of total, then f₂ of remainder, then receive cash, with a final/initial ratio constraint. State sequence: initial → after₁ → after₂ → after_gift.
- **Constant-Total / Internal Transfer** (P5/P6): A gives to B; sum invariant; equalise via LCM of part counts.
- **Constant-Difference / Age Problems** (P5/P6): both quantities change by equal absolute amount; difference invariant.
- **Constant-Part / Repeated Identity** (P5/P6): only one quantity changes; the other anchors the algebra.
- **Units-and-Parts** (P6): two distinct unit types in the same problem (e.g., adults:children ratio + boys:girls ratio).
- **Assumption / Excess-and-Shortage** (P5/P6): the chickens-and-rabbits family solved by replacement substitution.
- **Sequential-Purchase / Multi-stage Rate** (P5–Sec 1): tanks filling at different rates with geometric volume constraints.

**Secondary scope (Sec 1–4, codes 4052/4049):** Sec 1 introduces formal algebra, ratio/proportion, rate and speed; Sec 2 brings indices, quadratics, simultaneous equations, similar/congruent figures, and probability of single events; Sec 3 covers trigonometry (right-tri + sine/cosine rule), circle properties, arc/sector/segment, coordinate geometry; **Sec 4 adds vectors in 2D, matrices, set notation, and crucially standard deviation** for grouped/ungrouped data, cumulative frequency, and box-and-whisker plots. **A-Math 4049** is the calculus elective at Sec 3-4 (differentiation, integration, kinematics, exponentials, logs, plane-geometry proofs).

**JC / A-Level H2 Mathematics 9758:** Pure (functions, sequences/series including method of differences and induction, vectors in 3D, complex numbers, calculus including parametric, Maclaurin series, integration by parts, **first-order ODEs applied to population growth, radioactive decay, Newton's cooling**) + Probability/Statistics (binomial, normal, sampling distributions, **one-sample z and t hypothesis tests**, correlation and linear regression). Every paper includes one **applications question** in real-world context worth ≥12 marks — the single best K12 model for an AI multi-step benchmark item.

## 1.6 Japan — Course of Study (Gakushū Shidō Yōryō)

**Headline:** Multi-step reasoning lives primarily in **G8 geometric proof chains** and in **open-ended problems with multiple correct methods or answers**, orchestrated through *neriage* (whole-class comparison of solution methods). Statistics expanded substantially in the 2017–2018 reform; computational fluency remains foundational.

The 2017 (elementary/JHS) and 2018 (HS) revisions, fully in force 2020–2022, dramatically expanded statistics to address "Society 5.0" data needs: **histograms and box plots moved earlier (G6 and G8 respectively), the PPDAC investigation cycle entered the curriculum, and hypothesis testing became mainstream HS content via Math B**.

**Pedagogy — structured problem-solving (TTP):** The canonical 45-minute lesson is built around one rich problem and four phases: *hatsumon* (key question) → *kikan-shidō* (between-desks observation) → ***neriage* (polishing-up)** → *matome* (summary). Neriage is the heart: the teacher orchestrates students to present multiple solution methods in deliberate order, building new mathematical knowledge through comparison. *Lesson study* (jugyō kenkyū) sustains this nationally; *kyōzai-kenkyū* is the prep phase. The **open-ended approach** (Shimada, Becker, Nohda) provides three task types: open process (many ways to solve), open end-product (many correct answers), and open extensions (problem-posing).

**The G8 proof chain — mathbot gold:** Course of Study mandates formal proof gradually mastered by end of G8. The standard sequence: vertical angles → corresponding angles ⇒ parallel lines → alternate interior angles ⇒ parallel lines → co-interior sum 180° → triangle interior sum 180° → exterior-angle theorem → polygon angle sum → polygon exterior sum. Each is a multi-line two-column or paragraph proof. **This is the cleanest deductive multi-step template in any K-12 curriculum globally** and is heavily underweighted in mathbot's current taxonomy.

**HS topic mapping:** Math I (compulsory G10) covers quadratics with inequalities, sin/cos rule, and **mean/variance/SD/correlation/scatter plots — earlier than Singapore (Sec 4) or Sweden (Mat 2)**. Math II/B (G11) introduces calculus on polynomials + sequences with induction + statistical inference. Math III (G12 STEM) covers full limits, derivatives, integration with arc length and volume of revolution, and the complex plane. Math C reorganises vectors and conic sections.

**Procedural fluency stays foundational:** the *kuku* multiplication table memorised by end of G2, soroban training, and clean algebraic manipulation drills coexist with open-ended work — explicitly because procedural fluency frees cognitive capacity for conceptual neriage. A useful design principle for mathbot: do not artificially exclude single-step procedural items; rather, **scale step counts across the 1–10 range and tag them.**

## 1.7 Netherlands — Realistic Mathematics Education (RME)

**Headline:** RME's defining contribution to mathbot is the **multi-paragraph contextual chain**: a single rich situation with 4–6 sub-questions requiring parse → model → compute → interpret. This is structurally longer than Common Core's typical multi-step item.

RME originated at the Freudenthal Institute (Utrecht). Hans Freudenthal positioned mathematics as **a human activity to be reinvented**, not transmitted; "realistic" derives from *zich realiseren* ("to imagine") — contexts must be experientially real, which can include fantasy or within-mathematics situations. The three core design heuristics are **guided reinvention through progressive mathematization** (horizontal: situation → math; vertical: math → higher abstraction), **didactical phenomenology** (concepts come *after* the phenomena that demand them), and **emergent modeling** — the *model-of → model-for* transition where, e.g., an empty number line first stands for a measuring tape (model-of) and gradually becomes a tool for arithmetic reasoning generally (model-for).

**System structure:** Primary groep 1–8 (ages 4–12) followed by tracking into VMBO (vocational), HAVO (general higher), or VWO (pre-university). HAVO/VWO students choose **Wiskunde A/B/C/D** in upper years: A is data/statistics/financial-modelling for economic-social profiles; B is formal calculus and proof for STEM; C is logic/descriptive-stats for culture profile; D is enrichment (linear algebra, complex numbers, dynamical systems).

**Multi-step characteristic:** Wiskunde A/B exam items famously open with a 3–10-line context paragraph (wind turbines, drug clearance, tariff structures) followed by 4–6 sub-questions. **This is the longest multi-step prompt structure in any curriculum here** and a direct template for the upper-end of mathbot's 7–10 step range. Critics from Van de Craats and others (the Dutch "math war") have pushed back since 2007 on alleged loss of algebraic fluency — modern Dutch problems blend RME chains with explicit procedural drill.

**Topic coverage:** Statistics in Wiskunde A includes binomial, normal, hypothesis testing, correlation; Wiskunde B has full differential and integral calculus on VWO. Financial math is explicit in Wiskunde A (interest, growth, tax). Calculus is required in VWO Wiskunde B.

## 1.8 United States — Common Core State Standards (CCSSM)

**Headline:** The right anchor taxonomy for mathbot, but **typical CCSSM multi-step items are shorter** (1 paragraph, 1–3 steps) than Singapore P5/P6 or Dutch Wiskunde A items. The eight Standards for Mathematical Practice (especially MP1, MP4, MP7, MP8) provide the cleanest rubric for benchmark tagging.

CCSSM (2010, NGA + CCSSO, adopted by 45+ states) is consensus-driven and pragmatic, not philosophically positioned. Three "key shifts": **Focus** (narrow per-grade content), **Coherence** (vertical progressions), **Rigor** (equal intensity on conceptual understanding, procedural fluency, and application). Eight Standards for Mathematical Practice apply identically at every grade.

**The K6→K7→K8 algebra spine — the bridge mathbot needs to fill:**
- **6.RP**: ratio language, unit rates, percent as rate per 100.
- **7.RP.A.3**: **multistep ratio and percent problems** — simple interest, tax, markups/markdowns, gratuities, commissions, fees, percent error. *This is the single canonical CCSS multi-step standard and the primary K7 anchor for mathbot.*
- **7.EE.B.3**: multi-step problems with positive and negative rationals, **assessing reasonableness**.
- **7.NS.A.3**: multi-step real-world problems with rational numbers.
- **7.G**: scale drawings, cross-sections, area/circumference of circles, angle relationships, volume.
- **7.SP**: random sampling and inference; simple/compound probability.
- **8.EE.7–8**: linear equations (including no-/infinite-solution cases), systems of two linear equations.
- **8.F**: function definition, comparing across representations, constructing linear functions.
- **8.G.6–8**: Pythagorean theorem proof and applications including coordinate distances.
- **8.SP**: scatter plots, line of best fit, two-way frequency tables.

**HS spine:** HSA-CED (modeling with equations/inequalities), HSA-REI (solving methods), HSA-SSE (structural rewrites — including the famous 1.15^t = (1.15^(1/12))^(12t) for monthly rate), HSA-APR (polynomials, Remainder/Factor theorem). HSF-IF/BF/LE/TF for functions, including financial math via exponentials/logs. HSG-CO/SRT/C/GPE/GMD for transformation-based geometry. HSS-ID/IC/CP/MD for statistics and probability — the ★ Modeling category cuts across.

**What's missing from CCSSM relative to international peers:** Calculus (placed in AP/state 4th-year courses); formal mathematical induction; depth of geometric proof. Statistics is solid but enters the formal stats domain at HS rather than grade 8 (Estonia/Japan).

## 1.9 Comparative cross-reference — when topics enter

The single most useful artefact for mathbot's grade-tagging logic:

| Topic | Finland | Norway | Sweden | Estonia | Singapore | Japan | NL (HAVO/VWO) | US CCSS |
|---|---|---|---|---|---|---|---|---|
| Formal symbolic algebra | G7 | G8 | G7 (light) | **G7 (deep)** | Sec 1 (G7) | G7 | yr 1 sec (G7) | G7 (7.EE) |
| Linear systems (2 eqns) | G9 | G10 | G7–9 | G8 | Sec 2 (G8) | G8 | yr 2–3 sec | G8 (8.EE) |
| Quadratics with discriminant | G9 | G10 | Mat 2 (G11) | **G8** | Sec 2 (G8) | G9 | yr 3–4 sec | Algebra I |
| Pythagorean theorem | G7–9 | G9 | G7–9 | G8 | Sec 2 | G9 | yr 2 sec | G8 (8.G) |
| Functions (linear, quadratic) | G9 | G10 | Mat 1 (G10) | **G9** | Sec 2 | G8–9 | yr 3–4 sec | G8 (8.F) |
| Variance / standard deviation | Lukio (G11) | 2P/S1 (G12) | Mat 2 (G11) | **G9** + lai G12 | Sec 4 (G10) | **Math I (G10)** | Wisk A (G10–12) | HSS-ID |
| Compound interest | LOPS MAA9 (G11) | **G10** + 1P-Y/2P/S1 | Mat 1b (G10) | G7–9 applied | **P5 intro, Sec 1+** | Light (G5–6) | Wisk A | 7.RP.A.3, HSA-SSE |
| Calculus (derivative) | Lukio MAA6 (G11) | R1 (G12) | Mat 3 (G11) | Lai G11 | A-Math (Sec 4) / H2 JC | Math II (G11) | Wisk B (G11) | AP (post-CCSS) |
| Integral calculus | Lukio MAA7 (G11) | R1/R2 (G12–13) | Mat 4 (G12) | Lai G12 | H2 JC (G12) | Math III (G12) | Wisk B (G12) | AP |
| Hypothesis testing | LOPS MAA12 (opt) | S2 (G13) | Mat 5 (G12) | Lai G12 | H2 JC | **Math B (G11)** | Wisk A (G11–12) | HSS-IC |
| Mathematical induction | Lukio MAA11 (opt) | R2 (G13) | Mat 5 (G12) | Lai G11 | H2 JC | Math B (G11) | Wisk D (opt) | + standards |
| Formal geometric proof | Light G7–9; lukio | Light; weak in LK20 | Mat 2c (G11) | Lai G11–12 | A-Math (Sec 3–4) | **G8 — universal** | Wisk B | HS Geometry |
| Financial math (full) | LOPS MAA9/MAB6–7 (G11) | **Pervasive G10–13** | Mat 1b (G10) | Cross-curric. + applied | P5–H2 | Light | Wisk A | 7.RP, HSA-SSE |
| Programming integrated | **G1+** | **G5+** | G7+ (algebra) | Yes | Light in math | Light in math | Yes | Not in CCSSM |

## 1.10 Critical analysis — what each system does best, and what mathbot can learn

**Singapore wins for state-tracking word problems.** Nothing else in this set matches the bar-model-backed P5/P6 templates for structured multi-step reasoning with hidden state and clean integer/fraction answers. *Mathbot should treat the seven canonical bar-model types (Section 1.5) as P0 templates for K5–K8.*

**Japan wins for deductive proof chains and open-ended problems.** The G8 angle-theorem chain is the single best K-12 source of pure deductive multi-step reasoning (5–10 steps, each with a stated reason). The open-ended approach also suggests a benchmark category mathbot doesn't currently have: **problems with multiple correct answers or methods**, scored on justification quality rather than numerical match.

**Netherlands (RME) wins for long contextual chains.** Wiskunde A exam items show that 4–6-sub-question problems anchored in one rich context are pedagogically tractable for 16-year-olds. *Mathbot's 7–10-step problems should follow this structure*: one context, multiple sub-questions, with later questions depending on earlier answers (state propagation across sub-problems).

**Norway wins for the vocational context-injection axis.** The 1P-Y industry variants (healthcare, construction, naturbruk, restaurant, technical/industrial) demonstrate how to wrap a fixed math kernel in domain-specific contexts. *Mathbot should adopt this as a parameterisation axis* — same compound-growth template instantiated as savings, population, bacterial growth, depreciating equipment, radioactive decay, drug clearance, fuel costs.

**Estonia wins for symbolic-manipulation rigor.** Quadratic equations with discriminant by G8, polynomial division and rational expression simplification at G7–9, mathematical induction at G11 — abstractly rigorous symbolic items at earlier grades than Western peers. *Mathbot should not over-contextualise*: Estonia's PISA dominance with low contextualisation suggests that abstract symbolic multi-step problems carry their weight.

**Finland wins for goal-oriented brevity and the recent financial-math addition.** MAA9 / MAB6-7 give a clean compound-growth sequence (sequences → annuities → loans → real datasets) at G11–12 that maps directly to mathbot's `compound_growth` family.

**Sweden wins for the explicit competence rubric.** The five förmågor (problem-solving, concept, method, reasoning, communication) provide a near-direct mapping to mathbot's potential evaluation tags. *But Swedish textbooks themselves are weak on non-routine reasoning* — there's a content gap mathbot can fill.

**Common Core wins as the baseline taxonomy.** Standard codes (7.RP.A.3, HSA-CED, HSS-ID) give the cleanest grade-level anchoring. *Mathbot should label every template with at least one CCSS standard for benchmark interoperability.* But CCSS prompts are typically too short — mathbot should generate longer chains and use CCSS only as a topic anchor, not a length anchor.

**Where curricula disagree (and mathbot's call):** The biggest disagreement is on **statistics dispersion timing** (Japan/Estonia G9-G10, Netherlands/Singapore/Sweden G10-G11, Common Core HS, Finland G11, Norway informal G8 + formal G12). *Mathbot should introduce variance/SD at K9 minimum and place full treatment at K10–K11* — splitting the difference but biased toward earlier introduction, where the international evidence supports it. The second is **calculus**: Norway and US restrict calculus to advanced tracks at G12; Singapore (A-Math), Japan, Netherlands, and Finland push intro calculus to G11. *Mathbot should place introductory calculus at K11, with K12 as the depth target* — matching the international median.

---

# Part 2 — Problem proposals for mathbot

This section proposes concrete problem families for mathbot, organised by grade band and the spec-mandated families. Each proposal has the requested fields. **Proposals are tagged P0/P1/P2/P3** for prioritisation:

- **P0** — fills explicit cleanup-doc gaps (K7-K12 underrepresentation, spec-mandated families, K6→K7 bridge). Build first.
- **P1** — strong international curriculum coverage; fills K9-K12 area_perimeter_chain or K7-K10 compound_growth gaps.
- **P2** — rounds out coverage; useful for variety and benchmark robustness.
- **P3** — nice-to-have; only after P0–P2 are stable.

The proposals deliberately bias toward Singapore-bar-model state-tracking and RME-style contextual chains. Each is designed to generate **many concrete instances** through parameter randomisation. **Step counts** are stated as the multi-step depth; mathbot supports 1–10 but the sweet spot for these proposals is 3–7 steps.

## 2.1 K3-K5 gap-fillers (multi_person_sharing focus)

Cleanup doc explicitly flags **K3-K5 multi_person_sharing** as a conceptual gap. These are the foundation for K6+ ratio reasoning.

### Proposal 2.1.1 — Equal-share with remainder (multi_person_sharing) [P0]
**Concept:** N people share M items equally; some items remain undivided. Tests division with remainder, and the verbal interpretation of remainder ("each gets X, with R left over").
**Source curriculum:** Singapore P3 (division with remainder); Japan G3 (division algorithm); CCSS 4.OA.A.3.
**Multi-step structure:** 3 steps — total items, divide by N, identify remainder. State: total → per_person → remainder.
**Realistic contexts:** (a) cookies shared among a class table; (b) trading cards split among siblings; (c) marbles distributed in tournament prizes.
**Variable parameterisation:** N (3–8), total items M (chosen so M = qN+r with q ≥ 2 and 0 ≤ r < N), item type, character names from a diverse pool.
**Difficulty tier:** Easy (K3) when M ≤ 50; medium (K4) with M ≤ 1000.
**Why for AI benchmarking:** Tests whether the model correctly handles remainders without rounding or truncating — a known LLM failure mode at division boundaries.

### Proposal 2.1.2 — Unequal-share by stated rule (multi_person_sharing) [P0]
**Concept:** Three+ people share items by a stated rule like "A gets twice as many as B; C gets 5 more than A." Linear constraint resolution before formal algebra.
**Source curriculum:** Singapore P4–P5 (bar models); CCSS 4.OA.A.2 (multiplicative comparison).
**Multi-step structure:** 4 steps — interpret constraints, set up units (LCM), allocate, verify total.
**Realistic contexts:** (a) splitting shared chore money among siblings; (b) dividing donation supplies among classrooms; (c) allocating seeds among garden beds.
**Variable parameterisation:** number of sharers (3–5), comparison structure (multiplicative + additive offsets), totals chosen to yield integer answers.
**Difficulty tier:** Easy K4 (two-person multiplicative); medium K5 (three-person mixed); hard K5 (four-person with additive offset).
**Why for AI benchmarking:** Tests whether the model can translate a chain of natural-language constraints into a consistent allocation — a precursor to formal systems-of-equations reasoning that's easy to produce but hard to satisfy without explicit unit tracking.

### Proposal 2.1.3 — Sharing across two groups with rate (multi_person_sharing × rate_time) [P1]
**Concept:** Two teams share work; one team has more members but works fewer hours. Combines proportional reasoning with rate.
**Source curriculum:** Singapore P5 rate; CCSS 5.NF.B.7 (fractions in word problems).
**Multi-step structure:** 4–5 steps — compute team-A throughput, team-B throughput, total per period, total over duration, share per person.
**Realistic contexts:** (a) painting fence panels across two crews; (b) packing care packages at two stations; (c) harvesting apples in two orchards.
**Difficulty tier:** Medium K5.

## 2.2 K6→K7 bridge — pre-algebra to algebra

This is mathbot's thinnest band. The international consensus is that K6 is ratio-heavy (CCSS 6.RP, Singapore P6 ratio) and K7 is the formal-algebra entry point. Bridge problems should use **the same context and quantities** but solvable both with bar-model thinking (K6) and with a single-variable equation (K7).

### Proposal 2.2.1 — Ratio with internal transfer (multi_person_sharing) [P0]
**Concept:** A and B start with quantities in ratio p:q. A gives B an amount; new ratio is r:s. Find original quantities. Bar-model solvable; algebraically a 2-equation system.
**Source curriculum:** Singapore P5/P6 (constant-total bar-model); Estonia G7 (linear systems word problems).
**Multi-step structure:** 5 steps — identify invariant (total preserved), express both states in compatible units, equate, solve, verify with second ratio.
**Realistic contexts:** (a) Aisha and Ben's saved allowance; (b) library book counts at two branches transferring stock; (c) inventory at two warehouses.
**Variable parameterisation:** initial ratio (p:q), final ratio (r:s), transfer amount T, names from diverse pool. Constrain so original totals are integers ≤ 200.
**Difficulty tier:** Medium K6 (bar model); easy K7 (algebraic).
**Why:** Tests the *invariant-finding* skill — the single most underweighted reasoning move in current LLM benchmarks. GSM8K problems rarely require recognising what stays constant across a state change.

### Proposal 2.2.2 — Ratio with external transfer / age problem (multi_person_sharing) [P0]
**Concept:** Two people's quantities change by the same absolute amount (e.g., both get older by k years). Difference is invariant.
**Source curriculum:** Singapore P5 (constant-difference bar-model); a global classic.
**Multi-step structure:** 4–5 steps — identify difference invariant, set up unit equation, solve.
**Realistic contexts:** (a) ages of siblings; (b) annual savings goals; (c) heights tracked over years.
**Difficulty tier:** Medium K6, easy K7.

### Proposal 2.2.3 — Sequential percentage discount (sequential_purchase) [P0]
**Concept:** An item is marked up by p%, then discounted by q%, then has tax t% added. Show that order matters or doesn't (multiplicative commutativity).
**Source curriculum:** CCSS 7.RP.A.3 (canonical multistep percent); Norway grade 10 purchase aim.
**Multi-step structure:** 4 steps — apply markup, apply discount on new price, apply tax, compare to a one-step calculation.
**Realistic contexts:** (a) buying clothing on sale + sales tax; (b) car price negotiation with trade-in; (c) restaurant bill with service charge and discount voucher.
**Variable parameterisation:** base price, markup %, discount %, tax %; constrained so final price has at most 2 decimal places.
**Difficulty tier:** Easy K7 (3 steps), medium K7 (4 steps with verification), hard K8 (5+ steps with comparison statement).
**Why:** Tests multiplicative composition — LLMs often additively combine percentages. This is the cleanest test of that failure mode.

### Proposal 2.2.4 — Linear equation from word problem with negative coefficients (algebra) [P0]
**Concept:** Word problem requires setting up `ax + b = cx + d` where one side has a deduction (negative coefficient). Common in cost-comparison contexts (gym memberships, phone plans).
**Source curriculum:** CCSS 8.EE.C.7; Estonia G7; Norway G10.
**Multi-step structure:** 4 steps — set up equation for each option, equate, solve, interpret in context.
**Realistic contexts:** (a) two phone plans (one flat fee + per-minute, one higher fee + lower per-minute); (b) two gym memberships; (c) two car-rental plans.
**Difficulty tier:** Medium K7, easy K8.

## 2.3 K7-K9 expansion — the priority band

This is mathbot's heaviest underrepresentation (only 12 files combined currently). All proposals here are P0 unless noted.

### Proposal 2.3.1 — Compound percent change chain (compound_growth) [P0]
**Concept:** A quantity grows by p₁% in year 1, p₂% in year 2, p₃% in year 3 (mixed signs). Find final value and average annual growth rate.
**Source curriculum:** Norway grade 10 "growth factor ↔ exponential function" aim; Sweden Mat 1b index measures; Singapore Sec 1 percentage; CCSS HSA-SSE.B.3.c.
**Multi-step structure:** 5–6 steps — apply each growth factor sequentially, compute final, derive geometric mean, interpret.
**Realistic contexts:** (a) population of a town over 3 years; (b) value of a savings account with varying interest; (c) a small business's revenue.
**Variable parameterisation:** initial value, three percentage changes (mix of + and −, in range −20 to +30), constrained so final value is "nice" (integer or simple decimal).
**Difficulty tier:** Easy K8 (3 steps, all positive); medium K9 (mixed signs); hard K10 (with average growth rate).
**Why:** Tests sequential state update over multiple compounding events — exactly the kind of reasoning where models that memorise simple-interest formulas fail.

### Proposal 2.3.2 — Compound interest with periodic deposits (compound_growth) [P0]
**Concept:** Account starts at P, earns r% annually, plus a fixed deposit D at the end of each year. Find balance after N years.
**Source curriculum:** Finland LOPS MAA9; Norway 2P/S1; Singapore H1/H2 application context.
**Multi-step structure:** N+1 steps for N small (3-5); or 5 steps using the annuity formula at K11+.
**Realistic contexts:** (a) college savings plan; (b) retirement contributions; (c) emergency fund growth.
**Variable parameterisation:** P (1000–10000), r (1%–8%), D (100–2000), N (3–8 years for direct simulation; up to 30 for formula at K11+).
**Difficulty tier:** Medium K8 (3 years iterative); hard K9 (5 years iterative); easy K11 (formula).
**Why:** Multi-step iterative state-tracking with arithmetic; closed-form at higher grades. Distinguishes models that can iterate from those that pattern-match a single formula.

### Proposal 2.3.3 — Two-rate work problem (rate_time) [P0]
**Concept:** Person A completes a job in t_A hours alone; Person B in t_B hours. Together they work for x hours, then A leaves. How long until B finishes alone?
**Source curriculum:** Singapore Sec 1 rate; classic algebra word problem; Estonia G8.
**Multi-step structure:** 5 steps — compute individual rates, combined rate, work done together, remaining work, time for B.
**Realistic contexts:** (a) two painters on a house; (b) two pumps filling a pool; (c) two printers producing a print run.
**Variable parameterisation:** t_A, t_B chosen so that combined rate has clean LCM denominators; x chosen so remaining work is a clean fraction.
**Difficulty tier:** Medium K7, easy K8.

### Proposal 2.3.4 — Speed/distance with meeting and overtaking (rate_time) [P0]
**Concept:** Two travellers depart at different times with different speeds; find when/where they meet (or one overtakes the other).
**Source curriculum:** Singapore Sec 1 (speed); CCSS 7.RP; Japan G7 proportional relationships.
**Multi-step structure:** 5–6 steps — set up position functions, equate, solve for time, compute position, interpret in context.
**Realistic contexts:** (a) two cyclists on a trail; (b) freight and passenger trains on the same track; (c) hikers on different paces.
**Difficulty tier:** Medium K7 (same-direction overtake); hard K8 (head-on with different start times); hard K9 (with a stop).

### Proposal 2.3.5 — Sequential purchase with budget constraint (sequential_purchase) [P0]
**Concept:** Customer enters a store with budget B. Buys items in order, each at varying price; at some point cannot afford the next item. How much spent? How much left? Did optimal ordering matter?
**Source curriculum:** Norway grade 10 purchase aim; Sweden Mat 1a vocational; CCSS 7.NS.A.3.
**Multi-step structure:** 4–6 steps depending on item count — running total subtraction with affordability check.
**Realistic contexts:** (a) school supplies shopping with a list; (b) grocery run with a budget; (c) gift shopping for multiple recipients.
**Variable parameterisation:** budget, item prices (4–7 items), order, optional discount triggered at threshold.
**Difficulty tier:** Easy K7 (no discount), medium K8 (with bulk discount at threshold), hard K9 (with re-ordering optimisation question).
**Why:** Tests *running state* tracking under conditional logic — affordability check is a guard that LLMs sometimes skip.

### Proposal 2.3.6 — Multi-step area / perimeter chain — composite figures (area_perimeter_chain) [P0]
**Concept:** A rectangular room has a smaller rectangular alcove cut out (or added). Compute perimeter and area; then compute paint needed (with given coverage rate) and cost (with given $/can).
**Source curriculum:** Singapore P5 area; CCSS 6.G.A.1 + 7.G.B.6; Japan G6.
**Multi-step structure:** 5–6 steps — decompose figure, compute area_1, area_2, total area, divide by coverage to get cans (with ceiling), multiply by cost.
**Realistic contexts:** (a) painting an L-shaped room; (b) tiling a kitchen floor with a counter cutout; (c) carpeting a stage.
**Variable parameterisation:** outer dimensions, alcove dimensions, coverage rate, can cost; constrained so cans is a clean integer after ceiling.
**Difficulty tier:** Easy K7 (L-shape area only), medium K7 (with paint computation), hard K8 (with two paint colours and second wall).
**Why:** Composite-figure decomposition + ceiling function + unit conversion — three distinct reasoning moves chained together. **This directly fills the K9-K12 area_perimeter_chain gap.**

### Proposal 2.3.7 — Pythagorean chain in real context (area_perimeter_chain × geometry) [P1]
**Concept:** A rectangular field has a diagonal path; a fence is built along three sides plus the diagonal; compute total fence length, enclosed area on each side of the diagonal.
**Source curriculum:** Finland G7-9 Pythagoras; Norway G9; CCSS 8.G.B.7.
**Multi-step structure:** 4–5 steps — Pythagorean for diagonal, perimeter sum, area of each triangle, ratio.
**Realistic contexts:** (a) farmer dividing a field; (b) park designer with diagonal path; (c) sports facility layout.
**Difficulty tier:** Medium K8, easy K9.

### Proposal 2.3.8 — Linear function from two real-world data points (algebra/functions) [P0]
**Concept:** Cost is linear in quantity. Two data points given (e.g., "5 items cost $23, 12 items cost $51"); find the per-item cost and the fixed fee, then predict cost for n items.
**Source curriculum:** CCSS 8.F.B.4; Norway G10; Singapore Sec 1.
**Multi-step structure:** 4 steps — compute slope, compute intercept, write equation, evaluate at target.
**Realistic contexts:** (a) taxi fares (flag fee + per-mile); (b) phone plan; (c) catering quote (setup fee + per-guest).
**Difficulty tier:** Easy K8, easy K9.

### Proposal 2.3.9 — Variance and standard deviation introduction (statistics) [P0]
**Concept:** Compute mean, deviations, squared deviations, variance, and standard deviation for a small dataset (5–8 values). Compare two datasets with same mean but different SD.
**Source curriculum:** Estonia G9; Japan Math I (G10); Singapore Sec 4; Sweden Mat 2; CCSS HSS-ID.
**Multi-step structure:** 6 steps — sum, mean, deviations, squared deviations, variance, SD; +2 steps for comparison.
**Realistic contexts:** (a) test scores in two classes; (b) daily temperatures in two cities; (c) production quality across two factories.
**Variable parameterisation:** dataset of 5–8 small integers chosen so variance is rational and SD is exactly representable or "nice."
**Difficulty tier:** Medium K9 (single dataset), hard K9 (comparison), easy K10.
**Why:** **This directly fills the K7+ statistics gap (variance/std dev non-existent).** Multi-step arithmetic with named intermediate quantities — perfect for benchmarking sequential computation.

### Proposal 2.3.10 — Probability with tree diagram and conditional update (statistics) [P1]
**Concept:** Two-stage process (e.g., draw two balls, with or without replacement). Compute joint probability, then conditional probability given an outcome.
**Source curriculum:** Singapore Sec 3; Norway G9; CCSS 7.SP.C.8.
**Multi-step structure:** 5 steps — enumerate sample space, compute joint probabilities, sum the relevant ones, apply Bayes-lite for conditional, simplify.
**Realistic contexts:** (a) drawing balls from a bag; (b) drawing cards; (c) selecting students from a class with two attributes.
**Difficulty tier:** Medium K8, hard K9.

### Proposal 2.3.11 — Geometric proof chain (geometry) [P1]
**Concept:** Given a configuration with parallel lines and transversals, prove a target angle equals a given angle (or that two triangles are congruent).
**Source curriculum:** Japan G8 angle-theorem chain; Singapore Sec 2.
**Multi-step structure:** 4–7 reasoning steps, each citing a stated theorem.
**Realistic contexts:** Abstract geometric configurations; less amenable to context-injection.
**Variable parameterisation:** angle measures, configuration topology (kept fixed across instances; angles parameterised).
**Difficulty tier:** Medium K8, hard K9.
**Why:** Tests deductive chain construction with explicit reasons — distinct from numeric word problems. Mathbot's current taxonomy is light on this.

## 2.4 K10-K12 — the deepest gap

Currently only 5 files at K10-K12 combined. All proposals here are P0 or P1.

### Proposal 2.4.1 — Compound interest, monthly compounding, comparison of plans (compound_growth) [P0]
**Concept:** Two savings products: one at r₁% compounded annually, one at r₂% compounded monthly. After N years, which is greater? By how much?
**Source curriculum:** Finland LOPS MAA9 (financial math); Norway 2P/S1; Singapore Sec 4 / H1; CCSS HSA-SSE.B.3.c.
**Multi-step structure:** 5–6 steps — apply formula to plan A, apply formula to plan B (with periodic adjustment), compare, compute difference, interpret as effective annual rate.
**Realistic contexts:** (a) bank savings comparison; (b) retirement account A vs B; (c) certificate of deposit vs money market.
**Variable parameterisation:** principal, two rates, two compounding frequencies, N years.
**Difficulty tier:** Medium K10, hard K11 (with effective rate question).

### Proposal 2.4.2 — Loan amortisation with monthly payments (compound_growth × sequential_purchase) [P0]
**Concept:** Loan of L at r% annual, monthly payment M, find balance after k months and total interest paid.
**Source curriculum:** Finland MAA9; Norway grade 10 + 1P-Y/2P; Singapore H1.
**Multi-step structure:** 7+ steps for direct iterative simulation; 4 steps with annuity formula.
**Realistic contexts:** (a) car loan; (b) student loan; (c) small-business loan.
**Difficulty tier:** Hard K10 (iterative for k=3-6 months), easy K11 (formula).

### Proposal 2.4.3 — Geometric series application (compound_growth × algebra) [P0]
**Concept:** Sum of a geometric series in real context — population growth, drug accumulation, radioactive decay. Find total over N periods, or find N for a target threshold.
**Source curriculum:** Finland MAA9; Sweden Mat 4; Estonia lai G11; Singapore H2.
**Multi-step structure:** 5 steps — identify ratio, sum formula, solve for N, verify, interpret.
**Difficulty tier:** Medium K11, hard K11 (with logarithm to solve for N).

### Proposal 2.4.4 — Three-dimensional area_perimeter chain (area_perimeter_chain) [P0]
**Concept:** Compute surface area and volume of a composite solid (cylinder topped with hemisphere; cone embedded in cube), then use to compute paint, fill, or weight at given density.
**Source curriculum:** Singapore Sec 2 mensuration; Estonia G9; CCSS 8.G.C.9 + HSG-GMD.
**Multi-step structure:** 6–7 steps — decompose, compute each component's surface area / volume separately, sum (with overlap subtraction), apply rate.
**Realistic contexts:** (a) water tank with hemispherical top — fill capacity and paint; (b) silo with conical top; (c) ice cream cone.
**Variable parameterisation:** dimensions, paint coverage, water density, target unit.
**Difficulty tier:** Medium K10, hard K10–K11.
**Why:** **Directly fills the K9-K12 area_perimeter_chain gap.** Composite solids are the natural extension of K7-K8 composite figures.

### Proposal 2.4.5 — Optimisation via calculus (algebra/calculus) [P1]
**Concept:** Maximise volume of a box made by cutting squares from corners of a rectangular sheet; or minimise cost of a cylindrical container with fixed volume.
**Source curriculum:** Singapore A-Math (Sec 4); Norway R1; Sweden Mat 3; Finland MAA6; Japan Math II.
**Multi-step structure:** 6 steps — set up function, take derivative, set to zero, solve, verify second derivative, interpret with units.
**Difficulty tier:** Medium K11, hard K11.

### Proposal 2.4.6 — Hypothesis test with sample mean (statistics) [P1]
**Concept:** Sample of size n with sample mean and SD; test whether population mean differs from a stated value (z-test or one-sample t-test).
**Source curriculum:** Singapore H2; Japan Math B; Estonia lai G12; Sweden Mat 5; Norway S2.
**Multi-step structure:** 6–7 steps — state hypotheses, compute test statistic, compare with critical value or compute p-value, conclude, interpret.
**Difficulty tier:** Hard K11, medium K12.

### Proposal 2.4.7 — Exponential decay with half-life (compound_growth × rate_time) [P1]
**Concept:** Drug clearance, radioactive decay, or carbon dating. Given half-life, find concentration at time t, or solve for t given target concentration.
**Source curriculum:** Singapore H2 first-order ODE applications; Netherlands Wiskunde A; CCSS HSF-LE.
**Multi-step structure:** 5 steps — set up exponential model, substitute, solve (with logarithm), interpret.
**Difficulty tier:** Medium K11.

### Proposal 2.4.8 — Linear regression and prediction (statistics) [P1]
**Concept:** Given a small bivariate dataset, compute the regression line, predict y at a new x, compute correlation, comment on extrapolation risk.
**Source curriculum:** Singapore H2; Netherlands Wiskunde A; Estonia lai G12; CCSS HSS-ID.
**Multi-step structure:** 7 steps — sums, means, slope, intercept, prediction, correlation, qualitative comment.
**Difficulty tier:** Hard K11, medium K12.

### Proposal 2.4.9 — Mathematical induction (algebra) [P2]
**Concept:** Prove by induction a sum formula (e.g., 1+2+...+n = n(n+1)/2) or a divisibility statement.
**Source curriculum:** Norway R2; Sweden Mat 5; Estonia lai G11; Japan Math B; Singapore H2.
**Multi-step structure:** 4 steps — base case, inductive hypothesis, inductive step, conclusion.
**Difficulty tier:** Hard K11, medium K12.

### Proposal 2.4.10 — Vector geometry in 2D/3D (geometry) [P2]
**Concept:** Given three points, determine if they are collinear; or given two vectors, find the angle between them or the area of the parallelogram they span.
**Source curriculum:** Singapore Sec 4 / H2; Japan Math C; Norway R1; CCSS HSN-VM.
**Multi-step structure:** 4–5 steps.
**Difficulty tier:** Medium K11, hard K12 (3D).

## 2.5 Summary table of proposals

| ID | Title | Family | Grade | Tier | Steps | Priority |
|---|---|---|---|---|---|---|
| 2.1.1 | Equal-share with remainder | multi_person_sharing | K3-K4 | E | 3 | P0 |
| 2.1.2 | Unequal-share by rule | multi_person_sharing | K4-K5 | E-M | 4 | P0 |
| 2.1.3 | Sharing with rate | multi_person_sharing × rate_time | K5 | M | 5 | P1 |
| 2.2.1 | Ratio with internal transfer | multi_person_sharing | K6-K7 | M | 5 | P0 |
| 2.2.2 | Ratio with external transfer / age | multi_person_sharing | K6-K7 | M | 4-5 | P0 |
| 2.2.3 | Sequential percentage discount | sequential_purchase / percentages | K7-K8 | E-H | 4-5 | P0 |
| 2.2.4 | Linear equation, plan comparison | algebra | K7-K8 | M | 4 | P0 |
| 2.3.1 | Compound percent change chain | compound_growth | K8-K10 | E-H | 5-6 | P0 |
| 2.3.2 | Compound interest with deposits | compound_growth | K8-K11 | M-H | 4-7 | P0 |
| 2.3.3 | Two-rate work problem | rate_time | K7-K8 | M | 5 | P0 |
| 2.3.4 | Speed/distance meet & overtake | rate_time | K7-K9 | M-H | 5-6 | P0 |
| 2.3.5 | Sequential purchase with budget | sequential_purchase | K7-K9 | E-H | 4-6 | P0 |
| 2.3.6 | Composite-figure paint chain | area_perimeter_chain | K7-K8 | E-H | 5-6 | P0 |
| 2.3.7 | Pythagorean field-and-fence | area_perimeter_chain × geometry | K8-K9 | M | 4-5 | P1 |
| 2.3.8 | Linear function from data points | algebra / functions | K8-K9 | E | 4 | P0 |
| 2.3.9 | Variance and SD computation | statistics | K9-K10 | M-H | 6-8 | P0 |
| 2.3.10 | Probability tree + conditional | statistics | K8-K9 | M-H | 5 | P1 |
| 2.3.11 | Geometric proof chain | geometry | K8-K9 | M-H | 4-7 | P1 |
| 2.4.1 | Annual vs monthly compounding | compound_growth | K10-K11 | M-H | 5-6 | P0 |
| 2.4.2 | Loan amortisation | compound_growth × sequential_purchase | K10-K11 | H | 4-7+ | P0 |
| 2.4.3 | Geometric series application | compound_growth × algebra | K11 | M-H | 5 | P0 |
| 2.4.4 | 3D composite area/volume chain | area_perimeter_chain | K10-K11 | M-H | 6-7 | P0 |
| 2.4.5 | Calculus optimisation | algebra / calculus | K11 | M-H | 6 | P1 |
| 2.4.6 | Hypothesis test, one-sample | statistics | K11-K12 | M-H | 6-7 | P1 |
| 2.4.7 | Exponential decay / half-life | compound_growth × rate_time | K11 | M | 5 | P1 |
| 2.4.8 | Linear regression and prediction | statistics | K11-K12 | M-H | 7 | P1 |
| 2.4.9 | Mathematical induction | algebra | K11-K12 | H | 4 | P2 |
| 2.4.10 | Vector geometry | geometry | K11-K12 | M-H | 4-5 | P2 |

## 2.6 Prioritisation recommendation

**Build order, aligned with cleanup-doc gaps:**

1. **First wave (P0, K7-K10 spec-mandated families)** — proposals 2.3.1, 2.3.2, 2.3.3, 2.3.4, 2.3.5, 2.3.6, 2.3.9, 2.4.1, 2.4.2, 2.4.4. These directly hit the cleanup-doc's stated priorities: K7-K12 underrepresentation, the five spec-mandated families, K7+ statistics, and K9-K12 area_perimeter_chain.
2. **Second wave (P0, K6-K7 bridge and K3-K5 sharing)** — proposals 2.2.1, 2.2.2, 2.2.3, 2.2.4, 2.1.1, 2.1.2. These address the pre-algebra→algebra bridge gap and the K3-K5 multi_person_sharing conceptual gap.
3. **Third wave (P0, K8-K9 functions and K11 algebra/series)** — 2.3.8, 2.4.3. These round out the K7-K10 algebra coverage with function-from-data and series-application templates.
4. **Fourth wave (P1)** — 2.1.3, 2.3.7, 2.3.10, 2.3.11, 2.4.5, 2.4.6, 2.4.7, 2.4.8. Adds proof, probability, calculus optimisation, and hypothesis testing — completing K11-K12 statistics depth and bringing in deductive reasoning.
5. **Fifth wave (P2)** — 2.4.9, 2.4.10. Mathematical induction and vector geometry; useful but lowest-leverage given current taxonomy.

**Cross-cutting design recommendations for the coding agent:**

1. **Adopt Norway's vocational context-injection axis.** Define a context library (savings, population, paint/painting, recipe scaling, factory production, sports, healthcare, agriculture, transportation) and parameterise every template by context. The same compound-growth kernel should generate 6+ context-specific instances.
2. **Adopt Singapore's invariant-naming.** For multi_person_sharing problems, every template should explicitly tag which quantity is invariant (total, difference, one part) — this is a structural feature LLMs miss systematically.
3. **Use CCSS standard codes as primary grade tags** but **calibrate step counts using Dutch Wiskunde A item structure** for K10+ (4-6 sub-questions chained). Do not let Common Core's typically-shorter prompt structure cap mathbot's depth.
4. **Add an "open-ended" tag** for a small subset of problems (~5% of templates), inspired by Japan's Open-Ended Approach, where multiple correct answers or methods are valid. These are valuable benchmark items even if scoring is harder — they specifically test the failure mode where models converge on a memorised solution.
5. **Build the constraint engine to guarantee "nice" answers.** All Singapore P5/P6 templates rely on this: parameters are chosen so intermediate states and the final answer are integers or small fractions. Without this, generated problems will silently produce ugly decimals that obscure whether the model erred procedurally or arithmetically.

## Conclusion — what changed from the curriculum tour

Going in, the natural assumption is that Common Core should be mathbot's anchor since it's the largest English-speaking system. **The research argues against that as the *depth* anchor**: CCSS multi-step items are systematically shorter than what a multi-step reasoning benchmark needs. The right pattern is to use **CCSS as the grade-level taxonomy anchor**, **Singapore P5-Sec 4 as the multi-step word-problem template library**, **RME / Wiskunde A as the long-context-chain depth target for K10+**, and **Japan's G8 proof chain + open-ended approach as a deductive-reasoning category mathbot doesn't yet have**. Estonia and Finland's upper-secondary financial-math and statistics modules give the cleanest sequence for K11-K12, and Norway's vocational context-injection model is the design pattern that makes the whole thing scale to thousands of instances per template. The five spec-mandated families (`sequential_purchase`, `rate_time`, `compound_growth`, `multi_person_sharing`, `area_perimeter_chain`) all map cleanly onto established curriculum content; **the gap is not curricular — it is that current AI benchmarks (GSM8K et al.) under-sample these families relative to their importance in actual K-12 curricula worldwide**. Filling that gap is mathbot's highest-leverage contribution.