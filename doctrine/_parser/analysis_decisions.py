from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    AnalysisBodyParts,
    DecisionBodyParts,
    DecisionItemPart,
    RenderProfilePart,
    _body_prose_location,
    _body_prose_value,
    _item_line_column,
    _meta_line_column,
    _positioned_body_prose,
    _positioned_decision_item,
    _positioned_render_profile,
)
from doctrine.diagnostics import TransformParseFailure


class AnalysisDecisionTransformerMixin:
    """Shared analysis and decision lowering for the public parser boundary."""

    @v_args(inline=True)
    def analysis_field(self, ref):
        return model.AnalysisField(value=ref)

    @v_args(inline=True)
    def decision_field(self, ref):
        return model.DecisionField(value=ref)

    @v_args(inline=True)
    def analysis_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        analysis_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            analysis_body = body
        return model.AnalysisDecl(
            name=name,
            body=model.AnalysisBody(
                title=title,
                preamble=analysis_body.preamble,
                items=analysis_body.items,
            ),
            parent_ref=parent_ref,
            render_profile_ref=analysis_body.render_profile_ref,
        )

    @v_args(inline=True)
    def decision_decl(self, name, title, decision_body):
        return model.DecisionDecl(
            name=name,
            body=model.DecisionBody(
                title=title,
                preamble=decision_body.preamble,
                items=decision_body.items,
            ),
            render_profile_ref=decision_body.render_profile_ref,
        )

    @v_args(meta=True, inline=True)
    def analysis_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def analysis_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def analysis_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    def analysis_body(self, items):
        preamble: list[model.ProseLine] = []
        analysis_items: list[model.AnalysisItem] = []
        render_profile_ref: model.NameRef | None = None
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_ref is not None:
                    raise TransformParseFailure(
                        "Analysis declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per analysis declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if analysis_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Analysis prose lines must appear before keyed analysis entries.",
                        hints=(
                            "Move prose lines to the top of the analysis body or put them inside a titled analysis section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            analysis_items.append(item)
        return AnalysisBodyParts(
            preamble=tuple(preamble),
            items=tuple(analysis_items),
            render_profile_ref=render_profile_ref,
        )

    def analysis_section_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def analysis_section(self, key, title, items):
        return model.AnalysisSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def analysis_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def analysis_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.AnalysisOverrideSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    @v_args(inline=True)
    def analysis_section_item(self, value):
        return value

    @v_args(inline=True)
    def prove_stmt(self, target_title, basis):
        return model.ProveStmt(target_title=target_title, basis=basis)

    @v_args(inline=True)
    def derive_stmt(self, target_title, basis):
        return model.DeriveStmt(target_title=target_title, basis=basis)

    @v_args(inline=True)
    def classify_stmt(self, target_title, enum_ref):
        return model.ClassifyStmt(target_title=target_title, enum_ref=enum_ref)

    @v_args(inline=True)
    def compare_stmt(self, target_title, basis, using_expr=None):
        return model.CompareStmt(
            target_title=target_title,
            basis=basis,
            using_expr=using_expr,
        )

    @v_args(inline=True)
    def compare_using_clause(self, using_expr):
        return using_expr

    @v_args(inline=True)
    def defend_stmt(self, target_title, basis):
        return model.DefendStmt(target_title=target_title, basis=basis)

    @v_args(meta=True, inline=True)
    def decision_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    @v_args(meta=True, inline=True)
    def decision_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def decision_body_line(self, value):
        return value

    def decision_body(self, items):
        preamble: list[model.ProseLine] = []
        decision_items: list[model.DecisionItem] = []
        render_profile_ref: model.NameRef | None = None
        seen_entries: set[str] = set()
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_ref is not None:
                    raise TransformParseFailure(
                        "Decision declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per decision declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if decision_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Decision prose lines must appear before typed decision entries.",
                        hints=(
                            "Move prose lines to the top of the decision body before typed decision requirements.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue

            decision_item = item.item if isinstance(item, DecisionItemPart) else item
            line, column = _item_line_column(item)

            if isinstance(decision_item, model.DecisionMinimumCandidates):
                dedupe_key = "minimum_candidates"
            elif isinstance(decision_item, model.DecisionRequiredItem):
                dedupe_key = f"required:{decision_item.key}"
            elif isinstance(decision_item, model.DecisionChooseWinner):
                dedupe_key = "choose_winner"
            elif isinstance(decision_item, model.DecisionRankBy):
                dedupe_key = "rank_by"
            else:
                dedupe_key = type(decision_item).__name__

            if dedupe_key in seen_entries:
                raise TransformParseFailure(
                    f"Decision declarations may account for `{dedupe_key}` only once.",
                    hints=("Keep each decision requirement explicit only once per declaration.",),
                    line=line,
                    column=column,
                )
            seen_entries.add(dedupe_key)
            decision_items.append(decision_item)

        return DecisionBodyParts(
            preamble=tuple(preamble),
            items=tuple(decision_items),
            render_profile_ref=render_profile_ref,
        )

    @v_args(meta=True, inline=True)
    def decision_candidates_minimum_stmt(self, meta, count):
        parsed = int(count)
        if parsed < 1:
            line, column = _meta_line_column(meta)
            raise TransformParseFailure(
                "Decision candidate minimum must be at least 1.",
                hints=("Use `candidates minimum <positive number>`.",),
                line=line,
                column=column,
            )
        return _positioned_decision_item(meta, model.DecisionMinimumCandidates(count=parsed))

    @v_args(meta=True)
    def decision_rank_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="rank"))

    @v_args(meta=True)
    def decision_rejects_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="rejects"))

    @v_args(meta=True)
    def decision_candidate_pool_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="candidate_pool"))

    @v_args(meta=True)
    def decision_kept_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="kept"))

    @v_args(meta=True)
    def decision_rejected_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="rejected"))

    @v_args(meta=True)
    def decision_sequencing_proof_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="sequencing_proof"))

    @v_args(meta=True)
    def decision_winner_reasons_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionRequiredItem(key="winner_reasons"))

    @v_args(meta=True)
    def decision_winner_required_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionChooseWinner())

    @v_args(meta=True)
    def decision_choose_one_winner_stmt(self, meta, _items):
        return _positioned_decision_item(meta, model.DecisionChooseWinner())

    @v_args(meta=True)
    def decision_rank_by_stmt(self, meta, items):
        return _positioned_decision_item(meta, model.DecisionRankBy(dimensions=tuple(items)))
