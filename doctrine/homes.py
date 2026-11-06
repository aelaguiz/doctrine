from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.session import CompilationSession
from doctrine._compiler.teams import team_members, team_contract
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown
from doctrine.details import split_details, render_companion
from doctrine.emit_docs import _runtime_emit_roots_for_target, _build_runtime_emit_plan, _build_previous_turn_contexts, runtime_files


HEADER = re.compile(r'^<!-- doctrine sha256=([a-f0-9]{12}) source=.* -->\n\n')


def with_header(text, source):
    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
    return f'<!-- doctrine sha256={digest} source={source}. Do not edit. Run: doctrine where "<words>" -->\n\n{text}'


def compile_homes(target, *, evaluate_rules=False):
    session = CompilationSession(parse_file(target.entrypoint), project_config=target.project_config,
                                 evaluate_rules=evaluate_rules)
    context = CompilationContext(session)
    flow = session.root_flow
    homes, files, compiled = {}, {}, {}
    companions = {}
    owners = []
    plans = tuple(_build_runtime_emit_plan(root, target=target, output_root=target.output_dir,
        provider_root=session.provided_prompt_root_for(root.unit.prompt_root))
        for root in _runtime_emit_roots_for_target(session, target=target))
    session.emit_paths = {plan.root.agent_name: plan.markdown_path for plan in plans}
    roots = tuple((plan.root.unit, plan.root.agent_name) for plan in plans)
    ordinary = session.compile_agents_from_units(roots, previous_turn_contexts=_build_previous_turn_contexts(session, agent_roots=roots))
    for plan, result in zip(plans, ordinary, strict=True):
        unit = plan.root.unit
        owner = session.flow_for_unit(unit).agents_by_name[plan.root.agent_name]
        home = plan.markdown_path.parent.relative_to(target.output_dir).as_posix()
        owners.append((home, owner, unit, result, plan))
    for team in flow.teams_by_name.values():
        if not team.abstract:
            unit = flow.declaration_owner_units_by_id[id(team)]
            owners.append((team.home, team, unit, None, None))
            owners.extend((str(PurePosixPath(team.home) / member.key.replace("_", "-")), member, unit, None, None)
                          for member in team_members(context, team, unit=unit))
    for home, owner, unit, result, plan in owners:
        if home in homes:
            raise compile_error(code="E607", summary="Two homes, one path",
                                detail=f"`{homes[home]['owner'].name}` and `{owner.name}` both land at `{home}`.")
        session.emit_paths[owner.name] = target.output_dir / home / "AGENTS.md"
        if plan is None:
            result = session.compile_agent(owner.name)
        result, parts, pointers = split_details(result, home)
        for companion, content in parts.items():
            companions.setdefault(companion, []).extend(content if not companion.startswith("_details/") else [part for part in content if part not in companions.get(companion, [])])
        compiled[owner.name] = result
        text = render_markdown(result)
        if pointers:
            text = text.rstrip() + "\n\nFuller cases, under the same headings: " + ", ".join(f"[{path if path.startswith('_details/') else 'DETAILS.md'}]({os.path.relpath(path, home)})" for path in pointers) + ".\n"
        source_unit = owner.scope_unit or unit if isinstance(owner, model.Member) else unit
        source = source_unit.prompt_file.source_path.relative_to(target.project_config.config_dir).as_posix()
        paths = []
        if plan is not None:
            ordinary_files = runtime_files(plan, result, target)
            ordinary_files[plan.markdown_path] = text.encode()
            for path, content in ordinary_files.items():
                name = path.relative_to(target.output_dir).as_posix()
                files[name] = content
                paths.append(name)
        elif text.strip():
            runtimes = target.runtimes or ("codex",)
            filename = "CLAUDE.md" if runtimes == ("claude",) else "AGENTS.md"
            path = str(PurePosixPath(home) / filename)
            files[path] = with_header(text, source).encode()
            paths.append(path)
            if "claude" in runtimes and "codex" in runtimes:
                link = str(PurePosixPath(home) / "CLAUDE.md")
                files[link] = Path("AGENTS.md")
                paths.append(link)
        budget_fields = [field for field in owner.fields if isinstance(field, model.BudgetField)]
        budget_owner, budget_unit = owner, unit
        while isinstance(budget_owner, model.Team) and budget_owner.parent_ref:
            budget_unit, budget_owner = context._resolve_parent_agent_decl(budget_owner, unit=budget_unit)
            budget_fields.extend(field for field in budget_owner.fields if isinstance(field, model.BudgetField))
        homes[home] = {"owner": owner, "unit": unit, "compiled": result, "files": paths, "pointers": pointers, "budgets": budget_fields}
    for home, data in homes.items():
        owner = data["owner"]
        if isinstance(owner, model.Team) and team_members(context, owner, unit=data["unit"]):
            path = str(PurePosixPath(home) / "TEAM.contract.json")
            files[path] = (json.dumps(team_contract(context, owner, unit=data["unit"], compiled_members=compiled), indent=2) + "\n").encode()
            data["files"].append(path)
    for path, parts in companions.items():
        if path.startswith("_details/"):
            parts.sort(key=lambda part: int(part[1].origin[2].rsplit(":", 1)[1]))
        source = parts[0][1].origin[2].rsplit(":", 1)[0]
        text = render_companion(parts)
        owner = next((data["owner"] for home, data in homes.items() if str(PurePosixPath(home) / "DETAILS.md") == path), None)
        files[path] = (with_header(text, source) if owner is None or isinstance(owner, (model.Team, model.Member)) else text).encode()
        for home, data in homes.items():
            if str(PurePosixPath(home) / "DETAILS.md") == path:
                data["files"].append(path)
    return homes, files


def select_homes(homes, selectors):
    selected = set()
    for selector in selectors or ["."]:
        matches = {home for home, data in homes.items()
                   if selector == "." or data["owner"].name == selector
                   or home == selector or home.startswith(selector + "/")}
        if not matches:
            raise compile_error(code="E640", summary="No home matches", detail=f"`{selector}` matches no home.")
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
    if path.suffix == ".md" and (fresh is None or isinstance(fresh, Path) or fresh.startswith(b"<!-- doctrine sha256=")):
        text = content.decode()
        match = HEADER.match(text)
        if match is None or hashlib.sha256(text[match.end():].encode()).hexdigest()[:12] != match[1]:
            return "edited"
    return "unchanged" if content == fresh else "stale"


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent)
    if isinstance(content, Path):
        os.close(descriptor)
        os.unlink(temporary)
        os.symlink(str(content), temporary)
    else:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
    os.replace(temporary, path)


def build_homes(target, homes, files, *, selectors=(), output_dir=None, check=False, force=False):
    root = output_dir or target.output_dir
    selected = select_homes(homes, selectors)
    whole = not selectors or "." in selectors
    wanted = set(files) if whole else {path for home in selected for path in homes[home]["files"]}
    record = root / "HOMES.contract.json"
    obsolete = set(json.loads(record.read_bytes())["files"]) - set(files) if whole and record.exists() else set()
    if whole:
        files = {**files, "HOMES.contract.json": (json.dumps({"format_version": 1, "files": sorted(files)}, indent=2) + "\n").encode()}
        wanted.add("HOMES.contract.json")
    states = {name: file_state(root / name, files.get(name)) for name in sorted(wanted | obsolete)}
    if not check and not force:
        for name, state in states.items():
            if state == "edited":
                path = root / name
                if path.is_symlink():
                    detail = f"`{name}` is a link Doctrine didn't write."
                elif HEADER.match(path.read_text()) is None:
                    detail = f"`{name}` was written by hand."
                else:
                    detail = f"`{name}` was edited by hand."
                    if name in files and isinstance(files[name], bytes):
                        old_sections = {section.split("\n", 1)[0][3:]: section for section in re.split(r"(?m)(?=^## )", path.read_text()) if section.startswith("## ")}
                        fresh_sections = {section.split("\n", 1)[0][3:]: section for section in re.split(r"(?m)(?=^## )", files[name].decode()) if section.startswith("## ")}
                        for data in homes.values():
                            if name in data["files"]:
                                for section in data["compiled"].fields:
                                    if not isinstance(section, model.RoleScalar) and section.origin and old_sections.get(section.title) != fresh_sections.get(section.title):
                                        detail += f"\n- {section.title}: {section.origin[0]} at {section.origin[2]}"
                raise compile_error(code="E634", summary="Hand edit in a compiled file", detail=detail,
                    hints=("Move the edit to its source, then build. `--force` overwrites it.",))
    stale_levels = []
    if not whole:
        for home in selected:
            stale_levels.extend(path for path in homes[home]["pointers"] if path.startswith("_details/") and file_state(root / path, files[path]) != "unchanged")
            for level in PurePosixPath(home).parents:
                for filename in ("AGENTS.md", "CLAUDE.md"):
                    path = str(level / filename)
                    if path in files and file_state(root / path, files[path]) != "unchanged" or path not in files and (root / path).exists():
                        stale_levels.append(path)
    result = {"format_version": 1, "written": [], "unchanged": [], "removed": [], "stale_levels": sorted(set(stale_levels))}
    for name, state in states.items():
        if check:
            if name in obsolete:
                print(f"obsolete {name}")
            elif state != "unchanged":
                print(f"{state} {name}")
        elif name in obsolete:
            if (root / name).exists() or (root / name).is_symlink():
                (root / name).unlink()
                result["removed"].append(name)
        elif state == "unchanged":
            result["unchanged"].append(name)
        else:
            atomic_write(root / name, files[name])
            result["written"].append(name)
    return selected, result, any(state != "unchanged" or name in obsolete for name, state in states.items())
