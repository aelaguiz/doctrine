from __future__ import annotations

from doctrine import model
from dataclasses import replace

from doctrine._compiler.readable_diagnostics import (
    document_patch_error,
    duplicate_readable_key_error,
    readable_compile_error,
    readable_related_site,
    readable_source_span,
)
from doctrine._compiler.resolved_types import (
    IndexedUnit,
    ResolvedDocumentBody,
)
from doctrine._compiler.support_files import _dotted_decl_name


class ResolveDocumentsMixin:
    """Document-declaration resolution helpers for ResolveMixin."""

    def _document_item_by_key(
        self,
        items: tuple[model.DocumentItem, ...],
        key: str,
    ) -> object | None:
        return next((item for item in items if getattr(item, "key", None) == key), None)

    def _document_missing_related_sites(
        self,
        *,
        parent_unit: IndexedUnit | None,
        parent_body: model.DocumentBody | None,
        missing_keys: tuple[str, ...],
    ) -> tuple:
        if parent_unit is None or parent_body is None:
            return ()
        related = []
        for key in missing_keys:
            parent_item = self._document_item_by_key(parent_body.items, key)
            if parent_item is None:
                continue
            related.append(
                readable_related_site(
                    label=f"inherited `{key}` entry",
                    unit=parent_unit,
                    source_span=readable_source_span(parent_item),
                )
            )
        return tuple(related)

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
            raise readable_compile_error(
                code="E299",
                summary="Compile failure",
                detail=f"Cyclic document inheritance: {cycle}",
                unit=unit,
                source_span=document_decl.source_span,
            )

        self._document_resolution_stack.append(document_key)
        try:
            parent_document: ResolvedDocumentBody | None = None
            parent_body: model.DocumentBody | None = None
            parent_unit: IndexedUnit | None = None
            parent_label: str | None = None
            if document_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_document_decl(
                    document_decl,
                    unit=unit,
                )
                parent_document = self._resolve_document_decl(parent_decl, unit=parent_unit)
                parent_body = parent_decl.body
                parent_label = (
                    f"document {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            with self._with_addressable_self_root(
                self._local_addressable_self_root_ref(document_decl.name)
            ):
                resolved = self._resolve_document_body(
                    document_decl.body,
                    unit=unit,
                    owner_label=_dotted_decl_name(unit.module_parts, document_decl.name),
                    owner_source_span=document_decl.source_span,
                    parent_document=parent_document,
                    parent_body=parent_body,
                    parent_unit=parent_unit,
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
        owner_source_span: model.SourceSpan | None = None,
        parent_document: ResolvedDocumentBody | None = None,
        parent_body: model.DocumentBody | None = None,
        parent_unit: IndexedUnit | None = None,
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
        emitted_items: dict[str, object] = {}
        accounted_keys: set[str] = set()

        for item in document_body.items:
            key = item.key
            if key in emitted_items:
                raise duplicate_readable_key_error(
                    subject_label="Document",
                    owner_label=owner_label,
                    kind_label="document block",
                    key=key,
                    unit=unit,
                    source_span=readable_source_span(item),
                    first_source_span=readable_source_span(emitted_items[key]),
                )
            emitted_items[key] = item

            if isinstance(item, model.DocumentBlock):
                if key in parent_items_by_key:
                    raise document_patch_error(
                        detail=(
                            f"Document `{owner_label}` must use `override {key}` when it "
                            "patches an inherited document block."
                        ),
                        unit=unit,
                        source_span=item.source_span,
                        related=self._document_missing_related_sites(
                            parent_unit=parent_unit,
                            parent_body=parent_body,
                            missing_keys=(key,),
                        ),
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
                    raise document_patch_error(
                        detail=f"Document `{owner_label}` cannot inherit undefined entry `{key}`.",
                        unit=unit,
                        source_span=item.source_span or owner_source_span,
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise readable_compile_error(
                    code="E001",
                    summary="Cannot override undefined inherited entry",
                    detail=f"Cannot override undefined document entry in {parent_label}: {key}",
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                )
            if item.kind != parent_item.kind:
                raise document_patch_error(
                    detail=(
                        f"Document `{owner_label}` overrides entry `{key}` with the wrong "
                        "block kind."
                    ),
                    unit=unit,
                    source_span=item.source_span or owner_source_span,
                    related=self._document_missing_related_sites(
                        parent_unit=parent_unit,
                        parent_body=parent_body,
                        missing_keys=(key,),
                    ),
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
                        source_span=item.source_span,
                    ),
                    unit=unit,
                    owner_label=f"{owner_label}.{key}",
                )
            )

        missing_keys = tuple(
            parent_item.key for parent_item in parent_document.items if parent_item.key not in accounted_keys
        )
        if missing_keys:
            raise readable_compile_error(
                code="E003",
                summary="Missing inherited entry",
                detail=(
                    f"Missing inherited document entry in {owner_label}: "
                    f"{', '.join(missing_keys)}"
                ),
                unit=unit,
                source_span=owner_source_span,
                related=self._document_missing_related_sites(
                    parent_unit=parent_unit,
                    parent_body=parent_body,
                    missing_keys=missing_keys,
                ),
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
        seen_keys: dict[str, model.DocumentBlock] = {}
        for item in items:
            if isinstance(item, model.DocumentBlock):
                if item.key in seen_keys:
                    raise duplicate_readable_key_error(
                        subject_label="Document",
                        owner_label=owner_label,
                        kind_label="document block",
                        key=item.key,
                        unit=unit,
                        source_span=item.source_span,
                        first_source_span=seen_keys[item.key].source_span,
                    )
                seen_keys[item.key] = item
                resolved.append(
                    self._resolve_document_block(
                        item,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                    )
                )
                continue
            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise document_patch_error(
                detail=(
                    f"`{item_label}` for document entry `{item.key}` requires an inherited "
                    f"document declaration in `{owner_label}`."
                ),
                unit=unit,
                source_span=item.source_span,
            )
        return tuple(resolved)
