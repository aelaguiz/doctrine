from __future__ import annotations

import re
from dataclasses import replace

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


def read_markdown(declaration, *, source_path, project_path, prompt_root):
    base = project_path.parent if project_path is not None else prompt_root.parent
    path = base / declaration.markdown_path

    def error(code, summary, detail):
        return compile_error(
            code=code, summary=summary, detail=detail,
            path=source_path, source_span=declaration.source_span,
        )

    if not path.is_file():
        raise error(
            "E652", "Missing Markdown source",
            f"`{declaration.name}` reads `{declaration.markdown_path}`, which does not exist.",
        )
    lines = path.read_text().splitlines()

    def literal(text):
        value = model.AuthoredProse(text)
        value.markdown_path = path
        return value

    title = declaration.name
    if lines and lines[0].startswith("# "):
        title = literal(lines.pop(0)[2:])
        start = 2
    else:
        start = 1
    root = {"lines": [], "children": [], "keys": {}}
    stack = [root]
    fence = None
    for number, line in enumerate(lines, start):
        trimmed = line.lstrip()
        if trimmed.startswith(("```", "~~~")):
            marker = trimmed[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        elif fence is None:
            if line.startswith("@"):
                raise error(
                    "E654", "Import line in Markdown source",
                    f"`{declaration.markdown_path}` line {number} is a runtime import, and its path would break once inlined. Declare that file too and compose it.",
                )
            match = re.match(r"^(#{2,3}) (.+)$", line)
            if match:
                level = len(match[1]) - 1
                stack = stack[:level]
                parent = stack[-1]
                key = re.sub(r"[^a-z0-9]+", "_", match[2].lower()).strip("_")
                if key in parent["keys"]:
                    raise error(
                        "E653", "Duplicate heading key",
                        f"`{declaration.markdown_path}` has two sibling headings with key `{key}`, at lines {parent['keys'][key]} and {number}.",
                    )
                parent["keys"][key] = number
                node = {
                    "key": key, "title": literal(match[2]), "lines": [],
                    "children": [], "keys": {},
                }
                parent["children"].append(node)
                stack.append(node)
                continue
        stack[-1]["lines"].append(line)

    def body(node):
        prose = (literal("\n".join(node["lines"]).strip("\n")),) if node["lines"] and any(node["lines"]) else ()
        children = tuple(
            model.LocalSection(key=child["key"], title=child["title"], items=body(child))
            for child in node["children"]
        )
        return (*prose, *children)

    items = body(root)
    preamble = tuple(item for item in items if isinstance(item, str))
    sections = tuple(item for item in items if not isinstance(item, str))
    if isinstance(declaration, model.Agent):
        fields = tuple(
            model.AuthoredSlotField(key=section.key, value=model.WorkflowBody(
                title=section.title,
                preamble=tuple(item for item in section.items if isinstance(item, str)),
                items=tuple(item for item in section.items if not isinstance(item, str)),
            ))
            for section in sections
        )
        if preamble:
            fields = (model.RoleScalar(text=preamble[0]), *fields)
        return replace(declaration, fields=fields)
    return replace(declaration, body=model.WorkflowBody(title=title, preamble=preamble, items=sections))
