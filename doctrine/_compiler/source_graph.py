from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass, replace

from doctrine import model
from doctrine._compiler.constants import _INTERPOLATION_RE, LATE_ROOT
from doctrine._compiler.declaration_kinds import DECLARATION_KINDS
from doctrine._compiler.indexing import unit_loaded_imports, lookup_flow_registry_decl
from doctrine._compiler.teams import find_team_member, home_value_sources


def model_walk(value):
    yield value
    if is_dataclass(value):
        for field in fields(value):
            if field.compare:
                yield from model_walk(getattr(value, field.name))
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from model_walk(item)


def source_hash(declaration, base):
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
    graph = {}

    def visit(decl, owner):
        name = ".".join((*owner.module_parts, decl.name))
        if name in graph:
            return name
        dependencies = set()
        graph[name] = (owner, decl, dependencies)
        for value in model_walk(decl):
            refs = []
            if isinstance(value, model.NameRef):
                refs.append(value)
            elif isinstance(value, str):
                for match in _INTERPOLATION_RE.finditer(value):
                    if LATE_ROOT.fullmatch(match[0]):
                        continue
                    ref = context._parse_interpolation_expr_ref(match[1])
                    if ref is not None and ref.root is not None:
                        refs.append(ref.root)
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
