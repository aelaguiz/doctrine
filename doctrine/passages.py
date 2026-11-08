from __future__ import annotations

import re

from doctrine import model
from doctrine._compiler.diagnostics import compile_error


MARKER = re.compile(r"\{\{passage:([A-Za-z_][A-Za-z0-9_]*)\}\}")


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
        match = MARKER.fullmatch(parts[index])
        if match is None:
            continue
        name = match[1]
        if passages is None:
            raise compile_error(code="E659", summary="Passage needs a project build",
                detail=f"`{path}` uses passage `{name}`. Build it as a project skill.")
        if name not in passages:
            raise compile_error(code="E658", summary="Unknown passage",
                detail=f"`{path}` uses passage `{name}`, but the homes source does not declare it.")
        parts[index] = passages[name]
    return "".join(parts)
