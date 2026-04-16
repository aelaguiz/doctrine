from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterable

from doctrine._compiler.package_diagnostics import (
    package_compile_error,
    package_related_path,
)
from doctrine._diagnostics.contracts import DiagnosticRelatedLocation


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
    source_paths: dict[str, Path | None] = field(default_factory=dict)


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
    source_path: Path | None = None,
) -> str:
    if "\\" in path_text:
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"{registry.path_label_plural} must use `/` separators in "
                f"{registry.owner_label}: {path_text}"
            ),
            path=source_path,
            hints=("Use relative package paths with `/` separators.",),
        )
    path = PurePosixPath(path_text)
    parts = path.parts
    if not parts:
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=f"{registry.path_label_singular} is empty in {registry.owner_label}",
            path=source_path,
            hints=("Bundle files under a real relative file path.",),
        )
    if path.is_absolute():
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"{registry.path_label_plural} must be relative in "
                f"{registry.owner_label}: {path_text}"
            ),
            path=source_path,
            hints=("Keep bundled files inside the package root.",),
        )
    if any(part in {"", ".", ".."} for part in parts):
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"{registry.path_label_singular} must stay within the package root in "
                f"{registry.owner_label}: {path_text}"
            ),
            path=source_path,
            hints=("Keep bundled files under the package root.",),
        )
    if path.name in {"", ".", ".."}:
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"{registry.path_label_singular} must name a file in "
                f"{registry.owner_label}: {path_text}"
            ),
            path=source_path,
            hints=("Point each bundled path at one file, not a directory.",),
        )
    normalized = path.as_posix()
    if normalized in registry.seen_exact:
        prior_path = registry.source_paths.get(normalized)
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"Duplicate {registry.path_label_singular.lower()} in "
                f"{registry.owner_label}: {normalized}"
            ),
            path=source_path,
            related=_package_collision_related(
                prior_path=prior_path,
                source_path=source_path,
            ),
            hints=("Each bundled output path must be unique inside the package.",),
        )
    folded = normalized.casefold()
    prior = registry.seen_folded.get(folded)
    if prior is not None:
        raise package_compile_error(
            code="E304",
            summary="Invalid skill package bundle",
            detail=(
                f"{registry.path_label_singular} case-collides in "
                f"{registry.owner_label}: {normalized} vs {prior}"
            ),
            path=source_path,
            related=_package_collision_related(
                prior_path=registry.source_paths.get(prior),
                source_path=source_path,
            ),
            hints=("Bundle paths must stay unique even on case-folding filesystems.",),
        )
    registry.seen_exact.add(normalized)
    registry.seen_folded[folded] = normalized
    registry.source_paths[normalized] = source_path.resolve() if source_path is not None else None
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
        normalized_path = register_package_output_path(
            rel_path,
            registry=registry,
            source_path=source_path,
        )
        try:
            content = source_path.read_bytes()
        except OSError as exc:
            raise package_compile_error(
                code="E304",
                summary="Invalid skill package bundle",
                detail=(
                    f"Could not read {registry.read_label} in "
                    f"{registry.owner_label}: {normalized_path}"
                ),
                path=source_path,
                hints=("Keep bundled files readable during skill-package compilation.",),
            ) from exc
        bundled_files.append(
            BundledPackageFile(path=normalized_path, content=content)
        )
    return tuple(bundled_files)


def _package_collision_related(
    *,
    prior_path: Path | None,
    source_path: Path | None,
) -> tuple[DiagnosticRelatedLocation, ...]:
    if prior_path is None or prior_path == source_path:
        return ()
    return (package_related_path(label="first bundled source", path=prior_path),)
