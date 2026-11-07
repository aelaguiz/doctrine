from __future__ import annotations

from dataclasses import dataclass as _dataclass, field as _field
from pathlib import Path as _Path
from typing import TypeAlias as _TypeAlias

from doctrine._model.agent import Agent, Team
from doctrine._model.analysis import AnalysisDecl, DecisionDecl
from doctrine._model.core import ImportDecl, NameRef, RenderProfileDecl, SourceSpan
from doctrine._model.io import (
    EnumDecl,
    InputDecl,
    InputSourceDecl,
    InputsDecl,
    OutputDecl,
    OutputSchemaDecl,
    OutputShapeDecl,
    OutputTargetDecl,
    OutputsDecl,
    SkillDecl,
    SkillPackageDecl,
)
from doctrine._model.readable import DocumentDecl, TableDecl
from doctrine._model.receipts import ReceiptDecl
from doctrine._model.review import ReviewDecl
from doctrine._model.rule import RuleDecl
from doctrine._model.schema import SchemaDecl
from doctrine._model.skill_graph import ArtifactDecl, SkillFlowDecl, SkillGraphDecl, StageDecl
from doctrine._model.workflow import (
    GroundingDecl,
    RouteOnlyDecl,
    SkillsDecl,
    WorkflowDecl,
)


@_dataclass(slots=True, frozen=True)
class Person:
    name: str
    title: str
    owns: tuple[NameRef | str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class Quote:
    name: str
    title: str
    fields: tuple[tuple[str, object], ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


Declaration: _TypeAlias = (
    Quote
    | Person
    | ImportDecl
    | RenderProfileDecl
    | AnalysisDecl
    | DecisionDecl
    | SchemaDecl
    | TableDecl
    | DocumentDecl
    | WorkflowDecl
    | RouteOnlyDecl
    | GroundingDecl
    | ReviewDecl
    | SkillsDecl
    | Agent
    | InputsDecl
    | InputDecl
    | InputSourceDecl
    | OutputsDecl
    | OutputDecl
    | OutputTargetDecl
    | OutputShapeDecl
    | OutputSchemaDecl
    | SkillDecl
    | SkillPackageDecl
    | ArtifactDecl
    | ReceiptDecl
    | StageDecl
    | SkillFlowDecl
    | SkillGraphDecl
    | EnumDecl
    | RuleDecl
)


@_dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    exported_names: tuple[str, ...] = ()
    source_path: _Path | None = None
