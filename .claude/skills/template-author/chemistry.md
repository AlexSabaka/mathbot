# Chemistry domain (stub)

Chemistry template authoring is infrastructure-conditional. This file is a placeholder; populate from the SPEC + first authored exemplar when the first chemistry template lands.

## Infrastructure status

In place (shared with math/physics):

- `pint` backbone for unit arithmetic
- `sympy` for ICE tables (quadratic equilibrium with negative-root rejection is the canonical sympy use case)
- `scipy.stats` for chi-square / regression on chemistry data

Not in place yet — these are the load-bearing decisions to make before the first chemistry template:

1. **Rendering decision: dual-emit `unicode_text` + mhchem-LaTeX.** Chemistry formulas have grammatical structure (subscripts in H₂SO₄, charges in Fe³⁺, state labels (s)/(l)/(g)/(aq), equilibrium arrows ⇌, isotope notation ²³⁵₉₂U) that the planned Jinja+SVG layer cannot fake. ChemBench, ChemLLMBench, GPQA all use mhchem-LaTeX (`\ce{...}`) for equations and SMILES for individual molecules. The right call is to emit *both* a `unicode_text` and a `latex` field per chemistry string; downstream consumers (HTML/MathJax, Markdown/LaTeX, plain text) pick whichever they need. Schema implication: a new `ChemicalFormula` variable type with both fields, or a convention where chemistry templates render to a JSON sub-object instead of plain text.

2. **`chempy` as runtime dependency.** Covers equation balancing (linear-algebra null space, sympy-backed), formula parsing, `Substance.mass`, Unicode/LaTeX/HTML name rendering. Avoid rebuilding these.

3. **`mendeleev` as build-time generator.** Produce a frozen `data/elements.yaml` (~120 elements × 10-15 properties) with provenance comments. ~100KB checked-in artifact, no runtime dep.

4. **`RDKit` as optional dep.** For organic structure rendering from SMILES (`Draw.MolDraw2DSVG`). Load only for organic-tier templates.

5. **No `pymatgen`.** Drags in materials-science deps not needed for K-12.

6. **SI-only.** No imperial unit_system for chemistry. Universal globally in education.

## Hard scope exclusions

Chemistry has well-known things that *cannot* be auto-verified safely:

1. **IUPAC nomenclature generation.** Even ACD/Labs and OPSIN have edge cases at K-12 level. Policy: provide structures as RDKit-rendered images-from-SMILES (input only); never ask the model to produce novel IUPAC names; limit nomenclature to recognise/match MCQ format with a fixed answer key.

2. **Reaction mechanism arrow-pushing.** No FOSS verifier worth using. Skip entirely.

3. **Lewis structure production.** Resonance and formal-charge tie-breaking ambiguity. Provide as input, never as output.

## Authoring scope (when ready)

Realistic K-12 family count: 120-170 distinct families covering ~85% of the international common core; 80-100 as MVP.

The 13 canonical multi-step chains:

1. Stoichiometry chain (4 steps)
2. Strong-acid titration
3. Weak-acid titration with Henderson-Hasselbalch
4. Equilibrium ICE with Q-verify
5. Buffer design with H-H
6. Redox half-reaction balance
7. Galvanic + Nernst
8. Faraday electrolysis
9. Kinetics order-determination + half-life
10. Calorimetry → Hess
11. Empirical → molecular formula
12. Gas-collection-over-water with Dalton
13. Nuclear decay-mode + fraction-remaining

Each maps cleanly to mathbot's existing `sequential_purchase`-style multi-step shape: you set up state, apply transformations, verify constraints, report final answer.

## Antipatterns specific to chemistry

1. **SMILES-vs-IUPAC representation choice changes what you measure.** ChemBench documented 10% vs 25% accuracy on the same NMR-symmetry question depending on representation. Pick a representation per template and stick with it; don't mix.

2. **Underdetermined balancing.** C+O₂ → CO+CO₂ has a free parameter. `chempy.balance_stoichiometry` raises by default. Templates must specify uniquely-balanceable reactions. Test by running the balance routine before authoring the prose.

3. **Significant figures.** Netherlands and Singapore O-level penalize wrong sig-figs. Set a project-wide policy or you'll mismatch human-grading conventions.

4. **Decimal-separator localization.** Norway/Sweden/Finland use comma. Singapore mandates dm³ over l/L. Either the locale system handles this (preferred, via `culture:`) or the template hardcodes the convention and tags it.

## Verification tolerances

Pre-decided per the project notes:

- Numeric: ±2% relative
- pH: ±0.02
- Integer balancing: exact (via chempy)
- IUPAC: never auto-verify

Set `Answer:` formatting accordingly when the first templates land.

## When the first chemistry template lands

Update this file with:

- The dual-emit schema decision (concrete YAML pattern)
- A canonical recipe in `sandbox_recipes.md` for stoichiometry chain (the most representative pattern)
- The chempy/mendeleev integration pattern
- The exemplar template path
