from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from lark import Lark, Transformer, v_args

from pyprompt import model
from pyprompt.indenter import PyPromptIndenter


@dataclass(slots=True, frozen=True)
class WorkflowBodyParts:
    preamble: tuple[str, ...]
    items: tuple[model.WorkflowItem, ...]


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
    def inheritance(self, parent_name):
        return parent_name

    def agent(self, items):
        return self._agent(items, abstract=False)

    def abstract_agent(self, items):
        return self._agent(items, abstract=True)

    def _agent(self, items, *, abstract: bool):
        name = items[0]
        parent_name: str | None = None
        fields_start = 1
        if len(items) > 1 and isinstance(items[1], str):
            parent_name = items[1]
            fields_start = 2
        return model.Agent(
            name=name,
            fields=tuple(items[fields_start:]),
            abstract=abstract,
            parent_name=parent_name,
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
    def inputs_field(self, title, refs):
        return model.InputsField(title=title, refs=tuple(refs))

    @v_args(inline=True)
    def outputs_field(self, title, refs):
        return model.OutputsField(title=title, refs=tuple(refs))

    @v_args(inline=True)
    def outcome_field(self, title, items):
        return model.OutcomeField(title=title, items=tuple(items))

    @v_args(inline=True)
    def skills_field(self, title, items):
        return model.SkillsField(title=title, items=tuple(items))

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

    def slot_body(self, items):
        return items[0]

    @v_args(inline=True)
    def workflow_decl(self, name, parent_name_or_title, title_or_body, body=None):
        parent_name: str | None = None
        title = parent_name_or_title
        workflow_body = title_or_body
        if body is not None:
            parent_name = parent_name_or_title
            title = title_or_body
            workflow_body = body
        return model.WorkflowDecl(
            name=name,
            body=model.WorkflowBody(
                title=title,
                preamble=workflow_body.preamble,
                items=workflow_body.items,
            ),
            parent_name=parent_name,
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

    def workflow_body(self, items):
        preamble: tuple[str, ...] = ()
        workflow_items: tuple[model.WorkflowItem, ...] = ()
        for item in items:
            if not item:
                continue
            if isinstance(item[0], str):
                preamble = tuple(item)
            else:
                workflow_items = tuple(item)
        return WorkflowBodyParts(preamble=preamble, items=workflow_items)

    def workflow_section_body(self, items):
        return tuple(items)

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


def parse_text(source: str) -> model.PromptFile:
    tree = build_lark_parser().parse(source)
    return ToAst().transform(tree)


def parse_file(path: str | Path) -> model.PromptFile:
    resolved_path = Path(path).resolve()
    prompt_file = parse_text(resolved_path.read_text())
    return replace(prompt_file, source_path=resolved_path)
