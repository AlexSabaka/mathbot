# Physics domain (stub)

Physics template authoring is infrastructure-ready but not yet exercised. This file is a placeholder; populate from the SPEC + first authored exemplar when the first physics template lands.

## Infrastructure status

In place (Phase 5.3R):

- `pint` backbone via `Q_`, `ureg`, `get_pint_unit` in the sandbox (SPEC.md §9.2)
- Compound physics types: `density`, `energy`, `power`, `pressure`, `force`, `acceleration` — each rendered with the per-system canonical suffix
- Free-form `unit:` field on `VariableSpec` (SPEC.md §8.3) for one-off compound units (`m/s²`, `kg/m³`, `kPa·s`)
- `scipy.constants` is reachable via the `stats` import path's parent package, but **not yet surfaced as a top-level sandbox global**. Adding `from scipy import constants as const` to `safe_globals` in `src/solution_evaluator.py` is the minimum-viable next step before authoring physics templates that need G, c, h, ℏ, k_B, etc.

Not in place yet:

- 2D/3D vector primitives (Coulomb on a triangle, 2D collisions). When needed, surface `numpy.array` and `numpy.linalg` in `safe_globals`.
- `schemdraw` for circuit schematics. When the first circuit template lands, add as a hard dep, build a small builder library, and document here.
- Free-body-diagram (FBD) SVG library. Approach A (Jinja-rendered SVG with a small parameterized library of ~10 canonical layouts) is feasible; Approach B (Python builder classes via TD-3.1b) is the cleaner long-term answer.
- Wave/trajectory plots — render at *authoring time* with matplotlib and ship the SVG; don't put matplotlib at runtime.

## Authoring scope (when ready)

The realistic Phase-1 core is 80-100 families covering ~70% of every reference system's quantitative content:

- Kinematics 1D and 2D / projectiles
- Newton's laws / FBD / inclines
- Momentum 1D
- Energy / work
- Circular motion
- Gravitation / Kepler
- Simple harmonic motion
- Wave basics, Doppler, standing waves, Snell
- Thermal Q = mcΔT, ideal gas
- Electrostatics with point charges
- Capacitors, DC circuits (Ohm, series-parallel)
- Transformers
- Photoelectric effect, de Broglie
- Nuclear half-life, mass-energy
- Special relativity intro

Out of scope for procedural generation:

- Lab design and error analysis
- Qualitative modern physics ("describe and justify")
- NGSS performance expectations
- ~30-40% of the formal curriculum that's qualitative or essay-graded

## Antipatterns specific to physics

Documented as they emerge. Initial concerns to watch for:

1. **Sign conventions in lens/mirror problems.** Numeric is clean but sign-convention errors (object distance positive vs. negative, image distance for virtual images) are subtle. Pin the convention in the problem text or pick parameters that make the sign unambiguous.

2. **Significant figures.** Physics curricula often grade on sig-figs. Until a sig-fig policy lands, set `Answer` formatting to a fixed decimal place that matches the dominant input precision. Document the policy in `metadata.notes`.

3. **Prefix arithmetic.** Singapore A-level explicitly mandates p/n/μ/m/c/k/M/G/T prefix arithmetic. Use pint's prefix support rather than inventing scaled units.

4. **Vector vs. scalar answers.** When a problem asks for "velocity" and the answer is a vector, format requires both magnitude and direction. Until 2D vector primitives land, decompose into magnitude + angle in two `Answer` variables.

## When the first physics template lands

Update this file with:

- A canonical recipe in `sandbox_recipes.md` for the most-common pattern (likely kinematics or Ohm's law)
- The physics-specific antipattern catalog (informed by the first 5-10 templates)
- A template-by-template inventory of required visuals and which ones are blocked on schemdraw / FBD library work
- The exemplar template path so future authors can read it before starting
