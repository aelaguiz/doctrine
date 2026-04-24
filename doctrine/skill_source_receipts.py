from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any

from doctrine import model
from doctrine._compiler.indexing import IndexedUnit
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    display_path,
    emit_error,
    entrypoint_relative_dir,
)

if TYPE_CHECKING:
    from doctrine._compiler.session import CompilationSession
    from doctrine._compiler.types import CompiledSkillPackage


SOURCE_RECEIPT_FILE_NAME = "SKILL.source.json"
SOURCE_RECEIPT_VERSION = 1
SKILL_LOCK_VERSION = 1
DOCTRINE_LANGUAGE_VERSION = "5.7"


@dataclass(slots=True, frozen=True)
class SkillReceiptCheckResult:
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
) -> Path:
    output_root = (output_dir_override or target.output_dir).resolve()
    return output_root / entrypoint_relative_dir(target.entrypoint) / SOURCE_RECEIPT_FILE_NAME


def build_skill_source_receipt_payload(
    *,
    target: EmitTarget,
    compiled: "CompiledSkillPackage",
    package_decl: model.SkillPackageDecl,
    session: "CompilationSession",
    emitted_dir: Path,
    emitted_paths: tuple[Path, ...],
) -> dict[str, Any]:
    source_root = _receipt_source_root(target)
    inputs = _collect_source_inputs(
        target=target,
        package_decl=package_decl,
        session=session,
        source_root=source_root,
    )
    outputs = _collect_output_entries(
        compiled=compiled,
        emitted_dir=emitted_dir,
        emitted_paths=emitted_paths,
    )
    source_id = (
        target.source_id
        or package_decl.source.source_id
        or package_decl.metadata.name
        or package_decl.name
    )
    return {
        "receipt_version": SOURCE_RECEIPT_VERSION,
        "package": {
            "name": compiled.name,
            "title": compiled.title,
        },
        "doctrine": {
            "language_version": DOCTRINE_LANGUAGE_VERSION,
            "package_version": _package_version(),
        },
        "source": {
            "id": source_id,
            "root": display_path(source_root),
            "entrypoint": _relative_posix(target.entrypoint, source_root),
        },
        "inputs": inputs,
        "outputs": outputs,
        "source_tree_sha256": _tree_hash(inputs),
        "output_tree_sha256": _tree_hash(outputs),
    }


def render_skill_source_receipt_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def update_skill_lock(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
    receipt_path: Path,
) -> None:
    if target.lock_file is None:
        return
    lock_entries = _read_lock_entries(target.lock_file)
    lock_entries[target.name] = _lock_entry_for_receipt(
        target=target,
        receipt_payload=receipt_payload,
        receipt_path=receipt_path,
    )
    target.lock_file.parent.mkdir(parents=True, exist_ok=True)
    target.lock_file.write_text(_render_skill_lock(lock_entries), encoding="utf-8")


def verify_skill_receipt(
    *,
    target: EmitTarget,
    actual_receipt_payload: dict[str, Any],
    expected_receipt_payload: dict[str, Any],
) -> SkillReceiptCheckResult:
    expected_version = expected_receipt_payload.get("receipt_version")
    actual_version = actual_receipt_payload.get("receipt_version")
    if actual_version != SOURCE_RECEIPT_VERSION:
        return SkillReceiptCheckResult(
            target.name,
            "unsupported_receipt_version",
            f"Expected receipt version {SOURCE_RECEIPT_VERSION}, got {actual_version!r}.",
        )
    if expected_version != SOURCE_RECEIPT_VERSION:
        return SkillReceiptCheckResult(
            target.name,
            "unsupported_receipt_version",
            f"Compiler produced unsupported receipt version {expected_version!r}.",
        )

    if actual_receipt_payload.get("package") != expected_receipt_payload.get("package"):
        return SkillReceiptCheckResult(
            target.name,
            "foreign_package",
            "The receipt package does not match this emit target.",
        )
    if actual_receipt_payload.get("source") != expected_receipt_payload.get("source"):
        return SkillReceiptCheckResult(
            target.name,
            "stale_source",
            "The receipt source identity does not match this emit target.",
        )
    if actual_receipt_payload.get("doctrine") != expected_receipt_payload.get("doctrine"):
        return SkillReceiptCheckResult(
            target.name,
            "stale_source",
            "The receipt Doctrine metadata does not match this compiler.",
        )
    if actual_receipt_payload.get("source_tree_sha256") != expected_receipt_payload.get(
        "source_tree_sha256"
    ):
        return SkillReceiptCheckResult(
            target.name,
            "stale_source",
            "The source files no longer match the emitted receipt.",
        )
    if actual_receipt_payload.get("output_tree_sha256") != expected_receipt_payload.get(
        "output_tree_sha256"
    ):
        return SkillReceiptCheckResult(
            target.name,
            "edited_artifact",
            "The emitted files no longer match the source build.",
        )

    lock_result = _verify_lock(target=target, receipt_payload=actual_receipt_payload)
    if lock_result is not None:
        return lock_result

    return SkillReceiptCheckResult(
        target.name,
        "current",
        "The emitted skill tree matches its current source receipt.",
    )


def verify_actual_output_tree(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
) -> SkillReceiptCheckResult | None:
    output_dir = receipt_path_for_target(target).parent
    expected_outputs = tuple(
        entry
        for entry in receipt_payload.get("outputs", ())
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    )
    expected_paths = {str(entry["path"]) for entry in expected_outputs}
    if not output_dir.is_dir():
        return SkillReceiptCheckResult(
            target.name,
            "edited_artifact",
            f"Missing emitted skill directory: `{display_path(output_dir)}`.",
        )

    actual_paths: set[str] = set()
    root_receipt_path = output_dir / SOURCE_RECEIPT_FILE_NAME
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file() or path == root_receipt_path:
            continue
        actual_paths.add(path.relative_to(output_dir).as_posix())

    missing = sorted(expected_paths - actual_paths)
    if missing:
        return SkillReceiptCheckResult(
            target.name,
            "edited_artifact",
            f"Missing emitted file: `{missing[0]}`.",
        )
    extra = sorted(actual_paths - expected_paths)
    if extra:
        return SkillReceiptCheckResult(
            target.name,
            "unexpected_artifact",
            f"Unexpected emitted file: `{extra[0]}`.",
        )

    actual_entries = _entries_for_paths(
        (
            (
                output_dir / str(entry["path"]),
                str(entry["path"]),
                str(entry.get("kind", "file")),
            )
            for entry in expected_outputs
        )
    )
    if _tree_hash(actual_entries) != receipt_payload.get("output_tree_sha256"):
        return SkillReceiptCheckResult(
            target.name,
            "edited_artifact",
            "At least one emitted file was edited after emit.",
        )
    return None


def read_receipt_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise emit_error(
            "E554",
            "Missing skill source receipt",
            f"Missing skill source receipt: `{display_path(path)}`.",
            location=path_location_for(path),
        ) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise emit_error(
            "E555",
            "Invalid skill source receipt",
            f"Skill source receipt is not valid JSON: `{display_path(path)}`.",
            location=path_location_for(path),
            cause=str(exc),
        ) from exc
    if not isinstance(payload, dict):
        raise emit_error(
            "E555",
            "Invalid skill source receipt",
            f"Skill source receipt must be a JSON object: `{display_path(path)}`.",
            location=path_location_for(path),
        )
    return payload


def _receipt_source_root(target: EmitTarget) -> Path:
    return (target.source_root or target.entrypoint.parent).resolve()


def _collect_source_inputs(
    *,
    target: EmitTarget,
    package_decl: model.SkillPackageDecl,
    session: "CompilationSession",
    source_root: Path,
) -> tuple[dict[str, str], ...]:
    source_paths: dict[Path, str] = {}

    package_root = target.entrypoint.parent.resolve()
    package_files = sorted(path for path in package_root.rglob("*") if path.is_file())
    reserved_prompt_dirs = {
        path.parent
        for path in package_files
        if path.suffix == ".prompt"
        and path.parent != package_root
        and not _is_bundled_agent_prompt(path, package_root=package_root)
    }
    for path in package_files:
        if path.suffix == ".prompt" and not _is_bundled_agent_prompt(
            path,
            package_root=package_root,
        ):
            continue
        if any(
            reserved_dir == path.parent or reserved_dir in path.parents
            for reserved_dir in reserved_prompt_dirs
        ):
            continue
        source_paths[path.resolve()] = "package_file"

    for path in _session_prompt_paths(session):
        source_paths[path.resolve()] = "prompt"

    for tracked in package_decl.source.tracked_paths:
        for path in _resolve_tracked_paths(
            tracked,
            source_root=source_root,
            target=target,
        ):
            source_paths[path.resolve()] = "tracked"

    source_paths[target.entrypoint.resolve()] = "entrypoint"

    return _entries_for_paths(
        (
            (path, _relative_posix(path, source_root), kind)
            for path, kind in sorted(source_paths.items(), key=lambda item: _relative_posix(item[0], source_root))
        )
    )


def _session_prompt_paths(session: "CompilationSession") -> tuple[Path, ...]:
    paths: set[Path] = set()
    for flow in session._flow_cache.values():
        units: tuple[IndexedUnit, ...] = tuple(flow.units_by_path.values())
        for unit in units:
            source_path = unit.prompt_file.source_path
            if source_path is not None and source_path.is_file():
                paths.add(source_path.resolve())
    return tuple(sorted(paths))


def _is_bundled_agent_prompt(path: Path, *, package_root: Path) -> bool:
    if path.suffix != ".prompt" or path.parent == package_root:
        return False
    try:
        rel_path = path.relative_to(package_root)
    except ValueError:
        return False
    return bool(rel_path.parts) and rel_path.parts[0] == "agents"


def _resolve_tracked_paths(
    tracked: model.SkillPackageTrackedSource,
    *,
    source_root: Path,
    target: EmitTarget,
) -> tuple[Path, ...]:
    path_text = tracked.path
    if "\\" in path_text:
        raise emit_error(
            "E556",
            "Invalid tracked source path",
            f"Tracked source paths must use `/` separators in target `{target.name}`: {path_text}",
            hints=("Use a relative POSIX path inside the source root.",),
        )
    pure = PurePosixPath(path_text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise emit_error(
            "E556",
            "Invalid tracked source path",
            f"Tracked source path must stay inside the source root in target `{target.name}`: {path_text}",
            hints=("Use a relative path with no `.` or `..` segments.",),
        )
    resolved = (source_root / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(source_root.resolve())
    except ValueError as exc:
        raise emit_error(
            "E556",
            "Invalid tracked source path",
            f"Tracked source path leaves the source root in target `{target.name}`: {path_text}",
            hints=("Keep tracked paths below `source_root`.",),
        ) from exc
    if not resolved.exists():
        raise emit_error(
            "E554",
            "Missing tracked source path",
            f"Tracked source path does not exist in target `{target.name}`: `{display_path(resolved)}`.",
            location=path_location_for(resolved),
        )
    if resolved.is_file():
        return (resolved,)
    if resolved.is_dir():
        return tuple(path for path in sorted(resolved.rglob("*")) if path.is_file())
    raise emit_error(
        "E554",
        "Missing tracked source path",
        f"Tracked source path is not a file or directory in target `{target.name}`: `{display_path(resolved)}`.",
        location=path_location_for(resolved),
    )


def _collect_output_entries(
    *,
    compiled: "CompiledSkillPackage",
    emitted_dir: Path,
    emitted_paths: tuple[Path, ...],
) -> tuple[dict[str, str], ...]:
    artifact_kinds = {
        artifact.path: artifact.kind
        for artifact in compiled.contract.artifacts
    }
    output_specs: list[tuple[Path, str, str]] = []
    root_receipt_path = emitted_dir / SOURCE_RECEIPT_FILE_NAME
    for path in emitted_paths:
        if path == root_receipt_path:
            continue
        rel_path = path.relative_to(emitted_dir).as_posix()
        if rel_path == "SKILL.md":
            kind = "skill_package_root"
        elif rel_path == "SKILL.contract.json":
            kind = "host_contract"
        else:
            kind = artifact_kinds.get(rel_path, "file")
        output_specs.append((path, rel_path, kind))
    return _entries_for_paths(output_specs)


def _entries_for_paths(
    path_specs,
) -> tuple[dict[str, str], ...]:
    entries: list[dict[str, str]] = []
    for path, rel_path, kind in sorted(path_specs, key=lambda spec: str(spec[1])):
        entries.append(
            {
                "path": str(rel_path),
                "kind": str(kind),
                "sha256": _sha256_file(path),
            }
        )
    return tuple(entries)


def _tree_hash(entries: tuple[dict[str, str], ...]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["kind"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_posix(path: Path, root: Path) -> str:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return display_path(resolved_path)


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


def _lock_entry_for_receipt(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
    receipt_path: Path,
) -> dict[str, Any]:
    source = receipt_payload.get("source")
    package = receipt_payload.get("package")
    return {
        "receipt_version": receipt_payload["receipt_version"],
        "source_id": source.get("id") if isinstance(source, dict) else "",
        "package": package.get("name") if isinstance(package, dict) else "",
        "entrypoint": _relative_posix(target.entrypoint, target.project_config.config_dir or Path.cwd()),
        "receipt_path": _relative_posix(receipt_path, target.project_config.config_dir or Path.cwd()),
        "source_tree_sha256": receipt_payload["source_tree_sha256"],
        "output_tree_sha256": receipt_payload["output_tree_sha256"],
    }


def _read_lock_entries(lock_file: Path) -> dict[str, dict[str, Any]]:
    if not lock_file.exists():
        return {}
    try:
        raw = tomllib.loads(lock_file.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise emit_error(
            "E557",
            "Invalid skill lock file",
            f"Skill lock file is not valid TOML: `{display_path(lock_file)}`.",
            location=path_location_for(lock_file),
            cause=str(exc),
        ) from exc
    raw_targets = raw.get("target")
    if raw_targets is None:
        return {}
    if not isinstance(raw_targets, dict):
        raise emit_error(
            "E557",
            "Invalid skill lock file",
            f"Skill lock file `target` table must contain target entries: `{display_path(lock_file)}`.",
            location=path_location_for(lock_file),
        )
    entries: dict[str, dict[str, Any]] = {}
    for name, entry in raw_targets.items():
        if isinstance(name, str) and isinstance(entry, dict):
            entries[name] = dict(entry)
    return entries


def _render_skill_lock(entries: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# This file is generated by doctrine.emit_skill.",
        "# Re-run emit_skill when a tracked skill source changes.",
        f"version = {SKILL_LOCK_VERSION}",
        "",
    ]
    for target_name in sorted(entries):
        lines.append(f"[target.{json.dumps(target_name)}]")
        for key in (
            "receipt_version",
            "source_id",
            "package",
            "entrypoint",
            "receipt_path",
            "source_tree_sha256",
            "output_tree_sha256",
        ):
            value = entries[target_name].get(key)
            if isinstance(value, int):
                lines.append(f"{key} = {value}")
            else:
                lines.append(f"{key} = {json.dumps(str(value or ''))}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _verify_lock(
    *,
    target: EmitTarget,
    receipt_payload: dict[str, Any],
) -> SkillReceiptCheckResult | None:
    if target.lock_file is None:
        return None
    if not target.lock_file.is_file():
        return SkillReceiptCheckResult(
            target.name,
            "lock_out_of_date",
            f"Missing configured skill lock file: `{display_path(target.lock_file)}`.",
        )
    entries = _read_lock_entries(target.lock_file)
    lock_entry = entries.get(target.name)
    if lock_entry is None:
        return SkillReceiptCheckResult(
            target.name,
            "lock_out_of_date",
            f"Skill lock file has no entry for target `{target.name}`.",
        )
    expected_entry = _lock_entry_for_receipt(
        target=target,
        receipt_payload=receipt_payload,
        receipt_path=receipt_path_for_target(target),
    )
    for key, expected_value in expected_entry.items():
        if lock_entry.get(key) != expected_value:
            return SkillReceiptCheckResult(
                target.name,
                "receipt_lock_mismatch",
                f"Skill lock entry `{target.name}` is out of date at `{key}`.",
            )
    return None


def path_location_for(path: Path):
    from doctrine._compiler.support import path_location

    return path_location(path)
