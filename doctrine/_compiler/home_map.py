from __future__ import annotations

from dataclasses import dataclass, replace
from os.path import relpath

from doctrine import model
from doctrine.emit_common import agent_slug
from doctrine._compiler.naming import _agent_typed_field_key


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
            ("role",) if isinstance(field, (model.RoleScalar, model.RoleBlock)) else (field.key,) if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride, model.AuthoredSlotAbstract)) else (),
            field.source_span))
        if isinstance(field, (model.RoleScalar, model.RoleBlock, model.AuthoredSlotField,
            model.AuthoredSlotOverride, model.InputsField,
            model.OutputsField, model.AnalysisField, model.DecisionField, model.SkillsField,
            model.ReviewField, model.FinalOutputField, model.SelectorsField)) else field
        for field in fields))


def field_origin(spec, compiled):
    key = spec.field.key if isinstance(spec.field, (model.AuthoredSlotField, model.AuthoredSlotInherit, model.AuthoredSlotOverride)) else "role" if isinstance(spec.field, (model.RoleScalar, model.RoleBlock)) else _agent_typed_field_key(spec.field).split(":", 1)[0]
    origin = spec.slot_body.origin if spec.slot_body is not None else spec.field.origin
    return replace(compiled, origin=origin) if isinstance(compiled, model.RoleScalar) else replace(compiled, key=key, origin=origin)
