from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import InheritItem, NameRef, SourceSpan
from doctrine._model.skill_graph import (
    ReceiptDeclRouteField,
    ResolvedReceiptRouteField,
)


@_dataclass(slots=True, frozen=True)
class ReceiptDeclField:
    """One typed field inside a top-level `receipt` declaration."""

    key: str
    type_ref: NameRef
    list_element: bool = False
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReceiptDeclOverride:
    """Override entry inside a top-level `receipt` declaration body."""

    key: str
    type_ref: NameRef
    list_element: bool = False
    source_span: SourceSpan | None = _field(default=None, compare=False)


ReceiptDeclItem: _TypeAlias = (
    ReceiptDeclField | ReceiptDeclOverride | InheritItem | ReceiptDeclRouteField
)


@_dataclass(slots=True, frozen=True)
class ReceiptDecl:
    """A top-level reusable receipt declaration.

    Receipt declarations name a typed handoff fact that many skill packages or
    graph stages can share. They lower to a flat ordered field map where each
    field carries a type ref and an optional `list[...]` marker. Inheritance
    follows the explicit `inherit`/`override` patching model used by `output`,
    `workflow`, and `document`.
    """

    name: str
    title: str
    items: tuple[ReceiptDeclItem, ...]
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReceiptHostSlotRef:
    """Skill package host contract slot that points at a top-level receipt.

    Sits next to the inline `ReceiptHostSlot` form. A receipt-by-ref slot keeps
    the slot key local to the package while letting graph handoffs share one
    typed receipt declaration across packages.
    """

    key: str
    receipt_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def family(self) -> str:
        return "receipt"


@_dataclass(slots=True, frozen=True)
class ResolvedReceiptField:
    """One lowered field on a resolved receipt.

    `type_kind` names the resolved type family: one of `builtin`, `enum`,
    `table`, `schema`, or `receipt`. `type_name` is the dotted display name a
    consumer can use to look the type up; for builtins it is just the scalar
    keyword (`string`, `integer`, `number`, `boolean`).
    """

    key: str
    type_kind: str
    type_name: str
    list_element: bool = False
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedReceipt:
    """Top-level receipt after inheritance, override, and field-type checks.

    `fields` is the deterministic merged ordered tuple. `canonical_name` is the
    receipt declaration's canonical name from the source declaration; it stays
    fixed regardless of how a consumer authored the ref (bare name, dotted
    module path, or import alias). `module_parts` carry the resolved module
    location so consumers can disambiguate cross-module names. `routes` is the
    deterministic ordered tuple of lowered receipt route fields.
    """

    canonical_name: str
    title: str
    module_parts: tuple[str, ...]
    fields: tuple[ResolvedReceiptField, ...]
    routes: tuple[ResolvedReceiptRouteField, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedReceiptHostSlotRef:
    """Compiled form of `receipt key: ReceiptRef` after the resolver runs.

    Carries the local slot key plus the lowered receipt so emit and downstream
    consumers can read the receipt fields without re-resolving the source AST.
    `canonical_name` is the resolved receipt declaration's canonical name and
    is the value emit must use for the wire `receipt` field, so equivalent
    authored refs (bare, dotted, or aliased) lower to the same name.
    """

    key: str
    receipt: ResolvedReceipt
    receipt_ref: NameRef
    canonical_name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)

    @property
    def family(self) -> str:
        return "receipt"
