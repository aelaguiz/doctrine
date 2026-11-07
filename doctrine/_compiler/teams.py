from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


def _message_target(decl):
    return next((item for item in decl.items if isinstance(item, model.RecordScalar)
                 and item.key == "target" and isinstance(item.value, model.NameRef)
                 and not item.value.module_parts and item.value.declaration_name == "Message"), None)


FACT_KEYS = frozenset({"key", "title", "home", "folder", "members", "others"})


def member_home(team, member):
    return str(PurePosixPath(team.home) / member.key.replace("_", "-"))


def resolve_message_recipient(context, ref, *, unit):
    if context._ref_exists_in_registry(ref, unit=unit, registry_name="teams_by_name"):
        return context._resolve_decl_ref(ref, unit=unit, registry_name="teams_by_name",
                                         missing_label="team declaration")
    return context._resolve_agent_ref(ref, unit=unit)


def team_members(context, team, *, unit):
    expanded, _ = context._expand_agent_patches(team, unit=unit)
    return tuple(
        replace(field, name=f"{team.name}.{field.key}",
                scope_unit=field.scope_unit or unit, team_unit=unit)
        for field in expanded.fields if isinstance(field, model.Member)
    )


def find_team_member(context, unit, name):
    if "." in name:
        team_name, key = name.rsplit(".", 1)
        flow = context.session.flow_for_unit(unit)
        team = flow.teams_by_name.get(team_name)
        if team is not None and not team.abstract:
            owner = flow.declaration_owner_units_by_id[id(team)]
            return next(((owner, member) for member in team_members(context, team, unit=owner)
                         if member.key == key), None)
    return None


def find_home_team(context, agent, *, unit):
    if isinstance(agent, model.Team):
        name, flow = agent.name, context.session.flow_for_unit(unit)
    elif isinstance(agent, model.Member):
        name = agent.name.rsplit(".", 1)[0]
        flow = context.session.flow_for_unit(agent.team_unit)
    else:
        return None
    team = flow.teams_by_name[name]
    return flow.declaration_owner_units_by_id[id(team)], team


def agent_parents(context, decl, owner):
    while decl.parent_ref is not None:
        owner, decl = context._resolve_parent_agent_decl(decl, unit=owner)
        yield decl, owner


def home_value_sources(context, agent, unit):
    owner = agent.scope_unit or unit if isinstance(agent, model.Member) else unit
    agent_sources, team_sources = [(agent, owner)], []
    match = None if agent.abstract else find_home_team(context, agent, unit=unit)
    if match is not None:
        team_unit, team = match
        team_sources.append((team, team_unit))
        flow = context.session.flow_for_unit(team_unit)
        outer = [
            candidate for candidate in flow.teams_by_name.values()
            if not candidate.abstract
            and PurePosixPath(candidate.home) in PurePosixPath(team.home).parents
        ]
        team_sources.extend(
            (candidate, flow.declaration_owner_units_by_id[id(candidate)])
            for candidate in sorted(
                outer, key=lambda item: len(PurePosixPath(item.home).parts), reverse=True
            )
        )
        team_sources.extend(agent_parents(context, team, team_unit))
    agent_sources.extend(team_sources)
    agent_sources.extend(agent_parents(context, agent, owner))
    return agent_sources, team_sources


def validate_team(agent, *, unit):
    if isinstance(agent, model.Team):
        def error(detail, item):
            return compile_error(
                code="E606", summary="Invalid team", detail=detail,
                path=unit.prompt_file.source_path, source_span=item.source_span,
            )

        if agent.abstract and agent.home is not None:
            raise error(f"Abstract team `{agent.name}` can't have `home:`.", agent)
        if not agent.abstract and agent.home is None:
            raise error(f"Team `{agent.name}` needs `home:`.", agent)
        if agent.home is not None and (
            PurePosixPath(agent.home).is_absolute()
            or ".." in PurePosixPath(agent.home).parts
            or str(PurePosixPath(agent.home)) != agent.home
        ):
            raise error(
                f'`home: "{agent.home}"` must be a plain relative path, such as `pods/growth`.',
                agent,
            )
        keys = set()
        for field in agent.fields:
            key = field[0] if isinstance(field, tuple) else "role" if isinstance(field, (model.RoleScalar, model.RoleBlock)) else getattr(field, "key", None)
            if (isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotAbstract,
                                   model.AuthoredSlotOverride)) and key in {
                "inputs", "outputs", "analysis", "decision", "skills", "review", "final_output", "selectors"}):
                raise error(f"Team `{agent.name}` can't hold `{key}`. A team takes `role`, `values`, `budget`, slots, and members.", field)
            if key is not None:
                if key in keys:
                    raise error(f"Team `{agent.name}` uses key `{key}` twice.", agent if isinstance(field, tuple) else field)
                keys.add(key)
        agent = replace(agent, fields=tuple(field for field in agent.fields if not isinstance(field, tuple)))
    return agent


def validate_values(agent, *, unit):
    keys = set()
    for field in agent.fields:
        if isinstance(field, model.ValuesField):
            for key, text, span in field.items:
                if key in FACT_KEYS:
                    raise compile_error(code="E604", summary="Value sets a fact",
                        detail=f"`values:` can't set `{key}`. The compiler supplies it.",
                        path=unit.prompt_file.source_path, source_span=span)
                if key in keys:
                    raise compile_error(code="E608", summary="Value set twice",
                        detail=f"`values:` sets `{key}` twice.",
                        path=unit.prompt_file.source_path, source_span=span)
                keys.add(key)


def order_team_fields(agent, fields, *, keys, parent_fields, unit):
    if isinstance(agent, (model.Member, model.Team)):
        roles = [field for field in fields if isinstance(field, (model.RoleScalar, model.RoleBlock))]
        fields = roles + [field for field in fields if not isinstance(field, (model.RoleScalar, model.RoleBlock))]
    if isinstance(agent, model.Team):
        inherited_members = [key for key in keys if isinstance(parent_fields.get(key, [None])[0], model.Member)]
        own_members = {field.key: field for field in fields if isinstance(field, model.Member)}
        for field in agent.fields:
            if isinstance(field, model.Member) and field.override and field.key not in keys:
                raise compile_error(
                    code="E001", summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined authored slot in agent {agent.name}: {field.key}",
                    path=unit.prompt_file.source_path, source_span=field.source_span,
                )
            collision = isinstance(field, model.Member) and field.key in keys and (
                not field.override or field.key not in inherited_members
            )
            collision |= isinstance(field, (
                model.AuthoredSlotField, model.AuthoredSlotAbstract, model.AuthoredSlotOverride,
            )) and field.key in inherited_members
            if collision:
                raise compile_error(
                    code="E606", summary="Invalid team",
                    detail=f"Team `{agent.name}` uses key `{field.key}` twice.",
                    path=unit.prompt_file.source_path, source_span=field.source_span,
                )
        order = [key for key in inherited_members if key in own_members] + [key for key in own_members if key not in inherited_members]
        fields = [field for field in fields if not isinstance(field, model.Member)] + [
            replace(own_members[key], scope_unit=own_members[key].scope_unit or unit) for key in order
        ]
    return fields


def team_contract(context, team, *, unit, compiled_members):
    members = team_members(context, team, unit=unit)
    return {
        "format_version": 1, "language_version": "6.0",
        "team": {"key": team.name, "title": team.title, "home": team.home},
        "members": [
            {"key": member.key, "agent": member.name, "title": member.title,
             "home": member_home(team, member),
             "parent": None if member.parent_ref is None else ".".join((*member.parent_ref.module_parts, member.parent_ref.declaration_name)),
             "sections": [field.title for field in compiled_members[member.name].fields
                          if not isinstance(field, model.RoleScalar) and field.title]}
            for member in members
        ],
    }
