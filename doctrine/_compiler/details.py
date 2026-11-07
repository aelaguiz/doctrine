from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from pathlib import PurePosixPath

from doctrine import model
from doctrine._compiler.constants import LATE_ROOT
from doctrine._compiler.naming import model_walk
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.types import CompiledSection, CompiledGuardBlock, CompiledCodeBlock
from doctrine.renderer import render_readable_block


def reject_details(value, surface):
    if any(isinstance(item, (CompiledSection, model.ReadableBlock)) and item.kind == "details"
           for item in model_walk(value)):
        raise compile_error(
            code="E620", summary="Details not allowed here",
            detail=f"`details` can't be used in {surface}.",
        )


def split_details(compiled, home):
    companions, pointers = {}, []
    def visit(item, headings):
        if not isinstance(item, (CompiledSection, CompiledGuardBlock)):
            return item
        if isinstance(item, CompiledSection) and item.kind == "details":
            origin = item.origin
            if origin is None:
                reject_details(item, "a declaration without a home")
            path = origin.companion or str(PurePosixPath(home) / "DETAILS.md")
            if origin.companion:
                headings = origin.headings
            companions.setdefault(path, []).append((headings, item))
            if path not in pointers:
                pointers.append(path)
            return None
        nested = ((*headings, item.title) if item.title and (
            isinstance(item, CompiledGuardBlock) or item.kind != "paragraph"
        ) else headings)
        return replace(item, body=tuple(result for child in item.body
                                        if (result := visit(child, nested)) is not None))
    compiled = replace(compiled, fields=tuple(visit(field, ()) for field in compiled.fields))
    return compiled, companions, pointers


def render_companion(parts):
    output, previous, previous_path = [], (), ()
    for headings, block in parts:
        path = block.origin.path[:-1]
        offset = len(headings) - len(path)
        common = 0
        for index, (left, right) in enumerate(zip(previous, headings)):
            if left != right or previous_path[:index + 1 - offset] != path[:index + 1 - offset]:
                break
            common += 1
        output.extend("#" * (index + 2) + " " + title
                      for index, title in enumerate(headings) if index >= common)
        if block.title:
            output.append(render_readable_block(
                replace(block, kind="section"), depth=len(headings) + 2
            ))
        else:
            output.append(render_readable_block(
                replace(block, kind="section", title=""), depth=len(headings) + 1
            ).partition("\n\n")[2])
        previous = headings
        previous_path = path
    return "\n\n".join(output) + "\n"


def details_origin(block, body):
    def reads(value):
        if isinstance(value, str):
            return bool(LATE_ROOT.search(value))
        if isinstance(value, tuple):
            return any(reads(item) for item in value)
        if isinstance(value, model.ReadableBlock):
            if value.kind == "roster":
                return True
            if value.kind == "code":
                return reads(value.title)
        if isinstance(value, CompiledCodeBlock):
            return reads(value.title)
        if is_dataclass(value):
            return any(reads(getattr(value, field.name)) for field in fields(value)
                       if field.name != "origin")
        return False
    origin = block.origin
    if origin and origin.companion and (reads(origin.headings) or reads(block) or reads(body)):
        return replace(origin, companion=None)
    return origin
