from __future__ import annotations

import json

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.provenance import collect_quotes, quote_error
from doctrine._compiler.source_graph import build_home_deps, declarations_in
from doctrine.home_commands import resolve_target
from doctrine.homes import compile_homes


def quote_site(quote):
    return quote["site"] if quote["key"] == quote["site"] else f"{quote['key']}  {quote['site']}"


def sources(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return 2
        homes, _, _, _ = compile_homes(target, session=session)
        context = CompilationContext(session)
        build_home_deps(context, homes)
        declarations = declarations_in(session)
        base = target.project_config.config_dir
        if args.person and not any(args.person in (name, decl.name) and isinstance(decl, model.Person)
                                   for (name, _), (_, decl) in declarations.items()):
            raise quote_error(f"`--person {args.person}` is not a `person`.")
        entries = collect_quotes(context, declarations, base)
        people = {}
        for entry in entries:
            person_match, fields, day = entry["data"]
            unit, person = person_match
            person_key = '.'.join((*unit.module_parts, person.name))
            if args.person and args.person not in (person_key, person.name):
                continue
            row = {"key": entry["key"], "on": day.isoformat(), "to": fields.get("to"),
                   "about": fields.get("about"), "source": fields.get("source"),
                   "site": entry["site"], "cited_in": sorted(entry["cited_in"]),
                   "homes": sorted(home for home, data in homes.items()
                                   if entry["dependency"] in data["map"].deps)}
            people.setdefault(person_key, {"key": person_key, "title": person.title,
                                           "quotes": []})["quotes"].append(row)
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
                blocks.append(f"{person['title']}: {len(quotes)} "
                              f"{'quote' if len(quotes) == 1 else 'quotes'}, "
                              f"{len(missing)} with no source")
                for quote in quotes:
                    line = f"{quote['on']}  {quote_site(quote)}"
                    for key in ('to', 'about', 'source'):
                        if quote[key] is not None:
                            line += f"\n  {key}{':' if key == 'source' else ''} {quote[key]}"
                    count, reached = len(quote['cited_in']), len(quote['homes'])
                    line += (f"\n  cited in {count} "
                             f"{'declaration' if count == 1 else 'declarations'}, "
                             f"reaches {reached} {'home' if reached == 1 else 'homes'}")
                    blocks.append(line)
                if missing:
                    blocks.append('No source:\n' + '\n'.join(
                        f"  {quote_site(quote)}" for quote in missing
                    ))
            print('\n\n'.join(blocks))
        return 0
