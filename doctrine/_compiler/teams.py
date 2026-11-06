from __future__ import annotations

from dataclasses import replace

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


FACT_KEYS = frozenset({"key", "title", "home", "folder", "members", "others"})


def team_members(context, team, *, unit):
    expanded, _ = context._expand_agent_patches(team, unit=unit)
    return tuple(
        replace(field, name=f"{team.name}.{field.key}",
                scope_unit=field.scope_unit or unit, team_unit=unit)
        for field in expanded.fields if isinstance(field, model.Member)
    )


def find_home_team(context, agent, *, unit):
    if isinstance(agent, model.Team):
        return unit, agent
    if isinstance(agent, model.Member):
        name = agent.name.rsplit(".", 1)[0]
        flow = context.session.flow_for_unit(agent.team_unit)
        team = flow.teams_by_name[name]
        return flow.declaration_owner_units_by_id[id(team)], team
    return None


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
        if agent.home is not None and (agent.home.startswith("/") or ".." in agent.home.split("/") or agent.home.endswith("/")):
            raise error(f'`home: "{agent.home}"` must be a relative path with no `..` and no trailing `/`.', agent)
        keys = set()
        for field in agent.fields:
            key = "role" if isinstance(field, (model.RoleScalar, model.RoleBlock)) else getattr(field, "key", None)
            if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotAbstract, model.AuthoredSlotOverride)) and key in {"inputs", "outputs", "analysis", "decision", "skills", "review", "final_output", "selectors"}:
                raise error(f"Team `{agent.name}` can't hold `{key}`. A team takes `role`, `values`, `budget`, slots, and members.", field)
            if key is not None:
                if key in keys:
                    raise error(f"Team `{agent.name}` uses key `{key}` twice.", field)
                keys.add(key)


def validate_values(agent, *, unit):
    for field in agent.fields:
        if isinstance(field, model.ValuesField):
            for key, text, span in field.items:
                if key in FACT_KEYS:
                    raise compile_error(code="E604", summary="Value sets a fact",
                        detail=f"`values:` can't set `{key}`. The compiler supplies it.",
                        path=unit.prompt_file.source_path, source_span=span)


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
