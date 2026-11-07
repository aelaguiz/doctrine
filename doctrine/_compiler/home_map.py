from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from os.path import relpath

from doctrine import model
from doctrine.emit_common import agent_slug
from doctrine.runtime_load import text_size
from doctrine._compiler.naming import patch_item_key
from doctrine._compiler.types import CompiledSection, CompiledGuardBlock, CompiledRuleBlock
from doctrine._renderer.blocks import _render_block
from doctrine._renderer.semantic import DEFAULT_PROFILE


@dataclass(frozen=True, slots=True)
class MapEntry:
    path: tuple[str, ...]
    title: str | None
    origin: str
    origin_path: tuple[str, ...]
    site: str
    always_on: bool
    text_hash: str
    size_utf16: int
    size_bytes: int


@dataclass(frozen=True, slots=True)
class DropRecord:
    path: tuple[str, ...]
    origin: str
    reason: str


@dataclass(frozen=True, slots=True)
class HomeMap:
    entries: tuple[MapEntry, ...]
    drops: tuple[DropRecord, ...]
    texts: dict[MapEntry, str]
    wildcard_keys: frozenset[tuple[str, ...]] = frozenset()
    deps: frozenset[str] = frozenset()


def source_origin(context, declaration, unit, path, span):
    if unit.prompt_file.source_path is None:
        return None
    name = ".".join((*unit.module_parts, declaration.name))
    base = context.session.project_config.config_dir or context.session.prompt_root.parent
    source = relpath(
        base / declaration.markdown_path
        if isinstance(declaration, (model.Agent, model.WorkflowDecl)) and declaration.markdown_path
        else unit.prompt_file.source_path,
        base,
    )
    shared = not isinstance(declaration, model.Agent) or declaration.abstract
    slug = "-".join((*unit.module_parts, agent_slug(declaration.name).replace("_", "-")))
    companion = f"_details/{slug}.md" if shared else None
    headings = (
        (declaration.body.title,)
        if isinstance(declaration, (model.WorkflowDecl, model.DocumentDecl))
        else ()
    )
    line = span.line if span else declaration.source_span.line if declaration.source_span else 1
    return model.Origin(name, path, f"{source}:{line}", companion, headings, line, scope_unit=unit)


def child_origin(origin, key, span, title=None):
    if origin is None:
        return None
    line = span.line if span else origin.line
    return replace(
        origin,
        path=(*origin.path, key),
        line=line,
        site=origin.site.rsplit(":", 1)[0] + f":{line}",
        headings=(*origin.headings, title) if title else origin.headings,
    )


def stamp_agent(context, agent, unit):
    fields = []
    for field in agent.fields:
        if isinstance(field, model.Member):
            field = stamp_agent(context, replace(field, name=f"{agent.name}.{field.key}"), unit)
        if hasattr(field, "origin") and not isinstance(field, model.Member):
            key = patch_item_key(field)
            path = (key,) if key is not None else ()
            origin = field.origin or source_origin(context, agent, unit, path, field.source_span)
            if (
                isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride))
                and isinstance(field.value, model.WorkflowBody)
                and field.origin is None
                and origin
            ):
                origin = replace(origin, headings=(field.value.title,))
            field = replace(field, origin=origin)
        fields.append(field)
    return replace(agent, fields=tuple(fields))


def field_origin(spec, compiled):
    key = patch_item_key(spec.field)
    origin = spec.slot_body.origin if spec.slot_body is not None else spec.field.origin
    return (
        replace(compiled, origin=origin)
        if isinstance(compiled, model.RoleScalar)
        else replace(compiled, key=key, origin=origin)
    )


def drop_records(items, origin):
    return tuple(
        DropRecord(item.path, item.origin.declaration if item.origin else origin, item.reason)
        for item in items
        if isinstance(item, model.DropItem)
    )


def build_home_map(compiled):
    entries, texts, drops, wildcard_keys = [], {}, list(compiled.drops), set()

    def visit(item, path, depth, profile, always_on, entry, origin):
        origin = item.origin or origin
        if origin and origin.wildcard:
            wildcard_keys.add(path)
        position = len(entries)
        details = isinstance(item, CompiledSection) and item.kind == "details"
        if details and always_on:
            always_on, entry = False, True
        if isinstance(item, (CompiledSection, CompiledGuardBlock)):
            if isinstance(item, CompiledSection):
                profile = item.render_profile or profile
                drops.extend(replace(drop, path=(*path, *drop.path)) for drop in item.drops)
            body = []
            for child in item.body:
                if isinstance(child, (str, model.EmphasizedLine)):
                    body.append(child)
                else:
                    nested = (*path, child.key) if child.key else path
                    result = visit(
                        child,
                        nested,
                        depth + 1,
                        profile,
                        always_on,
                        bool(child.key),
                        origin,
                    )
                    if result is not None:
                        body.append(result)
            item = replace(item, body=tuple(body))
        if entry:
            if isinstance(item, model.RoleScalar):
                text, title = item.text.strip("\n"), None
            else:
                rendered = replace(item, kind="section") if details else item
                text = _render_block(rendered, depth=depth, profile=profile).strip("\n")
                if details and not item.title:
                    text = text.partition("\n\n")[2]
                title = None if isinstance(item, CompiledRuleBlock) else item.title
            if text:
                entry = MapEntry(
                    path, title, origin.declaration, origin.path, origin.site, always_on,
                    hashlib.sha256(text.encode()).hexdigest(),
                    text_size(text, "claude"), text_size(text, "codex"),
                )
                entries.insert(position, entry)
                texts[entry] = text
            return None
        return item

    for field in compiled.fields:
        path = ("role",) if isinstance(field, model.RoleScalar) else (field.key,)
        visit(field, path, 2, DEFAULT_PROFILE, True, True, field.origin)
    return HomeMap(tuple(entries), tuple(drops), texts, frozenset(wildcard_keys))
