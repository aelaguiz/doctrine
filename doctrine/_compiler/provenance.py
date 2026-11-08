from __future__ import annotations

import re
from datetime import date
from os.path import relpath
from pathlib import PurePath

from doctrine import model
from doctrine._compiler.constants import _INTERPOLATION_RE
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import _name_ref_from_dotted_name
from doctrine._compiler.source_graph import declaration_match
from doctrine._compiler.naming import model_walk


def declaration_owners(context, declarations, base):
    owners = {name: set() for name in declarations}
    for (name, _), (unit, person) in declarations.items():
        if not isinstance(person, model.Person):
            continue
        for item in person.owns:
            if isinstance(item, str):
                owned = [key for key, (owner, declaration) in declarations.items()
                         if PurePath(relpath(owner.prompt_file.source_path, base)).full_match(item)
                         or (isinstance(declaration, (model.Agent, model.WorkflowDecl, model.FileDecl))
                             and declaration.markdown_path
                             and PurePath(declaration.markdown_path).full_match(item))]
                if not owned:
                    raise compile_error(code="E651", summary="Invalid owner",
                        detail=f"Glob `{item}` in `owns:` matches no source file.",
                        path=unit.prompt_file.source_path, source_span=person.source_span)
            else:
                match = declaration_match(context, item, unit)
                if match is None or isinstance(match[1], model.Member):
                    ref = ".".join((*item.module_parts, item.declaration_name))
                    raise compile_error(code="E651", summary="Invalid owner",
                        detail=f"`{ref}` in `owns:` resolves to nothing.",
                        path=unit.prompt_file.source_path, source_span=person.source_span)
                target = ".".join((*match[0].module_parts, match[1].name))
                owned = [(target, type(match[1]))]
                if isinstance(match[1], model.Team):
                    owned.extend((f"{target}.{member.key}", type(member))
                                 for member in match[1].fields if isinstance(member, model.Member))
            for key in owned:
                owners[key].add(name)
    return owners


def quote_error(detail, path=None, source_span=None):
    return compile_error(code="E650", summary="Invalid quote", detail=detail,
                         path=path, source_span=source_span)


def quote_data(context, unit, quote):
    fields = {}
    for key, value in quote.fields:
        if key in fields and (key != "context" or quote.name):
            detail = (f"Inline quote: `{key}` is set twice." if not quote.name
                      else f"`{key}:` in `{quote.name}` is set twice.")
            raise quote_error(detail, unit.prompt_file.source_path, quote.source_span)
        fields[key] = value
    for key in ("by", "on"):
        if key not in fields:
            raise quote_error(f"Quote `{quote.name}` needs `{key}:`.",
                              unit.prompt_file.source_path, quote.source_span)
    ref = fields["by"]
    match = declaration_match(context, ref, unit)
    if match is None or not isinstance(match[1], model.Person):
        name = ".".join((*ref.module_parts, ref.declaration_name))
        detail = (f"Inline quote: `{name}` is not a `person`." if not quote.name
                  else f"`by:` in `{quote.name}` is not a `person`.")
        raise quote_error(detail, unit.prompt_file.source_path, quote.source_span)
    value = fields["on"]
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError
        day = date.fromisoformat(value)
    except ValueError:
        detail = (f"Inline quote: `{value}` must be a date, `YYYY-MM-DD`." if not quote.name
                  else f"`on:` in `{quote.name}` must be a date, `YYYY-MM-DD`.")
        raise quote_error(detail, unit.prompt_file.source_path, quote.source_span)
    return match, fields, day


def inline_quote(context, unit, expression):
    match = re.fullmatch(r'(.*?):\s*"(.*)"\s*', expression, re.S)
    if not match:
        raise quote_error('Inline quote: the words must come last, as `: "<words>"`.',
                          unit.prompt_file.source_path)
    parts = [part.strip() for part in match[1].split(",")]
    fields = [("by", _name_ref_from_dotted_name(parts[0])),
              ("on", parts[1] if len(parts) > 1 else "")]
    for part in parts[2:]:
        key, _, value = part.partition(' ')
        if key not in {"to", "about", "source"}:
            fields.append(("context", part))
            continue
        if not value.strip():
            raise quote_error(f"Inline quote: `{key}` needs text.", unit.prompt_file.source_path)
        fields.append((key, value))
    quote = model.Quote("", match[2], tuple(fields))
    return quote, quote_data(context, unit, quote)


def render_quote(quote, data):
    (_, person), fields, day = data
    text = f"{person.title}, {day.strftime('%B')} {day.day}, {day.year}"
    for key, value in quote.fields:
        if key in ("to", "about", "context"):
            text += f", {key + ' ' if key != 'context' else ''}{value}"
    return text + f': "{quote.title}"'


def render_inline_quotes(context, unit, value):
    for inline in re.finditer(r"\{\{([^,{}]+),.*?\}\}", value, re.S):
        expression = inline.group(0)[2:-2]
        if "{" in expression or "}" in expression:
            raise quote_error("Inline quote: `{` and `}` can't appear inside one.",
                              unit.prompt_file.source_path)
        quote, data = inline_quote(context, unit, expression)
        value = value.replace(inline.group(0), render_quote(quote, data), 1)
    return value


def collect_quotes(context, declarations, base):
    rows, cited = [], {}
    for (name, _), (unit, declaration) in declarations.items():
        path = unit.prompt_file.source_path
        if isinstance(declaration, model.Quote):
            site = f"{relpath(path, base)}:{declaration.source_span.line}"
            rows.append({"key": name, "site": site,
                         "data": quote_data(context, unit, declaration),
                         "cited_in": cited.setdefault(name, set()), "dependency": name})
        source = None
        cursors = {}
        for value in model_walk(declaration):
            refs = []
            if isinstance(value, model.SectionBodyRef):
                refs.append(value.ref.root)
            elif isinstance(value, str):
                for match in _INTERPOLATION_RE.finditer(value):
                    expression = match[1]
                    start = re.match(r"\s*(\w+(?:\.\w+)*)\s*,\s*(\d{4}-\d{2}-\d{2})", expression)
                    if start:
                        _, data = inline_quote(context, unit, expression)
                        if source is None:
                            source = path.read_text()
                            declaration_start = sum(len(line) for line in source.splitlines(
                                keepends=True)[:declaration.source_span.line - 1])
                        key = start.group(1, 2)
                        cursor = cursors.get(key, declaration_start)
                        pos = cursor + re.search(r"\{\{\s*" + re.escape(key[0]) + r"\s*,\s*"
                                                 + re.escape(key[1]), source[cursor:]).start()
                        cursors[key] = pos + 2
                        site = f"{relpath(path, base)}:{source.count(chr(10), 0, pos) + 1}"
                        rows.append({"key": site, "site": site, "data": data,
                                     "cited_in": {name}, "dependency": name})
                    elif ',' not in expression:
                        parsed = context._parse_interpolation_expr_ref(expression)
                        if parsed is not None:
                            refs.append(parsed.root)
            for ref in refs:
                if ref is None:
                    continue
                match = declaration_match(context, ref, unit)
                if match and isinstance(match[1], model.Quote):
                    key = '.'.join((*match[0].module_parts, match[1].name))
                    cited.setdefault(key, set()).add(name)
    return rows
