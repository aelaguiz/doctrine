from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class SkillRenderingTests(unittest.TestCase):
    def _compile_agent(
        self,
        source: str,
        *,
        agent_name: str,
        extra_files: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            for rel_path, contents in (extra_files or {}).items():
                target_path = root / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(textwrap.dedent(contents), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def test_required_skill_renders_compact_fields_and_titleless_lists(self) -> None:
        agent = self._compile_agent(
            """
            skill RepoSearch: "repo-search"
                purpose: "Find the right repo surface for the current job."

                use_when: "Use When"
                    bullets cases:
                        "Use this when the job still needs the right repo entrypoint."
                        "Narrow the task before you search if the request is still broad."

            agent Demo:
                role: "Use the skill."
                skills: "Skills"
                    can_run: "Can Run"
                        skill repo_search: RepoSearch
                            requirement: Required
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### repo-search", rendered)
        self.assertIn("_Required skill_", rendered)
        self.assertIn("**Purpose**", rendered)
        self.assertNotIn("##### Purpose", rendered)
        self.assertIn("**Use When**", rendered)
        self.assertNotIn("##### Use When", rendered)
        self.assertIn(
            "- Use this when the job still needs the right repo entrypoint.",
            rendered,
        )
        self.assertIn(
            "- Narrow the task before you search if the request is still broad.",
            rendered,
        )
        self.assertNotIn("### Cases", rendered)

    def test_advisory_skill_omits_required_marker_and_keeps_reason_compact(self) -> None:
        agent = self._compile_agent(
            """
            skill FindSkills: "find-skills"
                purpose: "Find the best matching repo skill for the current job."

            agent Demo:
                role: "Use the skill."
                skills: "Skills"
                    discover_with: "Discover With"
                        skill find_skills: FindSkills
                            requirement: Advisory
                            reason: "Use this when the job needs skill discovery before execution."
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("#### find-skills", rendered)
        self.assertNotIn("_Required skill_", rendered)
        self.assertIn("**Reason**", rendered)
        self.assertNotIn("##### Reason", rendered)
        self.assertIn(
            "Use this when the job needs skill discovery before execution.",
            rendered,
        )

    def test_skill_reference_readable_blocks_stay_as_blocks(self) -> None:
        agent = self._compile_agent(
            """
            skill GroundingSkill: "Grounding Skill"
                purpose: "Ground the current claim before you write."

            agent Demo:
                role: "Use the skill."
                skills: "Skills"
                    can_run: "Can Run"
                        skill grounding: GroundingSkill
                            callout usage_note: "Usage Note"
                                kind: note
                                "Use this before you summarize evidence."
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("**Purpose**", rendered)
        self.assertIn("> **NOTE — Usage Note**", rendered)
        self.assertIn("> Use this before you summarize evidence.", rendered)

    def test_skill_field_interpolation_stays_live(self) -> None:
        agent = self._compile_agent(
            """
            input CurrentPlan: "Current Plan"
                source: File
                    path: "track_root/current-plan.md"
                shape: MarkdownDocument
                requirement: Required

            agent ProjectLead:
                role: "Project Lead"

            skill GroundingSkill: "Grounding Skill"
                purpose: "Ground new claims against {{CurrentPlan}} before you write."

            agent Demo:
                role: "Use the skill."
                skills: "Skills"
                    can_run: "Can Run"
                        skill grounding: GroundingSkill
                            reason: "Ask {{ProjectLead}} for an owner decision only when the plan truly needs one."
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("Ground new claims against Current Plan before you write.", rendered)
        self.assertIn("Ask ProjectLead for an owner decision only when the plan truly needs one.", rendered)

    def test_workflow_owned_skills_keep_outer_heading_depth(self) -> None:
        agent = self._compile_agent(
            """
            skill FindSkills: "find-skills"
                purpose: "Find the right repo skill before you guess."

            workflow RoleHome: "Role Home"
                start_here: "Start Here"
                    "Read the current packet before you act."

                skills: "Skills"
                    can_run: "Can Run"
                        skill find_skills: FindSkills
                            reason: "Use this when the job needs skill discovery before execution."

            agent Demo:
                role: "Use the workflow-owned skills block."
                role_home: RoleHome
            """,
            agent_name="Demo",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Role Home", rendered)
        self.assertIn("### Skills", rendered)
        self.assertIn("#### Can Run", rendered)
        self.assertIn("##### find-skills", rendered)
        self.assertIn("**Purpose**", rendered)
        self.assertIn("**Reason**", rendered)


if __name__ == "__main__":
    unittest.main()
