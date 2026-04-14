from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import InheritItem, NameRef, ProseLine


@_dataclass(slots=True, frozen=True)
class SchemaSection:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@_dataclass(slots=True, frozen=True)
class SchemaGate:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@_dataclass(slots=True, frozen=True)
class SchemaArtifact:
    key: str
    title: str
    ref: NameRef


@_dataclass(slots=True, frozen=True)
class SchemaGroup:
    key: str
    title: str
    members: tuple[str, ...] = ()


@_dataclass(slots=True, frozen=True)
class SchemaSectionsBlock:
    items: tuple[SchemaSection, ...]


@_dataclass(slots=True, frozen=True)
class SchemaGatesBlock:
    items: tuple[SchemaGate, ...]


@_dataclass(slots=True, frozen=True)
class SchemaArtifactsBlock:
    items: tuple[SchemaArtifact, ...]


@_dataclass(slots=True, frozen=True)
class SchemaGroupsBlock:
    items: tuple[SchemaGroup, ...]


@_dataclass(slots=True, frozen=True)
class SchemaOverrideSectionsBlock:
    items: tuple[SchemaSection, ...]


@_dataclass(slots=True, frozen=True)
class SchemaOverrideGatesBlock:
    items: tuple[SchemaGate, ...]


@_dataclass(slots=True, frozen=True)
class SchemaOverrideArtifactsBlock:
    items: tuple[SchemaArtifact, ...]


@_dataclass(slots=True, frozen=True)
class SchemaOverrideGroupsBlock:
    items: tuple[SchemaGroup, ...]


SchemaItem: _TypeAlias = (
    SchemaSectionsBlock
    | SchemaGatesBlock
    | SchemaArtifactsBlock
    | SchemaGroupsBlock
    | InheritItem
    | SchemaOverrideSectionsBlock
    | SchemaOverrideGatesBlock
    | SchemaOverrideArtifactsBlock
    | SchemaOverrideGroupsBlock
)


@_dataclass(slots=True, frozen=True)
class SchemaBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SchemaItem, ...]


@_dataclass(slots=True, frozen=True)
class SchemaDecl:
    name: str
    body: SchemaBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title
