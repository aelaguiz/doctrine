from __future__ import annotations

from doctrine._compiler.resolve.addressable_skills import ResolveAddressableSkillsMixin
from doctrine._compiler.resolve.addressables import ResolveAddressablesMixin
from doctrine._compiler.resolve.agent_slots import ResolveAgentSlotsMixin
from doctrine._compiler.resolve.analysis import ResolveAnalysisMixin
from doctrine._compiler.resolve.document_blocks import ResolveDocumentBlocksMixin
from doctrine._compiler.resolve.documents import ResolveDocumentsMixin
from doctrine._compiler.resolve.io_contracts import ResolveIoContractsMixin
from doctrine._compiler.resolve.law_paths import ResolveLawPathsMixin
from doctrine._compiler.resolve.output_schemas import ResolveOutputSchemasMixin
from doctrine._compiler.resolve.outputs import ResolveOutputsMixin
from doctrine._compiler.resolve.receipts import ResolveReceiptsMixin
from doctrine._compiler.resolve.refs import ResolveRefsMixin
from doctrine._compiler.resolve.reviews import ResolveReviewsMixin
from doctrine._compiler.resolve.route_semantics import ResolveRouteSemanticsMixin
from doctrine._compiler.resolve.schemas import ResolveSchemasMixin
from doctrine._compiler.resolve.section_bodies import ResolveSectionBodiesMixin
from doctrine._compiler.resolve.skill_flows import ResolveSkillFlowsMixin
from doctrine._compiler.resolve.skill_graphs import ResolveSkillGraphsMixin
from doctrine._compiler.resolve.skills import ResolveSkillsMixin
from doctrine._compiler.resolve.stages import ResolveStagesMixin
from doctrine._compiler.resolve.workflows import ResolveWorkflowsMixin


class ResolveMixin(
    ResolveSchemasMixin,
    ResolveWorkflowsMixin,
    ResolveReviewsMixin,
    ResolveOutputSchemasMixin,
    ResolveOutputsMixin,
    ResolveRefsMixin,
    ResolveRouteSemanticsMixin,
    ResolveIoContractsMixin,
    ResolveAgentSlotsMixin,
    ResolveSkillsMixin,
    ResolveAddressableSkillsMixin,
    ResolveAnalysisMixin,
    ResolveDocumentsMixin,
    ResolveDocumentBlocksMixin,
    ResolveSectionBodiesMixin,
    ResolveReceiptsMixin,
    ResolveStagesMixin,
    ResolveSkillFlowsMixin,
    ResolveSkillGraphsMixin,
    ResolveAddressablesMixin,
    ResolveLawPathsMixin,
):
    """Resolution helper boundary for CompilationContext."""
