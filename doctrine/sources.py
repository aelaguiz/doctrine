from __future__ import annotations

from os.path import relpath

import json

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.provenance import quote_citations, quote_data
from doctrine._compiler.source_graph import build_home_deps, declarations_in
from doctrine.home_commands import resolve_target
from doctrine.homes import compile_homes


def sources(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return 2
        homes, _, _, _ = compile_homes(target, session=session)
        context = CompilationContext(session)
        build_home_deps(context, homes)
        declarations = declarations_in(session)
        base = target.project_config.config_dir
        if args.person and not any(name == args.person and isinstance(decl, model.Person)
                                   for (name, _), (_, decl) in declarations.items()):
            raise compile_error(code="E650", summary="Invalid quote", detail=f"`--person {args.person}` is not a `person`.")
        cited, inline = quote_citations(context, declarations, base)
        entries = []
        for (name, _), (unit, quote) in declarations.items():
            if isinstance(quote, model.Quote):
                site = f"{relpath(unit.prompt_file.source_path, base)}:{quote.source_span.line}"
                entries.append((name, site, quote_data(context, unit, quote), sorted(cited.get(name, [])), name))
        entries.extend((site, site, data, [name], name) for name, site, _, data in inline)
        people = {}
        for key, site, (person_match, fields, day), citations, dependency in entries:
            unit, person = person_match
            person_key = '.'.join((*unit.module_parts, person.name))
            if args.person and person_key != args.person:
                continue
            row = {"key": key, "on": day.isoformat(), "to": fields.get("to"),
                   "about": fields.get("about"), "source": fields.get("source"), "site": site,
                   "cited_in": citations, "homes": sorted(home for home, data in homes.items()
                                                               if dependency in data["map"].deps)}
            people.setdefault(person_key, {"key": person_key, "title": person.title, "quotes": []})["quotes"].append(row)
        result = {"format_version": 1, "people": [people[key] for key in sorted(people)]}
        for person in result["people"]:
            person["quotes"].sort(key=lambda quote: (quote["on"], quote["key"]))
        if args.json:
            print(json.dumps(result))
        else:
            blocks = []
            for person in result["people"]:
                quotes = person["quotes"]
                missing = [quote for quote in quotes if quote["source"] is None]
                blocks.append(f"{person['title']}: {len(quotes)} {'quote' if len(quotes) == 1 else 'quotes'}, {len(missing)} with no source")
                for quote in quotes:
                    line = f"{quote['on']}  {quote['key']}"
                    if quote['key'] != quote['site']:
                        line += f"  {quote['site']}"
                    for key in ('to', 'about', 'source'):
                        if quote[key] is not None:
                            line += f"\n  {key}{':' if key == 'source' else ''} {quote[key]}"
                    line += f"\n  cited in {len(quote['cited_in'])} declarations, reaches {len(quote['homes'])} homes"
                    blocks.append(line)
                if missing:
                    blocks.append('No source:\n' + '\n'.join(f"  {quote['key']}" + (f"  {quote['site']}" if quote['key'] != quote['site'] else '') for quote in missing))
            print('\n\n'.join(blocks))
        return 0
