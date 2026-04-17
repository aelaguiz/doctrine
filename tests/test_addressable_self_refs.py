from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class AddressableSelfRefTests(unittest.TestCase):
    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def _render_agent_markdown(
        self,
        source: str,
        *,
        agent_name: str,
    ) -> str:
        return render_markdown(self._compile_agent(source, agent_name=agent_name))

    def test_self_addressed_workflow_and_skills_refs_render_without_false_cycles(self) -> None:
        rendered = self._render_agent_markdown(
            """
            skill GroundingSkill: "Grounding Skill"
                purpose: "Ground the current claim before you write."

            skills SharedSkills: "Shared Skills"
                "Keep {{self:can_run.grounding}} available before you act."

                can_run: "Can Run"
                    skill grounding: GroundingSkill

            workflow ReviewRules: "Review Rules"
                "Run {{self:gates.build.check_build_honesty}} before you review anything else."

                gates: "Gates"
                    build: "Build"
                        check_build_honesty: "Check Build Honesty"
                            "Compare the current build to the plan before you accept it."

            workflow WorkflowRoot: "Workflow Root"
                use shared: ReviewRules

                skills: SharedSkills

                review_sequence: "Review Sequence"
                    self:shared.title
                    self:skills.title
                    self:shared.gates.build.check_build_honesty
                    self:skills.can_run.grounding
                    "Run {{self:shared.gates.build.check_build_honesty}} with {{self:skills.can_run.grounding}}."

            agent SelfAddressableRootsDemo:
                role: "Keep self-addressed and workflow-owned nested paths stable."

                workflow: WorkflowRoot
            """,
            agent_name="SelfAddressableRootsDemo",
        )

        self.assertIn("Keep self-addressed and workflow-owned nested paths stable.", rendered)
        self.assertIn("Run Check Build Honesty before you review anything else.", rendered)
        self.assertIn("Keep Grounding Skill available before you act.", rendered)
        self.assertIn("- Review Rules", rendered)
        self.assertIn("- Shared Skills", rendered)
        self.assertIn("- Check Build Honesty", rendered)
        self.assertIn("- Grounding Skill", rendered)
        self.assertIn("Run Check Build Honesty with Grounding Skill.", rendered)

    def test_self_refs_render_across_input_output_and_route_guard_surfaces(self) -> None:
        rendered = self._render_agent_markdown(
            """
            input RouteFacts: "Route Facts"
                source: Prompt
                shape: JsonObject
                requirement: Required

            input DemoInput: "Demo Input"
                source: File
                    path: self:title
                shape: MarkdownDocument
                requirement: Required

            output BaseRouteNote: "Base Route Note"
                target: TurnResponse
                shape: MarkdownDocument
                requirement: Required

                details: "Details"
                    summary: "Summary"
                        "Keep the route record honest."

                summary_copy: self:details.summary
                guarded_summary: self:details.summary when route.exists

            output RouteNote[BaseRouteNote]: "Route Note"
                inherit {target, shape, requirement, details, guarded_summary}
                override summary_copy: self:details

            agent ReviewLead:
                role: "Review the route repair."

            route_only RouteRepair: "Route Repair"
                facts: RouteFacts
                current none
                handoff_output: RouteNote
                routes:
                    else -> ReviewLead

            agent Demo:
                role: "Keep self-addressed output and input refs honest."
                workflow: RouteRepair
                inputs: "Inputs"
                    DemoInput
                    RouteFacts
                outputs: "Outputs"
                    RouteNote
            """,
            agent_name="Demo",
        )

        self.assertIn("- Path: Demo Input", rendered)
        self.assertIn("- Summary Copy: Details", rendered)
        self.assertIn("#### Guarded Summary", rendered)
        self.assertIn("Show this only when a routed owner exists.", rendered)
        self.assertIn("\nSummary\n", rendered)
