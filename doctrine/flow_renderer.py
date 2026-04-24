"""Public flow-render entrypoint for `emit_flow` and tests.

This module pins the repo-relative host paths (pinned D2 package, the
`flow_svg.mjs` helper, and `REPO_ROOT`) and forwards to `_flow_render.svg`
for the actual subprocess work. Keep it thin: new rendering logic belongs
in `_flow_render/` so every public caller shares one canonical entrypoint.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from doctrine._compiler.types import FlowGraph
from doctrine._flow_render.d2 import render_flow_d2 as _render_flow_d2
from doctrine._flow_render.layout import FlowLanePlan, ROUTE_EDGE_KINDS
from doctrine._flow_render.svg import (
    ensure_pinned_d2_dependency as _ensure_pinned_d2_dependency,
    render_flow_svg as _render_flow_svg,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
D2_HELPER_PATH = Path(__file__).resolve().with_name("flow_svg.mjs")
D2_PACKAGE_PATH = REPO_ROOT / "node_modules" / "@terrastruct" / "d2" / "package.json"


class FlowRenderDependencyError(RuntimeError):
    """Raised when flow renderer prerequisites are unavailable."""

    def __init__(self, message: str, *, hints: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.hints = hints


class FlowRenderFailure(RuntimeError):
    """Raised when D2 fails to render SVG output."""


def ensure_pinned_d2_dependency() -> None:
    _ensure_pinned_d2_dependency(
        D2_PACKAGE_PATH,
        helper_path=D2_HELPER_PATH,
        dependency_error_type=FlowRenderDependencyError,
    )


def render_flow_d2(graph: FlowGraph) -> str:
    return _render_flow_d2(graph)


def render_flow_svg(d2_path: Path, svg_path: Path) -> None:
    """Render the `.d2` source at `d2_path` into an SVG at `svg_path`.

    Raises `FlowRenderDependencyError` when a prerequisite is missing: the
    pinned D2 bundle under `node_modules/`, the `flow_svg.mjs` helper, or
    `node` on PATH. Raises `FlowRenderFailure` when the helper times out or
    exits non-zero (D2 itself rejected the source). The caller in
    `emit_flow.py` maps these to diagnostic codes E515 and E516 respectively.

    Caller invariant: `d2_path` must already be on disk before this runs, and
    stays on disk if this raises. That lets authors inspect the exact source
    that failed to render without re-running the compile pass.
    """
    _render_flow_svg(
        d2_path,
        svg_path,
        repo_root=REPO_ROOT,
        helper_path=D2_HELPER_PATH,
        package_path=D2_PACKAGE_PATH,
        run=subprocess.run,
        dependency_error_type=FlowRenderDependencyError,
        failure_type=FlowRenderFailure,
    )
