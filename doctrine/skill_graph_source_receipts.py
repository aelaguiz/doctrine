from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from doctrine import model
from doctrine.emit_common import (
    REPO_ROOT,
    EmitTarget,
    _validate_path_within_root,
    display_path,
    emit_error,
    entrypoint_relative_dir,
)


SOURCE_RECEIPT_FILE_NAME = "SKILL_GRAPH.source.json"
SOURCE_RECEIPT_VERSION = 1
DOCTRINE_LANGUAGE_VERSION = "5.7"


@dataclass(slots=True, frozen=True)
class GraphReceiptCheckResult:
    target_name: str
    status: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.status == "current"


def receipt_path_for_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
    graph: model.ResolvedSkillGraph | None = None,
) -> Path:
    output_dir = output_dir_for_target(target, output_dir_override=output_dir_override)
    raw_path = (
        _graph_source_view_path(graph)
        if graph is not None
        else SOURCE_RECEIPT_FILE_NAME
    )
    candidate = Path(raw_path)
    receipt_path = (
        candidate.resolve()
        if candidate.is_absolute()
        else (output_dir / candidate).resolve()
    )
    _validate_path_within_root(
        candidate_path=receipt_path,
        root=output_dir,
        detail_prefix=f"Skill graph source receipt for target `{target.name}`",
        code="E564",
        summary="Invalid skill graph view path",
    )
    return receipt_path


def output_dir_for_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> Path:
    output_root = (output_dir_override or target.output_dir).resolve()
    return output_root / entrypoint_relative_dir(target.entrypoint)


def build_graph_source_receipt_payload(
    *,
    target: EmitTarget,
    graph: model.ResolvedSkillGraph,
    input_paths: tuple[Path, ...],
    emitted_dir: Path,
    emitted_paths: tuple[Path, ...],
    resolved_view_paths: dict[str, Path],
    linked_package_receipts: tuple[dict[str, Any], ...],
    selected_view_keys: frozenset[str] | None = None,
) -> dict[str, Any]:
    inputs = _input_entries(input_paths)
    outputs = _output_entries(emitted_dir=emitted_dir, emitted_paths=emitted_paths)
    output_hashes = {entry["path"]: entry["sha256"] for entry in outputs}
    payload = {
        "receipt_version": SOURCE_RECEIPT_VERSION,
        "graph": {
            "name": graph.canonical_name,
            "title": graph.title,
            "purpose": graph.purpose,
        },
        "doctrine": {
            "language_version": DOCTRINE_LANGUAGE_VERSION,
            "package_version": _package_version(),
        },
        "target": {
            "name": target.name,
            "entrypoint": display_path(target.entrypoint.resolve()),
        },
        "inputs": inputs,
        "outputs": outputs,
        "source_tree_sha256": _tree_hash(inputs),
        "output_tree_sha256": _tree_hash(outputs),
        "graph_contract_sha256": _output_hash_for_path(
            output_hashes,
            emitted_dir=emitted_dir,
            path=resolved_view_paths["graph_contract"],
        ),
        "graph_json_sha256": _output_hash_for_path(
            output_hashes,
            emitted_dir=emitted_dir,
            path=resolved_view_paths["graph_json"],
        ),
        "diagram_d2_sha256": _output_hash_for_path(
            output_hashes,
            emitted_dir=emitted_dir,
            path=resolved_view_paths["diagram_d2"],
        ),
        "diagram_svg_sha256": _output_hash_for_path(
            output_hashes,
            emitted_dir=emitted_dir,
            path=resolved_view_paths["diagram_svg"],
        ),
        "diagram_mermaid_sha256": _output_hash_for_path(
            output_hashes,
            emitted_dir=emitted_dir,
            path=resolved_view_paths["diagram_mermaid"],
        ),
        "linked_package_receipts": list(linked_package_receipts),
    }
    if selected_view_keys is not None:
        payload["selected_views"] = sorted(selected_view_keys)
    return payload


def render_graph_source_receipt_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def verify_actual_output_tree(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
    graph: model.ResolvedSkillGraph | None = None,
    receipt_path: Path | None = None,
) -> GraphReceiptCheckResult | None:
    output_dir = output_dir_for_target(target)
    if not output_dir.is_dir():
        return GraphReceiptCheckResult(
            target.name,
            "edited_graph_artifact",
            f"Missing emitted graph directory: `{display_path(output_dir)}`.",
        )

    expected_outputs = tuple(
        entry
        for entry in receipt_payload.get("outputs", ())
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    )
    expected_paths = {str(entry["path"]) for entry in expected_outputs}
    actual_paths: set[str] = set()
    actual_receipt_path = (
        receipt_path or receipt_path_for_target(target, graph=graph)
    ).resolve()
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file() or path.resolve() == actual_receipt_path:
            continue
        actual_paths.add(path.relative_to(output_dir).as_posix())

    missing = sorted(expected_paths - actual_paths)
    if missing:
        return GraphReceiptCheckResult(
            target.name,
            "edited_graph_artifact",
            f"Missing emitted graph file: `{missing[0]}`.",
        )
    extra = sorted(actual_paths - expected_paths)
    if extra:
        return GraphReceiptCheckResult(
            target.name,
            "edited_graph_artifact",
            f"Unexpected emitted graph file: `{extra[0]}`.",
        )

    actual_entries = _entries_for_paths(
        (
            (
                output_dir / str(entry["path"]),
                str(entry["path"]),
                str(entry.get("kind", "graph_artifact")),
            )
            for entry in expected_outputs
        )
    )
    if _tree_hash(actual_entries) != receipt_payload.get("output_tree_sha256"):
        return GraphReceiptCheckResult(
            target.name,
            "edited_graph_artifact",
            "At least one emitted graph file was edited after emit.",
        )
    return None


def verify_linked_package_receipts(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
) -> GraphReceiptCheckResult | None:
    entries = receipt_payload.get("linked_package_receipts", ())
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        path_value = entry.get("receipt_path")
        expected_hash = entry.get("sha256")
        if not isinstance(path_value, str) or not isinstance(expected_hash, str):
            continue
        receipt_path = _payload_path(path_value)
        if not receipt_path.is_file():
            return GraphReceiptCheckResult(
                target.name,
                "missing_package_receipt",
                f"Missing linked package receipt: `{path_value}`.",
            )
        if _sha256_file(receipt_path) != expected_hash:
            return GraphReceiptCheckResult(
                target.name,
                "stale_package_receipt",
                f"Linked package receipt changed: `{path_value}`.",
            )
    return None


def verify_graph_receipt(
    *,
    target: EmitTarget,
    actual_receipt_payload: dict[str, Any],
    expected_receipt_payload: dict[str, Any],
) -> GraphReceiptCheckResult:
    actual_version = actual_receipt_payload.get("receipt_version")
    expected_version = expected_receipt_payload.get("receipt_version")
    if actual_version != SOURCE_RECEIPT_VERSION:
        return GraphReceiptCheckResult(
            target.name,
            "unsupported_graph_receipt_version",
            f"Expected receipt version {SOURCE_RECEIPT_VERSION}, got {actual_version!r}.",
        )
    if expected_version != SOURCE_RECEIPT_VERSION:
        return GraphReceiptCheckResult(
            target.name,
            "unsupported_graph_receipt_version",
            f"Compiler produced unsupported receipt version {expected_version!r}.",
        )
    if actual_receipt_payload.get("graph") != expected_receipt_payload.get("graph"):
        return GraphReceiptCheckResult(
            target.name,
            "stale_graph_source",
            "The graph identity does not match this target anymore.",
        )
    if actual_receipt_payload.get("doctrine") != expected_receipt_payload.get("doctrine"):
        return GraphReceiptCheckResult(
            target.name,
            "stale_graph_source",
            "The graph receipt Doctrine metadata does not match this compiler.",
        )
    if actual_receipt_payload.get("target") != expected_receipt_payload.get("target"):
        return GraphReceiptCheckResult(
            target.name,
            "stale_graph_source",
            "The graph receipt target identity does not match this emit target.",
        )
    if actual_receipt_payload.get("selected_views") != expected_receipt_payload.get(
        "selected_views"
    ):
        return GraphReceiptCheckResult(
            target.name,
            "stale_graph_source",
            "The graph receipt selected view set does not match a fresh graph emit.",
        )
    if actual_receipt_payload.get("source_tree_sha256") != expected_receipt_payload.get(
        "source_tree_sha256"
    ):
        return GraphReceiptCheckResult(
            target.name,
            "stale_graph_source",
            "The source prompt files no longer match this graph receipt.",
        )
    if actual_receipt_payload.get("graph_contract_sha256") != expected_receipt_payload.get(
        "graph_contract_sha256"
    ):
        return GraphReceiptCheckResult(
            target.name,
            "graph_contract_mismatch",
            "The graph contract no longer matches a fresh graph emit.",
        )
    if actual_receipt_payload.get("output_tree_sha256") != expected_receipt_payload.get(
        "output_tree_sha256"
    ):
        return GraphReceiptCheckResult(
            target.name,
            "edited_graph_artifact",
            "The emitted graph files no longer match a fresh graph emit.",
        )
    return GraphReceiptCheckResult(
        target.name,
        "current",
        "The emitted graph tree matches its current source receipt.",
    )


def read_receipt_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            f"Missing graph source receipt: `{display_path(path)}`.",
        ) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            f"Graph source receipt is not valid JSON: `{display_path(path)}`.",
        ) from exc
    if not isinstance(payload, dict):
        raise emit_error(
            "E565",
            "Skill graph emit failed",
            f"Graph source receipt must be a JSON object: `{display_path(path)}`.",
        )
    return payload


def _input_entries(paths: tuple[Path, ...]) -> tuple[dict[str, Any], ...]:
    unique = []
    seen: set[Path] = set()
    for path in sorted(path.resolve() for path in paths):
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        unique.append(
            {
                "path": display_path(path),
                "kind": "prompt",
                "sha256": _sha256_file(path),
            }
        )
    return tuple(unique)


def _output_entries(
    *,
    emitted_dir: Path,
    emitted_paths: tuple[Path, ...],
) -> tuple[dict[str, Any], ...]:
    entries = []
    for path in sorted(path.resolve() for path in emitted_paths):
        entries.append(
            {
                "path": path.relative_to(emitted_dir).as_posix(),
                "kind": "graph_artifact",
                "sha256": _sha256_file(path),
            }
        )
    return tuple(entries)


def _graph_source_view_path(graph: model.ResolvedSkillGraph) -> str:
    for view in graph.views:
        if view.key == "graph_source":
            return view.path
    return SOURCE_RECEIPT_FILE_NAME


def _entries_for_paths(
    entries: tuple[tuple[Path, str, str], ...] | Any,
) -> tuple[dict[str, Any], ...]:
    rendered = []
    for path, rel_path, kind in entries:
        rendered.append(
            {
                "path": rel_path,
                "kind": kind,
                "sha256": _sha256_file(path),
            }
        )
    return tuple(rendered)


def _tree_hash(entries: tuple[dict[str, Any], ...]) -> str:
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _output_hash_for_path(
    output_hashes: dict[str, str],
    *,
    emitted_dir: Path,
    path: Path,
) -> str | None:
    return output_hashes.get(path.resolve().relative_to(emitted_dir.resolve()).as_posix())


def _payload_path(path_value: str) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate.resolve()
    return (REPO_ROOT / candidate).resolve()


def _package_version() -> str:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    try:
        raw = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return "unknown"
    project = raw.get("project")
    if not isinstance(project, dict):
        return "unknown"
    version = project.get("version")
    return version if isinstance(version, str) else "unknown"
