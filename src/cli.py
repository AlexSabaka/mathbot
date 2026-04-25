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
            problem = template_gen._generate_from_template(template, seed=seed, template_path=template_path)
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
            
            try:
                # Generate variables with test seed
                var_gen = VariableGenerator(seed=test_seed)
                context = var_gen.generate_context(template.variables)
                
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


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
