from __future__ import annotations

from lark import v_args

from doctrine import model
from doctrine._parser.parts import (
    FinalOutputBodyParts,
    FinalOutputOutputPart,
    FinalOutputReviewFieldsPart,
    _meta_line_column,
)
from doctrine.diagnostics import TransformParseFailure


class AgentTransformerMixin:
    """Shared agent and agent-field lowering for the public parser boundary."""

    def agent(self, items):
        return self._agent(items, abstract=False)

    def abstract_agent(self, items):
        return self._agent(items, abstract=True)

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return model.RoleScalar(text=title_or_text)
        return model.RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def review_field(self, ref):
        return model.ReviewField(value=ref)

    @v_args(inline=True)
    def final_output_field(self, ref_or_body):
        if isinstance(ref_or_body, FinalOutputBodyParts):
            return model.FinalOutputField(
                value=ref_or_body.output_ref,
                review_fields=ref_or_body.review_fields,
            )
        return model.FinalOutputField(value=ref_or_body)

    @v_args(meta=True, inline=True)
    def final_output_output_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return FinalOutputOutputPart(ref=ref, line=line, column=column)

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

        return FinalOutputBodyParts(output_ref=output_ref, review_fields=review_fields)
