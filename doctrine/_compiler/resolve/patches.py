from __future__ import annotations

from dataclasses import dataclass, replace

from doctrine import model
from doctrine._model.core import role_text, interpolate_role_paragraphs
from doctrine._compiler.home_map import stamp_agent, drop_records, child_origin
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import patch_item_key, TYPED_FIELDS, map_model, model_walk
from doctrine._compiler.teams import order_team_fields, validate_team, validate_values
from doctrine._compiler.resolved_types import IndexedUnit
from doctrine._compiler.resolve.path_patches import apply_path_patches


@dataclass(frozen=True, slots=True)
class PatchExpansion:
    items: tuple
    dropped_keys: set[str]
    path_overrides: dict[tuple[str, ...], object]


def expand_patch_items(items, *, parent_keys, kind, owner_label, unit) -> PatchExpansion:
    def error(code, summary, detail, item):
        return compile_error(
            code=code,
            summary=summary,
            detail=detail,
            path=unit.prompt_file.source_path,
            source_span=item.source_span,
        )

    inherit_type = model.AuthoredSlotInherit if kind == "agent" else model.InheritItem
    named = {}
    wildcard = None
    dropped = set()
    paths = {}
    overlaps = {}
    for item in items:
        if isinstance(item, model.InheritAll):
            if wildcard is not None:
                raise error(
                    "E613",
                    "Duplicate inherit *",
                    f"`{owner_label}` writes `inherit *` more than once.",
                    item,
                )
            if not parent_keys:
                raise error(
                    "E610",
                    "Missing patch target",
                    f"`{owner_label}` writes `inherit *`, but it has nothing to inherit.",
                    item,
                )
            wildcard = item
            continue
        path = (
            item.path
            if isinstance(item, (model.DropItem, model.OverridePath, model.DetailsPath))
            else (patch_item_key(item),)
        )
        if path[0] is None:
            continue
        text = ".".join(path)
        if kind == "agent" and isinstance(item, model.DropItem) and path == ("role",):
            raise error(
                "E612",
                "Conflicting patches",
                (
                    f"`{owner_label}` can't drop `role`. Write `role:` to replace it, "
                    "or `inherit role` to keep it."
                ),
                item,
            )
        for previous, first in named.items():
            if path == previous:
                if isinstance(item, (model.DropItem, model.OverridePath, model.DetailsPath)) or isinstance(
                    first, (model.DropItem, model.OverridePath, model.DetailsPath)
                ):
                    raise error(
                        "E612",
                        "Conflicting patches",
                        f"`{owner_label}` patches `{text}` twice.",
                        item,
                    )
            elif path[: len(previous)] == previous or previous[: len(path)] == path:
                short = path if len(path) < len(previous) else previous
                long = previous if short == path else path
                short_item, long_item = (item, first) if short == path else (first, item)
                if isinstance(short_item, (model.AuthoredSlotOverride, model.OverrideSection,
                                           model.ReadableOverrideBlock, model.OverridePath)) and isinstance(
                    long_item, (model.DropItem, model.OverridePath, model.DetailsPath)
                ):
                    body = short_item.value if isinstance(short_item, (model.AuthoredSlotOverride, model.OverridePath)) else short_item
                    content = (*body.preamble, *body.items) if isinstance(body, model.WorkflowBody) else body.payload if isinstance(body, model.ReadableOverrideBlock) else body.items if isinstance(body, model.OverrideSection) else ()
                    if not isinstance(content, tuple) or not any(isinstance(part, model.SuperItem) for part in content):
                        overlaps[long] = short
                    continue
                if isinstance(item, (model.InheritItem, model.AuthoredSlotInherit)) or isinstance(
                    first, (model.InheritItem, model.AuthoredSlotInherit)
                ):
                    detail = (
                        f"`{owner_label}` writes `inherit {short[0]}` beside a patch under "
                        f"`{short[0]}`. The patch already accounts for it."
                    )
                else:
                    long = path if len(path) > len(previous) else previous
                    detail = (
                        f"`{owner_label}` patches `{'.'.join(long)}` under "
                        f"`{'.'.join(short)}`, which it already dropped or overrode."
                    )
                raise error("E612", "Conflicting patches", detail, item)
        named[path] = item
        if isinstance(item, (model.DropItem, model.OverridePath, model.DetailsPath)):
            if path[0] not in parent_keys:
                raise error(
                    "E610",
                    "Missing patch target",
                    f"`{owner_label}` patches `{text}`, but its parent has no such key.",
                    item,
                )
            if len(path) > 1:
                paths[path] = item
            else:
                dropped.add(path[0])
    written_keys = {
        patch_item_key(item)
        for item in items
        if isinstance(item, (model.InheritItem, model.AuthoredSlotInherit, *TYPED_FIELDS))
    }
    replacements = {}
    for item in items:
        key = patch_item_key(item)
        if key in parent_keys and key not in written_keys and key not in replacements:
            replacements[key] = item
    result = []
    emitted_dotted = set()
    for item in items:
        if isinstance(item, model.InheritAll):
            for key in parent_keys:
                if key not in dropped and key not in written_keys:
                    result.append(
                        replacements.get(
                            key,
                            inherit_type(key=key, wildcard=True, source_span=item.source_span),
                        )
                    )
            continue
        if isinstance(item, (model.DropItem, model.OverridePath, model.DetailsPath)):
            key = item.path[0]
            if (len(item.path) > 1 and wildcard is None and key not in emitted_dotted
                    and (key,) not in named):
                result.append(inherit_type(key=key, source_span=item.source_span))
                emitted_dotted.add(key)
            continue
        key = patch_item_key(item)
        if wildcard is not None and replacements.get(key) is item:
            continue
        result.append(item)
    return PatchExpansion(tuple(result), dropped,
                          {path: (item, overlaps.get(path)) for path, item in paths.items()})


def prepare_body_patches(body, parent, *, kind, owner_label, unit, source_span):
    if kind == "schema":
        parent_keys = [
            key
            for key in ("sections", "gates", "artifacts", "groups")
            if parent is not None and getattr(parent, key)
        ]
    else:
        parent_keys = [item.key for item in parent.items] if parent is not None else []
    parent_preamble = parent.preamble if parent is not None else ()
    if parent_preamble:
        parent_keys.insert(0, "preamble")
    expansion = expand_patch_items(
        body.items, parent_keys=parent_keys, kind=kind, owner_label=owner_label, unit=unit
    )
    inherited_head = bool(parent_preamble) and any(
        isinstance(item, model.InheritItem) and item.key == "preamble" for item in expansion.items
    )
    if parent_preamble and not inherited_head and "preamble" not in expansion.dropped_keys:
        raise compile_error(
            code="E003",
            summary="Missing inherited entry",
            detail=f"Missing inherited {kind} entry in {owner_label}: preamble",
            path=unit.prompt_file.source_path,
            source_span=source_span,
        )
    return replace(
        body,
        preamble=(*parent_preamble, *body.preamble) if inherited_head else body.preamble,
        items=tuple(
            item
            for item in expansion.items
            if not (
                inherited_head and isinstance(item, model.InheritItem) and item.key == "preamble"
            )
        ),
    ), expansion


def expand_agent_patches(context, agent, *, unit):
    agent = stamp_agent(context, validate_team(agent, unit=unit), unit)
    validate_values(agent, unit=unit)
    parent_fields = {}
    keys = []
    if agent.parent_ref is not None:
        parent_unit, parent = context._resolve_parent_agent_decl(agent, unit=unit)
        context._resolve_agent_slots(parent, unit=parent_unit)
        parent, _ = context._expand_agent_patches(parent, unit=parent_unit)

        def rebind(value):
            return map_model(value, lambda item: replace(item, scope_unit=item.scope_unit or parent_unit)
                             if isinstance(item, model.NameRef) else None, {"scope_unit", "team_unit"})

        for field in parent.fields:
            if isinstance(
                field,
                (
                    model.AuthoredSlotField,
                    model.AuthoredSlotAbstract,
                    model.AuthoredSlotInherit,
                    model.AuthoredSlotOverride,
                ),
            ):
                continue
            key = patch_item_key(field)
            parent_fields.setdefault(key, []).append(rebind(field))
        keys = list(
            dict.fromkeys(
                patch_item_key(field)
                for field in parent.fields
                if not isinstance(field, model.AuthoredSlotAbstract)
            )
        )
    patch_fields = tuple(field for field in agent.fields if not isinstance(field, (model.ValuesField, model.BudgetField)))
    if isinstance(agent, (model.Member, model.Team)) and keys and not any(
        isinstance(field, model.InheritAll) for field in patch_fields
    ):
        patch_fields = (*patch_fields, model.InheritAll(source_span=agent.source_span))
    expansion = expand_patch_items(
        patch_fields, parent_keys=keys, kind="agent", owner_label=agent.name, unit=unit
    )
    fields = []
    accounted = set(expansion.dropped_keys)
    for field in expansion.items:
        key = patch_item_key(field)
        accounted.add(key)
        if isinstance(field, model.AuthoredSlotInherit) and key in parent_fields:
            for inherited in parent_fields[key]:
                if isinstance(inherited, model.RoleScalar):
                    inherited = replace(
                        inherited,
                        text=context._interpolate_authored_prose_string(
                            inherited.text,
                            unit=parent_unit,
                            owner_label=f"agent {parent.name}",
                            surface_label="role prose",
                        ),
                    )
                    if inherited.paragraphs:
                        paragraphs = interpolate_role_paragraphs(
                            inherited.paragraphs, context._interpolate_authored_prose_string,
                            unit=parent_unit, owner_label=f"agent {parent.name}")
                        inherited = replace(inherited, paragraphs=paragraphs)
                    role_paths = {path: patch for path, patch in expansion.path_overrides.items() if path[0] == "role"}
                    if role_paths:
                        inherited = apply_path_patches(context, {"role": inherited}, role_paths,
                                                       owner_label=agent.name, unit=unit)["role"]
                elif isinstance(inherited, model.RoleBlock):
                    role_paths = [p for p in expansion.path_overrides if p[0] == "role"]
                    if role_paths:
                        path = ".".join(role_paths[0])
                        raise compile_error(code="E611", summary="Invalid patch path", path=unit.prompt_file.source_path,
                            source_span=expansion.path_overrides[role_paths[0]][0].source_span,
                            detail=f"`{agent.name}`: `{path}` steps through `role`, which has no keyed paragraphs.")
                    inherited = replace(
                        inherited,
                        lines=tuple(
                            context._interpolate_authored_prose_line(
                                line,
                                unit=parent_unit,
                                owner_label=f"agent {parent.name}",
                                surface_label="role prose",
                            )
                            for line in inherited.lines
                        ),
                    )
                fields.append(mark_wildcard(inherited) if field.wildcard else inherited)
        else:
            if isinstance(field, model.RoleScalar) and any(
                isinstance(item, (model.InheritItem, model.InheritAll, model.OverridePath)) for item in field.paragraphs
            ):
                parent_role = parent_fields.get("role", [None])[0]
                if not isinstance(parent_role, model.RoleScalar) or not parent_role.paragraphs:
                    raise compile_error(code="E611", summary="Invalid patch path", path=unit.prompt_file.source_path,
                        source_span=field.source_span, detail=f"`{agent.name}` inherits from `role`, which has no keyed paragraphs.")
                paragraphs = interpolate_role_paragraphs(parent_role.paragraphs, context._interpolate_authored_prose_string,
                    unit=parent_unit, owner_label=f"agent {parent.name}")
                paragraphs = tuple(replace(item, origin=item.origin or child_origin(parent_role.origin, item.key, item.source_span)) for item in paragraphs)
                parent_by_key = {item.key: item for item in paragraphs}
                named = set()
                overrides = {}
                items = []
                for item in field.paragraphs:
                    if isinstance(item, model.InheritAll):
                        items.append(item)
                        continue
                    key = item.path[-1] if isinstance(item, model.OverridePath) else item.key
                    if isinstance(item, model.ReadableBlock) and key in parent_by_key:
                        raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
                            source_span=item.source_span, detail=f"`{agent.name}` adds the paragraph `role.{key}`, which it already inherits. Write `override paragraph {key}:` to replace it.")
                    if isinstance(item, (model.InheritItem, model.OverridePath)):
                        if key not in parent_by_key:
                            raise compile_error(code="E610", summary="Missing patch target", path=unit.prompt_file.source_path,
                                source_span=item.source_span, detail=f"`{agent.name}` patches `role.{key}`, but its parent has no such key.")
                        if key in named:
                            raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
                                source_span=item.source_span, detail=f"`{agent.name}` patches `role.{key}` twice.")
                        named.add(key)
                    if isinstance(item, model.OverridePath):
                        overrides[key] = (item, None)
                        item = model.InheritItem(key=key, source_span=item.source_span)
                    items.append(item)
                role_expansion = expand_patch_items(items, parent_keys=list(parent_by_key), kind="role", owner_label=agent.name, unit=unit)
                missing_role = [key for key in parent_by_key if key not in named and not any(isinstance(item, model.InheritAll) for item in items)]
                if missing_role:
                    raise compile_error(code="E003", summary="Missing inherited entry", path=unit.prompt_file.source_path,
                        source_span=field.source_span, detail=f"Missing inherited role paragraph in agent {agent.name}: {', '.join(missing_role)}")
                if overrides:
                    parent_role = replace(parent_role, paragraphs=paragraphs, text=role_text(paragraphs))
                    parent_role = apply_path_patches(context, {"role": parent_role},
                        {("role", key): patch for key, patch in overrides.items()}, owner_label=agent.name, unit=unit)["role"]
                    parent_by_key = {item.key: item for item in parent_role.paragraphs}
                paragraphs = tuple(parent_by_key[item.key] if isinstance(item, model.InheritItem) else item for item in role_expansion.items)
                field = replace(field, paragraphs=paragraphs, text=role_text(paragraphs))
            fields.append(field)
    missing = [key for key in parent_fields if key not in accounted]
    if missing:
        raise compile_error(
            code="E003",
            summary="Missing inherited entry",
            detail=f"Missing inherited authored slot in agent {agent.name}: {', '.join(missing)}",
            path=unit.prompt_file.source_path,
            source_span=agent.source_span,
        )
    fields = order_team_fields(agent, fields, keys=keys, parent_fields=parent_fields, unit=unit)
    drops = (*(parent.drops if agent.parent_ref else ()),
             *drop_records(agent.fields, ".".join((*unit.module_parts, agent.name))))
    return replace(agent, fields=tuple(fields), drops=drops), expansion


def mark_wildcard(value):
    def leaf(item):
        if isinstance(item, model.Origin):
            return replace(item, wildcard=True)
        if isinstance(item, (model.NameRef, IndexedUnit)):
            return item
    return map_model(value, leaf, {"scope_unit", "team_unit"})


def reject_super(body, owner, unit):
    for item in model_walk(body):
        if isinstance(item, model.SuperItem):
            raise compile_error(code="E614", summary="Super outside an override",
                detail=f"`{owner}` writes `super` outside an `override`.",
                path=unit.prompt_file.source_path, source_span=item.source_span,
                hints=("Write it in an override body, or delete it.",))
