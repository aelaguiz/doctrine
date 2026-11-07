from __future__ import annotations

from collections import deque

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.source_graph import declaration_match, dependency_graph
from doctrine._compiler.teams import home_value_sources
from doctrine.runtime_load import loaded_levels


def validate_load_rules(context, homes):
    for flow in tuple(context.session._flow_cache.values()):
        for rule in flow.rules_by_name.values():
            rule_unit = flow.declaration_owner_units_by_id[id(rule)]
            for assertion in rule.assertions:
                if not isinstance(assertion, (model.RequiresLoadAssertion, model.ForbidsLoadAssertion)):
                    continue
                match = declaration_match(context, assertion.target, rule_unit)
                if match is None:
                    context._raise_rule_unknown_assertion_target(
                        rule=rule, rule_unit=rule_unit, source_span=assertion.source_span,
                        target_name=".".join((*assertion.target.module_parts, assertion.target.declaration_name)),
                    )
                unit, declaration = match
                target = ".".join((*unit.module_parts, declaration.name))
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
                        graph = {}
                        queue = deque()
                        for level in [data, *(level for _, level in levels if level is not data)]:
                            sources, team_sources = home_value_sources(context, level["owner"], level["unit"])
                            graph.update(dependency_graph(context, [sources[0], *team_sources]))
                            owner, source_unit = sources[0]
                            queue.append((".".join((*source_unit.module_parts, owner.name)),))
                        seen = set()
                        while queue:
                            chain = queue.popleft()
                            if chain[-1] == target:
                                detail += "\n- It arrives by: " + " -> ".join(chain)
                                break
                            if chain[-1] in seen:
                                continue
                            seen.add(chain[-1])
                            queue.extend((*chain, name) for name in sorted(graph[chain[-1]][2]))
                    raise compile_error(
                        code="RULE006" if required else "RULE007",
                        summary="Requires load" if required else "Forbids load", detail=detail,
                    )
