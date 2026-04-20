from __future__ import annotations

import fnmatch
from pathlib import Path

from doctrine import model
from doctrine._compiler.diagnostics import compile_error, related_prompt_site
from doctrine._compiler.resolved_types import CompileError, IndexedUnit

_AGENT_SLOT_FIELD_TYPES = (
    model.AuthoredSlotField,
    model.AuthoredSlotAbstract,
    model.AuthoredSlotInherit,
    model.AuthoredSlotOverride,
)


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

        for agent_name, agent in flow.agents_by_name.items():
            agent_unit = flow.declaration_owner_units_by_id[id(agent)]
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

    def _validate_rule_scope_targets(
        self,
        rule: model.RuleDecl,
        *,
        flow,
        rule_unit: IndexedUnit,
    ) -> None:
        for predicate in rule.scope.predicates:
            if isinstance(predicate, model.FlowPredicate):
                if predicate.flow_ref.declaration_name not in flow.agents_by_name:
                    self._raise_rule_unknown_scope_target(
                        rule=rule,
                        rule_unit=rule_unit,
                        source_span=predicate.source_span,
                        target_name=predicate.flow_ref.declaration_name,
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
                if assertion.target.declaration_name not in flow.agents_by_name:
                    self._raise_rule_unknown_assertion_target(
                        rule=rule,
                        rule_unit=rule_unit,
                        source_span=assertion.source_span,
                        target_name=assertion.target.declaration_name,
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
            if isinstance(predicate, model.AgentTagPredicate):
                if agent.name == predicate.tag:
                    return True
                continue
            if isinstance(predicate, model.FlowPredicate):
                target = predicate.flow_ref.declaration_name
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
        current_agent: model.Agent | None = agent
        current_unit = agent_unit
        visited: set[tuple[tuple[str, ...], str]] = set()
        while current_agent is not None:
            for field in current_agent.fields:
                if isinstance(field, _AGENT_SLOT_FIELD_TYPES) and field.key == slot_key:
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
            target = assertion.target.declaration_name
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
            target = assertion.target.declaration_name
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
