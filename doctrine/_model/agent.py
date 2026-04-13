from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import NameRef, RoleBlock, RoleScalar
from doctrine._model.io import IoFieldValue
from doctrine._model.workflow import SkillsValue, WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class AuthoredSlotAbstract:
    key: str


@_dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str


@_dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class InputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class OutputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@_dataclass(slots=True, frozen=True)
class AnalysisField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class DecisionField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue


@_dataclass(slots=True, frozen=True)
class ReviewField:
    value: NameRef


@_dataclass(slots=True, frozen=True)
class FinalOutputField:
    value: NameRef


Field: _TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotAbstract
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | AnalysisField
    | DecisionField
    | SkillsField
    | ReviewField
    | FinalOutputField
)


@_dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    title: str | None = None
    abstract: bool = False
    parent_ref: NameRef | None = None
