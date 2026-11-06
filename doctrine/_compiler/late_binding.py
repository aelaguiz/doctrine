from __future__ import annotations

import re
from dataclasses import fields, is_dataclass, replace
from pathlib import PurePosixPath

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.teams import find_home_team, team_members
from doctrine._compiler.types import CompiledCodeBlock


LATE_ROOT = re.compile(r"\{\{\s*(agent|team):([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
FACT_KEYS = frozenset({"key", "title", "home", "folder", "members", "others"})


def map_text(value, substitute):
    if isinstance(value, str):
        return value if hasattr(value, "markdown_path") else substitute(value)
    if isinstance(value, model.NameRef):
        return value
    if isinstance(value, CompiledCodeBlock):
        return replace(value, title=map_text(value.title, substitute))
    if isinstance(value, tuple):
        return tuple(map_text(item, substitute) for item in value)
    if isinstance(value, dict):
        return {key: map_text(item, substitute) for key, item in value.items()}
    if is_dataclass(value):
        return replace(value, **{
            field.name: map_text(getattr(value, field.name), substitute)
            for field in fields(value)
        })
    return value


def reject_late_roots(value, *, unit, why):
    def reject(text):
        match = LATE_ROOT.search(text)
        if match is not None:
            raise compile_error(
                code="E602", summary="Value has no owner here",
                detail=f"`{{{{{match[1]}:{match[2]}}}}}` can't be read here: {why}.",
                path=unit.prompt_file.source_path)
        return text
    map_text(value, reject)


def bind_home(context, compiled, agent, *, unit):
    team_match = find_home_team(context, agent, unit=unit)
    team_unit, team = team_match if team_match else (None, None)
    missing = {}
    stack = []
    sources = {
        source.prompt_file.source_path: source
        for flow in context.session._flow_cache.values()
        for source in flow.units_by_path.values()
    }

    def sites(text, root, key):
        token = re.compile(r"\{\{\s*" + root + ":" + key + r"\s*\}\}")
        readings = []
        for path, source in sources.items():
            records = source.prompt_file.string_sites
            if id(text) in records and token.search(records[id(text)][1]):
                components = [records[id(text)]]
            else:
                components = [record for record in records.values() if record[0] and record[0] in text]
            for _, raw, span in components:
                for match in token.finditer(raw):
                    site = (path, span.line + raw[:match.start()].count("\n"))
                    if site not in readings:
                        readings.append(site)
        return readings

    def no_owner(text, root, key, why):
        readings = sites(text, root, key)
        raise compile_error(
            code="E602", summary="Value has no owner here",
            detail=f"`{{{{{root}:{key}}}}}` can't be read here: {why}.",
            path=readings[0][0] if readings else unit.prompt_file.source_path,
            source_span=model.SourceSpan(readings[0][1], 1) if readings else agent.source_span)

    def values(decl, owner):
        if isinstance(decl, model.Member):
            owner = decl.scope_unit or owner
        return {
            key: (text, owner, span)
            for field in decl.fields if isinstance(field, model.ValuesField)
            for key, text, span in field.items
        }

    def parents(decl, owner):
        result = []
        while decl.parent_ref is not None:
            owner, decl = context._resolve_parent_agent_decl(decl, unit=owner)
            result.append(values(decl, owner))
        return result

    agent_values = [values(agent, unit)]
    team_values = []
    if team is not None:
        team_values.append(values(team, team_unit))
        outer = []
        flow = context.session.flow_for_unit(team_unit)
        home = PurePosixPath(team.home)
        for candidate in flow.teams_by_name.values():
            if candidate.abstract or candidate is team:
                continue
            path = PurePosixPath(candidate.home)
            if path in home.parents:
                outer.append(candidate)
        for candidate in sorted(outer, key=lambda item: len(PurePosixPath(item.home).parts), reverse=True):
            owner = flow.declaration_owner_units_by_id[id(candidate)]
            team_values.append(values(candidate, owner))
        team_values.extend(parents(team, team_unit))
    agent_values.extend(team_values)
    agent_values.extend(parents(agent, agent.scope_unit or unit if isinstance(agent, model.Member) else unit))

    def read(root, key, text):
        if root == "team" and team is None:
            no_owner(text, root, key, "this agent is outside any team")
        owner = agent if root == "agent" else team
        if key in {"key", "title"}:
            if key == "key":
                return owner.key if isinstance(owner, model.Member) else owner.name
            return substitute(context._display_readable_decl(owner))
        if key in {"home", "folder"}:
            if team is None:
                no_owner(text, root, key, "this agent is outside any team")
            home = team.home
            if root == "agent" and isinstance(agent, model.Member):
                home = str(PurePosixPath(home) / agent.key.replace("_", "-"))
            return home if key == "home" else home.rsplit("/", 1)[-1]
        if root == "team" and key in {"members", "others"}:
            if key == "others" and isinstance(agent, model.Team):
                no_owner(text, root, key, "a team's own file has no others")
            names = [
                bind_home(context, member.title, member, unit=team_unit)
                for member in team_members(context, team, unit=team_unit)
                if key == "members" or member.name != agent.name
            ]
            return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else "".join(names)
        identity = (root, key)
        if identity in stack:
            cycle = " -> ".join(item[1] for item in [*stack, identity])
            readings = [
                (source.prompt_file.source_path, span.line)
                for environment in (agent_values if root == "agent" else team_values)
                for name, (_, source, span) in environment.items() if name == key
            ]
            raise compile_error(
                code="E603", summary="Value cycle",
                detail=f"Values read each other: `{cycle}`",
                path=readings[0][0] if readings else unit.prompt_file.source_path,
                source_span=model.SourceSpan(readings[0][1], 1) if readings else agent.source_span)
        for environment in agent_values if root == "agent" else team_values:
            if key in environment:
                text, source, span = environment[key]
                text = context._interpolate_authored_prose_string(
                    text, unit=source,
                    owner_label=f"value {key}", surface_label="value text")
                stack.append(identity)
                result = substitute(text)
                stack.pop()
                return result
        readings = missing.setdefault(identity, [])
        readings.extend(site for site in sites(text, root, key) if site not in readings)
        return ""

    def substitute(text):
        return type(text)(LATE_ROOT.sub(lambda match: read(match[1], match[2], text), text))

    result = map_text(compiled, substitute)
    if missing:
        home = agent.name
        if team is not None:
            home = str(PurePosixPath(team.home) / agent.key.replace("_", "-")) if isinstance(agent, model.Member) else team.home
        lines = [f"Home `{home}` reads values nothing fills:"]
        for (root, key), readings in missing.items():
            lines.extend(f"- `{root}:{key}` at {path}:{line}" for path, line in readings)
        raise compile_error(code="E601", summary="Unfilled value", detail="\n".join(lines),
            path=unit.prompt_file.source_path, source_span=agent.source_span)
    return result
