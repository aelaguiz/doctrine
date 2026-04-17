from __future__ import annotations

import argparse
from pathlib import Path

from doctrine._verify_skill_examples import (
    default_skill_roots,
    run_skill_example_checks,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    roots = (
        tuple(Path(root).resolve() for root in args.root)
        if args.root
        else default_skill_roots(REPO_ROOT)
    )
    if not roots:
        print("No skill prompt trees found.")
        return 0

    failures = run_skill_example_checks(roots)
    for failure in failures:
        block = failure.block
        try:
            display_path = block.path.relative_to(REPO_ROOT)
        except ValueError:
            display_path = block.path
        print(f"FAIL {display_path}:{block.line} ({block.lang}): {failure.message}")

    total_blocks = sum(1 for root in roots for path in root.rglob("*.md")
                       for _ in _iter_prompt_blocks_in_file(path))

    if failures:
        print(f"\n{len(failures)} of {total_blocks} prompt block(s) failed to parse.")
        return 1

    print(f"All {total_blocks} prompt block(s) parsed cleanly.")
    return 0


def _iter_prompt_blocks_in_file(path):
    from doctrine._verify_skill_examples import extract_prompt_blocks

    yield from extract_prompt_blocks(path)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse every fenced ```prompt block inside skill-bundled Markdown.",
    )
    parser.add_argument(
        "--root",
        action="append",
        help=(
            "Path to a skill prompts directory to verify. "
            "Repeat to check multiple roots. Defaults to skills/*/prompts."
        ),
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
