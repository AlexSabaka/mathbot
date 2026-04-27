# The STEM pivot is mostly a bad idea. Here's the honest version.

**The short version:** don't rebrand mathbot. Physics is the one STEM domain that genuinely earns a module — roughly 120–180 templates, real curriculum convergence across all 8 reference systems, and a methodology gap (ABench-Physics Phy_B is 100 templates and graduate-level; PHYBench is symbolic-equivalence, not procedural). Chemistry is feasible at ~120–170 templates but only if you commit upfront to mhchem+RDKit and explicitly exclude IUPAC nomenclature and mechanism drawing. Biology is a small conditional module of ~50–60 templates, **almost entirely genetics**. Earth/space is not a module at all — its salvageable ~15 templates belong inside physics (Kepler, Hubble, Stefan-Boltzmann) or chemistry (radiometric dating). The proposed name "STEM-Symbolic-Benchmark" walks mathbot straight into a knife-fight with ABench-Physics, ChemBench, LAB-Bench, and EngChain simultaneously, and the Reddit/HN narrative gets weaker, not stronger, with breadth. The credible pivot is incremental: ship `mathbot-physics` as a sibling repo, claim the `stembench` namespace defensively, and keep the headline brand focused on math until physics signal is in.

This report works through that recommendation domain by domain, with the curriculum and benchmark evidence behind it.

## 1. Mathbot's current niche, briefly

Mathbot's defensible position is **K-12 grade-aligned, internationally-curriculum-grounded, structurally-diverse procedural robustness** for math. It competes with exactly one prior work — Apple's GSM-Symbolic — and beats it on openness, scale (358/640 templates vs Apple's small set), and a generation pipeline that downstream users can run themselves. Phase 5 commits the math stdlib + scipy.stats + sympy sandbox, a `unit_system` parameter for metric/imperial, an SVG visual layer (Jinja-rendered + Python builders), and a multi-language foundation. That positioning is sharp because it solves a single problem cleanly, and it has the right shape for r/LocalLLaMA and HN: one number ("Frontier model X drops Y% under perturbation") and an MIT-licensed pipeline anyone can run.

Any pivot has to preserve that sharpness or it isn't worth doing.

## 2. The four domains, ranked

| Domain | Procedural fit | Realistic K-12 templates | Net new infra cost | Curriculum coverage across 8 systems | Verdict |
|---|---|---|---|---|---|
| **Physics** | High, with caveats | 120–180 (80–100 for Phase 1 core) | Substantial: pint/astropy.units, scipy.constants, vectors, schemdraw | Strong — universal classical-mechanics → E&M → waves → modern spine | **Go, as `mathbot-physics`** |
| **Chemistry** | Medium-high if scope-disciplined | 120–170 (80–100 MVP) | Substantial: chempy + mendeleev + optional RDKit; mhchem-LaTeX dual-emit | Strong — ~80% common across all 8 systems | **Conditional go, after physics** |
| **Biology** | Mixed; mostly weak with one strong pocket | 50–80 (genetics is ~50–60% of value) | Modest: pedigree-tree builder, Punnett SVG | Strong for genetics + pop bio; weak for everything else | **Small dedicated module, ≤80 templates** |
| **Earth/space** | Poor | 25–40 raw, ~15 net after de-duplication with physics/chem | Negligible if absorbed | Fragmented — only 3/8 systems have a quantitative track | **No standalone module. Absorb ~15 into physics/chem; skip the rest.** |

The ranking is not subtle. Physics is genuinely strong; chemistry is feasible; biology is small; earth/space doesn't really exist as a peer. Anything claiming all four are equal is marketing.

## 3. Physics — the strong case, with non-trivial costs

Physics is the cleanest expansion target for three concrete reasons. First, **numerical answers are unambiguous within a tolerance** — better than math's canonical-form headaches. Second, **frontier LLMs underperform on physics relative to math at equivalent levels** (UGPhysics: o1-mini 49.8%; ABench-Physics Phy_A: Gemini 2.5 Pro ~43%), so a benchmark still has signal. Third, **curriculum convergence is real**. The eight reference systems — Finland LOPS Fysiikka, Norway LK20 Fysikk 1/2, Sweden Fysik 1/2/3, Estonia gümnaasium füüsika, Singapore O-level 6091 + A-level H1/H2 9749/9478, Japan 物理基礎/物理 (MEXT), Netherlands Natuurkunde HAVO/VWO, US NGSS HS-PS + AP Physics 1/2/C — converge on a classical mechanics → E&M → waves/optics → modern physics spine, with one well-built template covering 6+ systems and only the context wrapper changing.

Within K-12 quantitative content, the procedural fit is high for kinematics 1D/2D, Newton/FBD/inclines, momentum 1D, energy/work, circular motion, gravitation/Kepler, SHM, wave basics, Doppler, standing waves, Snell, thermal Q=mcΔT, ideal gas, electrostatics with point charges, capacitors, DC circuits, transformers, photoelectric, de Broglie, nuclear half-life, mass-energy, and special relativity intro. Medium fit covers 2D momentum, polarization (Malus only), heat engines, multi-loop Kirchhoff, RC/RL transients, magnetism with vectors, induction, AC impedance, and lens/mirror equations (numeric is clean; sign conventions are a trap). What is **not procedurally generable** is roughly 30–40% of the formal curriculum: NGSS performance expectations, lab design, error analysis as a skill, "describe and justify" items, and qualitative modern physics. Don't oversell coverage — be explicit that the benchmark targets the quantitative-calculation slice, which is most of what's *examined* but not all of what's *taught*.

The infrastructure delta is the part that matters and the part most likely to be underestimated. **The planned `unit_system: metric/imperial` flag will not survive the first capacitor or magnetic-flux problem.** Singapore A-level explicitly mandates p/n/μ/m/c/k/M/G/T prefix arithmetic; nuclear half-lives use ns; capacitors use μF/pF; frequencies use MHz/GHz. Compound units (m/s², N·m, J/(kg·K), V/m, T·m², W/m², Pa·s) must be first-class — you cannot fake this with a metric/imperial swap. Imperial in physics class is largely dead globally, so what you actually need is **SI plus first-class prefix dimension orthogonal to the math toggle**. The pragmatic path is to adopt `pint` or `astropy.units` rather than rolling a Quantity class. You also need 2D/3D vector primitives (Coulomb on a triangle, 2D collisions, F = qv×B), `scipy.constants` (G, c, h, ℏ, k_B, e, m_e, ε₀, μ₀, N_A, R, σ), and `numpy.linalg.solve` for multi-loop Kirchhoff. Complex numbers and ODE solvers are Phase 3 only — almost no K-12 problems require them.

The visual layer is the second cost center, and it costs more than math did. **Roughly 40–60% of K-12 physics problems lose meaning or become ambiguous without a figure.** Free-body diagrams, ray diagrams, and vector triangles are tractable in Jinja-SVG with a small parameterized library (~10 canonical layouts). **Circuit schematics are not.** Adopt schemdraw as a hard dependency — it's MIT-licensed, declarative, no GUI deps, and saves weeks vs hand-rolling SVG. For wave and trajectory plots, render at *authoring time* with matplotlib and ship the SVG; don't put matplotlib at runtime. Budget the visual layer at ~30% of total project effort.

The realistic family count is **120–180 for solid 8-system coverage, 80–100 for a Phase-1 core** that already serves ~70% of every system's quantitative content. Authoring is **1.5–2× math** per template — call it 2–6 hours per family, or 300–900 person-hours total. That's 2–6 person-months of focused work. Don't promise 358 anchors in the same time you produced 358 math anchors.

The published precedent worth knowing: **ABench-Physics** (arXiv 2507.04766) ships 400 static + 100 dynamic-variant problems with 1% tolerance and explicit unit/sig-fig grading; all models drop ~22.5% from static to dynamic. **PHYBench** (NeurIPS 2025) has 500 problems with symbolic-expression scoring (EED), Gemini 2.5 Pro at 36.9% vs human 61.9%. Both are graduate/olympiad level. The K-12 procedural slot is open.

## 4. Chemistry — feasible, but rendering is load-bearing

Chemistry is procedurally generatable but materially harder than physics on one axis: **chemical formulas have grammatical structure that the planned Jinja+SVG layer cannot fake**. Subscripts (H₂SO₄), charges (Fe³⁺), state labels, equilibrium arrows, isotope notation (²³⁵₉₂U with left-stacked super- and subscript), and reaction conditions over arrows together push you to a real rendering decision. The good news is the existing chemistry-LLM benchmarks have already converged on an answer: **ChemBench, ChemLLMBench, and GPQA chemistry all use mhchem-LaTeX (`\ce{...}`) for equations and SMILES for individual molecules**. The right call for mathbot is to emit *both* a `unicode_text` and a `latex` field per chemistry string in the YAML, and let downstream consumers (HTML/MathJax, Markdown/LaTeX, plain text) pick whichever they need.

If you take that decision, the curriculum picture is favorable. Across Finland Lukio Kemia (KE1–KE6 LOPS 2019), Norway Kjemi 1/2, Sweden Kemi 1/2, Estonia gümnaasium keemia, Singapore 6092 + H1/H2, Japan 化学基礎/化学, Netherlands Scheikunde HAVO/VWO, and US NGSS HS-PS1 + AP Chemistry, **roughly 80% of K-12 chemistry topics overlap**. The strongly procedural topics — stoichiometry, gas laws, solutions, thermochemistry, kinetics, equilibrium, acid-base, redox/electrochemistry, nuclear — are essentially numbers + ratios + a few exponential/log equations. ICE tables for equilibrium are the prime sympy use case (quadratic with negative-root rejection). Le Chatelier qualitative shifts and standard reduction potentials live cleanly as YAML data tables.

The library decisions are clearer than physics's. Use **mendeleev as a build-time generator** to produce a frozen `data/elements.yaml` (~120 elements × 10–15 properties, well under 100KB), with provenance comments for IUPAC sourcing. Add **chempy as a runtime dependency** — it covers equation balancing (linear-algebra null space, sympy-backed), formula parsing, `Substance.mass`, and Unicode/LaTeX/HTML name rendering, and saves you from rebuilding four sub-systems. Add **RDKit as an optional dep** for organic structure rendering from SMILES (`Draw.MolDraw2DSVG`); load it only for organic-tier templates. Skip pymatgen — it drags in materials-science deps you don't need.

The hard scope decision is what to **exclude**. IUPAC nomenclature *generation* is not safely auto-verifiable — even ACD/Labs and OPSIN have edge cases at K-12 level. Reaction mechanism arrow-pushing has no FOSS verifier worth using. Lewis structure *production* has resonance and formal-charge tie-breaking ambiguity. The right policy is to **provide structures as RDKit-rendered images-from-SMILES (input only), never ask the model to produce novel structures, and limit nomenclature to recognise/match MCQ format** with a fixed answer key. Chemistry's risks-to-flag list is short but real: SMILES-vs-IUPAC representation choice changes what you measure (ChemBench documents 10% vs 25% accuracy on the same NMR-symmetry question depending on representation); underdetermined balancing (C+O₂→CO+CO₂ has a free parameter — chempy raises by default, templates must specify uniquely-balanceable reactions); significant figures (Netherlands and Singapore O-level penalize wrong sig-figs; you need a policy or you'll mismatch human-grading conventions); and decimal-separator localization (Norway/Sweden/Finland use comma, Singapore mandates dm³ over l/L).

The 13 canonical multi-step chains that map to mathbot's "sequential_purchase"-style families are: stoichiometry chain (4 steps), strong-acid titration, weak-acid titration with H-H, equilibrium ICE with Q-verify, buffer design with H-H, redox half-reaction balance, Galvanic + Nernst, Faraday electrolysis, kinetics order-determination + half-life, calorimetry → Hess, empirical → molecular formula, gas-collection-over-water with Dalton, and nuclear decay-mode + fraction-remaining. Total realistic K-12 family count: **~120–170 distinct families covering ~85% of the international common core**, with ~80–100 as MVP. **Skip imperial unit_system entirely for chemistry** — it's universally SI in education globally.

## 5. Biology — small dedicated module, mostly genetics

Be honest: **most school biology is the recall-heavy MMLU-Bio territory you should explicitly exclude**. Organ system anatomy, taxonomy, evolution as conceptual essay, ecology vocabulary, organelle identification, mitosis/meiosis stage recall, DNA structure description, immune system narrative, plant hormones, neuron action potential narrative, biotechnology techniques — all qualitative, all already saturated, all useless for procedural perturbation. That excluded set is **~70–75% of typical school bio content**.

What's left is concentrated, and that concentration is the point. **Genetics is ~50–60% of bio's procedural value all by itself.** Monohybrid and dihybrid Punnett squares, sex-linked inheritance, ABO blood groups, codominance, pedigree analysis, Hardy-Weinberg with chi-square against expectation, allele frequencies from genotype counts, two-locus linkage with recombination frequency, chi-square goodness-of-fit on 9:3:3:1 and 3:1 ratios — that block alone is **~40 template families**, all parameter-rich, all visually distinct via Punnett grids and pedigree trees, all universally taught (AP Bio 5.5–7.5, NGSS HS-LS3-3, IB HL, Singapore H2 Core Idea 2, Japan EJU, Finland BI4, Estonia, Sweden Biologi 2). The pedigree-tree SVG generator is the one high-leverage build — mathbot already plans tree builders, so reuse + custom symbols.

Population biology adds another ~12 families (exponential, logistic, doubling time, Lincoln-Petersen mark-recapture, Lotka-Volterra qualitative, survivorship curves), heavily covered in AP/IB/H2/NGSS. Quantitative ecology adds ~7–8 (trophic 10% rule, Simpson's D, Shannon H, evenness/richness). Membrane transport / water potential adds ~8 (AP Bio formula sheet explicitly includes ψ = ψs + ψp). Enzyme kinetics + metabolism stoichiometry adds ~8–10 (Michaelis-Menten, Q10, ATP yield arithmetic, photosynthesis/respiration stoichiometry — the last overlaps chemistry, don't double-count). Biostats and microscopy add 3–5 mostly trivial families.

**Net realistic total after deduplication: 50–80 templates. Closer to 60 if you're disciplined.** That's roughly 10% of mathbot's current corpus size. Don't try to force more — you'll be padding with low-quality items, and that hurts benchmark credibility more than missing templates does. The case for biology is mostly subject-area-credibility: a math+physics+chem benchmark *feels* narrower than advertised, and a small but solid genetics module fixes that without committing to a full life-sciences pretense.

## 6. Earth/space — not a module

The brutal version: **most school earth science is qualitative description**, and the curriculum picture is fragmented enough that you cannot honestly claim 8-system coverage. Of the eight reference systems, only NGSS (US), Japan 地学/地学基礎 (a minority track most students don't take), and AP Environmental Science (peripheral) have meaningful quantitative earth/space content. Norway, Sweden, Estonia, Singapore O-level, Netherlands, and Finland route earth-science topics through *geography* — qualitative regional + physical-geography — at upper secondary, not through a dedicated quantitative course. **You can't write earth-science curriculum-mapping documents for 8 systems honestly because half don't have the track.** That alone disqualifies it from sitting alongside math/physics/chem as a peer module.

The ~46–51 raw template families that exist (Kepler, parallax, distance modulus, Hubble, Stefan-Boltzmann, Wien, telescope resolving power, radiometric dating, plate motion arithmetic, Richter, lapse rates, dew point, residence time, energy balance, albedo, simple greenhouse forcing, insolation by latitude) collapse to **~28–33 net after subtracting overlap with physics and chemistry**. Astronomy belongs in physics under gravitation/cosmology. Radiometric dating belongs in chemistry's nuclear/kinetics section. Stefan-Boltzmann/Wien is physics thermal radiation. Hydrology Q=vA is physics fluids.

The recommendation is concrete: add 5–8 **astronomy templates** to the physics module (Kepler, parallax, Hubble, distance modulus, simple planetary energy balance), add **radiometric dating** as 3–5 templates inside chemistry's nuclear section, and **skip the rest entirely**. Don't park earth/space as "future work" — that's how zombie scope creeps in. The structural problem (mostly qualitative content, low quantitative ceiling per topic, heavy overlap with adjacent domains) doesn't get better with time.

## 7. The benchmark landscape and the gap that's actually open

The K-12 STEM benchmark landscape is unambiguous: **standard MC is dead at the frontier**. MMLU's HS-Physics/HS-Chem/HS-Bio subsets sit at 95%+ for GPT-5.x, Gemini 3.x, and Claude Opus 4.x. ARC, OpenBookQA, SciQ — all at 96%+ for frontier, formally deprecated. AGIEval-STEM in the high 80s–90s. MedQA-USMLE 92%+. **The headroom in STEM lives at three places: graduate/olympiad level (GPQA-Diamond at 91–94% is itself saturating; OlympiadBench, PHYBench, CritPt still have room), symbolic/expression scoring (PHYBench's EED tree-edit distance), and procedural perturbation (ABench-Physics Phy_B, EngChain).**

The procedurally-perturbed STEM-Symbolic slot is partially filled but specifically and narrowly:

- **ABench-Physics Phy_B (July 2025)** — 100 problems with an automatic variation engine, 22.5% average drop from static to dynamic. This is the most direct GSM-Symbolic analog in physics. Graduate/olympiad-only. **Only 100 templates** — small enough that "broaden it to K-12" is defensible.
- **PHYBench (April 2025, NeurIPS 2025)** — 500 *original* problems with symbolic-expression answers and tree-edit-distance scoring. Doesn't perturb templates; tests symbolic equivalence. Different methodology, complementary not overlapping.
- **EngChain (November 2025, arXiv 2511.01650)** — the GSM-Symbolic methodology lifted directly into engineering: 90 templates, 9 domains, parameterized instantiations from authoritative handbooks. Engineering, not K-12 STEM. The closest spiritual sibling.

What is **not taken**: a K-12 procedural-template benchmark for biology, chemistry, or earth science; a unified math+physics+chem K-12-anchored symbolic-perturbation suite under one name with HF + lm-eval-harness adapters; any chemistry analog of GSM-Symbolic (ChemBench is curated MCQ, ChemLLMBench is task-curated); any biology analog (LAB-Bench is curated MC for research workflows, FutureHouse 2024); anything in earth/space.

The critical caveat: **ABench-Physics already establishes the procedural-perturbation methodology in physics**, and reviewers and Reddit will absolutely point at it. Mathbot's physics differentiation is "K-12 + breadth + scale of templates + open generation pipeline + math anchor", not "we invented procedural physics." Be precise about that or get punished for it.

## 8. Infrastructure delta summary

| Capability | Math (Phase 5) | Physics adds | Chemistry adds | Biology adds |
|---|---|---|---|---|
| Sandbox | math + scipy.stats + sympy | scipy.constants, numpy.linalg.solve, complex (Phase 3) | chempy, mendeleev (build-time), RDKit (optional) | scipy.stats already covers chi-square, regression |
| Units | metric/imperial flag | **pint or astropy.units** for compound + prefix; vectors mandatory | Pure SI; no imperial | Mostly unitless or biological units (cells, individuals, kJ already in chem/physics) |
| Visual | Jinja-SVG + tree/chart builders | FBD library, **schemdraw** (hard dep), ray diagrams, matplotlib→SVG at authoring time | Periodic-trend plots reuse charts; RDKit MolDraw2DSVG for organics | **Punnett grid + pedigree tree** are the two high-leverage builds |
| Data files | locale-aware pools | Constants table from scipy.constants | `data/elements.yaml` (~100KB), curated reaction library (~200–500 entries) | Allele/trait pools, organism names |
| Schema | existing | `domain: physics`, `subdomain: kinematics`, `unit_system: SI`, `vector: 2D` | `nomenclature: IUPAC|trivial`, `representation: smiles|formula|name`, dual `unicode_text`+`latex` emit | `inheritance_mode: autosomal_recessive|x_linked|...` |
| Verification | numeric tolerance | 1% relative; explicit sign-convention pinning; vector magnitude+direction | ±2% relative; ±0.02 pH; integer balancing via chempy; **no IUPAC autoverify** | Punnett ratio exact; chi-square p-value tolerance; H-W frequencies ±2% |

The honest reading of this table: **physics adds the most infrastructure cost, chemistry adds the most authoring discipline cost, biology adds the least of either.** Earth/space adds nothing because it isn't a module.

## 9. Sequencing recommendation

The right phasing is incremental and reversible:

**Phase 6 — `mathbot-physics` as a sibling repo (3–6 months solo).** Build it as a separate package under the mathbot org so that if it stalls, mathbot proper isn't tainted. Target the Phase-1 core: 1D kinematics, projectile, Newton/FBD/inclines, momentum 1D, energy, Ohm/series-parallel circuits, wave basics, thermal Q=mcΔT, photoelectric, half-life — roughly **80–100 families covering ~70% of every system's quantitative content**. SI-only with prefix arithmetic. FBD + simple-circuit (schemdraw) + ray + vector triangle visuals. Ship the lm-eval-harness adapter and a HuggingFace dataset card on day one. **The success criterion is a single Reddit-shareable headline:** "Frontier model X drops Y% on procedurally-perturbed K-12 physics" — analogous to GSM-Symbolic's headline. If the methodology transfer signal is strong, you have a real result and the chemistry expansion is justified. If it's weak, you've learned that the mathbot story doesn't transfer, and you stop.

**Phase 7 — chemistry, contingent on physics signal (4–6 months).** Lock the rendering decision early: emit `unicode_text` + mhchem-LaTeX; use mendeleev for build-time element data; chempy as runtime dep; RDKit as optional. Target ~80–100 templates MVP, ~120–170 full. Skip IUPAC generation and mechanism drawing entirely. Don't start this until physics has a result.

**Phase 8 — biology genetics module (2–3 months, optional).** ~40 genetics templates + ~15 pop-bio/ecology + ~10 enzyme/water-potential/biostats. Ship only if you want subject-area-credibility and not to chase template volume. The pedigree-tree builder is the one high-leverage piece of new infrastructure.

**Earth/space — no phase.** Absorb 5–8 astronomy templates into Phase 6 physics; absorb 3–5 radiometric-dating templates into Phase 7 chemistry; close the door on the rest.

Total realistic timeline if executed solo: **9–18 months from Phase 5 ship to a four-domain corpus**, with physics being the single biggest risk on the critical path. Realistic template totals at end-state: ~640 math (current) + ~150 physics + ~150 chemistry + ~60 biology = ~1,000 templates across STEM. That's a defensible benchmark. Promising more is overcommitment.

## 10. Naming and positioning — the awkward part

The proposed name "STEM-Symbolic-Benchmark" is the wrong move, and the reason is structural rather than aesthetic. Three name slots matter:

- **`stembot` is poisoned.** stemrobo/stembot is an active microbit/PXT robotics package with a live website selling robots to K-12 students. A worse possible collision context for a K-12-adjacent LLM benchmark is hard to imagine.
- **`scibench` is double-poisoned.** Wang et al. (ICML 2024) own the academic name; PyPI has had a `scibench` slot since 2022.
- **`stembench` appears free** on both GitHub and PyPI as of late April 2026, but I could not directly confirm PyPI from the research pass — verify via `pip install stembench` and `pypi.org/project/stembench/` before announcing. Claim both the GitHub org and PyPI immediately as a defensive move regardless of pivot decision.

But the deeper issue isn't the name slot; it's the **Reddit/HN positioning math**. The LLM-eval market is saturated with partial multi-domain surveys (SciEval, SciKnowEval, MMLU-Pro, AGIEval) and what gets cited and adopted is sharp single-purpose tools (GSM-Symbolic, GPQA-Diamond, FrontierMath, AIME-2025, SWE-bench, ARC-AGI). **Broader = weaker is the dominant risk in this market**, not single-domain niche-ness. The current mathbot pitch competes with exactly one prior work and beats it on three concrete axes; "STEM-Symbolic-Benchmark" competes with ABench-Physics, ChemBench, LAB-Bench, EngChain, and PHYBench simultaneously, and the differentiation in each fight has to be argued individually.

The pragmatic naming strategy is: **keep `mathbot` as the headline brand, ship `mathbot-physics` as a sibling, claim `stembench` defensively, and reserve the umbrella-rebrand decision for after physics has a result.** If you do eventually rebrand, **`STEM-Symbolic`** (without "-Benchmark") is the cleanest umbrella — it directly references GSM-Symbolic's methodology, is short, and doesn't sound like a curriculum product. "K-12 STEM Eval" reads as edtech and r/LocalLLaMA reflexively dismisses edtech.

## 11. Risks and failure modes

Five risks deserve naming explicitly because each has a concrete kill condition for the pivot.

**Domain expertise gap.** Alex's acoustics+electronics background covers physics comfortably, less so chemistry/biology/earth-space. Template correctness scales badly outside one's expertise — a wrong stoichiometry coefficient or a mis-stated dominant allele will get screenshotted on Reddit and the whole project's credibility takes the hit, not just one template. **Hard kill condition for chemistry: if you can't recruit a chem-credible reviewer (PhD or strong undergrad), don't ship Phase 7.** Mitigations: chempy/pymatgen as automated balancing verifiers, RDKit for structure validation, and a small panel of pre-publication reviewers from r/chemistry or chemistry-stackexchange. None of those substitutes for a real reviewer; they reduce blast radius.

**Visual rendering scope blow-up.** Lewis structures and circuit schematics are hard to do well in pure SVG. Physics needs schemdraw-as-hard-dep; chemistry needs RDKit for organic; both need matplotlib at authoring time for plots. The kill condition is if you find yourself writing a custom schematic-routing layout algorithm — stop, adopt the dependency, move on.

**Saturation transfer risk.** The mathbot story is "K-12 math MC is saturated; structural-diversity perturbation exposes brittleness." That story transfers cleanly to physics (UGPhysics 49.8%, ABench-Physics ~43%, MMLU-Physics 95%+ — the perturbation gap will exist). It transfers less cleanly to chemistry, where ChemBench documents that frontier models exceed top human chemists on average. **The pivot is bad if the chemistry perturbation gap turns out small.** This is exactly why physics-first sequencing matters — it's the highest-confidence transfer.

**Maintenance burden.** Four domains × N families × M templates is a corpus that won't get audited carefully by one author. Each domain accumulates errata, curriculum drift, frontier-model-specific failure modes. Math alone at 358 anchors is plausibly maintainable solo; STEM at ~1,000 templates is not, full-stop. Mitigation: only commit to a domain if you have a contributor, or accept that the corpus is frozen at v1 and won't be updated.

**The "broader = weaker" framing risk.** This is the one I'd most worry about. Mathbot's defensible niche is a sharp story: K-12, structurally diverse, internationally curriculum-grounded. "STEM-Symbolic-Benchmark" loses each of those adjectives slightly — K-12 becomes mixed (most physics olympiad benchmarks are upper-secondary+), structural diversity is harder to claim across four domains than one, international curriculum coverage is honest for math and physics but partial for chemistry and dishonest for earth/space. **The pivot is bad if you can't preserve all three adjectives in the new positioning**, and earth/space alone breaks the third one.

## 12. Concrete go/no-go per domain

**Physics: GO**, as `mathbot-physics` sibling repo, Phase 6, 80–100 templates MVP, ~150 full. Highest-confidence methodology transfer, real curriculum convergence, real published procedural-physics precedent (ABench-Physics) that's narrow enough to differentiate against. The infrastructure cost is real — pint/astropy.units, scipy.constants, vectors, schemdraw — but it's well-scoped and the pieces all exist as mature dependencies.

**Chemistry: CONDITIONAL GO**, Phase 7, contingent on (a) physics signal being strong, (b) recruiting at least one chem-credible reviewer, (c) committing upfront to mhchem-LaTeX dual-emit + chempy + mendeleev + RDKit-optional + explicitly excluding IUPAC nomenclature generation and mechanism drawing. Target 80–100 MVP, 120–170 full. If any of (a)/(b)/(c) fails, defer indefinitely.

**Biology: SMALL DEDICATED MODULE OR SKIP**, Phase 8 if at all, ≤80 templates, weighted ~50–60% to genetics. The pedigree-tree builder is the one high-leverage build. Don't pretend it scales to physics/chem volume; allocate ~10% of total benchmark weight. If you skip it, the cost is subject-area-breadth credibility, not structural correctness — survivable.

**Earth/space: NO STANDALONE MODULE.** Absorb ~5–8 astronomy templates into physics (Kepler, parallax, Hubble, distance modulus, planetary energy balance) and ~3–5 radiometric-dating templates into chemistry. Skip lapse rates, hydrology, Richter, Mohs, plate-rate arithmetic. Don't write 8-system curriculum mapping for earth science — half the systems don't have the track and the claim is dishonest.

## 13. The bottom line

The pivot framed as "STEM-Symbolic-Benchmark" overcommits. The pivot framed as "ship `mathbot-physics`, see what happens, expand only on signal" is sober and reversible. The K-12 STEM procedural-perturbation slot is genuinely open, but the slot is shaped like physics, then chemistry, then a small genetics module — not like a four-equal-domain umbrella. Mathbot's defensible niche is a sharp three-adjective claim (K-12, structurally diverse, internationally curriculum-grounded), and earth/space breaks the third adjective by itself. The right thing to do is keep the current brand sharp, claim the `stembench` namespace defensively, build the physics sibling, and let the empirical signal from physics decide whether chemistry and biology are real opportunities or sunk cost.

If the pitch is "we built a procedural K-12 math benchmark and it generalizes to physics with the same methodology," that's a Reddit post. If the pitch is "we built a four-domain STEM benchmark covering 8 international curricula across physics, chemistry, biology, and earth science," that's a survey paper that nobody on r/LocalLLaMA will read. The first pitch is what mathbot is already positioned to deliver. The second pitch is the trap.

---

## Appendix A — Authoring guardrails for the existing math corpus

Mathbot's defensibility rests on **structural diversity** (one of the three adjectives in the niche claim). The Phase 5.7 audit surfaced five templates whose problem shape overlaps GSM8K-saturated patterns — `with_tax`, `money_change`, `items_at_price_each`. They're kept because the patterns are load-bearing for `sequential_purchase` / `compound_growth`, but **the corpus should not grow more of them.** Each new template that re-uses these shapes erodes the structural-diversity claim relative to GSM8K.

Existing templates (do not delete, do not extend with siblings):

- `math_k6_medium_shopping_04` (sequential_purchase, with_tax)
- `math_k7_medium_sequential_discount` (sequential_purchase, with_tax)
- `math_k7_hard_sequential_03` (sequential, with_tax)
- `math_k6_medium_decimals_add_sub_01` (decimals_add_sub, money_change)
- `math_k6_medium_proportions_01` (proportions, items_at_price_each)

When adding a new word problem, prefer non-GSM8K-saturated framings: rate × time, multi-person sharing with constraint, area→side→perimeter chains, compound growth over N periods, etc. The audit's `gsm8k_*` flags in [audit_templates.py](audit_templates.py) catch the regex shapes — if a new template trips them, redesign the surface text rather than ship a flagged template.
