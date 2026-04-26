from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.parser import parse_file


def _compile_graph(source: str, *, filename: str = "SKILL.prompt"):
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prompt_path = root / "prompts" / "skills" / "graph" / filename
        prompt_path.parent.mkdir(parents=True)
        prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
        session = CompilationSession(parse_file(prompt_path))
        return session.compile_skill_graph()


class SkillGraphSemanticsTests(unittest.TestCase):
    def test_relations_mentions_and_allowed_unbound_edges_are_graph_facts(self) -> None:
        graph = _compile_graph(
            """\
            skill AuthorSkill: "Author Skill"
                purpose: "Own authoring work."
                package: "author-package"
                relations:
                    requires ReviewSkill:
                        why: "Needs {{skill:ReviewSkill.package}} for review."

            skill ReviewSkill: "Review Skill"
                purpose: "Review drafted work."
                package: "review-package"

            skill package AuthorPackage: "Author Package"
                metadata:
                    name: "author-package"
                    description: "Author package."
                "Author package."

            skill package ReviewPackage: "Review Package"
                metadata:
                    name: "review-package"
                    description: "Review package."
                "Review package."

            receipt DraftReceipt: "Draft Receipt"
                draft_id: string
                route next_route: "Next Route"
                    review: "Review" -> stage ReviewStage

            stage DraftStage: "Draft Stage"
                owner: AuthorSkill
                intent: "Draft with {{skill:ReviewSkill.purpose}} nearby."
                durable_target: "Draft receipt."
                durable_evidence: "Draft receipt."
                advance_condition: "Draft receipt lands."
                emits: DraftReceipt

            stage ReviewStage: "Review Stage"
                owner: ReviewSkill
                inputs:
                    draft: DraftReceipt
                intent: "Review the draft."
                durable_target: "Review notes."
                durable_evidence: "Review notes."
                advance_condition: "Review notes land."

            skill_flow AuthorFlow: "Author Flow"
                intent: "Use {{skill:AuthorSkill}}."
                start: DraftStage
                edge DraftStage -> ReviewStage:
                    why: "Send to {{skill:ReviewSkill}}."

            skill_graph Graph: "Graph"
                purpose: "Graph for {{skill:AuthorSkill}}."
                roots:
                    flow AuthorFlow
                policy:
                    require checked_skill_mentions
                    require relation_reason
                    allow unbound_edges
                    warn edge_route_binding_missing
            """
        )

        self.assertEqual(graph.purpose, "Graph for Author Skill.")
        self.assertEqual(
            {skill.name for skill in graph.skills},
            {"AuthorSkill", "ReviewSkill"},
        )
        self.assertEqual(len(graph.skill_relations), 1)
        relation = graph.skill_relations[0]
        self.assertEqual(relation.source_skill_name, "AuthorSkill")
        self.assertEqual(relation.target_skill_name, "ReviewSkill")
        self.assertEqual(relation.kind, "requires")
        self.assertEqual(relation.why, "Needs review-package for review.")
        draft_stage = next(stage for stage in graph.stages if stage.canonical_name == "DraftStage")
        self.assertEqual(
            draft_stage.intent,
            "Draft with Review drafted work. nearby.",
        )
        flow = graph.flows[0]
        self.assertEqual(flow.intent, "Use Author Skill.")
        self.assertEqual(flow.edges[0].why, "Send to Review Skill.")
        self.assertIn("W209", {warning.code for warning in graph.warnings})

    def test_branch_coverage_can_warn_on_graph_path(self) -> None:
        graph = _compile_graph(
            """\
            skill OwnerSkill: "Owner Skill"
                purpose: "Own branch work."

            enum BranchChoice: "Branch Choice"
                yes: "Yes"
                no: "No"

            stage StartStage: "Start Stage"
                owner: OwnerSkill
                intent: "Choose a path."
                durable_target: "Start receipt."
                durable_evidence: "Start receipt."
                advance_condition: "Start receipt lands."

            stage YesStage: "Yes Stage"
                owner: OwnerSkill
                intent: "Handle yes."
                durable_target: "Yes receipt."
                durable_evidence: "Yes receipt."
                advance_condition: "Yes receipt lands."

            skill_flow BranchFlow: "Branch Flow"
                start: StartStage
                edge StartStage -> YesStage:
                    when: BranchChoice.yes
                    why: "Only the yes branch is modeled for legacy work."

            skill_graph Graph: "Graph"
                purpose: "Graph with legacy incomplete branch coverage."
                roots:
                    flow BranchFlow
                policy:
                    warn branch_coverage_incomplete
            """
        )

        warnings = {warning.code: warning for warning in graph.warnings}
        self.assertIn("W205", warnings)
        self.assertEqual(
            warnings["W205"].policy_key,
            "branch_coverage_incomplete",
        )
        self.assertIn("no", warnings["W205"].detail)

    def test_checked_skill_mentions_fail_when_required(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph(
                """\
                skill OwnerSkill: "Owner Skill"
                    purpose: "Own the stage."

                stage StartStage: "Start Stage"
                    owner: OwnerSkill
                    intent: "Use {{skill:MissingSkill}}."
                    durable_target: "Receipt."
                    durable_evidence: "Receipt."
                    advance_condition: "Receipt lands."

                skill_graph Graph: "Graph"
                    purpose: "Strict graph."
                    roots:
                        stage StartStage
                    policy:
                        require checked_skill_mentions
                """
            )
        self.assertIn("E562", str(raised.exception))
        self.assertIn("MissingSkill", str(raised.exception))

    def test_relation_reason_can_be_required(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph(
                """\
                skill OwnerSkill: "Owner Skill"
                    purpose: "Own the stage."
                    relations:
                        requires HelperSkill:
                            why: ""

                skill HelperSkill: "Helper Skill"
                    purpose: "Help."

                stage StartStage: "Start Stage"
                    owner: OwnerSkill
                    intent: "Start."
                    durable_target: "Receipt."
                    durable_evidence: "Receipt."
                    advance_condition: "Receipt lands."

                skill_graph Graph: "Graph"
                    purpose: "Strict graph."
                    roots:
                        stage StartStage
                    policy:
                        require relation_reason
                """
            )
        self.assertIn("E566", str(raised.exception))
        self.assertIn("relation_reason", str(raised.exception))

    def test_dag_allow_cycle_keeps_cross_flow_cycle_in_scope(self) -> None:
        graph = _compile_graph(
            """\
            skill OwnerSkill: "Owner Skill"
                purpose: "Own stages."

            stage StageA: "Stage A"
                owner: OwnerSkill
                intent: "A."
                durable_target: "A."
                durable_evidence: "A."
                advance_condition: "A done."

            stage StageB: "Stage B"
                owner: OwnerSkill
                intent: "B."
                durable_target: "B."
                durable_evidence: "B."
                advance_condition: "B done."

            skill_flow ChildFlow: "Child Flow"
                start: StageB
                edge StageB -> StageA:
                    why: "Child returns to A."

            skill_flow ParentFlow: "Parent Flow"
                start: StageA
                edge StageA -> ChildFlow:
                    why: "Parent enters child."

            skill_graph Graph: "Graph"
                purpose: "Allow a named cycle."
                roots:
                    flow ParentFlow
                policy:
                    dag allow_cycle "The cycle models a manual review loop."
            """
        )

        policies = {
            (policy.action, policy.key): policy.reason
            for policy in graph.policies
        }
        self.assertEqual(
            policies[("dag", "allow_cycle")],
            "The cycle models a manual review loop.",
        )
        self.assertEqual(
            {(edge.source_stage_name, edge.target_stage_name) for edge in graph.stage_edges},
            {("StageA", "StageB"), ("StageB", "StageA")},
        )

    def test_artifacts_are_graph_owned_and_stage_inputs_can_read_them(self) -> None:
        graph = _compile_graph(
            """\
            skill ProducerSkill: "Producer Skill"
                purpose: "Write the packet."

            skill ConsumerSkill: "Consumer Skill"
                purpose: "Read the packet."

            document PacketPathFamily: "Packet Path Family"
                "Section packet paths."

            artifact SectionPacket: "Section Packet"
                owner: ProducePacket
                path_family: PacketPathFamily
                section: "Template"
                anchor: "Section Packet"
                intent: "Carry checked section facts."

            stage ProducePacket: "Produce Packet"
                owner: ProducerSkill
                artifacts:
                    SectionPacket
                intent: "Produce the packet."
                durable_target: "Section packet."
                durable_evidence: "Section packet receipt."
                advance_condition: "Packet is written."

            stage ConsumePacket: "Consume Packet"
                owner: ConsumerSkill
                inputs:
                    packet: SectionPacket
                intent: "Consume the packet."
                durable_target: "Review notes."
                durable_evidence: "Review notes."
                advance_condition: "Review notes land."

            skill_flow PacketFlow: "Packet Flow"
                start: ProducePacket
                edge ProducePacket -> ConsumePacket:
                    why: "The consumer reads the producer artifact."

            skill_graph Graph: "Graph"
                purpose: "Graph with durable artifacts."
                roots:
                    flow PacketFlow
            """
        )

        self.assertEqual(len(graph.artifacts), 1)
        artifact = graph.artifacts[0]
        self.assertEqual(artifact.name, "SectionPacket")
        self.assertEqual(artifact.owner_stage_name, "ProducePacket")
        self.assertEqual(artifact.path_family_kind, "document")
        self.assertEqual(artifact.path_family_name, "PacketPathFamily")
        producer = next(
            stage for stage in graph.stages if stage.canonical_name == "ProducePacket"
        )
        consumer = next(
            stage for stage in graph.stages if stage.canonical_name == "ConsumePacket"
        )
        self.assertEqual(producer.artifact_names, ("SectionPacket",))
        self.assertEqual(consumer.inputs[0].type_kind, "artifact")
