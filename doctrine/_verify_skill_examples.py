from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from doctrine.parser import parse_text

# Fenced ```prompt blocks must parse as standalone Doctrine prompt files so
# readers who copy them into a real `.prompt` can trust the snippet. Blocks
# tagged ```prompt-fragment opt out for partial teaching snippets.
_FENCE_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)```(?P<lang>[A-Za-z0-9_-]+)[ \t]*\n(?P<body>.*?)\n(?P=indent)```[ \t]*(?:\n|$)",
    re.DOTALL | re.MULTILINE,
)

_FRAGMENT_LANG = "prompt-fragment"
_PROMPT_LANG = "prompt"


@dataclass(frozen=True)
class FencedBlock:
    path: Path
    line: int
    lang: str
    body: str


@dataclass(frozen=True)
class SkillExampleFailure:
    block: FencedBlock
    message: str


def iter_markdown_files(skill_roots: Iterable[Path]) -> Iterable[Path]:
    for root in skill_roots:
        if not root.is_dir():
            continue
        yield from sorted(root.rglob("*.md"))


def extract_prompt_blocks(path: Path) -> list[FencedBlock]:
    text = path.read_text()
    blocks: list[FencedBlock] = []
    for match in _FENCE_PATTERN.finditer(text):
        lang = match.group("lang")
        if lang != _PROMPT_LANG:
            continue
        line = text.count("\n", 0, match.start("body")) + 1
        blocks.append(FencedBlock(path=path, line=line, lang=lang, body=match.group("body")))
    return blocks


def run_skill_example_checks(skill_roots: Iterable[Path]) -> list[SkillExampleFailure]:
    failures: list[SkillExampleFailure] = []
    for md_path in iter_markdown_files(skill_roots):
        for block in extract_prompt_blocks(md_path):
            # The indent-aware lexer needs a trailing newline so the last
            # block cleanly dedents back to the file root.
            body = block.body if block.body.endswith("\n") else block.body + "\n"
            try:
                parse_text(body, source_path=md_path)
            except Exception as exc:
                failures.append(
                    SkillExampleFailure(
                        block=block,
                        message=f"{type(exc).__name__}: {exc}",
                    )
                )
    return failures


def default_skill_roots(repo_root: Path) -> tuple[Path, ...]:
    # Only validate canonical source trees. Build output and the public
    # curated tree mirror the source, so duplicating checks would be noise.
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return ()
    roots: list[Path] = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.name.startswith("."):
            continue
        prompts_dir = entry / "prompts"
        if prompts_dir.is_dir():
            roots.append(prompts_dir)
    return tuple(roots)
