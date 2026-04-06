from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str


@dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class Workflow:
    title: str
    lines: tuple[str, ...]


Field: TypeAlias = RoleScalar | RoleBlock | Workflow


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]


@dataclass(slots=True, frozen=True)
class PromptFile:
    agents: tuple[Agent, ...]
