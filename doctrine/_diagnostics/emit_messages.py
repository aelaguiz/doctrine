from __future__ import annotations

import re
from typing import Callable

from doctrine._diagnostics.contracts import DoctrineDiagnostic

_EMIT_PATTERN_BUILDERS: tuple[
    tuple[re.Pattern[str], str, str, Callable[[re.Match[str]], str | None], tuple[str, ...]],
    ...,
] = (
    (
        re.compile(r"^Unknown emit target: (?P<target>.+)$"),
        "E501",
        "Unknown emit target",
        lambda match: f"Emit target `{match.group('target')}` is not defined in `pyproject.toml`.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) has no concrete agents in (?P<path>.+)$"),
        "E502",
        "Emit target has no concrete agents",
        lambda match: f"Emit target `{match.group('target')}` points at `{match.group('path')}`, which has no concrete agents.",
        (),
    ),
    (
        re.compile(r"^pyproject\.toml does not define any \[tool\.doctrine\.emit\.targets\]\.$"),
        "E503",
        "Missing emit targets",
        lambda _match: "The current `pyproject.toml` does not define any emit targets.",
        (),
    ),
    (
        re.compile(r"^Could not find pyproject\.toml in (?P<detail>.+)\.$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Could not find `pyproject.toml` in {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) maps both (?P<a>.+) and (?P<b>.+) to (?P<path>.+)$"),
        "E505",
        "Emit target path collision",
        lambda match: (
            f"Emit target `{match.group('target')}` maps `{match.group('a')}` and `{match.group('b')}` to the same path `{match.group('path')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Emit config must point at pyproject\.toml: (?P<path>.+)$"),
        "E507",
        "Emit config path must point at pyproject.toml",
        lambda match: f"Emit config path must point at `pyproject.toml`, got `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Missing pyproject\.toml: (?P<path>.+)$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Missing `pyproject.toml`: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Emit target #(?P<index>.+) must be a TOML table\.$"),
        "E508",
        "Emit target must be a TOML table",
        lambda match: f"Emit target #{match.group('index')} must be a TOML table.",
        (),
    ),
    (
        re.compile(r"^Duplicate emit target name: (?P<name>.+)$"),
        "E509",
        "Duplicate emit target name",
        lambda match: f"Emit target `{match.group('name')}` is defined more than once.",
        (),
    ),
    (
        re.compile(
            r"^Emit target (?P<name>.+) must point at an AGENTS\.prompt or SOUL\.prompt entrypoint, got (?P<entrypoint>.+)$"
        ),
        "E510",
        "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
        lambda match: (
            f"Emit target `{match.group('name')}` must point at an `AGENTS.prompt` or `SOUL.prompt` entrypoint, got `{match.group('entrypoint')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Emit target (?P<name>.+) output_dir is a file: (?P<path>.+)$"),
        "E511",
        "Emit target output_dir is a file",
        lambda match: f"Emit target `{match.group('name')}` output_dir is a file: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+) does not exist: (?P<value>.+)$"),
        "E512",
        "Emit config path does not exist",
        lambda match: f"{match.group('label')} does not exist: {match.group('value')}",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+)\.(?P<key>.+) must be a string\.$"),
        "E513",
        "Emit config value must be a string",
        lambda match: f"{match.group('label')}.{match.group('key')} must be a string.",
        (),
    ),
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)$"),
        "E514",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(
            r"^Use either configured target mode \(`--target`\) or direct mode \(`--entrypoint` with `--output-dir`\), not both\.$"
        ),
        "E517",
        "Emit flow CLI requires exactly one resolution mode",
        lambda _match: (
            "Use either configured target mode (`--target`) or direct mode "
            "(`--entrypoint` with `--output-dir`), not both."
        ),
        (),
    ),
    (
        re.compile(
            r"^Use configured target mode \(`--target`\) or direct mode \(`--entrypoint` with `--output-dir`\)\.$"
        ),
        "E517",
        "Emit flow CLI requires exactly one resolution mode",
        lambda _match: (
            "Use configured target mode (`--target`) or direct mode "
            "(`--entrypoint` with `--output-dir`)."
        ),
        (),
    ),
    (
        re.compile(r"^Direct `emit_flow` mode requires both `--entrypoint` and `--output-dir`\.$"),
        "E518",
        "Direct emit flow mode requires entrypoint and output_dir",
        lambda _match: "Direct `emit_flow` mode requires both `--entrypoint` and `--output-dir`.",
        (),
    ),
    (
        re.compile(
            r"^(?P<label>.+) resolves outside the target project root: (?P<path>.+) is not under (?P<root>.+)\.$"
        ),
        "E520",
        "Emit target output_dir must stay within project root",
        lambda match: (
            f"{match.group('label')} resolves outside the target project root: "
            f"`{match.group('path')}` is not under `{match.group('root')}`."
        ),
        (),
    ),
)


def _emit_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    for pattern, code, summary, detail_builder, hints in _EMIT_PATTERN_BUILDERS:
        match = pattern.match(message)
        if match is None:
            continue
        return DoctrineDiagnostic(
            code=code,
            stage="emit",
            summary=summary,
            detail=detail_builder(match),
            hints=hints,
            cause=message if message != detail_builder(match) else None,
        )
    return DoctrineDiagnostic(
        code="E599",
        stage="emit",
        summary="Emit failure",
        detail=message,
    )
