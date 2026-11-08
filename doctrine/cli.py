from __future__ import annotations

import argparse

from doctrine.home_commands import build, check, load, where, classes, run_command
from doctrine.diff import diff
from doctrine.import_markdown import import_markdown
from doctrine.sources import sources


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doctrine")
    commands = parser.add_subparsers(dest="command", required=True)
    for verb, help_text in {
        "build": "Build agent and team homes.",
        "check": "Check homes without writing files.",
        "load": "Show what each home loads and how much space it uses.",
        "diff": "Show changes and the homes they reach.",
        "where": "Find words and the homes that read them.",
    }.items():
        command = commands.add_parser(verb, help=help_text)
        command.add_argument("--pyproject", help="Use this pyproject.toml file.")
        command.add_argument("--target", help="Use this emit target.")
        command.add_argument("--json", action="store_true", help="Print the report as JSON.")
        command.set_defaults(rev=None, overlays=[])
        if verb != "where":
            command.add_argument("--rev", help="Read source from this Git revision.")
            command.add_argument("--with", dest="overlays", action="append", default=[], help="Overlay a working-tree file on the revision; may be repeated.")
        if verb != "where":
            command.add_argument("selectors", nargs="*", help="Select agents, teams, or home paths.")
        if verb == "build":
            command.add_argument("--out", help="Write homes under this output root.")
            command.add_argument("--force", action="store_true", help="Overwrite hand-edited generated files.")
        elif verb == "check":
            command.add_argument("--strict", action="store_true", help="Fail on warnings.")
        elif verb == "where":
            command.add_argument("words", help="Find these words in source text.")
            command.add_argument("--home", help="Search only this home.")
        elif verb == "diff":
            base = command.add_mutually_exclusive_group()
            base.add_argument("--base", default="HEAD", help="Compare with this Git revision (default: HEAD).")
            base.add_argument("--base-tree", help="Compare with this directory tree.")
        else:
            command.add_argument("--runtime", help="Show only this runtime.")
            command.add_argument("--full", action="store_true", help="Show one home's loaded files in full.")
    source_command = commands.add_parser("sources", help="List quotes, their sources, and where they are used.")
    source_command.add_argument("--pyproject", help="Use this pyproject.toml file.")
    source_command.add_argument("--target", help="Use this emit target.")
    source_command.add_argument("--json", action="store_true", help="Print the report as JSON.")
    source_command.add_argument("--person", help="Show sources for this person.")
    source_command.set_defaults(rev=None, overlays=[])
    classes_command = commands.add_parser("classes", help="Show the class tree, one class, or where an agent's text came from.")
    classes_command.add_argument("selector", nargs="?", help="Inspect a class, team, member, or home path.")
    classes_command.add_argument("--pyproject", help="Use this pyproject.toml file.")
    classes_command.add_argument("--target", help="Use this emit target.")
    classes_command.add_argument("--rev", help="Read source from this Git revision.")
    classes_command.add_argument("--with", dest="overlays", action="append", default=[], help="Overlay a working-tree file on the revision; may be repeated.")
    formats = classes_command.add_mutually_exclusive_group()
    formats.add_argument("--json", action="store_true", help="Print the report as JSON.")
    formats.add_argument("--mermaid", action="store_true", help="Print a Mermaid class diagram.")
    import_command = commands.add_parser("import", help="Turn a Markdown file into Doctrine source.")
    import_command.add_argument("path", help="Read this Markdown file.")
    import_command.add_argument("--name", required=True, help="Name the new declaration.")
    import_command.add_argument("--kind", choices=("workflow", "agent"), required=True, help="Choose the declaration kind.")
    import_command.add_argument("--check", action="store_true", help="Check that the render matches the Markdown.")
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
