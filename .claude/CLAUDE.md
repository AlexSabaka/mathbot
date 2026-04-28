# Mathbot — development guide

Procedural multi-step math word-problem generator. The corpus is a tree of
hand-authored YAML templates rendered with Jinja2 and post-processed by a
small Python sandbox; deterministic from a seed; produces problems with
verifiable answers for K1-K12.

## Quick start

```bash
uv sync                                                 # install deps + .venv (Python 3.12)
uv sync --extra png                                     # + cairosvg (for `mathbot rasterize`)
uv run pytest                                           # 93 tests
uv run mathbot generate -c 2 -g elementary -t arithmetic -s 42  # one problem
uv run mathbot batch 10 -s 1 -o json                    # 10 problems → stdout
uv run mathbot verify <path/to/template.yaml>           # validate one template
uv run mathbot test    <path/to/template.yaml>          # run its embedded tests
uv run mathbot lint                                     # whole-corpus audit (~5s)
uv run mathbot rasterize <dataset.json> [--dpi 150]     # SVG → PNG sidecars
```

`uv run` is the blessed entrypoint — the host shell's `VIRTUAL_ENV` may leak
in and trigger a benign warning when invoking `mathbot` directly.

## Repository layout

```text
src/
├── cli.py                  Click commands: generate, batch, verify, test, lint, health, rasterize, list, info
├── generator.py            Module API: generate_problem(), generate_problems()
├── template_generator.py   Loads + indexes templates; per-template generation
├── yaml_loader.py          YAMLLoader: schema validation + TemplateDefinition dataclass
├── jinja_renderer.py       Jinja2 env; locale-aware filters dispatch via i18n registry
├── variable_generator.py   Generates random values per VariableSpec.type; Faker locale-aware
├── solution_evaluator.py   Executes solution code in safe sandbox; formats answer
├── units.py                DISPLAY_UNITS table + pint registry; `get_pint_unit()` source of truth
├── providers.py            Thin loader → MathProblemProvider class attributes from data/pools.*.yaml
├── constants.py            MATH_TOPICS, PROBLEM_FAMILIES, GRADES enums
├── data/pools.<lang>.yaml  Per-locale entity pools (items, calendar, contexts) — `en` ships
├── i18n/languages.py       LanguageSpec registry; plural/ordinal/number_to_words per language
├── audit/                  `mathbot lint` and `mathbot health` implementation
└── templates/
    ├── SPEC.md             Canonical template spec (schema, sandbox, units, CLI, validation)
    └── <topic>/*_anchor.yaml + variants
scripts/
└── refresh_test_answers.py  Surgical test-answer regenerator (ruamel.yaml)
tests/                       pytest suite for CLI + generator API
```

## Where things live

This file is short on purpose. For anything beyond orientation, follow these pointers:

- **YAML schema, sandbox builtins, unit systems, i18n, multi-tier rules, anchor convention, output format, CLI reference, validation rules, spec-mandated families** → [src/templates/SPEC.md](../src/templates/SPEC.md). The single source of truth for everything reference-y. Browse the TOC: §3 top-level structure, §4 metadata, §5 variables, §6 template/Jinja gotchas, §7 multi-tier, §8 unit systems, §9 solution sandbox, §10 i18n, §11 tests, §12 visual, §13 output JSON, §14 CLI, §15 anchors, §16 authoring loop, §17 validation, Appendix families.
- **Authoring playbook** → `.claude/skills/template-author/` (auto-loads when work touches `src/templates/`). Cell-selection procedure, antipattern catalogue, sandbox recipes, every `mathbot lint` finding with its fix, math/physics/chemistry domain notes.
- **K7-K12 expansion roadmap** → [MATHBOT_PROBLEMS_PROPOSAL.md](../MATHBOT_PROBLEMS_PROPOSAL.md). P-XX entries the corpus is being built against; §6 is the don't-build list.
- **Per-grade rosters** → [docs/K1_PROBLEMS_DONE.md](../docs/K1_PROBLEMS_DONE.md) … [docs/K12_PROBLEMS.md](../docs/K12_PROBLEMS.md). What's authored vs planned at each grade.
- **Incomplete refactors / postponed decisions** → [TECHDEBT.md](../TECHDEBT.md).
- **Project history** → [CHANGELOG.md](../CHANGELOG.md) and `git log`.

## Spec-mandated families

Every problem ultimately maps to one of these (or a hybrid). See SPEC.md Appendix for the full taxonomy.

| Family                  | Pattern                                              |
| ----------------------- | ---------------------------------------------------- |
| `sequential_purchase`   | Multi-step shopping with discounts/budget            |
| `rate_time`             | Distance ↔ speed ↔ time, multi-segment               |
| `compound_growth`       | Interest, percent change chain over N periods        |
| `multi_person_sharing`  | Splitting amounts by ratio, transfer, or constraint  |
| `area_perimeter_chain`  | Geometry with area→side→perimeter or similar         |

## Known quirks

- Some legacy templates have unit-display bugs (e.g. trapezoidal-area
  problem stated in cm with answer in "meters"). Self-tests pass because
  they enshrine the buggy output as ground truth. Fix at the template
  level when you encounter one — don't patch the generator.
- `mathbot batch` retries up to `count * 10` times on no-template-match
  before giving up. If a `(grade, topic, family)` combo is sparse, the
  warning lands on stderr.
- The `.venv` warning about `VIRTUAL_ENV` mismatching is from the host
  shell, not the project — `uv run` works correctly regardless.
