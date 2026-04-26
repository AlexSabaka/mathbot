# Mathbot Plugin

Procedurally generated K1-K12 multi-step math word problems for the GoL Benchmark suite. Backed by the mathbot corpus (640 hand-authored Jinja templates spanning arithmetic, fractions, decimals, geometry, statistics, algebra, and more) — every problem is deterministic from a seed and ships with a verifiable expected answer.

## Wiring

This plugin lives inside the mathbot repo at `mathbot/gol_plugin/` and is exposed to gol_eval via a symlink:

```bash
ln -s /path/to/mathbot/gol_plugin /path/to/gol_eval/src/plugins/mathbot
```

`PluginRegistry` auto-discovers it as `task_type="mathbot"`. The generator shells out to the mathbot CLI (`uv run --project <mathbot_root> mathbot batch …`) at test-set generation time — keeping mathbot's `src.*` package namespace cleanly separated from gol_eval's.

## Configuration

| Field | Type | Notes |
|---|---|---|
| `grade` | select | `elementary` / `middle` / `high` / `college` / `university`. Empty = any grade. |
| `complexity` | select | `1` (easy), `2` (medium), `3` (hard). Empty = any. |
| `topic` | select | One of mathbot's 13 top-level topics (arithmetic, fractions, geometry, …). |
| `family` | text | Fine-grained problem family (~80 options). Advanced. |
| `num_steps` | number | Filter by solution step count (1-10). Advanced. |
| `mathbot_root` | text | Override the auto-detected mathbot project root. Advanced. |

## Parser

End-first via `parse_utils.re_search_last`. Strategy order, by confidence:

1. `latex_boxed` (0.95) — `\boxed{X}`
2. `markdown_bold` (0.90) — `**X**` (header bolds ending `:` skipped)
3. `answer_label` (0.85) — `answer:` / `final answer:` / `the answer is X`, with sentence-end truncation
4. `last_line` (0.50) — last non-empty line, fallback

## Evaluator

Mathbot answers span seven shapes: numeric, currency, percent, fraction, numeric-with-unit, pipe-joined multi-part, lettered (`(a) X, (b) Y`), key=value (`mean=82, sd=7.48`), and free string. The evaluator handles all of them with one rule:

- If the expected answer contains numeric tokens, every one must be present (with tolerance `±1e-3`) in the parsed answer span. Multiplicity is preserved.
- If the expected has no numeric tokens, fall back to a normalized substring match.
- We do NOT scan the full model response when the parser returned a non-empty span — that would credit numbers that only appeared in chain-of-thought reasoning.

Match types: `numeric_match`, `numeric_missing`, `substring_match`, `wrong`, `parse_error`.

`aggregate_results` reports per-shape and per-grade accuracy in addition to the overall score.
