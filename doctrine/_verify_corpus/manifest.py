from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


class ManifestError(RuntimeError):
    """Raised when a case manifest is structurally invalid."""


@dataclass(slots=True, frozen=True)
class CaseSpec:
    manifest_path: Path
    example_dir: Path
    name: str
    kind: str
    prompt_path: Path
    approx_ref_path: Path | None
    agent: str | None = None
    build_target: str | None = None
    declaration_kind: str | None = None
    declaration_name: str | None = None
    assertion: str | None = None
    expected_lines: tuple[str, ...] = ()
    exception_type: str | None = None
    error_code: str | None = None
    message_contains: tuple[str, ...] = ()


def _resolve_manifest_paths(manifest_args: list[str] | None) -> tuple[Path, ...]:
    if manifest_args:
        resolved = tuple(_resolve_repo_path(manifest) for manifest in manifest_args)
    else:
        resolved = tuple(sorted((REPO_ROOT / "examples").glob("*/cases.toml")))

    if not resolved:
        raise ManifestError("No manifest files were found.")

    missing = [path for path in resolved if not path.is_file()]
    if missing:
        formatted = ", ".join(_display_path(path) for path in missing)
        raise ManifestError(f"Missing manifest file(s): {formatted}")

    return resolved


def _resolve_repo_path(path_str: str) -> Path:
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate.resolve()


def _load_manifest(path: Path) -> tuple[CaseSpec, ...]:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"Invalid TOML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestError("Manifest root must be a TOML table.")

    schema_version = raw.get("schema_version")
    if schema_version != 1:
        raise ManifestError(f"Expected schema_version = 1, got {schema_version!r}.")

    example_dir = path.parent.resolve()
    default_prompt_rel = _require_str(raw, "default_prompt")
    default_prompt_path = _resolve_example_path(
        example_dir, default_prompt_rel, label="default_prompt"
    )

    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ManifestError("Manifest must define at least one [[cases]] entry.")

    seen_names: set[str] = set()
    cases: list[CaseSpec] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ManifestError(f"cases[{index}] must be a TOML table.")
        case = _load_case(
            manifest_path=path.resolve(),
            example_dir=example_dir,
            default_prompt_path=default_prompt_path,
            default_prompt_rel=default_prompt_rel,
            raw_case=raw_case,
            case_index=index,
        )
        if case.name in seen_names:
            raise ManifestError(f"Duplicate case name {case.name!r} in {path.name}.")
        seen_names.add(case.name)
        cases.append(case)

    return tuple(cases)


def _load_case(
    *,
    manifest_path: Path,
    example_dir: Path,
    default_prompt_path: Path,
    default_prompt_rel: str,
    raw_case: dict[str, Any],
    case_index: int,
) -> CaseSpec:
    name = _require_str(raw_case, "name", case_index=case_index)
    _require_choice(raw_case, "status", {"active"}, case_index=case_index)
    kind = _require_choice(
        raw_case,
        "kind",
        {
            "render_contract",
            "render_declaration",
            "build_contract",
            "parse_fail",
            "compile_fail",
        },
        case_index=case_index,
    )

    prompt_rel = raw_case.get("prompt", default_prompt_rel)
    if not isinstance(prompt_rel, str):
        raise ManifestError(f"cases[{case_index}].prompt must be a string when provided.")
    prompt_path = (
        default_prompt_path
        if prompt_rel == default_prompt_rel
        else _resolve_example_path(example_dir, prompt_rel, label=f"cases[{case_index}].prompt")
    )

    approx_ref_rel = raw_case.get("approx_ref")
    approx_ref_path: Path | None = None
    if approx_ref_rel is not None:
        if not isinstance(approx_ref_rel, str):
            raise ManifestError(
                f"cases[{case_index}].approx_ref must be a string when provided."
            )
        approx_ref_path = _resolve_example_path(
            example_dir, approx_ref_rel, label=f"cases[{case_index}].approx_ref"
        )

    if kind == "render_contract":
        agent = _require_str(raw_case, "agent", case_index=case_index)
        assertion = _require_choice(
            raw_case, "assertion", {"exact_lines"}, case_index=case_index
        )
        expected_lines = _require_string_list(
            raw_case, "expected_lines", case_index=case_index
        )
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            agent=agent,
            assertion=assertion,
            expected_lines=expected_lines,
        )

    if kind == "render_declaration":
        declaration_kind = _require_choice(
            raw_case,
            "declaration_kind",
            {"analysis", "schema", "document"},
            case_index=case_index,
        )
        declaration_name = _require_str(raw_case, "declaration_name", case_index=case_index)
        assertion = _require_choice(
            raw_case, "assertion", {"exact_lines"}, case_index=case_index
        )
        expected_lines = _require_string_list(
            raw_case, "expected_lines", case_index=case_index
        )
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            declaration_kind=declaration_kind,
            declaration_name=declaration_name,
            assertion=assertion,
            expected_lines=expected_lines,
        )

    if kind == "build_contract":
        build_target = _require_str(raw_case, "build_target", case_index=case_index)
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            build_target=build_target,
        )

    exception_type = _require_str(raw_case, "exception_type", case_index=case_index)
    error_code = raw_case.get("error_code")
    if error_code is not None and not isinstance(error_code, str):
        raise ManifestError(f"cases[{case_index}].error_code must be a string when provided.")
    message_contains = _require_string_list(
        raw_case, "message_contains", case_index=case_index
    )

    agent = raw_case.get("agent")
    if agent is not None and not isinstance(agent, str):
        raise ManifestError(f"cases[{case_index}].agent must be a string when provided.")

    return CaseSpec(
        manifest_path=manifest_path,
        example_dir=example_dir,
        name=name,
        kind=kind,
        prompt_path=prompt_path,
        approx_ref_path=approx_ref_path,
        agent=agent,
        exception_type=exception_type,
        error_code=error_code,
        message_contains=message_contains,
    )


def _resolve_example_path(example_dir: Path, rel_path: str, *, label: str) -> Path:
    resolved = (example_dir / rel_path).resolve()
    try:
        resolved.relative_to(example_dir)
    except ValueError as exc:
        raise ManifestError(
            f"{label} escapes the owning example directory: {rel_path!r}."
        ) from exc

    if not resolved.is_file():
        raise ManifestError(f"{label} does not exist: {rel_path!r}.")

    return resolved


def _require_str(raw: dict[str, Any], key: str, *, case_index: int | None = None) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        location = key if case_index is None else f"cases[{case_index}].{key}"
        raise ManifestError(f"{location} must be a string.")
    return value


def _require_choice(
    raw: dict[str, Any],
    key: str,
    allowed: set[str],
    *,
    case_index: int | None = None,
) -> str:
    value = _require_str(raw, key, case_index=case_index)
    if value not in allowed:
        location = key if case_index is None else f"cases[{case_index}].{key}"
        allowed_str = ", ".join(sorted(repr(item) for item in allowed))
        raise ManifestError(f"{location} must be one of {allowed_str}, got {value!r}.")
    return value


def _require_string_list(
    raw: dict[str, Any], key: str, *, case_index: int | None = None
) -> tuple[str, ...]:
    value = raw.get(key)
    location = key if case_index is None else f"cases[{case_index}].{key}"
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(f"{location} must be a list of strings.")
    return tuple(value)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
