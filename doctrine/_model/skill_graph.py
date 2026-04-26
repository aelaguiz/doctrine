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
class StageScalarItem:
    """A typed scalar field on a top-level `stage` declaration.

    Covers `id`, `intent`, `durable_target`, `durable_evidence`,
    `advance_condition`, `risk_guarded`, and `checkpoint`. The parser does not
    distinguish closed/open value sets here; the resolver enforces the closed
    `checkpoint` set and required-field rules.
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
