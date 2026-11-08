from __future__ import annotations

import re
from dataclasses import replace

from doctrine import model
from doctrine._model.core import role_text
from doctrine._compiler.naming import map_model
from doctrine._compiler.constants import DETAILS_LINK, LATE_ROOT
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.teams import find_home_team, team_members, home_value_sources, member_home
from doctrine._compiler.types import CompiledCodeBlock, CompiledRawTextBlock
from doctrine._compiler.markdown_links import rebase_markdown


def map_text(value, substitute, markdown=None):
    def leaf(item):
        if isinstance(item, model.RoleScalar) and item.paragraphs:
            paragraphs = map_text(item.paragraphs, substitute, markdown)
            return replace(item, text=role_text(paragraphs), paragraphs=paragraphs)
        if isinstance(item, str):
            return (markdown(item) if markdown else item) if isinstance(item, model.MarkdownProse) else substitute(item)
        if isinstance(item, model.NameRef):
            return item
        if isinstance(item, CompiledCodeBlock):
            return replace(item, title=map_text(item.title, substitute, markdown))
    return map_model(value, leaf, {"origin", "drops"})


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


def reject_case_links(value, *, unit):
    def reject(text):
        if match := DETAILS_LINK.search(text):
            raise compile_error(code="E602", summary="Value has no owner here",
                detail=f"`{match[0]}` can't be read here: a case link belongs in text the agent always reads.",
                path=unit.prompt_file.source_path)
        return text
    def leaf(item):
        if isinstance(item, (CompiledCodeBlock, CompiledRawTextBlock)):
            return replace(item, title=map_text(item.title, reject))
        if isinstance(item, (model.ReadableCodeData, model.ReadableRawTextData)):
            return item
        if isinstance(item, str) and not isinstance(item, model.MarkdownProse):
            return reject(item)
        if isinstance(item, model.NameRef):
            return item
    map_model(value, leaf, {"origin", "drops"})


def value_reading_sites(context, root, key):
    token = re.compile(r"\{\{\s*" + root + ":" + key + r"\s*\}\}")
    readings = []
    for unit in context.session.units():
        path = unit.prompt_file.source_path
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if token.search(line) and (path, number) not in readings:
                readings.append((path, number))
    return readings


def bind_home(context, compiled, agent, *, unit, _stack=None):
    team_match = find_home_team(context, agent, unit=unit)
    team_unit, team = team_match if team_match else (None, None)
    missing = []
    stack = [] if _stack is None else _stack
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
        identity = (root, key, agent.name)
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
        stack.append(identity)
        try:
            return read_value(root, key)
        finally:
            stack.pop()

    def read_value(root, key):
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
                home = member_home(team, agent)
            return home if key == "home" else home.rsplit("/", 1)[-1]
        if root == "team" and key in {"members", "others"}:
            if key == "others" and isinstance(agent, model.Team):
                no_owner(root, key, "a team's own file has no others")
            names = [
                bind_home(context, member.title, member, unit=team_unit, _stack=stack)
                for member in team_members(context, team, unit=team_unit)
                if key == "members" or member.name != agent.name
            ]
            if names:
                return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else names[0]
        identity = (root, key)
        environments = agent_values if root == "agent" else team_values
        for environment in environments:
            if key in environment:
                _, source, span = environment[key]
                context.session.value_reads.add((source.prompt_file.source_path, span.line))
        for environment in environments:
            if key in environment:
                text, source, span = environment[key]
                if context.session.value_home is not None:
                    context.session.value_origins.add(
                        (source.prompt_file.source_path, span.line, context.session.value_home))
                text = context._interpolate_authored_prose_string(
                    text, unit=source,
                    owner_label=f"value {key}", surface_label="value text")
                return substitute(text)
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
            home = member_home(team, agent) if isinstance(agent, model.Member) else team.home
        lines = [f"Home `{home}` reads values nothing fills:"]
        for root, key in missing:
            lines.extend(f"- `{root}:{key}` at {path}:{line}"
                         for path, line in value_reading_sites(context, root, key))
        error = compile_error(code="E601", summary="Unfilled value", detail="\n".join(lines),
            path=unit.prompt_file.source_path, source_span=agent.source_span)
        error.missing_values = tuple(missing)
        raise error
    return result
