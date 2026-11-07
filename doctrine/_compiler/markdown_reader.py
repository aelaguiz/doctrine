from __future__ import annotations

import re
from dataclasses import replace

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


def heading_key(title):
    key = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return re.sub(r"^([0-9])", r"_\1", key)


def fenced_lines(lines):
    fence = None
    for line in lines:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
        inside = fence is not None
        if fence is not None:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1]
                    and not marker[2].strip()):
                fence = None
        elif marker and (marker[1][0] == "~" or "`" not in marker[2]):
            fence = marker[1][0], len(marker[1])
            inside = True
        yield line, inside


def markdown_lines(lines, *, path, start, source_path=None, source_span=None):
    for number, (line, inside) in enumerate(fenced_lines(lines), start):
        if not inside and line.startswith("@"):
            raise compile_error(
                code="E654", summary="Import line in Markdown source",
                detail=f"`{path}` line {number} is a runtime import, and its path would break once inlined. Declare that file too and compose it.",
                path=source_path, source_span=source_span,
            )
        yield number, line, inside, None if inside else re.match(r"^(#{2,3}) (.+)$", line)


def markdown_head(path, name, display_path, *, source_path=None, source_span=None):
    if not path.is_file():
        raise compile_error(
            code="E652", summary="Missing Markdown source",
            detail=f"`{name}` reads `{display_path}`, which does not exist.",
            path=source_path, source_span=source_span,
        )
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines.pop(0)[2:] if lines and lines[0].startswith("# ") else None
    return lines, title if title is not None else name, 2 if title is not None else 1


def read_markdown(declaration, *, source_path, project_path, prompt_root):
    from doctrine._compiler.constants import _RESERVED_AGENT_FIELD_KEYS

    base = project_path.parent if project_path is not None else prompt_root.parent
    path = base / declaration.markdown_path

    def error(code, summary, detail):
        return compile_error(
            code=code, summary=summary, detail=detail,
            path=source_path, source_span=declaration.source_span,
        )

    lines, title, start = markdown_head(
        path, declaration.name, declaration.markdown_path,
        source_path=source_path, source_span=declaration.source_span,
    )

    def literal(text):
        return model.MarkdownProse(text, path)

    if start == 2:
        title = literal(title)
    root = {"lines": [], "children": [], "keys": {}}
    stack = [root]
    for number, line, inside_fence, match in markdown_lines(
        lines, path=declaration.markdown_path, start=start,
        source_path=source_path, source_span=declaration.source_span,
    ):
        if not inside_fence:
            if match:
                level = len(match[1]) - 1
                stack = stack[:level]
                parent = stack[-1]
                key = heading_key(match[2])
                if isinstance(declaration, model.Agent) and key in _RESERVED_AGENT_FIELD_KEYS:
                    key += "_"
                if key in parent["keys"]:
                    raise error(
                        "E653", "Duplicate heading key",
                        f"`{declaration.markdown_path}` has two sibling headings with key `{key}`, at lines {parent['keys'][key]} and {number}.",
                    )
                parent["keys"][key] = number
                node = {
                    "key": key, "title": literal(match[2]), "lines": [],
                    "children": [], "keys": {}, "span": model.SourceSpan(number, 1),
                }
                parent["children"].append(node)
                stack.append(node)
                continue
        stack[-1]["lines"].append(line)

    def body(node):
        prose = (literal("\n".join(node["lines"]).strip("\n")),) if node["lines"] and any(node["lines"]) else ()
        children = tuple(
            model.LocalSection(key=child["key"], title=child["title"],
                               items=body(child), source_span=child["span"])
            for child in node["children"]
        )
        return (*prose, *children)

    items = body(root)
    preamble = tuple(item for item in items if isinstance(item, str))
    sections = tuple(item for item in items if not isinstance(item, str))
    if isinstance(declaration, model.Agent):
        fields = tuple(
            model.AuthoredSlotField(
                key=section.key, source_span=section.source_span, value=model.WorkflowBody(
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
