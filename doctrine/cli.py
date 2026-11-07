from __future__ import annotations

import argparse

from doctrine.home_commands import build, check, load, where, classes, run_command
from doctrine.diff import diff
from doctrine.import_markdown import import_markdown
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
        if verb != "where":
            command.add_argument("selectors", nargs="*")
        if verb == "build":
            command.add_argument("--out")
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
    classes_command = commands.add_parser("classes")
    classes_command.add_argument("selector", nargs="?")
    classes_command.add_argument("--pyproject")
    classes_command.add_argument("--target")
    classes_command.add_argument("--rev")
    classes_command.add_argument("--with", dest="overlays", action="append", default=[])
    formats = classes_command.add_mutually_exclusive_group()
    formats.add_argument("--json", action="store_true")
    formats.add_argument("--mermaid", action="store_true")
    import_command = commands.add_parser("import")
    import_command.add_argument("path")
    import_command.add_argument("--name", required=True)
    import_command.add_argument("--kind", choices=("workflow", "agent"), required=True)
    import_command.add_argument("--check", action="store_true")
    import_command.set_defaults(overlays=[])
    args = parser.parse_args(argv)
    if args.overlays and not args.rev and args.command != "diff":
        parser.error("--with needs --rev")
    return run_command(args, {
        "build": build, "check": check, "load": load, "diff": diff, "where": where, "sources": sources,
        "import": import_markdown, "classes": classes,
    }[args.command])


if __name__ == "__main__":
    raise SystemExit(main())
