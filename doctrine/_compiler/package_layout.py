from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterable

from doctrine.diagnostics import CompileError


@dataclass(slots=True, frozen=True)
class BundledPackageFile:
    path: str
    content: bytes


@dataclass(slots=True)
class PackageOutputRegistry:
    owner_label: str
    path_label_singular: str = "Bundled path"
    path_label_plural: str = "Bundled paths"
    read_label: str = "bundled file"
    seen_exact: set[str] = field(default_factory=set)
    seen_folded: dict[str, str] = field(default_factory=dict)


def new_package_output_registry(
    *,
    owner_label: str,
    compiler_owned_paths: tuple[str, ...] = (),
    path_label_singular: str = "Bundled path",
    path_label_plural: str = "Bundled paths",
    read_label: str = "bundled file",
) -> PackageOutputRegistry:
    registry = PackageOutputRegistry(
        owner_label=owner_label,
        path_label_singular=path_label_singular,
        path_label_plural=path_label_plural,
        read_label=read_label,
    )
    for path_text in compiler_owned_paths:
        register_package_output_path(path_text, registry=registry)
    return registry


def register_package_output_path(
    path_text: str,
    *,
    registry: PackageOutputRegistry,
) -> str:
    if "\\" in path_text:
        raise CompileError(
            f"{registry.path_label_plural} must use `/` separators in {registry.owner_label}: {path_text}"
        )
    path = PurePosixPath(path_text)
    parts = path.parts
    if not parts:
        raise CompileError(
            f"{registry.path_label_singular} is empty in {registry.owner_label}"
        )
    if path.is_absolute():
        raise CompileError(
            f"{registry.path_label_plural} must be relative in {registry.owner_label}: {path_text}"
        )
    if any(part in {"", ".", ".."} for part in parts):
        raise CompileError(
            f"{registry.path_label_singular} must stay within the package root in "
            f"{registry.owner_label}: {path_text}"
        )
    if path.name in {"", ".", ".."}:
        raise CompileError(
            f"{registry.path_label_singular} must name a file in "
            f"{registry.owner_label}: {path_text}"
        )
    normalized = path.as_posix()
    if normalized in registry.seen_exact:
        raise CompileError(
            f"Duplicate {registry.path_label_singular.lower()} in {registry.owner_label}: {normalized}"
        )
    folded = normalized.casefold()
    prior = registry.seen_folded.get(folded)
    if prior is not None:
        raise CompileError(
            f"{registry.path_label_singular} case-collides in {registry.owner_label}: {normalized} vs {prior}"
        )
    registry.seen_exact.add(normalized)
    registry.seen_folded[folded] = normalized
    return normalized


def bundle_ordinary_package_files(
    source_root: Path,
    source_files: Iterable[Path],
    *,
    registry: PackageOutputRegistry,
) -> tuple[BundledPackageFile, ...]:
    # Keep prompt policy in the caller. This helper only owns normalized output
    # paths, collision checks, and byte-for-byte ordinary file bundling.
    bundled_files: list[BundledPackageFile] = []
    for source_path in sorted(source_files):
        rel_path = source_path.relative_to(source_root).as_posix()
        normalized_path = register_package_output_path(rel_path, registry=registry)
        try:
            content = source_path.read_bytes()
        except OSError as exc:
            raise CompileError(
                f"Could not read {registry.read_label} in {registry.owner_label}: {normalized_path}"
            ).ensure_location(path=source_path) from exc
        bundled_files.append(
            BundledPackageFile(path=normalized_path, content=content)
        )
    return tuple(bundled_files)
