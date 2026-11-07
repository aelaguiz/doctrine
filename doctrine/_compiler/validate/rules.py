from __future__ import annotations

import fnmatch
from pathlib import Path, PurePosixPath
import glob
import re

from doctrine import model
from doctrine._compiler.source_graph import declaration_match
from doctrine._compiler.teams import team_members, find_home_team
from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import CompileError, IndexedUnit

class ValidateRulesMixin:
    """Evaluates top-level `rule` declarations against the current flow."""

    def _validate_all_rules_in_flow(self, flow) -> None:
        if not getattr(flow, "rules_by_name", None):
            return
        validated_key = (flow.prompt_root.resolve(), flow.flow_root.resolve())
        cache = getattr(self, "_rules_validated_flows", None)
        if cache is None:
            cache = set()
            self._rules_validated_flows = cache
        if validated_key in cache:
            return
        cache.add(validated_key)
        for rule in flow.rules_by_name.values():
            rule_unit = flow.declaration_owner_units_by_id[id(rule)]
            self._validate_one_rule(rule, flow=flow, rule_unit=rule_unit)

    def _validate_one_rule(
        self,
        rule: model.RuleDecl,
        *,
        flow,
        rule_unit: IndexedUnit,
    ) -> None:
        self._validate_rule_scope_targets(rule, flow=flow, rule_unit=rule_unit)
        self._validate_rule_assertion_targets(rule, flow=flow, rule_unit=rule_unit)

        agents = [(flow.declaration_owner_units_by_id[id(agent)], agent) for agent in flow.agents_by_name.values()]
        for team in flow.teams_by_name.values():
            if not team.abstract:
                owner = flow.declaration_owner_units_by_id[id(team)]
                agents.append((owner, team))
                agents.extend((owner, member) for member in team_members(self, team, unit=owner))
        for agent_unit, agent in agents:
            if not self._agent_matches_rule_scope(
                agent,
                agent_unit=agent_unit,
                rule=rule,
                flow=flow,
            ):
                continue
            for assertion in rule.assertions:
                self._evaluate_rule_assertion(
                    assertion,
                    agent=agent,
                    agent_unit=agent_unit,
                    rule=rule,
                    rule_unit=rule_unit,
                    flow=flow,
                )

    def _rule_agent_name(self, ref, *, flow):
        if ref.module_parts and ref.module_parts[-1] in flow.teams_by_name:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return ref.declaration_name

    def _validate_rule_scope_targets(
        self,
        rule: model.RuleDecl,
        *,
        flow,
        rule_unit: IndexedUnit,
    ) -> None:
        for predicate in rule.scope.predicates:
            if isinstance(predicate, model.TeamPredicate) and predicate.target is not None:
                target = ".".join((
                    *predicate.target.module_parts, predicate.target.declaration_name
                ))
                match = declaration_match(self, predicate.target, rule_unit)
                if match is None or not isinstance(match[1], model.Team):
                    self._raise_rule_unknown_scope_target(
                        rule=rule, rule_unit=rule_unit, source_span=predicate.source_span,
                        target_name=target,
                    )
            if isinstance(predicate, model.FlowPredicate):
                target = self._rule_agent_name(predicate.flow_ref, flow=flow)
                if self._flow_decl_match(target, unit=rule_unit, registry_name="agents_by_name") is None:
                    self._raise_rule_unknown_scope_target(
                        rule=rule,
                        rule_unit=rule_unit,
                        source_span=predicate.source_span,
                        target_name=target,
                    )

    def _validate_rule_assertion_targets(
        self,
        rule: model.RuleDecl,
        *,
        flow,
        rule_unit: IndexedUnit,
    ) -> None:
        for assertion in rule.assertions:
            if isinstance(
                assertion,
                (model.RequiresInheritAssertion, model.ForbidsBindAssertion),
            ):
                target = self._rule_agent_name(assertion.target, flow=flow)
                if self._flow_decl_match(target, unit=rule_unit, registry_name="agents_by_name") is None:
                    self._raise_rule_unknown_assertion_target(
                        rule=rule,
                        rule_unit=rule_unit,
                        source_span=assertion.source_span,
                        target_name=target,
                    )

    def _agent_matches_rule_scope(
        self,
        agent: model.Agent,
        *,
        agent_unit: IndexedUnit,
        rule: model.RuleDecl,
        flow,
    ) -> bool:
        for predicate in rule.scope.predicates:
            if isinstance(predicate, model.TeamPredicate):
                if isinstance(agent, model.Member):
                    match = find_home_team(self, agent, unit=agent_unit)
                    if predicate.target is None:
                        return True
                    rule_unit = flow.declaration_owner_units_by_id[id(rule)]
                    target = declaration_match(self, predicate.target, rule_unit)
                    if (match[0].prompt_file.source_path, match[1].name) == (
                        target[0].prompt_file.source_path, target[1].name
                    ):
                        return True
                continue
            if isinstance(predicate, model.MemberPredicate):
                if isinstance(agent, model.Member) and agent.key == predicate.key:
                    return True
                continue
            if isinstance(predicate, model.HomePredicate):
                match = find_home_team(self, agent, unit=agent_unit)
                home = self.session.home_paths.get(agent.name)
                if match is not None:
                    home = match[1].home
                    if isinstance(agent, model.Member):
                        home = str(PurePosixPath(home) / agent.key.replace("_", "-"))
                if home is not None and re.fullmatch(
                    glob.translate(predicate.glob, recursive=True), home
                ):
                    return True
                continue
            if isinstance(predicate, model.AgentTagPredicate):
                if agent.name == predicate.tag:
                    return True
                continue
            if isinstance(predicate, model.FlowPredicate):
                target = self._rule_agent_name(predicate.flow_ref, flow=flow)
                if self._agent_ancestor_chain_includes(
                    agent,
                    agent_unit=agent_unit,
                    target_name=target,
                ):
                    return True
                continue
            if isinstance(predicate, model.RoleClassPredicate):
                if agent.name.endswith(predicate.role_class):
                    return True
                continue
            if isinstance(predicate, model.FileTreePredicate):
                source_path = agent_unit.prompt_file.source_path
                if source_path is None:
                    continue
                try:
                    relative = source_path.relative_to(agent_unit.prompt_root)
                    relative_text = relative.as_posix()
                except ValueError:
                    relative_text = str(source_path)
                if fnmatch.fnmatch(relative_text, predicate.glob):
                    return True
                continue
        return False

    def _agent_ancestor_chain_includes(
        self,
        agent: model.Agent,
        *,
        agent_unit: IndexedUnit,
        target_name: str,
    ) -> bool:
        current_agent: model.Agent | None = agent
        current_unit = agent_unit
        visited: set[tuple[tuple[str, ...], str]] = set()
        while current_agent is not None:
            if current_agent.name == target_name:
                return True
            if current_agent.parent_ref is None:
                return False
            key = (current_unit.module_parts, current_agent.name)
            if key in visited:
                return False
            visited.add(key)
            try:
                current_unit, current_agent = self._resolve_parent_agent_decl(
                    current_agent,
                    unit=current_unit,
                )
            except CompileError:
                return False
        return False

    def _agent_declares_slot(
        self,
        agent: model.Agent,
        *,
        agent_unit: IndexedUnit,
        slot_key: str,
    ) -> bool:
        return any(
            slot.key == slot_key
            for slot in self._resolve_agent_slots(agent, unit=agent_unit)
        )

    def _evaluate_rule_assertion(
        self,
        assertion,
        *,
        agent: model.Agent,
        agent_unit: IndexedUnit,
        rule: model.RuleDecl,
        rule_unit: IndexedUnit,
        flow,
    ) -> None:
        if isinstance(assertion, model.RequiresInheritAssertion):
            target = self._rule_agent_name(assertion.target, flow=flow)
            if not self._agent_ancestor_chain_includes(
                agent,
                agent_unit=agent_unit,
                target_name=target,
            ):
                self._raise_rule_violation(
                    code="RULE003",
                    summary="Rule `requires inherit` violated",
                    detail=(
                        f"Rule `{rule.name}` requires agents in scope to inherit from "
                        f"`{target}`, but agent `{agent.name}` does not inherit from it."
                    ),
                    rule=rule,
                    rule_unit=rule_unit,
                    agent=agent,
                    agent_unit=agent_unit,
                    source_span=assertion.source_span,
                )
            return
        if isinstance(assertion, model.ForbidsBindAssertion):
            target = self._rule_agent_name(assertion.target, flow=flow)
            if self._agent_ancestor_chain_includes(
                agent,
                agent_unit=agent_unit,
                target_name=target,
            ):
                self._raise_rule_violation(
                    code="RULE004",
                    summary="Rule `forbids bind` violated",
                    detail=(
                        f"Rule `{rule.name}` forbids agents in scope from binding "
                        f"`{target}`, but agent `{agent.name}` inherits from it."
                    ),
                    rule=rule,
                    rule_unit=rule_unit,
                    agent=agent,
                    agent_unit=agent_unit,
                    source_span=assertion.source_span,
                )
            return
        if isinstance(assertion, model.RequiresDeclareAssertion):
            if not self._agent_declares_slot(
                agent,
                agent_unit=agent_unit,
                slot_key=assertion.slot_key,
            ):
                self._raise_rule_violation(
                    code="RULE005",
                    summary="Rule `requires declare` violated",
                    detail=(
                        f"Rule `{rule.name}` requires agents in scope to declare slot "
                        f"`{assertion.slot_key}`, but agent `{agent.name}` does not "
                        "declare it or inherit it from any ancestor."
                    ),
                    rule=rule,
                    rule_unit=rule_unit,
                    agent=agent,
                    agent_unit=agent_unit,
                    source_span=assertion.source_span,
                )
            return

    def _raise_rule_unknown_scope_target(
        self,
        *,
        rule: model.RuleDecl,
        rule_unit: IndexedUnit,
        source_span: model.SourceSpan | None,
        target_name: str,
    ) -> None:
        raise compile_error(
            code="RULE001",
            summary="Rule scope predicate target does not resolve",
            detail=(
                f"Rule `{rule.name}` scope target `{target_name}` is not "
                "declared as an agent in the current flow."
            ),
            path=rule_unit.prompt_file.source_path,
            source_span=source_span or rule.source_span,
            hints=(
                "Declare the target agent in the same flow, or fix the name.",
                "Rules resolve scope targets against the current flow only.",
            ),
        )

    def _raise_rule_unknown_assertion_target(
        self,
        *,
        rule: model.RuleDecl,
        rule_unit: IndexedUnit,
        source_span: model.SourceSpan | None,
        target_name: str,
    ) -> None:
        raise compile_error(
            code="RULE002",
            summary="Rule assertion target does not resolve",
            detail=(
                f"Rule `{rule.name}` assertion target `{target_name}` is not "
                "declared as an agent in the current flow."
            ),
            path=rule_unit.prompt_file.source_path,
            source_span=source_span or rule.source_span,
            hints=(
                "Declare the target agent in the same flow, or fix the name.",
                "Rules resolve assertion targets against the current flow only.",
            ),
        )

    def _raise_rule_violation(
        self,
        *,
        code: str,
        summary: str,
        detail: str,
        rule: model.RuleDecl,
        rule_unit: IndexedUnit,
        agent: model.Agent,
        agent_unit: IndexedUnit,
        source_span: model.SourceSpan | None,
    ) -> None:
        full_detail = f"{detail} {rule.message}" if rule.message else detail
        raise compile_error(
            code=code,
            summary=summary,
            detail=full_detail,
            path=agent_unit.prompt_file.source_path,
            source_span=agent.source_span,
            related=(
                related_prompt_site(
                    label=f"rule `{rule.name}` assertion",
                    path=rule_unit.prompt_file.source_path,
                    source_span=source_span or rule.source_span,
                ),
            ),
            hints=(
                "Fix the agent to satisfy the rule, or narrow the rule scope.",
            ),
        )
