from __future__ import annotations

import ast
from pathlib import Path

from lark import Lark, Transformer, v_args

from doctrine import model
from doctrine._parser.agents import AgentTransformerMixin
from doctrine._parser.analysis_decisions import AnalysisDecisionTransformerMixin
from doctrine._parser.expressions import ExpressionTransformerMixin
from doctrine._parser.io import IoTransformerMixin
from doctrine._parser.parts import _name_ref_from_dotted_name, _source_span_from_meta, _with_source_span
from doctrine._parser.readables import ReadableNodeTransformerMixin
from doctrine._parser.reviews import ReviewTransformerMixin
from doctrine._parser.runtime import (
    build_lark_parser as _build_lark_parser,
    parse_file as _parse_file,
    parse_text as _parse_text,
)
from doctrine._parser.skills import SkillsTransformerMixin
from doctrine._parser.transformer import (
    DeclarationTransformerMixin,
    ReadableTransformerMixin,
    SchemaDocumentTransformerMixin,
)
from doctrine._parser.workflows import WorkflowTransformerMixin


class ToAst(
    SchemaDocumentTransformerMixin,
    DeclarationTransformerMixin,
    AgentTransformerMixin,
    AnalysisDecisionTransformerMixin,
    ExpressionTransformerMixin,
    IoTransformerMixin,
    ReviewTransformerMixin,
    SkillsTransformerMixin,
    WorkflowTransformerMixin,
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
        text = str(token)
        if "." in text or "e" in text.lower():
            return float(text)
        return int(text)

    @v_args(inline=True)
    def start(self, prompt_file):
        return prompt_file

    def prompt_file(self, items):
        declarations = []
        for item in items:
            if isinstance(item, list):
                declarations.extend(item)
            else:
                declarations.append(item)
        return model.PromptFile(declarations=tuple(declarations))

    @v_args(inline=True)
    def inheritance(self, parent_ref):
        return parent_ref

    def import_alias(self, items):
        return items[0]

    def grouped_inherit_keys(self, items):
        return tuple(items)

    def review_grouped_inherit_keys(self, items):
        return tuple(items)

    def schema_grouped_inherit_keys(self, items):
        return tuple(items)

    @v_args(inline=True)
    def import_decl(self, declaration):
        return declaration

    def imported_symbol_binding(self, items):
        name = items[0]
        alias = items[1] if len(items) > 1 else None
        return (name, alias)

    @v_args(meta=True)
    def module_import_decl(self, meta, items):
        path = items[0]
        alias = items[1] if len(items) > 1 else None
        return _with_source_span(
            model.ImportDecl(path=path, alias=alias),
            meta,
        )

    @v_args(meta=True)
    def from_import_decl(self, meta, items):
        path = items[0]
        bindings = items[1:]
        return [
            _with_source_span(
                model.ImportDecl(
                    path=path,
                    imported_name=name,
                    alias=alias,
                ),
                meta,
            )
            for name, alias in bindings
        ]

    @v_args(meta=True)
    def render_profile_decl(self, meta, items):
        name = items[0]
        return _with_source_span(
            model.RenderProfileDecl(name=name, rules=tuple(items[1:])),
            meta,
        )

    @v_args(meta=True, inline=True)
    def render_profile_rule(self, meta, target_parts, mode):
        return _with_source_span(
            model.RenderProfileRule(target_parts=tuple(target_parts), mode=mode),
            meta,
        )

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

    @v_args(meta=True, inline=True)
    def name_ref(self, meta, dotted_name):
        parts = tuple(dotted_name)
        return model.NameRef(
            module_parts=parts[:-1],
            declaration_name=parts[-1],
            source_span=_source_span_from_meta(meta),
        )

    @v_args(meta=True, inline=True)
    def path_ref(self, meta, raw_ref):
        root_name, path_name = raw_ref.split(":", 1)
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(
                root_name,
                source_span=_source_span_from_meta(meta),
            ),
            path=tuple(path_name.split(".")),
            source_span=_source_span_from_meta(meta),
        )


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
