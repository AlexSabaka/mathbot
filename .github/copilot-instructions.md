# Mathbot - AI Agent Guidelines

## Project Overview

Mathbot is a Python library that **procedurally generates multi-step math word problems** with realistic natural language context. It's designed to test LLM reasoning capabilities as well as general education and provide infinite problem variations with verifiable answers.

**Key Philosophy**: This is an agent-maintained project. Focus on extensibility, template diversity, and deterministic generation.

## Architecture

### Core Pattern: Family-Based Generation

```
generate_problem() → selects family → Family.generate() → returns structured dict
```

- **Families** (in `src/families/`): Self-contained problem generators implementing templates
- **Registry** (`FAMILY_REGISTRY` in `families/__init__.py`): Maps family names to classes
- **Each family**: Multiple template methods (~5-10) for variation within a category

### Output Structure (Critical)

All problems return this exact dict structure:
```python
{
    "test_id": "math_0001_family_name",
    "task_type": "multi_step_math",
    "config_name": "descriptive_config",
    "problem": "Natural language problem text",  # No intermediate steps
    "task_params": {
        "complexity": int(1-3),
        "grade": str,
        "math_topic": List[str],  # Can have multiple topics
        "problem_family": str,
        "num_steps": int,
        "expected_answer": str,  # Always string with units
        "operations": List[str]
    }
}
```

**Critical**: `expected_answer` is ALWAYS a string (e.g., "$6.94", "3/4", "y = 2x + 3", "3 hours 15 minutes")

## Key Constants & Compatibility

See `src/constants.py` for authoritative lists:

- **TOPIC_GRADE_COMPATIBILITY**: Defines which topics are appropriate for which grades
- **FAMILY_TOPIC_SUPPORT**: Maps families to topics they can meaningfully incorporate
- **COMPLEXITY_STEPS_RANGE**: Maps complexity levels to step ranges

When adding features, update these mappings to maintain consistency.

## Adding New Problem Families

1. Create `src/families/new_family.py` with class `NewFamilyFamily`
2. Implement `__init__(seed)` and `generate(complexity, grade, math_topic, num_steps)`
3. Add 5-10 template methods (e.g., `_template_shopping()`, `_template_online()`)
4. Register in `FAMILY_REGISTRY` in `families/__init__.py`
5. Update `PROBLEM_FAMILIES`, `FAMILY_TOPIC_SUPPORT` in `constants.py`
6. Add tests in `tests/test_generator.py`

**Template Pattern**: Use `faker` for cities/names, `names` for person names. Randomize ALL values (items, prices, quantities).

## Problem Quality Rules

Every generated problem MUST:
1. Have computable answer with reasonable precision (money: 2 decimals, etc.)
2. Use realistic values (no $7.3333... prices)
3. Maintain coherent context (matching names/items/locations)
4. Ensure positive intermediate values where appropriate
5. Match grade-level expectations (use compatibility maps)
6. Be deterministic from seed (same seed → identical output)

## Development Workflow

```bash
# Install (uses uv for dependency management)
uv sync

# Run tests
pytest

# Generate sample problems (CLI testing)
mathbot generate -c 2 -g middle -t arithmetic
mathbot generate -s 42 -o json --file problem.json
```

**Entry point**: `mathbot` command defined in `pyproject.toml` → `src.cli:main`

## Testing Patterns

- Test both single generation (`generate_problem`) and batch (`generate_problems`)
- Always test reproducibility: `seed=X` should produce identical output
- Test parameter validation (invalid complexity, grades, topics)
- Use `avoid_duplicates=True` in batch tests, but allow ~30% collisions

See [tests/test_generator.py](tests/test_generator.py) for patterns.

## Documentation Structure

`docs/` contains grade-level problem templates (K1-K12):
- These are REFERENCE templates showing problem patterns
- NOT used by code generation (families are self-contained)
- Use for inspiration when creating new templates
- [docs/INDEX.md](docs/INDEX.md) has variable naming conventions

## Key Utilities (src/utils.py)

- `round_money(value)`: Always use for currency (returns "$X.XX" string)
- `generate_price(min, max, step=0.25)`: Realistic prices with quarter increments
- `generate_percentage(min, max, step=5)`: Common percentages
- `round_to_decimals(value, decimals)`: Precise rounding using Decimal

**Critical**: Use `Decimal` for money calculations to avoid floating-point errors.

## CLI Structure

- Main command: `mathbot` (group command)
- Subcommands: `generate`, `batch`, `list`, `info`
- Formatters in `cli_formatters.py`: `format_pretty`, `format_json`, `format_text`
- All user-facing output uses click styling

## Common Pitfalls

1. ❌ Don't expose intermediate solution steps in output (internal only)
2. ❌ Don't use floating-point for money (`0.1 + 0.2 ≠ 0.3` issue)
3. ❌ Don't forget to update `FAMILY_REGISTRY` when adding families
4. ❌ Don't hard-code random values without considering seed reproducibility
5. ✅ DO use faker/names with same seed for consistent output
6. ✅ DO validate answer format matches expected format (string with units)
