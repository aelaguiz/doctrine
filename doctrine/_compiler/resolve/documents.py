from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.resolved_types import (
    CompileError,
    IndexedUnit,
    ResolvedDocumentBody,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveDocumentsMixin:
    """Document-declaration resolution helpers for ResolveMixin."""

    def _resolve_document_decl(
        self, document_decl: model.DocumentDecl, *, unit: IndexedUnit
    ) -> ResolvedDocumentBody:
        document_key = (unit.module_parts, document_decl.name)
        cached = self._resolved_document_cache.get(document_key)
        if cached is not None:
            return cached

        if document_key in self._document_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._document_resolution_stack, document_key]
            )
            raise CompileError(f"Cyclic document inheritance: {cycle}")

        self._document_resolution_stack.append(document_key)
        try:
            parent_document: ResolvedDocumentBody | None = None
            parent_label: str | None = None
            if document_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_document_decl(
                    document_decl,
                    unit=unit,
                )
                parent_document = self._resolve_document_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"document {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_document_body(
                document_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, document_decl.name),
                parent_document=parent_document,
                parent_label=parent_label,
            )
            resolved = replace(
                resolved,
                render_profile=(
                    self._resolve_render_profile_ref(document_decl.render_profile_ref, unit=unit)
                    if document_decl.render_profile_ref is not None
                    else parent_document.render_profile if parent_document is not None else None
                ),
            )
            self._resolved_document_cache[document_key] = resolved
            return resolved
        finally:
            self._document_resolution_stack.pop()

    def _resolve_document_body(
        self,
        document_body: model.DocumentBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_document: ResolvedDocumentBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedDocumentBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="document prose",
                ambiguous_label="document prose interpolation ref",
            )
            for line in document_body.preamble
        )
        if parent_document is None:
            return ResolvedDocumentBody(
                title=document_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_document_items(
                    document_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_document.items}
        resolved_items: list[model.DocumentBlock] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in document_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate document block key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.DocumentBlock):
                if key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited document requires `override {key}` in {owner_label}"
                    )
                resolved_items.append(
                    self._resolve_document_block(
                        item,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined document entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined document entry in {parent_label}: {key}"
                )
            if item.kind != parent_item.kind:
                raise CompileError(
                    f"Override kind mismatch for document entry in {owner_label}: {key}"
                )
            accounted_keys.add(key)
            resolved_items.append(
                self._resolve_document_block(
                    model.DocumentBlock(
                        kind=item.kind,
                        key=item.key,
                        title=(
                            item.title
                            if item.title is not None
                            else None
                            if item.kind in {"sequence", "bullets", "checklist"}
                            else parent_item.title
                        ),
                        payload=item.payload,
                        requirement=(
                            item.requirement
                            if item.requirement is not None
                            else parent_item.requirement
                        ),
                        when_expr=item.when_expr if item.when_expr is not None else parent_item.when_expr,
                        item_schema=(
                            item.item_schema
                            if item.item_schema is not None
                            else parent_item.item_schema
                        ),
                        row_schema=(
                            item.row_schema if item.row_schema is not None else parent_item.row_schema
                        ),
                        anonymous=parent_item.anonymous,
                        legacy_section=parent_item.legacy_section,
                    ),
                    unit=unit,
                    owner_label=f"{owner_label}.{key}",
                )
            )

        missing_keys = [
            parent_item.key for parent_item in parent_document.items if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited document entry in {owner_label}: {missing}"
            )

        return ResolvedDocumentBody(
            title=document_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_non_inherited_document_items(
        self,
        items: tuple[model.DocumentItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[model.DocumentBlock, ...]:
        resolved: list[model.DocumentBlock] = []
        seen_keys: set[str] = set()
        for item in items:
            if isinstance(item, model.DocumentBlock):
                if item.key in seen_keys:
                    raise CompileError(f"Duplicate document block key in {owner_label}: {item.key}")
                seen_keys.add(item.key)
                resolved.append(
                    self._resolve_document_block(
                        item,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited document declaration in {owner_label}: {item.key}"
            )
        return tuple(resolved)
