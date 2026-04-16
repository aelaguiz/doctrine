from __future__ import annotations

import tomllib
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any


PYPROJECT_FILE_NAME = "pyproject.toml"


class ProjectConfigError(ValueError):
    """Raised when Doctrine project configuration is invalid."""


@dataclass(slots=True, frozen=True)
class ProvidedPromptRoot:
    name: str
    path: str | PathLike[str]


@dataclass(slots=True, frozen=True)
class CompileConfig:
    additional_prompt_roots: tuple[Path, ...] = ()
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = ()


@dataclass(slots=True, frozen=True)
class ProjectConfig:
    path: Path | None
    raw_compile: object = None
    raw_emit: object = None
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provided_prompt_roots",
            tuple(self.provided_prompt_roots),
        )

    @property
    def config_dir(self) -> Path | None:
        if self.path is None:
            return None
        return self.path.parent

    def resolve_compile_config(self) -> CompileConfig:
        provided_prompt_roots = resolve_provided_prompt_roots(
            self.provided_prompt_roots
        )
        if self.path is None:
            return CompileConfig(provided_prompt_roots=provided_prompt_roots)

        if self.raw_compile is None:
            return CompileConfig(provided_prompt_roots=provided_prompt_roots)
        if not isinstance(self.raw_compile, dict):
            raise ProjectConfigError("Doctrine compile config must be a TOML table.")

        raw_roots = self.raw_compile.get("additional_prompt_roots", [])
        if raw_roots is None:
            return CompileConfig(provided_prompt_roots=provided_prompt_roots)
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
            _validate_prompt_root_dir(
                resolved_root,
                label="Configured additional prompts root",
            )
            if resolved_root in seen_roots:
                raise ProjectConfigError(
                    f"Duplicate configured prompts root: {resolved_root}"
                )

            seen_roots.add(resolved_root)
            additional_prompt_roots.append(resolved_root)

        return CompileConfig(
            additional_prompt_roots=tuple(additional_prompt_roots),
            provided_prompt_roots=provided_prompt_roots,
        )

    def with_provided_prompt_roots(
        self,
        provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
    ) -> "ProjectConfig":
        return ProjectConfig(
            path=self.path,
            raw_compile=self.raw_compile,
            raw_emit=self.raw_emit,
            provided_prompt_roots=(
                *self.provided_prompt_roots,
                *tuple(provided_prompt_roots),
            ),
        )


EMPTY_PROJECT_CONFIG = ProjectConfig(path=None)


def find_nearest_pyproject(start_dir: str | Path | None = None) -> Path | None:
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()
    for candidate_dir in [base_dir, *base_dir.parents]:
        candidate = candidate_dir / PYPROJECT_FILE_NAME
        if candidate.is_file():
            return candidate.resolve()
    return None


def load_project_config(
    pyproject_path: str | Path,
    *,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> ProjectConfig:
    config_path = Path(pyproject_path).resolve()
    raw = tomllib.loads(config_path.read_text())
    doctrine_table = _table_get(raw, "tool", "doctrine")
    return ProjectConfig(
        path=config_path,
        raw_compile=_value_get(doctrine_table, "compile"),
        raw_emit=_value_get(doctrine_table, "emit"),
        provided_prompt_roots=provided_prompt_roots,
    )


def load_project_config_for_source(
    source_path: Path | None,
    *,
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...] = (),
) -> ProjectConfig:
    if source_path is None:
        if provided_prompt_roots:
            return ProjectConfig(path=None, provided_prompt_roots=provided_prompt_roots)
        return EMPTY_PROJECT_CONFIG

    resolved_source = source_path.resolve()
    start_dir = resolved_source if resolved_source.is_dir() else resolved_source.parent
    config_path = find_nearest_pyproject(start_dir)
    if config_path is None:
        if provided_prompt_roots:
            return ProjectConfig(path=None, provided_prompt_roots=provided_prompt_roots)
        return EMPTY_PROJECT_CONFIG
    return load_project_config(
        config_path,
        provided_prompt_roots=provided_prompt_roots,
    )


def resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def resolve_provided_prompt_roots(
    provided_prompt_roots: tuple[ProvidedPromptRoot, ...],
) -> tuple[ProvidedPromptRoot, ...]:
    resolved_roots: list[ProvidedPromptRoot] = []
    seen_names: set[str] = set()
    seen_paths: dict[Path, str] = {}
    for index, provided_root in enumerate(provided_prompt_roots, start=1):
        if not isinstance(provided_root, ProvidedPromptRoot):
            raise ProjectConfigError(
                "Provided prompt roots must be ProvidedPromptRoot values."
            )

        name = provided_root.name
        if not isinstance(name, str) or not name.strip():
            raise ProjectConfigError(
                f"Provided prompt root #{index} name must be a non-empty string."
            )
        name = name.strip()
        if ":" in name:
            raise ProjectConfigError(
                f"Provided prompt root `{name}` name must not contain `:`."
            )
        if name in seen_names:
            raise ProjectConfigError(f"Duplicate provided prompt root name: {name}")

        try:
            resolved_path = Path(provided_root.path).resolve()
        except TypeError as exc:
            raise ProjectConfigError(
                f"Provided prompt root `{name}` path must be a string or path-like value."
            ) from exc

        # Provider roots are caller-owned inputs, not host TOML. Resolve the
        # path as supplied, then feed it into the same prompt-root validation.
        _validate_prompt_root_dir(
            resolved_path,
            label=f"Provided prompt root `{name}`",
        )
        prior_name = seen_paths.get(resolved_path)
        if prior_name is not None:
            raise ProjectConfigError(
                "Duplicate provided prompts root "
                f"`{name}` matches `{prior_name}`: {resolved_path}"
            )

        seen_names.add(name)
        seen_paths[resolved_path] = name
        resolved_roots.append(ProvidedPromptRoot(name=name, path=resolved_path))
    return tuple(resolved_roots)


def _validate_prompt_root_dir(path: Path, *, label: str) -> None:
    if path.name != "prompts" or not path.is_dir():
        raise ProjectConfigError(
            f"{label} must be an existing prompts directory: {path}"
        )


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
