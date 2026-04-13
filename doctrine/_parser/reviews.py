from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import GroundingBodyParts, ReviewBodyParts, RouteOnlyBodyParts


class ReviewTransformerMixin:
    """Shared review, route-only, and grounding lowering for the public parser boundary."""

    def abstract_review_decl(self, items):
        return self._review_decl(items, abstract=True, family=False)

    def review_family_decl(self, items):
        return self._review_decl(items, abstract=False, family=True)

    def review_decl(self, items):
        return self._review_decl(items, abstract=False, family=False)

    @v_args(inline=True)
    def route_only_decl(self, name, title, body):
        return model.RouteOnlyDecl(
            name=name,
            body=model.RouteOnlyBody(
                title=title,
                facts_ref=body.facts_ref,
                when_exprs=body.when_exprs,
                current_none=body.current_none,
                handoff_output_ref=body.handoff_output_ref,
                guarded=body.guarded,
                routes=body.routes,
            ),
        )

    @v_args(inline=True)
    def grounding_decl(self, name, title, body):
        return model.GroundingDecl(
            name=name,
            body=model.GroundingBody(
                title=title,
                source_ref=body.source_ref,
                target=body.target,
                policy_items=body.policy_items,
            ),
        )

    def review_body(self, items):
        return ReviewBodyParts(items=tuple(items))

    def route_only_body(self, items):
        facts_ref: model.NameRef | None = None
        when_exprs: tuple[model.Expr, ...] = ()
        current_none = False
        handoff_output_ref: model.NameRef | None = None
        guarded: tuple[model.RouteOnlyGuard, ...] = ()
        routes: tuple[model.RouteOnlyRoute, ...] = ()
        for item in items:
            if isinstance(item, tuple) and item and item[0] == "facts":
                facts_ref = item[1]
            elif isinstance(item, tuple) and item and item[0] == "when":
                when_exprs = item[1]
            elif item == "__ROUTE_ONLY_CURRENT_NONE__":
                current_none = True
            elif isinstance(item, tuple) and item and item[0] == "handoff_output":
                handoff_output_ref = item[1]
            elif isinstance(item, tuple) and item and item[0] == "guarded":
                guarded = item[1]
            elif isinstance(item, tuple) and item and item[0] == "routes":
                routes = item[1]
        return RouteOnlyBodyParts(
            facts_ref=facts_ref,
            when_exprs=when_exprs,
            current_none=current_none,
            handoff_output_ref=handoff_output_ref,
            guarded=guarded,
            routes=routes,
        )

    def grounding_body(self, items):
        source_ref: model.NameRef | None = None
        target: str | None = None
        policy_items: tuple[model.GroundingPolicyItem, ...] = ()
        for item in items:
            if isinstance(item, tuple) and item and item[0] == "source":
                source_ref = item[1]
            elif isinstance(item, tuple) and item and item[0] == "target":
                target = item[1]
            elif isinstance(item, tuple) and item and item[0] == "policy":
                policy_items = item[1]
        return GroundingBodyParts(
            source_ref=source_ref,
            target=target,
            policy_items=policy_items,
        )

    def artifact_subject_expr(self, items):
        return tuple(items)

    @v_args(inline=True)
    def artifact_ref(self, ref):
        return ref

    @v_args(inline=True)
    def enum_member_ref(self, ref):
        return ref

    @v_args(inline=True)
    def review_contract_ref(self, ref):
        return model.ReviewContractRef(ref=ref)

    @v_args(inline=True)
    def output_ref(self, ref):
        return ref

    @v_args(inline=True)
    def route_only_facts_stmt(self, ref):
        return ("facts", ref)

    def route_only_when_block(self, items):
        return ("when", tuple(items))

    @v_args(inline=True)
    def route_only_when_expr(self, expr):
        return expr

    def route_only_current_none_stmt(self, _items):
        return "__ROUTE_ONLY_CURRENT_NONE__"

    @v_args(inline=True)
    def route_only_handoff_output_stmt(self, output_ref):
        return ("handoff_output", output_ref)

    def route_only_guarded_block(self, items):
        return ("guarded", tuple(items))

    @v_args(inline=True)
    def route_only_guarded_entry(self, key, expr):
        return model.RouteOnlyGuard(key=key, expr=expr)

    def route_only_routes_block(self, items):
        return ("routes", tuple(items))

    @v_args(inline=True)
    def route_only_route_entry(self, key_or_target, maybe_target=None):
        if maybe_target is None:
            return model.RouteOnlyRoute(key=None, target=key_or_target)
        return model.RouteOnlyRoute(key=key_or_target, target=maybe_target)

    @v_args(inline=True)
    def grounding_source_stmt(self, ref):
        return ("source", ref)

    @v_args(inline=True)
    def grounding_target_stmt(self, target):
        return ("target", target)

    def grounding_policy_block(self, items):
        return ("policy", tuple(items))

    @v_args(inline=True)
    def grounding_policy_start_from(self, source, unless=None):
        return model.GroundingPolicyStartFrom(source=source, unless=unless)

    @v_args(inline=True)
    def grounding_policy_forbid(self, value):
        return model.GroundingPolicyForbid(value=value)

    @v_args(inline=True)
    def grounding_policy_allow(self, value):
        return model.GroundingPolicyAllow(value=value)

    @v_args(inline=True)
    def grounding_policy_route(self, condition, target):
        return model.GroundingPolicyRoute(condition=condition, target=target)

    @v_args(inline=True)
    def grounding_unless_clause(self, value):
        return value

    @v_args(inline=True)
    def subject_stmt(self, subjects):
        return model.ReviewSubjectConfig(subjects=tuple(subjects))

    def subject_map_stmt(self, items):
        return model.ReviewSubjectMapConfig(entries=tuple(items))

    @v_args(inline=True)
    def subject_map_entry(self, enum_member_ref, artifact_ref):
        return model.ReviewSubjectMapEntry(
            enum_member_ref=enum_member_ref,
            artifact_ref=artifact_ref,
        )

    @v_args(inline=True)
    def contract_stmt(self, contract_ref):
        return model.ReviewContractConfig(contract=contract_ref)

    @v_args(inline=True)
    def comment_output_stmt(self, output_ref):
        return model.ReviewCommentOutputConfig(output_ref=output_ref)

    def fields_stmt(self, items):
        return model.ReviewFieldsConfig(bindings=tuple(items))

    @v_args(inline=True)
    def semantic_field_binding(self, semantic_field, field_path):
        return model.ReviewFieldBinding(
            semantic_field=semantic_field,
            field_path=tuple(field_path),
        )

    def review_semantic_field_verdict(self, _items):
        return "verdict"

    def review_semantic_field_reviewed_artifact(self, _items):
        return "reviewed_artifact"

    def review_semantic_field_analysis(self, _items):
        return "analysis"

    def review_semantic_field_readback(self, _items):
        return "readback"

    def review_semantic_field_current_artifact(self, _items):
        return "current_artifact"

    def review_semantic_field_failing_gates(self, _items):
        return "failing_gates"

    def review_semantic_field_blocked_gate(self, _items):
        return "blocked_gate"

    def review_semantic_field_next_owner(self, _items):
        return "next_owner"

    def review_semantic_field_active_mode(self, _items):
        return "active_mode"

    def review_semantic_field_trigger_reason(self, _items):
        return "trigger_reason"

    @v_args(inline=True)
    def pre_outcome_review_section(self, key, title, *items):
        return model.ReviewSection(key=key, title=title, items=tuple(items))

    def pre_outcome_review_section_untitled(self, items):
        key = items[0]
        return model.ReviewSection(key=key, title=None, items=tuple(items[1:]))

    @v_args(inline=True)
    def on_accept_review_section_titled(self, title, *items):
        return model.ReviewOutcomeSection(key="on_accept", title=title, items=tuple(items))

    def on_accept_review_section_untitled(self, items):
        return model.ReviewOutcomeSection(key="on_accept", title=None, items=tuple(items))

    @v_args(inline=True)
    def on_reject_review_section_titled(self, title, *items):
        return model.ReviewOutcomeSection(key="on_reject", title=title, items=tuple(items))

    def on_reject_review_section_untitled(self, items):
        return model.ReviewOutcomeSection(key="on_reject", title=None, items=tuple(items))

    def selector_block(self, items):
        if len(items) != 1:
            raise ValueError("Review selector blocks must define exactly one selector.")
        return items[0]

    @v_args(inline=True)
    def review_selector_stmt(self, field_name, expr, enum_ref):
        return model.ReviewSelectorConfig(field_name=field_name, expr=expr, enum_ref=enum_ref)

    def review_cases_block(self, items):
        return model.ReviewCasesConfig(cases=tuple(items))

    def review_case_body(self, items):
        return tuple(items)

    def review_case_decl(self, items):
        key = items[0]
        title = items[1]
        body = items[2]
        head = body[0]
        subject = body[1]
        contract = body[2]
        checks = body[3]
        on_accept = body[4]
        on_reject = body[5]
        return model.ReviewCase(
            key=key,
            title=title,
            head=head,
            subject=subject,
            contract=contract,
            checks=checks,
            on_accept=on_accept,
            on_reject=on_reject,
        )

    @v_args(inline=True)
    def review_case_when_stmt(self, options):
        return model.ReviewMatchHead(options=tuple(options), when_expr=None)

    @v_args(inline=True)
    def review_case_subject_stmt(self, subjects):
        return model.ReviewSubjectConfig(subjects=tuple(subjects))

    @v_args(inline=True)
    def review_case_contract_stmt(self, contract_ref):
        return model.ReviewContractConfig(contract=contract_ref)

    def review_case_checks(self, items):
        return tuple(items)

    def review_case_on_accept(self, items):
        return model.ReviewOutcomeSection(key="on_accept", title=None, items=tuple(items))

    def review_case_on_reject(self, items):
        return model.ReviewOutcomeSection(key="on_reject", title=None, items=tuple(items))

    @v_args(inline=True)
    def review_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def review_item_key(self, key):
        return str(key)

    def review_item_key_fields(self, _items):
        return "fields"

    def review_item_key_on_accept(self, _items):
        return "on_accept"

    def review_item_key_on_reject(self, _items):
        return "on_reject"

    def review_override_fields(self, items):
        return model.ReviewOverrideFields(bindings=tuple(items))

    @v_args(inline=True)
    def review_override_pre_outcome_section_titled(self, key, title, *items):
        return model.ReviewOverrideSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def review_override_pre_outcome_section_untitled(self, key, *items):
        return model.ReviewOverrideSection(key=key, title=None, items=tuple(items))

    @v_args(inline=True)
    def review_override_on_accept_titled(self, title, *items):
        return model.ReviewOverrideOutcomeSection(
            key="on_accept",
            title=title,
            items=tuple(items),
        )

    def review_override_on_accept_untitled(self, items):
        return model.ReviewOverrideOutcomeSection(
            key="on_accept",
            title=None,
            items=tuple(items),
        )

    @v_args(inline=True)
    def review_override_on_reject_titled(self, title, *items):
        return model.ReviewOverrideOutcomeSection(
            key="on_reject",
            title=title,
            items=tuple(items),
        )

    def review_override_on_reject_untitled(self, items):
        return model.ReviewOverrideOutcomeSection(
            key="on_reject",
            title=None,
            items=tuple(items),
        )

    @v_args(inline=True)
    def block_stmt(self, gate, expr):
        return model.ReviewBlockStmt(gate=gate, expr=expr)

    @v_args(inline=True)
    def reject_stmt(self, gate, expr):
        return model.ReviewRejectStmt(gate=gate, expr=expr)

    @v_args(inline=True)
    def accept_stmt(self, gate, expr):
        return model.ReviewAcceptStmt(gate=gate, expr=expr)

    @v_args(inline=True)
    def contract_gate_ref(self, key):
        return model.ContractGateRef(key=key)

    @v_args(inline=True)
    def section_gate_ref(self, key):
        return model.SectionGateRef(key=key)

    @v_args(inline=True)
    def current_review_artifact_stmt(self, artifact_ref, carrier, when_expr=None):
        return model.ReviewCurrentArtifactStmt(
            artifact_ref=artifact_ref,
            carrier=carrier,
            when_expr=when_expr,
        )

    @v_args(inline=True)
    def current_review_none_stmt(self, when_expr=None):
        return model.ReviewCurrentNoneStmt(when_expr=when_expr)

    @v_args(inline=True)
    def carry_stmt(self, field_name, expr):
        return model.ReviewCarryStmt(field_name=field_name, expr=expr)

    def carried_field_active_mode(self, _items):
        return "active_mode"

    def carried_field_trigger_reason(self, _items):
        return "trigger_reason"

    @v_args(inline=True)
    def output_field_ref(self, parts):
        return model.ReviewOutputFieldRef(parts=tuple(parts))

    def pre_outcome_when_stmt(self, items):
        return model.ReviewPreOutcomeWhenStmt(expr=items[0], items=tuple(items[1:]))

    def outcome_when_stmt(self, items):
        return model.ReviewOutcomeWhenStmt(expr=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def pre_outcome_match_stmt(self, expr, *cases):
        return model.ReviewPreOutcomeMatchStmt(expr=expr, cases=tuple(cases))

    @v_args(inline=True)
    def outcome_match_stmt(self, expr, *cases):
        return model.ReviewOutcomeMatchStmt(expr=expr, cases=tuple(cases))

    def pre_outcome_match_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.ReviewPreOutcomeMatchArm(head=head, items=tuple(items[1:]))

    def outcome_match_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.ReviewOutcomeMatchArm(head=head, items=tuple(items[1:]))

    def review_match_head(self, items):
        options = items[0]
        when_expr: model.Expr | None = items[1] if len(items) > 1 else None
        return model.ReviewMatchHead(options=tuple(options), when_expr=when_expr)

    @v_args(inline=True)
    def review_match_when(self, expr):
        return expr

    def union_expr(self, items):
        return tuple(items)

    @v_args(inline=True)
    def outcome_route_stmt(self, label, target, when_expr=None):
        return model.ReviewOutcomeRouteStmt(label=label, target=target, when_expr=when_expr)

    @v_args(inline=True)
    def outcome_when_clause(self, expr):
        return expr
