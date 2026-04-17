from __future__ import annotations

from dataclasses import dataclass as _dataclass
from pathlib import Path as _Path
from typing import TypeAlias as _TypeAlias

from doctrine._model.agent import Agent
from doctrine._model.analysis import AnalysisDecl, DecisionDecl
from doctrine._model.core import ImportDecl, RenderProfileDecl
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
from doctrine._model.review import ReviewDecl
from doctrine._model.schema import SchemaDecl
from doctrine._model.workflow import (
    GroundingDecl,
    RouteOnlyDecl,
    SkillsDecl,
    WorkflowDecl,
)


Declaration: _TypeAlias = (
    ImportDecl
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
    | EnumDecl
)


@_dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: _Path | None = None
