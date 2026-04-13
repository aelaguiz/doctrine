from __future__ import annotations

import ast
from pathlib import Path

from lark import Lark, Transformer, v_args

from doctrine import model
from doctrine._parser.parts import *  # noqa: F401,F403
from doctrine._parser.readables import ReadableNodeTransformerMixin
from doctrine._parser.runtime import (
    build_lark_parser as _build_lark_parser,
    parse_file as _parse_file,
    parse_text as _parse_text,
)
from doctrine._parser.transformer import (
    DeclarationTransformerMixin,
    ReadableTransformerMixin,
    SchemaDocumentTransformerMixin,
)
from doctrine.diagnostics import TransformParseFailure


class ToAst(
    SchemaDocumentTransformerMixin,
    DeclarationTransformerMixin,
    ReadableNodeTransformerMixin,
    ReadableTransformerMixin,
    Transformer,
):
    def CNAME(self, token):
        return str(token)

    def DOTS(self, token):
        return str(token)

    def PATH_REF(self, token):
        return str(token)

    def ESCAPED_STRING(self, token):
        return ast.literal_eval(str(token))

    def MULTILINE_STRING(self, token):
        return ast.literal_eval(str(token))

    def SIGNED_NUMBER(self, token):
        return int(str(token))

    @v_args(inline=True)
    def start(self, prompt_file):
        return prompt_file

    def prompt_file(self, items):
        return model.PromptFile(declarations=tuple(items))

    @v_args(inline=True)
    def inheritance(self, parent_ref):
        return parent_ref

    def agent(self, items):
        return self._agent(items, abstract=False)

    def abstract_agent(self, items):
        return self._agent(items, abstract=True)

    @v_args(inline=True)
    def import_decl(self, path):
        return model.ImportDecl(path=path)

    def render_profile_decl(self, items):
        name = items[0]
        return model.RenderProfileDecl(name=name, rules=tuple(items[1:]))

    @v_args(inline=True)
    def render_profile_rule(self, target_parts, mode):
        return model.RenderProfileRule(target_parts=tuple(target_parts), mode=mode)

    @v_args(inline=True)
    def import_path(self, path):
        return path

    @v_args(inline=True)
    def absolute_import_path(self, module_parts):
        return model.ImportPath(level=0, module_parts=tuple(module_parts))

    @v_args(inline=True)
    def relative_import_path(self, dots, module_parts):
        return model.ImportPath(level=len(dots), module_parts=tuple(module_parts))

    def dotted_name(self, items):
        return tuple(items)

    @v_args(inline=True)
    def name_ref(self, dotted_name):
        parts = tuple(dotted_name)
        return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])

    @v_args(inline=True)
    def path_ref(self, raw_ref):
        root_name, path_name = raw_ref.split(":", 1)
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(root_name),
            path=tuple(path_name.split(".")),
        )

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return model.RoleScalar(text=title_or_text)
        return model.RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def inputs_inline_field(self, title, items):
        return model.InputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def inputs_ref_field(self, ref):
        return model.InputsField(title=None, value=ref)

    @v_args(inline=True)
    def inputs_patch_field(self, parent_ref, title, body):
        return model.InputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def outputs_inline_field(self, title, items):
        return model.OutputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def outputs_ref_field(self, ref):
        return model.OutputsField(title=None, value=ref)

    @v_args(inline=True)
    def outputs_patch_field(self, parent_ref, title, body):
        return model.OutputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def analysis_field(self, ref):
        return model.AnalysisField(value=ref)

    @v_args(inline=True)
    def decision_field(self, ref):
        return model.DecisionField(value=ref)

    @v_args(inline=True)
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def review_field(self, ref):
        return model.ReviewField(value=ref)

    @v_args(inline=True)
    def final_output_field(self, ref):
        return model.FinalOutputField(value=ref)

    @v_args(inline=True)
    def agent_slot_field(self, key, value, body=None):
        return model.AuthoredSlotField(key=key, value=self._workflow_slot_value(value, body))

    @v_args(inline=True)
    def agent_slot_abstract(self, key):
        return model.AuthoredSlotAbstract(key=key)

    @v_args(inline=True)
    def agent_slot_inherit(self, key):
        return model.AuthoredSlotInherit(key=key)

    @v_args(inline=True)
    def agent_slot_override(self, key, value, body=None):
        return model.AuthoredSlotOverride(
            key=key,
            value=self._workflow_slot_value(value, body),
        )

    def slot_body(self, items):
        return items[0]

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

    @v_args(inline=True)
    def workflow_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        workflow_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            workflow_body = body
        return model.WorkflowDecl(
            name=name,
            body=model.WorkflowBody(
                title=title,
                preamble=workflow_body.preamble,
                items=workflow_body.items,
                law=workflow_body.law,
            ),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def skills_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        skills_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            skills_body = body
        return model.SkillsDecl(
            name=name,
            body=model.SkillsBody(
                title=title,
                preamble=skills_body.preamble,
                items=skills_body.items,
            ),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def inputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.InputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def input_decl(self, name, title, body):
        return model.InputDecl(
            name=name,
            title=title,
            items=body.items,
            structure=body.structure,
        )

    @v_args(inline=True)
    def input_body_line(self, value):
        return value

    def input_body(self, items):
        record_items: list[model.RecordItem] = []
        structure: model.InputStructureConfig | None = None
        for item in items:
            if isinstance(item, InputStructurePart):
                if structure is not None:
                    raise TransformParseFailure(
                        "Input declarations may define `structure:` only once.",
                        hints=("Keep exactly one `structure:` attachment per input declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                structure = item.config
                continue
            record_items.append(item)
        return InputBodyParts(items=tuple(record_items), structure=structure)

    @v_args(meta=True, inline=True)
    def input_structure_stmt(self, meta, ref):
        return _positioned_input_structure(meta, ref)

    @v_args(inline=True)
    def input_source_decl(self, name, title, items):
        return model.InputSourceDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_decl(self, name, title, body):
        return model.OutputDecl(
            name=name,
            title=title,
            items=body.items,
            schema=body.schema,
            structure=body.structure,
            render_profile_ref=body.render_profile_ref,
            trust_surface=body.trust_surface,
        )

    @v_args(inline=True)
    def output_body_line(self, value):
        return value

    def output_body(self, items):
        record_items: list[model.OutputRecordItem] = []
        schema: model.OutputSchemaConfig | None = None
        structure: model.OutputStructureConfig | None = None
        render_profile_ref: model.NameRef | None = None
        trust_surface: tuple[model.TrustSurfaceItem, ...] = ()
        has_must_include = False
        for item in items:
            if isinstance(item, RenderProfilePart):
                if render_profile_ref is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `render_profile:` only once.",
                        hints=("Keep exactly one `render_profile:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                render_profile_ref = item.ref
                continue
            if isinstance(item, TrustSurfacePart):
                if trust_surface:
                    raise TransformParseFailure(
                        "Output declarations may define `trust_surface` only once.",
                        hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                trust_surface = item.items
                continue
            if isinstance(item, OutputSchemaPart):
                if schema is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `schema:` only once.",
                        hints=("Keep exactly one `schema:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                if structure is not None:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `structure:`.",
                        hints=(
                            "Pick one artifact owner per markdown output declaration.",
                            "Use `schema:` for reusable inventory ownership or `structure:` for reusable markdown structure, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                if has_must_include:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `must_include:`.",
                        hints=(
                            "Pick one inventory owner per output declaration.",
                            "Use `schema:` for reusable inventory ownership or keep local `must_include:` prose, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                schema = item.config
                continue
            if isinstance(item, OutputStructurePart):
                if structure is not None:
                    raise TransformParseFailure(
                        "Output declarations may define `structure:` only once.",
                        hints=("Keep exactly one `structure:` attachment per output declaration.",),
                        line=item.line,
                        column=item.column,
                    )
                if schema is not None:
                    raise TransformParseFailure(
                        "Outputs may not define both `schema:` and `structure:`.",
                        hints=(
                            "Pick one artifact owner per markdown output declaration.",
                            "Use `schema:` for reusable inventory ownership or `structure:` for reusable markdown structure, not both.",
                        ),
                        line=item.line,
                        column=item.column,
                    )
                structure = item.config
                continue
            if isinstance(item, OutputRecordSectionPart):
                if item.section.key == "must_include":
                    if schema is not None:
                        raise TransformParseFailure(
                            "Outputs may not define both `schema:` and `must_include:`.",
                            hints=(
                                "Pick one inventory owner per output declaration.",
                                "Use `schema:` for reusable inventory ownership or keep local `must_include:` prose, not both.",
                            ),
                            line=item.line,
                            column=item.column,
                        )
                    has_must_include = True
                record_items.append(item.section)
                continue
            record_items.append(item)
        return OutputBodyParts(
            items=tuple(record_items),
            schema=schema,
            structure=structure,
            render_profile_ref=render_profile_ref,
            trust_surface=trust_surface,
        )

    @v_args(meta=True, inline=True)
    def output_schema_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputSchemaPart(
            config=model.OutputSchemaConfig(schema_ref=ref),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_structure_stmt(self, meta, ref):
        line, column = _meta_line_column(meta)
        return OutputStructurePart(
            config=model.OutputStructureConfig(structure_ref=ref),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def output_render_profile_stmt(self, meta, ref):
        return _positioned_render_profile(meta, ref)

    def output_record_body(self, items):
        return tuple(
            item.section if isinstance(item, OutputRecordSectionPart) else item
            for item in items
        )

    @v_args(inline=True)
    def output_record_item(self, value):
        return value

    def output_record_item_body(self, items):
        return tuple(items[0])

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

    @v_args(inline=True)
    def decision_string(self, value):
        return value

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

    @v_args(meta=True, inline=True)
    def output_record_keyed_item(self, meta, key, head, body=None):
        if isinstance(head, str) and body is not None:
            line, column = _meta_line_column(meta)
            return OutputRecordSectionPart(
                section=model.RecordSection(key=key, title=head, items=tuple(body)),
                line=line,
                column=column,
            )
        return model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def output_record_ref_item(self, ref, body=None):
        return model.RecordRef(ref=ref, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def guarded_output_section(self, key, title, when_expr, items):
        return model.GuardedOutputSection(
            key=key,
            title=title,
            when_expr=when_expr,
            items=tuple(items),
        )

    @v_args(inline=True)
    def guarded_output_scalar_item(self, key, head, when_expr, body=None):
        return model.GuardedOutputScalar(
            key=key,
            value=head,
            when_expr=when_expr,
            body=None if body is None else tuple(body),
        )

    @v_args(meta=True)
    def trust_surface_block(self, meta, items):
        return _positioned_trust_surface(meta, tuple(items))

    @v_args(inline=True)
    def trust_surface_item(self, path, when_expr=None):
        return model.TrustSurfaceItem(path=tuple(path), when_expr=when_expr)

    @v_args(inline=True)
    def trust_surface_when(self, expr):
        return expr

    @v_args(inline=True)
    def outputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.OutputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def output_target_decl(self, name, title, items):
        return model.OutputTargetDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_shape_decl(self, name, title, items):
        return model.OutputShapeDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def json_schema_decl(self, name, title, items):
        return model.JsonSchemaDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def skill_package_decl(self, name, title, body):
        return model.SkillPackageDecl(
            name=name,
            title=title,
            items=body.items,
            metadata=body.metadata,
        )

    @v_args(inline=True)
    def skill_decl(self, name, title, items):
        return model.SkillDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def enum_decl(self, name, title, members):
        return model.EnumDecl(name=name, title=title, members=tuple(members))

    def enum_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def enum_member(self, key, title, body=None):
        wire: str | None = None
        for item in body or ():
            if isinstance(item, EnumMemberFieldPart):
                field_key = item.key
                field_value = item.value
                line, column = item.line, item.column
            else:
                field_key, field_value = item
                line, column = None, None
            if field_key != "wire":
                raise TransformParseFailure(
                    f"Unknown enum member field: {field_key}",
                    hints=("Only `wire:` is legal inside an enum-member body.",),
                    line=line,
                    column=column,
                )
            if wire is not None:
                raise TransformParseFailure(
                    "Enum member may declare `wire` at most once.",
                    hints=("Keep one `wire:` field per enum member.",),
                    line=line,
                    column=column,
                )
            wire = field_value
        return model.EnumMember(key=key, title=title, wire=wire)

    def enum_member_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def enum_member_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def enum_member_wire_stmt(self, meta, value):
        return _positioned_enum_member_field(meta, "wire", value)

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

    def workflow_preamble(self, items):
        return tuple(items)

    def workflow_items(self, items):
        return tuple(items)

    @v_args(meta=True, inline=True)
    def workflow_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def workflow_body_line(self, value):
        return value

    @v_args(meta=True, inline=True)
    def skills_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def skills_body_line(self, value):
        return value

    @v_args(inline=True)
    def required_line(self, _keyword, text):
        return model.EmphasizedLine(kind="required", text=text)

    @v_args(inline=True)
    def important_line(self, _keyword, text):
        return model.EmphasizedLine(kind="important", text=text)

    @v_args(inline=True)
    def warning_line(self, _keyword, text):
        return model.EmphasizedLine(kind="warning", text=text)

    @v_args(inline=True)
    def note_line(self, _keyword, text):
        return model.EmphasizedLine(kind="note", text=text)

    def workflow_body(self, items):
        preamble: list[model.ProseLine] = []
        workflow_items: list[model.WorkflowItem] = []
        law: model.LawBody | None = None
        for item in items:
            law_body = item.body if isinstance(item, WorkflowLawPart) else item if isinstance(item, model.LawBody) else None
            if law_body is not None:
                if law is not None:
                    line, column = _item_line_column(item)
                    raise TransformParseFailure(
                        "Workflow declarations may define `law` only once.",
                        hints=("Keep exactly one `law:` block per workflow body.",),
                        line=line,
                        column=column,
                    )
                law = law_body
                continue
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if workflow_items or law is not None:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Workflow prose lines must appear before keyed workflow entries.",
                        hints=(
                            "Move prose lines to the top of the workflow body or put them inside a titled section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            workflow_items.append(item)
        return WorkflowBodyParts(
            preamble=tuple(preamble),
            items=tuple(workflow_items),
            law=law,
        )

    def workflow_section_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def workflow_section_ref_item(self, ref):
        if isinstance(ref, model.NameRef):
            ref = model.AddressableRef(root=ref)
        return model.SectionBodyRef(ref=ref)

    @v_args(inline=True)
    def local_section(self, key, title, items):
        return model.LocalSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def workflow_readable_block(self, value):
        return value

    @v_args(inline=True)
    def workflow_section_block(self, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    @v_args(inline=True)
    def workflow_use(self, key, target):
        return model.WorkflowUse(key=key, target=target)

    @v_args(inline=True)
    def workflow_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def workflow_skills_inline(self, title, body):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_skills_ref(self, ref):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_skills_inline(self, title, body):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_override_skills_ref(self, ref):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSection(key=key, title=title, items=tuple(section_items))

    @v_args(inline=True)
    def workflow_override_use(self, key, target):
        return model.OverrideUse(key=key, target=target)

    @v_args(meta=True, inline=True)
    def law_block(self, meta, body):
        return _positioned_workflow_law(meta, body)

    def law_body(self, items):
        return model.LawBody(items=tuple(items))

    def law_section(self, items):
        return model.LawSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def law_inherit(self, key):
        return model.LawInherit(key=key)

    def law_override_section(self, items):
        return model.LawOverrideSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def active_when_stmt(self, expr):
        return model.ActiveWhenStmt(expr=expr)

    @v_args(inline=True)
    def mode_stmt(self, name, expr, enum_ref):
        return model.ModeStmt(name=name, expr=expr, enum_ref=enum_ref)

    @v_args(inline=True)
    def must_stmt(self, expr):
        return model.MustStmt(expr=expr)

    @v_args(inline=True)
    def current_artifact_stmt(self, target, carrier):
        return model.CurrentArtifactStmt(target=target, carrier=carrier)

    def current_none_stmt(self, _items):
        return model.CurrentNoneStmt()

    @v_args(inline=True)
    def own_only_stmt(self, target, when_expr=None):
        return model.OwnOnlyStmt(target=target, when_expr=when_expr)

    def preserve_stmt(self, items):
        kind = items[0]
        target = items[1]
        when_expr: model.Expr | None = items[2] if len(items) > 2 else None
        return model.PreserveStmt(kind=kind, target=target, when_expr=when_expr)

    @v_args(inline=True)
    def support_only_stmt(self, target, when_expr=None):
        return model.SupportOnlyStmt(target=target, when_expr=when_expr)

    def ignore_stmt(self, items):
        target = items[0]
        bases: tuple[str, ...] = ()
        when_expr: model.Expr | None = None
        for extra in items[1:]:
            if isinstance(extra, tuple):
                bases = extra
            else:
                when_expr = extra
        return model.IgnoreStmt(target=target, bases=bases, when_expr=when_expr)

    @v_args(inline=True)
    def invalidate_stmt(self, target, carrier, when_expr=None):
        return model.InvalidateStmt(target=target, carrier=carrier, when_expr=when_expr)

    @v_args(inline=True)
    def forbid_stmt(self, target, when_expr=None):
        return model.ForbidStmt(target=target, when_expr=when_expr)

    def when_stmt(self, items):
        return model.WhenStmt(expr=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def match_stmt(self, expr, *cases):
        return model.MatchStmt(expr=expr, cases=tuple(cases))

    def match_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.MatchArm(head=head, items=tuple(items[1:]))

    @v_args(inline=True)
    def route_from_stmt(self, expr, enum_ref, *cases):
        return model.RouteFromStmt(expr=expr, enum_ref=enum_ref, cases=tuple(cases))

    def route_from_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.RouteFromArm(head=head, route=items[1])

    def else_match_head(self, _items):
        return "__ELSE__"

    @v_args(inline=True)
    def stop_stmt(self, message=None, when_expr=None):
        if message is not None and not isinstance(message, str):
            when_expr = message
            message = None
        return model.StopStmt(message=message, when_expr=when_expr)

    @v_args(inline=True)
    def law_route_stmt(self, label, target, when_expr=None):
        return model.LawRouteStmt(label=label, target=target, when_expr=when_expr)

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

    def preserve_exact(self, _items):
        return "exact"

    def preserve_structure(self, _items):
        return "structure"

    def preserve_decisions(self, _items):
        return "decisions"

    def preserve_mapping(self, _items):
        return "mapping"

    def preserve_vocabulary(self, _items):
        return "vocabulary"

    def ignore_basis_list(self, items):
        return tuple(items)

    def ignore_basis_truth(self, _items):
        return "truth"

    def ignore_basis_comparison(self, _items):
        return "comparison"

    def ignore_basis_rewrite_evidence(self, _items):
        return "rewrite_evidence"

    @v_args(inline=True)
    def law_when_clause(self, expr):
        return expr

    def path_set_expr(self, items):
        paths: list[model.LawPath] = []
        except_paths: list[model.LawPath] = []
        if items:
            first = items[0]
            if isinstance(first, tuple):
                paths.extend(first)
            else:
                paths.append(first)
            for extra in items[1:]:
                if isinstance(extra, tuple):
                    except_paths.extend(extra)
                else:
                    except_paths.append(extra)
        return model.LawPathSet(paths=tuple(paths), except_paths=tuple(except_paths))

    def path_set_base(self, items):
        if len(items) == 1 and isinstance(items[0], model.LawPath):
            return items[0]
        return tuple(items)

    def law_path(self, items):
        parts = list(items[0])
        wildcard = len(items) > 1
        return model.LawPath(parts=tuple(parts), wildcard=wildcard)

    def law_path_wildcard(self, _items):
        return "*"

    def field_path(self, items):
        return tuple(items)

    @v_args(inline=True)
    def expr_ref(self, parts):
        return model.ExprRef(parts=tuple(parts))

    @v_args(inline=True)
    def expr_number(self, value):
        return value

    def expr_true(self, _items):
        return True

    def expr_false(self, _items):
        return False

    def expr_call(self, items):
        return model.ExprCall(name=items[0], args=tuple(items[1:]))

    def expr_set(self, items):
        return model.ExprSet(items=tuple(items))

    @v_args(inline=True)
    def expr_or(self, left, right):
        return model.ExprBinary(op="or", left=left, right=right)

    @v_args(inline=True)
    def expr_and(self, left, right):
        return model.ExprBinary(op="and", left=left, right=right)

    @v_args(inline=True)
    def expr_eq(self, left, right):
        return model.ExprBinary(op="==", left=left, right=right)

    @v_args(inline=True)
    def expr_ne(self, left, right):
        return model.ExprBinary(op="!=", left=left, right=right)

    @v_args(inline=True)
    def expr_gt(self, left, right):
        return model.ExprBinary(op=">", left=left, right=right)

    @v_args(inline=True)
    def expr_gte(self, left, right):
        return model.ExprBinary(op=">=", left=left, right=right)

    @v_args(inline=True)
    def expr_lt(self, left, right):
        return model.ExprBinary(op="<", left=left, right=right)

    @v_args(inline=True)
    def expr_lte(self, left, right):
        return model.ExprBinary(op="<=", left=left, right=right)

    @v_args(inline=True)
    def expr_in(self, left, right):
        return model.ExprBinary(op="in", left=left, right=right)

    @v_args(inline=True)
    def expr_not_in(self, left, right):
        return model.ExprBinary(op="not in", left=left, right=right)

    @v_args(inline=True)
    def skill_entry(self, key, target, body=None):
        return model.SkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(inline=True)
    def skills_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def skills_override_entry(self, key, target, body=None):
        return model.OverrideSkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(inline=True)
    def skills_section(self, key, title, items):
        return model.SkillsSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def skills_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSkillsSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    @v_args(meta=True, inline=True)
    def io_string(self, meta, value):
        return _positioned_body_prose(meta, value)

    @v_args(inline=True)
    def io_body_line(self, value):
        return value

    def io_body(self, items):
        preamble: list[model.ProseLine] = []
        io_items: list[model.IoItem] = []
        for item in items:
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if io_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Inputs and outputs prose lines must appear before keyed entries.",
                        hints=(
                            "Move prose lines to the top of the inputs or outputs body or put them inside a titled section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            io_items.append(item)
        return IoBodyParts(preamble=tuple(preamble), items=tuple(io_items))

    @v_args(inline=True)
    def io_section(self, key, title, items):
        return model.RecordSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def io_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def io_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideIoSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    def record_body(self, items):
        return tuple(items)

    def skill_package_body(self, items):
        record_items: list[model.RecordItem] = []
        metadata = model.SkillPackageMetadata()
        seen_metadata = False
        for item in items:
            if isinstance(item, SkillPackageMetadataBlockPart):
                if seen_metadata:
                    raise TransformParseFailure(
                        "Skill packages may define `metadata:` only once.",
                        hints=("Keep exactly one `metadata:` block per skill package.",),
                        line=item.line,
                        column=item.column,
                )
                metadata = self._skill_package_metadata(item.fields)
                seen_metadata = True
                continue
            record_items.append(item)
        return SkillPackageBodyParts(
            items=tuple(record_items),
            metadata=metadata,
        )

    @v_args(inline=True)
    def record_text(self, value):
        return value

    @v_args(meta=True)
    def package_metadata_block(self, meta, items):
        line, column = _meta_line_column(meta)
        return SkillPackageMetadataBlockPart(
            fields=tuple(items),
            line=line,
            column=column,
        )

    @v_args(meta=True, inline=True)
    def package_metadata_item(self, meta, key, value):
        line, column = _meta_line_column(meta)
        return SkillPackageMetadataFieldPart(
            key=key,
            value=value,
            line=line,
            column=column,
        )

    @v_args(inline=True)
    def record_readable_block(self, value):
        return value

    @v_args(inline=True)
    def record_section_block(self, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    @v_args(inline=True)
    def output_readable_block(self, value):
        return value

    @v_args(inline=True)
    def output_section_block(self, key, title, *parts):
        requirement, when_expr, item_schema, row_schema, payload = self._split_readable_parts(parts)
        return model.ReadableBlock(
            kind="section",
            key=key,
            title=title,
            payload=tuple(payload),
            requirement=requirement,
            when_expr=when_expr,
            item_schema=item_schema,
            row_schema=row_schema,
        )

    def record_item_body(self, items):
        return tuple(items[0])

    @v_args(inline=True)
    def record_keyed_item(self, key, head, body=None):
        if isinstance(head, str) and body is not None:
            return model.RecordSection(key=key, title=head, items=tuple(body))
        return model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def record_ref_item(self, ref, body=None):
        return model.RecordRef(ref=ref, body=None if body is None else tuple(body))

    def skills_body(self, items):
        preamble: list[model.ProseLine] = []
        skills_items: list[model.SkillsItem] = []
        for item in items:
            prose_value = _body_prose_value(item)
            if prose_value is not None:
                if skills_items:
                    line, column = _body_prose_location(item)
                    raise TransformParseFailure(
                        "Skills prose lines must appear before keyed skills entries.",
                        hints=(
                            "Move prose lines to the top of the skills body or put them inside a titled skills section.",
                        ),
                        line=line,
                        column=column,
                    )
                preamble.append(prose_value)
                continue
            skills_items.append(item)
        return SkillsBodyParts(preamble=tuple(preamble), items=tuple(skills_items))

    def skills_section_body(self, items):
        return tuple(items)

    def skill_entry_body(self, items):
        return tuple(items[0])

    def ref_list(self, items):
        return tuple(items)

    @v_args(inline=True)
    def ref_item(self, ref):
        return ref

    @v_args(inline=True)
    def route_stmt(self, label, target):
        return model.RouteLine(label=label, target=target)

    def block_lines(self, items):
        return tuple(items)

def build_lark_parser() -> Lark:
    return _build_lark_parser()


def parse_text(source: str, *, source_path: str | Path | None = None) -> model.PromptFile:
    return _parse_text(
        source,
        source_path=source_path,
        transform=lambda tree: ToAst().transform(tree),
    )


def parse_file(path: str | Path) -> model.PromptFile:
    return _parse_file(path, transform=lambda tree: ToAst().transform(tree))
