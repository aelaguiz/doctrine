from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.details import split_details, render_companion
from doctrine._compiler.home_map import build_home_map
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_reader import fenced_lines
from doctrine._compiler.teams import team_members, team_contract
from doctrine.emit_docs import (
    _runtime_emit_roots_for_target,
    _build_runtime_emit_plan,
    _build_previous_turn_contexts,
    runtime_files,
)
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import entrypoint_relative_dir
from doctrine.renderer import render_markdown
from doctrine.runtime_load import home_budgets


HEADER = re.compile(
    r"^<!-- doctrine sha256=([a-f0-9]{12}) source=(.*)\. Do not edit\. "
    r'Run: doctrine where "<words>" -->\n\n'
)


def with_header(text, source):
    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
    return (
        f"<!-- doctrine sha256={digest} source={source}. Do not edit. "
        f'Run: doctrine where "<words>" -->\n\n{text}'
    )


def home_files(target, home, owner, unit, compiled, pointers, plan, evaluate_rules):
    text = render_markdown(compiled)
    if pointers:
        links = (
            f"[{path if path.startswith('_details/') else 'DETAILS.md'}]"
            f"({os.path.relpath(path, home)})"
            for path in pointers
        )
        text = (
            text.rstrip() + "\n\nFuller cases, under the same headings: " + ", ".join(links) + ".\n"
        )
    if plan is not None:
        files = runtime_files(plan, compiled, target, evaluate_rules=evaluate_rules)
        files[plan.markdown_path] = text.encode()
        source = unit.prompt_file.source_path.relative_to(
            target.project_config.config_dir
        ).as_posix()
        return {
            path.relative_to(target.output_dir).as_posix(): with_header(
                content.decode(), source
            ).encode()
            if path.suffix == ".md"
            else content
            for path, content in files.items()
        }
    files = {}
    if text.strip():
        source_unit = (owner.scope_unit or unit) if isinstance(owner, model.Member) else unit
        source = source_unit.prompt_file.source_path.relative_to(
            target.project_config.config_dir
        ).as_posix()
        runtimes = target.runtimes or ("codex",)
        filename = "CLAUDE.md" if runtimes == ("claude",) else "AGENTS.md"
        files[str(PurePosixPath(home) / filename)] = with_header(text, source).encode()
        if "claude" in runtimes and "codex" in runtimes:
            files[str(PurePosixPath(home) / "CLAUDE.md")] = Path("AGENTS.md")
    return files


def compile_home(target, session, context, home, owner, unit, compiled, plan):
    session.emit_paths[owner.name] = target.output_dir / home / "AGENTS.md"
    if plan is None:
        compiled = session.compile_agent(owner.name)
    home_map = build_home_map(compiled, home)
    source_compiled = compiled
    compiled, parts, pointers = split_details(compiled, home)
    files = home_files(target, home, owner, unit, compiled, pointers, plan, session.evaluate_rules)
    data = {
        "owner": owner,
        "unit": unit,
        "compiled": compiled,
        "source_compiled": source_compiled,
        "map": home_map,
        "files": list(files),
        "pointers": pointers,
        "budgets": home_budgets(owner, unit, context),
    }
    return data, files, parts


def companion_files(homes, companions):
    files = {}
    for path, parts in companions.items():
        if path.startswith("_details/"):
            parts.sort(key=lambda part: part[1].origin.line)
        source = parts[0][1].origin.site.rsplit(":", 1)[0]
        text = render_companion(parts)
        local = [
            data for home, data in homes.items() if str(PurePosixPath(home) / "DETAILS.md") == path
        ]
        files[path] = with_header(text, source).encode()
        for data in local:
            data["files"].append(path)
    return files


def compile_homes(target, *, session, evaluate_rules=False, selectors=()):
    selectors = tuple(
        next(
            (
                team.home for team in session.root_flow.teams_by_name.values()
                if not team.abstract and team.name == selector
            ),
            selector,
        )
        for selector in selectors
    )
    whole = not selectors or "." in selectors
    session.evaluate_rules = evaluate_rules
    context = CompilationContext(session)
    homes, files, compiled, companions = {}, {}, {}, {}
    owners, failures = [], []
    for root in _runtime_emit_roots_for_target(session, target=target):
        try:
            plan = _build_runtime_emit_plan(
                root,
                target=target,
                output_root=target.output_dir,
                provider_root=session.provided_prompt_root_for(root.unit.prompt_root),
            )
            unit = root.unit
            owner = session.flow_for_unit(unit).agents_by_name[root.agent_name]
            home = plan.markdown_path.parent.relative_to(target.output_dir).as_posix()
            owners.append((home, owner, unit, plan))
            session.emit_paths[root.agent_name] = plan.markdown_path
        except DoctrineError as exc:
            home = entrypoint_relative_dir(root.unit.prompt_file.source_path).as_posix()
            if whole or any(
                selector == root.agent_name or selector == home or home.startswith(selector + "/")
                for selector in selectors
            ):
                raise
            failures.append(exc)
    for team in session.root_flow.teams_by_name.values():
        if not team.abstract:
            unit = session.root_flow.declaration_owner_units_by_id[id(team)]
            try:
                members = team_members(context, team, unit=unit)
            except DoctrineError as exc:
                if whole or any(
                    selector == team.home
                    or selector.startswith(team.home + "/")
                    or team.home.startswith(selector + "/")
                    or selector.startswith(team.name + ".")
                    for selector in selectors
                ):
                    raise
                failures.append(exc)
                continue
            owners.append((team.home, team, unit, None))
            owners.extend(
                (str(PurePosixPath(team.home) / member.key.replace("_", "-")), member, unit, None)
                for member in members
            )
    for home, owner, unit, plan in owners:
        homes.setdefault(home, {"owner": owner, "unit": unit, "plan": plan})
        session.home_paths[owner.name] = home
    try:
        selected = select_homes(owners, selectors)
    except DoctrineError:
        if failures:
            raise failures[0]
        raise
    for failure in failures:
        print(failure, file=sys.stderr)
    needed = {
        home
        for home in homes
        if home in selected
        or any(PurePosixPath(home) in PurePosixPath(child).parents for child in selected)
    }
    for home, owner, unit, plan in owners:
        if home in needed and homes[home]["owner"] is not owner:
            raise compile_error(
                code="E607", summary="Two homes, one path",
                detail=f"`{homes[home]['owner'].name}` and `{owner.name}` both land at `{home}`.",
            )
    homes = {home: data for home, data in homes.items() if home in needed}
    for home, data in list(homes.items()):
        owner, unit, plan = data["owner"], data["unit"], data["plan"]
        try:
            result = None
            if plan is not None:
                roots = ((unit, owner.name),)
                (result,) = session.compile_agents_from_units(
                    roots,
                    previous_turn_contexts=_build_previous_turn_contexts(
                        session, agent_roots=roots
                    ),
                )
            data, content, parts = compile_home(
                target, session, context, home, owner, unit, result, plan
            )
        except DoctrineError as exc:
            if home in selected:
                raise
            print(exc, file=sys.stderr)
            del homes[home]
            continue
        homes[home] = data
        files.update(content)
        compiled[owner.name] = data["compiled"]
        for companion, content in parts.items():
            collected = companions.setdefault(companion, [])
            collected.extend(
                [
                    part
                    for part in content
                    if not companion.startswith("_details/") or part not in collected
                ]
            )
    for home, data in homes.items():
        owner = data["owner"]
        if (
            home in selected
            and isinstance(owner, model.Team)
            and team_members(context, owner, unit=data["unit"])
        ):
            path = str(PurePosixPath(home) / "TEAM.contract.json")
            contract = team_contract(context, owner, unit=data["unit"], compiled_members=compiled)
            files[path] = (json.dumps(contract, indent=2) + "\n").encode()
            data["files"].append(path)
    files.update(companion_files(homes, companions))
    return homes, files, selected, whole


def select_homes(owners, selectors):
    selected = set()
    for selector in selectors or ["."]:
        matches = {
            home
            for home, owner, unit, plan in owners
            if selector == "."
            or owner.name == selector
            or home == selector
            or home.startswith(selector + "/")
        }
        if not matches:
            raise compile_error(
                code="E640", summary="No home matches", detail=f"`{selector}` matches no home."
            )
        selected.update(matches)
    return selected


def file_state(path, fresh):
    if path.is_symlink():
        if path.name == "CLAUDE.md" and os.readlink(path) == "AGENTS.md":
            return "unchanged" if isinstance(fresh, Path) else "stale"
        return "edited"
    if not path.exists():
        return "missing"
    content = path.read_bytes()
    if path.suffix == ".md":
        text = content.decode()
        match = HEADER.match(text)
        if (
            match is None
            or hashlib.sha256(text[match.end() :].encode()).hexdigest()[:12] != match[1]
        ):
            return "edited"
    return "unchanged" if content == fresh else "stale"


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}")
    if isinstance(content, Path):
        os.symlink(str(content), temporary)
    else:
        with temporary.open("wb") as stream:
            stream.write(content)
    os.replace(temporary, path)


def home_sections(text):
    sections, counts = {}, {}
    key = None
    for line, inside in fenced_lines(text.splitlines(keepends=True)):
        if not inside:
            heading = re.match(r"^ {0,3}##[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$", line.rstrip("\n"))
            if heading:
                title = heading[1]
                key = title, counts.get(title, 0)
                counts[title] = key[1] + 1
                sections[key] = ""
        if key is not None:
            sections[key] += line
    return {key: text.strip("\n") for key, text in sections.items()}


def hand_edit_detail(root, name, files, homes):
    path = root / name
    if path.is_symlink():
        return f"`{name}` is a link Doctrine didn't write."
    old = path.read_text()
    header = HEADER.match(old)
    if header is None:
        return f"`{name}` was written by hand."
    detail = f"`{name}` was edited by hand."
    if path.name == "DETAILS.md" or path.parent.name == "_details":
        return detail + f"\nsource={header[2]}"
    if name in files:
        fresh = files[name]
        if isinstance(fresh, Path):
            fresh = files[str(PurePosixPath(name).parent / str(fresh))]
        old_sections, fresh_sections = home_sections(old), home_sections(fresh.decode())
        origins = {}
        for data in homes.values():
            if name in data["files"]:
                for entry in data["map"].entries:
                    if len(entry.path) == 1 and entry.title is not None and entry.always_on:
                        key = entry.title, sum(title == entry.title for title, _ in origins)
                        origins[key] = entry
        for key in dict.fromkeys((*old_sections, *fresh_sections)):
            if old_sections.get(key) != fresh_sections.get(key):
                if key not in fresh_sections:
                    detail += f"\n- {key[0]}: no longer in source"
                else:
                    entry = origins.get(key)
                    detail += f"\n- {key[0]}"
                    if entry is not None:
                        detail += f": {entry.origin} at {entry.site}"
    return detail


def stale_levels(root, selected, files):
    stale = []
    for home in selected:
        for level in PurePosixPath(home).parents:
            if str(level) in selected:
                continue
            for filename in ("AGENTS.md", "CLAUDE.md"):
                path = str(level / filename)
                if (root / path).is_file() and not (root / path).read_bytes().startswith(
                    b"<!-- doctrine sha256="
                ):
                    continue
                if (
                    path in files
                    and file_state(root / path, files[path]) != "unchanged"
                    or path not in files
                    and (root / path).exists()
                ):
                    stale.append(path)
    return sorted(set(stale))


def build_homes(
    target, homes, files, *, selected, whole, output_dir=None, check=False, force=False
):
    root = output_dir or target.output_dir
    wanted = set(files) if whole else {path for home in selected for path in homes[home]["files"]}
    obsolete = set()
    record = root / "HOMES.contract.json"
    if whole:
        if record.exists():
            try:
                obsolete = set(json.loads(record.read_bytes())["files"]) - set(files)
            except json.JSONDecodeError:
                pass
        files = {
            **files,
            "HOMES.contract.json": (
                json.dumps({"format_version": 1, "files": sorted(files)}, indent=2) + "\n"
            ).encode(),
        }
        wanted.add("HOMES.contract.json")
    states = {name: file_state(root / name, files.get(name)) for name in sorted(wanted | obsolete)}
    if not check and not force:
        for name, state in states.items():
            if state == "edited":
                raise compile_error(
                    code="E634",
                    summary="Hand edit in a compiled file",
                    detail=hand_edit_detail(root, name, files, homes),
                    hints=("Move the edit to its source, then build. `--force` overwrites it.",),
                )
    result = {
        "format_version": 1,
        "written": [],
        "unchanged": [],
        "removed": [],
        "stale_levels": [] if whole else stale_levels(root, selected, files),
    }
    if check:
        result["paths"] = [
            {"path": name, "state": "obsolete" if name in obsolete else state}
            for name, state in states.items()
            if name in obsolete or state != "unchanged"
        ]
    for name, state in states.items():
        if check:
            continue
        if name in obsolete:
            if (root / name).exists() or (root / name).is_symlink():
                (root / name).unlink()
                result["removed"].append(name)
        elif state == "unchanged":
            result["unchanged"].append(name)
        else:
            atomic_write(root / name, files[name])
            result["written"].append(name)
    changed = any(state != "unchanged" or name in obsolete for name, state in states.items())
    return result, changed
