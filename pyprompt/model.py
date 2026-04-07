from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


@dataclass(slots=True, frozen=True)
class EmphasizedLine:
    kind: str
    text: str


ProseLine: TypeAlias = str | EmphasizedLine


@dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str


@dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[ProseLine, ...]


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


@dataclass(slots=True, frozen=True)
class SectionBodyRef:
    ref: NameRef


SectionBodyItem: TypeAlias = ProseLine | RouteLine | SectionBodyRef


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


RecordItem: TypeAlias = ProseLine | RecordScalar | RecordSection | RecordRef


@dataclass(slots=True, frozen=True)
class SkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


SkillsSectionItem: TypeAlias = ProseLine | SkillEntry


@dataclass(slots=True, frozen=True)
class SkillsSection:
    key: str
    title: str
    items: tuple[SkillsSectionItem, ...]


@dataclass(slots=True, frozen=True)
class OverrideSkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


@dataclass(slots=True, frozen=True)
class OverrideSkillsSection:
    key: str
    title: str | None
    items: tuple[SkillsSectionItem, ...]


SkillsItem: TypeAlias = (
    SkillsSection | SkillEntry | InheritItem | OverrideSkillsSection | OverrideSkillEntry
)


@dataclass(slots=True, frozen=True)
class SkillsBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SkillsItem, ...]


SkillsValue: TypeAlias = SkillsBody | NameRef


@dataclass(slots=True, frozen=True)
class OverrideIoSection:
    key: str
    title: str | None
    items: tuple[RecordItem, ...]


IoItem: TypeAlias = RecordSection | RecordRef | InheritItem | OverrideIoSection


@dataclass(slots=True, frozen=True)
class IoBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[IoItem, ...]


IoFieldValue: TypeAlias = tuple[RecordItem, ...] | NameRef | IoBody


@dataclass(slots=True, frozen=True)
class WorkflowSkillsItem:
    key: str
    value: SkillsValue


@dataclass(slots=True, frozen=True)
class OverrideWorkflowSkillsItem:
    key: str
    value: SkillsValue


WorkflowItem: TypeAlias = (
    LocalSection
    | WorkflowUse
    | InheritItem
    | OverrideSection
    | OverrideUse
    | WorkflowSkillsItem
    | OverrideWorkflowSkillsItem
)


@dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[WorkflowItem, ...]


@dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class SkillsDecl:
    name: str
    body: SkillsBody
    parent_ref: NameRef | None = None


WorkflowSlotValue: TypeAlias = WorkflowBody | NameRef


@dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class AuthoredSlotAbstract:
    key: str


@dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str


@dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class InputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class OutputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue


Field: TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotAbstract
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | SkillsField
)


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    abstract: bool = False
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class InputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


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
class OutputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


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
    | SkillsDecl
    | Agent
    | InputsDecl
    | InputDecl
    | InputSourceDecl
    | OutputsDecl
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
