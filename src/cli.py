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
def generate(complexity, grade, topic, family, num_steps, seed, output, file, show_answer):
    """Generate a single math problem.

    Examples:

      mathbot generate

      mathbot generate -c 2 -g middle -t arithmetic

      mathbot generate -s 42 -o json --file problem.json

      mathbot generate --complexity 3 --topic algebra --no-show-answer
    """
    try:
        problem = generate_problem(
            complexity=complexity,
            grade=grade,
            math_topic=topic,
            problem_family=family,
            num_steps=num_steps,
            seed=seed
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
@click.option('--avoid-duplicates/--allow-duplicates', default=True,
              help='Avoid duplicate problems (default: avoid)')
@click.option('-o', '--output',
              type=click.Choice(['json', 'jsonl']),
              default='json',
              help='Output format (default: json)')
@click.option('--file', type=click.Path(), required=True,
              help='Output file path (required)')
def batch(count, complexity, grade, topic, family, num_steps, avoid_duplicates, output, file):
    """Generate multiple math problems.

    COUNT is the number of problems to generate.

    Examples:

      mathbot batch 10 --file problems.json

      mathbot batch 50 -c 2 -g middle --file test_set.json

      mathbot batch 100 --topic arithmetic -o jsonl --file problems.jsonl
    """
    try:
        # Generate problems with progress bar
        with click.progressbar(length=count, label='Generating problems') as bar:
            problems = generate_problems(
                n=count,
                complexity=complexity,
                grade=grade,
                math_topic=topic,
                problem_family=family,
                num_steps=num_steps,
                avoid_duplicates=avoid_duplicates
            )
            bar.update(count)

        # Save to file
        with open(file, 'w') as f:
            if output == 'jsonl':
                for problem in problems:
                    f.write(json.dumps(problem) + '\n')
            else:  # json
                json.dump(problems, f, indent=2)

        click.echo(click.style(f"✓ Generated {count} problems and saved to {file}", fg='green'))

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


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
