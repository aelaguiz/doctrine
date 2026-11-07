from __future__ import annotations

from os.path import relpath

import re
from datetime import date

from doctrine._compiler.constants import _INTERPOLATION_RE
from doctrine._compiler.indexing import lookup_flow_registry_decl, unit_loaded_imports
from doctrine._compiler.naming import _name_ref_from_dotted_name

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.source_graph import declaration_match, model_walk


def declaration_owners(context, declarations, base):
    owners = {name: set() for name in declarations}
    for (name, _), (unit, person) in declarations.items():
        if not isinstance(person, model.Person):
            continue
        for item in person.owns:
            if isinstance(item, str):
                paths = {path.resolve() for path in base.glob(item) if path.is_file()}
                if not paths:
                    raise compile_error(code="E651", summary="Invalid owner",
                        detail=f"Glob `{item}` in `owns:` matches no file.",
                        path=unit.prompt_file.source_path, source_span=person.source_span)
                owned = [key for key, (owner, declaration) in declarations.items()
                         if owner.prompt_file.source_path.resolve() in paths or (
                             isinstance(declaration, (model.Agent, model.WorkflowDecl))
                             and declaration.markdown_path and
                             (base / declaration.markdown_path).resolve() in paths)]
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
                    owned.extend(key for key, (_, decl) in declarations.items()
                                 if isinstance(decl, model.Member) and key[0].startswith(target + "."))
            for key in owned:
                owners[key].add(name)
    return owners

def quote_data(context, unit, quote, inline=False):
    fields = {}
    for key, value in quote.fields:
        if key in fields:
            detail = f"Inline quote: `{key}` is set twice." if inline else f"`{key}:` in `{quote.name}` is set twice."
            raise compile_error(code="E650", summary="Invalid quote", detail=detail, path=unit.prompt_file.source_path, source_span=quote.source_span)
        fields[key] = value
    for key in ("by", "on"):
        if key not in fields:
            raise compile_error(code="E650", summary="Invalid quote", detail=f"Quote `{quote.name}` needs `{key}:`.", path=unit.prompt_file.source_path, source_span=quote.source_span)
    ref = fields["by"]
    targets = () if ref.module_parts and ref.module_parts != unit.module_parts and ref.module_parts not in unit_loaded_imports(unit).visible_imported_units else context._decl_lookup_targets(ref, unit=unit)
    match = next((result for target in targets
                  if (result := lookup_flow_registry_decl(context.session.flow_for_unit(target.unit), registry_name="people_by_name", declaration_name=target.declaration_name))), None)
    if match is None:
        name = ".".join((*ref.module_parts, ref.declaration_name))
        detail = f"Inline quote: `{name}` is not a `person`." if inline else f"`by:` in `{quote.name}` is not a `person`."
        raise compile_error(code="E650", summary="Invalid quote", detail=detail, path=unit.prompt_file.source_path, source_span=quote.source_span)
    value = fields["on"]
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError
        day = date.fromisoformat(value)
    except ValueError:
        detail = f"Inline quote: `{value}` must be a date, `YYYY-MM-DD`." if inline else f"`on:` in `{quote.name}` must be a date, `YYYY-MM-DD`."
        raise compile_error(code="E650", summary="Invalid quote", detail=detail, path=unit.prompt_file.source_path, source_span=quote.source_span)
    return match, fields, day


def inline_quote(context, unit, expression):
    match = re.fullmatch(r'(.*):\s*"([^"{}]*)"\s*', expression, re.S)
    if not match:
        raise compile_error(code="E650", summary="Invalid quote", detail='Inline quote: the words must come last, as `: "<words>"`.', path=unit.prompt_file.source_path)
    parts = [part.strip() for part in match[1].split(",")]
    fields = [("by", _name_ref_from_dotted_name(parts[0])), ("on", parts[1])]
    for part in parts[2:]:
        key, _, value = part.partition(' ')
        if key not in {"to", "about", "source"}:
            raise compile_error(code="E650", summary="Invalid quote", detail=f"Inline quote: `{key}` is not a field. Use `to`, `about`, or `source`.", path=unit.prompt_file.source_path)
        fields.append((key, value))
    quote = model.Quote("", match[2], tuple(fields))
    return quote, quote_data(context, unit, quote, inline=True)


def render_quote(quote, data):
    (_, person), fields, day = data
    text = f"({person.title}, {day.strftime('%B')} {day.day}, {day.year}"
    for key in ("to", "about"):
        if key in fields:
            text += f", {key} {fields[key]}"
    return text + f': "{quote.title}")'


def quote_citations(context, declarations, base):
    cited, inline = {}, []
    for (name, _), (unit, declaration) in declarations.items():
        path = unit.prompt_file.source_path
        source = path.read_text()
        offset = sum(len(line) for line in source.splitlines(keepends=True)[:declaration.source_span.line - 1])
        for value in model_walk(declaration):
            refs = []
            if isinstance(value, model.SectionBodyRef):
                refs.append(value.ref.root)
            elif isinstance(value, str):
                for match in _INTERPOLATION_RE.finditer(value):
                    expression = match[1]
                    if ',' in expression:
                        quote, data = inline_quote(context, unit, expression)
                        pos = offset + re.search(r"\{\{\s*" + re.escape(expression.split(",", 1)[0].strip()) + r"\s*,", source[offset:]).start()
                        offset = pos + 2
                        site = f"{relpath(path, base)}:{source.count(chr(10), 0, pos) + 1}"
                        inline.append((name, site, quote, data))
                    else:
                        parsed = context._parse_interpolation_expr_ref(expression)
                        if parsed is not None and not parsed.path:
                            refs.append(parsed.root)
            for ref in refs:
                match = declaration_match(context, ref, unit)
                if match:
                    match = lookup_flow_registry_decl(context.session.flow_for_unit(match[0]), registry_name="quotes_by_name", declaration_name=match[1].name)
                if match:
                    key = '.'.join((*match[0].module_parts, match[1].name))
                    cited.setdefault(key, set()).add(name)
    return cited, inline
