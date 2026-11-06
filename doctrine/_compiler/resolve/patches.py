from __future__ import annotations

from dataclasses import dataclass, replace, fields as dataclass_fields, is_dataclass

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.naming import _agent_typed_field_key
from doctrine._compiler.resolved_types import ResolvedAgentSlot, ResolvedSectionItem


TYPED_FIELDS = (
    model.RoleScalar,
    model.RoleBlock,
    model.InputsField,
    model.OutputsField,
    model.AnalysisField,
    model.DecisionField,
    model.SkillsField,
    model.ReviewField,
    model.FinalOutputField,
    model.SelectorsField,
)


@dataclass(frozen=True, slots=True)
class PatchExpansion:
    items: tuple
    dropped_keys: set[str]
    path_overrides: dict[tuple[str, ...], object]


def patch_item_key(item):
    if isinstance(item, (model.RoleScalar, model.RoleBlock)):
        return "role"
    if isinstance(item, TYPED_FIELDS):
        return _agent_typed_field_key(item).split(":", 1)[0]
    if isinstance(item, (model.ReviewFieldsConfig, model.ReviewOverrideFields)):
        return "fields"
    if isinstance(item, (model.SchemaSectionsBlock, model.SchemaOverrideSectionsBlock)):
        return "sections"
    if isinstance(item, (model.SchemaGatesBlock, model.SchemaOverrideGatesBlock)):
        return "gates"
    if isinstance(item, (model.SchemaArtifactsBlock, model.SchemaOverrideArtifactsBlock)):
        return "artifacts"
    if isinstance(item, (model.SchemaGroupsBlock, model.SchemaOverrideGroupsBlock)):
        return "groups"
    return getattr(item, "key", None)


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
    for item in items:
        if isinstance(item, model.InheritAll):
            if wildcard is not None:
                raise error(
                    "E613",
                    "Duplicate inherit *",
                    f"`{owner_label}` writes `inherit *` more than once.",
                    item,
                )
            wildcard = item
            continue
        path = (
            item.path
            if isinstance(item, (model.DropItem, model.OverridePath))
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
                if isinstance(item, (model.DropItem, model.OverridePath)) or isinstance(
                    first, (model.DropItem, model.OverridePath)
                ):
                    raise error(
                        "E612",
                        "Conflicting patches",
                        f"`{owner_label}` patches `{text}` twice.",
                        item,
                    )
            elif path[: len(previous)] == previous or previous[: len(path)] == path:
                short = path if len(path) < len(previous) else previous
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
        if isinstance(item, (model.DropItem, model.OverridePath)):
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
        if key in parent_keys and key not in written_keys:
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
                            inherit_type(key=key, source_span=item.source_span),
                        )
                    )
            continue
        if isinstance(item, (model.DropItem, model.OverridePath)):
            key = item.path[0]
            if len(item.path) > 1 and wildcard is None and key not in emitted_dotted:
                result.append(inherit_type(key=key, source_span=item.source_span))
                emitted_dotted.add(key)
            continue
        key = patch_item_key(item)
        if wildcard is not None and key in replacements:
            continue
        result.append(item)
    return PatchExpansion(tuple(result), dropped, paths)


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
    parent_fields = {}
    keys = []
    if agent.parent_ref is not None:
        parent_unit, parent = context._resolve_parent_agent_decl(agent, unit=unit)
        context._resolve_agent_slots(parent, unit=parent_unit)
        parent, _ = expand_agent_patches(context, parent, unit=parent_unit)

        def rebind(value):
            if isinstance(value, model.NameRef):
                return context._rebind_inherited_output_name_ref(
                    value,
                    parent_unit=parent_unit,
                    rebound_imported=True,
                )
            if isinstance(value, tuple):
                return tuple(rebind(item) for item in value)
            if is_dataclass(value):
                return replace(
                    value,
                    **{
                        field.name: rebind(getattr(value, field.name))
                        for field in dataclass_fields(value)
                    },
                )
            return value

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
    expansion = expand_patch_items(
        agent.fields, parent_keys=keys, kind="agent", owner_label=agent.name, unit=unit
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
                elif isinstance(inherited, model.RoleBlock):
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
                fields.append(inherited)
        else:
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
    return replace(agent, fields=tuple(fields)), expansion


def apply_path_patches(context, parent_items, paths, *, owner_label, unit):
    def walk(node, tail, prefix, patch):
        path = ".".join(patch.path)

        def error(code, summary, detail):
            return compile_error(
                code=code,
                summary=summary,
                detail=detail,
                path=unit.prompt_file.source_path,
                source_span=patch.source_span,
            )

        if not tail:
            if isinstance(patch, model.DropItem):
                return None
            if not isinstance(node, (ResolvedSectionItem, model.LocalSection)) and not (
                isinstance(node, model.ReadableBlock) and node.kind in {"section", "paragraph"}
            ):
                kind = node.kind if isinstance(node, model.ReadableBlock) else "scalar"
                raise error(
                    "E611",
                    "Invalid patch path",
                    (
                        f"`{owner_label}`: `override {path}` targets a `{kind}`. "
                        "Override the section that holds it."
                    ),
                )
            value = patch.value
            items = (*value.preamble, *value.items)
            if isinstance(node, model.ReadableBlock) and node.kind == "paragraph":
                if any(not isinstance(item, (str, model.EmphasizedLine)) for item in items):
                    raise error(
                        "E611",
                        "Invalid patch path",
                        (
                            f"`{owner_label}`: `override {path}` gives a paragraph "
                            "a body it can't hold. "
                            "A paragraph takes prose and `details`."
                        ),
                    )
            title = value.title if value.title is not None else node.title
            if isinstance(node, model.ReadableBlock):
                return replace(node, title=title, payload=items)
            return replace(
                node,
                title=title,
                items=items
                if isinstance(node, model.LocalSection)
                else context._resolve_section_body_items(items, unit=unit, owner_label=owner_label),
            )
        if isinstance(node, ResolvedAgentSlot):
            children = node.body.items
        elif isinstance(node, (ResolvedSectionItem, model.LocalSection)):
            children = node.items
        elif isinstance(node, model.ReadableBlock) and node.kind == "section":
            children = node.payload
        else:
            raise error(
                "E611",
                "Invalid patch path",
                (
                    f"`{owner_label}`: `{path}` steps through `{'.'.join(prefix)}`, "
                    "which has no keyed items."
                ),
            )
        matched = next(
            (child for child in children if getattr(child, "key", None) == tail[0]), None
        )
        if matched is None:
            raise error(
                "E610",
                "Missing patch target",
                f"`{owner_label}` patches `{path}`, but its parent has no such key.",
            )
        replacement = walk(matched, tail[1:], (*prefix, tail[0]), patch)
        children = tuple(
            replacement if child is matched else child
            for child in children
            if child is not matched or replacement is not None
        )
        if isinstance(node, ResolvedAgentSlot):
            return replace(node, body=replace(node.body, items=children))
        return replace(
            node, **{"payload" if isinstance(node, model.ReadableBlock) else "items": children}
        )

    result = dict(parent_items)
    for path, patch in paths.items():
        if path[0] not in result:
            raise compile_error(
                code="E611",
                summary="Invalid patch path",
                detail=(
                    f"`{owner_label}`: `{'.'.join(path)}` steps through `{path[0]}`, "
                    "which has no keyed items."
                ),
                path=unit.prompt_file.source_path,
                source_span=patch.source_span,
            )
        result[path[0]] = walk(result[path[0]], path[1:], (path[0],), patch)
    return result
