from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import _with_source_span


class RuleTransformerMixin:
    """Transforms top-level `rule` declarations into `RuleDecl` nodes."""

    @v_args(meta=True, inline=True)
    def rule_decl(self, meta, name, title, body):
        scope, assertions, message = body
        return _with_source_span(
            model.RuleDecl(
                name=name,
                title=title,
                scope=scope,
                assertions=tuple(assertions),
                message=message,
            ),
            meta,
        )

    def rule_body(self, items):
        scope = items[0]
        assertions = items[1]
        message = items[2]
        return (scope, assertions, message)

    @v_args(meta=True)
    def rule_scope_block(self, meta, predicates):
        return _with_source_span(
            model.RuleScope(predicates=tuple(predicates)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def agent_tag_predicate(self, meta, tag):
        return _with_source_span(model.AgentTagPredicate(tag=tag), meta)

    @v_args(meta=True, inline=True)
    def flow_predicate(self, meta, ref):
        return _with_source_span(model.FlowPredicate(flow_ref=ref), meta)

    @v_args(meta=True, inline=True)
    def role_class_predicate(self, meta, role_class):
        return _with_source_span(
            model.RoleClassPredicate(role_class=role_class),
            meta,
        )

    @v_args(meta=True, inline=True)
    def file_tree_predicate(self, meta, glob):
        return _with_source_span(model.FileTreePredicate(glob=glob), meta)

    def rule_assertions_block(self, assertions):
        return tuple(assertions)

    @v_args(meta=True, inline=True)
    def requires_inherit_assertion(self, meta, ref):
        return _with_source_span(
            model.RequiresInheritAssertion(target=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def forbids_bind_assertion(self, meta, ref):
        return _with_source_span(
            model.ForbidsBindAssertion(target=ref),
            meta,
        )

    @v_args(meta=True, inline=True)
    def requires_declare_assertion(self, meta, slot_key):
        return _with_source_span(
            model.RequiresDeclareAssertion(slot_key=slot_key),
            meta,
        )

    @v_args(inline=True)
    def rule_message(self, value):
        return value
