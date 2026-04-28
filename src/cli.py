"""Command-line interface for math problem generator."""

import click
import json
import sys

from .generator import generate_problem, generate_problems, get_available_options
from .cli_formatters import format_pretty, format_json, format_text, format_list, format_info
from .constants import MATH_TOPICS, PROBLEM_FAMILIES, GRADES


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version='0.1.0', prog_name='mathbot')
def cli(ctx):
    """Math Problem Generator - Generate procedural math word problems.

    Generate single or batch problems with configurable complexity,
    grade levels, math topics, and problem families.
    """
    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option('-c', '--complexity', type=click.IntRange(1, 3),
              help='Complexity level (1=easy, 2=medium, 3=hard)')
@click.option('-g', '--grade',
              type=click.Choice(GRADES, case_sensitive=False),
              help='Grade level (elementary, middle, high, college, university)')
@click.option('-t', '--topic',
              type=click.Choice(MATH_TOPICS, case_sensitive=False),
              help='Math topic (arithmetic, percentages, etc.)')
@click.option('-f', '--family',
              type=click.Choice(PROBLEM_FAMILIES, case_sensitive=False),
              help='Problem family (sequential_purchase, rate_time, etc.)')
@click.option('-n', '--num-steps', type=click.IntRange(1, 10),
              help='Number of solution steps (1-10)')
@click.option('-s', '--seed', type=int,
              help='Random seed for reproducibility')
@click.option('-o', '--output',
              type=click.Choice(['json', 'pretty', 'text']),
              default='pretty',
              help='Output format (default: pretty)')
@click.option('--file', type=click.Path(),
              help='Save to file instead of stdout')
@click.option('--show-answer/--no-show-answer', default=True,
              help='Show answer in output (default: show)')
@click.option('--input', 'input_template', type=click.Path(exists=True),
              help='Generate from specific template file')
@click.option('--template-dir', type=click.Path(exists=True),
              help='Custom directory containing template files')
def generate(complexity, grade, topic, family, num_steps, seed, output, file, show_answer, input_template, template_dir):
    """Generate a single math problem.

    Examples:

      mathbot generate

      mathbot generate -c 2 -g middle -t arithmetic

      mathbot generate -s 42 -o json --file problem.json

      mathbot generate --complexity 3 --topic algebra --no-show-answer
      
      mathbot generate --input src/templates/geometry/k5_medium_geometry_01.yaml

      mathbot generate --template-dir custom_templates/ -t arithmetic
    """
    try:
        if input_template:
            # Generate from specific template file
            from pathlib import Path
            from .template_generator import TemplateGenerator
            from .yaml_loader import YAMLLoader
            
            template_path = Path(input_template)
            loader = YAMLLoader()
            template = loader.load_template(template_path)
            
            if not template:
                click.echo(click.style(f"Error: Failed to load template from {input_template}", fg='red'), err=True)
                if loader.errors:
                    for error in loader.errors:
                        click.echo(click.style(f"  ERROR: {error}", fg='red'), err=True)
                sys.exit(1)
            
            # Use custom template dir if provided
            templates_dir = Path(template_dir) if template_dir else None
            template_gen = TemplateGenerator(templates_dir=templates_dir, seed=seed)
            problem = template_gen._generate_from_template(
                template, seed=seed, template_path=template_path,
                requested_complexity=complexity,
            )
        else:
            # Regular generation with filters
            if template_dir:
                from pathlib import Path
                from .template_generator import TemplateGenerator

                template_gen = TemplateGenerator(templates_dir=Path(template_dir), seed=seed)
                problem = template_gen.generate(
                    complexity=complexity,
                    grade=grade,
                    math_topic=topic,
                    problem_family=family,
                    num_steps=num_steps,
                    seed=seed,
                )
            else:
                problem = generate_problem(
                    complexity=complexity,
                    grade=grade,
                    math_topic=topic,
                    problem_family=family,
                    num_steps=num_steps,
                    seed=seed,
                )

        # Format output
        if output == 'json':
            output_text = format_json(problem, show_answer)
        elif output == 'text':
            output_text = format_text(problem, show_answer)
        else:  # pretty
            output_text = format_pretty(problem, show_answer)

        # Write to file or stdout
        if file:
            with open(file, 'w') as f:
                f.write(output_text)
            click.echo(click.style(f"✓ Problem saved to {file}", fg='green'), err=True)
        else:
            click.echo(output_text)

    except ValueError as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('count', type=int)
@click.option('-c', '--complexity', type=click.IntRange(1, 3),
              help='Complexity level (1=easy, 2=medium, 3=hard)')
@click.option('-g', '--grade',
              type=click.Choice(GRADES, case_sensitive=False),
              help='Grade level')
@click.option('-t', '--topic',
              type=click.Choice(MATH_TOPICS, case_sensitive=False),
              help='Math topic')
@click.option('-f', '--family',
              type=click.Choice(PROBLEM_FAMILIES, case_sensitive=False),
              help='Problem family')
@click.option('-n', '--num-steps', type=click.IntRange(1, 10),
              help='Number of solution steps (1-10)')
@click.option('-s', '--seed', type=int,
              help='Random seed for reproducibility')
@click.option('--avoid-duplicates/--allow-duplicates', default=True,
              help='Avoid duplicate problems (default: avoid)')
@click.option('-o', '--output',
              type=click.Choice(['json', 'jsonl']),
              default='json',
              help='Output format (default: json)')
@click.option('--file', type=click.Path(),
              help='Output file path (default: stdout)')
def batch(count, complexity, grade, topic, family, num_steps, seed, avoid_duplicates, output, file):
    """Generate multiple math problems.

    COUNT is the number of problems to generate.

    Examples:

      mathbot batch 10

      mathbot batch 10 --file problems.json

      mathbot batch 50 -c 2 -g middle --file test_set.json

      mathbot batch 100 --topic arithmetic -o jsonl --file problems.jsonl
    """
    try:
        import random as _random

        rng = _random.Random(seed) if seed is not None else _random.Random()

        problems = []
        attempts = 0
        max_attempts = count * 10
        seen = set()

        bar_ctx = (
            click.progressbar(length=count, label='Generating problems', file=sys.stderr)
            if file else None
        )

        try:
            while len(problems) < count and attempts < max_attempts:
                attempts += 1
                item_seed = rng.randint(0, 2**31 - 1)
                try:
                    problem = generate_problem(
                        complexity=complexity,
                        grade=grade,
                        math_topic=topic,
                        problem_family=family,
                        num_steps=num_steps,
                        seed=item_seed,
                    )
                except ValueError:
                    # No templates matched this random combination; retry with a new seed.
                    continue

                if avoid_duplicates:
                    key = problem.get('problem')
                    if key in seen:
                        continue
                    seen.add(key)

                problems.append(problem)
                if bar_ctx is not None:
                    bar_ctx.update(1)
        finally:
            if bar_ctx is not None:
                bar_ctx.render_finish()

        if len(problems) < count:
            click.echo(
                click.style(
                    f"Warning: only generated {len(problems)}/{count} problems after {attempts} attempts",
                    fg='yellow'),
                err=True)

        # Serialize
        if output == 'jsonl':
            output_text = '\n'.join(json.dumps(p) for p in problems) + ('\n' if problems else '')
        else:  # json
            output_text = json.dumps(problems, indent=2)

        if file:
            with open(file, 'w') as f:
                f.write(output_text)
                if output == 'json':
                    f.write('\n')
            click.echo(click.style(f"✓ Generated {len(problems)} problems and saved to {file}", fg='green'), err=True)
        else:
            click.echo(output_text)

    except ValueError as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)
    except IOError as e:
        click.echo(click.style(f"File error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('category',
                required=False,
                type=click.Choice(['topics', 'families', 'grades', 'all']))
@click.option('-v', '--verbose', is_flag=True,
              help='Show descriptions for topics and families')
def list(category, verbose):
    """List available options (topics, families, grades).

    CATEGORY can be: topics, families, grades, or all

    Examples:

      mathbot list

      mathbot list topics

      mathbot list families -v

      mathbot list all
    """
    try:
        options = get_available_options()
        output_text = format_list(options, category, verbose)
        click.echo(output_text)

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('name')
def info(name):
    """Show detailed information about a topic or family.

    NAME should be a valid topic or family name.

    Examples:

      mathbot info arithmetic

      mathbot info sequential_purchase

      mathbot info geometry
    """
    try:
        options = get_available_options()
        output_text = format_info(name, options)
        click.echo(output_text)

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('template_path', type=click.Path(exists=True))
@click.option('--template-dir', type=click.Path(exists=True),
              help='Custom directory containing template files')
def verify(template_path, template_dir):
    """Verify template variable constraints and structure.

    TEMPLATE_PATH should be path to a YAML template file.

    Examples:

      mathbot verify src/templates/arithmetic/k3_easy_shopping_01.yaml

      mathbot verify custom_templates/my_template.yaml --template-dir custom_templates/
    """
    try:
        from pathlib import Path
        from .yaml_loader import YAMLLoader
        
        template_file = Path(template_path)
        loader = YAMLLoader()
        template = loader.load_template(template_file)
        
        errors, warnings = loader.get_validation_results()
        
        if template and not errors:
            click.echo(click.style(f"✓ Template '{template.id}' is valid", fg='green'))
            click.echo(f"\n  Grade: {template.grade}")
            click.echo(f"  Difficulty: {template.difficulty}")
            click.echo(f"  Family: {template.family}")
            click.echo(f"  Steps: {template.steps}")
            click.echo(f"  Variables: {len(template.variables)}")
            click.echo(f"  Tests: {len(template.tests)}")
            
            if warnings:
                click.echo(click.style(f"\n⚠ Warnings:", fg='yellow'))
                for warning in warnings:
                    click.echo(click.style(f"  • {warning}", fg='yellow'))
        else:
            click.echo(click.style(f"✗ Template validation failed", fg='red'))
            if errors:
                click.echo(click.style(f"\nErrors:", fg='red'))
                for error in errors:
                    click.echo(click.style(f"  • {error}", fg='red'))
            if warnings:
                click.echo(click.style(f"\nWarnings:", fg='yellow'))
                for warning in warnings:
                    click.echo(click.style(f"  • {warning}", fg='yellow'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('template_path', type=click.Path(exists=True))
@click.option('--template-dir', type=click.Path(exists=True),
              help='Custom directory containing template files')
@click.option('-v', '--verbose', is_flag=True,
              help='Show detailed output for each test')
def test(template_path, template_dir, verbose):
    """Run template test cases and verify expected answers.

    TEMPLATE_PATH should be path to a YAML template file with test cases.

    Examples:

      mathbot test src/templates/arithmetic/k3_easy_shopping_01.yaml

      mathbot test custom_templates/my_template.yaml -v

      mathbot test src/templates/geometry/k5_medium_area_01.yaml --verbose
    """
    try:
        from pathlib import Path
        from .yaml_loader import YAMLLoader
        from .template_generator import TemplateGenerator
        from .variable_generator import VariableGenerator
        from .solution_evaluator import execute_solution, format_answer
        from .jinja_renderer import JinjaRenderer
        
        template_file = Path(template_path)
        loader = YAMLLoader()
        template = loader.load_template(template_file)
        
        if not template:
            errors, warnings = loader.get_validation_results()
            click.echo(click.style(f"✗ Failed to load template", fg='red'))
            for error in errors:
                click.echo(click.style(f"  ERROR: {error}", fg='red'))
            sys.exit(1)
        
        if not template.tests:
            click.echo(click.style(f"⚠ No test cases defined in template", fg='yellow'))
            sys.exit(0)
        
        click.echo(f"Running {len(template.tests)} test case(s) for template '{template.id}'...\n")
        
        renderer = JinjaRenderer()
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(template.tests, 1):
            test_seed = test_case.seed
            expected = test_case.expected
            # Multi-tier templates declare per-test difficulty; fall back to
            # the template's default tier so single-tier fixtures keep
            # working unchanged.
            test_difficulty = test_case.difficulty or template.difficulty

            try:
                # Generate variables with test seed
                var_gen = VariableGenerator(seed=test_seed)
                context = var_gen.generate_context(
                    template.variables, difficulty=test_difficulty,
                )

                # Execute solution
                answer_value = execute_solution(template.solution, context)
                
                # Format answer(s)
                if isinstance(answer_value, dict):
                    # Multi-answer problem
                    formatted_answers = []
                    for j in sorted(answer_value.keys()):
                        answer_spec = template.variables.get(f'Answer{j}')
                        formatted = format_answer(answer_value[j], answer_spec)
                        formatted_answers.append(formatted)
                    actual_answer = " | ".join(formatted_answers)
                else:
                    # Single answer
                    answer_spec = template.variables.get('Answer')
                    actual_answer = format_answer(answer_value, answer_spec)
                
                # Get expected answer
                expected_answer = expected.get('answer', '')
                
                # Compare
                if actual_answer == expected_answer:
                    passed += 1
                    status = click.style("✓ PASS", fg='green')
                    if verbose:
                        click.echo(f"Test {i} (seed={test_seed}): {status}")
                        click.echo(f"  Expected: {expected_answer}")
                        click.echo(f"  Actual:   {actual_answer}")
                        if test_case.notes:
                            click.echo(f"  Notes: {test_case.notes}")
                        click.echo()
                else:
                    failed += 1
                    status = click.style("✗ FAIL", fg='red')
                    click.echo(f"Test {i} (seed={test_seed}): {status}")
                    click.echo(click.style(f"  Expected: {expected_answer}", fg='red'))
                    click.echo(click.style(f"  Actual:   {actual_answer}", fg='red'))
                    if test_case.notes:
                        click.echo(f"  Notes: {test_case.notes}")
                    if verbose:
                        click.echo(f"  Context: {context}")
                    click.echo()
                    
            except Exception as e:
                failed += 1
                click.echo(f"Test {i} (seed={test_seed}): {click.style('✗ ERROR', fg='red')}")
                click.echo(click.style(f"  Error: {e}", fg='red'))
                click.echo()
        
        # Summary
        click.echo("=" * 60)
        total = passed + failed
        if failed == 0:
            click.echo(click.style(f"✓ All {total} test(s) passed!", fg='green'))
        else:
            click.echo(click.style(f"✗ {failed} of {total} test(s) failed", fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('-o', '--output-dir', type=click.Path(), default=None,
              help='PNG output directory (default: <dataset>.pngs/)')
@click.option('--dpi', type=int, default=150,
              help='Raster DPI (default: 150)')
@click.option('--width', type=int, default=None,
              help='Output PNG width in px. Overrides --dpi when set.')
@click.option('--in-place/--write-out', default=True,
              help='Update dataset in-place with png_path entries (default), '
                   'or write a parallel <dataset>.rasterized.<ext> file.')
def rasterize(dataset_path, output_dir, dpi, width, in_place):
    """Rasterize the visual.source SVG of every row in a generated dataset.

    Reads a JSON list or JSONL file produced by `mathbot batch -o json|jsonl`,
    finds rows with a `visual.source` SVG, writes one PNG per row to the
    output directory, and augments each row with `visual.png_path`.

    The SVG source is the canonical artifact — it is not modified. Re-run
    with a different --dpi/--width to regenerate at any resolution.

    System dep: requires `libcairo` (macOS: `brew install cairo`;
    Debian/Ubuntu: `apt install libcairo2`). The Python wheel `cairosvg`
    is installed via `uv sync --extra png`.
    """
    from pathlib import Path

    try:
        import cairosvg  # noqa: F401  (lazy import — only needed for rasterization)
    except OSError as exc:
        click.echo(click.style(
            f"cairosvg loaded but libcairo is missing: {exc}\n"
            f"Install the system library:\n"
            f"  macOS:        brew install cairo\n"
            f"  Debian/Ubuntu: sudo apt install libcairo2\n"
            f"  Fedora:       sudo dnf install cairo",
            fg='red',
        ), err=True)
        sys.exit(1)
    except ImportError:
        click.echo(click.style(
            "cairosvg is not installed. Run `uv sync --extra png` to install it.",
            fg='red',
        ), err=True)
        sys.exit(1)

    dataset_path = Path(dataset_path)
    is_jsonl = dataset_path.suffix.lower() in {'.jsonl', '.ndjson'}

    if output_dir is None:
        output_dir = dataset_path.with_suffix(dataset_path.suffix + '.pngs')
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load rows; remember whether the source was a single object so we
    # can write the augmented dataset back in the same shape.
    rows: list[dict] = []
    single_object = False
    raw = dataset_path.read_text(encoding='utf-8')
    if is_jsonl:
        for line in raw.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    else:
        loaded = json.loads(raw)
        # NB: the `list` builtin is shadowed by the `mathbot list` Click
        # subcommand defined in this module — check for dict, default to
        # treating the rest as a list of rows.
        if isinstance(loaded, dict):
            rows = [loaded]
            single_object = True
        elif isinstance(loaded, (tuple,)) or type(loaded).__name__ == 'list':
            rows = loaded
        else:
            click.echo(click.style(
                f"Unsupported dataset shape: top-level {type(loaded).__name__}",
                fg='red',
            ), err=True)
            sys.exit(1)

    rendered = skipped = errored = 0
    for row in rows:
        visual = row.get('visual')
        if not isinstance(visual, dict) or visual.get('format') != 'svg':
            skipped += 1
            continue
        source = visual.get('source')
        if not isinstance(source, str) or not source.strip():
            skipped += 1
            continue

        # Use test_id (or hash of source) as filename stem
        stem = row.get('test_id') or f"row_{rendered + skipped + errored:06d}"
        png_path = output_dir / f"{stem}.png"
        try:
            kwargs = {'bytestring': source.encode('utf-8'), 'dpi': dpi}
            if width is not None:
                kwargs['output_width'] = width
            cairosvg.svg2png(write_to=str(png_path), **kwargs)
        except Exception as e:  # rasterize errors shouldn't kill the batch
            errored += 1
            click.echo(click.style(
                f"  err  {stem}: {type(e).__name__}: {e}", fg='yellow',
            ), err=True)
            continue

        # Store relative path so the dataset stays portable
        try:
            visual['png_path'] = str(png_path.relative_to(dataset_path.parent))
        except ValueError:
            visual['png_path'] = str(png_path)
        rendered += 1

    # Write augmented dataset
    out_path = dataset_path if in_place else dataset_path.with_suffix(
        '.rasterized' + dataset_path.suffix,
    )
    if is_jsonl:
        with out_path.open('w', encoding='utf-8') as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    else:
        payload = rows[0] if single_object else rows
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')

    click.echo(
        f"Rasterized {rendered}, skipped {skipped} (no visual), "
        f"errored {errored}. PNGs in {output_dir}/, dataset → {out_path}.",
    )


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--samples-per-template', '-k', default=4, show_default=True,
              type=int,
              help='Render each template K times for the render-driven rules.')
@click.option('--seed-base', default=0, show_default=True, type=int,
              help='Starting seed for the K samples (deterministic across runs).')
@click.option('--rules', default=None,
              help='Comma-separated rule ids to include (default: all).')
@click.option('--strict', is_flag=True,
              help='Treat warnings as errors for the exit code.')
@click.option('--json', 'as_json', is_flag=True,
              help='Emit findings as JSON to stdout.')
def lint(path, samples_per_template, seed_base, rules, strict, as_json):
    """Lint a template, directory, or the whole corpus.

    With no PATH, lints every template under src/templates/. JSON
    output goes to stdout; a one-line summary always goes to stderr.

    Examples:

      mathbot lint                                          # whole corpus
      mathbot lint src/templates/geometry/k5_*.yaml --json  # one file, JSON
      mathbot lint src/templates/arithmetic --strict        # subdir, fail on warnings
      mathbot lint --rules render_crash,empty_answer        # subset of rules
    """
    from pathlib import Path
    from .audit import lint_corpus, lint_path
    from .audit.findings import count_by_severity
    from .audit.report import emit_json, lint_report, write_lint_summary

    rule_set = (
        {r.strip() for r in rules.split(',') if r.strip()}
        if rules else None
    )

    target = Path(path) if path else None
    if target is None:
        # Default: lint the whole corpus under src/templates/.
        from pathlib import Path as _Path
        templates_dir = _Path(__file__).parent / 'templates'
        findings = lint_corpus(
            templates_dir,
            samples_per_template=samples_per_template,
            seed_base=seed_base,
            rules=rule_set,
        )
        templates_checked = sum(1 for _ in templates_dir.rglob('*.yaml'))
    else:
        findings = lint_path(
            target,
            samples_per_template=samples_per_template,
            seed_base=seed_base,
            rules=rule_set,
        )
        templates_checked = (
            sum(1 for _ in target.rglob('*.yaml')) if target.is_dir() else 1
        )

    if as_json:
        emit_json(lint_report(findings))

    write_lint_summary(findings, templates_checked)

    counts = count_by_severity(findings)
    if counts['error'] > 0 or (strict and (counts['warning'] > 0 or counts['info'] > 0)):
        sys.exit(1)


@cli.command()
@click.option('--samples-per-template', '-k', default=4, show_default=True,
              type=int,
              help='Render each template K times for contamination shingles.')
@click.option('--seed-base', default=0, show_default=True, type=int)
@click.option('--top-pairs', default=50, show_default=True, type=int,
              help='Number of top contamination pairs to include in output.')
@click.option('--n-gram', default=5, show_default=True, type=int,
              help='Shingle size for cross-template Jaccard.')
@click.option('--json', 'as_json', is_flag=True, default=True,
              help='Emit JSON to stdout (default; the only structured format).')
def health(samples_per_template, seed_base, top_pairs, n_gram, as_json):
    """Corpus-level health report — coverage, density, dupes, contamination.

    Always JSON to stdout. Slower than `lint` because it renders every
    template K times for the contamination shingles.

    Examples:

      mathbot health > health.json
      mathbot health --top-pairs 100 -k 6 > health.json
      mathbot health | jq '.coverage.summary'
    """
    from pathlib import Path
    from .audit import run_health
    from .audit.report import emit_json

    templates_dir = Path(__file__).parent / 'templates'
    report = run_health(
        templates_dir,
        samples_per_template=samples_per_template,
        seed_base=seed_base,
        top_pairs=top_pairs,
        n_gram=n_gram,
    )
    emit_json(report)

    cov = report['coverage']['summary']
    cont = report['contamination']['summary']
    near_dupes = len(report['near_dupes'])
    click.echo(
        f"health: {cov['total']} templates ({cov['anchors']} anchors / "
        f"{cov['variants']} variants), "
        f"{cov['cells']} cells, "
        f"{near_dupes} within-cell near-dupes, "
        f"contamination max={cont['max']:.3f} p95={cont['p95']:.3f}.",
        err=True,
    )


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
