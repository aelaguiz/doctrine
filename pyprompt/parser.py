from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, VisitError

from pyprompt import model
from pyprompt.diagnostics import ParseError, TransformParseFailure
from pyprompt.indenter import PyPromptIndenter


@dataclass(slots=True, frozen=True)
class WorkflowBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.WorkflowItem, ...]


@dataclass(slots=True, frozen=True)
class SkillsBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SkillsItem, ...]


@dataclass(slots=True, frozen=True)
class IoBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.IoItem, ...]


class ToAst(Transformer):
    def CNAME(self, token):
        return str(token)

    def DOTS(self, token):
        return str(token)

    def ESCAPED_STRING(self, token):
        return ast.literal_eval(str(token))

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
    def outcome_field(self, title, items):
        return model.OutcomeField(title=title, items=tuple(items))

    @v_args(inline=True)
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def agent_slot_field(self, key, value, body=None):
        return model.AuthoredSlotField(key=key, value=self._workflow_slot_value(value, body))

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
        return model.WorkflowBody(title=value, preamble=body.preamble, items=body.items)

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
    def output_decl(self, name, title, items):
        return model.OutputDecl(name=name, title=title, items=tuple(items))

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
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if workflow_items:
                    raise TransformParseFailure(
                        "Workflow prose lines must appear before keyed workflow entries.",
                        hints=(
                            "Move prose lines to the top of the workflow body or put them inside a titled section.",
                        ),
                    )
                preamble.append(item)
                continue
            workflow_items.append(item)
        return WorkflowBodyParts(preamble=tuple(preamble), items=tuple(workflow_items))

    def workflow_section_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def workflow_section_ref_item(self, ref):
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


@lru_cache(maxsize=1)
def build_lark_parser() -> Lark:
    return Lark.open(
        "grammars/pyprompt.lark",
        rel_to=__file__,
        parser="lalr",
        lexer="contextual",
        postlex=PyPromptIndenter(),
        strict=True,
        maybe_placeholders=False,
    )


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
