from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from pathlib import PurePosixPath

from doctrine._compiler.constants import LATE_ROOT
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.types import CompiledSection, CompiledCodeBlock
from doctrine.renderer import render_readable_block


def reject_details(value, surface):
    if isinstance(value, CompiledSection) and value.kind == "details":
        raise compile_error(code="E620", summary="Details outside a home", detail=f"`details` can't be used in {surface}. It only works in text that lands in a home.")
    if isinstance(value, tuple):
        for item in value:
            reject_details(item, surface)
    elif is_dataclass(value):
        for field in fields(value):
            if field.name != "origin":
                reject_details(getattr(value, field.name), surface)


def split_details(compiled, home):
    companions, pointers = {}, []
    def visit(item, headings):
        if not isinstance(item, CompiledSection):
            return item
        if item.kind == "details":
            origin = item.origin
            path = origin[3] or str(PurePosixPath(home) / "DETAILS.md")
            if origin[3]:
                headings = origin[4]
            companions.setdefault(path, []).append((headings, item))
            if path not in pointers:
                pointers.append(path)
            return None
        nested = (*headings, item.title) if item.title and item.kind != "paragraph" else headings
        return replace(item, body=tuple(result for child in item.body if (result := visit(child, nested)) is not None))
    compiled = replace(compiled, fields=tuple(visit(field, ()) for field in compiled.fields))
    return compiled, companions, pointers


def render_companion(parts):
    output, previous, previous_path = [], (), ()
    for headings, block in parts:
        path = block.origin[1][:-1]
        offset = len(headings) - len(path)
        common = 0
        for index, (left, right) in enumerate(zip(previous, headings)):
            if left != right or previous_path[:index + 1 - offset] != path[:index + 1 - offset]:
                break
            common += 1
        output.extend("#" * (index + 2) + " " + title for index, title in enumerate(headings) if index >= common)
        if block.title:
            output.append(render_readable_block(replace(block, kind="section"), depth=len(headings) + 2))
        else:
            output.append(render_readable_block(replace(block, kind="section", title=""), depth=len(headings) + 1).partition("\n\n")[2])
        previous = headings
        previous_path = path
    return "\n\n".join(output) + "\n"


def validate_shared_details(block):
    if not (isinstance(block, CompiledSection) and block.kind == "details" and block.origin and block.origin[3]):
        return
    def read(value):
        if isinstance(value, str):
            match = LATE_ROOT.search(value)
            if match:
                raise compile_error(code="E621", summary="Shared details read one agent's words",
                    detail=f"`{block.origin[3]}` serves every home that points at it, so it can't read `{{{{{match[1]}:{match[2]}}}}}`.",
                    hints=("Move this into the team or member, or write it in words that fit every reader.",))
        elif isinstance(value, tuple):
            for item in value:
                read(item)
        elif is_dataclass(value):
            for field in fields(value):
                if field.name != "origin" and not (isinstance(value, CompiledCodeBlock) and field.name == "text"):
                    read(getattr(value, field.name))
    read((block.origin[4], block))
