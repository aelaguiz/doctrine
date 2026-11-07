from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from os.path import relpath

from doctrine import model
from doctrine.emit_common import agent_slug
from doctrine._compiler.naming import _agent_typed_field_key
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
    home: str
    agent: str
    entries: tuple[MapEntry, ...]
    drops: tuple[DropRecord, ...]


def source_origin(context, declaration, unit, path, span):
    if unit.prompt_file.source_path is None:
        return None
    name = ".".join((*unit.module_parts, declaration.name))
    source = relpath(unit.prompt_file.source_path, context.session.project_config.config_dir or context.session.prompt_root.parent)
    shared = not isinstance(declaration, model.Agent) or declaration.abstract
    companion = "_details/" + "-".join((*unit.module_parts, agent_slug(declaration.name).replace("_", "-"))) + ".md" if shared else None
    headings = (declaration.body.title,) if isinstance(declaration, (model.WorkflowDecl, model.DocumentDecl)) else ()
    return name, path, f"{source}:{span.line if span else declaration.source_span.line if declaration.source_span else 1}", companion, headings


def child_origin(origin, key, span, title=None):
    if origin is None:
        return None
    site = origin[2].rsplit(":", 1)[0] + f":{span.line}" if span else origin[2]
    return origin[0], (*origin[1], key), site, origin[3], (*origin[4], title) if title else origin[4]


def stamp_agent(context, agent, unit):
    fields = []
    for field in agent.fields:
        if isinstance(field, model.Member):
            field = stamp_agent(context, replace(field, name=f"{agent.name}.{field.key}"), unit)
        if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride)) and isinstance(field.value, model.WorkflowBody) and field.origin is None:
            origin = source_origin(context, agent, unit, (field.key,), field.source_span)
            if origin:
                field = replace(field, origin=(*origin[:4], (field.value.title,)))
        fields.append(field)
    return replace(agent, fields=tuple(
        replace(field, origin=field.origin or source_origin(context, agent, unit,
            ("role",) if isinstance(field, (model.RoleScalar, model.RoleBlock)) else (field.key,) if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride)) else () if isinstance(field, (model.DropItem, model.OverridePath)) else (_agent_typed_field_key(field).split(":", 1)[0],),
            field.source_span))
        if isinstance(field, (model.RoleScalar, model.RoleBlock, model.AuthoredSlotField,
            model.AuthoredSlotOverride, model.InputsField,
            model.OutputsField, model.AnalysisField, model.DecisionField, model.SkillsField,
            model.ReviewField, model.FinalOutputField, model.SelectorsField, model.DropItem, model.OverridePath)) else field
        for field in fields))


def field_origin(spec, compiled):
    key = spec.field.key if isinstance(spec.field, (model.AuthoredSlotField, model.AuthoredSlotInherit, model.AuthoredSlotOverride)) else "role" if isinstance(spec.field, (model.RoleScalar, model.RoleBlock)) else _agent_typed_field_key(spec.field).split(":", 1)[0]
    origin = spec.slot_body.origin if spec.slot_body is not None else spec.field.origin
    return replace(compiled, origin=origin) if isinstance(compiled, model.RoleScalar) else replace(compiled, key=key, origin=origin)


def drop_records(items, origin):
    return tuple(DropRecord(item.path, item.origin[0] if item.origin else origin, item.reason)
                 for item in items if isinstance(item, model.DropItem))


def build_home_map(compiled, home):
    entries, drops = [], list(compiled.drops)
    def visit(item, path, depth, profile, always_on, entry):
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
                    result = visit(child, nested, depth + 1, profile, always_on, bool(child.key) and len(path) < 2)
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
                origin = item.origin
                entries.insert(position, MapEntry(path[:2], title, origin[0], origin[1], origin[2], always_on,
                    hashlib.sha256(text.encode()).hexdigest(), len(text.encode("utf-16-le")) // 2, len(text.encode())))
            return None
        return item
    for field in compiled.fields:
        visit(field, ("role",) if isinstance(field, model.RoleScalar) else (field.key,), 2, DEFAULT_PROFILE, True, True)
    return HomeMap(home, compiled.name, tuple(entries), tuple(drops))
