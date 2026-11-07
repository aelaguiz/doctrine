from __future__ import annotations

from collections import deque

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.source_graph import build_home_deps, declaration_match
from doctrine.runtime_load import loaded_levels


def validate_load_rules(context, homes):
    build_home_deps(context, homes)
    for flow in tuple(context.session._flow_cache.values()):
        for rule in flow.rules_by_name.values():
            rule_unit = flow.declaration_owner_units_by_id[id(rule)]
            for assertion in rule.assertions:
                if not isinstance(
                    assertion, (model.RequiresLoadAssertion, model.ForbidsLoadAssertion)
                ):
                    continue
                match = declaration_match(context, assertion.target, rule_unit)
                if match is None:
                    context._raise_rule_unknown_assertion_target(
                        rule=rule, rule_unit=rule_unit, source_span=assertion.source_span,
                        target_name=".".join((
                            *assertion.target.module_parts, assertion.target.declaration_name
                        )),
                    )
                unit, declaration = match
                name_unit = declaration.team_unit if isinstance(declaration, model.Member) else unit
                target = ".".join((*name_unit.module_parts, declaration.name))
                for home, data in homes.items():
                    if context.session.flow_for_unit(data["unit"]) is not flow:
                        continue
                    if not context._agent_matches_rule_scope(
                        data["owner"], agent_unit=data["unit"], rule=rule, flow=flow
                    ):
                        continue
                    levels = loaded_levels(homes, home)
                    present = any(
                        entry.always_on and entry.origin == target
                        for _, level in levels for entry in level["map"].entries
                    )
                    required = isinstance(assertion, model.RequiresLoadAssertion)
                    if present == required:
                        continue
                    agent = data["owner"].name
                    detail = f"{agent} must {'load' if required else 'not load'} {target}."
                    if not required:
                        detail += "\n- It arrives by: " + " -> ".join(
                            arrival_path(levels, data, target)
                        )
                    raise compile_error(
                        code="RULE006" if required else "RULE007",
                        summary="Requires load" if required else "Forbids load", detail=detail,
                    )


def arrival_path(levels, home, target):
    graph, queue = {}, deque()
    for level in [home, *(level for _, level in levels if level is not home)]:
        graph.update(level["deps_graph"])
        queue.append((next(iter(level["deps_graph"])),))
    seen = set()
    while queue:
        chain = queue.popleft()
        if chain[-1] == target:
            return chain
        if chain[-1] in seen:
            continue
        seen.add(chain[-1])
        queue.extend((*chain, name) for name in sorted(graph[chain[-1]][2]))
