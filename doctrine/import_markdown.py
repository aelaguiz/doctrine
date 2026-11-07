from __future__ import annotations

import re
import sys
import tempfile
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

from doctrine._compiler.constants import _RESERVED_AGENT_FIELD_KEYS
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_reader import heading_key, markdown_head, markdown_lines, opening_paragraphs
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import ParseError
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown, render_readable_block


def import_markdown(args):
    path = Path(args.path)
    lines, title, start = markdown_head(path, args.name, args.path)
    output = [f'abstract agent {args.name}:' if args.kind == 'agent'
              else f'workflow {args.name}: {title_string(title)}']
    stack = [{"keys": {}, "keyed": False, "text": 0}]
    pending = []
    paragraph = False
    people = {}
    quote_originals = {}
    converted = set()

    def replace_quote(match):
        name, written_date, context, words = match.groups()
        if lead and match.start() < lead.end(1):
            return match[0]
        try:
            day = datetime.strptime(written_date, "%B %d, %Y")
        except ValueError:
            return match[0]
        if written_date != f"{day.strftime('%B')} {day.day}, {day.year}":
            return match[0]
        parts = context.split(",") if context else []
        seen = set()
        for part in parts:
            key, _, value = part.strip().partition(" ")
            if key in {"to", "about", "source"}:
                if key == "source" or key in seen or not value.strip():
                    return match[0]
                seen.add(key)
        if context and context != ", ".join(part.strip() for part in parts):
            return match[0]
        key = "".join(word[0].upper() + word[1:] for word in name.split())
        if key in people and people[key] != name:
            return match[0]
        people[key] = name
        converted.add((number, match.start(4) - 1))
        extra = f", {context}" if context else ""
        result = f'{{{{{key}, {day:%Y-%m-%d}{extra}: "{words}"}}}}'
        quote_originals[result] = match[0]
        return result

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
            parts = opening_paragraphs(text.splitlines())
            if len(parts) == 1:
                output.append(f'{indent}role: {source_string(text)}')
            else:
                output.append(f'{indent}role:')
                for lead, body, key_text in parts:
                    key = key_for(key_text, paragraph=True)
                    title = f' {title_string(lead)}' if lead else ""
                    output.append(f'{indent}    paragraph {key}:{title}')
                    output.append(f'{indent}        {source_string(body)}')
        elif node["keyed"]:
            node["text"] += 1
            output.append(f'{indent}paragraph text_{node["text"]}:')
            output.append(f'{indent}    {source_string(text)}')
        else:
            output.append(f'{indent}{source_string(text)}')

    def key_for(title, *, paragraph=False):
        for quote, original in quote_originals.items():
            title = title.replace(quote, original)
        key = heading_key(" ".join(title.split()[:4]))
        sample = ('agent Probe:\n    role: "Role."\n' if args.kind == "agent"
                  else 'workflow Probe: "Probe"\n')
        for level in range(1, len(stack)):
            sample += f'{"    " * level}parent_{level}: "Parent"\n'
        indent = "    " * len(stack)
        sample += f'{indent}prior: "Prior"\n{indent}    paragraph probe: "Probe"\n{indent}        "Text"\n'
        if paragraph:
            sample += f'{indent}paragraph {key}: "Title"\n{indent}    "Text"\n'
            if len(stack) == 1 and args.kind == "agent":
                sample = f'agent Probe:\n    role:\n        paragraph {key}: "Title"\n            "Text"\n'
        else:
            sample += f'{indent}{key}: "Title"\n{indent}    paragraph probe: "Probe"\n{indent}        "Text"\n'
        try:
            parse_text(sample)
        except ParseError:
            key += "_"
        if args.kind == "agent" and len(stack) == 1 and key in _RESERVED_AGENT_FIELD_KEYS:
            key += "_"
        keys = stack[-1]["keys"]
        base, count = key, 1
        while key in keys:
            count += 1
            key = f"{base}_{count}"
        keys[key] = True
        return key

    for number, line, inside_fence, heading in markdown_lines(lines, path=args.path, start=start):
        if not inside_fence and not heading:
            lead = re.match(r'^\*\*(.+?)\*\*(?:\s|$)', line)
            line = re.sub(r'(?:^|(?<=\()|(?<=[.!?] )|(?<=[.!?][")] ))([A-Z][a-zA-Z0-9]*(?: [A-Z][a-zA-Z0-9]*){0,2}), '
                          r'([A-Z][a-z]+ \d{1,2}, \d{4})(?:, ([^\n{}]+?))?: "([^"{}]*)"(?=$|[\s).,;:!?])',
                          replace_quote, line)
        if not inside_fence:
            if heading:
                flush()
                stack = stack[:len(heading[1]) - 1]
                node = stack[-1]
                key = key_for(heading[2])
                output.append(f'{"    " * len(stack)}{key}: {title_string(heading[2])}')
                node["keyed"] = True
                stack.append({"keys": {}, "keyed": False, "text": 0})
                continue
            bold = re.match(r"^\*\*(.+?)\*\*\s+(.+)$", line)
            if bold and (not pending or not pending[-1]) and len(stack) > 1:
                flush()
                key = key_for(bold[1], paragraph=True)
                indent = "    " * len(stack)
                output.append(f'{indent}paragraph {key}: {title_string(bold[1])}')
                pending.append(bold[2])
                stack[-1]["keyed"] = True
                paragraph = True
                continue
            if paragraph and not line:
                flush()
                continue
        pending.append(line)
    flush()
    original = "\n".join(([f"# {title}"] if start == 2 else []) + lines)
    for number, line in enumerate(original.splitlines(), 1):
        for quote in re.finditer(r'"((?:[^"]|(?<=\s)"(?=\S)[^"]*")*)"', line):
            if (number, quote.start()) not in converted and len(quote[1].split()) >= 6:
                print(f"Quote left as prose at line {number}.", file=sys.stderr)
    output[:0] = [f'person {key}: {title_string(name)}' for key, name in people.items()]
    print("\n".join(output))
    if args.check:
        return check_render(args, output, lines, start)
    return 0


def check_render(args, output, lines, start):
    source = "\n".join(output) + "\n"
    if args.kind == "agent":
        source = source.replace("abstract agent ", "agent ", 1)
        stand_in = not any(line.startswith("    role:") for line in output)
        if stand_in:
            source = source.replace(f'agent {args.name}:', f'agent {args.name}:\n    role: "Stand-in."', 1)
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
            rendered = render_readable_block(compiled.fields[1], depth=1).splitlines()[2:]
    original = [line.rstrip() for line in lines]
    rendered = [line.rstrip() for line in rendered]
    while original and not original[0]:
        original.pop(0)
        start += 1
    while original and not original[-1]:
        original.pop()
    for number, (before, after) in enumerate(zip_longest(original, rendered, fillvalue=""), start):
        if before != after:
            print(f"Line {number} differs.\n  Markdown: {before}\n  Render: {after}", file=sys.stderr)
            return 1
    print("Render matches.", file=sys.stderr)
    return 0


def source_string(text):
    text = text.replace("\\", "\\\\")
    ending = re.search(r'"+$', text)
    text = text.replace('"""', '""\\"')
    if ending and len(ending[0]) % 3:
        text = text[:-1] + '\\"'
    return '"""' + text + '"""'


def title_string(text):
    if '"' in text:
        return source_string(text)
    return '"' + text.replace("\\", "\\\\") + '"'
