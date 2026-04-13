from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PYPROJECT_FILE_NAME = "pyproject.toml"


class ProjectConfigError(ValueError):
    """Raised when Doctrine project configuration is invalid."""


@dataclass(slots=True, frozen=True)
class CompileConfig:
    additional_prompt_roots: tuple[Path, ...] = ()


@dataclass(slots=True, frozen=True)
class ProjectConfig:
    path: Path | None
    raw_compile: object = None
    raw_emit: object = None

    @property
    def config_dir(self) -> Path | None:
        if self.path is None:
            return None
        return self.path.parent

    def resolve_compile_config(self) -> CompileConfig:
        if self.path is None:
            return CompileConfig()

        if self.raw_compile is None:
            return CompileConfig()
        if not isinstance(self.raw_compile, dict):
            raise ProjectConfigError("Doctrine compile config must be a TOML table.")

        raw_roots = self.raw_compile.get("additional_prompt_roots", [])
        if raw_roots is None:
            return CompileConfig()
        if not isinstance(raw_roots, list):
            raise ProjectConfigError(
                "Doctrine compile config additional_prompt_roots must be an array of strings."
            )

        config_dir = self.config_dir
        assert config_dir is not None

        additional_prompt_roots: list[Path] = []
        seen_roots: set[Path] = set()
        for index, raw_root in enumerate(raw_roots, start=1):
            if not isinstance(raw_root, str):
                raise ProjectConfigError(
                    "Doctrine compile config additional_prompt_roots must be an array of strings."
                )

            resolved_root = resolve_config_path(config_dir, raw_root)
            if resolved_root.name != "prompts" or not resolved_root.is_dir():
                raise ProjectConfigError(
                    f"Configured additional prompts root must be an existing prompts directory: {resolved_root}"
                )
            if resolved_root in seen_roots:
                raise ProjectConfigError(
                    f"Duplicate configured prompts root: {resolved_root}"
                )

            seen_roots.add(resolved_root)
            additional_prompt_roots.append(resolved_root)

        return CompileConfig(additional_prompt_roots=tuple(additional_prompt_roots))


EMPTY_PROJECT_CONFIG = ProjectConfig(path=None)


def find_nearest_pyproject(start_dir: str | Path | None = None) -> Path | None:
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()
    for candidate_dir in [base_dir, *base_dir.parents]:
        candidate = candidate_dir / PYPROJECT_FILE_NAME
        if candidate.is_file():
            return candidate.resolve()
    return None


def load_project_config(pyproject_path: str | Path) -> ProjectConfig:
    config_path = Path(pyproject_path).resolve()
    raw = tomllib.loads(config_path.read_text())
    doctrine_table = _table_get(raw, "tool", "doctrine")
    return ProjectConfig(
        path=config_path,
        raw_compile=_value_get(doctrine_table, "compile"),
        raw_emit=_value_get(doctrine_table, "emit"),
    )


def load_project_config_for_source(source_path: Path | None) -> ProjectConfig:
    if source_path is None:
        return EMPTY_PROJECT_CONFIG

    resolved_source = source_path.resolve()
    start_dir = resolved_source if resolved_source.is_dir() else resolved_source.parent
    config_path = find_nearest_pyproject(start_dir)
    if config_path is None:
        return EMPTY_PROJECT_CONFIG
    return load_project_config(config_path)


def resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def _table_get(raw: dict[str, Any], *keys: str) -> dict[str, object] | None:
    current: object = raw
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    if not isinstance(current, dict):
        return None
    return current


def _value_get(table: dict[str, object] | None, key: str) -> object | None:
    if table is None:
        return None
    return table.get(key)
