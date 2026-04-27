from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.parser import parse_file


def _compile_graph(source: str, *, filename: str = "SKILL.prompt"):
    return _compile_graph_files(
        {f"skills/graph/{filename}": source},
        entrypoint=f"skills/graph/{filename}",
    )


def _compile_graph_files(source_by_path: dict[str, str], *, entrypoint: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prompt_root = root / "prompts"
        for rel_path, source in source_by_path.items():
            prompt_path = prompt_root / rel_path
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
        prompt_path = prompt_root / entrypoint
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

    def test_imported_branch_enum_missing_member_fails_strict_coverage(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        export enum BranchChoice: "Branch Choice"
                            yes: "Yes"
                            no: "No"
                        """,
                    "AGENTS.prompt": """\
                        from shared import BranchChoice

                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own branch work."

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
                                why: "Only the yes branch is modeled."

                        skill_graph Graph: "Graph"
                            purpose: "Strict graph with imported branches."
                            roots:
                                flow BranchFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Imported enum refs must enforce the same full coverage as local
        # enum refs. Otherwise a graph can skip a branch and still compile.
        self.assertIn("E561", str(raised.exception))
        self.assertIn("BranchChoice", str(raised.exception))
        self.assertIn("no", str(raised.exception))

    def test_module_qualified_branch_enum_missing_member_warns_on_graph_path(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    export enum BranchChoice: "Branch Choice"
                        yes: "Yes"
                        no: "No"
                    """,
                "AGENTS.prompt": """\
                    import shared

                    skill OwnerSkill: "Owner Skill"
                        purpose: "Own branch work."

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
                            when: shared.BranchChoice.yes
                            why: "Only the yes branch is modeled."

                    skill_graph Graph: "Graph"
                        purpose: "Warning graph with imported branches."
                        roots:
                            flow BranchFlow
                        policy:
                            warn branch_coverage_incomplete
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Warning mode must still find missing members on module-qualified
        # enum refs, because reviewers depend on W205 to see skipped paths.
        warnings = {warning.code: warning for warning in graph.warnings}
        self.assertIn("W205", warnings)
        self.assertEqual(
            warnings["W205"].policy_key,
            "branch_coverage_incomplete",
        )
        self.assertIn("BranchChoice", warnings["W205"].detail)
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

    def test_dag_policy_rejects_acyclic_and_allow_cycle_together(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph(
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
                    purpose: "Conflicting DAG policy."
                    roots:
                        flow ParentFlow
                    policy:
                        dag acyclic
                        dag allow_cycle "The cycle models a manual review loop."
                """
            )

        # A graph cannot both require an acyclic expansion and allow a cycle.
        # The resolver must fail before the looser allowance hides the strict line.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("dag acyclic", str(raised.exception))
        self.assertIn("dag allow_cycle", str(raised.exception))

    def test_imported_stage_route_binding_is_still_required(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own routed stages."

                        receipt DraftReceipt: "Draft Receipt"
                            draft_id: string
                            route next_route: "Next Route"
                                review: "Review" -> stage ReviewStage

                        export stage DraftStage: "Draft Stage"
                            owner: OwnerSkill
                            intent: "Draft."
                            durable_target: "Draft."
                            durable_evidence: "Draft."
                            advance_condition: "Draft done."
                            emits: DraftReceipt

                        export stage ReviewStage: "Review Stage"
                            owner: OwnerSkill
                            inputs:
                                draft: DraftReceipt
                            intent: "Review."
                            durable_target: "Review."
                            durable_evidence: "Review."
                            advance_condition: "Review done."
                        """,
                    "AGENTS.prompt": """\
                        from shared import DraftStage, ReviewStage

                        skill_flow ImportedRouteFlow: "Imported Route Flow"
                            start: DraftStage
                            edge DraftStage -> ReviewStage:
                                why: "Review follows the routed receipt."

                        skill_graph Graph: "Graph"
                            purpose: "Graph with imported routed stages."
                            roots:
                                flow ImportedRouteFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Imported stages keep their own emitted receipts. The route binding
        # check must look at that owner file, not only at the flow's file.
        self.assertIn("E561", str(raised.exception))
        self.assertIn("is unbound", str(raised.exception))
        self.assertIn("DraftReceipt.next_route.review", str(raised.exception))

    def test_module_qualified_stage_start_closes_in_graph(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    skill SharedOwnerSkill: "Shared Owner Skill"
                        purpose: "Own imported stages."

                    export stage DraftStage: "Draft Stage"
                        owner: SharedOwnerSkill
                        intent: "Draft."
                        durable_target: "Draft."
                        durable_evidence: "Draft."
                        advance_condition: "Draft done."
                    """,
                "AGENTS.prompt": """\
                    import shared

                    skill LocalOwnerSkill: "Local Owner Skill"
                        purpose: "Own local stages."

                    stage DraftStage: "Draft Stage"
                        owner: LocalOwnerSkill
                        intent: "Local draft."
                        durable_target: "Local draft."
                        durable_evidence: "Local draft."
                        advance_condition: "Local draft done."

                    skill_flow ImportedStartFlow: "Imported Start Flow"
                        start: shared.DraftStage

                    skill_graph Graph: "Graph"
                        purpose: "Graph with module-qualified stage start."
                        roots:
                            flow ImportedStartFlow
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Graph closure must keep the owner of a module-qualified stage node.
        # A valid imported stage start should not be re-resolved as a local name.
        self.assertEqual(
            {stage.canonical_name for stage in graph.stages},
            {"DraftStage"},
        )
        self.assertEqual(graph.stages[0].owner_skill_name, "SharedOwnerSkill")

    def test_same_named_imported_and_local_stages_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill SharedOwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared review."

                        export stage ReviewStage: "Review Stage"
                            owner: SharedOwnerSkill
                            intent: "Shared review."
                            durable_target: "Shared review."
                            durable_evidence: "Shared review."
                            advance_condition: "Shared review done."

                        export skill_flow SharedReviewFlow: "Shared Review Flow"
                            start: ReviewStage
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill LocalOwnerSkill: "Local Owner Skill"
                            purpose: "Own local review."

                        stage ReviewStage: "Review Stage"
                            owner: LocalOwnerSkill
                            intent: "Local review."
                            durable_target: "Local review."
                            durable_evidence: "Local review."
                            advance_condition: "Local review done."

                        skill_flow LocalReviewFlow: "Local Review Flow"
                            start: ReviewStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding public stage names."
                            roots:
                                flow LocalReviewFlow
                                flow shared.SharedReviewFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts are keyed by stage name. Reaching two
        # same-named stages must fail instead of merging their owners and flows.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("ReviewStage", str(raised.exception))
        self.assertIn("shared.ReviewStage", str(raised.exception))

    def test_same_named_imported_and_local_flows_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill SharedOwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared flow."

                        stage SharedStage: "Shared Stage"
                            owner: SharedOwnerSkill
                            intent: "Shared."
                            durable_target: "Shared."
                            durable_evidence: "Shared."
                            advance_condition: "Shared done."

                        stage SharedStartStage: "Shared Start Stage"
                            owner: SharedOwnerSkill
                            intent: "Shared start."
                            durable_target: "Shared start."
                            durable_evidence: "Shared start."
                            advance_condition: "Shared start done."

                        export skill_flow ReviewFlow: "Shared Review Flow"
                            start: SharedStage

                        export skill_flow SharedRootFlow: "Shared Root Flow"
                            start: SharedStartStage
                            edge SharedStartStage -> ReviewFlow:
                                why: "Enter the shared review flow."
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill LocalOwnerSkill: "Local Owner Skill"
                            purpose: "Own local flow."

                        stage LocalStartStage: "Local Start Stage"
                            owner: LocalOwnerSkill
                            intent: "Local start."
                            durable_target: "Local start."
                            durable_evidence: "Local start."
                            advance_condition: "Local start done."

                        stage LocalStage: "Local Stage"
                            owner: LocalOwnerSkill
                            intent: "Local."
                            durable_target: "Local."
                            durable_evidence: "Local."
                            advance_condition: "Local done."

                        skill_flow ReviewFlow: "Local Review Flow"
                            start: LocalStage

                        skill_flow LocalRootFlow: "Local Root Flow"
                            start: LocalStartStage
                            edge LocalStartStage -> ReviewFlow:
                                why: "Enter the local review flow."

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding public flow names."
                            roots:
                                flow LocalRootFlow
                                flow shared.SharedRootFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts expose flow names without module identity.
        # Reaching two same-named flows must fail instead of merging them.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("ReviewFlow", str(raised.exception))
        self.assertIn("shared.ReviewFlow", str(raised.exception))

    def test_same_named_imported_and_local_skills_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill OwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared stage."

                        stage SharedStage: "Shared Stage"
                            owner: OwnerSkill
                            intent: "Shared."
                            durable_target: "Shared."
                            durable_evidence: "Shared."
                            advance_condition: "Shared done."

                        export skill_flow SharedFlow: "Shared Flow"
                            start: SharedStage
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill OwnerSkill: "Local Owner Skill"
                            purpose: "Own local stage."

                        stage LocalStage: "Local Stage"
                            owner: OwnerSkill
                            intent: "Local."
                            durable_target: "Local."
                            durable_evidence: "Local."
                            advance_condition: "Local done."

                        skill_flow LocalFlow: "Local Flow"
                            start: LocalStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding public skill names."
                            roots:
                                flow LocalFlow
                                flow shared.SharedFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts expose skills by name. Same-named skills from
        # different modules must not collapse into one owner or relation entry.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("OwnerSkill", str(raised.exception))
        self.assertIn("shared.OwnerSkill", str(raised.exception))

    def test_same_package_id_from_imported_skills_fails_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "left/AGENTS.prompt": """\
                        skill LeftSkill: "Left Skill"
                            purpose: "Own the left package."
                            package: "shared-package"

                        skill package LeftPackage: "Left Package"
                            metadata:
                                name: "shared-package"
                                description: "Left package."
                            "Left package."

                        stage LeftStage: "Left Stage"
                            owner: LeftSkill
                            intent: "Left."
                            durable_target: "Left."
                            durable_evidence: "Left."
                            advance_condition: "Left done."

                        export skill_flow LeftFlow: "Left Flow"
                            start: LeftStage
                        """,
                    "right/AGENTS.prompt": """\
                        skill RightSkill: "Right Skill"
                            purpose: "Own the right package."
                            package: "shared-package"

                        skill package RightPackage: "Right Package"
                            metadata:
                                name: "shared-package"
                                description: "Right package."
                            "Right package."

                        stage RightStage: "Right Stage"
                            owner: RightSkill
                            intent: "Right."
                            durable_target: "Right."
                            durable_evidence: "Right."
                            advance_condition: "Right done."

                        export skill_flow RightFlow: "Right Flow"
                            start: RightStage
                        """,
                    "AGENTS.prompt": """\
                        import left
                        import right

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding package ids."
                            roots:
                                flow left.LeftFlow
                                flow right.RightFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts expose package metadata by package id. Distinct
        # reached packages must fail instead of keeping whichever record landed first.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("shared-package", str(raised.exception))
        self.assertIn("left.shared-package", str(raised.exception))
        self.assertIn("right.shared-package", str(raised.exception))

    def test_same_named_imported_and_local_receipts_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill SharedOwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared receipt."

                        receipt PacketReceipt: "Shared Packet Receipt"
                            packet_id: string

                        stage SharedStage: "Shared Stage"
                            owner: SharedOwnerSkill
                            intent: "Shared."
                            durable_target: "Shared."
                            durable_evidence: "Shared."
                            advance_condition: "Shared done."
                            emits: PacketReceipt

                        export skill_flow SharedFlow: "Shared Flow"
                            start: SharedStage
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill LocalOwnerSkill: "Local Owner Skill"
                            purpose: "Own local receipt."

                        receipt PacketReceipt: "Local Packet Receipt"
                            packet_id: string

                        stage LocalStage: "Local Stage"
                            owner: LocalOwnerSkill
                            intent: "Local."
                            durable_target: "Local."
                            durable_evidence: "Local."
                            advance_condition: "Local done."
                            emits: PacketReceipt

                        skill_flow LocalFlow: "Local Flow"
                            start: LocalStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding public receipt names."
                            roots:
                                flow LocalFlow
                                flow shared.SharedFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts expose receipts by name. Same-named receipts
        # from different modules must not collapse fields or emit metadata.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("PacketReceipt", str(raised.exception))
        self.assertIn("shared.PacketReceipt", str(raised.exception))

    def test_same_named_imported_and_local_artifacts_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill SharedOwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared artifact."

                        stage SharedProducerStage: "Shared Producer Stage"
                            owner: SharedOwnerSkill
                            intent: "Produce shared artifact."
                            durable_target: "Shared artifact."
                            durable_evidence: "Shared artifact."
                            advance_condition: "Shared artifact done."

                        artifact EvidenceArtifact: "Shared Evidence Artifact"
                            owner: SharedProducerStage
                            path: "shared/evidence.md"
                            intent: "Shared evidence."

                        stage SharedConsumerStage: "Shared Consumer Stage"
                            owner: SharedOwnerSkill
                            inputs:
                                evidence: EvidenceArtifact
                            intent: "Read shared artifact."
                            durable_target: "Shared review."
                            durable_evidence: "Shared review."
                            advance_condition: "Shared review done."

                        export skill_flow SharedFlow: "Shared Flow"
                            start: SharedConsumerStage
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill LocalOwnerSkill: "Local Owner Skill"
                            purpose: "Own local artifact."

                        stage LocalProducerStage: "Local Producer Stage"
                            owner: LocalOwnerSkill
                            intent: "Produce local artifact."
                            durable_target: "Local artifact."
                            durable_evidence: "Local artifact."
                            advance_condition: "Local artifact done."

                        artifact EvidenceArtifact: "Local Evidence Artifact"
                            owner: LocalProducerStage
                            path: "local/evidence.md"
                            intent: "Local evidence."

                        stage LocalConsumerStage: "Local Consumer Stage"
                            owner: LocalOwnerSkill
                            inputs:
                                evidence: EvidenceArtifact
                            intent: "Read local artifact."
                            durable_target: "Local review."
                            durable_evidence: "Local review."
                            advance_condition: "Local review done."

                        skill_flow LocalFlow: "Local Flow"
                            start: LocalConsumerStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding public artifact names."
                            roots:
                                flow LocalFlow
                                flow shared.SharedFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Public graph artifacts expose artifacts by name. Same-named input
        # artifacts must fail instead of dropping one path or owner contract.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("EvidenceArtifact", str(raised.exception))
        self.assertIn("shared.EvidenceArtifact", str(raised.exception))

    def test_same_named_recovery_enums_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        export enum Status: "Shared Status"
                            ready: "Ready"
                            blocked: "Blocked"
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        enum Status: "Local Status"
                            current: "Current"
                            stale: "Stale"

                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own recovery graph."

                        receipt FlowReceipt: "Flow Receipt"
                            current_stage: string

                        stage LocalStage: "Local Stage"
                            owner: OwnerSkill
                            intent: "Local."
                            durable_target: "Local."
                            durable_evidence: "Local."
                            advance_condition: "Local done."

                        skill_flow LocalFlow: "Local Flow"
                            start: LocalStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding recovery enum names."
                            roots:
                                flow LocalFlow
                            recovery:
                                flow_receipt: FlowReceipt
                                stage_status: Status
                                durable_artifact_status: shared.Status
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Recovery refs are public graph facts keyed by enum name. Same-named
        # enums from different modules must not both render as `Status`.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("Status", str(raised.exception))
        self.assertIn("shared.Status", str(raised.exception))

    def test_same_named_artifact_path_families_fail_loud_in_one_graph(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        document PathFamily: "Shared Path Family"
                            "Shared artifact paths."

                        skill SharedOwnerSkill: "Shared Owner Skill"
                            purpose: "Own shared artifact path family."

                        artifact SharedEvidenceArtifact: "Shared Evidence Artifact"
                            owner: SharedProducerStage
                            path_family: PathFamily
                            path: "shared/evidence.md"
                            intent: "Shared evidence."

                        stage SharedProducerStage: "Shared Producer Stage"
                            owner: SharedOwnerSkill
                            artifacts:
                                SharedEvidenceArtifact
                            intent: "Produce shared artifact."
                            durable_target: "Shared artifact."
                            durable_evidence: "Shared artifact."
                            advance_condition: "Shared artifact done."

                        export skill_flow SharedFlow: "Shared Flow"
                            start: SharedProducerStage
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        document PathFamily: "Local Path Family"
                            "Local artifact paths."

                        skill LocalOwnerSkill: "Local Owner Skill"
                            purpose: "Own local artifact path family."

                        artifact LocalEvidenceArtifact: "Local Evidence Artifact"
                            owner: LocalProducerStage
                            path_family: PathFamily
                            path: "local/evidence.md"
                            intent: "Local evidence."

                        stage LocalProducerStage: "Local Producer Stage"
                            owner: LocalOwnerSkill
                            artifacts:
                                LocalEvidenceArtifact
                            intent: "Produce local artifact."
                            durable_target: "Local artifact."
                            durable_evidence: "Local artifact."
                            advance_condition: "Local artifact done."

                        skill_flow LocalFlow: "Local Flow"
                            start: LocalProducerStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with colliding path family names."
                            roots:
                                flow LocalFlow
                                flow shared.SharedFlow
                        """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Artifact path families render as a public kind/name pair. Same-named
        # document path families from different modules must not both render as
        # document `PathFamily`.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("PathFamily", str(raised.exception))
        self.assertIn("shared.PathFamily", str(raised.exception))

    def test_recovery_flow_receipt_uses_authored_owner_identity(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    export receipt FlowReceipt: "Shared Flow Receipt"
                        shared_stage: string
                    """,
                "AGENTS.prompt": """\
                    import shared

                    receipt FlowReceipt: "Local Flow Receipt"
                        local_stage: string

                    skill OwnerSkill: "Owner Skill"
                        purpose: "Own recovery graph."

                    stage LocalStage: "Local Stage"
                        owner: OwnerSkill
                        intent: "Local."
                        durable_target: "Local."
                        durable_evidence: "Local."
                        advance_condition: "Local done."

                    skill_flow LocalFlow: "Local Flow"
                        start: LocalStage

                    skill_graph Graph: "Graph"
                        purpose: "Graph with an imported recovery receipt."
                        roots:
                            flow LocalFlow
                        recovery:
                            flow_receipt: shared.FlowReceipt
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Recovery flow receipts are authored refs. A same-named local receipt
        # must not replace the imported receipt after graph recovery resolves.
        self.assertEqual(graph.recovery.flow_receipt_name, "FlowReceipt")
        self.assertEqual(
            {receipt.title for receipt in graph.receipts},
            {"Shared Flow Receipt"},
        )
        self.assertEqual(
            {field.key for receipt in graph.receipts for field in receipt.fields},
            {"shared_stage"},
        )

    def test_orphan_stage_warning_uses_owner_identity(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    skill SharedOwnerSkill: "Shared Owner Skill"
                        purpose: "Own the shared stage."

                    export stage ReviewStage: "Shared Review Stage"
                        owner: SharedOwnerSkill
                        intent: "Shared review."
                        durable_target: "Shared review."
                        durable_evidence: "Shared review."
                        advance_condition: "Shared review done."
                    """,
                "AGENTS.prompt": """\
                    import shared

                    skill LocalOwnerSkill: "Local Owner Skill"
                        purpose: "Own the local stage."

                    stage ReviewStage: "Local Review Stage"
                        owner: LocalOwnerSkill
                        intent: "Local review."
                        durable_target: "Local review."
                        durable_evidence: "Local review."
                        advance_condition: "Local review done."

                    skill_graph Graph: "Graph"
                        purpose: "Graph with an imported same-named stage."
                        roots:
                            stage shared.ReviewStage
                        policy:
                            warn orphan_stage
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Orphan warnings check the graph entrypoint module. A reached imported
        # ReviewStage must not hide the same-named local ReviewStage. Public
        # warning owners stay name-only, so the detail must disambiguate.
        warnings = {warning.code: warning for warning in graph.warnings}
        self.assertIn("W201", warnings)
        self.assertEqual(warnings["W201"].owner_kind, "stage")
        self.assertEqual(warnings["W201"].owner_name, "ReviewStage")
        self.assertEqual(
            warnings["W201"].detail,
            "Skill graph `Graph` reaches stage `shared.ReviewStage`, "
            "but does not reach local stage `ReviewStage` from the graph "
            "entrypoint module.",
        )

    def test_orphan_skill_warning_uses_owner_identity(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    export skill ReviewSkill: "Shared Review Skill"
                        purpose: "Own the shared stage."

                    export stage SharedStage: "Shared Stage"
                        owner: ReviewSkill
                        intent: "Shared work."
                        durable_target: "Shared work."
                        durable_evidence: "Shared work."
                        advance_condition: "Shared work done."
                    """,
                "AGENTS.prompt": """\
                    import shared

                    skill ReviewSkill: "Local Review Skill"
                        purpose: "This local skill is not reached."

                    skill_graph Graph: "Graph"
                        purpose: "Graph with an imported same-named skill."
                        roots:
                            stage shared.SharedStage
                        policy:
                            warn orphan_skill
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Orphan skill warnings must compare owner identity, not only public
        # skill name, or a reached imported skill can hide a local orphan.
        # Public warning owners stay name-only, so the detail must disambiguate.
        warnings = {warning.code: warning for warning in graph.warnings}
        self.assertIn("W202", warnings)
        self.assertEqual(warnings["W202"].owner_kind, "skill")
        self.assertEqual(warnings["W202"].owner_name, "ReviewSkill")
        self.assertEqual(
            warnings["W202"].detail,
            "Skill graph `Graph` reaches skill `shared.ReviewSkill`, "
            "but does not reach local skill `ReviewSkill` from a stage owner, "
            "stage support, relation, or checked skill mention in the graph "
            "entrypoint module.",
        )

    def test_route_target_matching_uses_stage_owner_identity(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own the shared review stage."

                        export stage ReviewStage: "Review Stage"
                            owner: OwnerSkill
                            intent: "Shared review."
                            durable_target: "Shared review."
                            durable_evidence: "Shared review."
                            advance_condition: "Shared review done."
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own local stages."

                        receipt DraftReceipt: "Draft Receipt"
                            draft_id: string
                            route next_route: "Next Route"
                                review: "Review" -> stage shared.ReviewStage

                        stage DraftStage: "Draft Stage"
                            owner: OwnerSkill
                            intent: "Draft."
                            durable_target: "Draft."
                            durable_evidence: "Draft."
                            advance_condition: "Draft done."
                            emits: DraftReceipt

                        stage ReviewStage: "Review Stage"
                            owner: OwnerSkill
                            inputs:
                                draft: DraftReceipt
                            intent: "Local review."
                            durable_target: "Local review."
                            durable_evidence: "Local review."
                            advance_condition: "Local review done."

                        skill_flow RouteFlow: "Route Flow"
                            start: DraftStage
                            edge DraftStage -> ReviewStage:
                                route: DraftReceipt.next_route.review
                                why: "This incorrectly targets the local stage."

                        skill_graph Graph: "Graph"
                            purpose: "Graph with same-named route targets."
                            roots:
                                flow RouteFlow
                    """,
                },
                entrypoint="AGENTS.prompt",
            )

        # The route choice points to shared.ReviewStage, not the local
        # ReviewStage. Name-only matching can bind the wrong target.
        self.assertIn("E561", str(raised.exception))
        self.assertIn("targets stage `shared.ReviewStage`", str(raised.exception))
        self.assertIn("instead of the declared edge target", str(raised.exception))

    def test_applies_to_coverage_uses_flow_owner_identity(self) -> None:
        with self.assertRaises(DoctrineError) as raised:
            _compile_graph_files(
                {
                    "shared/AGENTS.prompt": """\
                        export skill_flow ReviewFlow: "Shared Review Flow"
                        """,
                    "AGENTS.prompt": """\
                        import shared

                        skill OwnerSkill: "Owner Skill"
                            purpose: "Own local stages."

                        stage DraftStage: "Draft Stage"
                            owner: OwnerSkill
                            applies_to:
                                shared.ReviewFlow
                            intent: "Draft."
                            durable_target: "Draft."
                            durable_evidence: "Draft."
                            advance_condition: "Draft done."

                        skill_flow ReviewFlow: "Local Review Flow"
                            start: DraftStage

                        skill_graph Graph: "Graph"
                            purpose: "Graph with same-named applies_to flow."
                            roots:
                                flow ReviewFlow
                    """,
                },
                entrypoint="AGENTS.prompt",
            )

        # Stage `applies_to:` lists shared.ReviewFlow. Reaching the stage
        # through local ReviewFlow must not pass just because names match.
        self.assertIn("E562", str(raised.exception))
        self.assertIn("applies_to", str(raised.exception))
        self.assertIn("ReviewFlow", str(raised.exception))

    def test_graph_set_repeat_can_target_module_qualified_flow(self) -> None:
        graph = _compile_graph_files(
            {
                "shared/AGENTS.prompt": """\
                    skill OwnerSkill: "Owner Skill"
                        purpose: "Own imported repeat flow."

                    stage ChildStage: "Child Stage"
                        owner: OwnerSkill
                        intent: "Child."
                        durable_target: "Child."
                        durable_evidence: "Child."
                        advance_condition: "Child done."

                    export skill_flow ChildFlow: "Child Flow"
                        start: ChildStage
                    """,
                "AGENTS.prompt": """\
                    import shared

                    enum SlotKind: "Slot Kind"
                        one: "One"

                    skill LocalOwnerSkill: "Local Owner Skill"
                        purpose: "Own local repeat flow."

                    stage LocalChildStage: "Local Child Stage"
                        owner: LocalOwnerSkill
                        intent: "Local child."
                        durable_target: "Local child."
                        durable_evidence: "Local child."
                        advance_condition: "Local child done."

                    skill_flow ChildFlow: "Local Child Flow"
                        start: LocalChildStage

                    skill_flow ParentFlow: "Parent Flow"
                        repeat SlotRun: shared.ChildFlow
                            over: SlotSet
                            order: serial
                            why: "Run once per graph slot."

                    skill_graph Graph: "Graph"
                        purpose: "Graph with imported repeat target."
                        roots:
                            flow ParentFlow
                        sets:
                            SlotSet: "Slot Set"
                    """,
            },
            entrypoint="AGENTS.prompt",
        )

        # Repeat target flow identity must survive graph-set late binding.
        # Otherwise graph closure re-resolves shared.ChildFlow as local ChildFlow.
        repeats = {
            repeat.name: repeat
            for flow in graph.flows
            for repeat in flow.repeats
        }
        self.assertEqual(repeats["SlotRun"].over_kind, "graph_set")
        self.assertEqual(
            {stage.canonical_name for stage in graph.stages},
            {"ChildStage"},
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
