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
]
