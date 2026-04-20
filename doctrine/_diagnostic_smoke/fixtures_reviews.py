from __future__ import annotations

import re
from pathlib import Path

from doctrine._diagnostic_smoke.fixtures_common import _indent_block


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


def _review_case_gate_override_base_source(*, override_block: str) -> str:
    """Case-selected review with one override block spliced in per caller.

    The override_block is pasted inside case `draft_path` right after its
    `contract:` line. Use this for E531/E532 smoke fixtures.
    """
    return f"""enum ReviewMode: "Review Mode"
    draft_rewrite: "draft-rewrite"
    metadata_refresh: "metadata-refresh"

input DraftSpec: "Draft Spec"
    source: File
        path: "unit_root/DRAFT_SPEC.md"
    shape: MarkdownDocument
    requirement: Required

input MetadataRecord: "Metadata Record"
    source: File
        path: "unit_root/METADATA.json"
    shape: JsonObject
    requirement: Required

input ReviewFacts: "Review Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required

workflow DraftReviewContract: "Draft Review Contract"
    completeness: "Completeness"
        "Confirm the draft covers the required sections."

workflow MetadataReviewContract: "Metadata Review Contract"
    freshness: "Freshness"
        "Confirm the metadata stays current."

agent RevisionOwner:
    role: "Own the next revision pass after review."
    workflow: "Revise"
        "Take the selected current artifact to the next revision step."

output SelectedReviewComment: "Selected Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "Say whether the review accepted the selected subject or asked for changes."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact this review judged."

    analysis_performed: "Analysis Performed"
        "Sum up the review work that led to the verdict."

    output_contents_that_matter: "Output Contents That Matter"
        "Sum up the parts of the selected subject the next owner should read first."

    next_owner: "Next Owner"
        "Name the next owner. Use {{{{RevisionOwner}}}} in both selected review modes."

    current_artifact: "Current Artifact"
        "Name the artifact that is current in the selected review mode."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "Name the failing review gates in authored order."

    standalone_read: "Standalone Read"
        "This comment should stand on its own."

    trust_surface:
        current_artifact

review_family SelectedReviewFamily: "Selected Review"
    comment_output: SelectedReviewComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner
        current_artifact: current_artifact

    selector:
        mode selected_mode = ReviewFacts.selected_mode as ReviewMode

    cases:
        draft_path: "Draft Path"
            when ReviewMode.draft_rewrite
            subject: DraftSpec
            contract: DraftReviewContract
{override_block}
            checks:
                accept "The draft review contract passes." when contract.passes
            on_accept:
                current artifact DraftSpec via SelectedReviewComment.current_artifact
                route "Accepted draft rewrite goes to RevisionOwner." -> RevisionOwner
            on_reject:
                current artifact DraftSpec via SelectedReviewComment.current_artifact
                route "Rejected draft rewrite goes to RevisionOwner." -> RevisionOwner

        metadata_path: "Metadata Path"
            when ReviewMode.metadata_refresh
            subject: MetadataRecord
            contract: MetadataReviewContract
            checks:
                accept "The metadata review contract passes." when contract.passes
            on_accept:
                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                route "Accepted metadata refresh goes to RevisionOwner." -> RevisionOwner
            on_reject:
                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                route "Rejected metadata refresh goes to RevisionOwner." -> RevisionOwner

agent SelectedReviewFamilyDemo:
    role: "Keep case-selected review families explicit and exhaustive."
    review: SelectedReviewFamily
    inputs: "Inputs"
        DraftSpec
        MetadataRecord
        ReviewFacts
    outputs: "Outputs"
        SelectedReviewComment
"""


def _review_case_gate_override_remove_missing_source() -> str:
    override_block = (
        "            override gates:\n"
        "                remove not_declared\n"
    )
    return _review_case_gate_override_base_source(override_block=override_block)


def _review_case_gate_override_add_collision_source() -> str:
    override_block = (
        "            override gates:\n"
        "                add completeness: \"Collides\"\n"
    )
    return _review_case_gate_override_base_source(override_block=override_block)
