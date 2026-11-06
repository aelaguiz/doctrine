from __future__ import annotations

import os
import posixpath
import re
from pathlib import Path

from doctrine import model


def rebase_markdown(text, folder):
    masked = list(text)
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
        inside = fence is not None
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker and (marker[1][0] == "~" or "`" not in marker[2]):
            fence = marker[1][0], len(marker[1])
            inside = True
        if inside:
            masked[offset:offset + len(line)] = " " * len(line)
        offset += len(line)
    visible = "".join(masked)
    position = 0
    while position < len(visible):
        if visible[position] == "\\":
            position += 2
            continue
        run = re.match(r"`+", visible[position:])
        if run:
            end = position + len(run[0])
            closing = re.search(r"(?<!`)" + re.escape(run[0]) + r"(?!`)", visible[end:])
            if closing:
                end += closing.end()
                masked[position:end] = " " * (end - position)
                position = end
                continue
            position = end
        else:
            position += 1
    visible = "".join(masked)
    destinations = []
    for match in re.finditer(r"(?<!\\)\]\([ \t\n]*|^ {0,3}\[(?:\\.|[^\]\\\n])+\]:[ \t\n]*", visible, re.M):
        inline = visible[match.start()] == "]"
        if inline:
            cursor, brackets = match.start() - 1, 1
            while cursor >= 0 and brackets:
                if visible[cursor] in "[]" and (cursor == 0 or visible[cursor - 1] != "\\"):
                    brackets += 1 if visible[cursor] == "]" else -1
                cursor -= 1
            if brackets:
                continue
        start = match.end()
        if start == len(text):
            continue
        angle = text[start] == "<"
        start += angle
        end, depth = start, 0
        while end < len(text):
            char = text[end]
            if char == "\\":
                end += 2
                continue
            if angle:
                if char in ">\n":
                    break
            elif char.isspace() or char == ")" and depth == 0:
                break
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            end += 1
        if angle and (end == len(text) or text[end] != ">"):
            continue
        after = end + angle
        if inline and not re.match(r"\s*(?:[\"'](?:\\.|[^\"'\\])*[\"']\s*)?\)", text[after:]):
            continue
        destination = text[start:end]
        if not destination or destination.startswith(("/", "#", "~")) or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", destination):
            continue
        path, separator, anchor = destination.partition("#")
        relative = os.path.relpath(text.source_path.parent / path, folder).replace(os.sep, "/")
        destinations.append((start, end, posixpath.normpath(relative) + separator + anchor))
    result = str(text)
    for start, end, destination in reversed(destinations):
        result = result[:start] + destination + result[end:]
    return model.MarkdownProse(result, text.source_path)
