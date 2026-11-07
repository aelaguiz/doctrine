from __future__ import annotations

import argparse

from doctrine.home_commands import build, check, load, where, run_command
from doctrine.diff import diff
from doctrine.sources import sources


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doctrine")
    commands = parser.add_subparsers(dest="command", required=True)
    for verb in ("build", "check", "load", "diff", "where"):
        command = commands.add_parser(verb)
        command.add_argument("--pyproject")
        command.add_argument("--target")
        command.add_argument("--json", action="store_true")
        command.set_defaults(rev=None, overlays=[])
        if verb != "where":
            command.add_argument("--rev")
            command.add_argument("--with", dest="overlays", action="append", default=[])
        if verb not in {"check", "where"}:
            command.add_argument("selectors", nargs="*")
        if verb == "build":
            command.add_argument("--out")
            command.add_argument("--check", action="store_true")
            command.add_argument("--force", action="store_true")
        elif verb == "check":
            command.add_argument("--strict", action="store_true")
        elif verb == "where":
            command.add_argument("words")
            command.add_argument("--home")
        elif verb == "diff":
            base = command.add_mutually_exclusive_group()
            base.add_argument("--base", default="HEAD")
            base.add_argument("--base-tree")
        else:
            command.add_argument("--runtime")
            command.add_argument("--full", action="store_true")
    source_command = commands.add_parser("sources")
    source_command.add_argument("--pyproject")
    source_command.add_argument("--target")
    source_command.add_argument("--json", action="store_true")
    source_command.add_argument("--person")
    source_command.set_defaults(rev=None, overlays=[])
    args = parser.parse_args(argv)
    if args.overlays and not args.rev and args.command != "diff":
        parser.error("--with needs --rev")
    return run_command(args, {
        "build": build, "check": check, "load": load, "diff": diff, "where": where, "sources": sources
    }[args.command])


if __name__ == "__main__":
    raise SystemExit(main())
