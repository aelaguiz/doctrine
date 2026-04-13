from __future__ import annotations

from dataclasses import dataclass as _dataclass
from pathlib import Path as _Path
from typing import TypeAlias as _TypeAlias

from doctrine._model.analysis import AnalysisDecl, DecisionDecl
from doctrine._model.core import ImportDecl, RenderProfileDecl
from doctrine._model.readable import DocumentDecl
from doctrine._model.review import ReviewDecl
from doctrine._model.schema import SchemaDecl
from doctrine._model.workflow import (
    Agent,
    GroundingDecl,
    InputDecl,
    InputSourceDecl,
    InputsDecl,
    JsonSchemaDecl,
    OutputDecl,
    OutputShapeDecl,
    OutputTargetDecl,
    OutputsDecl,
    RouteOnlyDecl,
    SkillDecl,
    SkillPackageDecl,
    SkillsDecl,
    WorkflowDecl,
    EnumDecl,
)


Declaration: _TypeAlias = (
    ImportDecl
    | RenderProfileDecl
    | AnalysisDecl
    | DecisionDecl
    | SchemaDecl
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
    | JsonSchemaDecl
    | SkillDecl
    | SkillPackageDecl
    | EnumDecl
)


@_dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: _Path | None = None
