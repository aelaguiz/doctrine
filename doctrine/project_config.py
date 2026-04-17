from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field as _field
from os import PathLike
from pathlib import Path
from typing import Any


PYPROJECT_FILE_NAME = "pyproject.toml"


class ProjectConfigError(ValueError):
    """Raised when Doctrine project configuration is invalid."""

    def __init__(
        self,
        message: str,
        *,
        path: Path | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        self.path = path.resolve() if path is not None else None
        self.line = line
        self.column = column
        super().__init__(message)


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
    raw_text: str | None = _field(default=None, compare=False, repr=False)

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
            raise self._compile_config_error(
                "Doctrine compile config must be a TOML table.",
                key="compile",
            )

        raw_roots = self.raw_compile.get("additional_prompt_roots", [])
        if raw_roots is None:
            return CompileConfig(provided_prompt_roots=provided_prompt_roots)
        if not isinstance(raw_roots, list):
            raise self._compile_config_error(
                "Doctrine compile config additional_prompt_roots must be an array of strings.",
                key="additional_prompt_roots",
            )

        config_dir = self.config_dir
        assert config_dir is not None

        additional_prompt_roots: list[Path] = []
        seen_roots: set[Path] = set()
        for index, raw_root in enumerate(raw_roots, start=1):
            if not isinstance(raw_root, str):
                raise self._compile_config_error(
                    "Doctrine compile config additional_prompt_roots must be an array of strings.",
                    key="additional_prompt_roots",
                    item_index=index,
                )

            resolved_root = resolve_config_path(config_dir, raw_root)
            _validate_prompt_root_dir(
                resolved_root,
                label="Configured additional prompts root",
                error_path=self.path,
                line=self._compile_config_line("additional_prompt_roots", item_index=index),
                column=self._compile_config_column("additional_prompt_roots", item_index=index),
            )
            if resolved_root in seen_roots:
                raise self._compile_config_error(
                    f"Duplicate configured prompts root: {resolved_root}",
                    key="additional_prompt_roots",
                    item_index=index,
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
            raw_text=self.raw_text,
        )

    def _compile_config_error(
        self,
        message: str,
        *,
        key: str,
        item_index: int | None = None,
    ) -> ProjectConfigError:
        line, column = _locate_compile_config_site(
            self.raw_text,
            key=key,
            item_index=item_index,
        )
        return ProjectConfigError(
            message,
            path=self.path,
            line=line,
            column=column,
        )

    def _compile_config_line(
        self,
        key: str,
        *,
        item_index: int | None = None,
    ) -> int | None:
        line, _column = _locate_compile_config_site(
            self.raw_text,
            key=key,
            item_index=item_index,
        )
        return line

    def _compile_config_column(
        self,
        key: str,
        *,
        item_index: int | None = None,
    ) -> int | None:
        _line, column = _locate_compile_config_site(
            self.raw_text,
            key=key,
            item_index=item_index,
        )
        return column


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
    raw_text = config_path.read_text(encoding="utf-8")
    raw = tomllib.loads(raw_text)
    doctrine_table = _table_get(raw, "tool", "doctrine")
    return ProjectConfig(
        path=config_path,
        raw_compile=_value_get(doctrine_table, "compile"),
        raw_emit=_value_get(doctrine_table, "emit"),
        provided_prompt_roots=provided_prompt_roots,
        raw_text=raw_text,
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
def _validate_prompt_root_dir(
    path: Path,
    *,
    label: str,
    error_path: Path | None = None,
    line: int | None = None,
    column: int | None = None,
) -> None:
    if path.name != "prompts" or not path.is_dir():
        raise ProjectConfigError(
            f"{label} must be an existing prompts directory: {path}",
            path=error_path,
            line=line,
            column=column,
        )


def _locate_compile_config_site(
    source: str | None,
    *,
    key: str,
    item_index: int | None = None,
) -> tuple[int | None, int | None]:
    if source is None:
        return None, None
    if item_index is not None:
        line, column = _locate_toml_array_item(source, key=key, item_index=item_index)
        if line is not None and column is not None:
            return line, column
    return _locate_toml_key_assignment(source, key=key)


def _locate_toml_key_assignment(
    source: str,
    *,
    key: str,
) -> tuple[int | None, int | None]:
    match = re.search(rf"(?m)^(?P<indent>\s*)(?P<key>{re.escape(key)})\s*=", source)
    if match is None:
        return None, None
    return _offset_to_line_column(source, match.start("key"))


def _locate_toml_array_item(
    source: str,
    *,
    key: str,
    item_index: int,
) -> tuple[int | None, int | None]:
    match = re.search(rf"(?m)^(?P<indent>\s*)(?P<key>{re.escape(key)})\s*=", source)
    if match is None:
        return None, None
    position = match.end()
    while position < len(source) and source[position].isspace():
        position += 1
    if position >= len(source) or source[position] != "[":
        return _offset_to_line_column(source, match.start("key"))

    position += 1
    depth = 1
    current_item_start: int | None = None
    current_index = 0
    quote_char: str | None = None
    while position < len(source):
        char = source[position]
        if quote_char is not None:
            if quote_char == '"' and char == "\\":
                position += 2
                continue
            if char == quote_char:
                quote_char = None
            position += 1
            continue

        if char in ('"', "'"):
            if current_item_start is None:
                current_item_start = position
            quote_char = char
            position += 1
            continue
        if char in " \t\r\n":
            position += 1
            continue
        if char == "," and depth == 1:
            if current_item_start is not None:
                current_index += 1
                if current_index == item_index:
                    return _offset_to_line_column(source, current_item_start)
                current_item_start = None
            position += 1
            continue
        if char in "[{":
            if current_item_start is None:
                current_item_start = position
            depth += 1
            position += 1
            continue
        if char in "]}":
            if depth == 1 and current_item_start is not None:
                current_index += 1
                if current_index == item_index:
                    return _offset_to_line_column(source, current_item_start)
            if depth == 1:
                break
            depth -= 1
            position += 1
            continue
        if current_item_start is None:
            current_item_start = position
        position += 1
    return _offset_to_line_column(source, match.start("key"))


def _offset_to_line_column(source: str, offset: int) -> tuple[int, int]:
    line = source.count("\n", 0, offset) + 1
    last_newline = source.rfind("\n", 0, offset)
    if last_newline == -1:
        return line, offset + 1
    return line, offset - last_newline


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
