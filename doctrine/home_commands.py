from __future__ import annotations

import json
import sys
import subprocess
from contextlib import contextmanager, nullcontext
from pathlib import Path

from doctrine._compiler.session import CompilationSession
from doctrine._compiler.diagnostics import compile_error
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import load_emit_targets
from doctrine.homes import compile_homes, build_homes, select_homes
from doctrine.parser import parse_file
from doctrine.revision_source import revision_source
from doctrine.runtime_load import runtime_settings, home_loads, budget_findings, render_load


@contextmanager
def resolve_target(args):
    source = revision_source(args) if args.rev else nullcontext((args.pyproject, None, None))
    with source as (project_path, target_names, live_root):
        targets = load_emit_targets(project_path, target_names=target_names)
        team_targets = [target for target in targets.values()
                        if target.entrypoint.name in ("AGENTS.prompt", "SOUL.prompt")
                        and any(not team.abstract for team in CompilationSession(
                            parse_file(target.entrypoint), project_config=target.project_config,
                            evaluate_rules=False).root_flow.teams_by_name.values())]
        if args.target is None and len(team_targets) != 1:
            print("Choose a target with --target.", file=sys.stderr)
            yield None, live_root
            return
        if args.target is not None and args.target not in targets:
            print(f"Unknown target: {args.target}", file=sys.stderr)
            yield None, live_root
            return
        target = targets[args.target] if args.target else team_targets[0]
        for other in team_targets:
            if other.name != target.name and other.output_dir == target.output_dir:
                raise compile_error(
                    code="E607", summary="Two homes, one path",
                    detail=f"Targets `{target.name}` and `{other.name}` "
                           f"share output folder `{target.output_dir}`.",
                )
        yield target, live_root


def build(args):
    with resolve_target(args) as (target, live_root):
        if target is None:
            return 2
        settings = runtime_settings(target)
        homes, files = compile_homes(target)
        loads = home_loads(target, homes, files, settings)
        findings, _ = budget_findings(loads, settings, build=True)
        for finding in findings:
            print(finding, file=sys.stderr)
        output = Path(args.out).resolve() if args.out else (
            live_root / target.output_dir.relative_to(target.project_config.config_dir)
            if live_root else None
        )
        selected, result, changed = build_homes(
            target, homes, files, selectors=args.selectors, output_dir=output,
            check=args.check, force=args.force,
        )
        for level in result["stale_levels"]:
            print(f"W307 stale level: {level} differs from this build.", file=sys.stderr)
        if args.json:
            print(json.dumps(result))
        elif not args.check:
            count = sum(any(path.endswith(".md") for path in homes[home]["files"])
                        for home in selected)
            changed_files = len(result["written"]) + len(result["removed"])
            print(f"built {count} {'home' if count == 1 else 'homes'}, "
                  f"{changed_files} {'file' if changed_files == 1 else 'files'} changed")
        return int(args.check and changed)


def check(args):
    homes = {}
    try:
        with resolve_target(args) as (target, _):
            if target is None:
                return 2
            settings = runtime_settings(target)
            homes, files = compile_homes(target, evaluate_rules=True)
            loads = home_loads(target, homes, files, settings)
            findings, failed = budget_findings(loads, settings)
            ok = not failed and not (args.strict and findings)
    except DoctrineError as exc:
        if not args.json:
            raise
        findings, ok = [str(exc)], False
    if args.json:
        print(json.dumps({"format_version": 1, "ok": ok, "homes": len(homes),
            "errors": [{"code": finding.split()[0], "text": finding}
                       for finding in findings if not finding.startswith("W")],
            "warnings": [{"code": finding.split()[0], "text": finding}
                         for finding in findings if finding.startswith("W")]}))
    else:
        for finding in findings:
            print(finding, file=sys.stderr)
        if ok:
            print(f"ok: {len(homes)} homes checked")
    return int(not ok)


def load(args):
    with resolve_target(args) as (target, _):
        if target is None:
            return 2
        settings = runtime_settings(target)
        homes, files = compile_homes(target)
        loads = home_loads(target, homes, files, settings)
        selected = select_homes(homes, args.selectors)
        if args.runtime and args.runtime not in settings:
            raise compile_error(code="E632", summary="Invalid runtime settings",
                                detail=f"Unknown runtime `{args.runtime}`.")
        loads = [home for home in loads if home["home"] in selected]
        if args.runtime:
            for home in loads:
                home["runtimes"] = {runtime: load for runtime, load in home["runtimes"].items()
                                    if runtime == args.runtime}
        if args.json:
            for home in loads:
                for runtime in home["runtimes"].values():
                    runtime["files"] = [{key: value for key, value in file.items() if key != "text"}
                                        for file in runtime["files"]]
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
    except (OSError, subprocess.CalledProcessError) as exc:
        print(exc, file=sys.stderr)
        return 2
