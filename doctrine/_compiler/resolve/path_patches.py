from __future__ import annotations

from dataclasses import replace

from doctrine import model
from doctrine._model.core import role_text
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.home_map import child_origin
from doctrine._compiler.naming import patch_item_key
from doctrine._compiler.resolved_types import ResolvedAgentSlot, ResolvedSectionItem


def apply_path_patches(context, parent_items, paths, *, owner_label, unit, origin=None):
    def walk(node, tail, prefix, patch, replacement_origin):
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
            if short and not (isinstance(node, model.ReadableBlock) and node.kind == "details"):
                raise error("E612", "Conflicting patches", f"`{owner_label}` patches `{path}` under `{'.'.join(short)}`, which it already dropped or overrode.")
            if isinstance(patch, model.DropItem):
                return None
            if not isinstance(node, (ResolvedSectionItem, model.LocalSection)) and not (
                isinstance(node, model.ReadableBlock) and node.kind in {"section", "paragraph", "details", "sequence", "bullets", "checklist"}
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
            if isinstance(node, model.ReadableBlock) and node.kind in {"sequence", "bullets", "checklist"}:
                if any(not isinstance(item, (str, model.EmphasizedLine, model.SuperItem)) for item in items):
                    raise error("E611", "Invalid patch path", f"`{owner_label}`: `override {path}` gives a list a body it can't hold. A list takes items.")
                items = tuple(model.ReadableListItem(key=None, text=item) if isinstance(item, (str, model.EmphasizedLine)) else item for item in items)
            if isinstance(node, model.ReadableBlock) and node.kind == "paragraph":
                if any(not isinstance(item, (str, model.EmphasizedLine, model.SuperItem)) and not (isinstance(item, model.ReadableBlock) and item.kind == "details") for item in items):
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
            if replacement_origin and value.title is not None and (not isinstance(node, model.ReadableBlock) or node.kind == "section"):
                replacement_origin = replace(
                    replacement_origin, headings=(*replacement_origin.headings[:-1], title)
                )
            if isinstance(node, model.ReadableBlock):
                if node.kind != "details" or any(isinstance(item, model.SuperItem) for item in items):
                    items = merge_override(node.payload, items, owner_label, path, unit, patch.source_span, node.origin)
                return replace(node, title=title, payload=items, origin=replacement_origin,
                               anonymous=False if node.kind in {"sequence", "bullets", "checklist"} and value.title is not None else node.anonymous,
                               patch=(path, ".".join(short)) if short else None)
            if isinstance(node, ResolvedSectionItem):
                items = context._resolve_section_body_items(items, unit=unit, owner_label=owner_label, origin=replacement_origin)
            return replace(node, title=title, origin=replacement_origin,
                items=merge_override(node.items, items, owner_label, path, unit, patch.source_span, node.origin))
        if isinstance(patch, model.DetailsPath) and len(tail) == 1 and not (
            isinstance(node, (ResolvedAgentSlot, ResolvedSectionItem, model.LocalSection)) or
            isinstance(node, model.ReadableBlock) and node.kind in {"section", "paragraph"}
        ):
            kind = node.kind if isinstance(node, model.ReadableBlock) else "scalar"
            raise error("E611", "Invalid patch path", f"`{owner_label}`: `details {path}` attaches to a `{kind}`. Attach it to the section or paragraph that holds it.")
        if isinstance(node, model.RoleScalar):
            if not node.paragraphs:
                raise error("E611", "Invalid patch path", f"`{owner_label}`: `{path}` steps through `role`, which has no keyed paragraphs.")
            children = node.paragraphs
        elif isinstance(node, ResolvedAgentSlot):
            children = node.body.items
        elif isinstance(node, (ResolvedSectionItem, model.LocalSection)):
            children = node.items
        elif isinstance(node, model.ReadableBlock) and node.kind in {"section", "paragraph", "guard"}:
            children = node.payload
        else:
            if short and not isinstance(patch, model.DetailsPath):
                raise error("E612", "Conflicting patches", f"`{owner_label}` patches `{path}` under `{'.'.join(short)}`, which it already dropped or overrode.")
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
        if isinstance(patch, model.DetailsPath) and len(tail) == 1:
            if matched is not None:
                raise error("E612", "Conflicting patches", f"`{owner_label}` adds the case `{path}`, which it already has. Write `override {path}` to replace it.")
            children = (*children, replace(patch.value,
                origin=child_origin(replacement_origin, tail[0], patch.source_span),
                patch=(path, ".".join(short)) if short else None))
            if isinstance(node, ResolvedAgentSlot):
                return replace(node, body=replace(node.body, items=children))
            return replace(node, **{"payload" if isinstance(node, model.ReadableBlock) else "items": children})
        if matched is None:
            if short and not isinstance(patch, model.DetailsPath):
                raise error("E612", "Conflicting patches", f"`{owner_label}` patches `{path}` under `{'.'.join(short)}`, which it already dropped or overrode.")
            if isinstance(node, model.ReadableBlock) and node.kind == "paragraph" and not isinstance(patch, model.DetailsPath):
                raise error("E611", "Invalid patch path", f"`{owner_label}`: `{path}` steps through `{'.'.join(prefix)}`, which has no keyed items.")
            raise error(
                "E610",
                "Missing patch target",
                f"`{owner_label}` patches `{path}`, but its parent has no such key.",
            )
        title = matched.title if isinstance(matched, (ResolvedSectionItem, model.LocalSection)) or (
            isinstance(matched, model.ReadableBlock) and matched.kind == "section") else None
        replacement = walk(matched, tail[1:], (*prefix, tail[0]), patch,
                           child_origin(replacement_origin, tail[0], patch.source_span, title))
        children = tuple(
            replacement if child is matched else child
            for child in children
            if child is not matched or replacement is not None
        )
        if isinstance(node, ResolvedAgentSlot):
            return replace(node, body=replace(node.body, items=children))
        if isinstance(node, model.RoleScalar):
            return replace(node, paragraphs=children, text=role_text(children))
        return replace(
            node, **{"payload" if isinstance(node, model.ReadableBlock) else "items": children}
        )

    result = dict(parent_items)
    for path in sorted(paths, key=len, reverse=True):
        patch, short = paths[path]
        if path[0] not in result:
            if isinstance(patch, model.DetailsPath):
                raise compile_error(code="E611", summary="Invalid patch path", path=unit.prompt_file.source_path,
                    source_span=patch.source_span, detail=f"`{owner_label}`: `details {'.'.join(path)}` attaches to a `scalar`. Attach it to the section or paragraph that holds it.")
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
        item = result[path[0]]
        title = item.body.title if isinstance(item, ResolvedAgentSlot) else item.title if isinstance(item, (ResolvedSectionItem, model.LocalSection)) else None
        result[path[0]] = walk(item, path[1:], (path[0],), patch,
                               child_origin(patch.origin or origin, path[0], patch.source_span, title))
    return result


def merge_override(old, new, owner, path, unit, span, origin, parent_preamble=None, preamble=None):
    content = (*preamble, *new) if preamble is not None else new
    supers = [item for item in content if isinstance(item, model.SuperItem)]
    if len(supers) > 1:
        raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
            source_span=span, detail=f"`{owner}` writes `super` twice in `override {path}`.")
    if supers:
        old_keys = {patch_item_key(item) for item in old} - {None}
        for item in new:
            key = patch_item_key(item)
            if key in old_keys:
                raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
                    source_span=span, detail=f"`{owner}` writes `{key}` in `override {path}`, and `super` already brings it. Override `{key}` on its own, or drop `super`.")
        old = tuple(replace(item, origin=item.origin or child_origin(origin, item.key, item.source_span,
            item.title if isinstance(item, (ResolvedSectionItem, model.LocalSection)) or item.kind == "section" else None))
            if isinstance(item, (model.ReadableBlock, ResolvedSectionItem, model.LocalSection)) else item for item in old)
        if preamble is not None:
            head = tuple(part for item in preamble for part in (parent_preamble if isinstance(item, model.SuperItem) else (item,)))
            return head, (*old, *new)
        return tuple(part for item in new for part in (old if isinstance(item, model.SuperItem) else (item,)))
    def cases(items, direct, origin):
        for item in items:
            if isinstance(item, model.ReadableBlock):
                item_origin = item.origin or child_origin(origin, item.key, item.source_span,
                                                          item.title if item.kind == "section" else None)
                if item.kind == "details":
                    yield replace(item, origin=item_origin), direct
                elif item.kind in {"section", "paragraph", "guard"}:
                    yield from cases(item.payload, False, item_origin)
            elif isinstance(item, (ResolvedSectionItem, model.LocalSection)):
                yield from cases(item.items, False, item.origin or child_origin(origin, item.key, item.source_span, item.title))
    replaced = {item.key for item in new if isinstance(item, model.ReadableBlock) and item.kind == "details"}
    keys = {patch_item_key(item) for item in new}
    kept = []
    for case, direct in cases(old, True, origin):
        if case.key in keys and case.patch and case.patch[1] == path:
            patched, short = case.patch
            raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
                source_span=span, detail=f"`{owner}` patches `{patched}`, and `override {short}` writes `{case.key}` too. Keep one.")
        if direct and case.key in replaced:
            continue
        if case.key in keys:
            raise compile_error(code="E612", summary="Conflicting patches", path=unit.prompt_file.source_path,
                source_span=span, detail=f"`{owner}` overrides `{path}`, which would keep two cases keyed `{case.key}`. Drop one with a reason, or give them different keys.")
        keys.add(case.key)
        kept.append(case)
    result = (*new, *kept)
    return (preamble, result) if preamble is not None else result
