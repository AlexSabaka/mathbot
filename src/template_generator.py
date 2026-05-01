"""YAML-based template problem generator for mathbot v2.0."""

import ast
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional
from faker import Faker

from .yaml_loader import YAMLLoader, TemplateDefinition, discover_yaml_templates
from .variable_generator import VariableGenerator
from .jinja_renderer import JinjaRenderer
from .solution_evaluator import execute_solution, format_answer
from .constants import PROBLEM_FAMILIES


# Grade mapping for compatibility
GRADE_MAP = {
    'elementary': ['k1', 'k2', 'k3', 'k4', 'k5'],
    'middle': ['k6', 'k7', 'k8'],
    'high': ['k9', 'k10', 'k11', 'k12'],
}

# Family aliases for backward compatibility
FAMILY_ALIASES = {
    'sequential_purchase': 'shopping',
    'rate_time': 'travel',
    'compound_growth': 'growth',
    'multi_person_sharing': 'sharing',
    'area_perimeter_chain': 'geometry',
}

# Reverse mapping (new → old) for output
FAMILY_REVERSE_ALIASES = {v: k for k, v in FAMILY_ALIASES.items()}


class TemplateGenerator:
    """Generates math problems from YAML templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None, seed: Optional[int] = None):
        """Initialize generator.
        
        Args:
            templates_dir: Path to templates directory (default: src/templates/)
            seed: Random seed for reproducibility
        """
        if templates_dir is None:
            # Default to src/templates/
            current_dir = Path(__file__).parent
            templates_dir = current_dir / 'templates'
        
        self.templates_dir = templates_dir
        self.seed = seed
        
        # Initialize components
        self.loader = YAMLLoader()
        self.renderer = JinjaRenderer()
        
        # Set random seeds if provided
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        # Load all templates
        self._load_templates()
    
    def _load_templates(self):
        """Discover and load all YAML templates."""
        self.templates: Dict[str, TemplateDefinition] = {}
        self.template_paths: Dict[str, Path] = {}  # Store paths by template ID
        self.templates_by_criteria: Dict[str, List[TemplateDefinition]] = {}
        
        yaml_files = discover_yaml_templates(self.templates_dir)
        
        for file_path in yaml_files:
            template = self.loader.load_template(file_path)
            if template:
                self.templates[template.id] = template
                self.template_paths[template.id] = file_path  # Store the path
                
                # Index by various criteria for filtering
                self._index_template(template)
            else:
                # Print validation errors
                errors, warnings = self.loader.get_validation_results()
                if errors:
                    print(f"Failed to load {file_path}:", file=sys.stderr)
                    for error in errors:
                        print(f"  ERROR: {error}", file=sys.stderr)
    
    def _index_template(self, template: TemplateDefinition):
        """Index template by various criteria for fast filtering."""
        # Index by grade
        grade_key = f"grade_{template.grade}"
        self.templates_by_criteria.setdefault(grade_key, []).append(template)
        
        # Index by difficulty
        diff_key = f"difficulty_{template.difficulty}"
        self.templates_by_criteria.setdefault(diff_key, []).append(template)
        
        # Index by family
        family_key = f"family_{template.family}"
        self.templates_by_criteria.setdefault(family_key, []).append(template)
        
        # Index by topic
        topic_key = f"topic_{template.topic}"
        self.templates_by_criteria.setdefault(topic_key, []).append(template)
        
        # Index by steps
        steps_key = f"steps_{template.steps}"
        self.templates_by_criteria.setdefault(steps_key, []).append(template)
    
    def _filter_templates(
        self,
        complexity: Optional[int] = None,
        grade: Optional[str] = None,
        math_topic: Optional[str] = None,
        problem_family: Optional[str] = None,
        num_steps: Optional[int] = None
    ) -> List[TemplateDefinition]:
        """Filter templates by criteria."""
        candidates = list(self.templates.values())
        
        # Filter by complexity (maps to difficulty). Multi-tier templates
        # match if the requested tier is in their `difficulty_tiers`;
        # single-tier templates match only their declared `difficulty`.
        if complexity is not None:
            difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
            difficulty = difficulty_map.get(complexity)
            if difficulty:
                candidates = [
                    t for t in candidates
                    if (t.difficulty_tiers and difficulty in t.difficulty_tiers)
                    or t.difficulty == difficulty
                ]
        
        # Filter by grade
        if grade is not None:
            # Map grade names to k-grades
            if grade in GRADE_MAP:
                k_grades = GRADE_MAP[grade]
                # Extract grade number (k4 → 4)
                candidates = [t for t in candidates if f"k{t.grade}" in k_grades]
            elif grade.startswith('k'):
                grade_num = int(grade[1:])
                candidates = [t for t in candidates if t.grade == grade_num]
            else:
                # Try direct number
                try:
                    grade_num = int(grade)
                    candidates = [t for t in candidates if t.grade == grade_num]
                except ValueError:
                    pass
        
        # Filter by math topic
        if math_topic is not None:
            candidates = [t for t in candidates if math_topic in t.topic]
        
        # Filter by problem family (handle aliases)
        if problem_family is not None:
            # Map old names to new
            family = FAMILY_ALIASES.get(problem_family, problem_family)
            candidates = [t for t in candidates if t.family == family]
        
        # Filter by num_steps
        if num_steps is not None:
            candidates = [t for t in candidates if t.steps == num_steps]
        
        return candidates
    
    def generate(
        self,
        complexity: Optional[int] = None,
        grade: Optional[str] = None,
        math_topic: Optional[str] = None,
        problem_family: Optional[str] = None,
        num_steps: Optional[int] = None,
        seed: Optional[int] = None,
        inject_noop: bool = False,
    ) -> Dict:
        """Generate a single problem.

        Args:
            complexity: Difficulty level (1=easy, 2=medium, 3=hard)
            grade: Grade level ('elementary', 'middle', 'high', or 'k1'-'k12')
            math_topic: Math topic filter
            problem_family: Problem family filter
            num_steps: Number of steps filter
            seed: Random seed for this problem
            inject_noop: When True, deterministically pick one entry from
                the chosen template's `metadata.noop_clauses` (if any),
                Jinja-render it against the variable context, and bind it
                to the `noop_clause` Jinja variable. The template must
                contain `{{ noop_clause }}` for the injection to surface
                — `mathbot lint` enforces that pairing. When False (the
                default) `noop_clause` resolves to an empty string,
                preserving the byte-identical legacy render.

        Returns:
            Problem dictionary with standard structure
        """
        # Set seed if provided. Note: VariableGenerator re-seeds with the
        # same seed in _generate_from_template so that variable values depend
        # only on the seed, not on which template was selected (template
        # selection below consumes entropy via random.choice). The two
        # seedings are intentional — do not add Faker/random calls between
        # them or fixture determinism breaks.
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        elif self.seed is not None:
            random.seed(self.seed)
            Faker.seed(self.seed)

        # Filter templates
        candidates = self._filter_templates(
            complexity=complexity,
            grade=grade,
            math_topic=math_topic,
            problem_family=problem_family,
            num_steps=num_steps
        )
        
        if not candidates:
            raise ValueError(
                f"No templates found matching criteria: "
                f"complexity={complexity}, grade={grade}, topic={math_topic}, "
                f"family={problem_family}, steps={num_steps}"
            )
        
        # Select random template
        template = random.choice(candidates)

        # Get template path
        template_path = self.template_paths.get(template.id)

        # Generate problem from template
        return self._generate_from_template(
            template,
            seed=seed,
            template_path=template_path,
            requested_complexity=complexity,
            inject_noop=inject_noop,
        )

    def _generate_from_template(
        self,
        template: TemplateDefinition,
        seed: Optional[int] = None,
        template_path: Optional[Path] = None,
        requested_complexity: Optional[int] = None,
        requested_difficulty: Optional[str] = None,
        inject_noop: bool = False,
    ) -> Dict:
        """Generate problem from a specific template.

        `requested_difficulty` (a tier name) takes precedence over
        `requested_complexity` (an int 1/2/3). Internal callers — the test
        runner and the fixture-refresh script — pass the tier directly so
        they can render a specific row regardless of the caller's complexity
        filter.
        """
        # Resolve the effective difficulty for this render. Single-tier
        # templates always render at their declared `difficulty`. Multi-tier
        # templates honour the caller's --complexity if it lands in their
        # `difficulty_tiers`; with no complexity specified they sample a
        # tier uniformly so a `mathbot batch` run still spreads across tiers.
        difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
        requested = (
            requested_difficulty
            if requested_difficulty is not None
            else difficulty_map.get(requested_complexity)
        )
        if template.difficulty_tiers:
            if requested in template.difficulty_tiers:
                effective_difficulty = requested
            else:
                effective_difficulty = random.choice(template.difficulty_tiers)
        else:
            effective_difficulty = template.difficulty

        # Initialize variable generator with seed and the template's locale
        # (derived from `metadata.culture`, e.g. 'en-US' → Faker 'en_US').
        var_gen = VariableGenerator(seed=seed, locale=template.culture)

        # Generate variable values, honoring per-difficulty `ranges:` overrides.
        context = var_gen.generate_context(
            template.variables, difficulty=effective_difficulty,
        )

        # Auto-inject `<var>_unit` for variables that declare a free-form
        # `unit:` (Stage 3 — TD-3.6). Available to both Jinja and the
        # solution sandbox, so a template can write
        #   solution: |
        #     v_q = Q_(velocity, velocity_unit)
        # without hardcoding the unit string in two places.
        for var_name, spec in template.variables.items():
            if spec.unit:
                context[f"{var_name}_unit"] = spec.unit

        # Create display context with formatted values for template rendering
        display_context = {}
        for var_name, value in context.items():
            if var_name in template.variables:
                spec = template.variables[var_name]
                # Format for display (adds $, %, units…) using the
                # template's unit_system as the default; per-variable
                # unit_system overrides per-spec.
                display_context[var_name] = var_gen.format_value(
                    value, spec, template_unit_system=template.unit_system,
                )
            else:
                display_context[var_name] = value
        
        # Create combined context with both raw and formatted values
        # Raw values for calculations, formatted for display
        combined_context = context.copy()
        for var_name, formatted_value in display_context.items():
            # Only override if formatting changed the value (i.e., it's a string now)
            if isinstance(formatted_value, str) and not isinstance(context[var_name], str):
                # Keep raw value, formatted will be in {var_name}_formatted
                combined_context[f"{var_name}_formatted"] = formatted_value
            else:
                combined_context[var_name] = formatted_value

        # Inject `language` so locale-aware Jinja filters can dispatch.
        combined_context.setdefault('language', template.language)

        # H3 (Phase β). Bind `noop_clause` to either a rendered clause
        # (when `inject_noop=True` and the template ships a pool) or an
        # empty string. The empty-string default keeps every existing
        # template byte-identical: a `{{ noop_clause }}` in the body
        # renders to "" and Jinja's `trim_blocks`/whitespace handling in
        # the renderer eats the surrounding whitespace.
        #
        # Selection uses a derived RNG seeded from the request seed so
        # which clause lands on a given fixture is independent of any
        # prior `random.*` consumption (variable generation, template
        # selection). That keeps fixtures reproducible if the noop pool
        # later grows or its order changes.
        if inject_noop and template.noop_clauses:
            clause_rng = random.Random(seed if seed is not None else 0)
            chosen_clause = clause_rng.choice(template.noop_clauses)
            try:
                combined_context['noop_clause'] = self.renderer.render(
                    chosen_clause, combined_context,
                )
            except Exception as exc:
                raise ValueError(
                    f"Failed to render noop clause for {template.id}: {exc}"
                )
        else:
            combined_context.setdefault('noop_clause', "")

        # γ A.3. Bind `{{ simplifications }}` to the active (non-omitted)
        # simplifying-assumption sentences for the effective tier,
        # space-joined into a single string. Empty when no
        # simplifications survive (or none defined). Each entry is
        # itself a Jinja string so it can reference template variables
        # ("Treat the {{container}} as a perfect cylinder.").
        simplifications_text = ""
        if template.simplifications:
            active = [
                s for s in template.simplifications
                if effective_difficulty not in (s.omit_at or [])
            ]
            rendered_parts: List[str] = []
            for s in active:
                try:
                    rendered = self.renderer.render(s.text, combined_context).strip()
                except Exception as exc:
                    raise ValueError(
                        f"Failed to render simplification for {template.id}: {exc}"
                    )
                if rendered:
                    rendered_parts.append(rendered)
            simplifications_text = " ".join(rendered_parts)
        combined_context.setdefault('simplifications', simplifications_text)

        # Render template with Jinja2 (using combined context with both raw and formatted values)
        try:
            problem_text = self.renderer.render(template.template, combined_context)
        except Exception as e:
            raise ValueError(f"Failed to render template {template.id}: {e}")

        # Execute solution to compute answer (using raw numeric context)
        try:
            answer_value = execute_solution(
                template.solution, context, language=template.language,
            )
        except Exception as e:
            raise ValueError(f"Failed to execute solution for {template.id}: {e}")
        
        # Format answer(s) based on Answer variable spec(s); thread the
        # template's unit_system so suffixes/symbols respect metric/imperial/mixed_us.
        if isinstance(answer_value, dict):
            # Multi-answer problem
            formatted_answers = []
            for i in sorted(answer_value.keys()):
                answer_spec = template.variables.get(f'Answer{i}')
                formatted = format_answer(
                    answer_value[i], answer_spec,
                    template_unit_system=template.unit_system,
                )
                formatted_answers.append(formatted)
            expected_answer = " | ".join(formatted_answers)
        else:
            # Single answer
            answer_spec = template.variables.get('Answer')
            expected_answer = format_answer(
                answer_value, answer_spec,
                template_unit_system=template.unit_system,
            )
        
        # Extract math topic (use first part before dot)
        math_topic = template.topic.split('.')[0] if '.' in template.topic else template.topic
        
        # Map family name back to old name for compatibility
        family_name = FAMILY_REVERSE_ALIASES.get(template.family, template.family)
        
        # Extract operations from solution (basic heuristic)
        operations = self._extract_operations(template.solution)
        
        # Build standard output structure. Multi-tier templates encode
        # the rendered tier in `test_id` so each (template, tier) combination
        # is uniquely identifiable downstream; single-tier templates keep
        # their historical `math_<id>` so existing dataset consumers don't
        # see id changes.
        if template.difficulty_tiers:
            test_id = f"math_{template.id}__{effective_difficulty}"
        else:
            test_id = f"math_{template.id}"

        output = {
            "test_id": test_id,
            "task_type": "multi_step_math",
            "config_name": f"{template.grade}_{effective_difficulty}_{template.family}",
            "problem": problem_text.strip(),
            "task_params": {
                "complexity": {'easy': 1, 'medium': 2, 'hard': 3}[effective_difficulty],
                "grade": f"k{template.grade}",
                "math_topic": [math_topic],
                "problem_family": family_name,
                "num_steps": template.steps,
                "expected_answer": expected_answer,
                "operations": operations,
            }
        }
        
        # Add template path if provided
        if template_path:
            try:
                rel_path = template_path.relative_to(self.templates_dir.parent.parent)
                output["template_path"] = str(rel_path)
            except ValueError:
                # Path is not relative to templates_dir, use absolute
                output["template_path"] = str(template_path)

        # Render canonical visual source (Phase 5.5 + Phase β H1). Same
        # variable context as the problem template so visual labels can
        # reference the same variables.
        #   - format=svg: source is a Jinja2 string → SVG markup.
        #   - format=python: source is Python executed against the
        #     solution sandbox extended with PlotSVG / TreeSVG /
        #     MarkovSVG; the sandbox must bind `Visual` to an SVG
        #     string. Output is normalised to format=svg so downstream
        #     readers and `mathbot rasterize` stay format-agnostic.
        # The PNG is produced by the separate `mathbot rasterize` step;
        # this output ships only the source so the dataset is
        # re-rasterizable.
        if template.visual is not None:
            try:
                if template.visual.format == "python":
                    rendered_source = self._render_python_visual(
                        template, combined_context,
                    )
                else:
                    rendered_source = self.renderer.render(
                        template.visual.source, combined_context,
                    )
                rendered_alt = (
                    self.renderer.render(template.visual.alt_text, combined_context)
                    if template.visual.alt_text else None
                )
            except Exception as e:
                raise ValueError(f"Failed to render visual for {template.id}: {e}")

            visual_out = {
                # Always emit `svg` to downstream — `python` is an
                # authoring-side concept; the dataset row carries the
                # rendered markup.
                "format": "svg",
                "source": rendered_source.strip(),
            }
            if rendered_alt is not None:
                visual_out["alt_text"] = rendered_alt.strip()
            output["visual"] = visual_out

        return output

    def _render_python_visual(
        self,
        template: TemplateDefinition,
        context: Dict,
    ) -> str:
        """Phase β (H1). Execute a `format: python` visual.source.

        The sandbox is the same as the solution sandbox plus the visual
        builders. Authors set ``Visual = builder.render()``; the
        function returns that string verbatim. Raises ``ValueError`` if
        the source omits the ``Visual`` binding or if the returned
        value isn't a string — the parser-stage drift is loud rather
        than surfacing as a malformed-XML downstream finding.
        """
        from .solution_evaluator import build_visual_sandbox
        sandbox = build_visual_sandbox(language=template.language)
        # Merge sandbox + variable context into a single namespace so that
        # lambdas defined inside the source — which K12 plot-style visuals
        # rely on (`plot.plot(lambda x: a*x*x + b*x + c)`) — can resolve
        # variables through their `__globals__`. exec's two-dict mode
        # would pin lambda globals to the sandbox dict and the lambda
        # would NameError on the template variables when PlotSVG
        # later samples it. Context wins on key collisions so a
        # template-side `sum = 7` shadows the builtin, matching solution-
        # sandbox precedence.
        ns = {**sandbox, **context}
        try:
            exec(template.visual.source, ns)
        except Exception as exc:
            raise ValueError(
                f"visual.source (python) raised: {exc}"
            )
        if "Visual" not in ns:
            raise ValueError(
                "visual.source (python) did not set the `Visual` variable"
            )
        out = ns["Visual"]
        if not isinstance(out, str):
            raise ValueError(
                f"visual.source (python) bound `Visual` to {type(out).__name__}, "
                f"expected str (an SVG document)"
            )
        return out
    
    def _extract_operations(self, solution_code: str) -> List[str]:
        """Extract Python arithmetic operations from solution code.

        AST-based (post-checkpoint fix). The pre-fix version was a
        substring check on the raw source, which over-counted: any
        non-trivial solution has `+`, `-`, `*`, `/` somewhere — in
        comments, f-strings, kwargs, negative literals — and produced
        the same `[addition, subtraction, multiplication, division]`
        list for nearly every template.

        Walks the parsed AST and records BinOp operators plus
        `pow(...)` / `math.pow(...)` calls. Unary minus on a literal
        is *not* counted as subtraction (a `-3` literal is a sign,
        not an operation). String `%` formatting is not counted as
        modulo because it's a `BinOp` on a string LHS — the AST node
        type doesn't distinguish, but in practice all real arithmetic
        modulo lands on numeric LHS, and string-formatting templates
        don't typically need a modulo tag.

        Falls back to `['arithmetic']` on a SyntaxError so a malformed
        solution still surfaces a non-empty list (matches the prior
        contract used by `mathbot lint`'s `zero_steps_with_ops` rule).
        """
        try:
            tree = ast.parse(solution_code)
        except SyntaxError:
            return ['arithmetic']

        # Order-preserving dedupe of the operations as they're
        # encountered in source-order. Stable across re-renders.
        found: List[str] = []

        def _add(name: str) -> None:
            if name not in found:
                found.append(name)

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type is ast.Add:
                    _add('addition')
                elif op_type is ast.Sub:
                    _add('subtraction')
                elif op_type is ast.Mult:
                    _add('multiplication')
                elif op_type in (ast.Div, ast.FloorDiv):
                    _add('division')
                elif op_type is ast.Pow:
                    _add('exponentiation')
                elif op_type is ast.Mod:
                    _add('modulo')
            elif isinstance(node, ast.Call):
                # `pow(x, y)` or `math.pow(x, y)` — both surface as
                # exponentiation. Other callables don't.
                fname: Optional[str] = None
                if isinstance(node.func, ast.Name):
                    fname = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    fname = node.func.attr
                if fname == 'pow':
                    _add('exponentiation')

        return found or ['arithmetic']
    
    def get_available_options(self) -> Dict[str, List[str]]:
        """Get available filtering options."""
        families = set()
        topics = set()
        grades = set()
        
        for template in self.templates.values():
            families.add(template.family)
            # Add original family name for compatibility
            original = FAMILY_REVERSE_ALIASES.get(template.family, template.family)
            families.add(original)
            
            topics.add(template.topic.split('.')[0])
            grades.add(f"k{template.grade}")
        
        return {
            "problem_families": sorted(families),
            "math_topics": sorted(topics),
            "grades": sorted(grades),
            "complexity_levels": [1, 2, 3],
        }
