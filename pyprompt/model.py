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
class WorkflowTarget:
    module_parts: tuple[str, ...]
    declaration_name: str


@dataclass(slots=True, frozen=True)
class LocalSection:
    key: str
    title: str
    lines: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class WorkflowUse:
    key: str
    target: WorkflowTarget


WorkflowItem: TypeAlias = LocalSection | WorkflowUse


@dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[str, ...]
    items: tuple[WorkflowItem, ...]


@dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody


Field: TypeAlias = RoleScalar | RoleBlock | WorkflowBody


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]


Declaration: TypeAlias = ImportDecl | WorkflowDecl | Agent


@dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: Path | None = None
