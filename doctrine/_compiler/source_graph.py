from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass, replace

from doctrine import model
from doctrine._compiler.constants import _INTERPOLATION_RE, LATE_ROOT
from doctrine._compiler.declaration_kinds import DECLARATION_KINDS
from doctrine._compiler.indexing import unit_loaded_imports, lookup_flow_registry_decl
from doctrine._compiler.teams import (
    find_home_team, find_team_member, home_value_sources, team_members,
)


def declarations_in(session):
    declarations = {}
    for flow in session._flow_cache.values():
        for unit in flow.units_by_path.values():
            for declaration in unit.prompt_file.declarations:
                if isinstance(declaration, model.ImportDecl):
                    continue
                name = ".".join((*unit.module_parts, declaration.name))
                declarations[name, type(declaration)] = (unit, declaration)
                if isinstance(declaration, model.Team):
                    declarations.update(
                        ((f"{name}.{member.key}", type(member)), (unit, member))
                        for member in declaration.fields if isinstance(member, model.Member)
                    )
    return declarations


def model_walk(value):
    yield value
    if is_dataclass(value):
        for field in fields(value):
            if field.compare:
                child = getattr(value, field.name)
                if isinstance(value, model.Team) and field.name == "fields":
                    child = tuple(item for item in child if not isinstance(item, model.Member))
                yield from model_walk(child)
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from model_walk(item)


def source_hash(declaration, base):
    if isinstance(declaration, model.Team):
        declaration = replace(declaration, fields=tuple(
            field for field in declaration.fields if not isinstance(field, model.Member)
        ))
    def data(value):
        if isinstance(value, model.SourceSpan):
            return None
        if is_dataclass(value):
            result = {
                "type": type(value).__qualname__,
                **{field.name: data(getattr(value, field.name))
                for field in fields(value) if field.compare},
            }
            if result.get("markdown_path"):
                result["markdown_content"] = (base / result["markdown_path"]).read_text()
            return result
        if isinstance(value, tuple):
            return [data(item) for item in value if not isinstance(item, model.SourceSpan)]
        return value
    return hashlib.sha256(json.dumps(data(declaration), sort_keys=True).encode()).hexdigest()


def declaration_match(context, ref, unit):
    unit = ref.scope_unit or unit
    imports = unit_loaded_imports(unit)
    if (ref.module_parts and ref.module_parts != unit.module_parts
            and ref.module_parts not in imports.visible_imported_units):
        match = declaration_match(
            context, model.NameRef(ref.module_parts[:-1], ref.module_parts[-1]), unit
        )
        if match is None:
            return None
        owner, declaration = match
        member = find_team_member(context, owner, f"{declaration.name}.{ref.declaration_name}")
        return None if member is None else (member[1].scope_unit or member[0], member[1])
    for target in context._decl_lookup_targets(ref, unit=unit):
        member = find_team_member(context, target.unit, target.declaration_name)
        if member is not None:
            return member[1].scope_unit or member[0], member[1]
        for kind in DECLARATION_KINDS:
            match = lookup_flow_registry_decl(
                context.session.flow_for_unit(target.unit),
                declaration_name=target.declaration_name, registry_name=kind.registry_attr,
            )
            if match is not None:
                return match
    return None


def dependency_graph(context, sources):
    graph, visited = {}, set()

    def visit(decl, owner):
        if isinstance(decl, model.Member):
            team = next(
                team for team in owner.declarations.teams_by_name.values()
                if any(isinstance(field, model.Member) and field.source_span == decl.source_span
                       for field in team.fields)
            )
            name = ".".join((*owner.module_parts, team.name, decl.key))
        else:
            name = ".".join((*owner.module_parts, decl.name))
        identity = (name, type(decl))
        if identity in visited:
            return name
        visited.add(identity)
        if name not in graph:
            graph[name] = (owner, decl, set())
        dependencies = graph[name][2]
        if isinstance(decl, model.Quote):
            for field, ref in decl.fields:
                if field == "by":
                    for target in context._decl_lookup_targets(ref, unit=owner):
                        match = lookup_flow_registry_decl(context.session.flow_for_unit(target.unit), registry_name="people_by_name", declaration_name=target.declaration_name)
                        if match:
                            dependencies.add(visit(match[1], match[0]))
        for value in model_walk(decl):
            refs = []
            reads_members = isinstance(value, model.ReadableBlock) and value.kind == "roster"
            if isinstance(value, str):
                reads_members = any(
                    match[1] == "team" and match[2] in {"members", "others"}
                    for match in LATE_ROOT.finditer(value)
                )
            if reads_members:
                match = find_home_team(context, sources[0][0], unit=sources[0][1])
                if match is not None:
                    team_unit, team = match
                    dependencies.update(
                        visit(member, member.scope_unit or team_unit)
                        for member in team_members(context, team, unit=team_unit)
                    )
            if isinstance(value, model.SectionBodyRef):
                ref = value.ref.root
                match = declaration_match(context, ref, owner)
                if match:
                    match = lookup_flow_registry_decl(context.session.flow_for_unit(match[0]), registry_name="quotes_by_name", declaration_name=match[1].name)
                if match:
                    dependencies.add(visit(match[1], match[0]))
            if isinstance(value, model.NameRef):
                refs.append(value)
            elif isinstance(value, str):
                for match in _INTERPOLATION_RE.finditer(value):
                    if LATE_ROOT.fullmatch(match[0]):
                        continue
                    match_text = match[1]
                    expression = match_text.split(",", 1)[0] if "," in match_text else match_text
                    ref = context._parse_interpolation_expr_ref(expression)
                    if ref is not None and ref.root is not None:
                        refs.append(ref.root)
                        match = declaration_match(context, ref.root, owner)
                        if match:
                            registry = "people_by_name" if "," in match_text else "quotes_by_name"
                            typed = lookup_flow_registry_decl(context.session.flow_for_unit(match[0]), registry_name=registry, declaration_name=match[1].name)
                            if typed:
                                dependencies.add(visit(typed[1], typed[0]))
            refs.extend(
                model.NameRef(ref.module_parts[:i], part, scope_unit=ref.scope_unit)
                for ref in tuple(refs) for i, part in enumerate(ref.module_parts)
            )
            for ref in refs:
                match = declaration_match(context, ref, owner)
                if match is not None:
                    dependencies.add(visit(match[1], match[0]))
        return name

    root = visit(*sources[0])
    graph[root][2].update(visit(*source) for source in sources[1:])
    return graph


def build_home_deps(context, homes):
    for data in homes.values():
        sources, team_sources = home_value_sources(context, data["owner"], data["unit"])
        graph = dependency_graph(context, [sources[0], *team_sources])
        data["map"] = replace(data["map"], deps=frozenset(graph))
        data["deps_graph"] = graph
