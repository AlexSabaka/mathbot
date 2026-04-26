"""Thin Ollama HTTP client for the eval loop."""

import time

import httpx


DEFAULT_HOST = "http://localhost:11434"


def ollama_generate(
    model: str,
    prompt: str,
    system: str | None = None,
    host: str = DEFAULT_HOST,
    timeout: float = 120.0,
    options: dict | None = None,
) -> tuple[str, int]:
    """POST to Ollama /api/generate; return (response_text, latency_ms).

    One automatic retry on connection error.
    """
    payload: dict = {"model": model, "prompt": prompt, "stream": False}
    if system is not None:
        payload["system"] = system
    if options:
        payload["options"] = options

    last_exc: Exception | None = None
    for attempt in range(2):
        t0 = time.monotonic()
        try:
            with httpx.Client(timeout=timeout) as client:
                r = client.post(f"{host}/api/generate", json=payload)
                r.raise_for_status()
                data = r.json()
            latency_ms = int((time.monotonic() - t0) * 1000)
            return data.get("response", ""), latency_ms
        except (httpx.ConnectError, httpx.ReadError) as e:
            last_exc = e
            if attempt == 0:
                time.sleep(0.5)
                continue
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

    raise RuntimeError(f"Ollama unreachable after retry: {last_exc}")


def ollama_list_models(host: str = DEFAULT_HOST, timeout: float = 10.0) -> list[str]:
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{host}/api/tags")
        r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]
