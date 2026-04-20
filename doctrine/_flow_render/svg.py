from __future__ import annotations

from pathlib import Path


def ensure_pinned_d2_dependency(
    package_path: Path,
    *,
    helper_path: Path | None = None,
    dependency_error_type,
) -> None:
    if not package_path.is_file():
        raise dependency_error_type(
            "Pinned D2 dependency is missing under `node_modules/@terrastruct/d2`. Run `npm ci` at the repo root.",
            hints=("Run `npm ci` at the repo root.",),
        )
    if helper_path is not None and not helper_path.is_file():
        raise dependency_error_type(
            f"Doctrine flow renderer helper is missing: `{helper_path}`. Restore the `flow_svg.mjs` helper file.",
            hints=("Restore the `flow_svg.mjs` helper file.",),
        )


def render_flow_svg(
    d2_path: Path,
    svg_path: Path,
    *,
    repo_root: Path,
    helper_path: Path,
    package_path: Path,
    run,
    dependency_error_type,
    failure_type,
) -> None:
    """Spawn the pinned D2 helper as a subprocess and translate its failures.

    Two error translations live here and are the reason the public facade
    raises two different exception types:
      - `FileNotFoundError` from `run(...)` means `node` itself is not on
        PATH. That is a prerequisite problem, not a render problem, so it
        becomes `dependency_error_type` (mapped to E515 upstream).
      - Non-zero exit after the helper starts means D2 compiled or rendered
        the source but the helper rejected it. That becomes `failure_type`
        (mapped to E516 upstream) with the helper's stderr — falling back to
        stdout, then a synthesized exit-code message — as the detail.

    Other prerequisite problems (missing pinned bundle, missing helper file)
    are caught by the `ensure_pinned_d2_dependency` pre-flight before any
    subprocess spawns.
    """
    ensure_pinned_d2_dependency(
        package_path,
        helper_path=helper_path,
        dependency_error_type=dependency_error_type,
    )

    try:
        result = run(
            ["node", str(helper_path), str(d2_path), str(svg_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise dependency_error_type(
            "Node.js is required to render flow SVG output, but `node` was not found on PATH."
        ) from exc
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout).strip() or f"node exited {result.returncode}"
    raise failure_type(detail)
