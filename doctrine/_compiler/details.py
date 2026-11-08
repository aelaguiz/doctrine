from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
import json
import re
from pathlib import PurePosixPath

from doctrine import model
from doctrine._compiler.constants import DETAILS_LINK, LATE_ROOT
from doctrine._compiler.late_binding import map_text, reject_case_links
from doctrine._compiler.markdown_reader import fenced_lines, heading_anchor
from doctrine._compiler.naming import model_walk
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.types import CompiledSection, CompiledGuardBlock, CompiledCodeBlock, CompiledReadableBlock, CompiledRuleBlock
from doctrine.renderer import render_readable_block


def reject_details(value, surface):
    if any(isinstance(item, (CompiledSection, model.ReadableBlock)) and item.kind == "details"
           for item in model_walk(value)):
        raise compile_error(
            code="E620", summary="Details not allowed here",
            detail=f"`details` can't be used in {surface}.",
        )


def split_details(compiled, home, root, home_map, unit):
    companions, pointers, cases, linked = {}, [], {}, {}
    paths = {entry.path for entry in home_map.entries}
    for item in model_walk(compiled):
        if is_dataclass(item):
            for field in fields(item):
                if field.name.endswith("title") and isinstance(title := getattr(item, field.name), str):
                    reject_case_links(str(title), unit=unit)
        if isinstance(item, CompiledReadableBlock) and not isinstance(item, CompiledRuleBlock):
            if item.origin:
                reject_case_links(item.origin.headings, unit=unit)
    def visit(item, headings, key_path):
        if not isinstance(item, (CompiledSection, CompiledGuardBlock)):
            return item
        if isinstance(item, CompiledSection) and item.kind == "details":
            reject_case_links(item.body, unit=unit)
            origin = item.origin
            if origin is None:
                reject_details(item, "a declaration without a home")
            path = origin.companion or str(PurePosixPath(home) / "DETAILS.md")
            if origin.companion:
                headings = origin.headings
            companions.setdefault(path, []).append((headings, item))
            cases[key_path] = (path, item)
            if path not in pointers:
                pointers.append(path)
            return None
        nested = ((*headings, item.title) if item.title and (
            isinstance(item, CompiledGuardBlock) or item.kind != "paragraph"
        ) else headings)
        return replace(item, body=tuple(result for child in item.body
            if (result := visit(child, nested, (*key_path, child.key) if isinstance(child, (CompiledSection, CompiledGuardBlock)) and child.key else key_path)) is not None))
    compiled = replace(compiled, fields=tuple(visit(field, (), (field.key,))
        if isinstance(field, (CompiledSection, CompiledGuardBlock)) else field for field in compiled.fields))
    def link(text, prefix):
        lines = list(fenced_lines(text.splitlines()))
        for index, (line, inside) in enumerate(lines):
            if not inside and re.match(r"^ {0,3}#{1,6}(?:\s|$)", line):
                reject_case_links(line, unit=unit)
            if not inside and index and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line):
                reject_case_links(lines[index - 1][0], unit=unit)
        def resolve(match):
            name = match[1]
            key = (*prefix, *name.split("."))
            if key not in cases:
                detail = (f"`details:{name}` isn't a case." if key in paths else
                          f"`{home}` links to `details:{name}`, which it doesn't have.")
                hints = () if key in paths else ("Override the sentence that links to it, or keep the case.",)
                raise compile_error(code="E637", summary="Dead case link", detail=detail, hints=hints)
            path, case = cases[key]
            if not case.title:
                raise compile_error(code="E637", summary="Dead case link",
                    detail=f"`details:{name}` has no title to link to. Give the case a title.")
            anchor = heading_anchor(case.title, {})
            linked[key] = (path, anchor, name)
            return "" + json.dumps(["link", case.title, str(root / path), anchor]) + ""
        return type(text)(DETAILS_LINK.sub(resolve, text))
    def resolve_item(item, key_path, prefix=()):
        if isinstance(item, (CompiledSection, CompiledGuardBlock)):
            if item.origin:
                size = len(item.origin.path)
                prefix = key_path[:-size] if size else key_path
            body = tuple(resolve_item(child, (*key_path, child.key)
                if isinstance(child, (CompiledSection, CompiledGuardBlock)) and child.key else key_path, prefix)
                for child in item.body)
            return replace(map_text(replace(item, body=()), lambda text: link(text, prefix)), body=body)
        return map_text(item, lambda text: link(text, prefix))
    compiled = replace(compiled, fields=tuple(resolve_item(field, (field.key,))
        if isinstance(field, (CompiledSection, CompiledGuardBlock)) else resolve_item(field, ())
        for field in compiled.fields))
    unlinked = [path for path in pointers if any(case_path not in linked
        for case_path, (companion, _) in cases.items() if companion == path)]
    return compiled, companions, pointers, unlinked, tuple(linked.values())


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
        output.extend("#" * min(index + 2, 6) + " " + title
                      for index, title in enumerate(headings) if index >= common)
        if block.title:
            output.append(render_readable_block(
                replace(block, kind="section"), depth=min(len(headings) + 2, 6)
            ))
        else:
            output.append(render_readable_block(
                replace(block, kind="section", title=""), depth=min(len(headings) + 1, 6)
            ).partition("\n\n")[2])
        previous = headings
        previous_path = path
    text = "\n\n".join(output) + "\n"
    return "".join(re.sub(r"^#{7,} ", "###### ", line) if not inside else line
                   for line, inside in fenced_lines(text.splitlines(keepends=True)))


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
