# MathBot Phase γ — Harness Hardening & Gold-Standard Seed

*Seed document for the planning coding agent. Defines the scope of Phase γ: harness gaps that block K12 templates from reaching publishable quality, the rendering-pipeline upgrades needed to support tables / graphs / juicy LaTeX, and the gold-standard exemplar set that anchors the corpus going forward. The grader-skill (Phase δ) lives downstream of this and is intentionally out of scope here — its rubric will be designed against the gold-standards once they exist.*

---

## 0. Why this exists

Two K12 demo templates landed at the end of Phase β (N15 cooling and N16 RLC). Both had correct math and competent YAML structure. Both shipped broken visuals: the cooling plot has artifact-y axis ranges (17 to 89, 0 to 37.85) and a marked "answer" point that doesn't visually intersect the labeled target line; the RLC schematic shows a closed circuit while the prose says the source is disconnected. Both also declared a `noop_clauses` feature that no fixture exercises.

Three lessons from the post-mortem:

1. **The harness is missing primitives K12 needs.** No table rendering, no figure-builder for the load-bearing-figure problems Stewart's Calculus is built around (sector-cutout cone, riverbank optimization, related-rates geometry, Riemann-sum tables), no schema axis for "simplifying assumption omitted at hard tier" — the actual K12 difficulty lever.

2. **The rendering pipeline is text-first.** PDF/PNG/LaTeX/Markdown each need a distinct path through the renderer; today only SVG-and-rasterize-to-PNG exists. Text-form table rendering and inline LaTeX are absent. Multi-target rendering matters because the eval consumers are different (a JSON benchmark uses LaTeX strings; a PDF preview uses raster; a Markdown human-review wants Unicode-and-MathJax; a vision-model grader wants PNG).

3. **NoOp clauses are a grade-school construct mis-applied to K12.** The K12 analog is *simplifying-assumption suppression* (Stewart's "we assume the speed of the water is negligible" footnote), and *figure-load* (whether quantities are stated in prose, marked on a figure, or both). Those are the difficulty levers; noop is not.

Phase γ fixes the harness for these. Phase δ (separate doc, downstream) builds a deterministic vision-LM grader against the gold-standards Phase γ produces.

---

## 1. Scope and shape

Phase γ has three parallel workstreams, listed in dependency order:

- **Workstream A — Harness primitives.** New visual builders, schema additions, lint rules. Independent sub-tasks; parallelizable across sub-agents.
- **Workstream B — Rendering pipelines.** Multi-target output (text / Markdown / LaTeX / SVG / PNG / PDF). Some sub-tasks depend on Workstream A primitives existing.
- **Workstream C — Gold-standard exemplars.** Eight templates re-authored or newly authored using everything from A and B. Sequenced after A and B mostly land; Alex authors with light agent assist.

**Out of scope for Phase γ:**
- The grader-skill itself (Phase δ).
- Concrete grader rubric design (waiting on more template data points before locking the rubric).
- Physics and chemistry domain templates (separate skill, separate roadmap).
- Re-grading or re-fixing the existing 633-template corpus (Phase ε; needs the grader to exist first).

**In scope, but flagged as small/cheap deferrals if they bloat:**
- The `simplifications:` lint rule that flags hard-tier templates with no assumption lift (heuristic, may produce false positives).
- The Markdown-table renderer's MathJax compatibility (depends on which Markdown flavor downstream consumers want; defer if ambiguous).

---

## 2. Workstream A — Harness primitives

### A.1 `TableSVG` builder

A visual-sandbox builder analogous to existing `PlotSVG` and `CircuitSVG`. Renders function-value tables, data tables, and matrix displays as SVG.

**Input shape:**

```python
table = TableSVG(
    headers=["x", "f(x)", "f'(x)"],
    rows=[
        [0, 2.0, "<auto>"],          # "<auto>" cells get computed via solution-side
        [1, 2.5, 0.6],
        [2, 3.1, 0.7],
        [3, 3.9, "..."],             # ellipsis literal
    ],
    highlight_cells=[(1, 1), (2, 1)],   # row, col indexed; renders with bg fill
    column_align=["center", "right", "right"],
    caption="Tabulated values of f and its derivative",
)
```

**Output:** SVG with proper cell borders, monospace numerical alignment, configurable caption, optional row/column dividers. Default styling matches the existing PlotSVG visual idiom (clean, schoolbook, no gratuitous color).

**Variants to support in v1:**
- `FunctionValueTable` — convenience wrapper for the canonical Stewart-style "x | f(x)" two-column case
- `MatrixTable` — for K12 N9 templates (matrix display with bracket characters `[ ]`, optional row/column index labels)
- `DataTable` — generic; supports mixed numeric and string cells

**Variants explicitly deferred to v2:**
- Sortable / interactive tables (we don't render to interactive surfaces)
- Tables with embedded sparklines or per-cell color gradients
- Multi-page tables with continuation markers

**Required hooks:**
- `to_svg() -> str` — primary output
- `to_text() -> str` — Unicode box-drawing fallback for text-rendering pipeline (see B.1)
- `to_markdown() -> str` — pipe-table form for the Markdown pipeline (see B.2)
- `to_latex() -> str` — `tabular` environment for the LaTeX pipeline (see B.3)

These four output methods are non-negotiable. The whole point of TableSVG is that the same input description produces all four target forms losslessly.

### A.2 `FigureSVG` primitives for K12 canon

A small library of parametric geometry-builders for the figure-load-bearing problems. **Each is its own builder class**, not a single mega-builder, so the agent can call e.g. `RiverbankFigure(width=3, downstream=8, ...)` directly.

Minimum viable set for Phase γ (eight builders):

1. **`SectorFigure`** — circular sector with parametric center angle and radius. Optional cutout angle (for the "cone-cup-from-paper" problem in image #2 of the post-mortem screenshots). Labels on radii and arc.

2. **`ConeNetFigure`** — sector-to-cone unfold pair (the sector becomes a cone of derived radius and height). Useful for the cup-volume optimization problem.

3. **`RiverbankFigure`** — Stewart's two-bank-with-paths setup. Parameters: river width, downstream distance to target, optional landing-point variable `x`, label set. The figure is *load-bearing* — without it, the prose can't describe "row to point D between C and B" sensibly.

4. **`OptimizationRegionFigure`** — shaded feasibility region in 2D. Parameters: list of constraint lines (ax + by ≤ c form), optional shading style, optional vertex labels. For K12 linear-programming and constrained-max problems.

5. **`RelatedRatesGeometry`** — a small dispatcher that produces the canonical setups: `ladder_sliding`, `cone_draining`, `balloon_inflating`, `shadow_lengthening`, `boat_pulled_to_dock`. Each is parameterized by the relevant geometry (ladder length, cone half-angle, etc.) and renders the labeled diagram.

6. **`FunctionGraphFigure`** — generic plot of f(x) over a domain, with optional marked points, tangent lines, secant lines, area-under-curve shading, x-axis interval highlighting. Distinct from `PlotSVG` (which is general-purpose) by being calibrated for *problem-statement* graphs where students reason from the figure (read off intercepts, count intersections, identify monotonicity intervals).

7. **`AxesAnnotation`** — utility class for marking axis intercepts, asymptotes, and critical points on any figure produced by 6. Used as a method on FunctionGraphFigure, not standalone, but called out separately because the cooling-template visual failure was largely an axis-annotation problem (dangling labels, no leader lines).

8. **`TriangleFigure`** — labeled triangle with sides, angles, optional altitude/median/angle-bisector. For K10 and K11 trig-application templates. Parameters: side lengths or angles (one set determines the other up to congruence). Auto-detects which sides/angles to label based on what's given.

**Required hooks for each builder** (mirroring TableSVG):
- `to_svg() -> str` — SVG source
- `to_text() -> str` — ASCII-art or text-description fallback (e.g., "Triangle ABC with sides a=3, b=4, c=5; right angle at C"). Won't be pretty, but downstream text-only consumers need *something*.
- `to_latex() -> str` — TikZ or `pgfplots` source where applicable; falls back to a `\fbox{[Figure: description]}` for builders without a TikZ analog.

PNG output is handled by the rendering pipeline (B.4), not per-builder.

### A.3 Schema additions

Three schema fields. Each defaults to absent/empty so existing templates are unaffected.

#### A.3.a `simplifications:` block

A list of stated simplifying assumptions, each tagged with which difficulty tiers omit it. Renderer suppresses per-tier; the rendered prose includes only the assumptions for the current tier.

```yaml
simplifications:
  - text: "Assume air resistance is negligible."
    omit_at: [hard]
  - text: "Use g = 9.8 m/s² for gravity."
    omit_at: []                       # always shown
  - text: "Assume the river current is negligible compared to rowing speed."
    omit_at: [medium, hard]           # only easy tier sees this
```

The renderer concatenates non-omitted assumptions into the prose at a `{{ simplifications }}` Jinja variable, or omits the section entirely if all are stripped.

**Lint rule:** `simplification_lift_missing` (warning, not error) — flags hard-tier templates that have no `omit_at: [..., hard]` entries. Heuristic: hard tier should usually suppress at least one assumption visible at easy/medium. Override allowed via `notes:` justification.

#### A.3.b `figure_load:` axis

Per-template or per-tier value indicating how load-bearing the figure is.

```yaml
visual:
  format: python
  figure_load: load_bearing       # one of: none | decorative | partial | load_bearing
  source: |
    ...
```

Per-tier override:

```yaml
visual:
  format: python
  figure_load:
    easy: decorative
    medium: partial
    hard: load_bearing
  source: |
    ...
```

**Semantics:**
- `none` — no figure
- `decorative` — figure illustrates but isn't required (cooling template's exponential-decay plot)
- `partial` — some quantities only readable from the figure; prose covers the rest
- `load_bearing` — problem unsolvable without the figure

**Lint rule:** `figure_load_inconsistent` (warning) — flags `load_bearing` templates whose prose contains all the parametric values needed to solve (suggests the figure isn't actually load-bearing); flags `none`/`decorative` templates whose prose references "the figure shows..." or "from the diagram..." (suggests the figure *is* load-bearing but the schema disagrees).

#### A.3.c Retire `noop_clauses:` from the schema

Mark deprecated; lint warns on use; remove entirely after one minor-version cycle. Update §6 of `MATHBOT_PROBLEMS_PROPOSAL.md` v2: remove rule #12, retire structural-tag T16, replace with **T18 `assumption_omission`** documented as the K12-appropriate analog.

### A.4 Lint rule additions

Beyond the per-feature lint rules above, three corpus-wide rules:

- `axis_range_artifact` (warning) — for visuals using `PlotSVG` or `FunctionGraphFigure`, flag axis ranges that look like `min(data)`/`max(data)` rather than rounded values. Heuristic: any axis bound whose decimal representation has more than 2 significant figures and isn't a multiple of 5/10/100/etc. earns the flag. Catches the cooling-template "0 to 37.85" failure.

- `visual_prose_contradiction` (warning) — heuristic check that the alt_text and the prose don't make contradictory claims. Phase γ ships a minimal version: token-level check that key nouns from prose appear in alt_text. Sophisticated semantic checking is Phase δ (vision-LM grader).

- `feature_declared_but_unused` (info) — flag templates that declare a schema feature (e.g., `simplifications:`) but no fixture exercises the variant the feature creates. Catches the "noop_clauses defined but no `inject_noop: true` fixture" failure pattern in the demo templates.

---

## 3. Workstream B — Rendering pipelines

The harness today is SVG-first with PNG-via-rasterize. K12 needs five output forms, each driven by a different consumer:

| Pipeline | Consumer | Format | Status |
|---|---|---|---|
| Text | Plain-text JSON benchmark, terminal preview | UTF-8 with Unicode math symbols | Partial (no tables) |
| Markdown | Human review, GitHub rendering | GFM + MathJax-compatible LaTeX | Missing |
| LaTeX | Academic-paper export, journal-style PDF | Standalone `.tex` + compile | Missing |
| SVG | Web embed, vector preview | SVG 1.1 | Exists |
| PNG | Vision-LM grader, raster preview | PNG @ 2x DPI | Exists |
| PDF | Print preview, archival | PDF via LaTeX or via SVG-print | Missing |

### B.1 Text-rendering pipeline

**Goal:** every template renders to a plain-text form usable in a terminal or copy-pasted into a non-rendered text field.

Components:
- Math expressions render via Unicode (`x²` not `x^2`, `≤` not `<=`, `∫` not `int`, `→` not `->`, full Greek alphabet).
- Tables render via box-drawing characters (`┌─┬─┐ │ │ │ ├─┼─┤ └─┴─┘`) — TableSVG.to_text() handles this.
- Figures render to a one-line ASCII description from `FigureSVG.to_text()` since real ASCII-art figures don't help a text consumer.
- Inline math like `T(t) = T_amb + (T_0 - T_amb) e^{-kt}` becomes Unicode `T(t) = T_ambient + (T_0 - T_ambient) e^(-kt)` — exponents via Unicode superscripts where available, parenthesized otherwise.

**Required:** a `render_text(template, fixture_seed) -> str` function exposed via the CLI as `mathbot generate --format text`.

### B.2 Markdown-rendering pipeline

**Goal:** every template renders to GitHub-Flavored-Markdown for human review, GitHub PR comments, and the eventual Markdown-based corpus browser.

Components:
- Math expressions wrapped in `$...$` (inline) or `$$...$$` (block) for MathJax/KaTeX rendering on GitHub.
- Tables as GFM pipe-tables — TableSVG.to_markdown() handles this.
- Figures embedded as `![alt_text](data:image/png;base64,...)` data URIs OR as relative paths to a sibling `.png` if the renderer is writing to a directory. CLI flag `--embed-images` chooses which.
- Code blocks for any verbatim ODE / equation snippets.
- Front-matter optional (`---\nid: ...\ndifficulty: ...\n---`) for downstream tooling.

**Required:** `render_markdown(template, fixture_seed, embed_images=True) -> str` exposed via `mathbot generate --format markdown`.

**Cross-platform note:** GitHub MathJax is *almost*-but-not-quite standard LaTeX. `\frac`, `\sqrt`, basic operators all work; `\begin{align}` does not. Stick to the GitHub-supported subset and document the constraint.

### B.3 LaTeX-rendering pipeline

**Goal:** every template renders to a self-contained `.tex` source compilable to PDF via `pdflatex` or `xelatex`.

Components:
- Math expressions native LaTeX, no escaping (`$\int_0^t e^{-kx}\,dx$`).
- Tables via TableSVG.to_latex() → `tabular` environments inside `table` floats.
- Figures inline via TikZ where the FigureSVG builder supports it; via `\includegraphics{...png}` for builders without a TikZ analog.
- Document preamble: `\documentclass{article}`, geometry settings, AMS-math, AMS-symbols, TikZ, `siunitx` for unit-bearing answers (`\SI{0.05}{\per\minute}` formats `0.05 1/min` as a clean `0.05 min⁻¹`).
- Each rendered template is a complete document by default; CLI flag `--fragment` outputs body-only for inclusion in larger documents.

**Required:** `render_latex(template, fixture_seed, fragment=False) -> str` exposed via `mathbot generate --format latex`.

**Why this matters for the juicy renders:** LaTeX is where formulas look properly typeset. The N15 cooling template's prose says `dT/dt = -k (T - T_ambient)` in plain text; in LaTeX it's `\frac{dT}{dt} = -k(T - T_{\text{ambient}})` with proper Leibniz notation. The vision-LM grader (Phase δ) will be much happier looking at properly typeset math, and the human-review experience is night-and-day.

### B.4 PDF-rendering pipeline

**Goal:** every template renders to a standalone PDF file.

Two implementation paths; pick one in Phase γ planning:

**Path 1: LaTeX → PDF.** Compile `render_latex(..., fragment=False)` via `pdflatex` or `tectonic`. Pros: highest typographic quality; native vector math; `siunitx` units. Cons: requires LaTeX toolchain in the build environment; slower (1–2 sec per render).

**Path 2: SVG → PDF.** Render SVG and convert via `cairosvg` or `weasyprint` from a Markdown intermediate. Pros: faster; no LaTeX dep. Cons: math is rasterized inside SVG (KaTeX→SVG step needed); typography is "OK" not "beautiful."

**Recommendation:** Path 1, with `tectonic` as the compiler (single-binary, network-free, deterministic). Slower per-render is acceptable because PDF is the lowest-frequency output form. Path 2 as a fallback flag for environments without a LaTeX toolchain.

**Required:** `render_pdf(template, fixture_seed) -> bytes` exposed via `mathbot generate --format pdf`.

### B.5 Math-expression rendering as a shared layer

All five pipelines need to render math expressions, and they all need to render the *same* mathematical content into different surface forms. Centralize this:

```python
class MathExpr:
    """Internal representation of a math expression with multi-target rendering."""
    def __init__(self, sympy_expr_or_string): ...
    def to_text(self) -> str:        # Unicode
    def to_markdown(self) -> str:    # MathJax-compatible LaTeX in $...$
    def to_latex(self) -> str:       # raw LaTeX, no delimiters
    def to_svg(self) -> str:         # KaTeX → SVG render
    def to_png(self) -> bytes:       # KaTeX → SVG → rasterize
```

Templates expressing math via Jinja `{{ expr }}` go through this class. The solution-side sympy expressions (the N16 RLC `Answer = sp.simplify(sol.rhs)` case) get wrapped in a MathExpr automatically when the formatter detects sympy types.

This is the single biggest leverage point in Phase γ. **Without a centralized MathExpr class, the four math-renderers drift and the corpus produces inconsistent math typography across formats.** The hours spent on this class pay back across every K12 template.

### B.6 Renderer CLI surface

After Phase γ, the CLI surface is:

```bash
# Text (current default)
mathbot generate --input <path> -s <seed> -o text

# Markdown with embedded images
mathbot generate --input <path> -s <seed> -o markdown --embed-images

# LaTeX fragment for inclusion
mathbot generate --input <path> -s <seed> -o latex --fragment

# Standalone LaTeX document
mathbot generate --input <path> -s <seed> -o latex

# PDF via LaTeX
mathbot generate --input <path> -s <seed> -o pdf

# SVG (visual block only)
mathbot generate --input <path> -s <seed> -o svg

# PNG @ 2x DPI
mathbot generate --input <path> -s <seed> -o png --dpi 2x

# Multi-format batch — produce text + markdown + pdf + png in one render pass
mathbot generate --input <path> -s <seed> --formats text,markdown,pdf,png --output-dir <dir>
```

The multi-format mode (`--formats`) shares the variable-generation and solution-evaluation phases across formats and only re-invokes the renderer per format, so it's roughly 1.2x the cost of a single-format render rather than 5x.

---

## 4. Workstream C — Gold-standard exemplars

**Eight templates, authored by Alex with light agent assist, exercising every Phase γ harness feature.** These become the visual and structural reference for the rest of the corpus going forward, and the calibration set for the Phase δ grader rubric.

Each gold-standard ships with all six rendering forms checked into the repo (text, markdown, LaTeX, SVG, PNG, PDF) so reviewers can see the full output stack. Each ships with a `notes:` block explaining the design choices.

### Gold-standard set

1. **`k12_optimization_cup_capacity_anchor.yaml`** — the cone-cup-from-sector problem (image #2 of the post-mortem screenshots). Topic: `k12.calculus.optimization`. Uses `SectorFigure` + `ConeNetFigure` side-by-side; `figure_load: load_bearing` (the cutout angle is only readable from the figure). `simplifications:` lifts an "assume the paper has no thickness" assumption between medium and hard tiers. Solution uses sympy to derive volume as a function of cutout angle, optimize via critical-point analysis. Hard tier additionally asks for the *ratio* of cutout angle to total angle, exercising T17 inverse-direction.

2. **`k12_optimization_riverbank_anchor.yaml`** — Stewart Example 4 (image #1 of the post-mortem screenshots). Topic: `k12.calculus.optimization`. Uses `RiverbankFigure` with `figure_load: load_bearing`. Easy tier states "we assume the river current is negligible" explicitly; hard tier omits this assumption (student must either declare it or solve with a current term). Solution uses sympy to find critical-point landing position; checks endpoint feasibility (the "cross directly" and "row directly" boundary cases).

3. **`k12_related_rates_cone_draining_anchor.yaml`** — water draining from inverted cone, find rate of water-level fall. Topic: `k12.calculus.related_rates`. Uses `RelatedRatesGeometry(setup='cone_draining')`. `figure_load: partial` (cone half-angle on the figure, drain rate in the prose). Demonstrates the T13 symbolic-chain and T14 formula-recall tags. Hard tier: cone is *frustum* not full cone, requiring an additional similar-triangles step to find the changing radius.

4. **`k12_riemann_sum_table_anchor.yaml`** — estimate ∫f(x)dx from a table of values via left/right/midpoint/trapezoidal rules. Topic: `k12.calculus.integrals`. Uses `TableSVG` for the function-value table. `figure_load: load_bearing` (the f-values are only in the table, not in prose). Asks for *which* rule gives the best estimate, exercising T15 method-selection. Hard tier: table has irregular x-spacing, ruling out vanilla Riemann sums and forcing the trapezoidal-with-irregular-intervals formula.

5. **`k11_trig_beat_frequency_anchor.yaml`** — superposition of two near-frequency tones via sum-to-product identity. Topic: `k11.trigonometry.identities`. Uses `FunctionGraphFigure` to plot the carrier and envelope with `AxesAnnotation` marking the beat period. `figure_load: partial` (frequencies in prose, beat period readable from figure). Demonstrates the trig-identity-as-tool-not-target principle from N11.

6. **`k10_conic_whispering_gallery_anchor.yaml`** — elliptical whispering gallery with foci, sound reflection. Topic: `k10.geometry.conic_sections`. Uses a custom inline `EllipseFigure` (gold-standard set surfaces this as a candidate addition to `FigureSVG` — if it's broadly useful, promote to A.2 in a Phase γ-revision). `figure_load: decorative` (parameters in prose, figure shows geometry). Demonstrates the LaTeX pipeline producing properly typeset ellipse equations `\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1`.

7. **`k12_first_order_ode_cooling_anchor.yaml`** — *redo* of the Phase β demo. Same problem and same math; fixed visuals (rounded axis bounds, leader lines on labels, marker provably on the curve) and proper inline LaTeX for the ODE. Drops `noop_clauses`, adds `simplifications:` lift between easy ("assume the room temperature is constant") and hard. This is the *before/after* exemplar — direct comparison to the Phase β version demonstrates what Phase γ buys.

8. **`k12_rlc_critical_damping_anchor.yaml`** — *redo* of the Phase β demo. Schematic corrected (source removed entirely; circuit is just R-L-C in a loop with capacitor showing initial charge annotation `q(0) = q₀`). LaTeX pipeline produces the proper `\ddot{q} + \frac{R}{L}\dot{q} + \frac{1}{LC}q = 0` characteristic equation. `compare: symbolic` exercise via `MathExpr` + sympy equivalence.

### Gold-standard process discipline

For each gold-standard:

- Author the YAML by hand (Alex), agent-assisted only for the solution-code sympy mechanics.
- Render all six output forms via the new pipeline.
- Manually inspect each form. *Especially the PNG.* Treat the rendered output as the deliverable, not the YAML.
- Write a `notes:` block explaining: which harness features it exercises, which design choices were deliberate vs. default, what the agent should *not* copy from this template.
- Commit alongside a `README.md` in `src/templates/_gold_standards/` that indexes the eight and cross-references which features each demonstrates.

The gold-standards are *not* part of the eval corpus by default. They live in `_gold_standards/` (underscore-prefixed to sort first and signal "not for normal sampling") and are excluded from `mathbot generate` random selection unless explicitly requested via `--include-gold-standards`.

---

## 5. Sequencing and dependencies

```
┌─────────────────────────────────────────────────┐
│ A.3 Schema additions (simplifications:,         │
│      figure_load:, retire noop_clauses)         │  ← starts immediately, no deps
└─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│ A.4 Lint rule additions                         │  ← needs A.3 schemas
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ B.5 MathExpr shared layer                       │  ← starts immediately, no deps
└─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│ B.1 Text  │  B.2 Markdown  │  B.3 LaTeX        │  ← parallelizable across sub-agents,
│  pipeline │   pipeline     │   pipeline         │     each depends on B.5 + own scope
└─────────────────────────────────────────────────┘
            │            │            │
            ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│ B.4 PDF pipeline (LaTeX → PDF via tectonic)     │  ← needs B.3
│ B.6 CLI surface                                 │  ← needs B.1/B.2/B.3/B.4
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ A.1 TableSVG builder                            │  ← needs B.5 for math cells
│ A.2 FigureSVG primitives (8 builders)           │  ← needs B.5 for inline labels;
│                                                 │     parallelizable across builders
└─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│ Workstream C — Gold-standard exemplars (8)      │  ← needs all of A and B
└─────────────────────────────────────────────────┘
```

**Critical-path:** B.5 MathExpr → B.3 LaTeX → A.1 TableSVG → C.4 Riemann sum gold-standard. Roughly the longest dependency chain, so prioritize MathExpr early.

**Parallelizable surface:**
- Schema additions (A.3) — single sub-agent, small scope.
- Eight FigureSVG builders (A.2) — eight sub-agents, one per builder.
- Three text-flavor pipelines (B.1, B.2, B.3) — three sub-agents.
- TableSVG (A.1) — single sub-agent, but four output methods so could be sub-decomposed if needed.
- Lint rules (A.4) — one sub-agent for all four new rules.

**Estimated total work:** Phase γ is roughly 14–18 sub-agent tasks if maximally parallelized; rough total Claude-Code-token budget on the order of [Alex's call, depends on his subscription cap]. Gold-standards are sequential and Alex-driven, so they're more wall-clock than token cost.

---

## 6. Acceptance criteria

Phase γ is complete when all of the following are true:

1. The eight gold-standard templates exist in `src/templates/_gold_standards/`, each with all six rendered output forms checked in.
2. `mathbot lint --strict` passes on the gold-standards and on the existing 633-template corpus.
3. `mathbot generate --formats text,markdown,latex,pdf,svg,png` produces all six outputs for any template in the corpus, with no per-format crashes.
4. A K12 template author (Alex or a coding agent) can produce a Riemann-sum, optimization-with-sector, related-rates, or beat-frequency template using only the documented harness features (no inline workarounds, no `# TODO: TD-X.Y` markers).
5. The LaTeX renders look *good* (Alex's call; the `_gold_standards/` PDFs are the reference).
6. The Phase β demo templates (cooling, RLC) have been re-authored as gold-standards #7 and #8; the original Phase β versions are either upgraded in place or moved to a `_legacy/` directory with a deprecation note.
7. `noop_clauses` is removed from the schema (or marked deprecated with a removal date in CHANGELOG).
8. `MATHBOT_PROBLEMS_PROPOSAL.md` v2 is updated: §6 rule #12 removed, T16 retired, T18 `assumption_omission` added with documentation pointing at gold-standards #1, #2, #7 as exemplars.

When all eight criteria are met, Phase δ (grader-skill design) can begin against the gold-standard set as its calibration corpus.

---

## 7. Non-goals and explicit deferrals

- **Interactive visualizations.** No JS, no canvas, no WebGL. Static rendering only. Web embeds are SVG-static.
- **3D figures.** Where K12 N10 vectors-3D needs a "drone above terrain plane" diagram, render an isometric 2D projection. Real 3D rendering is out of scope.
- **Animation.** No GIF / MP4 / SVG-animation outputs. If a template's natural exposition is animated (e.g., showing the related-rates motion), produce a multi-panel SVG showing snapshots instead.
- **Per-template custom visual builders.** If a template needs something the eight `FigureSVG` builders don't cover, the answer is "extend the builders, not inline a one-off." Inline custom SVG via `format: svg` remains supported as an escape hatch but lint flags it as `custom_visual_inline` (info, not warning) so the corpus tracks where the standardized builders need extension.
- **The grader.** Phase δ. Out of scope.
- **Re-grading the existing corpus.** Phase ε. Out of scope. The existing 633 templates continue to work; new templates and gold-standards use the new features.

---

## Appendix: open questions for Alex before kickoff

1. **PDF pipeline path:** Path 1 (`tectonic`-based LaTeX→PDF) or Path 2 (SVG→PDF via `cairosvg`)? Recommendation is Path 1, but it adds a system dep.

2. **Markdown flavor:** GitHub-Flavored-Markdown (with the GitHub MathJax subset) or CommonMark + KaTeX? GFM is simpler and matches where humans actually review; CommonMark+KaTeX is more standard. Recommendation is GFM.

3. **Gold-standard `_gold_standards/` location:** under `src/templates/` (visible to lint, excluded from random sampling) or in a sibling top-level `gold_standards/` directory (separate, manually invoked). Recommendation is under `src/templates/` with the underscore prefix.

4. **`figure_load` lint enforcement:** warning or error? Warning is friendlier for in-flight authoring; error blocks CI. Recommendation is warning, promote to error in Phase ε after the corpus settles.

5. **Should the Phase β cooling and RLC templates be upgraded *in place* (file path unchanged, just fixed) or moved to `_gold_standards/` and the originals deleted? Either way, no data loss — it's about whether the file paths in CHANGELOG and external references stay valid. Recommendation is "upgrade in place; copy to `_gold_standards/` as the canonical reference; the corpus file is an exemplar of the gold-standard."