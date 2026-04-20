"""Single entrypoint for `type:` resolution across every field-shaped surface.

Every surface that accepts `type: <CNAME>` on a field body (output schema
field/route field/def, readable row_schema entry, readable item_schema
entry, readable table column, record scalar) must route through
`resolve_field_type_ref` here. That is the only place E320 fires, and the
only place a CNAME becomes a `FieldTypeRef`. To add a new field-shaped
surface, make its resolver call this helper rather than rolling its own
builtin-or-enum path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from doctrine import model
from doctrine._compiler.indexing import IndexedUnit
from doctrine._compiler.reference_diagnostics import reference_compile_error
from doctrine._compiler.resolved_types import CompileError
from doctrine._model.core import SourceSpan


BUILTIN_TYPE_NAMES: frozenset[str] = frozenset(
    {"array", "boolean", "integer", "null", "number", "object", "string"}
)


@dataclass(slots=True, frozen=True)
class BuiltinTypeRef:
    name: str


@dataclass(slots=True, frozen=True)
class EnumTypeRef:
    ref: model.NameRef
    decl: model.EnumDecl


FieldTypeRef: TypeAlias = BuiltinTypeRef | EnumTypeRef


class EnumLookup(Protocol):
    def __call__(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> model.EnumDecl | None: ...


def resolve_field_type_ref(
    name: str,
    *,
    span: SourceSpan | None,
    unit: IndexedUnit,
    lookup_enum: EnumLookup,
) -> FieldTypeRef:
    """Resolve a field's `type: <name>` to a `FieldTypeRef`.

    Builtin CNAME -> `BuiltinTypeRef`. CNAME that resolves to an `enum`
    decl via `lookup_enum` -> `EnumTypeRef`. Anything else -> E320.
    """
    if name in BUILTIN_TYPE_NAMES:
        return BuiltinTypeRef(name=name)
    ref = model.NameRef(
        module_parts=(),
        declaration_name=name,
        source_span=span,
    )
    decl = lookup_enum(ref, unit=unit)
    if decl is not None:
        return EnumTypeRef(ref=ref, decl=decl)
    raise _raise_e320(name=name, span=span, unit=unit)


def resolve_record_scalar_type_refs(
    items: tuple[object, ...],
    *,
    unit: IndexedUnit,
    lookup_enum: EnumLookup,
) -> tuple[object, ...]:
    """Walk `items` and fill `type_ref` on every reachable `RecordScalar`.

    The walk is structural and immutable: each `RecordScalar` that carries a
    `type_name` but no `type_ref` is replaced with a copy whose `type_ref`
    resolves via `resolve_field_type_ref`. Unknown CNAMEs raise E320 at the
    span captured by the parser. `RecordSection` and `GuardedOutputSection`
    walls are descended; unrelated nodes (prose, refs, overrides) pass
    through unchanged.
    """
    return tuple(
        _resolve_record_type_ref_item(item, unit=unit, lookup_enum=lookup_enum)
        for item in items
    )


def _resolve_record_type_ref_item(
    item: object,
    *,
    unit: IndexedUnit,
    lookup_enum: EnumLookup,
) -> object:
    if isinstance(item, model.RecordScalar):
        resolved_body = None
        if item.body is not None:
            resolved_body = resolve_record_scalar_type_refs(
                item.body, unit=unit, lookup_enum=lookup_enum
            )
        resolved_type_ref = item.type_ref
        if resolved_type_ref is None and item.type_name is not None:
            resolved_type_ref = resolve_field_type_ref(
                item.type_name,
                span=item.type_source_span,
                unit=unit,
                lookup_enum=lookup_enum,
            )
        if resolved_body is item.body and resolved_type_ref is item.type_ref:
            return item
        return model.RecordScalar(
            key=item.key,
            value=item.value,
            body=resolved_body,
            type_ref=resolved_type_ref,
            type_name=item.type_name,
            type_source_span=item.type_source_span,
            source_span=item.source_span,
        )
    if isinstance(item, model.RecordSection):
        resolved_items = resolve_record_scalar_type_refs(
            item.items, unit=unit, lookup_enum=lookup_enum
        )
        if resolved_items is item.items:
            return item
        return model.RecordSection(
            key=item.key,
            title=item.title,
            items=resolved_items,
            source_span=item.source_span,
        )
    if isinstance(item, model.GuardedOutputSection):
        resolved_items = resolve_record_scalar_type_refs(
            item.items, unit=unit, lookup_enum=lookup_enum
        )
        if resolved_items is item.items:
            return item
        return model.GuardedOutputSection(
            key=item.key,
            title=item.title,
            when_expr=item.when_expr,
            items=resolved_items,
            source_span=item.source_span,
        )
    return item


def _raise_e320(
    *,
    name: str,
    span: SourceSpan | None,
    unit: IndexedUnit,
) -> CompileError:
    builtins = ", ".join(sorted(BUILTIN_TYPE_NAMES))
    return reference_compile_error(
        code="E320",
        summary="Field `type:` references unknown name",
        detail=(
            f"Field `type:` references unknown name `{name}`. "
            f"Declare `enum {name}: \"...\"` in this flow or import it, "
            f"or use a builtin primitive ({builtins})."
        ),
        unit=unit,
        source_span=span,
        hints=(
            f"Declare `enum {name}: \"...\"` before using it as a field type.",
            f"Or use a builtin primitive: {builtins}.",
        ),
    )


__all__ = [
    "BUILTIN_TYPE_NAMES",
    "BuiltinTypeRef",
    "EnumTypeRef",
    "FieldTypeRef",
    "EnumLookup",
    "resolve_field_type_ref",
    "resolve_record_scalar_type_refs",
]
