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

