"""YAML template loader and validator for mathbot v2.0."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml

from .units import VALID_UNIT_SYSTEMS, DEFAULT_UNIT_SYSTEM, ureg


@dataclass
class VariableSpec:
    """Specification for a single variable."""
    name: str
    type: str
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    category: Optional[str] = None
    singular: Optional[bool] = None
    probability: Optional[float] = None
    choices: Optional[List[Any]] = None
    # Per-variable override of the template's unit system. None means
    # "inherit from metadata.unit_system". See `src.units`.
    unit_system: Optional[str] = None
    # Optional free-form pint unit string (Stage 3 — TD-3.6). When set,
    # overrides the (type, system)-table lookup: the formatter wraps the
    # magnitude as `Q_(value, unit)` and prints with pint's compact pretty
    # form (`~P` → `m/s²`, `kg/m³`, `mi/gal`). Pairs with the Stage 2
    # sandbox: a solution that returns `Q_(...)` for an Answer with
    # `unit:` set is converted to that unit before display. The string
    # is validated at load time via `ureg.parse_units()`.
    unit: Optional[str] = None
    # Optional per-difficulty range overrides. Keyed by tier name
    # ("easy"/"medium"/"hard"); each entry can carry `min`/`max`/`step`/
    # `choices` that override the flat fields above for that tier. Used
    # by multi-tier templates (metadata.difficulty_tiers) so a single
    # template can render at multiple difficulty levels with different
    # number ranges. None means the flat fields apply at every tier.
    ranges: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class SimplificationSpec:
    """v2 γ (A.3). Stated simplifying assumption with per-tier suppression.

    The pedagogically interesting K12 difficulty axis isn't number
    range — it's *which simplifications are stated*. At easy tier the
    template tells the solver "assume the cup is a perfect cone";
    at hard tier the same template suppresses that line and the
    solver has to recognise the modeling step on their own.

    `text` is a Jinja string (rendered against the same context as
    `template:`), and `omit_at` is the list of tier names where this
    simplification is *not* surfaced. An entry with `omit_at: [hard]`
    appears at easy/medium and disappears at hard. An entry with
    `omit_at: []` is unconditional (always stated).

    The renderer concatenates the active (non-omitted) entries with
    a single space and binds the result to the `{{ simplifications }}`
    Jinja variable. Templates that don't reference `{{ simplifications }}`
    in `template:` get a `simplification_lift_missing` lint warning
    when the field is non-empty.
    """
    text: str
    omit_at: List[str] = field(default_factory=list)


@dataclass
class TestCase:
    """Test case for template validation."""
    seed: int
    expected: Dict[str, Any]
    notes: Optional[str] = None
    # For multi-tier templates: which difficulty tier this fixture targets.
    # Single-tier templates leave it None and the runner uses
    # `metadata.difficulty`.
    difficulty: Optional[str] = None
    # v2 (B3/B4). Comparison mode for `actual` vs `expected.answer`.
    #   - `string` (default): exact-string equality (legacy behaviour).
    #   - `numeric`: parse both sides as floats and compare with
    #     `tolerance` (absolute) or `tolerance_rel` (relative); useful
    #     for calc-style answers where the formatter rounds.
    #   - `symbolic`: parse both sides via `sympy.sympify` and compare
    #     with `sympy.simplify(a - b) == 0` (or `a.equals(b)`); used by
    #     N3/N7/N9/N11–N16 templates whose canonical answer form is
    #     ambiguous up to algebraic simplification.
    # Falling back to string-equality when unset preserves byte-for-byte
    # behaviour for the existing 1278-fixture corpus.
    compare: Optional[str] = None
    # Absolute tolerance for `compare: numeric`. None means strict
    # equality after parsing as float.
    tolerance: Optional[float] = None
    # Relative tolerance (|a-b| / max(|a|,|b|)). Combined with `tolerance`
    # via OR — passing either threshold counts as a match — to handle
    # both small-magnitude (absolute wins) and large-magnitude (relative
    # wins) answers gracefully.
    tolerance_rel: Optional[float] = None


# Phase 5.5 visual layer. The YAML stores **source** (Jinja2-rendered SVG
# string today; Python builder scripts later) — never raster output. A
# separate `mathbot rasterize` step produces PNG from this source at a
# configurable DPI. Source must always be preserved so the dataset can be
# re-rasterized at a different resolution without re-generating problems.
# Phase β (H1). Visual.source format dispatch:
#   - `svg`: source is a Jinja2 string that renders to an SVG. Same
#     Jinja context as the problem template.
#   - `python`: source is Python code executed against the solution
#     sandbox extended with the visual builders (PlotSVG, TreeSVG,
#     MarkovSVG). The sandbox must bind `Visual` to an SVG string;
#     `template_generator` captures that and emits it on the dataset
#     row's `visual.source` field with format normalised to `svg` so
#     downstream rasterizers / dataset readers stay format-agnostic.
VALID_VISUAL_FORMATS = {"svg", "python"}


@dataclass
class VisualSpec:
    """Per-template canonical visual source.

    `format` selects how `source` is interpreted. Today only `svg` ships:
    `source` is a Jinja2 template that renders to an `<svg>…</svg>` string
    using the same variable context as the problem `template:` block.
    `alt_text` is also Jinja2-rendered and surfaces in the output JSON for
    screen-reader / multimodal-eval consumption.
    """
    format: str
    source: str
    alt_text: Optional[str] = None


@dataclass
class TemplateDefinition:
    """Complete YAML template definition."""
    # Metadata
    id: str
    version: str
    author: str
    created: str
    grade: int
    topic: str
    family: str
    difficulty: str
    steps: int
    # `language` is the BCP-47 language tag used for locale-aware filters
    # (plural, ordinal, number-to-words) and translated entity pools.
    # `culture` is a regional hint (BCP-47 region tag) used to drive Faker
    # locale (cities/companies). It does not drive language behavior.
    language: str = "en"
    culture: str = "en-US"
    # Display-time unit system: "metric" | "imperial" | "mixed_us" (default).
    # Solutions still compute in system-native units; this only controls
    # what the formatter prints. Per-variable override available on
    # VariableSpec. See `src.units`.
    unit_system: str = "mixed_us"
    # When set, the template renders at any of the listed tiers (driven by
    # the caller's --complexity, or randomly chosen when complexity is
    # unspecified). Variables can carry per-tier `ranges:` overrides so the
    # number ranges scale with the tier. Must include `difficulty` (the
    # default tier). When None the template is single-tier (the legacy
    # behaviour: it renders only at `difficulty`).
    difficulty_tiers: Optional[List[str]] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    # v2 (B2). Curriculum-track tag for eval slicing across reference
    # systems. `core` covers material universal across the 8 cross-curriculum
    # references (CCSS HSA/HSF/HSG/HSN/HSS plus Singapore H2, Japan,
    # Finland, Norway, Sweden, Estonia, NL); `advanced` covers the
    # advanced/optional advanced track (CCSS-(+) etc.); `tertiary` covers
    # first-year-university material absent from most secondary curricula
    # (eigenvalues, second-order ODEs, L'Hôpital); `US-emphasized` covers
    # topics over-weighted in CCSS relative to international norms
    # (piecewise functions, conic sections beyond circle, two-column
    # proofs). Default `core`. None means "not yet tagged" — `mathbot lint`
    # warns on K9+ templates without `track:`.
    track: Optional[str] = None
    # v2 (H2). Cross-cutting structural pattern tags. Orthogonal to
    # `family:` — a single template can carry multiple tags. Original
    # 12 (T1–T12) describe surface skeletons (running_total,
    # multi_person_sharing, ...); the v2 K9+ additions (T13–T17) target
    # the LLM-eval failure modes called out in
    # MATHBOT_PROBLEMS_PROPOSAL_v2.md §6 (compositional reasoning,
    # method selection, selective attention to noop clauses, inverse
    # query direction). See VALID_STRUCTURAL_TAGS for the closed set.
    structural_tags: List[str] = field(default_factory=list)
    # v2 (H4). Optional `forward` / `inverse` toggle for templates that
    # naturally render in two query directions (N1 inverse functions,
    # N4 year-to-target, N8 log inversion, N15 time-to-target ODE).
    # The solution sandbox can branch on this value; lint allows but
    # does not require its use. None means "not applicable" (most
    # templates).
    direction: Optional[str] = None
    # v2 (H3). DEPRECATED in Phase γ — superseded by `simplifications:`
    # + `T18_assumption_omission`. The K12-appropriate analog of GSM-NoOp
    # is *suppressing* a stated simplifying assumption at hard tier
    # rather than *injecting* an irrelevant clause. `noop_clauses:`
    # populated on a template still works (back-compat through the
    # 0.6.x cycle) but `mathbot lint` emits `noop_clauses_deprecated`
    # info findings, and the field is scheduled for removal in 0.7.0
    # (Phase γ.5).
    noop_clauses: List[str] = field(default_factory=list)

    # v2 γ (A.3). Stated simplifying assumptions with per-tier
    # suppression. Each entry is a SimplificationSpec; the renderer
    # filters by tier and concatenates the active entries into the
    # `{{ simplifications }}` Jinja variable. The K12-appropriate
    # difficulty axis: at easy tier the template tells the solver
    # "assume the speed of the water is negligible"; at hard tier the
    # same line is suppressed and the solver has to recognise the
    # modeling step on their own. Pairs with `T18_assumption_omission`.
    simplifications: List[SimplificationSpec] = field(default_factory=list)

    # v2 γ (A.3). How load-bearing the visual is for solving the
    # problem. Either a single value applied at every tier, or a per-
    # tier mapping {tier: value}. Values: `none` (no figure),
    # `decorative` (figure illustrative; prose is sufficient),
    # `partial` (figure carries some quantities the prose doesn't),
    # `load_bearing` (the figure is *required* to solve — quantities
    # only appear on it). `mathbot lint` emits
    # `figure_load_inconsistent` warnings when prose and declared
    # load disagree (e.g. `figure_load: decorative` but the prose says
    # "as shown in the figure").
    figure_load: Optional[Any] = None
    
    # Core sections
    variables: Dict[str, VariableSpec] = field(default_factory=dict)
    template: str = ""
    solution: str = ""
    tests: List[TestCase] = field(default_factory=list)
    # Optional canonical visual source (Phase 5.5). When present, the
    # generator renders `visual.source` and `visual.alt_text` with the
    # same Jinja context as the problem text and emits the result on
    # the output JSON's `visual` field.
    visual: Optional[VisualSpec] = None

    # Source file path
    file_path: Optional[Path] = None

class YAMLLoader:
    """Loads and validates YAML template files."""
    
    REQUIRED_METADATA = {
        'id', 'version', 'author', 'created', 'grade', 
        'topic', 'family', 'difficulty', 'steps'
    }
    
    # Active types: every entry here has a generation branch in
    # VariableGenerator._generate_value and at least one corresponding
    # format rule in format_value / format_answer.
    VALID_TYPES = {
        # numeric integer types
        'integer', 'ordinal',
        # fractions
        'fraction',
        # numeric decimal types
        'decimal', 'volume', 'area', 'length', 'weight', 'temperature',
        'speed', 'acceleration', 'money', 'price', 'percentage',
        # compound physics quantities (Stage 2 — see src.units DISPLAY_UNITS)
        'density', 'energy', 'power', 'pressure', 'force',
        # entity types
        'person', 'name', 'location', 'city',
        'store', 'restaurant', 'company', 'item',
        # date/time types
        'weekday', 'month', 'season', 'time', 'duration',
        # other types
        'boolean', 'string', 'choice',
    }
    
    VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}

    # v2 (B2). See TemplateDefinition.track for semantics. The set is closed
    # so a typo ("tetiary") fails at load time rather than slipping through
    # to eval-slice queries. Add new values here only after a corresponding
    # entry in MATHBOT_PROBLEMS_PROPOSAL_v2.md and SPEC.md.
    VALID_TRACKS = {'core', 'advanced', 'tertiary', 'US-emphasized'}

    # v2 (B3). Closed set of fixture comparison modes. See `TestCase.compare`.
    VALID_COMPARE_MODES = {'string', 'numeric', 'symbolic'}

    # v2 (H2). Structural-pattern tag taxonomy. T1–T12 are the original
    # surface skeletons retained from the January roadmap; T13–T17 are
    # the K9+ additions targeting the LLM-eval failure modes called out
    # in MATHBOT_PROBLEMS_PROPOSAL_v2.md §6 (Compositional GSM,
    # MATH-P-Hard, GSM-NoOp, Putnam-AXIOM Variation, inverse-direction).
    VALID_STRUCTURAL_TAGS = {
        # T1–T12 (original). Surface-pattern tags retained from the
        # January 2026 roadmap.
        'running_total',
        'multi_person_sharing',
        'sequential_purchase',
        'rate_time',
        'area_perimeter_chain',
        'compound_growth',
        'mixture_alloy',
        'multi_step_purchase',
        'division_with_remainder',
        'fraction_of_a_quantity',
        'percentage_change',
        'unit_conversion_chain',
        # T13–T17 (v2 K9+). Each maps to a specific antipattern rule.
        'T13_symbolic_chain',          # rule #11; Compositional GSM gap
        'T14_formula_recall',          # rule #9; pure-recall is too easy
        'T15_method_selection',        # rule #10; MATH-P-Hard parameters change method
        'T16_selective_attention',     # rule #12; GSM-NoOp irrelevant clause
        'T17_inverse_query',           # rule on inverse-direction queries
        # T18 (γ A.3). K12-appropriate replacement for the retired T16:
        # the eval perturbation isn't injecting irrelevant clauses
        # (grade-school surface noise) but suppressing a stated
        # simplifying assumption. Pairs with `simplifications:`.
        'T18_assumption_omission',
    }

    # v2 (H4). Closed set of query directions. See TemplateDefinition.direction.
    VALID_DIRECTIONS = {'forward', 'inverse'}

    # v2 γ (A.3). Closed set of `figure_load` values. See
    # TemplateDefinition.figure_load. None at template level means
    # "not declared" — `mathbot lint` doesn't require it for templates
    # without a `visual:` block.
    VALID_FIGURE_LOAD = {'none', 'decorative', 'partial', 'load_bearing'}
    
    VALID_ITEM_CATEGORIES = {
        'grocery', 'electronics', 'clothing', 'book', 'online',
        'school', 'furniture', 'other'
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_template(self, file_path: Path) -> Optional[TemplateDefinition]:
        """Load and validate a YAML template file."""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse YAML: {e}")
            return None
        
        if not isinstance(data, dict):
            self.errors.append("YAML root must be a dictionary")
            return None
        
        # Validate structure
        if not self._validate_structure(data):
            return None
        
        # Parse metadata
        metadata = data.get('metadata', {})
        
        # Parse variables
        variables = {}
        for var_name, var_spec in data.get('variables', {}).items():
            variables[var_name] = self._parse_variable(var_name, var_spec)
        
        # Parse tests
        tests = []
        for test_data in data.get('tests', []):
            test_diff = test_data.get('difficulty')
            if test_diff is not None and test_diff not in self.VALID_DIFFICULTIES:
                self.errors.append(
                    f"Test case (seed={test_data.get('seed')}) has invalid "
                    f"difficulty '{test_diff}'. Must be one of: "
                    f"{sorted(self.VALID_DIFFICULTIES)}"
                )
            test_compare = test_data.get('compare')
            if test_compare is not None and test_compare not in self.VALID_COMPARE_MODES:
                self.errors.append(
                    f"Test case (seed={test_data.get('seed')}) has invalid "
                    f"compare '{test_compare}'. Must be one of: "
                    f"{sorted(self.VALID_COMPARE_MODES)}"
                )
            test_tol = test_data.get('tolerance')
            test_tol_rel = test_data.get('tolerance_rel')
            for tol_name, tol_val in (('tolerance', test_tol), ('tolerance_rel', test_tol_rel)):
                if tol_val is not None and not isinstance(tol_val, (int, float)):
                    self.errors.append(
                        f"Test case (seed={test_data.get('seed')}) has invalid "
                        f"{tol_name} {tol_val!r}: must be a number"
                    )
                if isinstance(tol_val, (int, float)) and tol_val < 0:
                    self.errors.append(
                        f"Test case (seed={test_data.get('seed')}) has invalid "
                        f"{tol_name} {tol_val}: must be non-negative"
                    )
            # Tolerance only meaningful in numeric mode; warn (don't error)
            # if it's set without an explicit numeric mode declared.
            if (test_tol is not None or test_tol_rel is not None) and test_compare not in ('numeric', None):
                self.warnings.append(
                    f"Test case (seed={test_data.get('seed')}) sets tolerance "
                    f"with compare='{test_compare}' (only used by 'numeric')"
                )
            tests.append(TestCase(
                seed=test_data['seed'],
                expected=test_data['expected'],
                notes=test_data.get('notes'),
                difficulty=test_diff,
                compare=test_compare,
                tolerance=test_tol,
                tolerance_rel=test_tol_rel,
            ))

        # Parse optional visual block
        visual_spec = self._parse_visual(data.get('visual'))

        # Parse simplifications: each entry → SimplificationSpec.
        # Validation in _validate_structure has already run; this just
        # builds the dataclass list. Skipped entries (validation
        # errors above) are silently dropped — the load itself fails
        # via self.errors propagation.
        simplifications: List[SimplificationSpec] = []
        for entry in (metadata.get('simplifications') or []):
            if isinstance(entry, dict) and isinstance(entry.get('text'), str):
                simplifications.append(SimplificationSpec(
                    text=entry['text'],
                    omit_at=list(entry.get('omit_at') or []),
                ))

        # Create template definition
        template_def = TemplateDefinition(
            id=metadata['id'],
            version=metadata['version'],
            author=metadata['author'],
            created=metadata['created'],
            grade=metadata['grade'],
            topic=metadata['topic'],
            family=metadata['family'],
            difficulty=metadata['difficulty'],
            steps=metadata['steps'],
            language=metadata.get('language', 'en'),
            culture=metadata.get('culture', 'en-US'),
            unit_system=metadata.get('unit_system', DEFAULT_UNIT_SYSTEM),
            difficulty_tiers=metadata.get('difficulty_tiers'),
            tags=metadata.get('tags', []),
            notes=metadata.get('notes'),
            track=metadata.get('track'),
            structural_tags=metadata.get('structural_tags', []) or [],
            direction=metadata.get('direction'),
            noop_clauses=metadata.get('noop_clauses', []) or [],
            simplifications=simplifications,
            figure_load=metadata.get('figure_load'),
            variables=variables,
            template=data.get('template', ''),
            solution=data.get('solution', ''),
            tests=tests,
            visual=visual_spec,
            file_path=file_path
        )
        
        # Validate template
        self._validate_template(template_def)
        
        return template_def if not self.errors else None
    
    def _validate_structure(self, data: Dict) -> bool:
        """Validate overall YAML structure."""
        # Check required sections
        if 'metadata' not in data:
            self.errors.append("Missing required section: metadata")
            return False
        
        if 'variables' not in data:
            self.errors.append("Missing required section: variables")
            return False
        
        if 'template' not in data:
            self.errors.append("Missing required section: template")
            return False
        
        if 'solution' not in data:
            self.errors.append("Missing required section: solution")
            return False
        
        # Check metadata fields
        metadata = data['metadata']
        missing_fields = self.REQUIRED_METADATA - set(metadata.keys())
        if missing_fields:
            self.errors.append(f"Missing required metadata fields: {missing_fields}")
            return False
        
        # Validate difficulty
        if metadata['difficulty'] not in self.VALID_DIFFICULTIES:
            self.errors.append(
                f"Invalid difficulty '{metadata['difficulty']}'. "
                f"Must be one of: {self.VALID_DIFFICULTIES}"
            )

        # Validate unit_system if present (None/missing → DEFAULT_UNIT_SYSTEM)
        meta_us = metadata.get('unit_system')
        if meta_us is not None and meta_us not in VALID_UNIT_SYSTEMS:
            self.errors.append(
                f"Invalid metadata.unit_system '{meta_us}'. "
                f"Must be one of: {sorted(VALID_UNIT_SYSTEMS)}"
            )

        # Validate track if present. Unset is allowed at load time;
        # `mathbot lint` flags K9+ templates without track set.
        meta_track = metadata.get('track')
        if meta_track is not None and meta_track not in self.VALID_TRACKS:
            self.errors.append(
                f"Invalid metadata.track '{meta_track}'. "
                f"Must be one of: {sorted(self.VALID_TRACKS)}"
            )

        # Validate structural_tags if present. Each tag must be in the
        # closed set; the field itself is optional and defaults to [].
        meta_st = metadata.get('structural_tags')
        if meta_st is not None:
            if not isinstance(meta_st, list) or not all(isinstance(t, str) for t in meta_st):
                self.errors.append(
                    "metadata.structural_tags must be a list of strings"
                )
            else:
                bad = [t for t in meta_st if t not in self.VALID_STRUCTURAL_TAGS]
                if bad:
                    self.errors.append(
                        f"metadata.structural_tags has invalid tag(s) {bad}. "
                        f"Must be from: {sorted(self.VALID_STRUCTURAL_TAGS)}"
                    )

        # Validate direction if present.
        meta_dir = metadata.get('direction')
        if meta_dir is not None and meta_dir not in self.VALID_DIRECTIONS:
            self.errors.append(
                f"Invalid metadata.direction '{meta_dir}'. "
                f"Must be one of: {sorted(self.VALID_DIRECTIONS)}"
            )

        # Validate noop_clauses if present. Each clause is a Jinja string;
        # the wiring (whether `template:` actually contains
        # `{{ noop_clause }}`) is checked by `mathbot lint`. The field
        # itself is deprecated — see TemplateDefinition.noop_clauses
        # docstring; lint emits an info finding when populated.
        meta_nc = metadata.get('noop_clauses')
        if meta_nc is not None:
            if not isinstance(meta_nc, list) or not all(isinstance(c, str) for c in meta_nc):
                self.errors.append(
                    "metadata.noop_clauses must be a list of Jinja string clauses"
                )

        # Validate simplifications if present. List of {text, omit_at}
        # mappings; `omit_at` is optional and defaults to []. Each tier
        # in `omit_at` must be a valid difficulty.
        meta_simp = metadata.get('simplifications')
        if meta_simp is not None:
            if not isinstance(meta_simp, list):
                self.errors.append(
                    "metadata.simplifications must be a list of "
                    "{text, omit_at} mappings"
                )
            else:
                for i, entry in enumerate(meta_simp):
                    if not isinstance(entry, dict):
                        self.errors.append(
                            f"metadata.simplifications[{i}] must be a "
                            f"mapping with `text` (and optional `omit_at`)"
                        )
                        continue
                    text = entry.get('text')
                    if not isinstance(text, str) or not text.strip():
                        self.errors.append(
                            f"metadata.simplifications[{i}].text must be "
                            f"a non-empty string"
                        )
                    omit_at = entry.get('omit_at', [])
                    if not isinstance(omit_at, list):
                        self.errors.append(
                            f"metadata.simplifications[{i}].omit_at must "
                            f"be a list of difficulty tier names"
                        )
                    else:
                        bad_tiers = [
                            t for t in omit_at
                            if t not in self.VALID_DIFFICULTIES
                        ]
                        if bad_tiers:
                            self.errors.append(
                                f"metadata.simplifications[{i}].omit_at "
                                f"has invalid tier(s) {bad_tiers}. Must "
                                f"be from: {sorted(self.VALID_DIFFICULTIES)}"
                            )

        # Validate figure_load if present. Either a single value from
        # VALID_FIGURE_LOAD, or a per-tier mapping {tier: value}.
        meta_fl = metadata.get('figure_load')
        if meta_fl is not None:
            if isinstance(meta_fl, str):
                if meta_fl not in self.VALID_FIGURE_LOAD:
                    self.errors.append(
                        f"metadata.figure_load '{meta_fl}' is invalid. "
                        f"Must be one of: {sorted(self.VALID_FIGURE_LOAD)}"
                    )
            elif isinstance(meta_fl, dict):
                for tier, value in meta_fl.items():
                    if tier not in self.VALID_DIFFICULTIES:
                        self.errors.append(
                            f"metadata.figure_load key '{tier}' is not "
                            f"a valid difficulty. Must be from: "
                            f"{sorted(self.VALID_DIFFICULTIES)}"
                        )
                    if value not in self.VALID_FIGURE_LOAD:
                        self.errors.append(
                            f"metadata.figure_load['{tier}'] = '{value}' "
                            f"is invalid. Must be one of: "
                            f"{sorted(self.VALID_FIGURE_LOAD)}"
                        )
            else:
                self.errors.append(
                    "metadata.figure_load must be a string or a "
                    "{tier: value} mapping"
                )

        # Validate difficulty_tiers if present. Must be a list of valid
        # tier names that includes `difficulty` (the default render tier).
        meta_tiers = metadata.get('difficulty_tiers')
        if meta_tiers is not None:
            if not isinstance(meta_tiers, list) or not all(
                isinstance(t, str) for t in meta_tiers
            ):
                self.errors.append(
                    "metadata.difficulty_tiers must be a list of difficulty strings"
                )
            else:
                bad = [t for t in meta_tiers if t not in self.VALID_DIFFICULTIES]
                if bad:
                    self.errors.append(
                        f"metadata.difficulty_tiers has invalid tier(s) {bad}. "
                        f"Must be from: {sorted(self.VALID_DIFFICULTIES)}"
                    )
                if metadata.get('difficulty') not in meta_tiers:
                    self.errors.append(
                        f"metadata.difficulty_tiers {meta_tiers} must include "
                        f"the default difficulty '{metadata.get('difficulty')}'"
                    )
        
        # Check for Answer variable (or Answer1, Answer2, etc.)
        variables = data.get('variables', {})
        has_answer = 'Answer' in variables
        has_numbered_answers = any(key.startswith('Answer') and key[6:].isdigit() for key in variables)
        
        if not has_answer and not has_numbered_answers:
            self.errors.append(
                "Missing required answer variable: must have 'Answer' or 'Answer1', 'Answer2', etc."
            )
        
        # Warn about missing tests
        if 'tests' not in data or not data['tests']:
            self.warnings.append(
                "No tests defined. Recommended: 2-3 test cases for validation."
            )
        
        return not self.errors
    
    def _parse_variable(self, name: str, spec: Dict) -> VariableSpec:
        """Parse a variable specification."""
        var_type = spec.get('type')
        
        if var_type not in self.VALID_TYPES:
            self.errors.append(
                f"Invalid type '{var_type}' for variable '{name}'. "
                f"Must be one of: {self.VALID_TYPES}"
            )
        
        # Validate item category
        if var_type == 'item':
            category = spec.get('category')
            if category and category not in self.VALID_ITEM_CATEGORIES:
                self.errors.append(
                    f"Invalid item category '{category}' for variable '{name}'. "
                    f"Must be one of: {self.VALID_ITEM_CATEGORIES}"
                )
        
        # Validate constraints
        min_val = spec.get('min')
        max_val = spec.get('max')
        step = spec.get('step')
        
        if min_val is not None and max_val is not None:
            if min_val > max_val:
                self.errors.append(
                    f"Variable '{name}': min ({min_val}) must not exceed max ({max_val})"
                )
            
            if step is not None:
                range_val = max_val - min_val
                if range_val % step > 0.0001:  # Floating-point tolerance
                    self.warnings.append(
                        f"Variable '{name}': step ({step}) does not evenly divide "
                        f"range ({range_val}). May cause uneven distribution."
                    )
        
        # Validate per-variable unit_system override (if present)
        var_unit_system = spec.get('unit_system')
        if var_unit_system is not None and var_unit_system not in VALID_UNIT_SYSTEMS:
            self.errors.append(
                f"Variable '{name}': invalid unit_system '{var_unit_system}'. "
                f"Must be one of: {sorted(VALID_UNIT_SYSTEMS)}"
            )

        # Validate per-variable free-form `unit:` (Stage 3). Must parse
        # via the project's pint registry — typos like 'meeter' fail at
        # load time rather than rendering an empty suffix later.
        var_unit = spec.get('unit')
        if var_unit is not None:
            if not isinstance(var_unit, str) or not var_unit.strip():
                self.errors.append(
                    f"Variable '{name}': unit must be a non-empty pint unit string"
                )
                var_unit = None
            else:
                try:
                    ureg.parse_units(var_unit)
                except Exception as exc:
                    self.errors.append(
                        f"Variable '{name}': invalid pint unit "
                        f"{var_unit!r}: {exc}"
                    )
                    var_unit = None

        # Validate per-difficulty `ranges:` override (if present). Each key
        # must be a valid tier; each entry must be a mapping carrying any of
        # min/max/step/choices.
        ranges = spec.get('ranges')
        if ranges is not None:
            if not isinstance(ranges, dict):
                self.errors.append(
                    f"Variable '{name}': ranges must be a mapping of "
                    f"difficulty -> {{min, max, step, choices}}"
                )
                ranges = None
            else:
                for tier, tier_spec in ranges.items():
                    if tier not in self.VALID_DIFFICULTIES:
                        self.errors.append(
                            f"Variable '{name}': ranges key '{tier}' is not a "
                            f"valid difficulty. Must be one of: "
                            f"{sorted(self.VALID_DIFFICULTIES)}"
                        )
                    if not isinstance(tier_spec, dict):
                        self.errors.append(
                            f"Variable '{name}': ranges['{tier}'] must be a mapping"
                        )

        return VariableSpec(
            name=name,
            type=var_type,
            min=min_val,
            max=max_val,
            step=step,
            category=spec.get('category'),
            singular=spec.get('singular'),
            probability=spec.get('probability'),
            choices=spec.get('choices'),
            unit_system=var_unit_system,
            unit=var_unit,
            ranges=ranges,
        )
    
    def _parse_visual(self, raw: Any) -> Optional[VisualSpec]:
        """Parse and validate the optional `visual:` block."""
        if raw is None:
            return None
        if not isinstance(raw, dict):
            self.errors.append("visual: must be a mapping with `format` and `source` keys")
            return None

        fmt = raw.get('format')
        if fmt not in VALID_VISUAL_FORMATS:
            self.errors.append(
                f"visual.format '{fmt}' is invalid. "
                f"Must be one of: {sorted(VALID_VISUAL_FORMATS)}"
            )
            return None

        source = raw.get('source')
        if not isinstance(source, str) or not source.strip():
            self.errors.append("visual.source must be a non-empty string")
            return None

        alt_text = raw.get('alt_text')
        if alt_text is not None and not isinstance(alt_text, str):
            self.errors.append("visual.alt_text must be a string when present")
            return None

        return VisualSpec(format=fmt, source=source, alt_text=alt_text)

    def _validate_template(self, template_def: TemplateDefinition) -> None:
        """Validate template content and solution."""
        # Check solution sets Answer
        if 'Answer' not in template_def.solution:
            self.errors.append(
                "Solution must set the Answer variable"
            )

        # Validate solution is valid Python
        try:
            compile(template_def.solution, '<solution>', 'exec')
        except SyntaxError as e:
            self.errors.append(f"Solution has syntax error: {e}")

        # Enforce topic ↔ directory invariant: a template under
        # src/templates/<X>/ must declare topic: X.<subtopic>.
        if template_def.file_path is not None:
            parent_dir = template_def.file_path.parent.name
            top_topic = template_def.topic.split('.')[0]
            if top_topic != parent_dir:
                self.errors.append(
                    f"Topic '{template_def.topic}' does not match parent "
                    f"directory '{parent_dir}'. Top-level topic must equal "
                    f"the directory name (or move the file)."
                )
    
    def get_validation_results(self) -> Tuple[List[str], List[str]]:
        """Get validation errors and warnings."""
        return self.errors, self.warnings


def discover_yaml_templates(base_path: Path) -> List[Path]:
    """Discover all YAML template files recursively."""
    return sorted(base_path.rglob("*.yaml"))


def load_all_templates(base_path: Path) -> Dict[str, TemplateDefinition]:
    """Load all YAML templates from a directory."""
    loader = YAMLLoader()
    templates = {}
    
    for file_path in discover_yaml_templates(base_path):
        template = loader.load_template(file_path)
        if template:
            templates[template.id] = template
        else:
            print(f"Failed to load {file_path}:", file=sys.stderr)
            for error in loader.errors:
                print(f"  ERROR: {error}", file=sys.stderr)
            for warning in loader.warnings:
                print(f"  WARNING: {warning}", file=sys.stderr)
    
    return templates
