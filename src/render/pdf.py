"""B.4 PDF-rendering pipeline (tectonic backend).

Compiles the LaTeX form via the `tectonic` binary — a single-file,
network-free, deterministic LaTeX compiler. Chosen over `latexmk` /
`xelatex` because it has zero per-machine setup beyond installing
the binary itself: no texlive distribution, no `tlmgr` package
fetches, and reproducible output across machines.

System dep: `tectonic` binary on PATH.

  - macOS: ``brew install tectonic`` or ``cargo install tectonic``
  - Debian/Ubuntu: ``apt install tectonic`` (newer releases) or cargo
  - Fedora: ``dnf install tectonic`` (or cargo)

The first compile downloads the relevant LaTeX packages (~60 MB
total) into ``~/.cache/Tectonic``; subsequent compiles are fully
offline. Per-template wall-clock is typically 1–3 seconds.

`render_pdf` returns the compiled PDF as bytes. The caller is
responsible for writing the bytes (or for sidecar image files
referenced by the LaTeX). Errors surface as ``RuntimeError`` with
the tectonic stderr appended — the LaTeX log file is captured so
the user can inspect compile failures.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional

from .latex import render_latex


# tectonic's *first* compile on a fresh cache downloads ~60 MB of
# LaTeX packages from the network — this is a one-time cost and
# subsequent compiles drop to ~1–3 s. The timeout has to cover the
# cold-cache case so a freshly installed tectonic doesn't time out
# on its first run; users on slow connections may need to bump it.
_TECTONIC_TIMEOUT_SECONDS = 120


def render_pdf(
    problem: Dict,
    *,
    show_answer: bool = True,
    image_path: Optional[Path] = None,
    timeout: int = _TECTONIC_TIMEOUT_SECONDS,
) -> bytes:
    """Compile a generated problem dict to PDF bytes.

    When the problem carries a ``visual`` block and ``image_path``
    is *not* supplied, the function auto-generates a composite-PNG
    sidecar (body + visual + answer composed into a single SVG via
    :func:`src.visuals.compose.compose_problem_svg`, then
    rasterised via cairosvg) and feeds it to LaTeX as the figure.
    The auto-generated sidecar lives in the temp directory tectonic
    works in and is cleaned up after compile.

    ``image_path`` (if set) takes precedence over auto-generation —
    pass it when you've already prepared a sidecar (multi-format
    mode does this so latex / pdf / png in one batch share one
    PNG render).

    Raises :exc:`RuntimeError` when tectonic isn't on PATH, when
    cairosvg / libcairo are missing for auto-PNG generation, or
    when the compile fails. The exception message includes the
    stderr output so a tectonic-level error (missing package,
    syntax) is surfaced cleanly.
    """
    _check_tectonic()

    # Auto-generate composite PNG sidecar when the problem has a
    # visual but the caller didn't supply one. This keeps `-o pdf`
    # self-contained: a problem with a visual produces a PDF
    # *with* the figure, no extra setup required.
    auto_png_bytes: Optional[bytes] = None
    auto_png_name: Optional[str] = None
    visual_block = problem.get('visual') or {}
    visual_source = visual_block.get('source')
    if image_path is None and visual_source:
        auto_png_bytes = _compose_problem_to_png_bytes(
            problem, show_answer=show_answer,
        )
        auto_png_name = "problem_visual.png"

    effective_image_path: Optional[object] = image_path
    if auto_png_name is not None:
        # render_latex stringifies the image_path; using the bare
        # filename means tectonic resolves it from its working dir
        # (where we'll drop auto_png_bytes before compile).
        effective_image_path = auto_png_name

    latex_source = render_latex(
        problem,
        show_answer=show_answer,
        fragment=False,
        image_path=effective_image_path,
    )
    return _compile_with_tectonic(
        latex_source,
        external_assets=[image_path] if image_path is not None else [],
        inline_assets=[(auto_png_name, auto_png_bytes)] if auto_png_bytes else [],
        timeout=timeout,
    )


def _compose_problem_to_png_bytes(problem: Dict, *, show_answer: bool) -> bytes:
    """Rasterise the visual SVG (only) to PNG bytes for LaTeX embed.

    *Not* the composite (body + visual + answer): the LaTeX document
    already typesets the body and the answer, so embedding the
    composite would duplicate that text inside the figure. The PDF
    review surfaced this as a "rendered visual contains problem text
    too" recursion. The fix is for the figure inside a LaTeX
    document to carry *only* the visual; body / answer come from
    the surrounding text.

    Standalone ``-o png`` uses ``compose_problem_svg`` (composite)
    via [src.cli], not this function. The two output forms are
    deliberately distinct:

    - ``-o png``: a single image of the whole problem (body + visual
      + answer). Useful for one-off inspection.
    - ``-o pdf`` / ``-o latex --formats ...``: the visual lives
      *inside* a LaTeX document; only the figure needs to be a
      raster.

    Raises :exc:`RuntimeError` with the same friendly message when
    cairosvg / libcairo isn't usable.
    """
    visual_block = problem.get('visual') or {}
    visual_svg = visual_block.get('source')
    if not visual_svg:
        raise RuntimeError(
            "_compose_problem_to_png_bytes: problem has no visual.source"
        )

    try:
        import cairosvg
    except ImportError:
        raise RuntimeError(
            "cairosvg is needed to embed visuals in PDFs. "
            "Install with `uv sync --extra png`."
        )
    except OSError as exc:
        raise RuntimeError(
            f"cairosvg loaded but libcairo is missing: {exc}\n"
            f"Install the system library:\n"
            f"  macOS:        brew install cairo\n"
            f"  Debian/Ubuntu: sudo apt install libcairo2\n"
            f"  Fedora:       sudo dnf install cairo"
        )

    try:
        return cairosvg.svg2png(bytestring=visual_svg.encode('utf-8'))
    except OSError as exc:
        raise RuntimeError(
            f"libcairo runtime error while rasterising the visual: {exc}\n"
            f"Confirm `libcairo` is on your dylib search path "
            f"(macOS: `DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib` "
            f"if installed via Homebrew)."
        )


def _check_tectonic() -> None:
    """Fail fast if the binary isn't installed."""
    if shutil.which("tectonic") is None:
        raise RuntimeError(
            "tectonic binary not found on PATH. PDF rendering requires "
            "tectonic; install via:\n"
            "  macOS:        brew install tectonic\n"
            "  Linux:        apt/dnf install tectonic, or cargo install tectonic\n"
            "Once installed, re-run the same command."
        )


def _compile_with_tectonic(
    latex_source: str,
    *,
    external_assets: list,
    inline_assets: Optional[list] = None,
    timeout: int,
) -> bytes:
    """Run tectonic on ``latex_source`` and return the PDF bytes.

    Uses an isolated temp directory as the working tree so concurrent
    invocations don't fight over filenames. ``external_assets`` (e.g.
    a PNG sidecar referenced via ``\\includegraphics``) is copied
    into the same temp directory if it's not already an absolute path
    that tectonic can resolve from the working directory.
    ``inline_assets`` is a list of ``(filename, bytes)`` tuples for
    auto-generated artifacts (composite-PNG of the visual) that have
    no on-disk source file — they get written into the temp dir
    under ``filename`` directly.
    """
    inline_assets = inline_assets or []

    with tempfile.TemporaryDirectory(prefix="mathbot_pdf_") as tmp:
        tmp_path = Path(tmp)
        tex_path = tmp_path / "doc.tex"
        tex_path.write_text(latex_source, encoding="utf-8")

        for asset in external_assets:
            if asset is None:
                continue
            asset = Path(asset)
            if asset.exists():
                # Copy under the same basename so the LaTeX
                # \\includegraphics{<path>} call can reference it
                # via the relative path the renderer chose.
                target = tmp_path / asset.name
                if asset.resolve() != target.resolve():
                    target.write_bytes(asset.read_bytes())

        for name, payload in inline_assets:
            if name is None or payload is None:
                continue
            (tmp_path / name).write_bytes(payload)

        cmd = [
            "tectonic",
            "--keep-logs",
            "--outdir", str(tmp_path),
            str(tex_path),
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=tmp_path,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"tectonic timed out after {timeout}s. The two common causes:\n"
                f"  1. Cold cache: tectonic's first compile downloads ~60 MB\n"
                f"     of LaTeX packages. Run `tectonic --help` once to warm\n"
                f"     the cache, then retry; subsequent compiles take 1–3 s.\n"
                f"  2. Runaway macro in the LaTeX. Inspect with\n"
                f"     `mathbot generate ... -o latex --fragment` and a\n"
                f"     manual compile."
            ) from exc

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            log_path = tmp_path / "doc.log"
            log_excerpt = ""
            if log_path.exists():
                # The LaTeX log is verbose; show the last 40 lines —
                # that's where tectonic puts the actual error.
                log_lines = log_path.read_text(
                    encoding="utf-8", errors="replace",
                ).splitlines()
                log_excerpt = "\n".join(log_lines[-40:])
            raise RuntimeError(
                f"tectonic compile failed (exit {result.returncode}).\n"
                f"--- stderr ---\n{stderr}\n"
                f"--- log tail ---\n{log_excerpt}"
            )

        pdf_path = tmp_path / "doc.pdf"
        if not pdf_path.exists():
            raise RuntimeError(
                "tectonic exited 0 but produced no PDF; this should not happen"
            )
        return pdf_path.read_bytes()
