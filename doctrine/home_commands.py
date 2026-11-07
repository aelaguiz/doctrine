from __future__ import annotations

import argparse
import json
import sys
import subprocess
from contextlib import contextmanager, nullcontext
from pathlib import Path

from doctrine._compiler.session import CompilationSession
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.load_rules import validate_load_rules
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.provenance import declaration_owners
from doctrine._compiler.source_graph import declarations_in
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import load_emit_targets, resolve_pyproject_path
from doctrine.homes import compile_homes, build_homes
from doctrine.parser import parse_file
from doctrine.project_config import load_project_config
from doctrine.project_warnings import project_warnings
from doctrine.revision_source import revision_source
from doctrine.runtime_load import (
    runtime_settings, home_loads, budget_findings, render_load, loaded_levels,
)


@contextmanager
def resolve_target(args):
    source = revision_source(args) if args.rev else nullcontext((args.pyproject, None, None))
    with source as (project_path, target_names, live_root):
        config = load_project_config(resolve_pyproject_path(project_path))
        if args.target:
            raw_targets = (config.raw_emit or {}).get("targets", [])
            chosen = next((item for item in raw_targets if item["name"] == args.target), None)
            if chosen is None:
                print(f"Unknown target: {args.target}", file=sys.stderr)
                yield None, None, live_root
                return
            target_names = tuple(
                item["name"] for item in raw_targets if item["output_dir"] == chosen["output_dir"]
            )
        targets = load_emit_targets(project_path, target_names=target_names)
        sessions, team_targets = {}, []
        for target in targets.values():
            if target.entrypoint.name in ("AGENTS.prompt", "SOUL.prompt"):
                session = CompilationSession(
                    parse_file(target.entrypoint),
                    project_config=target.project_config,
                    evaluate_rules=False,
                )
                sessions[target.name] = session
                if any(not team.abstract for team in session.root_flow.teams_by_name.values()):
                    team_targets.append(target)
        if args.target is None and len(team_targets) != 1:
            print("Choose a target with --target.", file=sys.stderr)
            yield None, None, live_root
            return
        target = targets[args.target] if args.target else team_targets[0]
        if target.name not in sessions:
            print(f"Target {target.name} has no homes.", file=sys.stderr)
            yield None, None, live_root
            return
        for other in team_targets:
            if other.name != target.name and other.output_dir == target.output_dir:
                raise compile_error(
                    code="E607",
                    summary="Two homes, one path",
                    detail=f"Targets `{target.name}` and `{other.name}` "
                    f"share output folder `{target.output_dir}`.",
                )
        yield target, sessions[target.name], live_root


def build(args):
    with resolve_target(args) as (target, session, live_root):
        if target is None:
            return 2
        homes, files, selected, whole = compile_homes(
            target, session=session, selectors=args.selectors
        )
        try:
            settings = runtime_settings(target)
            loads = home_loads(target, homes, files, settings)
            findings, _ = budget_findings(
                [load for load in loads if load["home"] in selected], settings, build=True
            )
            for finding in findings:
                print(finding, file=sys.stderr)
        except DoctrineError as exc:
            if exc.code not in {"E631", "E632", "E633"}:
                raise
            print(exc, file=sys.stderr)
        output = (
            Path(args.out).resolve()
            if args.out
            else (
                live_root / target.output_dir.relative_to(target.project_config.config_dir)
                if live_root
                else None
            )
        )
        result, changed = build_homes(
            target,
            homes,
            files,
            selected=selected,
            whole=whole,
            output_dir=output,
            check=args.check,
            force=args.force,
        )
        for level in result["stale_levels"]:
            print(f"W307 stale level: {level} differs from this build.", file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {"format_version": 1, "paths": result["paths"]} if args.check else result
                )
            )
        elif args.check:
            for path in result["paths"]:
                print(f"{path['state']} {path['path']}")
        else:
            count = sum(
                any(path.endswith(".md") for path in homes[home]["files"]) for home in selected
            )
            changed_files = len(result["written"]) + len(result["removed"])
            print(
                f"built {count} {'home' if count == 1 else 'homes'}, "
                f"{changed_files} {'file' if changed_files == 1 else 'files'} changed"
            )
        return int(args.check and changed)


def check(args):
    homes, warnings = {}, []
    try:
        with resolve_target(args) as (target, session, _):
            if target is None:
                return 2
            settings = runtime_settings(target)
            homes, files, _, _ = compile_homes(target, evaluate_rules=True, session=session)
            context = CompilationContext(session)
            declarations = declarations_in(session)
            declaration_owners(context, declarations, target.project_config.config_dir)
            validate_load_rules(context, homes)
            loads = home_loads(target, homes, files, settings)
            findings, failed = budget_findings(loads, settings)
            warnings = project_warnings(session, homes, loads, context, declarations) + [
                {"code": finding.split()[0], "text": finding}
                for finding in findings if finding.startswith("W")
            ]
            disabled = (target.project_config.raw_check or {}).get("disable", [])
            warnings = [warning for warning in warnings if warning["code"] not in disabled]
            findings = [finding for finding in findings if not finding.startswith("W")]
            ok = not failed and not (args.strict and (findings or warnings))
    except DoctrineError as exc:
        if not args.json:
            raise
        findings, ok = [str(exc)], False
    if args.json:
        print(
            json.dumps(
                {
                    "format_version": 1,
                    "ok": ok,
                    "homes": len(homes),
                    "errors": [
                        {"code": finding.split()[0], "text": finding}
                        for finding in findings
                    ],
                    "warnings": warnings,
                }
            )
        )
    else:
        for finding in (*findings, *(warning["text"] for warning in warnings)):
            print(finding, file=sys.stderr)
        if ok:
            print(f"ok: {len(homes)} homes checked")
    return int(not ok)


def load(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return 2
        settings = runtime_settings(target)
        homes, files, selected, _ = compile_homes(
            target, session=session, selectors=args.selectors
        )
        loads = home_loads(target, homes, files, settings)
        if args.runtime and args.runtime not in settings:
            raise compile_error(
                code="E632",
                summary="Invalid runtime settings",
                detail=f"Unknown runtime `{args.runtime}`.",
            )
        loads = [home for home in loads if home["home"] in selected]
        if args.runtime:
            for home in loads:
                home["runtimes"] = {
                    runtime: load
                    for runtime, load in home["runtimes"].items()
                    if runtime == args.runtime
                }
        if args.json:
            for home in loads:
                for runtime in home["runtimes"].values():
                    runtime["files"] = [
                        {key: value for key, value in file.items() if key != "text"}
                        for file in runtime["files"]
                    ]
            print(json.dumps({"format_version": 1, "homes": loads}))
        elif args.full and len(selected) == 1:
            for runtime in loads[0]["runtimes"].values():
                for file in runtime["files"]:
                    print(f"===== {file['path']} ({file['size']:,}) =====")
                    print(file["text"], end="" if file["text"].endswith("\n") else "\n")
        else:
            print(render_load(loads))
        return 0


def run_command(args, command):
    try:
        return command(args)
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (argparse.ArgumentError, OSError, subprocess.CalledProcessError) as exc:
        print(exc, file=sys.stderr)
        return 2


def where(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return 2
        homes, _, selected, _ = compile_homes(
            target, session=session, selectors=[args.home] if args.home else ()
        )
        needle = " ".join(args.words.casefold().split())
        matches = {}
        for home in sorted(selected):
            for level, data in loaded_levels(homes, home):
                for entry, text in data["map"].texts.items():
                    if (level != home and not entry.always_on) or needle not in " ".join(
                        text.casefold().split()
                    ):
                        continue
                    key = (entry.origin, entry.origin_path, entry.site)
                    matches.setdefault(key, set()).add(home)
        result = [
            {"origin": ".".join((origin, *path)), "site": site, "homes": sorted(reached)}
            for (origin, path, site), reached in matches.items()
        ]
        if args.json:
            print(json.dumps({"format_version": 1, "matches": result}))
        else:
            for match in result:
                count = len(match["homes"])
                print(f"{match['origin']}  {match['site']}")
                print(
                    f"  reaches {count} {'home' if count == 1 else 'homes'}: "
                    + ", ".join(match["homes"])
                )
        return 0 if matches else 1
