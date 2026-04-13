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
class ExprRef:
    parts: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ExprCall:
    name: str
    args: tuple["Expr", ...]


@dataclass(slots=True, frozen=True)
class ExprSet:
    items: tuple["Expr", ...]


@dataclass(slots=True, frozen=True)
class ExprBinary:
    op: str
    left: "Expr"
    right: "Expr"


Expr: TypeAlias = ExprRef | ExprCall | ExprSet | ExprBinary | str | int | bool


@dataclass(slots=True, frozen=True)
class RenderProfileRule:
    target_parts: tuple[str, ...]
    mode: str


@dataclass(slots=True, frozen=True)
class RenderProfileDecl:
    name: str
    rules: tuple[RenderProfileRule, ...] = ()


@dataclass(slots=True, frozen=True)
class LawPath:
    parts: tuple[str, ...]
    wildcard: bool = False


@dataclass(slots=True, frozen=True)
class LawPathSet:
    paths: tuple[LawPath, ...]
    except_paths: tuple[LawPath, ...] = ()


@dataclass(slots=True, frozen=True)
class TrustSurfaceItem:
    path: tuple[str, ...]
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ActiveWhenStmt:
    expr: Expr


@dataclass(slots=True, frozen=True)
class ModeStmt:
    name: str
    expr: Expr
    enum_ref: NameRef


@dataclass(slots=True, frozen=True)
class MustStmt:
    expr: Expr


@dataclass(slots=True, frozen=True)
class CurrentArtifactStmt:
    target: LawPath
    carrier: LawPath


@dataclass(slots=True, frozen=True)
class CurrentNoneStmt:
    pass


@dataclass(slots=True, frozen=True)
class OwnOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class PreserveStmt:
    kind: str
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class SupportOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class IgnoreStmt:
    target: LawPathSet
    bases: tuple[str, ...]
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class InvalidateStmt:
    target: LawPath
    carrier: LawPath
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ForbidStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class WhenStmt:
    expr: Expr
    items: tuple["LawStmt", ...]


@dataclass(slots=True, frozen=True)
class MatchArm:
    head: Expr | None
    items: tuple["LawStmt", ...]
    display_label: str | None = None


@dataclass(slots=True, frozen=True)
class MatchStmt:
    expr: Expr
    cases: tuple[MatchArm, ...]


@dataclass(slots=True, frozen=True)
class StopStmt:
    message: str | None = None
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class LawRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None


LawStmt: TypeAlias = (
    ActiveWhenStmt
    | ModeStmt
    | MustStmt
    | CurrentArtifactStmt
    | CurrentNoneStmt
    | OwnOnlyStmt
    | PreserveStmt
    | SupportOnlyStmt
    | IgnoreStmt
    | InvalidateStmt
    | ForbidStmt
    | WhenStmt
    | MatchStmt
    | StopStmt
    | LawRouteStmt
)


@dataclass(slots=True, frozen=True)
class LawSection:
    key: str
    items: tuple[LawStmt, ...]


@dataclass(slots=True, frozen=True)
class LawInherit:
    key: str


@dataclass(slots=True, frozen=True)
class LawOverrideSection:
    key: str
    items: tuple[LawStmt, ...]


LawTopLevelItem: TypeAlias = LawStmt | LawSection | LawInherit | LawOverrideSection


@dataclass(slots=True, frozen=True)
class LawBody:
    items: tuple[LawTopLevelItem, ...]


@dataclass(slots=True, frozen=True)
class AddressableRef:
    root: NameRef
    path: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class RouteLine:
    label: str
    target: NameRef


@dataclass(slots=True, frozen=True)
class SectionBodyRef:
    ref: AddressableRef


ReadableRequirement: TypeAlias = str


@dataclass(slots=True, frozen=True)
class ReadableListItem:
    key: str | None
    text: ProseLine


@dataclass(slots=True, frozen=True)
class ReadableDefinitionItem:
    key: str
    title: str
    body: tuple[ProseLine, ...]


@dataclass(slots=True, frozen=True)
class ReadablePropertyItem:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@dataclass(slots=True, frozen=True)
class ReadablePropertiesData:
    entries: tuple[ReadablePropertyItem, ...]


@dataclass(slots=True, frozen=True)
class ReadableSchemaEntry:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@dataclass(slots=True, frozen=True)
class ReadableInlineSchemaData:
    entries: tuple[ReadableSchemaEntry, ...]


@dataclass(slots=True, frozen=True)
class ReadableTableCell:
    key: str
    text: str | None = None
    body: tuple["ReadableSectionBodyItem", ...] | None = None


@dataclass(slots=True, frozen=True)
class ReadableTableColumn:
    key: str
    title: str
    body: tuple[ProseLine, ...]


@dataclass(slots=True, frozen=True)
class ReadableTableRow:
    key: str
    cells: tuple[ReadableTableCell, ...]


@dataclass(slots=True, frozen=True)
class ReadableTableData:
    columns: tuple[ReadableTableColumn, ...]
    rows: tuple[ReadableTableRow, ...] = ()
    notes: tuple[ProseLine, ...] = ()
    row_schema: ReadableInlineSchemaData | None = None


@dataclass(slots=True, frozen=True)
class ReadableCalloutData:
    kind: str | None
    body: tuple[ProseLine, ...]


@dataclass(slots=True, frozen=True)
class ReadableCodeData:
    language: str | None
    text: str


@dataclass(slots=True, frozen=True)
class ReadableRawTextData:
    text: str


@dataclass(slots=True, frozen=True)
class ReadableFootnoteItem:
    key: str
    text: ProseLine


@dataclass(slots=True, frozen=True)
class ReadableFootnotesData:
    entries: tuple[ReadableFootnoteItem, ...]


@dataclass(slots=True, frozen=True)
class ReadableImageData:
    src: str
    alt: str
    caption: str | None = None


ReadableSectionBodyItem: TypeAlias = ProseLine | "ReadableBlock"
ReadablePayload: TypeAlias = (
    tuple[ReadableSectionBodyItem, ...]
    | tuple[ReadableListItem, ...]
    | tuple[ReadableDefinitionItem, ...]
    | ReadablePropertiesData
    | ReadableTableData
    | ReadableCalloutData
    | ReadableCodeData
    | ReadableRawTextData
    | ReadableFootnotesData
    | ReadableImageData
    | None
)


@dataclass(slots=True, frozen=True)
class ReadableBlock:
    kind: str
    key: str
    title: str | None
    payload: ReadablePayload
    requirement: ReadableRequirement | None = None
    when_expr: Expr | None = None
    item_schema: ReadableInlineSchemaData | None = None
    row_schema: ReadableInlineSchemaData | None = None
    anonymous: bool = False
    legacy_section: bool = False


SectionBodyItem: TypeAlias = ProseLine | RouteLine | SectionBodyRef | "LocalSection" | ReadableBlock


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


RecordScalarValue: TypeAlias = str | NameRef | AddressableRef


@dataclass(slots=True, frozen=True)
class RecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["AnyRecordItem", ...] | None = None


@dataclass(slots=True, frozen=True)
class RecordSection:
    key: str
    title: str
    items: tuple["AnyRecordItem", ...]


@dataclass(slots=True, frozen=True)
class GuardedOutputSection:
    key: str
    title: str
    when_expr: Expr
    items: tuple["AnyRecordItem", ...]


@dataclass(slots=True, frozen=True)
class GuardedOutputScalar:
    key: str
    value: RecordScalarValue
    when_expr: Expr
    body: tuple["AnyRecordItem", ...] | None = None


@dataclass(slots=True, frozen=True)
class RecordRef:
    ref: NameRef
    body: tuple["AnyRecordItem", ...] | None = None


RecordItem: TypeAlias = ProseLine | RecordScalar | RecordSection | RecordRef | ReadableBlock
AnyRecordItem: TypeAlias = RecordItem | GuardedOutputSection | GuardedOutputScalar
OutputRecordItem: TypeAlias = RecordItem | GuardedOutputSection | GuardedOutputScalar


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
    law: LawBody | None = None


@dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class RouteOnlyGuard:
    key: str
    expr: Expr


@dataclass(slots=True, frozen=True)
class RouteOnlyRoute:
    key: str | None
    target: NameRef


@dataclass(slots=True, frozen=True)
class RouteOnlyBody:
    title: str
    facts_ref: NameRef | None = None
    when_exprs: tuple[Expr, ...] = ()
    current_none: bool = False
    handoff_output_ref: NameRef | None = None
    guarded: tuple[RouteOnlyGuard, ...] = ()
    routes: tuple[RouteOnlyRoute, ...] = ()


@dataclass(slots=True, frozen=True)
class RouteOnlyDecl:
    name: str
    body: RouteOnlyBody


@dataclass(slots=True, frozen=True)
class GroundingPolicyStartFrom:
    source: str
    unless: str | None = None


@dataclass(slots=True, frozen=True)
class GroundingPolicyForbid:
    value: str


@dataclass(slots=True, frozen=True)
class GroundingPolicyAllow:
    value: str


@dataclass(slots=True, frozen=True)
class GroundingPolicyRoute:
    condition: str
    target: NameRef


GroundingPolicyItem: TypeAlias = (
    GroundingPolicyStartFrom
    | GroundingPolicyForbid
    | GroundingPolicyAllow
    | GroundingPolicyRoute
)


@dataclass(slots=True, frozen=True)
class GroundingBody:
    title: str
    source_ref: NameRef | None = None
    target: str | None = None
    policy_items: tuple[GroundingPolicyItem, ...] = ()


@dataclass(slots=True, frozen=True)
class GroundingDecl:
    name: str
    body: GroundingBody


@dataclass(slots=True, frozen=True)
class SkillsDecl:
    name: str
    body: SkillsBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class ProveStmt:
    target_title: str
    basis: LawPathSet


@dataclass(slots=True, frozen=True)
class DeriveStmt:
    target_title: str
    basis: LawPathSet


@dataclass(slots=True, frozen=True)
class ClassifyStmt:
    target_title: str
    enum_ref: NameRef


@dataclass(slots=True, frozen=True)
class CompareStmt:
    target_title: str
    basis: LawPathSet
    using_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class DefendStmt:
    target_title: str
    basis: LawPathSet


AnalysisSectionItem: TypeAlias = (
    ProseLine
    | SectionBodyRef
    | ProveStmt
    | DeriveStmt
    | ClassifyStmt
    | CompareStmt
    | DefendStmt
)


@dataclass(slots=True, frozen=True)
class AnalysisSection:
    key: str
    title: str
    items: tuple[AnalysisSectionItem, ...]


@dataclass(slots=True, frozen=True)
class AnalysisOverrideSection:
    key: str
    title: str | None
    items: tuple[AnalysisSectionItem, ...]


AnalysisItem: TypeAlias = AnalysisSection | InheritItem | AnalysisOverrideSection


@dataclass(slots=True, frozen=True)
class AnalysisBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[AnalysisItem, ...]


@dataclass(slots=True, frozen=True)
class AnalysisDecl:
    name: str
    body: AnalysisBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title


@dataclass(slots=True, frozen=True)
class DecisionMinimumCandidates:
    count: int


@dataclass(slots=True, frozen=True)
class DecisionRequiredItem:
    key: str


@dataclass(slots=True, frozen=True)
class DecisionChooseWinner:
    pass


@dataclass(slots=True, frozen=True)
class DecisionRankBy:
    dimensions: tuple[str, ...]


DecisionItem: TypeAlias = (
    DecisionMinimumCandidates | DecisionRequiredItem | DecisionChooseWinner | DecisionRankBy
)


@dataclass(slots=True, frozen=True)
class DecisionBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[DecisionItem, ...]


@dataclass(slots=True, frozen=True)
class DecisionDecl:
    name: str
    body: DecisionBody
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title


@dataclass(slots=True, frozen=True)
class SchemaSection:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@dataclass(slots=True, frozen=True)
class SchemaGate:
    key: str
    title: str
    body: tuple[ProseLine, ...] = ()


@dataclass(slots=True, frozen=True)
class SchemaArtifact:
    key: str
    title: str
    ref: NameRef


@dataclass(slots=True, frozen=True)
class SchemaGroup:
    key: str
    title: str
    members: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class SchemaSectionsBlock:
    items: tuple[SchemaSection, ...]


@dataclass(slots=True, frozen=True)
class SchemaGatesBlock:
    items: tuple[SchemaGate, ...]


@dataclass(slots=True, frozen=True)
class SchemaArtifactsBlock:
    items: tuple[SchemaArtifact, ...]


@dataclass(slots=True, frozen=True)
class SchemaGroupsBlock:
    items: tuple[SchemaGroup, ...]


@dataclass(slots=True, frozen=True)
class SchemaOverrideSectionsBlock:
    items: tuple[SchemaSection, ...]


@dataclass(slots=True, frozen=True)
class SchemaOverrideGatesBlock:
    items: tuple[SchemaGate, ...]


@dataclass(slots=True, frozen=True)
class SchemaOverrideArtifactsBlock:
    items: tuple[SchemaArtifact, ...]


@dataclass(slots=True, frozen=True)
class SchemaOverrideGroupsBlock:
    items: tuple[SchemaGroup, ...]


SchemaItem: TypeAlias = (
    SchemaSectionsBlock
    | SchemaGatesBlock
    | SchemaArtifactsBlock
    | SchemaGroupsBlock
    | InheritItem
    | SchemaOverrideSectionsBlock
    | SchemaOverrideGatesBlock
    | SchemaOverrideArtifactsBlock
    | SchemaOverrideGroupsBlock
)


@dataclass(slots=True, frozen=True)
class SchemaBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SchemaItem, ...]


@dataclass(slots=True, frozen=True)
class SchemaDecl:
    name: str
    body: SchemaBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title


@dataclass(slots=True, frozen=True)
class ReadableOverrideBlock:
    kind: str
    key: str
    title: str | None
    payload: ReadablePayload
    requirement: ReadableRequirement | None = None
    when_expr: Expr | None = None
    item_schema: ReadableInlineSchemaData | None = None
    row_schema: ReadableInlineSchemaData | None = None
    anonymous: bool = False


DocumentBlock = ReadableBlock
DocumentOverrideBlock = ReadableOverrideBlock
DocumentItem: TypeAlias = ProseLine | ReadableBlock | InheritItem | ReadableOverrideBlock


@dataclass(slots=True, frozen=True)
class DocumentBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[DocumentItem, ...]


@dataclass(slots=True, frozen=True)
class DocumentDecl:
    name: str
    body: DocumentBody
    parent_ref: NameRef | None = None
    render_profile_ref: NameRef | None = None

    @property
    def title(self) -> str:
        return self.body.title


@dataclass(slots=True, frozen=True)
class ReviewSubjectConfig:
    subjects: tuple[NameRef, ...]


@dataclass(slots=True, frozen=True)
class ReviewSubjectMapEntry:
    enum_member_ref: NameRef
    artifact_ref: NameRef


@dataclass(slots=True, frozen=True)
class ReviewSubjectMapConfig:
    entries: tuple[ReviewSubjectMapEntry, ...]


@dataclass(slots=True, frozen=True)
class ReviewContractRef:
    ref: NameRef


@dataclass(slots=True, frozen=True)
class ReviewContractConfig:
    contract: ReviewContractRef

    @property
    def contract_ref(self) -> NameRef:
        return self.contract.ref


@dataclass(slots=True, frozen=True)
class ReviewCommentOutputConfig:
    output_ref: NameRef


@dataclass(slots=True, frozen=True)
class ReviewFieldBinding:
    semantic_field: str
    field_path: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ReviewFieldsConfig:
    bindings: tuple[ReviewFieldBinding, ...]


@dataclass(slots=True, frozen=True)
class ReviewSelectorConfig:
    field_name: str
    expr: Expr
    enum_ref: NameRef


@dataclass(slots=True, frozen=True)
class ContractGateRef:
    key: str


@dataclass(slots=True, frozen=True)
class SectionGateRef:
    key: str


ReviewGateLabel: TypeAlias = str | ContractGateRef | SectionGateRef


@dataclass(slots=True, frozen=True)
class ReviewBlockStmt:
    gate: ReviewGateLabel
    expr: Expr


@dataclass(slots=True, frozen=True)
class ReviewRejectStmt:
    gate: ReviewGateLabel
    expr: Expr


@dataclass(slots=True, frozen=True)
class ReviewAcceptStmt:
    gate: ReviewGateLabel
    expr: Expr


@dataclass(slots=True, frozen=True)
class ReviewOutputFieldRef:
    parts: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ReviewCurrentArtifactStmt:
    artifact_ref: NameRef
    carrier: ReviewOutputFieldRef
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ReviewCurrentNoneStmt:
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ReviewCarryStmt:
    field_name: str
    expr: Expr


@dataclass(slots=True, frozen=True)
class ReviewOutcomeRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ReviewMatchHead:
    options: tuple[Expr, ...]
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ReviewPreOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewPreOutcomeStmt", ...]


@dataclass(slots=True, frozen=True)
class ReviewOutcomeWhenStmt:
    expr: Expr
    items: tuple["ReviewOutcomeStmt", ...]


@dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewPreOutcomeStmt", ...]


@dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchArm:
    head: ReviewMatchHead | None
    items: tuple["ReviewOutcomeStmt", ...]


@dataclass(slots=True, frozen=True)
class ReviewPreOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewPreOutcomeMatchArm, ...]


@dataclass(slots=True, frozen=True)
class ReviewOutcomeMatchStmt:
    expr: Expr
    cases: tuple[ReviewOutcomeMatchArm, ...]


ReviewPreOutcomeStmt: TypeAlias = (
    ReviewBlockStmt
    | ReviewRejectStmt
    | ReviewAcceptStmt
    | PreserveStmt
    | SupportOnlyStmt
    | IgnoreStmt
    | ReviewPreOutcomeWhenStmt
    | ReviewPreOutcomeMatchStmt
    | ProseLine
)


ReviewOutcomeStmt: TypeAlias = (
    ReviewCurrentArtifactStmt
    | ReviewCurrentNoneStmt
    | ReviewCarryStmt
    | ReviewOutcomeRouteStmt
    | ReviewOutcomeWhenStmt
    | ReviewOutcomeMatchStmt
    | ProseLine
)


@dataclass(slots=True, frozen=True)
class ReviewSection:
    key: str
    title: str | None
    items: tuple[ReviewPreOutcomeStmt, ...]


@dataclass(slots=True, frozen=True)
class ReviewOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]


@dataclass(slots=True, frozen=True)
class ReviewOverrideFields:
    bindings: tuple[ReviewFieldBinding, ...]


@dataclass(slots=True, frozen=True)
class ReviewOverrideSection:
    key: str
    title: str | None
    items: tuple[ReviewPreOutcomeStmt, ...]


@dataclass(slots=True, frozen=True)
class ReviewOverrideOutcomeSection:
    key: str
    title: str | None
    items: tuple[ReviewOutcomeStmt, ...]


@dataclass(slots=True, frozen=True)
class ReviewCase:
    key: str
    title: str
    head: ReviewMatchHead
    subject: ReviewSubjectConfig
    contract: ReviewContractConfig
    checks: tuple[ReviewPreOutcomeStmt, ...]
    on_accept: ReviewOutcomeSection
    on_reject: ReviewOutcomeSection


@dataclass(slots=True, frozen=True)
class ReviewCasesConfig:
    cases: tuple[ReviewCase, ...]


ReviewItem: TypeAlias = (
    ReviewSubjectConfig
    | ReviewSubjectMapConfig
    | ReviewContractConfig
    | ReviewCommentOutputConfig
    | ReviewFieldsConfig
    | ReviewSelectorConfig
    | ReviewCasesConfig
    | ReviewSection
    | ReviewOutcomeSection
    | InheritItem
    | ReviewOverrideFields
    | ReviewOverrideSection
    | ReviewOverrideOutcomeSection
)


@dataclass(slots=True, frozen=True)
class ReviewBody:
    title: str
    items: tuple[ReviewItem, ...]


@dataclass(slots=True, frozen=True)
class ReviewDecl:
    name: str
    body: ReviewBody
    abstract: bool = False
    parent_ref: NameRef | None = None
    family: bool = False


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
class AnalysisField:
    value: NameRef


@dataclass(slots=True, frozen=True)
class DecisionField:
    value: NameRef


@dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue


@dataclass(slots=True, frozen=True)
class ReviewField:
    value: NameRef


@dataclass(slots=True, frozen=True)
class FinalOutputField:
    value: NameRef


Field: TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotAbstract
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | AnalysisField
    | DecisionField
    | SkillsField
    | ReviewField
    | FinalOutputField
)


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    title: str | None = None
    abstract: bool = False
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class InputStructureConfig:
    structure_ref: NameRef


@dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    structure: InputStructureConfig | None = None

    @property
    def structure_ref(self) -> NameRef | None:
        return None if self.structure is None else self.structure.structure_ref


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
class OutputSchemaConfig:
    schema_ref: NameRef


@dataclass(slots=True, frozen=True)
class OutputStructureConfig:
    structure_ref: NameRef


@dataclass(slots=True, frozen=True)
class OutputDecl:
    name: str
    title: str
    items: tuple[OutputRecordItem, ...]
    schema: OutputSchemaConfig | None = None
    structure: OutputStructureConfig | None = None
    render_profile_ref: NameRef | None = None
    trust_surface: tuple[TrustSurfaceItem, ...] = ()

    @property
    def schema_ref(self) -> NameRef | None:
        return None if self.schema is None else self.schema.schema_ref

    @property
    def structure_ref(self) -> NameRef | None:
        return None if self.structure is None else self.structure.structure_ref


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


@dataclass(slots=True, frozen=True)
class EnumMember:
    key: str
    title: str
    wire: str | None = None

    @property
    def value(self) -> str:
        return self.wire if self.wire is not None else self.title


@dataclass(slots=True, frozen=True)
class EnumDecl:
    name: str
    title: str
    members: tuple[EnumMember, ...]


Declaration: TypeAlias = (
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
    | EnumDecl
)


@dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: Path | None = None
