from __future__ import annotations


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

