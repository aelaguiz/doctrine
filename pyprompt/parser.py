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

    def agent(self, items):
        return model.Agent(name=items[0], fields=tuple(items[1:]))

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

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return model.RoleScalar(text=title_or_text)
        return model.RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def workflow_decl(self, name, title, body):
        return model.WorkflowDecl(
            name=name,
            body=model.WorkflowBody(
                title=title,
                preamble=body.preamble,
                items=body.items,
            ),
        )

    @v_args(inline=True)
    def workflow_field(self, title, body):
        return model.WorkflowBody(
            title=title,
            preamble=body.preamble,
            items=body.items,
        )

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

    @v_args(inline=True)
    def local_section(self, key, title, lines):
        return model.LocalSection(key=key, title=title, lines=tuple(lines))

    @v_args(inline=True)
    def workflow_use(self, key, target):
        return model.WorkflowUse(key=key, target=target)

    @v_args(inline=True)
    def workflow_target(self, dotted_name):
        parts = tuple(dotted_name)
        return model.WorkflowTarget(
            module_parts=parts[:-1],
            declaration_name=parts[-1],
        )

    def block_lines(self, items):
        return tuple(items)


@lru_cache(maxsize=1)
def build_lark_parser() -> Lark:
    # Pin the bootstrap parser to the exact stock-Lark shape the plan earned.
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
