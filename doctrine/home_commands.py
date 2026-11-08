from __future__ import annotations

import argparse
import io
import json
import re
import sys
import subprocess
from html import unescape
from contextlib import contextmanager, nullcontext, redirect_stderr
from dataclasses import replace
from difflib import SequenceMatcher
from os.path import relpath
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from doctrine import model
from doctrine._compiler.session import CompilationSession
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.load_rules import validate_load_rules
from doctrine._compiler.markdown_links import markdown_destinations
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.provenance import declaration_owners
from doctrine._compiler.source_graph import declarations_in
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import load_emit_targets, resolve_pyproject_path
from doctrine.homes import compile_homes, build_homes
from doctrine.parser import parse_file
from doctrine.project_config import load_project_config, project_file_path, real_project_path
from doctrine.project_warnings import project_warnings
from doctrine.revision_source import revision_source
from doctrine.runtime_load import (
    RUNTIMES, runtime_settings, home_loads, budget_findings, render_load, loaded_levels, is_missing,
    text_size, padded_rows,
)


@contextmanager
def resolve_target(args):
    source = revision_source(args) if args.rev else nullcontext((args.pyproject, None, None, None))
    with source as (project_path, target_names, live_root, revision):
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
        if revision:
            targets = {name: replace(target, project_config=replace(target.project_config, revision=revision))
                       for name, target in targets.items()}
        sessions, team_targets = {}, []
        for target in targets.values():
            if target.entrypoint.name in ("AGENTS.prompt", "SOUL.prompt"):
                session = CompilationSession(
                    parse_file(target.entrypoint),
                    project_config=target.project_config,
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


def check_homes(target, session, selectors):
    homes, files, selected, whole = compile_homes(
        target, session=session, selectors=selectors, evaluate_rules=True
    )
    root = target.project_config.config_dir.resolve()
    built = {(target.output_dir / path).resolve() for path in files}
    dead_links = []
    for name, content in files.items():
        if not name.endswith(".md") or isinstance(content, Path):
            continue
        text = content.decode()
        for start, end, is_import in markdown_destinations(text):
            if is_import and text[end:].split("\n", 1)[0].strip():
                continue
            dest = text[start:end]
            url = urlsplit(dest)
            if url.scheme or url.netloc or not url.path:
                continue
            path = re.sub(r"\\([ !\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", unquote(unescape(url.path)))
            resolved = ((target.output_dir / name).parent / Path(path).expanduser()).resolve()
            if resolved.is_relative_to(root) and not resolved.exists() and resolved not in built:
                dead_links.append(f"{name} points at {dest}, which does not exist.")
    if dead_links:
        raise compile_error(code="E636", summary="Dead link", detail="\n".join(dead_links))
    settings = runtime_settings(target)
    context = CompilationContext(session)
    validate_load_rules(context, homes, selected, whole)
    loads = home_loads(target, homes, files, settings, selected)
    findings, failed = budget_findings(loads, settings)
    warnings = []
    if whole:
        declarations = declarations_in(session)
        declaration_owners(context, declarations, target.project_config.config_dir)
        warnings = project_warnings(session, homes, loads, context, declarations)
    warnings += [{"code": finding.split()[0], "text": finding}
                 for finding in findings if finding.startswith("W")]
    disabled = (target.project_config.raw_check or {}).get("disable", [])
    warnings = [warning for warning in warnings if warning["code"] not in disabled]
    findings = [finding for finding in findings if not finding.startswith("W")]
    return homes, files, selected, whole, findings, warnings, failed


def build(args):
    with resolve_target(args) as (target, session, live_root):
        if target is None:
            return 2
        homes, files, selected, whole, findings, warnings, failed = check_homes(
            target, session, args.selectors
        )
        for finding in (*findings, *(warning["text"] for warning in warnings)):
            print(finding, file=sys.stderr)
        if failed:
            return 1
        output = (Path(args.out).resolve() if args.out else
                  live_root / target.output_dir.relative_to(target.project_config.config_dir)
                  if live_root else None)
        result = build_homes(target, homes, files, selected=selected, whole=whole,
                             output_dir=output, force=args.force)
        if args.json:
            print(json.dumps(result))
        else:
            count = sum(any(path.endswith(".md") for path in homes[home]["files"])
                        for home in selected)
            changed = len(result["written"]) + len(result["removed"])
            print(f"built {count} {'home' if count == 1 else 'homes'}, "
                  f"{changed} {'file' if changed == 1 else 'files'} changed")
        return 0


def check(args):
    homes, warnings, paths = {}, [], []
    try:
        with resolve_target(args) as (target, session, live_root):
            if target is None:
                return 2
            homes, files, selected, whole, findings, warnings, failed = check_homes(
                target, session, args.selectors
            )
            output = (live_root / target.output_dir.relative_to(target.project_config.config_dir)
                      if live_root else None)
            result = build_homes(target, homes, files, selected=selected, whole=whole,
                                 output_dir=output, read_only=True)
            paths = result["paths"]
            ok = not failed and not paths and not (args.strict and warnings)
    except DoctrineError as exc:
        if not args.json:
            raise
        findings, ok = [str(exc)], False
    if args.json:
        print(json.dumps({"format_version": 1, "ok": ok, "homes": len(selected) if homes else 0,
                          "errors": [{"code": finding.split()[0], "text": finding}
                                     for finding in findings],
                          "warnings": warnings, "paths": paths}))
    else:
        for finding in (*findings, *(warning["text"] for warning in warnings)):
            print(finding, file=sys.stderr)
        for path in paths:
            print(f"{path['state']} {path['path']}", file=sys.stderr)
        if ok:
            print(f"ok: {len(selected)} homes checked")
    return int(not ok)


def load(args):
    with resolve_target(args) as (target, session, live_root):
        if target is None:
            return 2
        settings = runtime_settings(target)
        homes, files, selected, _ = compile_homes(
            target, session=session, selectors=args.selectors
        )
        generated = {(target.output_dir / name).resolve(): content for name, content in files.items()
                     if isinstance(content, bytes)}
        shared = {}
        for home in sorted(selected):
            for _, level in loaded_levels(homes, home):
                for ref, _ in level["file_refs"]:
                    path = Path(ref[2])
                    name = relpath(real_project_path(target.project_config, path),
                                   real_project_path(target.project_config, target.project_config.config_dir))
                    if name not in shared:
                        source = project_file_path(target.project_config, path)
                        text = (generated[source] if source in generated else source.read_bytes()).decode(errors="replace")
                        shared[name] = {"path": name, "sizes": {
                            runtime: text_size(text, runtime) for runtime in target.runtimes}, "homes": []}
                    if home not in shared[name]["homes"]:
                        shared[name]["homes"].append(home)
        shared_files = sorted(shared.values(), key=lambda row: (
            -row["sizes"][target.runtimes[0]], row["path"]))
        if live_root:
            output = live_root / target.output_dir.relative_to(target.project_config.config_dir)
        loads = home_loads(target, homes, files, settings, selected)
        for home in loads:
            for runtime, load in home["runtimes"].items():
                for file in load["files"]:
                    if live_root and file["kind"] in ("external", "reserved"):
                        file["on_disk"] = (live_root / Path(file["path"]).expanduser()).is_file()
                    if live_root and file["kind"] == "home":
                        link = PurePosixPath(file["path"]).parent / RUNTIMES[runtime][0]
                        file["on_disk"] = (output / link).is_file()
                    if file["kind"] == "home" and not file["on_disk"]:
                        file["path"] = str(PurePosixPath(file["path"]).parent / RUNTIMES[runtime][0])
        if args.runtime and args.runtime not in settings:
            raise compile_error(
                code="E632",
                summary="Invalid runtime settings",
                detail=f"Unknown runtime `{args.runtime}`.",
            )
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
            print(json.dumps({"format_version": 1, "homes": loads, "shared_files": shared_files}))
        elif args.full and len(selected) == 1:
            for runtime in loads[0]["runtimes"].values():
                for file in runtime["files"]:
                    if file["kind"] == "read_first":
                        continue
                    missing = " missing" if is_missing(file) else ""
                    print(f"===== {file['path']} ({file['size']:,}){missing} =====")
                    print(file["text"], end="" if file["text"].endswith("\n") else "\n")
        else:
            print(render_load(loads))
            if shared_files:
                rows = [("  Path", *target.runtimes, "Homes")]
                rows.extend(("  " + row["path"], *(f"{row['sizes'][runtime]:,}"
                    for runtime in target.runtimes), str(len(row["homes"]))) for row in shared_files)
                print("\nShared files:\n" + padded_rows(rows))
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


def where_source(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return None
        homes, files, selected, _ = compile_homes(
            target, session=session, selectors=[args.home] if args.home else ()
        )
        if args.home:
            selected = {home for home in selected
                        if home == args.home or homes[home]["owner"].name == args.home}
            if not selected:
                raise compile_error(code="E640", summary="No home matches",
                                    detail=f"`{args.home}` matches no home.")
        needle = " ".join(args.words.casefold().split())
        matches, sentences, readers = {}, {}, {}
        for path, line, home in session.value_origins:
            readers.setdefault(home, set()).add((path, line))
        reached_values = {}
        for home in sorted(selected):
            for level, data in loaded_levels(homes, home):
                for site in readers.get(level, ()):
                    reached_values.setdefault(site, set()).add(home)
                for entry, text in data["map"].texts.items():
                    if level != home and not entry.always_on:
                        continue
                    key = (entry.origin, entry.origin_path, entry.site)
                    if needle in " ".join(text.casefold().split()):
                        matches.setdefault(key, set()).add(home)
                    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
                        if sentence.strip():
                            sentences.setdefault((*key, sentence.strip()), set()).add(home)
        values = {}
        for unit, declaration in declarations_in(session).values():
            if isinstance(declaration, (model.Agent, model.Team, model.Member)):
                for field in declaration.fields:
                    if isinstance(field, model.ValuesField):
                        for key, text, span in field.items:
                            path = unit.prompt_file.source_path
                            if needle in " ".join(text.casefold().split()):
                                reached = reached_values.get((path, span.line), set())
                                if not args.home or reached:
                                    site = f"{relpath(path, target.project_config.config_dir)}:{span.line}"
                                    values[path, span.line] = {
                                        "origin": f"value {key}", "site": site,
                                        "homes": sorted(reached),
                                    }
        result = list(values.values()) + [
            {"origin": ".".join((origin, *path)), "site": site, "homes": sorted(reached)}
            for (origin, path, site), reached in matches.items()
        ]
        generated = {(target.output_dir / name).resolve(): content for name, content in files.items()
                     if isinstance(content, bytes)}
        for unit, declaration in declarations_in(session).values():
            if not isinstance(declaration, model.FileDecl):
                continue
            base = target.output_dir if declaration.body is not None else target.project_config.config_dir
            path = ((base / declaration.path).resolve() if declaration.body is not None
                    else project_file_path(target.project_config, declaration.path))
            reached = {home for home in selected for _, level in loaded_levels(homes, home)
                       if any(project_file_path(target.project_config, ref[2]) == path for ref, _ in level["file_refs"])}
            if (args.home and not reached) or (declaration.body is not None and path not in generated):
                continue
            text = generated[path].decode() if path in generated else path.read_text(errors="replace")
            for line, value in enumerate(text.splitlines(), 1):
                if needle in " ".join(value.casefold().split()):
                    result.append({"origin": f"file {declaration.name}",
                        "site": f"{relpath(path, target.project_config.config_dir)}:{line}",
                        "homes": sorted(reached)})
        closest, best = None, 0.6
        if not result:
            for (origin, path, site, sentence), reached in sorted(
                sentences.items(), key=lambda item: (item[0][2].rsplit(":", 1)[0],
                                                       int(item[0][2].rsplit(":", 1)[1]))
            ):
                score = SequenceMatcher(None, needle.split(), sentence.casefold().split()).ratio()
                if score >= best and (closest is None or score > best):
                    closest, best = {
                        "origin": ".".join((origin, *path)), "site": site,
                        "homes": sorted(reached), "text": sentence,
                    }, score
        return {"matches": result, "closest": closest}


def where(args):
    try:
        result = where_source(args)
    except DoctrineError as original:
        if original.code == "E640":
            raise
        try:
            with redirect_stderr(io.StringIO()):
                result = where_source(argparse.Namespace(**{**vars(args), "rev": "HEAD"}))
            if result is None:
                raise original
        except (DoctrineError, subprocess.CalledProcessError, OSError):
            raise original
        print("Source has errors. Searching HEAD.", file=sys.stderr)
    if result is None:
        return 2
    if args.json:
        print(json.dumps({"format_version": 1, **result}))
    else:
        for match in result["matches"] or ([result["closest"]] if result["closest"] else []):
            if not result["matches"]:
                print("No exact match. Closest:")
            count = len(match["homes"])
            print(f"{match['origin']}  {match['site']}")
            if "text" in match:
                print(f"  {match['text']}")
            reach = f"  reaches {count} {'home' if count == 1 else 'homes'}"
            print(reach + (": " + ", ".join(match["homes"]) if count else ""))
    return 0 if result["matches"] else 1
