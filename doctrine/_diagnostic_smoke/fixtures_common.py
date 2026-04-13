from __future__ import annotations

import textwrap
from pathlib import Path


class SmokeFailure(RuntimeError):
    """Raised when the direct diagnostic smoke checks fail."""


def _write_prompt(tmp_dir: str, source: str) -> Path:
    root = Path(tmp_dir)
    prompts = root / "prompts"
    prompts.mkdir()
    prompt_path = prompts / "AGENTS.prompt"
    prompt_path.write_text(source)
    return prompt_path


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    normalized = textwrap.dedent(text).strip("\n")
    return "\n".join(f"{prefix}{line}" if line else "" for line in normalized.splitlines())


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)

