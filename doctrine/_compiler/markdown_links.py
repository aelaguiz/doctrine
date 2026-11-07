from __future__ import annotations

import os
import posixpath
import re

from doctrine import model
from doctrine._compiler.markdown_reader import fenced_lines


def rebase_markdown(text, folder):
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
        r"(?<!\S)@((?:\\ |[^\s])+)",
    )
    changes = []
    for pattern in patterns:
        for match in re.finditer(pattern, visible, re.M):
            start, end = match.span(match.lastindex)
            dest = text[start:end]
            if dest.startswith(("/", "#", "~")) or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", dest):
                continue
            path, separator, anchor = (dest.replace("\\ ", " ") if pattern == patterns[-1] else dest).partition("#")
            relative = os.path.relpath(text.source_path.parent / path, folder).replace(os.sep, "/")
            rebased = posixpath.normpath(relative) + separator + anchor
            changes.append((start, end, rebased.replace(" ", "\\ ") if pattern == patterns[-1] else rebased))
    result = str(text)
    for start, end, dest in sorted(changes, reverse=True):
        result = result[:start] + dest + result[end:]
    return model.MarkdownProse(result, text.source_path)
