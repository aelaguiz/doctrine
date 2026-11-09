from __future__ import annotations

import json
import re

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


MARKER = re.compile(r"\{\{passage:([A-Za-z_][A-Za-z0-9_]*)(?:\((.*)\))?\}\}")
VALUE = r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*("(?:[^"\\]|\\.)*")\s*'
VALUES = re.compile(rf"(?:{VALUE}(?:,{VALUE})*)?")
READ = re.compile(r"\{\{value:([A-Za-z_][A-Za-z0-9_]*)\}\}")


def read_marker(line, path):
    """The passage a marker line places and the values it gives, or None for any other line."""
    if not (line.startswith("{{passage:") and line.endswith("}}")):
        return None
    match = MARKER.fullmatch(line)
    values = {}
    if match and match[2] is not None:
        if VALUES.fullmatch(match[2]) is None:
            match = None
        else:
            for key, text in re.findall(VALUE, match[2]):
                if key in values:
                    match = None
                values[key] = json.loads(text)
    if match is None:
        raise compile_error(code="E663", summary="Bad passage marker",
            detail=f"`{path}` has a marker line that is not `{{{{passage:Name}}}}` or "
                   f'`{{{{passage:Name(key: "value")}}}}` with each key once: `{line}`.')
    return match[1], values


def collect_passages(prompts, root):
    passages = {}
    for prompt in prompts:
        for declaration in prompt.declarations:
            if not isinstance(declaration, model.PassageDecl):
                continue
            name = declaration.name
            if name in passages:
                raise compile_error(code="E661", summary="Duplicate passage",
                    detail=f"Passage `{name}` is declared more than once.",
                    path=prompt.source_path, source_span=declaration.source_span)
            text = declaration.text
            if declaration.markdown_path is not None:
                source = root / declaration.markdown_path
                try:
                    text = source.read_bytes().decode("utf-8")
                except (OSError, UnicodeDecodeError):
                    raise compile_error(code="E652", summary="Missing or invalid Markdown source",
                        detail=f"Passage `{name}` cannot read UTF-8 file `{declaration.markdown_path}`.",
                        path=prompt.source_path, source_span=declaration.source_span) from None
                # The file's last line ending goes; the marker line keeps its own.
                text = re.sub(r"(\r\n|\r|\n)\Z", "", text, count=1)
            passages[name] = text
    return passages


def place_passages(text, passages, *, path):
    parts = re.split(r"(\r\n|\r|\n)", text)
    for index in range(0, len(parts), 2):
        marker = read_marker(parts[index], path)
        if marker is None:
            continue
        name, values = marker
        if passages is None:
            raise compile_error(code="E659", summary="Passage needs a project build",
                detail=f"`{path}` uses passage `{name}`. Build it as a project skill.")
        if name not in passages:
            raise compile_error(code="E658", summary="Unknown passage",
                detail=f"`{path}` uses passage `{name}`, but the homes source does not declare it.")
        reads = set(READ.findall(passages[name]))
        problems = []
        if missing := sorted(reads - set(values)):
            problems.append(f"without {', '.join(f'`{key}`' for key in missing)}, which it reads")
        if unused := sorted(set(values) - reads):
            problems.append(f"with {', '.join(f'`{key}`' for key in unused)}, which it never reads")
        if problems:
            raise compile_error(code="E662", summary="Passage values don't match",
                detail=f"`{path}` places passage `{name}` " + ", and ".join(problems) + ".")
        parts[index] = READ.sub(lambda read: values[read[1]], passages[name])
    return "".join(parts)
