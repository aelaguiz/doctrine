from __future__ import annotations

from doctrine._compiler.compile.agent import CompileAgentMixin
from doctrine._compiler.compile.final_output import CompileFinalOutputMixin
from doctrine._compiler.compile.outputs import CompileOutputsMixin
from doctrine._compiler.compile.readable_blocks import CompileReadableBlocksMixin
from doctrine._compiler.compile.readables import CompileReadablesMixin
from doctrine._compiler.compile.records import CompileRecordsMixin
from doctrine._compiler.compile.review_cases import CompileReviewCasesMixin
from doctrine._compiler.compile.review_contract import CompileReviewContractMixin
from doctrine._compiler.compile.reviews import CompileReviewsMixin
from doctrine._compiler.compile.skill_package import CompileSkillPackageMixin
from doctrine._compiler.compile.workflows import CompileWorkflowsMixin


class CompileMixin(
    CompileWorkflowsMixin,
    CompileReviewCasesMixin,
    CompileReviewContractMixin,
    CompileReviewsMixin,
    CompileRecordsMixin,
    CompileOutputsMixin,
    CompileReadableBlocksMixin,
    CompileAgentMixin,
    CompileReadablesMixin,
    CompileFinalOutputMixin,
    CompileSkillPackageMixin,
):
    """Compile helper boundary for CompilationContext."""
