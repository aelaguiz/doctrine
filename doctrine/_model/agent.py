from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import NameRef, RoleBlock, RoleScalar, SourceSpan
from doctrine._model.io import IoFieldValue
from doctrine._model.review import ReviewFieldsConfig
from doctrine._model.workflow import SkillsValue, WorkflowSlotValue


@_dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AuthoredSlotAbstract:
    key: str
    declared_type: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class InputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class OutputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AnalysisField:
    value: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class DecisionField:
    value: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReviewField:
    value: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class FinalOutputField:
    value: NameRef
    route_path: tuple[str, ...] | None = None
    review_fields: ReviewFieldsConfig | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class AgentSelectorBinding:
    selector_name: str
    enum_member_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SelectorsField:
    bindings: tuple[AgentSelectorBinding, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


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
    | SelectorsField
)


@_dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    title: str | None = None
    abstract: bool = False
    parent_ref: NameRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)
