from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import Literal as _Literal
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import NameRef, SourceSpan


@_dataclass(slots=True, frozen=True)
class AgentTagPredicate:
    tag: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class FlowPredicate:
    flow_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RoleClassPredicate:
    role_class: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class FileTreePredicate:
    glob: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


RuleScopePredicate: _TypeAlias = (
    AgentTagPredicate | FlowPredicate | RoleClassPredicate | FileTreePredicate
)


@_dataclass(slots=True, frozen=True)
class RuleScope:
    predicates: tuple[RuleScopePredicate, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RequiresInheritAssertion:
    target: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ForbidsBindAssertion:
    target: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class RequiresDeclareAssertion:
    slot_key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


RuleAssertion: _TypeAlias = (
    RequiresInheritAssertion | ForbidsBindAssertion | RequiresDeclareAssertion
)

RuleAssertionKind: _TypeAlias = _Literal[
    "requires_inherit", "forbids_bind", "requires_declare"
]


@_dataclass(slots=True, frozen=True)
class RuleDecl:
    name: str
    title: str
    scope: RuleScope
    assertions: tuple[RuleAssertion, ...]
    message: str
    source_span: SourceSpan | None = _field(default=None, compare=False)
