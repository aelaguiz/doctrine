from __future__ import annotations

import json
import sys
import subprocess
from contextlib import nullcontext
from pathlib import Path

from doctrine._compiler.session import CompilationSession
from doctrine._compiler.diagnostics import compile_error
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import load_emit_targets
from doctrine.homes import compile_homes, build_homes, select_homes
from doctrine.parser import parse_file
from doctrine.revision_source import revision_source
from doctrine.runtime_load import runtime_settings, home_loads, budget_findings


def run_command(args):
    try:
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
                return 2
            if args.target is not None and args.target not in targets:
                print(f"Unknown target: {args.target}", file=sys.stderr)
                return 2
            target = targets[args.target] if args.target else team_targets[0]
            for other in team_targets:
                if other.name != target.name and other.output_dir == target.output_dir:
                    raise compile_error(code="E607", summary="Two homes, one path", detail=f"Targets `{target.name}` and `{other.name}` share output folder `{target.output_dir}`.")
            settings = runtime_settings(target)
            homes, files = compile_homes(target, evaluate_rules=args.command == "check")
            loads = home_loads(target, homes, files, settings)
            if args.command in ("build", "check"):
                findings, failed = budget_findings(loads, settings, build=args.command == "build")
                for finding in findings:
                    print(finding, file=sys.stderr)
                if args.command == "check":
                    if not failed and not (args.strict and findings):
                        print(f"ok: {sum(bool(home['files']) for home in homes.values())} homes checked")
                        return 0
                    return 1
            if args.command == "build":
                selected, result, changed = build_homes(target, homes, files,
                    selectors=args.selectors, output_dir=Path(args.out).resolve() if args.out else live_root / target.output_dir.relative_to(target.project_config.config_dir) if live_root else None,
                    check=args.check, force=args.force)
                for level in result["stale_levels"]:
                    print(f"W307 stale level: {level} differs from this build.", file=sys.stderr)
                if args.json:
                    print(json.dumps(result))
                elif not args.check:
                    selected = [home for home in selected if any(path.endswith(".md") for path in homes[home]["files"])]
                    count = len(result["written"]) + len(result["removed"])
                    print(f"built {len(selected)} {'home' if len(selected) == 1 else 'homes'}, {count} {'file' if count == 1 else 'files'} changed")
                return int(args.check and changed)
            selected = select_homes(homes, args.selectors)
            if args.runtime and args.runtime not in settings:
                raise compile_error(code="E632", summary="Invalid runtime settings", detail=f"Unknown runtime `{args.runtime}`.")
            if args.full and len(selected) == 1:
                for home in loads:
                    if home["home"] in selected:
                        for runtime, load in home["runtimes"].items():
                            if args.runtime is None or runtime == args.runtime:
                                for file in load["files"]:
                                    print(f"===== {file['path']} ({file['size']:,}) =====")
                                    print(file["text"], end="" if file["text"].endswith("\n") else "\n")
            return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, subprocess.CalledProcessError) as exc:
        print(exc, file=sys.stderr)
        return 2
