from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    FinalOutputBodyParts,
    FinalOutputOutputPart,
    FinalOutputRoutePart,
    FinalOutputReviewFieldsPart,
    _meta_line_column,
    _source_span_from_meta,
    _with_source_span,
)
from doctrine.diagnostics import TransformParseFailure


class AgentTransformerMixin:
    """Shared agent and agent-field lowering for the public parser boundary."""

    @v_args(meta=True)
    def agent(self, meta, items):
        return self._agent(items, abstract=False, source_span=_source_span_from_meta(meta))

    @v_args(meta=True)
    def abstract_agent(self, meta, items):
        return self._agent(items, abstract=True, source_span=_source_span_from_meta(meta))

    def role_body(self, items):
        return items[0]

    @v_args(meta=True, inline=True)
    def role_field(self, meta, title_or_text, body=None):
        if body is None:
            return _with_source_span(model.RoleScalar(text=title_or_text), meta)
        return _with_source_span(
            model.RoleBlock(title=title_or_text, lines=tuple(body)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def skills_field(self, meta, title_or_ref, body=None):
        return _with_source_span(
            model.SkillsField(value=self._skills_value(title_or_ref, body)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def review_field(self, meta, ref):
        return _with_source_span(model.ReviewField(value=ref), meta)

    @v_args(meta=True)
    def agent_selectors_field(self, meta, items):
        return _with_source_span(
            model.SelectorsField(bindings=tuple(items)),
            meta,
        )

    @v_args(meta=True, inline=True)
    def agent_selector_stmt(self, meta, selector_name, enum_member_ref):
        return _with_source_span(
            model.AgentSelectorBinding(
                selector_name=selector_name,
                enum_member_ref=enum_member_ref,
            ),
            meta,
        )

    @v_args(meta=True, inline=True)
    def final_output_field(self, meta, ref_or_body):
        if isinstance(ref_or_body, FinalOutputBodyParts):
            return _with_source_span(
                model.FinalOutputField(
                    value=ref_or_body.output_ref,
                    route_path=ref_or_body.route_path,
                    review_fields=ref_or_body.review_fields,
                ),
                meta,
            )
        return _with_source_span(model.FinalOutputField(value=ref_or_body), meta)

    @v_args(meta=True, inline=True)
    def final_output_output_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return FinalOutputOutputPart(ref=ref, line=line, column=column)

    @v_args(meta=True)
    def final_output_route_stmt(self, meta, items):
        line, column = _meta_line_column(meta)
        return FinalOutputRoutePart(
            path=tuple(items[0]),
            line=line,
            column=column,
        )

    @v_args(meta=True)
    def final_output_review_fields_stmt(self, meta, items):
        line, column = _meta_line_column(meta)
        return FinalOutputReviewFieldsPart(
            config=model.ReviewFieldsConfig(bindings=tuple(items)),
            line=line,
            column=column,
        )

    def final_output_body(self, items):
        output_ref: model.NameRef | None = None
        route_path: tuple[str, ...] | None = None
        review_fields: model.ReviewFieldsConfig | None = None

        for item in items:
            if isinstance(item, FinalOutputOutputPart):
                if output_ref is not None:
                    raise TransformParseFailure(
                        "final_output block may define `output:` only once.",
                        hints=("Keep exactly one `output:` entry inside the final_output block.",),
                        line=item.line,
                        column=item.column,
                    )
                output_ref = item.ref
                continue
            if isinstance(item, FinalOutputRoutePart):
                if route_path is not None:
                    raise TransformParseFailure(
                        "final_output block may define `route:` only once.",
                        hints=("Keep exactly one `route:` entry inside the final_output block.",),
                        line=item.line,
                        column=item.column,
                    )
                route_path = item.path
                continue
            if isinstance(item, FinalOutputReviewFieldsPart):
                if review_fields is not None:
                    raise TransformParseFailure(
                        "final_output block may define `review_fields:` only once.",
                        hints=(
                            "Keep exactly one `review_fields:` block inside the final_output block.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                review_fields = item.config

        if output_ref is None:
            raise TransformParseFailure(
                "final_output block is missing `output:`.",
                hints=("Add `output: OutputName` inside the final_output block.",),
            )

        return FinalOutputBodyParts(
            output_ref=output_ref,
            route_path=route_path,
            review_fields=review_fields,
        )
