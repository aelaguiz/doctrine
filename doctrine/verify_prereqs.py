from __future__ import annotations

import argparse
import sys

from doctrine.flow_renderer import FlowRenderDependencyError, ensure_pinned_d2_dependency


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    try:
        if args.require_flow_renderer:
            ensure_pinned_d2_dependency()
        return 0
    except FlowRenderDependencyError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check repo prerequisites needed by the shipped verification targets."
    )
    parser.add_argument(
        "--require-flow-renderer",
        action="store_true",
        help="Require the pinned D2 package used by flow rendering.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
