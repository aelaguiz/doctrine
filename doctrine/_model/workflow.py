from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import (
    Expr,
    InheritItem,
    NameRef,
    ProseLine,
    RouteLine,
    SectionBodyRef,
)
from doctrine._model.io import RecordItem
from doctrine._model.law import LawBody
from doctrine._model.readable import ReadableBlock
from doctrine._model.readable import ReadableOverrideBlock


SectionBodyItem: _TypeAlias = ProseLine | RouteLine | SectionBodyRef | "LocalSection" | ReadableBlock


@_dataclass(slots=True, frozen=True)
class LocalSection:
    key: str
    title: str
    items: tuple[SectionBodyItem, ...]


@_dataclass(slots=True, frozen=True)
class WorkflowUse:
    key: str
    target: NameRef


@_dataclass(slots=True, frozen=True)
class OverrideSection:
    key: str
    title: str | None
    items: tuple[SectionBodyItem, ...]


@_dataclass(slots=True, frozen=True)
class OverrideUse:
    key: str
    target: NameRef


@_dataclass(slots=True, frozen=True)
class SkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


SkillsSectionItem: _TypeAlias = ProseLine | SkillEntry


@_dataclass(slots=True, frozen=True)
class SkillsSection:
    key: str
    title: str
    items: tuple[SkillsSectionItem, ...]


@_dataclass(slots=True, frozen=True)
class OverrideSkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


@_dataclass(slots=True, frozen=True)
class OverrideSkillsSection:
    key: str
    title: str | None
    items: tuple[SkillsSectionItem, ...]


SkillsItem: _TypeAlias = (
    SkillsSection | SkillEntry | InheritItem | OverrideSkillsSection | OverrideSkillEntry
)


@_dataclass(slots=True, frozen=True)
class SkillsBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SkillsItem, ...]


SkillsValue: _TypeAlias = SkillsBody | NameRef


@_dataclass(slots=True, frozen=True)
class WorkflowSkillsItem:
    key: str
    value: SkillsValue


@_dataclass(slots=True, frozen=True)
class OverrideWorkflowSkillsItem:
    key: str
    value: SkillsValue


WorkflowItem: _TypeAlias = (
    LocalSection
    | ReadableBlock
    | WorkflowUse
    | InheritItem
    | ReadableOverrideBlock
    | OverrideSection
    | OverrideUse
    | WorkflowSkillsItem
    | OverrideWorkflowSkillsItem
)


@_dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[WorkflowItem, ...]
    law: LawBody | None = None


@_dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class RouteOnlyGuard:
    key: str
    expr: Expr


@_dataclass(slots=True, frozen=True)
class RouteOnlyRoute:
    key: str | None
    target: NameRef


@_dataclass(slots=True, frozen=True)
class RouteOnlyBody:
    title: str
    facts_ref: NameRef | None = None
    when_exprs: tuple[Expr, ...] = ()
    current_none: bool = False
    handoff_output_ref: NameRef | None = None
    guarded: tuple[RouteOnlyGuard, ...] = ()
    routes: tuple[RouteOnlyRoute, ...] = ()


@_dataclass(slots=True, frozen=True)
class RouteOnlyDecl:
    name: str
    body: RouteOnlyBody


@_dataclass(slots=True, frozen=True)
class GroundingPolicyStartFrom:
    source: str
    unless: str | None = None


@_dataclass(slots=True, frozen=True)
class GroundingPolicyForbid:
    value: str


@_dataclass(slots=True, frozen=True)
class GroundingPolicyAllow:
    value: str


@_dataclass(slots=True, frozen=True)
class GroundingPolicyRoute:
    condition: str
    target: NameRef


GroundingPolicyItem: _TypeAlias = (
    GroundingPolicyStartFrom
    | GroundingPolicyForbid
    | GroundingPolicyAllow
    | GroundingPolicyRoute
)


@_dataclass(slots=True, frozen=True)
class GroundingBody:
    title: str
    source_ref: NameRef | None = None
    target: str | None = None
    policy_items: tuple[GroundingPolicyItem, ...] = ()


@_dataclass(slots=True, frozen=True)
class GroundingDecl:
    name: str
    body: GroundingBody


@_dataclass(slots=True, frozen=True)
class SkillsDecl:
    name: str
    body: SkillsBody
    parent_ref: NameRef | None = None


WorkflowSlotValue: _TypeAlias = WorkflowBody | NameRef
