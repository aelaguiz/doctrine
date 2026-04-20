from __future__ import annotations


def _analysis_attachment_source() -> str:
    return """analysis DraftAnalysis: "Draft Analysis"
    facts: "Facts"
        "Restate the current draft job before you route work."

agent AnalysisDemo:
    role: "Keep the analysis attachment visible."
    analysis: DraftAnalysis
"""


def _reserved_analysis_slot_source() -> str:
    return """analysis DraftAnalysis: "Draft Analysis"
    facts: "Facts"
        "Restate the current draft job before you route work."

abstract agent AnalysisBase:
    role: "Base role."
    abstract analysis

agent AnalysisDemo [AnalysisBase]:
    role: "Keep the analysis attachment visible."
    analysis: DraftAnalysis
"""


def _output_schema_attachment_source() -> str:
    return """schema LessonInventory: "Lesson Inventory"
    sections:
        summary: "Summary"
            "State the required summary."

output SchemaOutput: "Schema Output"
    target: TurnResponse
    shape: JsonObject
    requirement: Required
    schema: LessonInventory

agent OutputDemo:
    role: "Keep the schema attachment visible."
    outputs: "Outputs"
        SchemaOutput
"""


def _input_structure_attachment_source() -> str:
    return """document LessonPlan: "Lesson Plan"
    section summary: "Summary"
        "State the lesson summary."

input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required
    structure: LessonPlan

agent InputDemo:
    role: "Keep the structure attachment visible."
    inputs: "Inputs"
        DraftSpec
"""


def _invalid_readable_guard_source() -> str:
    return """output BrokenComment: "Broken Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    callout scope: "Scope" when BrokenComment.summary_present
        kind: note
        "This should fail."

agent ReadableGuardDemo:
    role: "Keep readable guards honest."
    outputs: "Outputs"
        BrokenComment
"""


def _invalid_readable_table_source() -> str:
    return """document BrokenGuide: "Broken Guide"
    table release_gates: "Release Gates"
        notes:
            "This should fail."

output BrokenGuideFile: "Broken Guide File"
    target: File
        path: "broken.md"
    shape: MarkdownDocument
    requirement: Required
    structure: BrokenGuide

agent ReadableTableDemo:
    role: "Keep readable tables honest."
    outputs: "Outputs"
        BrokenGuideFile
"""


def _output_schema_owner_conflict_source() -> str:
    return """schema LessonInventory: "Lesson Inventory"
    sections:
        summary: "Summary"
            "State the required summary."

output SchemaOutput: "Schema Output"
    target: TurnResponse
    shape: JsonObject
    requirement: Required
    schema: LessonInventory

    must_include: "Must Include"
        summary: "Summary"
            "Repeat the summary locally."

agent OutputDemo:
    role: "Keep the schema attachment visible."
    outputs: "Outputs"
        SchemaOutput
"""


def _output_schema_structure_conflict_source() -> str:
    return """schema DeliveryInventory: "Delivery Inventory"
    sections:
        summary: "Summary"
            "Include a short summary."

document DeliveryPlan: "Delivery Plan"
    section summary: "Summary"
        "Write the summary."

output InvalidDeliveryPlan: "Invalid Delivery Plan"
    target: File
        path: "unit_root/INVALID_DELIVERY_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: DeliveryInventory
    structure: DeliveryPlan
"""


def _output_target_typed_as_unsupported_kind_source() -> str:
    return """enum HandoffKind: "Handoff Kind"
    alpha: "alpha"
    beta: "beta"


output target StrayHandoff: "Stray Handoff"
    typed_as: HandoffKind


output StrayNote: "Stray Note"
    target: StrayHandoff
    shape: MarkdownDocument
    requirement: Advisory

    standalone_read: "Standalone Read"
        "Nothing here."


agent StrayHandoffDemo:
    role: "Demo invalid typed_as."
    outputs: "Outputs"
        StrayNote
"""


def _skill_binding_mode_enum_missing_source() -> str:
    return """skill package SharedSkillPackage: "Shared Skill Package"
    metadata:
        name: "shared-skill-package"
        description: "Shared producer/audit package with no host binds."
    "Run the shared producer/audit package."


enum SkillMode: "Skill Mode"
    producer: "Producer"
    audit: "Audit"


skill SharedSkill: "Shared Skill"
    purpose: "Run the shared producer/audit package."
    package: "shared-skill-package"


agent ProducerAgent:
    role: "Tag the skill binding with an undeclared enum."
    skills: "Skills"
        skill shared: SharedSkill
            mode producer = SkillMode.producer as MissingEnum
"""


def _skill_binding_mode_audit_output_bind_source() -> str:
    return """skill package BoundOutputPackage: "Bound Output Package"
    metadata:
        name: "bound-output-package"
        description: "Emit through a host-bound final_output slot."
    host_contract:
        final_output final_response: "Final Response"
    "Emit through {{host:final_response}}."


enum SkillMode: "Skill Mode"
    producer: "Producer"
    audit: "Audit"


output AuditResponse: "Audit Response"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required


skill BoundOutputSkill: "Bound Output Skill"
    purpose: "Emit through the shared final_output slot."
    package: "bound-output-package"


agent AuditorAgent:
    role: "Audit-mode skill binding must not emit to an output target."
    outputs: "Outputs"
        AuditResponse
    final_output: AuditResponse
    skills: "Skills"
        skill shared: BoundOutputSkill
            mode audit = SkillMode.audit as SkillMode
            bind:
                final_response: final_output
"""


def _skill_binding_mode_not_in_enum_source() -> str:
    return """skill package SharedSkillPackage: "Shared Skill Package"
    metadata:
        name: "shared-skill-package"
        description: "Shared producer/audit package with no host binds."
    "Run the shared producer/audit package."


enum SkillMode: "Skill Mode"
    producer: "Producer"
    audit: "Audit"


skill SharedSkill: "Shared Skill"
    purpose: "Run the shared producer/audit package."
    package: "shared-skill-package"


agent ProducerAgent:
    role: "Tag the skill binding with a mode that is not in the enum."
    skills: "Skills"
        skill shared: SharedSkill
            mode nonexistent = SkillMode.producer as SkillMode
"""


def _output_shape_enum_only_selector_source() -> str:
    return """enum WriterRole: "Writer Role"
    producer: "Producer"
    critic: "Critic"


output schema WriterTurnSchema: "Writer Turn Schema"
    field headline: "Headline"
        type: string

    example:
        headline: "Draft ready for review"


output shape WriterTurnJson: "Writer Turn JSON"
    kind: JsonObject
    schema: WriterTurnSchema

    selector:
        mode role as WriterRole

    field_notes: "Field Notes"
        case WriterRole.producer:
            "Producer guidance."
        case WriterRole.critic:
            "Critic guidance."


output WriterTurnResponse: "Writer Turn Response"
    target: TurnResponse
    shape: WriterTurnJson
    requirement: Required


agent WriterDemo:
    role: "Keep the soft-deprecated enum-only selector form alive until the timebox expires."
    selectors:
        role: WriterRole.producer
    outputs: "Outputs"
        WriterTurnResponse
    final_output: WriterTurnResponse
"""


def _output_target_typed_as_family_mismatch_source() -> str:
    return """document HandoffDocA: "Handoff Doc A"
    section summary: "Summary"
        "Write the summary."


document HandoffDocB: "Handoff Doc B"
    section summary: "Summary"
        "Write the summary."


output target MismatchedHandoff: "Mismatched Handoff"
    typed_as: HandoffDocA


output MismatchedNote: "Mismatched Note"
    target: MismatchedHandoff
    shape: MarkdownDocument
    structure: HandoffDocB
    requirement: Advisory

    standalone_read: "Standalone Read"
        "Nothing here."


agent MismatchedHandoffDemo:
    role: "Demo the family mismatch."
    outputs: "Outputs"
        MismatchedNote
"""


def _abstract_slot_annotation_unresolved_source() -> str:
    return """abstract agent TypedPolicyBase:
    abstract policy: UndeclaredPolicyDoc


agent TypedPolicyConcrete[TypedPolicyBase]:
    role: "Try to bind a missing typed policy."

    policy: UndeclaredPolicyDoc
"""


def _concrete_agent_wrong_family_binding_source() -> str:
    return """document RealPolicyDoc: "Real Policy"
    section summary: "Summary"
        "Read the real policy."


workflow WrongFamilyWorkflow: "Wrong Family"
    "Do the wrong-family work."


abstract agent TypedPolicyBase:
    abstract policy: RealPolicyDoc


agent TypedPolicyConcrete[TypedPolicyBase]:
    role: "Bind a wrong-family entity to a typed slot."

    policy: WrongFamilyWorkflow
"""


def _rule_unknown_scope_target_source() -> str:
    return """abstract agent ComposerBase:
    role: "Base composer."


agent DemoComposer[ComposerBase]:
    role: "Demo composer."


rule ComposerNeedsBase: "Composers must inherit the base"
    scope:
        flow: MissingBase
    assertions:
        requires inherit ComposerBase
    message: "Every composer must inherit ComposerBase."
"""


def _rule_unknown_assertion_target_source() -> str:
    return """abstract agent ComposerBase:
    role: "Base composer."


agent DemoComposer[ComposerBase]:
    role: "Demo composer."


rule ComposerNeedsBase: "Composers must inherit the base"
    scope:
        role_class: Composer
    assertions:
        requires inherit MissingAncestor
    message: "Every composer must inherit MissingAncestor."
"""


def _rule_requires_inherit_violated_source() -> str:
    return """abstract agent UpstreamPoisoningInvariant:
    role: "Invariant base."


agent HonestComposer:
    role: "Honest composer without inheritance."


rule ComposerNeedsInvariant: "Composers must inherit the invariant"
    scope:
        role_class: Composer
    assertions:
        requires inherit UpstreamPoisoningInvariant
    message: "Every composer must inherit UpstreamPoisoningInvariant."
"""


def _rule_forbids_bind_violated_source() -> str:
    return """abstract agent LegacyBase:
    role: "Forbidden ancestor."


agent BadComposer[LegacyBase]:
    role: "Composer that still inherits the forbidden base."


rule NoLegacyBase: "Composers must not inherit LegacyBase"
    scope:
        role_class: Composer
    assertions:
        forbids bind LegacyBase
    message: "LegacyBase is retired."
"""


def _rule_requires_declare_violated_source() -> str:
    return """abstract agent SoulBase:
    role: "Base agent."
    abstract soul


agent PlainComposer:
    role: "Composer without the required slot."


rule ComposerHasSoul: "Composers must declare soul"
    scope:
        role_class: Composer
    assertions:
        requires declare soul
    message: "Every composer must declare the soul slot."
"""
