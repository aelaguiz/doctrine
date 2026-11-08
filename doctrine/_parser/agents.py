from __future__ import annotations

from lark import v_args
from dataclasses import replace

from doctrine import model
from doctrine._model.core import role_text
from doctrine._parser.parts import (
    FinalOutputBodyParts,
    FinalOutputOutputPart,
    FinalOutputRoutePart,
    FinalOutputReviewFieldsPart,
    _flatten_grouped_items,
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

    @v_args(meta=True)
    def values_block(self, meta, items):
        return _with_source_span(model.ValuesField(items=tuple(items)), meta)

    @v_args(meta=True, inline=True)
    def value_item(self, meta, key, value):
        return key, value, _source_span_from_meta(meta)

    @v_args(meta=True)
    def budget_block(self, meta, items):
        return _with_source_span(model.BudgetField(items=tuple(items)), meta)

    def budget_item(self, items):
        return str(items[0]), float(items[1])

    def team_body(self, items):
        return items

    def member_body(self, items):
        return items

    def team_home_stmt(self, items):
        return ("home", items[0])

    def quote_by(self, items): return "by", items[0]
    def quote_on(self, items): return "on", items[0]
    def quote_to(self, items): return "to", items[0]
    def quote_about(self, items): return "about", items[0]
    def quote_source(self, items): return "source", items[0]
    def quote_context(self, items): return "context", items[0]

    @v_args(meta=True)
    def quote_decl(self, meta, items):
        return _with_source_span(model.Quote(items[0], items[1], tuple(items[2:])), meta)

    def person_owned_item(self, items):
        return items[0]

    def person_body(self, items):
        return tuple(items)

    @v_args(meta=True)
    def person_decl(self, meta, items):
        return _with_source_span(model.Person(items[0], items[1], items[2] if len(items) > 2 else ()), meta)

    @v_args(meta=True)
    def team_decl(self, meta, items):
        return self._team(items, abstract=False, source_span=_source_span_from_meta(meta))

    @v_args(meta=True)
    def abstract_team_decl(self, meta, items):
        return self._team(items, abstract=True, source_span=_source_span_from_meta(meta))

    def _team(self, items, *, abstract, source_span):
        head = self._agent(items[:-1], abstract=False, source_span=source_span)
        body = items[-1]
        return model.Team(
            name=head.name, title=head.title, abstract=abstract, parent_ref=head.parent_ref,
            fields=_flatten_grouped_items(body),
            home=next((item[1] for item in body if isinstance(item, tuple)), None),
            source_span=source_span,
        )

    @v_args(meta=True)
    def member_decl(self, meta, items):
        head_items = [*items[:-1], *items[-1]] if isinstance(items[-1], list) else items
        head = self._agent(head_items, abstract=False, source_span=_source_span_from_meta(meta))
        return model.Member(
            name=head.name, title=head.title, parent_ref=head.parent_ref,
            fields=head.fields, source_span=head.source_span,
        )

    @v_args(meta=True)
    def member_override_decl(self, meta, items):
        return replace(self.member_decl(meta, items), override=True)

    @v_args(meta=True, inline=True)
    def abstract_agent_markdown(self, meta, name, path):
        return _with_source_span(model.Agent(name=name, fields=(), abstract=True, markdown_path=path), meta)

    @v_args(meta=True, inline=True)
    def workflow_markdown(self, meta, name, path):
        return _with_source_span(model.WorkflowDecl(name=name, body=model.WorkflowBody(
            title=name, preamble=(), items=()), markdown_path=path), meta)

    def role_body(self, items):
        return items[0]

    def role_prose(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def role_paragraph(self, meta, key, *parts):
        title = parts[0] if len(parts) == 2 else None
        return _with_source_span(model.ReadableBlock("paragraph", key, title, tuple(parts[-1])), meta)

    @v_args(meta=True)
    def role_paragraphs(self, meta, items):
        return _with_source_span(model.RoleScalar(text=role_text(items) if all(isinstance(item, model.ReadableBlock) for item in items) else "", paragraphs=tuple(items)), meta)

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
