from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import TypeAlias as _TypeAlias

from doctrine._model.core import NameRef, SourceSpan


@_dataclass(slots=True, frozen=True)
class StageOwnerItem:
    """Raw `owner: SkillRef` line on a top-level `stage` declaration."""

    owner_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageLaneItem:
    """Raw `lane: EnumRef.member` line on a top-level `stage` declaration."""

    lane_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageSupportsItem:
    """Raw `supports:` block on a top-level `stage` declaration.

    Each ref must resolve to a top-level `skill`. The resolver fails loud on
    duplicate supports or a support that repeats the stage owner.
    """

    skill_refs: tuple[NameRef, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageAppliesToItem:
    """Raw `applies_to:` block on a top-level `stage` declaration.

    Sub-plan 2 only validates that each listed ref resolves to a top-level
    `skill_flow` and that the resolved flow does not repeat. Reachability and
    closure checks wait for real `skill_flow` expansion in a later slice.
    """

    flow_refs: tuple[NameRef, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageInputEntry:
    """One `<key>: <Ref>` row inside a stage `inputs:` block."""

    key: str
    type_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageInputsItem:
    """Raw `inputs:` block on a top-level `stage` declaration."""

    entries: tuple[StageInputEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageEmitsItem:
    """Raw `emits: ReceiptRef` line on a top-level `stage` declaration."""

    receipt_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageArtifactsItem:
    """Raw `artifacts:` block on a top-level `stage` declaration."""

    artifact_refs: tuple[NameRef, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageScalarItem:
    """A typed scalar field on a top-level `stage` declaration.

    Covers `id`, `intent`, `durable_target`, `durable_evidence`,
    `advance_condition`, `risk_guarded`, `entry`, `repair_routes`,
    `waiver_policy`, and `checkpoint`. The parser does not distinguish
    closed/open value sets here; the resolver enforces the closed `checkpoint`
    set and required-field rules.
    """

    key: str
    value: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class StageForbiddenOutputsItem:
    """Raw `forbidden_outputs:` list of strings on a stage declaration."""

    values: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


StageBodyItem: _TypeAlias = (
    StageOwnerItem
    | StageLaneItem
    | StageSupportsItem
    | StageAppliesToItem
    | StageInputsItem
    | StageEmitsItem
    | StageArtifactsItem
    | StageScalarItem
    | StageForbiddenOutputsItem
)


@_dataclass(slots=True, frozen=True)
class StageDecl:
    """A top-level `stage` declaration.

    A stage names one graph node and binds an owner skill to typed inputs, an
    optional emitted receipt, an advance condition, and a durable checkpoint
    rule. Sub-plan 2 ships the typed-fields surface only; flow membership and
    closure expansion belong to later sub-plans.
    """

    name: str
    title: str
    items: tuple[StageBodyItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowIntentItem:
    """Raw `intent:` line on a `skill_flow` declaration."""

    value: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowStartItem:
    """Raw `start: NodeRef` line on a `skill_flow` declaration."""

    node_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowApproveItem:
    """Raw `approve: SkillFlowRef` line on a `skill_flow` declaration."""

    flow_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowEdgeRouteRef:
    """Raw `route: ReceiptRef.route_field.choice` ref on an edge body."""

    receipt_ref: NameRef
    route_field_key: str
    choice_key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowEdgeWhenRef:
    """Raw `when: EnumName.member` ref on an edge body."""

    enum_ref: NameRef
    member_key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Closed kind set for `kind:` on skill-flow edges.
SKILL_FLOW_EDGE_KINDS: frozenset[str] = frozenset(
    {"normal", "review", "repair", "recovery", "approval", "handoff"}
)


@_dataclass(slots=True, frozen=True)
class SkillFlowEdgeItem:
    """Raw `edge Source -> Target:` block on a `skill_flow` declaration.

    `kind` defaults to `normal` when the author omits `kind:`. The resolver
    enforces the closed kind set and the required `why:`. `route` and `when`
    stay `None` until the author binds a typed route or branch condition.
    """

    source_ref: NameRef
    target_ref: NameRef
    why: str
    kind: str = "normal"
    route: SkillFlowEdgeRouteRef | None = None
    when: SkillFlowEdgeWhenRef | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Closed `order:` set for `repeat` items.
SKILL_FLOW_REPEAT_ORDERS: frozenset[str] = frozenset(
    {"serial", "parallel", "unspecified"}
)


@_dataclass(slots=True, frozen=True)
class SkillFlowRepeatItem:
    """Raw `repeat Name: FlowRef` block on a `skill_flow` declaration."""

    name: str
    target_flow_ref: NameRef
    over_ref: NameRef
    order: str
    why: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowVariationItem:
    """Raw `variation <name>:` block on a `skill_flow` declaration."""

    name: str
    title: str
    safe_when: SkillFlowEdgeWhenRef | None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillFlowUnsafeItem:
    """Raw `unsafe <name>: "Title"` line on a `skill_flow` declaration."""

    name: str
    title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Closed `require` keys for `changed_workflow:` items.
SKILL_FLOW_CHANGED_WORKFLOW_REQUIRES: frozenset[str] = frozenset(
    {"nearest_flow", "difference", "safety_rationale"}
)


@_dataclass(slots=True, frozen=True)
class SkillFlowChangedWorkflowItem:
    """Raw `changed_workflow:` block on a `skill_flow` declaration."""

    allow_provisional_flow: bool
    requires: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


SkillFlowBodyItem: _TypeAlias = (
    SkillFlowIntentItem
    | SkillFlowStartItem
    | SkillFlowApproveItem
    | SkillFlowEdgeItem
    | SkillFlowRepeatItem
    | SkillFlowVariationItem
    | SkillFlowUnsafeItem
    | SkillFlowChangedWorkflowItem
)


@_dataclass(slots=True, frozen=True)
class SkillFlowDecl:
    """A top-level `skill_flow` declaration.

    Sub-plan 3 lifts the body from registry-only to a real DAG: `intent:`,
    `start:`, `approve:`, `edge`, `repeat`, `variation`, `unsafe`, and
    `changed_workflow:`. Graph closure, graph policies, and graph emit stay
    in later sub-plans.
    """

    name: str
    title: str
    items: tuple[SkillFlowBodyItem, ...] = ()
    source_span: SourceSpan | None = _field(default=None, compare=False)


# ---- Resolved skill-flow facts (compiler-owned only) ---------------------


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowNode:
    """One resolved node in a skill flow.

    `kind` is one of `stage`, `flow`, or `repeat`. `name` is the node identity
    used inside the flow (the local repeat name for repeat nodes; the
    canonical declaration name for stage/flow nodes).
    """

    name: str
    kind: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowEdgeRouteBinding:
    """Resolved receipt-route binding for one flow edge."""

    receipt_name: str
    route_field_key: str
    choice_key: str
    target_kind: str
    target_name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowEdgeWhen:
    """Resolved enum-member branch condition for one flow edge."""

    enum_name: str
    member_key: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowEdge:
    """One resolved flow edge."""

    source: ResolvedSkillFlowNode
    target: ResolvedSkillFlowNode
    kind: str
    why: str
    route: ResolvedSkillFlowEdgeRouteBinding | None = None
    when: ResolvedSkillFlowEdgeWhen | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowRepeat:
    """Resolved `repeat Name: FlowRef` metadata."""

    name: str
    target_flow_name: str
    over_kind: str
    over_name: str
    order: str
    why: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowVariation:
    """Resolved safe variation metadata."""

    name: str
    title: str
    safe_when: ResolvedSkillFlowEdgeWhen | None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowUnsafe:
    """Resolved unsafe variation metadata."""

    name: str
    title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlowChangedWorkflow:
    """Resolved `changed_workflow:` facts for one flow."""

    allow_provisional_flow: bool
    requires: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillFlow:
    """Resolved flow-local facts for one `skill_flow` declaration.

    Sub-plan 3 produces this object from one source unit. Graph closure across
    flows belongs to sub-plan 4.
    """

    canonical_name: str
    title: str
    intent: str | None
    start: ResolvedSkillFlowNode | None
    approve: str | None
    nodes: tuple[ResolvedSkillFlowNode, ...]
    edges: tuple[ResolvedSkillFlowEdge, ...]
    repeats: tuple[ResolvedSkillFlowRepeat, ...]
    variations: tuple[ResolvedSkillFlowVariation, ...]
    unsafe_variations: tuple[ResolvedSkillFlowUnsafe, ...]
    changed_workflow: ResolvedSkillFlowChangedWorkflow | None
    terminals: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Receipt route targets ----------------------------------------------------

# Closed v1 sentinel set for receipt route targets. New sentinels must be added
# explicitly here, in the grammar, and in the resolver.
RECEIPT_ROUTE_SENTINELS: frozenset[str] = frozenset({"human", "external", "terminal"})


@_dataclass(slots=True, frozen=True)
class ReceiptRouteStageTarget:
    """`-> stage StageRef` target on a receipt route choice."""

    stage_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReceiptRouteFlowTarget:
    """`-> flow SkillFlowRef` target on a receipt route choice."""

    flow_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReceiptRouteSentinelTarget:
    """`-> human | external | terminal` sentinel target on a receipt route choice."""

    sentinel: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


ReceiptRouteTarget: _TypeAlias = (
    ReceiptRouteStageTarget | ReceiptRouteFlowTarget | ReceiptRouteSentinelTarget
)


@_dataclass(slots=True, frozen=True)
class ReceiptRouteChoice:
    """One choice line inside a receipt route field.

    Form: `<choice_key>: "<choice title>" -> <target>`. The target is one of
    `stage StageRef`, `flow FlowRef`, `human`, `external`, or `terminal`.
    """

    key: str
    title: str
    target: ReceiptRouteTarget
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ReceiptDeclRouteField:
    """A `route <route_key>: "<title>"` block inside a top-level receipt body.

    Receipt route fields lower into a deterministic per-receipt `routes:`
    metadata map. They also lower into receipt-by-ref `json_schema` metadata
    as required string enum properties over the authored route choice keys.
    The human labels and target facts stay on the separate `routes:` payload.
    """

    key: str
    title: str
    choices: tuple[ReceiptRouteChoice, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedReceiptRouteChoice:
    """Lowered receipt route choice after target resolution.

    `target_kind` is one of `stage`, `flow`, or `sentinel`. `target_name`
    carries either the canonical declaration name (for stage and flow) or the
    sentinel keyword (for sentinel targets).
    """

    key: str
    title: str
    target_kind: str
    target_name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedReceiptRouteField:
    """Lowered receipt route field after target resolution."""

    key: str
    title: str
    choices: tuple[ResolvedReceiptRouteChoice, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Skill-graph declarations -------------------------------------------------

SKILL_GRAPH_RECOVERY_KEYS: frozenset[str] = frozenset(
    {"flow_receipt", "stage_status", "durable_artifact_status"}
)
SKILL_GRAPH_VIEW_KEYS: frozenset[str] = frozenset(
    {
        "flow_registry",
        "stage_contracts",
        "recovery_audit",
        "stepwise_manifest",
        "skill_inventory",
        "graph_markdown",
        "graph_json",
        "graph_contract",
        "graph_source",
        "artifact_inventory",
        "receipt_schema_dir",
        "diagram_d2",
        "diagram_svg",
        "diagram_mermaid",
    }
)
SKILL_GRAPH_WARNING_POLICY_KEYS: frozenset[str] = frozenset(
    {
        "branch_coverage_incomplete",
        "checked_skill_mention_unknown",
        "edge_route_binding_missing",
        "flow_without_approve",
        "manual_only_default_flow_conflict",
        "orphan_skill",
        "orphan_stage",
        "receipt_without_consumer",
        "relation_without_reason",
        "stage_owner_shared",
        "stage_without_risk_guard",
    }
)
SKILL_GRAPH_STRICT_POLICY_KEYS: frozenset[str] = frozenset(
    {
        "checked_skill_mentions",
        "edge_reason",
        "durable_checkpoint",
        "relation_reason",
        "route_targets_resolve",
        "branch_coverage",
        "stage_lane",
    }
)
SKILL_GRAPH_ALLOW_POLICY_KEYS: frozenset[str] = frozenset({"unbound_edges"})
SKILL_GRAPH_DAG_POLICY_KEYS: frozenset[str] = frozenset({"acyclic", "allow_cycle"})
SKILL_RELATION_KINDS: frozenset[str] = frozenset(
    {
        "baseline_for",
        "blocks",
        "extends",
        "requires",
        "supports",
        "composes",
        "audits",
        "teaches",
        "repairs",
        "delegates_to",
        "owns_surface",
        "reads_surface",
        "wraps",
        "writes_surface",
        "supersedes",
        "related",
    }
)


@_dataclass(slots=True, frozen=True)
class SkillRelation:
    """Raw `relations:` entry on a top-level `skill` declaration."""

    kind: str
    target_ref: NameRef
    why: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ArtifactOwnerItem:
    """Raw `owner: StageRef` line on a top-level `artifact` declaration."""

    stage_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ArtifactPathFamilyItem:
    """Raw `path_family: Ref` line on a top-level `artifact` declaration."""

    target_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ArtifactScalarItem:
    """A scalar field on a top-level `artifact` declaration."""

    key: str
    value: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


ArtifactBodyItem: _TypeAlias = ArtifactOwnerItem | ArtifactPathFamilyItem | ArtifactScalarItem


@_dataclass(slots=True, frozen=True)
class ArtifactDecl:
    """A top-level durable artifact declaration."""

    name: str
    title: str
    items: tuple[ArtifactBodyItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphPurposeItem:
    """Raw `purpose:` line on a top-level `skill_graph` declaration."""

    value: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphRootEntry:
    """One `flow <Ref>` or `stage <Ref>` line inside `roots:`."""

    kind: str
    target_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphRootsItem:
    """Raw `roots:` block on a top-level `skill_graph` declaration."""

    entries: tuple[SkillGraphRootEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphSetEntry:
    """One `<SetName>: "Title"` row inside `sets:`."""

    name: str
    title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphSetsItem:
    """Raw `sets:` block on a top-level `skill_graph` declaration."""

    entries: tuple[SkillGraphSetEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphRecoveryEntry:
    """One recovery ref inside `recovery:`."""

    key: str
    target_ref: NameRef
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphRecoveryItem:
    """Raw `recovery:` block on a top-level `skill_graph` declaration."""

    entries: tuple[SkillGraphRecoveryEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphPolicyEntry:
    """One policy line inside `policy:`."""

    action: str
    key: str
    reason: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphPolicyItem:
    """Raw `policy:` block on a top-level `skill_graph` declaration."""

    entries: tuple[SkillGraphPolicyEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphViewEntry:
    """One `<view_key>: "path"` row inside `views:`."""

    key: str
    path: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class SkillGraphViewsItem:
    """Raw `views:` block on a top-level `skill_graph` declaration."""

    entries: tuple[SkillGraphViewEntry, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


SkillGraphBodyItem: _TypeAlias = (
    SkillGraphPurposeItem
    | SkillGraphRootsItem
    | SkillGraphSetsItem
    | SkillGraphRecoveryItem
    | SkillGraphPolicyItem
    | SkillGraphViewsItem
)


@_dataclass(slots=True, frozen=True)
class SkillGraphDecl:
    """A top-level `skill_graph` declaration."""

    name: str
    title: str
    items: tuple[SkillGraphBodyItem, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Resolved stage facts -----------------------------------------------------


@_dataclass(slots=True, frozen=True)
class ResolvedStageInput:
    """One resolved stage input."""

    key: str
    type_kind: str
    type_name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedStage:
    """Compiler-owned facts for one top-level `stage` declaration."""

    canonical_name: str
    title: str
    stage_id: str | None
    owner_skill_name: str
    lane_name: str | None
    support_skill_names: tuple[str, ...]
    applies_to_flow_names: tuple[str, ...]
    inputs: tuple[ResolvedStageInput, ...]
    emits_receipt_name: str | None
    artifact_names: tuple[str, ...]
    checkpoint: str
    intent: str
    durable_target: str | None
    durable_evidence: str | None
    advance_condition: str
    risk_guarded: str | None
    entry: str | None
    repair_routes: str | None
    waiver_policy: str | None
    forbidden_outputs: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


# Resolved graph closure ---------------------------------------------------


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphRoot:
    """One resolved root on a `skill_graph` declaration."""

    kind: str
    name: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphSet:
    """One resolved graph-local set."""

    name: str
    title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphRecovery:
    """Resolved `recovery:` refs for one graph."""

    flow_receipt_name: str | None
    stage_status_name: str | None
    durable_artifact_status_name: str | None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphPolicy:
    """One resolved graph policy fact."""

    action: str
    key: str
    reason: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphView:
    """One resolved graph view override."""

    key: str
    path: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphRepeat:
    """Graph-closed repeat metadata with graph-set refs finalized."""

    name: str
    target_flow_name: str
    over_kind: str
    over_name: str
    order: str
    why: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphFlow:
    """Graph-owned view of one reached `skill_flow`."""

    canonical_name: str
    title: str
    intent: str | None
    start: ResolvedSkillFlowNode | None
    approve: str | None
    nodes: tuple[ResolvedSkillFlowNode, ...]
    edges: tuple[ResolvedSkillFlowEdge, ...]
    repeats: tuple[ResolvedSkillGraphRepeat, ...]
    variations: tuple[ResolvedSkillFlowVariation, ...]
    unsafe_variations: tuple[ResolvedSkillFlowUnsafe, ...]
    changed_workflow: ResolvedSkillFlowChangedWorkflow | None
    terminals: tuple[str, ...]
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphSkill:
    """One reached skill in a resolved graph."""

    name: str
    title: str
    purpose: str | None
    package_id: str | None
    category: str | None = None
    visibility: str | None = None
    manual_only: str | None = None
    default_flow_member: str | None = None
    aliases: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphSkillRelation:
    """One graph-closed relation between two reached skills."""

    source_skill_name: str
    target_skill_name: str
    kind: str
    why: str | None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphArtifact:
    """One reached durable artifact symbol in a resolved graph."""

    name: str
    title: str
    owner_stage_name: str
    path_family_kind: str | None = None
    path_family_name: str | None = None
    path: str | None = None
    section: str | None = None
    anchor: str | None = None
    intent: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphWarning:
    """One non-fatal graph warning produced by a `warn` policy."""

    code: str
    policy_key: str
    summary: str
    owner_kind: str
    owner_name: str
    detail: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphPackage:
    """One reached skill package id in a resolved graph."""

    package_id: str
    package_name: str
    package_title: str
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraphStageEdge:
    """One expanded stage-to-stage edge in the graph DAG."""

    source_stage_name: str
    target_stage_name: str
    via_flow_name: str
    kind: str
    why: str
    route_receipt_name: str | None = None
    route_field_key: str | None = None
    route_choice_key: str | None = None
    source_span: SourceSpan | None = _field(default=None, compare=False)


@_dataclass(slots=True, frozen=True)
class ResolvedSkillGraph:
    """Canonical resolved graph closure used by emit and verify."""

    canonical_name: str
    title: str
    purpose: str
    roots: tuple[ResolvedSkillGraphRoot, ...]
    sets: tuple[ResolvedSkillGraphSet, ...]
    recovery: ResolvedSkillGraphRecovery | None
    policies: tuple[ResolvedSkillGraphPolicy, ...]
    views: tuple[ResolvedSkillGraphView, ...]
    flows: tuple[ResolvedSkillGraphFlow, ...]
    stages: tuple[ResolvedStage, ...]
    skills: tuple[ResolvedSkillGraphSkill, ...]
    skill_relations: tuple[ResolvedSkillGraphSkillRelation, ...]
    artifacts: tuple[ResolvedSkillGraphArtifact, ...]
    receipts: tuple["ResolvedReceipt", ...]
    packages: tuple[ResolvedSkillGraphPackage, ...]
    warnings: tuple[ResolvedSkillGraphWarning, ...]
    stage_edges: tuple[ResolvedSkillGraphStageEdge, ...]
    stage_successors: dict[str, tuple[str, ...]]
    stage_predecessors: dict[str, tuple[str, ...]]
    stage_reaching_flows: dict[str, tuple[str, ...]]
    source_span: SourceSpan | None = _field(default=None, compare=False)
