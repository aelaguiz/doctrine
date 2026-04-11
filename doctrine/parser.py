from __future__ import annotations

import ast
import threading
from dataclasses import dataclass, replace
from pathlib import Path

from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, VisitError

from doctrine import model
from doctrine.diagnostics import ParseError, TransformParseFailure
from doctrine.indenter import DoctrineIndenter


@dataclass(slots=True, frozen=True)
class WorkflowBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.WorkflowItem, ...]
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class SkillsBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SkillsItem, ...]


@dataclass(slots=True, frozen=True)
class IoBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.IoItem, ...]


@dataclass(slots=True, frozen=True)
class OutputBodyParts:
    items: tuple[model.OutputRecordItem, ...]
    trust_surface: tuple[model.TrustSurfaceItem, ...]


@dataclass(slots=True, frozen=True)
class ReviewBodyParts:
    items: tuple[model.ReviewItem, ...]


@dataclass(slots=True, frozen=True)
class AnalysisBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.AnalysisItem, ...]


@dataclass(slots=True, frozen=True)
class SchemaBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SchemaItem, ...]


@dataclass(slots=True, frozen=True)
class DocumentBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.DocumentItem, ...]


class ToAst(Transformer):
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

    def _agent(self, items, *, abstract: bool):
        name = items[0]
        parent_ref: model.NameRef | None = None
        fields_start = 1
        if len(items) > 1 and isinstance(items[1], model.NameRef):
            parent_ref = items[1]
            fields_start = 2
        return model.Agent(
            name=name,
            fields=tuple(items[fields_start:]),
            abstract=abstract,
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def import_decl(self, path):
        return model.ImportDecl(path=path)

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
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def review_field(self, ref):
        return model.ReviewField(value=ref)

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

    def _workflow_slot_value(
        self,
        value: str | model.NameRef,
        body: WorkflowBodyParts | None,
    ) -> model.WorkflowSlotValue:
        if body is None:
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Authored workflow slot references cannot also define an inline body.")
        return model.WorkflowBody(
            title=value,
            preamble=body.preamble,
            items=body.items,
            law=body.law,
        )

    def _skills_value(
        self,
        value: str | model.NameRef,
        body: SkillsBodyParts | None,
    ) -> model.SkillsValue:
        if body is None:
            if isinstance(value, str):
                raise ValueError("Inline skills blocks must define an indented body.")
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Skills references cannot also define an inline body.")
        return model.SkillsBody(title=value, preamble=body.preamble, items=body.items)

    def _io_body(self, title: str, body: IoBodyParts) -> model.IoBody:
        return model.IoBody(title=title, preamble=body.preamble, items=body.items)

    def slot_body(self, items):
        return items[0]

    def abstract_review_decl(self, items):
        return self._review_decl(items, abstract=True)

    def review_decl(self, items):
        return self._review_decl(items, abstract=False)

    def _review_decl(self, items, *, abstract: bool):
        name = items[0]
        parent_ref: model.NameRef | None = None
        title = items[1]
        review_body = items[2]
        if len(items) == 4:
            parent_ref = items[1]
            title = items[2]
            review_body = items[3]
        return model.ReviewDecl(
            name=name,
            body=model.ReviewBody(title=title, items=review_body.items),
            abstract=abstract,
            parent_ref=parent_ref,
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
        )

    @v_args(inline=True)
    def schema_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        schema_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            schema_body = body
        return model.SchemaDecl(
            name=name,
            body=model.SchemaBody(
                title=title,
                preamble=schema_body.preamble,
                items=schema_body.items,
            ),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def document_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        document_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            document_body = body
        return model.DocumentDecl(
            name=name,
            body=model.DocumentBody(
                title=title,
                preamble=document_body.preamble,
                items=document_body.items,
            ),
            parent_ref=parent_ref,
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
    def input_decl(self, name, title, items):
        return model.InputDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def input_source_decl(self, name, title, items):
        return model.InputSourceDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_decl(self, name, title, body):
        return model.OutputDecl(
            name=name,
            title=title,
            items=body.items,
            trust_surface=body.trust_surface,
        )

    @v_args(inline=True)
    def output_body_line(self, value):
        return value

    def output_body(self, items):
        record_items: list[model.OutputRecordItem] = []
        trust_surface: tuple[model.TrustSurfaceItem, ...] = ()
        for item in items:
            if isinstance(item, tuple) and item and isinstance(item[0], model.TrustSurfaceItem):
                if trust_surface:
                    raise TransformParseFailure(
                        "Output declarations may define `trust_surface` only once.",
                        hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                    )
                trust_surface = tuple(item)
                continue
            record_items.append(item)
        return OutputBodyParts(items=tuple(record_items), trust_surface=trust_surface)

    def output_record_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def output_record_item(self, value):
        return value

    def output_record_item_body(self, items):
        return tuple(items[0])

    @v_args(inline=True)
    def analysis_string(self, value):
        return value

    @v_args(inline=True)
    def analysis_body_line(self, value):
        return value

    def analysis_body(self, items):
        preamble: list[model.ProseLine] = []
        analysis_items: list[model.AnalysisItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if analysis_items:
                    raise TransformParseFailure(
                        "Analysis prose lines must appear before keyed analysis entries.",
                        hints=(
                            "Move prose lines to the top of the analysis body or put them inside a titled analysis section.",
                        ),
                    )
                preamble.append(item)
                continue
            analysis_items.append(item)
        return AnalysisBodyParts(preamble=tuple(preamble), items=tuple(analysis_items))

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
    def schema_string(self, value):
        return value

    @v_args(inline=True)
    def schema_body_line(self, value):
        return value

    def schema_body(self, items):
        preamble: list[model.ProseLine] = []
        schema_items: list[model.SchemaItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if schema_items:
                    raise TransformParseFailure(
                        "Schema prose lines must appear before keyed schema entries.",
                        hints=(
                            "Move prose lines to the top of the schema body or put them inside a schema section.",
                        ),
                    )
                preamble.append(item)
                continue
            schema_items.append(item)
        return SchemaBodyParts(preamble=tuple(preamble), items=tuple(schema_items))

    @v_args(inline=True)
    def schema_section(self, key, title, items):
        return model.SchemaSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def schema_gate(self, key, title):
        return model.SchemaGate(key=key, title=title)

    @v_args(inline=True)
    def schema_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def schema_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.SchemaOverrideSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    @v_args(inline=True)
    def schema_override_gate(self, key, title):
        return model.SchemaOverrideGate(key=key, title=title)

    @v_args(inline=True)
    def document_string(self, value):
        return value

    @v_args(inline=True)
    def document_body_line(self, value):
        return value

    def document_body(self, items):
        preamble: list[model.ProseLine] = []
        document_items: list[model.DocumentItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if document_items:
                    raise TransformParseFailure(
                        "Document prose lines must appear before keyed document blocks.",
                        hints=(
                            "Move prose lines to the top of the document body or put them inside a document block.",
                        ),
                    )
                preamble.append(item)
                continue
            document_items.append(item)
        return DocumentBodyParts(preamble=tuple(preamble), items=tuple(document_items))

    @v_args(inline=True)
    def document_block(self, kind, key, title, items):
        return model.DocumentBlock(kind=kind, key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def document_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def document_override_block(self, kind, key, title_or_items, items=None):
        title: str | None = None
        block_items = title_or_items
        if items is not None:
            title = title_or_items
            block_items = items
        return model.DocumentOverrideBlock(
            kind=kind,
            key=key,
            title=title,
            items=tuple(block_items),
        )

    def document_block_kind_section(self, _items):
        return "section"

    def document_block_kind_sequence(self, _items):
        return "sequence"

    def document_block_kind_bullets(self, _items):
        return "bullets"

    def document_block_kind_checklist(self, _items):
        return "checklist"

    def document_block_kind_definitions(self, _items):
        return "definitions"

    def document_block_kind_table(self, _items):
        return "table"

    def document_block_kind_callout(self, _items):
        return "callout"

    def document_block_kind_code(self, _items):
        return "code"

    def document_block_kind_rule(self, _items):
        return "rule"

    @v_args(inline=True)
    def output_record_keyed_item(self, key, head, body=None):
        if isinstance(head, str) and body is not None:
            return model.RecordSection(key=key, title=head, items=tuple(body))
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

    def trust_surface_block(self, items):
        return tuple(items)

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
    def skill_decl(self, name, title, items):
        return model.SkillDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def enum_decl(self, name, title, members):
        return model.EnumDecl(name=name, title=title, members=tuple(members))

    def enum_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def enum_member(self, key, value):
        return model.EnumMember(key=key, value=value)

    def review_body(self, items):
        return ReviewBodyParts(items=tuple(items))

    def artifact_subject_expr(self, items):
        return tuple(items)

    @v_args(inline=True)
    def artifact_ref(self, ref):
        return ref

    @v_args(inline=True)
    def enum_member_ref(self, ref):
        return ref

    @v_args(inline=True)
    def workflow_ref(self, ref):
        return ref

    @v_args(inline=True)
    def output_ref(self, ref):
        return ref

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
    def contract_stmt(self, workflow_ref):
        return model.ReviewContractConfig(workflow_ref=workflow_ref)

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

    @v_args(inline=True)
    def workflow_string(self, value):
        return value

    @v_args(inline=True)
    def workflow_body_line(self, value):
        return value

    @v_args(inline=True)
    def skills_string(self, value):
        return value

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
            if isinstance(item, model.LawBody):
                if law is not None:
                    raise TransformParseFailure(
                        "Workflow declarations may define `law` only once.",
                        hints=("Keep exactly one `law:` block per workflow body.",),
                    )
                law = item
                continue
            if isinstance(item, (str, model.EmphasizedLine)):
                if workflow_items or law is not None:
                    raise TransformParseFailure(
                        "Workflow prose lines must appear before keyed workflow entries.",
                        hints=(
                            "Move prose lines to the top of the workflow body or put them inside a titled section.",
                        ),
                    )
                preamble.append(item)
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

    @v_args(inline=True)
    def law_block(self, body):
        return body

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
    def current_review_artifact_stmt(self, artifact_ref, carrier):
        return model.ReviewCurrentArtifactStmt(artifact_ref=artifact_ref, carrier=carrier)

    def current_review_none_stmt(self, _items):
        return model.ReviewCurrentNoneStmt()

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

    @v_args(inline=True)
    def io_string(self, value):
        return value

    @v_args(inline=True)
    def io_body_line(self, value):
        return value

    def io_body(self, items):
        preamble: list[model.ProseLine] = []
        io_items: list[model.IoItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if io_items:
                    raise TransformParseFailure(
                        "Inputs and outputs prose lines must appear before keyed entries.",
                        hints=(
                            "Move prose lines to the top of the inputs or outputs body or put them inside a titled section.",
                        ),
                    )
                preamble.append(item)
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

    @v_args(inline=True)
    def record_text(self, value):
        return value

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
            if isinstance(item, (str, model.EmphasizedLine)):
                if skills_items:
                    raise TransformParseFailure(
                        "Skills prose lines must appear before keyed skills entries.",
                        hints=(
                            "Move prose lines to the top of the skills body or put them inside a titled skills section.",
                        ),
                    )
                preamble.append(item)
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
    parser = getattr(_THREAD_LOCAL_STATE, "lark_parser", None)
    if parser is None:
        parser = Lark.open(
            "grammars/doctrine.lark",
            rel_to=__file__,
            parser="lalr",
            lexer="contextual",
            postlex=DoctrineIndenter(),
            strict=True,
            maybe_placeholders=False,
        )
        _THREAD_LOCAL_STATE.lark_parser = parser
    return parser


def parse_text(source: str, *, source_path: str | Path | None = None) -> model.PromptFile:
    resolved_path = Path(source_path).resolve() if source_path is not None else None
    try:
        tree = build_lark_parser().parse(source)
    except UnexpectedInput as exc:
        raise ParseError.from_lark(source=source, path=resolved_path, exc=exc) from exc
    try:
        return ToAst().transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, ValueError):
            raise ParseError.from_transform(source=source, path=resolved_path, exc=exc) from exc
        raise


def parse_file(path: str | Path) -> model.PromptFile:
    resolved_path = Path(path).resolve()
    prompt_file = parse_text(resolved_path.read_text(), source_path=resolved_path)
    return replace(prompt_file, source_path=resolved_path)


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


_THREAD_LOCAL_STATE = threading.local()
