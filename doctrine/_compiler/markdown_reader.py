from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

import yaml

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._model.core import role_text


def heading_key(title):
    key = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return re.sub(r"^([0-9])", r"_\1", key)


def heading_link_text(text):
    parts = re.split(r"(?<![\\`])(`+)(?!`)(.*?)(?<!`)\1(?!`)", text, flags=re.S)
    for index in range(0, len(parts), 3):
        parts[index] = re.sub(r"(?<!!)\[((?:\\.|[^\]\\])*)\]\((?:\\.|[^()\\]|\([^()]*\))*\)", r"\1", parts[index])
    return "".join(parts[index] + (parts[index + 1] + parts[index + 2] + parts[index + 1]
                   if index + 1 < len(parts) else "") for index in range(0, len(parts), 3))


def heading_anchor(text, seen):
    text = re.sub(r"\s+#+$", "", text.strip())
    parts = re.split(r"(?<![\\`])(`+)(?!`)(.*?)(?<!`)\1(?!`)", heading_link_text(text), flags=re.S)
    for index in range(0, len(parts), 3):
        parts[index] = re.sub(r"!\[((?:\\.|[^\]\\])*)\]\((?:\\.|[^()\\]|\([^()]*\))*\)", r"\1", parts[index])
        parts[index] = re.sub(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^<>\s]*|[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+@[A-Za-z0-9.-]+)>", r"\1", parts[index])
        parts[index] = re.sub(r"<(?:[A-Za-z]|/)[^>]*>", "", parts[index]).lower().replace("*", "")
        before = parts[index - 1][-1:] if index else ""
        after = parts[index + 2][:1] if index + 2 < len(parts) else ""
        parts[index] = re.sub(r"_+", lambda match: match[0] if
                              (left := (parts[index][:match.start()] or before)[-1:]) and
                              (right := (parts[index][match.end():] or after)[:1]) and
                              unicodedata.category(left)[0] in "LMN" and unicodedata.category(right)[0] in "LMN"
                              else "", parts[index])
    text = "".join(part for index, part in enumerate(parts) if index % 3 != 1).lower()
    anchor = "".join(c for c in text if unicodedata.category(c)[0] in "LMN" or c in " -_").replace(" ", "-")
    seen[anchor] = seen.get(anchor, 0) + 1
    return anchor


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


def opening_paragraphs(lines):
    groups, pending = [], []
    for line, inside in fenced_lines(lines):
        if not inside and not line.strip():
            if pending:
                groups.append("\n".join(pending))
                pending = []
            elif groups:
                groups[-1] += "\n"
        else:
            pending.append(line)
    if pending:
        groups.append("\n".join(pending))
    elif groups:
        groups[-1] = groups[-1].rstrip("\n")
    result = []
    for text in groups:
        bold = re.match(r"^\*\*(.+?)\*\*(?: (?=[^ \t\n])|\n)", text)
        inline = bold and not bold[0].endswith("\n")
        result.append((bold[1] if inline else None, text[bold.end():] if inline else text,
                       bold[1] if bold else text))
    return result


def markdown_lines(lines, *, path, start, source_path=None, source_span=None):
    for number, (line, inside) in enumerate(fenced_lines(lines), start):
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


def skill_frontmatter_end(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---" or lines[0] == "---":
        return None
    offset = len(lines[0])
    for line in lines[1:]:
        offset += len(line)
        if line.rstrip("\r\n") == "---":
            return offset
    return None


def read_markdown(declaration, *, source_path, project_path, prompt_root):
    from doctrine._compiler.constants import _RESERVED_AGENT_FIELD_KEYS

    base = project_path.parent if project_path is not None else prompt_root.parent
    path = base / declaration.markdown_path

    def error(code, summary, detail):
        return compile_error(
            code=code, summary=summary, detail=detail,
            path=source_path, source_span=declaration.source_span,
        )

    if isinstance(declaration, model.FileDecl) and path.is_file():
        try:
            path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise error("E652", "Invalid Markdown source",
                        f"`{declaration.markdown_path}` is not UTF-8. Save it as UTF-8.") from None

    skill_text = None
    skill_metadata = None
    if isinstance(declaration, model.SkillPackageDecl):
        if not path.is_file():
            raise error("E652", "Missing Markdown source",
                        f"`{declaration.name}` reads `{declaration.markdown_path}`, which does not exist.")
        try:
            skill_text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise error("E652", "Invalid Markdown source",
                        f"`{declaration.markdown_path}` is not UTF-8. Save it as UTF-8.") from None
        end = skill_frontmatter_end(skill_text)
        if end is None:
            raise error("E657", "Invalid skill frontmatter",
                        f"`{declaration.markdown_path}` needs frontmatter with opening and closing `---` lines.")
        header_lines = skill_text[:end].splitlines()
        try:
            metadata = yaml.safe_load("\n".join(header_lines[1:-1]))
        except yaml.YAMLError as exc:
            raise error("E657", "Invalid skill frontmatter",
                        f"`{declaration.markdown_path}` has invalid YAML: {exc}") from None
        if not isinstance(metadata, dict):
            metadata = {}
        for key in ("name", "description"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                raise error("E657", "Invalid skill frontmatter",
                            f"`{declaration.markdown_path}` needs a non-empty `{key}` in its frontmatter.")
        skill_metadata = model.SkillPackageMetadata(name=metadata["name"], description=metadata["description"])
        lines = skill_text[end:].splitlines()
        title, start = declaration.name, len(header_lines) + 1
    else:
        lines, title, start = markdown_head(
            path, declaration.name, declaration.markdown_path,
            source_path=source_path, source_span=declaration.source_span,
        )

    def literal(text):
        return model.MarkdownProse(text, path)

    if start == 2 and skill_text is None:
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
    if isinstance(declaration, model.SkillPackageDecl):
        def readable_skill(section):
            return model.ReadableBlock("section", section.key, section.title,
                tuple(readable_skill(item) if isinstance(item, model.LocalSection) else item
                      for item in section.items), source_span=section.source_span)
        return replace(declaration, metadata=skill_metadata, markdown_text=skill_text,
                       items=(*preamble, *(readable_skill(section) for section in sections)))
    if isinstance(declaration, model.FileDecl):
        def readable(section):
            return model.ReadableBlock("section", section.key, section.title,
                tuple(readable(item) if isinstance(item, model.LocalSection) else item
                      for item in section.items), source_span=section.source_span)
        return replace(declaration, title=title, body=model.DocumentBody(
            title=title, preamble=preamble, items=tuple(readable(section) for section in sections)))
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
            parts = opening_paragraphs(root["lines"])
            if len(parts) > 1:
                keys = {}
                paragraphs = []
                for lead, text, key_text in parts:
                    key = heading_key(" ".join(key_text.split()[:4]))
                    base, count = key, 1
                    while key in keys:
                        count += 1
                        key = f"{base}_{count}"
                    keys[key] = True
                    paragraphs.append(model.ReadableBlock("paragraph", key, literal(lead) if lead else None, (literal(text),)))
                fields = (model.RoleScalar(text=literal(role_text(paragraphs)), paragraphs=tuple(paragraphs)), *fields)
            else:
                fields = (model.RoleScalar(text=preamble[0]), *fields)
        return replace(declaration, fields=fields)
    return replace(declaration, body=model.WorkflowBody(title=title, preamble=preamble, items=sections))
