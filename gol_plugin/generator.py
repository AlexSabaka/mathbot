"""Mathbot generator — shells out to the mathbot CLI to produce test cases.

Decoupling: avoids importing mathbot directly because mathbot's package layout
roots at `src/`, which collides with gol_eval's own `src.*` namespace.
A single `uv run --project <mathbot_root> mathbot batch …` call generates `count`
problems in one shot; we parse stdout JSONL into TestCase objects.

The mathbot project root is discovered by following this file's symlink and
walking up until a `pyproject.toml` with `name = "mathbot"` is found.
"""

import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.plugins.base import ConfigField, TestCase, TestCaseGenerator
from src.plugins.i18n.loader import compose_user_prompt

from .evaluator import classify_shape


_ANY = "any"  # sentinel for "no filter"; non-empty so Radix Select accepts it
_GRADE_OPTIONS = ["elementary", "middle", "high", "college", "university"]
_COMPLEXITY_OPTIONS = [1, 2, 3]
_TOPIC_OPTIONS = [
    "numbers", "arithmetic", "percentages", "fractions", "decimals", "ratios",
    "algebra", "geometry", "measurement", "statistics",
    "quadratics", "derivatives", "powers_logs",
]


def _find_mathbot_root() -> Path:
    """Resolve symlinks then walk up to find mathbot's project root."""
    here = Path(__file__).resolve()
    for ancestor in (here, *here.parents):
        candidate = ancestor / "pyproject.toml"
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8")
            if 'name = "mathbot"' in text:
                return ancestor
    raise RuntimeError(
        "Could not locate mathbot's project root from "
        f"{here}. Expected a pyproject.toml with `name = \"mathbot\"`."
    )


class MathbotGenerator(TestCaseGenerator):
    PLUGIN_NAME = "mathbot"

    def generate_batch(
        self,
        config: Dict[str, Any],
        prompt_config: Dict[str, str],
        count: int,
        seed: Optional[int] = None,
    ) -> List[TestCase]:
        if count <= 0:
            return []

        language = prompt_config.get("language", "en")
        user_style = prompt_config.get("user_style", "linguistic")
        system_style = prompt_config.get("system_style", "analytical")
        config_name = prompt_config.get("name", f"{user_style}_{system_style}")

        mathbot_root = (
            Path(config["mathbot_root"]).expanduser()
            if config.get("mathbot_root")
            else _find_mathbot_root()
        )

        cmd = [
            "uv", "run", "--project", str(mathbot_root),
            "mathbot", "batch", str(count),
            "-s", str(seed if seed is not None else 0),
            "-o", "jsonl",
        ]
        if (grade := _resolve(config.get("grade"))):
            cmd.extend(["-g", grade])
        if (topic := _resolve(config.get("topic"))):
            cmd.extend(["-t", topic])
        if (family := _resolve(config.get("family"))):
            cmd.extend(["-f", family])
        if (complexity := _resolve(config.get("complexity"))):
            cmd.extend(["-c", complexity])
        if num_steps := config.get("num_steps"):
            cmd.extend(["-n", str(num_steps)])

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_seconds", 300),
            env={**os.environ, "VIRTUAL_ENV": ""},
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"mathbot batch failed (exit {proc.returncode}):\n"
                f"  cmd: {' '.join(cmd)}\n"
                f"  stderr: {proc.stderr.strip()[:600]}"
            )

        timestamp = _dt.datetime.now(tz=_dt.timezone.utc).isoformat()
        test_cases: List[TestCase] = []

        for i, line in enumerate(proc.stdout.splitlines()):
            line = line.strip()
            if not line:
                continue
            mb = json.loads(line)
            problem_text = mb["problem"]
            params_in = mb.get("task_params", {}) or {}
            expected = params_in.get("expected_answer", "")

            user_prompt = compose_user_prompt(
                self.PLUGIN_NAME, language, user_style, problem=problem_text,
            )
            system_prompt = self._get_system_prompt(system_style, language)
            full_prompt = (
                f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
            )

            test_cases.append(TestCase(
                test_id=f"mathbot_{seed if seed is not None else 0}_{i:04d}",
                task_type="mathbot",
                config_name=config_name,
                prompts={
                    "system": system_prompt,
                    "user": user_prompt,
                    "full": full_prompt,
                },
                task_params={
                    "expected_answer": expected,
                    "answer_shape": classify_shape(expected),
                    "mathbot_grade": params_in.get("grade"),
                    "mathbot_topic": params_in.get("math_topic"),
                    "mathbot_family": params_in.get("problem_family"),
                    "mathbot_complexity": params_in.get("complexity"),
                    "mathbot_num_steps": params_in.get("num_steps"),
                    "mathbot_test_id": mb.get("test_id"),
                    "mathbot_template_path": mb.get("template_path"),
                },
                prompt_metadata={
                    "language": language,
                    "user_style": user_style,
                    "system_style": system_style,
                },
                generation_metadata={
                    "seed": seed,
                    "index": i,
                    "timestamp": timestamp,
                    "version": "1.0.0",
                    "mathbot_root": str(mathbot_root),
                },
            ))

        return test_cases

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "grade": _ANY,
            "complexity": _ANY,
            "topic": _ANY,
            "family": "",
            "num_steps": 0,
            "mathbot_root": "",
        }

    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="grade", label="Grade band", field_type="select",
                default=_ANY, options=[_ANY, *_GRADE_OPTIONS],
                help="Coarse grade band (mathbot CLI accepts elementary/middle/high). "
                     "Pick 'any' for no grade filter.",
            ),
            ConfigField(
                name="complexity", label="Complexity", field_type="select",
                default=_ANY, options=[_ANY, *(str(c) for c in _COMPLEXITY_OPTIONS)],
                help="1=easy, 2=medium, 3=hard. Pick 'any' for no filter.",
            ),
            ConfigField(
                name="topic", label="Math topic", field_type="select",
                default=_ANY, options=[_ANY, *_TOPIC_OPTIONS],
                help="Filter by top-level math topic. Pick 'any' for no filter.",
            ),
            ConfigField(
                name="family", label="Problem family", field_type="text",
                default="",
                help="Optional fine-grained family (e.g. 'sequential_purchase'). "
                     "Mathbot defines ~80 families. Leave empty for no filter.",
                group="advanced",
            ),
            ConfigField(
                name="num_steps", label="Solution steps", field_type="number",
                default=0, min_value=0, max_value=10, step=1,
                help="Filter by solution step count (1-10). 0 = any.",
                group="advanced",
            ),
            ConfigField(
                name="mathbot_root", label="Mathbot project path", field_type="text",
                default="",
                help="Override the auto-detected mathbot project root. "
                     "Leave empty when using the symlinked plugin.",
                group="advanced",
            ),
        ]


def _resolve(value: Any) -> Optional[str]:
    """Normalise a config value to a CLI string, or None when the user wants no filter.

    Empty string, ``None``, the sentinel ``"any"``, and the int ``0`` all mean
    'no filter'. Lists/tuples collapse to their first element under the same rules.
    """
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() == _ANY or s == "0":
        return None
    return s


# Re-export for tests / external smoke scripts that want to inspect the helper.
find_mathbot_root = _find_mathbot_root


# Avoid an unused-import lint when sys is only referenced via env tweaks above.
_ = sys
