from __future__ import annotations

import argparse

from doctrine.home_commands import build, check, load, run_command


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doctrine")
    commands = parser.add_subparsers(dest="command", required=True)
    for verb in ("build", "check", "load"):
        command = commands.add_parser(verb)
        command.add_argument("--pyproject")
        command.add_argument("--target")
        command.add_argument("--json", action="store_true")
        command.add_argument("--rev")
        command.add_argument("--with", dest="overlays", action="append", default=[])
        if verb != "check":
            command.add_argument("selectors", nargs="*")
        if verb == "build":
            command.add_argument("--out")
            command.add_argument("--check", action="store_true")
            command.add_argument("--force", action="store_true")
        elif verb == "check":
            command.add_argument("--strict", action="store_true")
        else:
            command.add_argument("--runtime")
            command.add_argument("--full", action="store_true")
    args = parser.parse_args(argv)
    if args.overlays and not args.rev:
        parser.error("--with needs --rev")
    return run_command(args, {"build": build, "check": check, "load": load}[args.command])


if __name__ == "__main__":
    raise SystemExit(main())
