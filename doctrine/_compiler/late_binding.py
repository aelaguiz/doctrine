from __future__ import annotations

import re
from dataclasses import fields, is_dataclass, replace
from pathlib import PurePosixPath

from doctrine import model
from doctrine._compiler.details import validate_shared_details
from doctrine._compiler.constants import LATE_ROOT
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.teams import find_home_team, team_members, home_value_sources
from doctrine._compiler.types import CompiledCodeBlock
from doctrine._compiler.markdown_links import rebase_markdown


def map_text(value, substitute, markdown=None):
    if isinstance(value, str):
        return (markdown(value) if markdown else value) if isinstance(value, model.MarkdownProse) else substitute(value)
    if isinstance(value, model.NameRef):
        return value
    if isinstance(value, CompiledCodeBlock):
        return replace(value, title=map_text(value.title, substitute, markdown))
    if isinstance(value, tuple):
        return tuple(map_text(item, substitute, markdown) for item in value)
    if is_dataclass(value):
        return replace(value, **{
            field.name: map_text(getattr(value, field.name), substitute, markdown)
            for field in fields(value) if field.name not in {"origin", "drops"}
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


def value_reading_sites(context, root, key):
    token = re.compile(r"\{\{\s*" + root + ":" + key + r"\s*\}\}")
    readings = []
    for flow in context.session._flow_cache.values():
        for unit in flow.units_by_path.values():
            path = unit.prompt_file.source_path
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if token.search(line) and (path, number) not in readings:
                    readings.append((path, number))
    return readings


def bind_home(context, compiled, agent, *, unit):
    validate_shared_details(compiled)
    team_match = find_home_team(context, agent, unit=unit)
    team_unit, team = team_match if team_match else (None, None)
    missing = []
    stack = []
    def no_owner(root, key, why):
        raise compile_error(
            code="E602", summary="Value has no owner here",
            detail=f"`{{{{{root}:{key}}}}}` can't be read here: {why}.",
            path=(agent.scope_unit or unit).prompt_file.source_path if isinstance(agent, model.Member) else unit.prompt_file.source_path,
            source_span=agent.source_span)

    def values(decl, owner):
        if isinstance(decl, model.Member):
            owner = decl.scope_unit or owner
        return {
            key: (text, owner, span)
            for field in decl.fields if isinstance(field, model.ValuesField)
            for key, text, span in field.items
        }

    agent_sources, team_sources = home_value_sources(context, agent, unit)
    agent_values = [values(decl, owner) for decl, owner in agent_sources]
    team_values = [values(decl, owner) for decl, owner in team_sources]

    def read(root, key):
        if root == "team" and team is None:
            no_owner(root, key, "this agent is outside any team")
        owner = agent if root == "agent" else team
        if key in {"key", "title"}:
            if key == "key":
                return owner.key if isinstance(owner, model.Member) else owner.name
            return substitute(context._display_readable_decl(owner))
        if key in {"home", "folder"}:
            if team is None:
                no_owner(root, key, "this agent is outside any team")
            home = team.home
            if root == "agent" and isinstance(agent, model.Member):
                home = str(PurePosixPath(home) / agent.key.replace("_", "-"))
            return home if key == "home" else home.rsplit("/", 1)[-1]
        if root == "team" and key in {"members", "others"}:
            if key == "others" and isinstance(agent, model.Team):
                no_owner(root, key, "a team's own file has no others")
            names = [
                bind_home(context, member.title, member, unit=team_unit)
                for member in team_members(context, team, unit=team_unit)
                if key == "members" or member.name != agent.name
            ]
            if names:
                return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else names[0]
        identity = (root, key)
        if identity in stack:
            cycle = " -> ".join(item[1] for item in [*stack[stack.index(identity):], identity])
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
        environments = agent_values if root == "agent" else team_values
        for environment in environments:
            if key in environment:
                _, source, span = environment[key]
                context.session.value_reads.add((source.prompt_file.source_path, span.line))
        for environment in environments:
            if key in environment:
                text, source, span = environment[key]
                text = context._interpolate_authored_prose_string(
                    text, unit=source,
                    owner_label=f"value {key}", surface_label="value text")
                stack.append(identity)
                result = substitute(text)
                stack.pop()
                return result
        if identity not in missing:
            missing.append(identity)
        return ""

    def substitute(text):
        return type(text)(LATE_ROOT.sub(lambda match: read(match[1], match[2]), text))

    output = context.session.emit_paths.get(agent.name)
    result = map_text(compiled, substitute, (lambda text: rebase_markdown(text, output.parent)) if output else None)
    if missing:
        home = agent.name
        if team is not None:
            home = str(PurePosixPath(team.home) / agent.key.replace("_", "-")) if isinstance(agent, model.Member) else team.home
        lines = [f"Home `{home}` reads values nothing fills:"]
        for root, key in missing:
            lines.extend(f"- `{root}:{key}` at {path}:{line}"
                         for path, line in value_reading_sites(context, root, key))
        raise compile_error(code="E601", summary="Unfilled value", detail="\n".join(lines),
            path=unit.prompt_file.source_path, source_span=agent.source_span)
    return result
