from __future__ import annotations

_DEFAULT_EXAMPLE_BODY = object()


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
    schema_body: str | None = None,
    example_body: str | None | object = _DEFAULT_EXAMPLE_BODY,
) -> str:
    rendered_schema_body = schema_body or """enum RepoStatus: "Repo Status"
    ok: "OK"
    action_required: "Action Required"


output schema RepoStatusSchema: "Repo Status Schema"
    field summary: "Summary"
        type: string
        note: "Short natural-language status."

    field status: "Status"
        type: RepoStatus
        note: "Current repo outcome."

    field next_step: "Next Step"
        type: string
        nullable
        note: "Null only when no follow-up is needed."
"""
    if example_body is _DEFAULT_EXAMPLE_BODY:
        rendered_example_body: str | None = """example:
        summary: "Branch is clean and checks passed."
        status: "ok"
        next_step: null
"""
    else:
        rendered_example_body = example_body
    rendered_schema = rendered_schema_body.rstrip()
    if rendered_example_body is not None:
        example_lines = rendered_example_body.rstrip().splitlines()
        if example_lines and not example_lines[0].startswith("    "):
            example_lines[0] = f"    {example_lines[0]}"
        rendered_schema = f"{rendered_schema}\n\n" + "\n".join(example_lines)

    return f"""{rendered_schema}

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    schema: RepoStatusSchema

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


def _final_output_missing_local_shape_source() -> str:
    return """output FinalReply: "Final Reply"
    target: TurnResponse
    shape: MissingShape
    requirement: Required

agent InvalidFinalOutputAgent:
    role: "Use a missing local output shape."
    workflow: "Reply"
        "Reply and stop."
    outputs: "Outputs"
        FinalReply
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
    return """enum AcceptanceRoute: "Acceptance Route"
    follow_up: "Follow Up"
    revise: "Revise"


output schema AcceptanceControlSchema: "Acceptance Control Schema"
    field route: "Route"
        type: AcceptanceRoute
        note: "Control route for the next owner."

    field current_artifact: "Current Artifact"
        type: string
        note: "Current artifact after review."

    field next_owner: "Next Owner"
        type: string
        note: "Next owner after review."

    example:
        route: "follow_up"
        current_artifact: "Draft Plan"
        next_owner: "ReviewLead"

output shape AcceptanceControlJson: "Acceptance Control JSON"
    kind: JsonObject
    schema: AcceptanceControlSchema

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
