from __future__ import annotations

import re
import textwrap
from pathlib import Path


class SmokeFailure(RuntimeError):
    """Raised when the direct diagnostic smoke checks fail."""


def _write_prompt(tmp_dir: str, source: str) -> Path:
    root = Path(tmp_dir)
    prompts = root / "prompts"
    prompts.mkdir()
    prompt_path = prompts / "AGENTS.prompt"
    prompt_path.write_text(source)
    return prompt_path


def _review_smoke_source(
    *,
    on_accept_body: str,
    next_owner_text: str = '"Name the next owner, including {{AcceptOwner}} when the draft is accepted and {{RejectOwner}} when the draft is rejected."',
    failure_detail_guard: str = "fields.verdict == ReviewVerdict.changes_requested",
) -> str:
    return f"""input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

agent AcceptOwner:
    role: "Own accepted drafts."
    workflow: "Accept"
        "Handle the accepted draft."

agent RejectOwner:
    role: "Own rejected drafts."
    workflow: "Reject"
        "Handle the rejected draft."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "Say whether the review accepted the draft or asked for changes."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."

    analysis_performed: "Analysis Performed"
        "Sum up the review work that led to the verdict and compare {{{{fields.reviewed_artifact}}}} with {{{{contract.completeness}}}}."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize the parts of the draft the next owner must read first."

    next_owner: "Next Owner"
        {next_owner_text}

    failure_detail: "Failure Detail" when {failure_detail_guard}:
        failing_gates: "Failing Gates"
            "Name the failing review gates in authored order."

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        "Use {{{{contract.completeness}}}} before you route {{{{fields.next_owner}}}}."
        accept "The shared draft review contract passes." when contract.passes

    on_accept:
{_indent_block(on_accept_body, 8)}

    on_reject:
        current none
        route "Rejected draft goes to RejectOwner." -> RejectOwner

agent ReviewDemo:
    role: "Keep review routing aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
"""


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


def _review_invalid_guarded_match_head_source() -> str:
    return """input DraftSpec: "Draft Spec"
    source: File
        path: "draft.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    checks: "Checks"
        match DraftSpec.status:
            else when DraftSpec.needs_follow_up:
                accept "The shared draft review contract passes." when contract.passes

    on_accept:
        current none
        route "Accepted draft goes to AcceptOwner." -> AcceptOwner

    on_reject:
        current none
        route "Rejected draft goes to RejectOwner." -> RejectOwner

agent AcceptOwner:
    role: "Own accepted drafts."
    workflow: "Accept"
        "Handle the accepted draft."

agent RejectOwner:
    role: "Own rejected drafts."
    workflow: "Reject"
        "Handle the rejected draft."

agent ReviewDemo:
    role: "Keep review routing aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
"""


def _review_exact_gate_stress_source(*, gate_count: int) -> str:
    base_path = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "45_review_contract_gate_export_and_exact_failures"
        / "prompts"
        / "AGENTS.prompt"
    )
    base = base_path.read_text()
    modes = "\n".join(f"    m{i}: \"m{i}\"" for i in range(gate_count))
    gates = "".join(
        f"""    gate_{i}: "Gate {i}"
        "Confirm gate {i}."

"""
        for i in range(gate_count)
    )
    gate_refs = ", ".join(f"{{{{contract.gate_{i}}}}}" for i in range(gate_count))
    mode_checks = "".join(
        f"""            ReviewMode.m{i}:
                reject contract.gate_{i} when ReviewFacts.selected_review_basis_failed

"""
        for i in range(gate_count)
    )
    source = (
        f"""enum ReviewMode: "Review Mode"
{modes}

input ReviewFacts: "Review Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required

"""
        + base
    )
    source = re.sub(
        r'workflow ExactGateReviewContract: "Exact Gate Review Contract"\n(?:    .*?\n\n)+?# Declare the owners',
        'workflow ExactGateReviewContract: "Exact Gate Review Contract"\n'
        + gates
        + "# Declare the owners",
        source,
        flags=re.S,
    )
    source = source.replace(
        '    inputs: "Inputs"\n        DraftSpec\n',
        '    inputs: "Inputs"\n        DraftSpec\n        ReviewFacts\n',
    )
    source = source.replace(
        '            "List the exact shared-contract gate names in authored order, including {{contract.completeness}}, {{contract.clarity}}, and {{contract.handoff_truth}} when they fail."',
        f'            "Name the exact exported shared-contract gate identities in authored order, including {gate_refs} when they fail."',
    )
    source = re.sub(
        r'    contract_gate_checks: "Contract Gate Checks"\n(?:        .*\n)+?\n    on_accept:',
        '    contract_gate_checks: "Contract Gate Checks"\n'
        '        match ReviewFacts.selected_mode:\n'
        + mode_checks
        + '        accept "The shared review contract passes." when contract.passes\n\n'
        '    on_accept:',
        source,
    )
    return source


def _flow_visualizer_showcase_source() -> str:
    return """input ProjectBrief: "Project Brief"
    source: File
        path: "project_root/_authoring/PROJECT_BRIEF.md"
    shape: MarkdownDocument
    requirement: Required

input AudienceGuide: "Audience Guide"
    source: File
        path: "project_root/_authoring/AUDIENCE_GUIDE.md"
    shape: MarkdownDocument
    requirement: Required

output ExecutionPlan: "Execution Plan"
    target: File
        path: "project_root/_authoring/EXECUTION_PLAN.md"
    shape: MarkdownDocument
    requirement: Required

output ResearchPacket: "Research Packet"
    target: File
        path: "project_root/_authoring/RESEARCH_PACKET.md"
    shape: MarkdownDocument
    requirement: Required

output LaunchDraft: "Launch Draft"
    target: File
        path: "project_root/_authoring/LAUNCH_DRAFT.md"
    shape: MarkdownDocument
    requirement: Required

output SharedHandoff: "Shared Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the artifact that is current after this turn."

    use_now: "Use Now"
        "Name the file or comment the next owner should read first."

    next_owner: "Next Owner"
        "Name the honest next owner."

    trust_surface:
        current_artifact
        use_now
        next_owner

agent ProjectLead:
    role: "Plan the work and route it to research."
    workflow: "Project Lead"
        routing: "Project Routing"
            route "Start research with ResearchSpecialist." -> ResearchSpecialist
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        ExecutionPlan
        SharedHandoff

agent ResearchSpecialist:
    role: "Turn the brief into a research packet."
    workflow: "Research"
        routing: "Project Routing"
            route "Hand the research packet to WritingSpecialist." -> WritingSpecialist
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        ResearchPacket
        SharedHandoff

agent WritingSpecialist:
    role: "Turn the research packet into a launch draft."
    workflow: "Writing"
        routing: "Project Routing"
            route "Return the draft to ProjectLead." -> ProjectLead
    inputs: "Inputs"
        ProjectBrief
        AudienceGuide
    outputs: "Outputs"
        LaunchDraft
        SharedHandoff
"""


def _final_output_prose_source() -> str:
    return """output FinalReply: "Final Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

    format_notes: "Expected Structure"
        "Lead with the shipped outcome."

    standalone_read: "Standalone Read"
        "The user should understand what changed and what happens next."

agent HelloAgent:
    role: "Answer plainly and end the turn."
    workflow: "Reply"
        "Reply and stop."
    outputs: "Outputs"
        FinalReply
    final_output: FinalReply
"""


def _final_output_json_source(
    *,
    schema_file: str = "schemas/repo_status.schema.json",
    example_file: str = "examples/repo_status.example.json",
) -> str:
    return f"""json schema RepoStatusSchema: "Repo Status Schema"
    profile: OpenAIStructuredOutput
    file: "{schema_file}"

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema
    example_file: "{example_file}"

    explanation: "Field Notes"
        "Use the schema fields exactly once."

output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required

    standalone_read: "Standalone Read"
        "The final answer should stand on its own as one structured repo-status result."

agent RepoStatusAgent:
    role: "Report repo status in structured form."
    workflow: "Summarize"
        "Summarize the repo state and end with the declared final output."
    outputs: "Outputs"
        RepoStatusFinalResponse
    final_output: RepoStatusFinalResponse
"""


def _final_output_non_output_ref_source() -> str:
    return """schema ReleaseSchema: "Release Schema"
    sections:
        summary: "Summary"
            "Provide a summary."

agent InvalidFinalOutputAgent:
    role: "Try to point final_output at a schema."
    workflow: "Reply"
        "Reply and stop."
    final_output: ReleaseSchema
"""


def _final_output_missing_emission_source() -> str:
    return """output FinalReply: "Final Reply"
    target: TurnResponse
    shape: CommentText
    requirement: Required

agent InvalidFinalOutputAgent:
    role: "Forget to emit the declared final output."
    workflow: "Reply"
        "Reply and stop."
    final_output: FinalReply
"""


def _final_output_file_target_source() -> str:
    return """output ReleaseNotesFile: "Release Notes File"
    target: File
        path: "artifacts/RELEASE_NOTES.md"
    shape: MarkdownDocument
    requirement: Required

agent InvalidFinalOutputAgent:
    role: "Try to end with a file."
    workflow: "Reply"
        "Reply and stop."
    outputs: "Outputs"
        ReleaseNotesFile
    final_output: ReleaseNotesFile
"""


def _final_output_review_prose_source() -> str:
    return """input DraftSpec: "Draft Spec"
    source: File
        path: "unit_root/DRAFT_SPEC.md"
    shape: MarkdownDocument
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

agent ReviewLead:
    role: "Own accepted drafts."
    workflow: "Follow Up"
        "Take accepted drafts forward."

agent DraftAuthor:
    role: "Fix rejected drafts."
    workflow: "Revise"
        "Revise the rejected draft."

output DraftReviewComment: "Draft Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the draft passed review."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize what the next owner should read first."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    next_owner: "Next Owner"
        "Name {{ReviewLead}} when accepted and {{DraftAuthor}} when rejected."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "List the failing review gates in authored order."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "From this output alone, a downstream owner should know the review verdict, current artifact, and next owner."

review DraftReview: "Draft Review"
    subject: DraftSpec
    contract: DraftReviewContract
    comment_output: DraftReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        accept "The shared draft review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact DraftSpec via DraftReviewComment.current_artifact
        route "Accepted draft goes to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact DraftSpec via DraftReviewComment.current_artifact
        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

agent ReviewFinalOutputAgent:
    role: "Keep review final outputs aligned."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
    final_output: DraftReviewComment
"""


def _final_output_review_split_prose_source() -> str:
    return _final_output_review_prose_source() + """

output DraftReviewDecision: "Draft Review Decision"
    target: TurnResponse
    shape: CommentText
    requirement: Required

    control_summary: "Control Summary"
        "End with one short control summary for the routed owner."

    retry_note: "Retry Note" when verdict == ReviewVerdict.changes_requested:
        "Only include this note when the review requests changes."

    current_alignment: "Current Artifact Alignment"
        "Keep the control summary aligned with {{fields.current_artifact}}."

    standalone_read: "Standalone Read"
        "The final control summary should stand on its own for the routed owner."

agent SplitReviewFinalOutputAgent:
    role: "Emit the rich review comment and a small final control summary."
    review: DraftReview
    inputs: "Inputs"
        DraftSpec
    outputs: "Outputs"
        DraftReviewComment
        DraftReviewDecision
    final_output: DraftReviewDecision
"""


def _final_output_review_split_json_source() -> str:
    return """json schema AcceptanceControlSchema: "Acceptance Control Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/acceptance_control.schema.json"

output shape AcceptanceControlJson: "Acceptance Control JSON"
    kind: JsonObject
    schema: AcceptanceControlSchema
    example_file: "examples/acceptance_control.example.json"

    field_notes: "Field Notes"
        "Keep `current_artifact` aligned with {{fields.current_artifact}}."
        "Use `route` value `revise` only when {{contract.outline_complete}} fails."

input DraftPlan: "Draft Plan"
    source: File
        path: "unit_root/DRAFT_PLAN.md"
    shape: MarkdownDocument
    requirement: Required

schema PlanReviewContract: "Plan Review Contract"
    sections:
        summary: "Summary"
            "Summarize the reviewed plan."

    gates:
        outline_complete: "Outline Complete"
            "Confirm the reviewed plan includes the outline."

agent ReviewLead:
    role: "Own accepted plans."
    workflow: "Follow Up"
        "Take accepted plans forward."

agent PlanAuthor:
    role: "Fix rejected plans."
    workflow: "Revise"
        "Revise the rejected plan."

output AcceptanceReviewComment: "Acceptance Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the plan passed review."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis."

    output_contents_that_matter: "Output Contents That Matter"
        "Summarize what the next owner should read first."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    next_owner: "Next Owner"
        "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "List exact failing gates, including {{contract.outline_complete}} when it fails."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "From this output alone, a downstream owner should know the acceptance verdict, current artifact, and next owner."

output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    changes_requested_note: "Changes Requested Note" when verdict == ReviewVerdict.changes_requested:
        "Only emit this retry control when the review requests changes."

    standalone_read: "Standalone Read"
        "This final JSON should be enough for the next owner to route the review result."

review AcceptanceReview: "Acceptance Review"
    subject: DraftPlan
    contract: PlanReviewContract
    comment_output: AcceptanceReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    contract_checks: "Contract Checks"
        accept "The acceptance review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Accepted plan goes to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Rejected plan goes to PlanAuthor." -> PlanAuthor

agent ReviewSplitJsonFinalOutputAgent:
    role: "Emit the review comment and end with a control-only JSON result."
    review: AcceptanceReview
    inputs: "Inputs"
        DraftPlan
    outputs: "Outputs"
        AcceptanceReviewComment
        AcceptanceControlFinalResponse
    final_output: AcceptanceControlFinalResponse
"""


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    normalized = textwrap.dedent(text).strip("\n")
    return "\n".join(f"{prefix}{line}" if line else "" for line in normalized.splitlines())


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)
