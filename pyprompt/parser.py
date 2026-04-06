from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

from lark import Lark, Transformer, v_args

from pyprompt.indenter import PyPromptIndenter
from pyprompt.model import Agent, PromptFile, RoleBlock, RoleScalar, Workflow


class ToAst(Transformer):
    def CNAME(self, token):
        return str(token)

    def ESCAPED_STRING(self, token):
        return ast.literal_eval(str(token))

    @v_args(inline=True)
    def start(self, prompt_file):
        return prompt_file

    def prompt_file(self, items):
        return PromptFile(agents=tuple(items))

    def agent(self, items):
        return Agent(name=items[0], fields=tuple(items[1:]))

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return RoleScalar(text=title_or_text)
        return RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def workflow(self, title, lines):
        return Workflow(title=title, lines=tuple(lines))

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


def parse_text(source: str) -> PromptFile:
    tree = build_lark_parser().parse(source)
    return ToAst().transform(tree)


def parse_file(path: str | Path) -> PromptFile:
    return parse_text(Path(path).read_text())
