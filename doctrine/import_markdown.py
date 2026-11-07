from __future__ import annotations

import re
import sys
import tempfile
from itertools import zip_longest
from pathlib import Path

from doctrine._compiler.constants import _RESERVED_AGENT_FIELD_KEYS
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_reader import markdown_lines
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import ParseError
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown, render_readable_block


def import_markdown(args):
    path = Path(args.path)
    if not path.is_file():
        raise compile_error(
            code="E652", summary="Missing Markdown source",
            detail=f"`{args.name}` reads `{args.path}`, which does not exist.",
        )
    lines = path.read_text(encoding="utf-8").splitlines()
    title = args.name
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:]
        start = 2
    else:
        start = 1
    output = [f'abstract agent {args.name}:' if args.kind == 'agent'
              else f'workflow {args.name}: {source_string(title)}']
    stack = [{"keys": {}, "keyed": False, "text": 0}]
    pending = []
    paragraph = False

    def flush():
        nonlocal paragraph
        text = "\n".join(pending).strip("\n")
        pending.clear()
        if not text:
            return
        node = stack[-1]
        indent = "    " * len(stack)
        if paragraph:
            output.append(f'{indent}    {source_string(text)}')
            paragraph = False
        elif len(stack) == 1 and args.kind == "agent":
            output.append(f'{indent}role: {source_string(text)}')
        elif node["keyed"]:
            node["text"] += 1
            output.append(f'{indent}paragraph text_{node["text"]}:')
            output.append(f'{indent}    {source_string(text)}')
        else:
            output.append(f'{indent}{source_string(text)}')

    def key_for(title, *, agent_slot=False, paragraph=False):
        key = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        if agent_slot:
            sample = f'abstract agent Probe:\n    {key}: "Title"\n        "Text"\n'
        elif paragraph:
            sample = f'workflow Probe: "Title"\n    paragraph {key}: "Title"\n        "Text"\n'
        elif len(stack) > 1:
            sample = f'workflow Probe: "Title"\n    parent: "Parent"\n        {key}: "Title"\n            "Text"\n'
        else:
            sample = f'workflow Probe: "Title"\n    {key}: "Title"\n        "Text"\n'
        try:
            parse_text(sample)
        except ParseError:
            key += "_"
        if agent_slot and key in _RESERVED_AGENT_FIELD_KEYS:
            key += "_"
        keys = stack[-1]["keys"]
        count = keys.get(key, 0) + 1
        keys[key] = count
        return f"{key}_{count}" if count > 1 else key

    for _, line, inside_fence, heading in markdown_lines(lines, path=args.path, start=start):
        if not inside_fence:
            if heading:
                flush()
                stack = stack[:len(heading[1]) - 1]
                node = stack[-1]
                key = key_for(heading[2], agent_slot=args.kind == "agent" and len(stack) == 1)
                output.append(f'{"    " * len(stack)}{key}: {source_string(heading[2])}')
                node["keyed"] = True
                stack.append({"keys": {}, "keyed": False, "text": 0})
                continue
            bold = re.match(r"^\*\*(.+?)\*\*\s+(.+)$", line)
            if bold and (not pending or not pending[-1]) and not (args.kind == "agent" and len(stack) == 1):
                flush()
                key = key_for(bold[1], paragraph=True)
                indent = "    " * len(stack)
                output.append(f'{indent}paragraph {key}: {source_string(bold[1])}')
                pending.append(bold[2])
                stack[-1]["keyed"] = True
                paragraph = True
                continue
            if paragraph and not line:
                flush()
                continue
        pending.append(line)
    flush()
    print("\n".join(output))
    if args.check:
        return check_render(args, output, lines, start)
    return 0


def check_render(args, output, lines, start):
    source = "\n".join(output) + "\n"
    if args.kind == "agent":
        source = source.replace("abstract agent ", "agent ", 1)
        stand_in = not output[1].startswith("    role:")
        if stand_in:
            source = source.replace("\n", '\n    role: "Stand-in."\n', 1)
        agent = args.name
    else:
        agent = args.name + "Check"
        source += f'\nagent {agent}:\n    role: "Stand-in."\n    content: {args.name}\n'
    with tempfile.TemporaryDirectory() as directory:
        prompt = Path(directory) / "prompts" / "AGENTS.prompt"
        prompt.parent.mkdir()
        prompt.write_text(source, encoding="utf-8")
        compiled = CompilationSession(parse_file(prompt)).compile_agent(agent)
        if args.kind == "agent":
            rendered = render_markdown(compiled).splitlines()
            if stand_in:
                rendered = rendered[2:]
        else:
            rendered = render_readable_block(compiled.fields[1], depth=1).splitlines()[1:]
    original = [line.rstrip() for line in lines]
    rendered = [line.rstrip() for line in rendered]
    while original and not original[0]:
        original.pop(0)
        start += 1
    while original and not original[-1]:
        original.pop()
    while rendered and not rendered[0]:
        rendered.pop(0)
    while rendered and not rendered[-1]:
        rendered.pop()
    for number, (before, after) in enumerate(zip_longest(original, rendered, fillvalue=""), start):
        if before != after:
            print(f"Line {number} differs.\n  Markdown: {before}\n  Render: {after}", file=sys.stderr)
            return 1
    return 0


def source_string(text):
    if "\n" not in text and '"' not in text and "\\" not in text:
        return f'"{text}"'
    text = text.replace("\\", "\\\\")
    ending = re.search(r'"+$', text)
    text = text.replace('"""', '""\\"')
    if ending and len(ending[0]) % 3:
        text = text[:-1] + '\\"'
    return '"""' + text + '"""'
