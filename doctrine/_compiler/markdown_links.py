from __future__ import annotations

import os
import posixpath
import re
import json
from pathlib import Path

from doctrine import model
from doctrine.project_config import real_project_path
from doctrine._compiler.markdown_reader import fenced_lines


def render_file_refs(text, folder, config):
    def render(match):
        mode, title, path, anchor = json.loads(match[1])
        relative = os.path.relpath(real_project_path(config, Path(path)),
                                   real_project_path(config, folder)).replace(os.sep, "/")
        if anchor:
            relative += "#" + anchor
        if mode == "load":
            return "@" + relative
        destination = "<" + relative + ">" if any(c.isspace() for c in relative) else relative
        return f"[{title}]({destination})"
    result = re.sub(r"\x1e([^\x1f]+)\x1f", render, text)
    return model.AuthoredProse(result) if isinstance(text, model.AuthoredProse) else result


def markdown_destinations(text):
    visible = "".join(
        re.sub(r"[^\n]", " ", line) if inside else line
        for line, inside in fenced_lines(text.splitlines(keepends=True))
    )
    visible = re.sub(
        r"(?<![\\`])(`+)(?!`)((?:(?!\n[ \t]*\n).)*?)(?<!`)\1(?!`)",
        lambda match: " " * len(match[0]),
        visible,
        flags=re.S,
    )
    destination = r"(?:<([^<>\n]+)>|((?:\\.|[^()\s\\]|\((?:\\.|[^()\\])*\))+))"
    patterns = (
        r"(?<!\\)\]\([ \t\n]*" + destination + r"\s*(?:[\"'][^\"']*[\"']\s*)?\)",
        r"^ {0,3}\[(?!\^)(?:\\.|[^\]\\\n])+\]:[ \t\n]*"
        + destination
        + r"[ \t]*(?:[\"'][^\"'\n]*[\"'][ \t]*)?$",
        r"(?<!\S)@([^\s\[\]()]+)",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, visible, re.M):
            start, end = match.span(match.lastindex)
            yield start, end, pattern == patterns[-1]


def rebase_markdown(text, folder):
    changes = []
    for start, end, is_import in markdown_destinations(text):
        dest = text[start:end]
        if dest.startswith(("/", "#", "~")) or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", dest):
            continue
        path, separator, anchor = dest.partition("#")
        if is_import and (text[end:].split("\n", 1)[0].strip() or not (text.source_path.parent / path).is_file()):
            continue
        relative = os.path.relpath(text.source_path.parent / path, folder).replace(os.sep, "/")
        rebased = posixpath.normpath(relative) + separator + anchor
        changes.append((start, end, rebased))
    result = str(text)
    for start, end, dest in sorted(changes, reverse=True):
        result = result[:start] + dest + result[end:]
    return model.MarkdownProse(result, text.source_path)
