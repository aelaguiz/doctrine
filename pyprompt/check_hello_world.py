from __future__ import annotations

import sys
from difflib import unified_diff
from pathlib import Path

from pyprompt.compiler import compile_prompt
from pyprompt.parser import parse_file
from pyprompt.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "examples/01_hello_world/prompts/AGENTS.prompt"
REF_PATH = REPO_ROOT / "examples/01_hello_world/ref/AGENTS.md"
TARGET_AGENT = "HelloWorld"
EXPECTED_AGENT_NAMES = ("HelloWorld", "HelloWorld2")
EXPECTED_RENDERED_LINES = [
    "You are the hello world agent.",
    "",
    "## Instruction",
    "",
    "Say hello world.",
]


def main() -> int:
    try:
        prompt_file = parse_file(PROMPT_PATH)
        _run_parse_smoke_check(prompt_file)

        compiled = compile_prompt(prompt_file, TARGET_AGENT)
        rendered = render_markdown(compiled)
        _run_render_smoke_check(rendered)
        _print_advisory_ref_diff(rendered, REF_PATH.read_text())
    except Exception as exc:  # pragma: no cover - exercised by the command itself
        print(f"hello-world check failed: {exc}", file=sys.stderr)
        return 1

    print("hello-world check passed")
    return 0


def _run_parse_smoke_check(prompt_file) -> None:
    actual_names = tuple(agent.name for agent in prompt_file.agents)
    if actual_names != EXPECTED_AGENT_NAMES:
        raise AssertionError(
            f"Expected fixture agents {EXPECTED_AGENT_NAMES}, got {actual_names}."
        )


def _run_render_smoke_check(rendered: str) -> None:
    actual_lines = rendered.splitlines()
    if actual_lines != EXPECTED_RENDERED_LINES:
        raise AssertionError(
            "Rendered HelloWorld output no longer matches the current prompt-derived smoke contract."
        )


def _print_advisory_ref_diff(rendered: str, ref_text: str) -> None:
    if rendered == ref_text:
        return

    diff = "".join(
        unified_diff(
            ref_text.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile=str(REF_PATH),
            tofile="rendered://HelloWorld",
        )
    )
    print(
        "Advisory diff against approximate ref. This may indicate a renderer bug or a ref bug.",
        file=sys.stderr,
    )
    print(diff, file=sys.stderr, end="" if diff.endswith("\n") else "\n")


if __name__ == "__main__":
    raise SystemExit(main())
