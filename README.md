# Math Problem Generator

A standalone Python library for generating procedurally-created, multi-step math word problems with natural language context.

## Vibe Coding Disclaimer

This project almost fully developed and maintained by a coding agent.

## Installation

```bash
pip install mathbot
```

## Quick Start

CLI usage:

```bash
mathbot generate # random problem 

mathbot generate -c 2 -g middle -t arithmetic # medium complexity for middle grades topic of arithmetics

mathbot generate -s 42 -o json --file problem.json # set random generator seed 43 and output in json file

mathbot generate --complexity 3 --topic algebra --no-show-answer # highest complexity in algebra topic

mathbot generate --help # show help
```

Python usage:

```python
from mathbot import generate_problem, generate_problems

# Generate a single problem
problem = generate_problem(
    complexity=2,
    grade='middle',
    math_topic='arithmetic',
    problem_family='sequential_purchase',
    num_steps=3,
    seed=42
)

# Generate multiple problems
problems = generate_problems(
    n=10,
    complexity=2,
    grade='middle',
    avoid_duplicates=True
)
```

## Features

- A lot of template variations of multi-step math problems
- Configurable complexity, grade levels, and math topics
- Reproducible generation via seeds
- Natural language context using realistic data

## Development

```bash
# Install dependencies
uv sync

# Run tests
pytest
```
