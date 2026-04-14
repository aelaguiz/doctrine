from __future__ import annotations

import argparse
import sys

from doctrine.diagnostics import DoctrineError
from doctrine._release_flow.ops import (
    draft_release,
    prepare_release,
    publish_release,
    render_release_worksheet,
    tag_release,
)
from doctrine._release_flow.parsing import repo_root

__all__ = [
    "draft_release",
    "prepare_release",
    "publish_release",
    "render_release_worksheet",
    "tag_release",
]


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        root = repo_root()
        if args.command == "prepare":
            plan = prepare_release(
                repo_root=root,
                release=args.release,
                release_class=args.release_class,
                language_version=args.language_version,
                channel=args.channel,
            )
            print(render_release_worksheet(plan))
            return 0

        if args.command == "tag":
            tag_release(repo_root=root, release=args.release, channel=args.channel)
            return 0

        if args.command == "draft":
            draft_release(
                repo_root=root,
                release=args.release,
                channel=args.channel,
                previous_tag=args.previous_tag,
            )
            return 0

        publish_release(repo_root=root, release=args.release)
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Doctrine's repo-owned release prepare, tag, draft, and publish flow."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    prepare = subparsers.add_parser(
        "prepare",
        help="Validate release inputs and print the fixed release worksheet.",
    )
    prepare.add_argument("--release", required=True, help="Release tag such as v1.2.3 or v1.2.3-beta.1.")
    prepare.add_argument(
        "--class",
        dest="release_class",
        required=True,
        choices=("internal", "additive", "soft-deprecated", "breaking"),
        help="Release class that drives the release-kind and version-move rules.",
    )
    prepare.add_argument(
        "--language-version",
        required=True,
        help="Use `unchanged` or the next Doctrine language version such as 1.1 or 2.0.",
    )
    prepare.add_argument(
        "--channel",
        required=True,
        choices=("stable", "beta", "rc"),
        help="Public release channel.",
    )

    tag = subparsers.add_parser(
        "tag",
        help="Create and push one signed annotated public release tag.",
    )
    tag.add_argument("--release", required=True, help="Release tag such as v1.2.3 or v1.2.3-beta.1.")
    tag.add_argument(
        "--channel",
        required=True,
        choices=("stable", "beta", "rc"),
        help="Public release channel.",
    )

    draft = subparsers.add_parser(
        "draft",
        help="Create one GitHub draft release from an existing pushed tag.",
    )
    draft.add_argument("--release", required=True, help="Release tag such as v1.2.3 or v1.2.3-beta.1.")
    draft.add_argument(
        "--channel",
        required=True,
        choices=("stable", "beta", "rc"),
        help="Public release channel.",
    )
    draft.add_argument(
        "--previous-tag",
        default="auto",
        help="Use `auto` or one explicit earlier tag for generated-note diffing.",
    )

    publish = subparsers.add_parser(
        "publish",
        help="Publish one existing reviewed GitHub draft release.",
    )
    publish.add_argument("--release", required=True, help="Release tag such as v1.2.3 or v1.2.3-beta.1.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
