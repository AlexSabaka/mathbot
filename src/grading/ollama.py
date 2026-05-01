"""Thin Ollama `/api/generate` client.

Pure stdlib (`urllib.request`). No new dependency in `pyproject.toml`.
The grader is the only caller; this module exists so the network code
stays out of the rubric/finding logic and is straightforward to mock in
tests by patching `urllib.request.urlopen`.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


DEFAULT_HOST = "http://localhost:11434"
DEFAULT_TIMEOUT = 180.0  # K1 prompts at qwen3.5:2b commonly take 30–90s.
DEFAULT_NUM_PREDICT = 1024
"""Hard cap on generated tokens. Small models (e.g. qwen3.5:0.8b) can
loop indefinitely without one — the rubric's ~20 verdicts fit in well
under 512 tokens, so 1024 leaves headroom without burning compute on
runaway generation."""


class OllamaError(RuntimeError):
    """Raised when the Ollama call fails after the one allowed retry."""


def call_ollama(
    model: str,
    prompt: str,
    *,
    host: str = DEFAULT_HOST,
    image_b64: Optional[List[str]] = None,
    temperature: float = 0.0,
    timeout: float = DEFAULT_TIMEOUT,
    format_json: bool = True,
    think: bool = False,
) -> Dict[str, Any]:
    """POST to `<host>/api/generate` and return the parsed response body.

    `image_b64` is a list of base64-encoded PNG bytes (without the
    `data:` prefix). When None or empty the request is text-only and any
    text-only Ollama model can serve it.

    `think=False` (default) suppresses the dedicated `thinking` channel
    on reasoning models like `qwen3.5:*` — without it, those models
    return their JSON in `thinking` and leave `response` empty when
    `format=json` is set. Non-thinking models ignore the flag.

    Returns the raw response dict from Ollama (which contains a
    `response` field with the model's generated text). The grader is
    responsible for parsing the JSON inside `response`.
    """
    body: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": bool(think),
        "options": {
            "temperature": float(temperature),
            "num_predict": DEFAULT_NUM_PREDICT,
        },
    }
    if format_json:
        body["format"] = "json"
    if image_b64:
        body["images"] = list(image_b64)

    payload = json.dumps(body).encode("utf-8")
    url = host.rstrip("/") + "/api/generate"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_err: Optional[Exception] = None
    for attempt in range(2):  # one retry on transport error
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_err = exc
            if attempt == 1:
                break
        except json.JSONDecodeError as exc:
            # Server returned 200 but the body isn't JSON — don't retry,
            # surface immediately so the grader records a parse_error
            # finding rather than waiting for a second timeout.
            raise OllamaError(f"ollama returned non-JSON body: {exc}") from exc

    raise OllamaError(f"ollama request failed: {last_err}") from last_err
