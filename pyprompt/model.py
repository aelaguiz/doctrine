from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


@dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str


@dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ImportPath:
    level: int
    module_parts: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ImportDecl:
    path: ImportPath


@dataclass(slots=True, frozen=True)
class NameRef:
    module_parts: tuple[str, ...]
    declaration_name: str


@dataclass(slots=True, frozen=True)
class RouteLine:
    label: str
    target: NameRef


SectionBodyItem: TypeAlias = str | RouteLine


@dataclass(slots=True, frozen=True)
class LocalSection:
    key: str
    title: str
    items: tuple[SectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class WorkflowUse:
    key: str
    target: NameRef


@dataclass(slots=True, frozen=True)
class InheritItem:
    key: str


@dataclass(slots=True, frozen=True)
class OverrideSection:
    key: str
    title: str | None
    items: tuple[SectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class OverrideUse:
    key: str
    target: NameRef


WorkflowItem: TypeAlias = (
    LocalSection | WorkflowUse | InheritItem | OverrideSection | OverrideUse
)


@dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[str, ...]
    items: tuple[WorkflowItem, ...]


@dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_name: str | None = None


RecordScalarValue: TypeAlias = str | NameRef


@dataclass(slots=True, frozen=True)
class RecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["RecordItem", ...] | None = None


@dataclass(slots=True, frozen=True)
class RecordSection:
    key: str
    title: str
    items: tuple["RecordItem", ...]


@dataclass(slots=True, frozen=True)
class RecordRef:
    ref: NameRef
    body: tuple["RecordItem", ...] | None = None


RecordItem: TypeAlias = str | RecordScalar | RecordSection | RecordRef | RouteLine


WorkflowSlotValue: TypeAlias = WorkflowBody | NameRef


@dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str


@dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class InputsField:
    title: str
    refs: tuple[NameRef, ...]


@dataclass(slots=True, frozen=True)
class OutputsField:
    title: str
    refs: tuple[NameRef, ...]


@dataclass(slots=True, frozen=True)
class OutcomeField:
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class SkillsField:
    title: str
    items: tuple[RecordItem, ...]


Field: TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | OutcomeField
    | SkillsField
)


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    abstract: bool = False
    parent_name: str | None = None


@dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class InputSourceDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class OutputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class OutputTargetDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class OutputShapeDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class JsonSchemaDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class SkillDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


Declaration: TypeAlias = (
    ImportDecl
    | WorkflowDecl
    | Agent
    | InputDecl
    | InputSourceDecl
    | OutputDecl
    | OutputTargetDecl
    | OutputShapeDecl
    | JsonSchemaDecl
    | SkillDecl
)


@dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: Path | None = None
