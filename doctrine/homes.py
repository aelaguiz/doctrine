from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path, PurePosixPath

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.details import split_details, render_companion
from doctrine._compiler.home_map import build_home_map
from doctrine._compiler.late_binding import bind_home, map_text, reject_case_links
from doctrine._compiler.markdown_links import render_file_refs
from doctrine._compiler.naming import model_walk
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_reader import fenced_lines, heading_anchor
from doctrine._compiler.teams import team_members, team_contract, member_home, find_home_team
from doctrine.emit_docs import (
    _runtime_emit_roots_for_target,
    _build_runtime_emit_plan,
    _build_previous_turn_contexts,
    runtime_files, RuntimeEmitPlan,
)
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import entrypoint_relative_dir, RuntimeEmitRoot
from doctrine.renderer import render_markdown
from doctrine.project_config import project_file_path
from doctrine.runtime_load import home_budgets, loaded_levels
from doctrine.shared_files import HEADER, compile_shared_files, file_state, with_header


def home_files(target, home, owner, unit, compiled, pointers, plan, context):
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
    runtimes = target.runtimes
    filename = "CLAUDE.md" if runtimes == ("claude",) else "AGENTS.md"
    files = {}
    if plan is not None:
        files = runtime_files(plan, compiled, target, evaluate_rules=context.session.evaluate_rules)
        del files[plan.markdown_path]
        source = os.path.relpath(unit.prompt_file.source_path, target.project_config.config_dir)
        files = {
            path.relative_to(target.output_dir).as_posix(): with_header(
                content.decode(), source
            ).encode()
            if path.suffix == ".md"
            else content
            for path, content in files.items()
        }
    if plan is not None or text.strip():
        if isinstance(owner, model.Team) and home != ".":
            title = bind_home(context, owner.title, owner, unit=unit)
            text = f"This file loads for every session started under `{home}/`. If yours started there, you are a member of {title}. If not, it only describes them.\n\n" + text
        elif isinstance(owner, model.Member):
            _, team = find_home_team(context, owner, unit=unit)
            team_title = bind_home(context, team.title, owner, unit=unit)
            title = bind_home(context, owner.title, owner, unit=unit)
            text = f"If your session started in this folder, you are {team_title}'s {title}. If not, this only describes that role.\n\n" + text
        elif not isinstance(owner, model.Team) and owner.title:
            title = bind_home(context, owner.title, owner, unit=unit)
            text = f"If your session started in this folder, you are {title}. If not, this only describes that role.\n\n" + text
        source_unit = (owner.scope_unit or unit) if isinstance(owner, model.Member) else unit
        source = os.path.relpath(source_unit.prompt_file.source_path, target.project_config.config_dir)
        files[str(PurePosixPath(home) / filename)] = with_header(text, source).encode()
        if "claude" in runtimes and "codex" in runtimes:
            files[str(PurePosixPath(home) / "CLAUDE.md")] = Path("AGENTS.md")
    if isinstance(owner, model.Member):
        member_plan = RuntimeEmitPlan(
            root=RuntimeEmitRoot(unit=unit, agent_name=owner.name),
            markdown_path=target.output_dir / home / "AGENTS.md",
            provider_root=None,
        )
        for path, content in runtime_files(member_plan, compiled, target).items():
            if path != member_plan.markdown_path:
                files[path.relative_to(target.output_dir).as_posix()] = content
    return files


def compile_home(target, session, context, home, owner, unit, plan):
    if owner.title:
        reject_case_links(bind_home(context, owner.title, owner, unit=unit), unit=unit)
    if isinstance(owner, model.Member):
        _, team = find_home_team(context, owner, unit=unit)
        reject_case_links(bind_home(context, team.title, owner, unit=unit), unit=unit)
    if plan is None:
        compiled = session.compile_agent(owner.name)
    else:
        roots = ((unit, owner.name),)
        (compiled,) = session.compile_agents_from_units(
            roots, previous_turn_contexts=_build_previous_turn_contexts(session, agent_roots=roots)
        )
    home_map = build_home_map(map_text(
        compiled, lambda text: render_file_refs(text, target.output_dir / home, target.project_config)))
    compiled, parts, pointers, unlinked, case_links = split_details(compiled, home, target.output_dir, home_map, unit)
    refs = [(json.loads(match[1]), always_on)
            for value, always_on in [(compiled, True), (tuple(parts.values()), False)]
            for text in model_walk(value) if isinstance(text, str)
            for match in re.finditer(r"([^]+)", text)]
    contract_compiled = compiled
    compiled = map_text(compiled, lambda text: render_file_refs(text, target.output_dir / home, target.project_config))
    files = home_files(target, home, owner, unit, compiled, unlinked, plan, context)
    data = {
        "owner": owner,
        "unit": unit,
        "compiled": compiled,
        "contract_compiled": contract_compiled,
        "map": home_map,
        "files": list(files),
        "pointers": pointers,
        "case_links": case_links,
        "budgets": home_budgets(owner, unit, context),
        "file_refs": refs,
    }
    return data, files, parts


def companion_files(homes, companions, target):
    files = {}
    for path, parts in companions.items():
        if path.startswith("_details/"):
            parts.sort(key=lambda part: part[1].origin.line)
        source = parts[0][1].origin.site.rsplit(":", 1)[0]
        text = render_file_refs(render_companion(parts), (target.output_dir / path).parent, target.project_config)
        seen = {}
        for line, inside in fenced_lines(text.splitlines()):
            if not inside and (heading := re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)):
                heading_anchor(heading[1], seen)
        for data in homes.values():
            for companion, anchor, name in data["case_links"]:
                if companion == path and seen.get(anchor, 0) > 1:
                    raise compile_error(code="E637", summary="Dead case link",
                        detail=f"`details:{name}` shares its heading with another in `{path}`. Give it a title of its own.")
        local = [
            data for home, data in homes.items() if str(PurePosixPath(home) / "DETAILS.md") == path
        ]
        files[path] = with_header(text, source).encode()
        for data in local:
            data["files"].append(path)
    return files


def home_selectors(teams, selectors):
    homes = {team.name: team.home for team in teams if not team.abstract}
    return tuple(homes.get(selector, selector) for selector in selectors)


def is_level(home, selected):
    return home in selected or any(PurePosixPath(home) in PurePosixPath(child).parents for child in selected)


def home_owners(target, session):
    context = CompilationContext(session)
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
        except DoctrineError as exc:
            home = entrypoint_relative_dir(root.unit.prompt_file.source_path).as_posix()
            owner = session.flow_for_unit(root.unit).agents_by_name[root.agent_name]
            owners.append((home, owner, root.unit, None))
            failures.append((home, exc))
    for team in session.root_flow.teams_by_name.values():
        if not team.abstract:
            unit = session.root_flow.declaration_owner_units_by_id[id(team)]
            try:
                members = team_members(context, team, unit=unit)
            except DoctrineError as exc:
                owners.append((team.home, team, unit, None))
                failures.append((team.home, exc))
                continue
            owners.append((team.home, team, unit, None))
            owners.extend(
                (member_home(team, member), member, unit, None)
                for member in members
            )
    return owners, failures


def compile_homes(target, *, session, evaluate_rules=False, selectors=()):
    selectors = home_selectors(session.root_flow.teams_by_name.values(), selectors)
    whole = not selectors or "." in selectors
    session.evaluate_rules = evaluate_rules
    context = CompilationContext(session)
    homes, files, compiled, companions = {}, {}, {}, {}
    owners, failures = home_owners(target, session)
    session.emit_root = target.output_dir
    for home, owner, unit, plan in owners:
        homes.setdefault(home, {"owner": owner, "unit": unit, "plan": plan})
        session.emit_paths[owner.name] = plan.markdown_path if plan else target.output_dir / home / "AGENTS.md"
    try:
        selected = select_homes(((home, owner) for home, owner, _, _ in owners), selectors)
    except DoctrineError:
        if failures:
            raise failures[0][1]
        raise
    for home, failure in failures:
        if whole or is_level(home, selected):
            raise failure
        print(failure, file=sys.stderr)
    session.rule_agents = None if whole else [
        (data["unit"], data["owner"]) for home, data in homes.items()
        if home in selected and not isinstance(data["owner"], model.Team)
    ]
    needed = {home for home in homes if is_level(home, selected)}
    for home, owner, unit, plan in owners:
        if home in needed and homes[home]["owner"] is not owner:
            raise compile_error(
                code="E607", summary="Two homes, one path",
                detail=f"`{homes[home]['owner'].name}` and `{owner.name}` both land at `{home}`.",
            )
    homes = {home: data for home, data in homes.items() if home in needed}
    for home, data in list(homes.items()):
        owner, unit, plan = data["owner"], data["unit"], data["plan"]
        session.evaluate_rules = evaluate_rules and home in selected
        session.value_home = home
        data, content, parts = compile_home(target, session, context, home, owner, unit, plan)
        homes[home] = data
        files.update(content)
        compiled[owner.name] = data["contract_compiled"]
        for companion, content in parts.items():
            collected = companions.setdefault(companion, [])
            collected.extend([
                part for part in content
                if not companion.startswith("_details/") or part not in collected
            ])
    session.value_home = None
    for home, data in homes.items():
        owner = data["owner"]
        if (
            home in selected
            and isinstance(owner, model.Team)
            and team_members(context, owner, unit=data["unit"])
        ):
            path = str(PurePosixPath(home) / "TEAM.contract.json")
            contract = team_contract(context, owner, unit=data["unit"], compiled_members={
                name: map_text(value, lambda text: render_file_refs(text, target.output_dir / home, target.project_config))
                for name, value in compiled.items()})
            files[path] = (json.dumps(contract, indent=2) + "\n").encode()
            data["files"].append(path)
    files.update(companion_files(homes, companions, target))
    declarations = [(unit, decl) for unit in session.units()
                    for decl in unit.declarations.files_by_name.values()]
    referenced = {project_file_path(target.project_config, ref[2]) for data in homes.values() for ref, _ in data["file_refs"]}
    for unit, decl in declarations:
        path = project_file_path(target.project_config, decl.path)
        if (decl.body is None and (path in referenced or whole and session.flow_for_unit(unit) is session.root_flow)
                and not path.is_file()):
            raise compile_error(code="E652", summary="Missing Markdown source",
                detail=f"`{decl.name}` names `{decl.path}`, which doesn't exist.",
                path=unit.prompt_file.source_path, source_span=decl.source_span)
    written, links = compile_shared_files(target, context, files, declarations, referenced, whole)
    for data in homes.values():
        data["shared_files"] = [str(Path(ref[2]).relative_to(target.output_dir))
            for ref, _ in data["file_refs"] if Path(ref[2]).is_relative_to(target.output_dir)
            and str(Path(ref[2]).relative_to(target.output_dir)) in written]
        for path in data["shared_files"]:
            for child in links[path]:
                if child in written and child not in data["shared_files"]:
                    data["shared_files"].append(child)
    return homes, files, selected, whole


def matches_home(home, name, selector):
    return name == selector or home == selector or home.startswith(selector + "/")


def select_homes(owners, selectors):
    owners = tuple(owners)
    selected = set()
    for selector in selectors or ["."]:
        matches = {home for home, owner in owners
                   if selector == "." or matches_home(home, owner.name, selector)}
        if not matches:
            raise compile_error(
                code="E640", summary="No home matches", detail=f"`{selector}` matches no home."
            )
        selected.update(matches)
    return selected


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
    old = path.read_bytes().decode(errors="replace")
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


def needed_files(root, homes, files, selected, wanted):
    for home in sorted(selected):
        levels = loaded_levels(homes, home)
        for level, _ in levels:
            if level in selected:
                continue
            for filename in ("AGENTS.md", "CLAUDE.md"):
                path = str(PurePosixPath(level) / filename)
                disk = root / path
                if path in files or disk.is_file() and disk.read_bytes().startswith(b"<!-- doctrine sha256="):
                    state = file_state(disk, files.get(path))
                    if state != "unchanged":
                        yield home, "loads", path, state
        for path in dict.fromkeys(path for _, data in levels for path in data["pointers"]):
            if path not in wanted:
                disk = root / path
                state = ("missing" if not disk.is_file() else "unchanged"
                         if path.startswith("_details/") else file_state(disk, files[path]))
                if state != "unchanged":
                    yield home, "links to", path, state
        for path in dict.fromkeys(path for _, data in levels for path in data["shared_files"]):
            state = file_state(root / path, files[path])
            if state != "unchanged":
                yield home, "links to", path, state


def build_homes(
    target, homes, files, *, selected, whole, output_dir=None, read_only=False, force=False
):
    root = output_dir or target.output_dir
    wanted = set(files) if whole else {path for home in selected for path in homes[home]["files"]}
    obsolete = set()
    record = root / "HOMES.contract.json"
    if whole:
        if record.exists():
            try:
                obsolete = {
                    name for name in set(json.loads(record.read_bytes())["files"]) - set(files)
                    if (root / name).exists() or (root / name).is_symlink()
                }
            except (json.JSONDecodeError, KeyError):
                pass
        files = {
            **files,
            "HOMES.contract.json": (
                json.dumps({"format_version": 1, "files": sorted(files)}, indent=2) + "\n"
            ).encode(),
        }
        wanted.add("HOMES.contract.json")
    states = {name: file_state(root / name, files.get(name)) for name in sorted(wanted | obsolete)}
    if not whole:
        needed = needed_files(root, homes, files, selected, wanted)
        if not read_only:
            for home, action, path, state in needed:
                detail = "missing" if state == "missing" else "out of date"
                raise compile_error(
                    code="E635", summary="Home needs a full build",
                    detail=f"`{home}` {action} `{path}`, which is {detail}.",
                    hints=("Run `doctrine build .`, then build this home.",),
                )
    if not read_only and not force:
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
    }
    if read_only:
        result["paths"] = [
            {"path": name, "state": "obsolete" if name in obsolete else state}
            for name, state in states.items()
            if name in obsolete or state != "unchanged"
        ]
        if not whole:
            seen = {item["path"] for item in result["paths"]}
            for _, _, path, state in needed:
                if path not in seen:
                    result["paths"].append({"path": path, "state": state})
                    seen.add(path)
    for name, state in states.items():
        if read_only:
            continue
        if name in obsolete:
            (root / name).unlink()
            result["removed"].append(name)
        elif state == "unchanged":
            result["unchanged"].append(name)
        else:
            atomic_write(root / name, files[name])
            result["written"].append(name)
    return result
