# Changelog

All notable changes to the Mathbot project are documented in this file.

---

## [0.1.3] - 2026-04-22 - Corpus cleanup, anchor convention, K7-K12 seeding

### Phase 1-3 — restore working state after the schema refactor

A previous session migrated variable schema from `{type, format}` to a single
`type` field, but the migration landed incompletely — the CLI was wired to a
nonexistent method, the loader rejected several valid template constructs,
and embedded test cases held stale expected values across ~80% of the corpus.
This release fixes the regressions:

- **CLI generate** — was calling `TemplateGenerator.generate_problem` which
  doesn't exist; now routes through `src/generator.py:generate_problem` for
  the default path and `TemplateGenerator.generate` for `--template-dir`.
- **YAMLLoader** — added `choice` to `VALID_TYPES`; added `school`, `furniture`,
  `other` to `VALID_ITEM_CATEGORIES`; relaxed `min > max` (was `min >= max`)
  to allow fixed-value ranges; routed load-failure messages to stderr.
- **VariableGenerator** — wired `choice` type (alias of `string` with choices);
  honored `choices` list on `integer` type; mapped new item categories to pools.
- **MathProblemProvider** — added `SCHOOL_ITEMS`, `FURNITURE_ITEMS`,
  `OTHER_ITEMS`; extended `WEEKDAYS` to include weekends; added `MONTHS` list.
- **Solution sandbox** — exposed `gcd` and `lcm` directly so 31 fraction and
  divisibility templates execute without per-template imports.
- **Batch CLI** — `--file` is now optional (stdout default); added `-s/--seed`
  for reproducibility; per-item retry on no-template-match instead of fatal.

### Phase 4 — corpus cleanup, anchor convention, K7-K12 expansion

**Stage 1: 278 deletions and topic harmonization.** Six sub-agents reviewed
the 892-template corpus by topic slice. Deleted templates fell into three
buckets: trivial range-variation duplicates (same operation, same step count,
only `min/max` ranges differ), off-grade content (45 K6 statistics templates
that were really K3-K4 arithmetic), and three structurally-unrecoverable
files (mislabeled rectangle area, missing variable, non-existent Jinja
filter). 51 surviving templates had bare or directory-mismatched topic
metadata (e.g. `topic: arithmetic` with no subtopic, or `topic: geometry.measurement`
in `measurement/`); now harmonized to `topic: <dir>.<subtopic>`.

**Stage 2: surgical test-answer regeneration.** Wrote
`scripts/refresh_test_answers.py` using `ruamel.yaml` round-trip mode (preserves
comments, key order, quoting). Replaces the broken
`migrate_templates.py --update-tests` (which gates on a no-longer-firing
format→type migration check and uses lossy `yaml.dump`). Multi-answer
templates were normalized: legacy `answer1/answer2/...` keys removed in favor
of a single pipe-joined `answer:` field (the only field the CLI test runner
actually reads).

**Stage 4.1: anchor convention.** Designated 330 lead variants as anchors via
`*_anchor.yaml` filename suffix — one per (grade, topic, family, difficulty)
quadruplet. Anchors are the canonical pattern for their quadruplet; new
templates added there should follow the anchor's style.

**Stage 4.2: 27 hand-authored seed templates.** Closed the K7-K12 coverage
gap and seeded all five spec-mandated families (`sequential_purchase`,
`rate_time`, `compound_growth`, `multi_person_sharing`, `area_perimeter_chain`).
Each template hand-authored against the patterns in
`mathbot-phase4-problem-proposals.md` (Singapore P5/P6 bar models, RME
contextual chains, CCSS multistep ratio/percent), parameterized so generated
values yield clean integer or 2-decimal answers. New domains seeded:
geometric series, calculus optimization, hypothesis testing, exponential
decay, linear regression, mathematical induction, vector geometry,
probability tree, geometric proof chains.

### Result

| Metric                            | Before | After             |
| --------------------------------- | ------ | ----------------- |
| Templates                         | 892    | 642               |
| Anchor templates                  | 0      | 358               |
| Templates that throw exceptions   | 15     | 0                 |
| Template self-test pass rate      | ~14%   | 100% (1311/1311)  |
| pytest                            | 28/35  | 35/35             |
| K7-K12 templates                  | 14     | 39+               |

### Tooling added

- `scripts/refresh_test_answers.py` — surgical test-answer regenerator
- `ruamel.yaml` added to dev deps for format-preserving YAML rewrites

### Tooling deprecated

- `migrate_templates.py --update-tests` — broken (no-op gate + lossy dump);
  will be removed in a future release. Use `scripts/refresh_test_answers.py`.

### Historical context — pre-alpha spec

The `.claude/CLAUDE.md` shipped with v0.1.0 contained the original
implementation specification: 9 math topics, 5 problem families, package
layout under `families/*.py`, and the "5-10 templates per family" target.
That spec served its purpose during initial implementation and the
subsequent Mustache → YAML+Jinja2 migration. As of v0.1.3 it is replaced
with a development guide describing the actual implementation —
templates live in `src/templates/<topic>/*.yaml` (not `families/*.py`),
the math-topic taxonomy is dotted (e.g. `arithmetic.addition`,
`geometry.area_composite`), and grades use the K1-K12 schema rather than
elementary/middle/high/college. The five spec-mandated families remain
the intent.

---

## [0.1.2] - 2026-01-30 - YAML+Jinja2 Migration Complete

### 🎉 Complete Migration to YAML+Jinja2 Template System

Full architectural migration from Mustache to YAML+Jinja2 with comprehensive template specification.

#### System Overhaul

- **YAML Template Format** - Structured metadata, variables, template, solution, and tests sections
- **Jinja2 Rendering** - Powerful template engine with filters and logic support
- **Multi-Answer Support** - Answer1, Answer2, Answer3 for problems with multiple outputs
- **Template Path Tracking** - All generated problems include source template path
- **Format System** - 9 format types: money, percentage, ordinal, length, weight, temperature, area, volume, speed

#### New Core Infrastructure

| Module | Purpose |
|--------|----------|
| `src/yaml_loader.py` | YAML parsing and validation with TemplateDefinition dataclass |
| `src/jinja_renderer.py` | Jinja2 environment with custom filters (choice, plural, format_money, etc.) |
| `src/variable_generator.py` | Type-aware value generation with format constraints |
| `src/solution_evaluator.py` | Python solution execution with multi-answer support |
| `src/template_generator.py` | Core generator with template discovery and path tracking |

#### Template Structure (v2.0)

```yaml
metadata:
  id: k6_medium_shopping_01
  grade: 6
  topic: arithmetic.shopping
  family: shopping
  difficulty: medium
  steps: 3

variables:
  name:
    type: person
  price:
    type: decimal
    format: money
    min: 5.0
    max: 20.0
  Answer:
    type: decimal
    format: money

template: |
  {{name}} bought items for {{price}}.
  Please solve this problem and provide your final answer.

solution: |
  Answer = price * 2

tests:
  - seed: 12345
    expected:
      answer: "$24.50"
```

#### Key Features

- **Template Specification** - Complete format documentation in `src/templates/SPEC.md` (source of truth)
- **Variable System** - 14 types: integer, decimal, fraction, person, location, store, restaurant, company, weekday, season, time, item, boolean, string
- **Format Constraints** - Automatic unit formatting (e.g., "45m", "$12.50", "15%")
- **Multi-Answer** - Problems can return multiple answers formatted as "Answer1 | Answer2 | Answer3"
- **CLI Options** - Added `--input` flag for generating from specific template file
- **Context Handling** - Templates have access to both raw values (for logic) and formatted values (for display)

#### Migration Summary

- **33 YAML templates** migrated from 33 Mustache templates
- **All 5 topics** converted: arithmetic (10), geometry (5), measurement (7), percentages (6), ratios (5)
- **Infrastructure modules** created: yaml_loader, jinja_renderer, variable_generator (6 new files)
- **Old modules removed** - variable_parser.py, template_helpers.py, template_loader.py (Mustache-specific)
- **Dependencies updated** - Removed chevron, added jinja2>=3.1.0, pyyaml>=6.0
- **Cleanup** - Removed 7 temporary test/verification scripts

#### Test Coverage

- **35/35 tests passing** (100% success rate)
- All templates validated and tested
- Multi-answer problems verified
- Format system tested (money, time, area, perimeter, speed)

#### Breaking Changes

- Template format changed from `.mustache` to `.yaml`
- Variable syntax changed from `{{name_person}}` to YAML structure
- Solution section now uses Python expressions instead of Mustache variables

#### Documentation

- **src/templates/SPEC.md** - Complete template format specification (moved from docs/INDEX.md)
- **Updated copilot-instructions.md** - Reflects new YAML+Jinja2 system
- **Grade-level examples** - docs/K1_PROBLEMS.md through docs/K12_PROBLEMS.md

---

## [0.1.1] - 2026-01-30 - Template-Driven Architecture

### 🚀 Major Refactoring: Pure Template-Driven Generation

Complete architectural shift from Python family classes to self-describing Mustache templates.

#### New System Overview

- **No more Python family classes** - All problem generation driven by `.mustache` templates
- **Self-describing variables** - Metadata embedded in variable names (e.g., `{{price_decimal_money_min_5_max_20}}`)
- **Computed answers** - Solution expressions evaluated from template's `---` section
- **Template helpers** - 8 Mustache lambdas for text formatting

#### New Core Modules

| Module | Purpose |
|--------|---------|
| `src/variable_parser.py` | Parses variable metadata from template names |
| `src/template_helpers.py` | Mustache helper functions (choice, plural, etc.) |
| `src/solution_evaluator.py` | Evaluates solution expressions for answers |
| `src/template_generator.py` | Main generator class, discovers and renders templates |

#### Template Format

```mustache
{{name_person}} bought {{qty_integer_min_2_max_5}} items for {{price_decimal_money_min_5_max_20}}.
---
total = {{qty}} * {{price}}
Answer = total
```

#### Migration Summary

- **30 templates migrated** from old structure to new naming convention
- **5 directories reorganized** by topic (arithmetic, geometry, measurement, percentages, ratios)
- **Old family directories removed** (sequential_purchase, rate_time, compound_growth, etc.)
- **Old Python family files deleted** (5 files in `src/families/`)

#### Backward Compatibility

- Family name aliases: `sequential_purchase` → `shopping`, `rate_time` → `travel`, etc.
- Grade mapping: `elementary` → k1-k5, `middle` → k6-k8, `high` → k9-k12
- Legacy variable inference for templates without metadata

#### Test Results

- **51/52 tests passing** (98% success rate)
- 1 known issue: `test_avoid_duplicates` needs more template variety

---

## [0.1.0] - 2026-01-28 - Initial Implementation

### 🎉 Project Setup Complete

Fully functional Python library for generating procedurally-created, multi-step math word problems.

#### Features Implemented

**Core Functionality:**
- Single problem generation with `generate_problem()`
- Batch generation with `generate_problems()`
- Available options query with `get_available_options()`
- Seed-based reproducibility
- Duplicate avoidance in batch mode

**Problem Families (5):**
1. `sequential_purchase` - Shopping scenarios with discounts
2. `rate_time` - Distance/speed/time problems
3. `compound_growth` - Interest/investment problems
4. `multi_person_sharing` - Ratio/splitting problems
5. `area_perimeter_chain` - Geometry problems

**Math Topics (9):**
arithmetic, percentages, fractions, ratios, algebra, geometry, quadratics, derivatives, powers_logs

**Configuration Parameters:**
- `complexity` (1-3)
- `grade` (elementary, middle, high, college, university)
- `math_topic` (9 topics)
- `problem_family` (5 families)
- `num_steps` (1-10)
- `seed` (for reproducibility)

#### Output Format

```json
{
  "test_id": "math_7912_sequential_purchase",
  "task_type": "multi_step_math",
  "config_name": "sequential_purchase_medium_arithmetic",
  "problem": "Natural language problem text...",
  "task_params": {
    "complexity": 2,
    "grade": "middle",
    "math_topic": ["arithmetic"],
    "problem_family": "sequential_purchase",
    "num_steps": 6,
    "expected_answer": "$37.20",
    "operations": ["multiply", "add"]
  }
}
```

#### Dependencies

- `faker>=20.0.0` - Realistic fake data
- `names>=0.3.0` - Person name generation
- `chevron>=0.14.0` - Mustache template rendering
- `inflect>=7.0.0` - Pluralization (added in v2.0)

---

## Project Structure

```
mathbot/
├── src/
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point
│   ├── cli_formatters.py       # Output formatters
│   ├── constants.py            # Configuration constants
│   ├── generator.py            # Public API
│   ├── providers.py            # MathProblemProvider (Faker)
│   ├── template_generator.py   # Template-driven generator
│   ├── template_helpers.py     # Mustache helpers
│   ├── template_loader.py      # Template loading utilities
│   ├── solution_evaluator.py   # Answer computation
│   ├── variable_parser.py      # Variable metadata parsing
│   ├── utils.py                # Utility functions
│   └── templates/              # Mustache templates
│       ├── arithmetic/         # Shopping problems
│       ├── geometry/           # Shape problems
│       ├── measurement/        # Travel problems
│       ├── percentages/        # Growth problems
│       └── ratios/             # Sharing problems
├── tests/
│   ├── test_cli.py
│   └── test_generator.py
├── docs/
│   ├── INDEX.md               # Template reference
│   └── K1-K12_PROBLEMS.md     # Grade-level examples
└── pyproject.toml
```

---

## Quick Start

```bash
# Install
uv sync

# Generate a problem
mathbot generate --grade middle --complexity 2 --topic arithmetic

# With seed for reproducibility
mathbot generate --seed 42

# Run tests
pytest
```

---

## Future Improvements

- [ ] Add more templates for broader coverage
- [ ] Implement template validation tool
- [ ] Add more variable types (date, temperature, weight)
- [ ] Support for symbolic algebra (SymPy integration)
- [ ] Multilingual template support
