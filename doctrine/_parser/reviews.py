from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    GroundingBodyParts,
    ReviewBodyParts,
    RouteOnlyBodyParts,
    _expand_grouped_inherit,
    _flatten_grouped_items,
    _source_span_from_meta,
    _with_source_span,
)


class ReviewTransformerMixin:
    """Shared review, route-only, and grounding lowering for the public parser boundary."""

    @v_args(meta=True)
    def abstract_review_decl(self, meta, items):
        return self._review_decl(
            items,
            abstract=True,
            family=False,
            source_span=_source_span_from_meta(meta),
        )

    @v_args(meta=True)
    def review_family_decl(self, meta, items):
        return self._review_decl(
            items,
            abstract=False,
            family=True,
            source_span=_source_span_from_meta(meta),
        )

    @v_args(meta=True)
    def review_decl(self, meta, items):
        return self._review_decl(
            items,
            abstract=False,
            family=False,
            source_span=_source_span_from_meta(meta),
        )

    @v_args(meta=True, inline=True)
    def route_only_decl(self, meta, name, title, body):
        return _with_source_span(
            model.RouteOnlyDecl(
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
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def grounding_decl(self, meta, name, title, body):
        return _with_source_span(
            model.GroundingDecl(
                name=name,
                body=model.GroundingBody(
                    title=title,
                    source_ref=body.source_ref,
                    target=body.target,
                    policy_items=body.policy_items,
                ),
            ),
            meta,
        )

    def review_body(self, items):
        return ReviewBodyParts(items=_flatten_grouped_items(items))

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

    @v_args(meta=True, inline=True)
    def review_contract_ref(self, meta, ref):
        return _with_source_span(model.ReviewContractRef(ref=ref), meta)

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

    @v_args(meta=True, inline=True)
    def route_only_guarded_entry(self, meta, key, expr):
        return _with_source_span(model.RouteOnlyGuard(key=key, expr=expr), meta)

    def route_only_routes_block(self, items):
        return ("routes", tuple(items))

    @v_args(meta=True, inline=True)
    def route_only_route_entry(self, meta, key_or_target, maybe_target=None):
        if maybe_target is None:
            return _with_source_span(
                model.RouteOnlyRoute(key=None, target=key_or_target),
                meta,
            )
        return _with_source_span(
            model.RouteOnlyRoute(key=key_or_target, target=maybe_target),
            meta,
        )

    @v_args(inline=True)
    def grounding_source_stmt(self, ref):
        return ("source", ref)

    @v_args(inline=True)
    def grounding_target_stmt(self, target):
        return ("target", target)

    def grounding_policy_block(self, items):
        return ("policy", tuple(items))

    @v_args(meta=True, inline=True)
    def grounding_policy_start_from(self, meta, source, unless=None):
        return _with_source_span(
            model.GroundingPolicyStartFrom(source=source, unless=unless),
            meta,
        )

    @v_args(meta=True, inline=True)
    def grounding_policy_forbid(self, meta, value):
        return _with_source_span(model.GroundingPolicyForbid(value=value), meta)

    @v_args(meta=True, inline=True)
    def grounding_policy_allow(self, meta, value):
        return _with_source_span(model.GroundingPolicyAllow(value=value), meta)

    @v_args(meta=True, inline=True)
    def grounding_policy_route(self, meta, condition, target):
        return _with_source_span(
            model.GroundingPolicyRoute(condition=condition, target=target),
            meta,
        )

    @v_args(inline=True)
    def grounding_unless_clause(self, value):
        return value

    @v_args(meta=True, inline=True)
    def subject_stmt(self, meta, subjects):
        return _with_source_span(model.ReviewSubjectConfig(subjects=tuple(subjects)), meta)

    @v_args(meta=True)
    def subject_map_stmt(self, meta, items):
        return _with_source_span(model.ReviewSubjectMapConfig(entries=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def subject_map_entry(self, meta, enum_member_ref, artifact_ref):
        return _with_source_span(
            model.ReviewSubjectMapEntry(
                enum_member_ref=enum_member_ref,
                artifact_ref=artifact_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def contract_stmt(self, meta, contract_ref):
        return _with_source_span(model.ReviewContractConfig(contract=contract_ref), meta)

    @v_args(meta=True, inline=True)
    def comment_output_stmt(self, meta, output_ref):
        return _with_source_span(
            model.ReviewCommentOutputConfig(output_ref=output_ref),
            meta,
        )

    @v_args(meta=True)
    def fields_stmt(self, meta, items):
        return _with_source_span(model.ReviewFieldsConfig(bindings=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def semantic_field_binding(self, meta, semantic_field, field_path):
        return _with_source_span(
            model.ReviewFieldBinding(
                semantic_field=semantic_field,
                field_path=tuple(field_path),
            ),
            meta,
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

    @v_args(meta=True, inline=True)
    def pre_outcome_review_section(self, meta, key, title, *items):
        return _with_source_span(
            model.ReviewSection(key=key, title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True)
    def pre_outcome_review_section_untitled(self, meta, items):
        key = items[0]
        return _with_source_span(
            model.ReviewSection(key=key, title=None, items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def on_accept_review_section_titled(self, meta, title, *items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_accept", title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True)
    def on_accept_review_section_untitled(self, meta, items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_accept", title=None, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def on_reject_review_section_titled(self, meta, title, *items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_reject", title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True)
    def on_reject_review_section_untitled(self, meta, items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_reject", title=None, items=tuple(items)),
            meta,
        )

    def selector_block(self, items):
        if len(items) != 1:
            raise ValueError("Review selector blocks must define exactly one selector.")
        return items[0]

    @v_args(meta=True, inline=True)
    def review_selector_stmt(self, meta, field_name, expr, enum_ref):
        return _with_source_span(
            model.ReviewSelectorConfig(field_name=field_name, expr=expr, enum_ref=enum_ref),
            meta,
        )

    @v_args(meta=True)
    def review_cases_block(self, meta, items):
        return _with_source_span(model.ReviewCasesConfig(cases=tuple(items)), meta)

    def review_case_body(self, items):
        return tuple(items)

    @v_args(meta=True)
    def review_case_decl(self, meta, items):
        key = items[0]
        title = items[1]
        body = items[2]
        head = body[0]
        subject = body[1]
        contract = body[2]
        checks = body[3]
        on_accept = body[4]
        on_reject = body[5]
        return _with_source_span(
            model.ReviewCase(
                key=key,
                title=title,
                head=head,
                subject=subject,
                contract=contract,
                checks=checks,
                on_accept=on_accept,
                on_reject=on_reject,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_case_when_stmt(self, meta, options):
        return _with_source_span(
            model.ReviewMatchHead(options=tuple(options), when_expr=None),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_case_subject_stmt(self, meta, subjects):
        return _with_source_span(model.ReviewSubjectConfig(subjects=tuple(subjects)), meta)

    @v_args(meta=True, inline=True)
    def review_case_contract_stmt(self, meta, contract_ref):
        return _with_source_span(model.ReviewContractConfig(contract=contract_ref), meta)

    def review_case_checks(self, items):
        return tuple(items)

    @v_args(meta=True)
    def review_case_on_accept(self, meta, items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_accept", title=None, items=tuple(items)),
            meta,
        )

    @v_args(meta=True)
    def review_case_on_reject(self, meta, items):
        return _with_source_span(
            model.ReviewOutcomeSection(key="on_reject", title=None, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_inherit(self, meta, key):
        return _with_source_span(model.InheritItem(key=key), meta)

    @v_args(meta=True, inline=True)
    def review_inherit_group(self, meta, keys=()):
        return _expand_grouped_inherit(meta, keys, model.InheritItem)

    @v_args(inline=True)
    def review_item_key(self, key):
        return str(key)

    def review_item_key_fields(self, _items):
        return "fields"

    def review_item_key_on_accept(self, _items):
        return "on_accept"

    def review_item_key_on_reject(self, _items):
        return "on_reject"

    @v_args(meta=True)
    def review_override_fields(self, meta, items):
        return _with_source_span(model.ReviewOverrideFields(bindings=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def review_override_pre_outcome_section_titled(self, meta, key, title, *items):
        return _with_source_span(
            model.ReviewOverrideSection(key=key, title=title, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_override_pre_outcome_section_untitled(self, meta, key, *items):
        return _with_source_span(
            model.ReviewOverrideSection(key=key, title=None, items=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_override_on_accept_titled(self, meta, title, *items):
        return _with_source_span(
            model.ReviewOverrideOutcomeSection(
                key="on_accept",
                title=title,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True)
    def review_override_on_accept_untitled(self, meta, items):
        return _with_source_span(
            model.ReviewOverrideOutcomeSection(
                key="on_accept",
                title=None,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_override_on_reject_titled(self, meta, title, *items):
        return _with_source_span(
            model.ReviewOverrideOutcomeSection(
                key="on_reject",
                title=title,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True)
    def review_override_on_reject_untitled(self, meta, items):
        return _with_source_span(
            model.ReviewOverrideOutcomeSection(
                key="on_reject",
                title=None,
                items=tuple(items),
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def block_stmt(self, meta, gate, expr):
        return _with_source_span(model.ReviewBlockStmt(gate=gate, expr=expr), meta)

    @v_args(meta=True, inline=True)
    def reject_stmt(self, meta, gate, expr):
        return _with_source_span(model.ReviewRejectStmt(gate=gate, expr=expr), meta)

    @v_args(meta=True, inline=True)
    def accept_stmt(self, meta, gate, expr):
        return _with_source_span(model.ReviewAcceptStmt(gate=gate, expr=expr), meta)

    @v_args(meta=True, inline=True)
    def contract_gate_ref(self, meta, key):
        return _with_source_span(model.ContractGateRef(key=key), meta)

    @v_args(meta=True, inline=True)
    def section_gate_ref(self, meta, key):
        return _with_source_span(model.SectionGateRef(key=key), meta)

    @v_args(meta=True, inline=True)
    def current_review_artifact_stmt(self, meta, artifact_ref, carrier, when_expr=None):
        return _with_source_span(
            model.ReviewCurrentArtifactStmt(
                artifact_ref=artifact_ref,
                carrier=carrier,
                when_expr=when_expr,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def current_review_none_stmt(self, meta, when_expr=None):
        return _with_source_span(model.ReviewCurrentNoneStmt(when_expr=when_expr), meta)

    @v_args(meta=True, inline=True)
    def carry_stmt(self, meta, field_name, expr):
        return _with_source_span(model.ReviewCarryStmt(field_name=field_name, expr=expr), meta)

    def carried_field_active_mode(self, _items):
        return "active_mode"

    def carried_field_trigger_reason(self, _items):
        return "trigger_reason"

    @v_args(meta=True, inline=True)
    def output_field_ref(self, meta, parts):
        return _with_source_span(model.ReviewOutputFieldRef(parts=tuple(parts)), meta)

    @v_args(meta=True)
    def pre_outcome_when_stmt(self, meta, items):
        return _with_source_span(
            model.ReviewPreOutcomeWhenStmt(expr=items[0], items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True)
    def outcome_when_stmt(self, meta, items):
        return _with_source_span(
            model.ReviewOutcomeWhenStmt(expr=items[0], items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def pre_outcome_match_stmt(self, meta, expr, *cases):
        return _with_source_span(
            model.ReviewPreOutcomeMatchStmt(expr=expr, cases=tuple(cases)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def outcome_match_stmt(self, meta, expr, *cases):
        return _with_source_span(
            model.ReviewOutcomeMatchStmt(expr=expr, cases=tuple(cases)),
            meta,
        )

    @v_args(meta=True)
    def pre_outcome_match_case(self, meta, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return _with_source_span(
            model.ReviewPreOutcomeMatchArm(head=head, items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True)
    def outcome_match_case(self, meta, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return _with_source_span(
            model.ReviewOutcomeMatchArm(head=head, items=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True)
    def review_match_head(self, meta, items):
        options = items[0]
        when_expr: model.Expr | None = items[1] if len(items) > 1 else None
        return _with_source_span(
            model.ReviewMatchHead(options=tuple(options), when_expr=when_expr),
            meta,
        )

    @v_args(inline=True)
    def review_match_when(self, expr):
        return expr

    def union_expr(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def outcome_route_stmt(self, meta, label, target, when_expr=None):
        return _with_source_span(
            model.ReviewOutcomeRouteStmt(label=label, target=target, when_expr=when_expr),
            meta,
        )

    @v_args(inline=True)
    def outcome_when_clause(self, expr):
        return expr
