from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from doctrine.emit_common import load_emit_targets
from doctrine.emit_skill import emit_target_skill
from doctrine.emit_skill_graph import emit_target_skill_graph
from doctrine.skill_graph_source_receipts import receipt_path_for_target as graph_receipt_path_for_target


def _write_graph_repo(root: Path) -> Path:
    prompt_path = root / "prompts" / "skills" / "controller" / "SKILL.prompt"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text(
        textwrap.dedent(
            """\
            enum StageLane: "Stage Lane"
                pipeline: "Pipeline"
                review: "Review"

            skill ControllerSkill: "Controller Skill"
                purpose: "Own the controller stages."
                package: "controller-package"

            receipt LessonPlanReceipt: "Lesson Plan Receipt"
                plan_status: string
                route next_route: "Next Route"
                    review: "Review the plan." -> stage AuthorReview
                    done: "Finish the graph." -> terminal

            stage LessonPlan: "Lesson Plan"
                owner: ControllerSkill
                lane: StageLane.pipeline
                intent: "Plan the lesson."
                durable_target: "Lesson plan."
                durable_evidence: "Plan receipt."
                advance_condition: "Plan receipt landed."
                emits: LessonPlanReceipt

            stage AuthorReview: "Author Review"
                owner: ControllerSkill
                lane: StageLane.review
                inputs:
                    flow_receipt: LessonPlanReceipt
                intent: "Review the plan."
                durable_target: "Review notes."
                durable_evidence: "Review receipt."
                advance_condition: "Review receipt landed."

            skill_flow F1AuthorLesson: "F1 - Author One Lesson"
                intent: "Plan then review one lesson."
                start: LessonPlan
                edge LessonPlan -> AuthorReview:
                    route: LessonPlanReceipt.next_route.review
                    why: "The review stage follows the receipt route."

            skill package ControllerPackage: "Controller Package"
                metadata:
                    name: "controller-package"
                    description: "Own the controller graph package."
                "Own the controller graph package."

            skill_graph ControllerGraph: "Controller Graph"
                purpose: "Emit the full controller graph bundle from one closure."
                roots:
                    flow F1AuthorLesson
                policy:
                    dag acyclic
                    require edge_reason
                    require durable_checkpoint
                    require route_targets_resolve
                    require stage_lane
                views:
                    graph_markdown: "references/controller-graph.md"
                    diagram_mermaid: "references/controller-graph.mmd"
            """
        ),
        encoding="utf-8",
    )
    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "doctrine-test"
            version = "0.0.0"

            [tool.doctrine.emit]

            [[tool.doctrine.emit.targets]]
            name = "skill_bundle"
            entrypoint = "prompts/skills/controller/SKILL.prompt"
            output_dir = "build/skill"

            [[tool.doctrine.emit.targets]]
            name = "graph_bundle"
            entrypoint = "prompts/skills/controller/SKILL.prompt"
            graph = "ControllerGraph"
            output_dir = "build/graph"
            """
        ),
        encoding="utf-8",
    )
    return pyproject


class EmitSkillGraphTests(unittest.TestCase):
    def test_emit_skill_graph_writes_graph_bundle_and_links_skill_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = _write_graph_repo(root)
            targets = load_emit_targets(pyproject)
            emit_target_skill(targets["skill_bundle"])
            with patch(
                "doctrine.emit_skill_graph.render_flow_svg",
                side_effect=lambda _d2, svg: svg.write_text("<svg>graph</svg>\n", encoding="utf-8"),
            ):
                emitted = emit_target_skill_graph(targets["graph_bundle"])

            emitted_dir = graph_receipt_path_for_target(targets["graph_bundle"]).parent
            emitted_relpaths = {
                path.relative_to(emitted_dir).as_posix()
                for path in emitted
            }
            self.assertIn("SKILL_GRAPH.contract.json", emitted_relpaths)
            self.assertIn("references/skill-graph.json", emitted_relpaths)
            self.assertIn("references/skill-graph.svg", emitted_relpaths)
            self.assertIn("SKILL_GRAPH.source.json", emitted_relpaths)

            receipt_payload = json.loads(
                graph_receipt_path_for_target(targets["graph_bundle"]).read_text(
                    encoding="utf-8"
                )
            )
            outputs = {
                entry["path"]: entry["sha256"]
                for entry in receipt_payload["outputs"]
            }
            self.assertIn("references/controller-graph.mmd", outputs)
            self.assertEqual(
                receipt_payload["diagram_mermaid_sha256"],
                outputs["references/controller-graph.mmd"],
            )
            linked = receipt_payload["linked_package_receipts"]
            self.assertEqual(len(linked), 1)
            self.assertEqual(linked[0]["package_id"], "controller-package")
            self.assertEqual(linked[0]["target_name"], "skill_bundle")
