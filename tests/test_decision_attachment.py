from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class DecisionAttachmentTests(unittest.TestCase):
    def _compile_agent(self, source: str, *, agent_name: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
            prompt = parse_file(prompt_path)
            return CompilationSession(prompt).compile_agent(agent_name)

    def _compile_error(self, source: str, *, agent_name: str) -> CompileError:
        with self.assertRaises(CompileError) as ctx:
            self._compile_agent(source, agent_name=agent_name)
        return ctx.exception

    def test_agent_can_attach_multiple_distinct_decisions(self) -> None:
        agent = self._compile_agent(
            """
            decision PlayableStrategyChoice: "Playable Strategy Choice"
                candidates minimum 3
                rank required
                rejects required
                winner required
                rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}

            decision RepChoice: "Rep Choice"
                candidate_pool required
                kept required
                rejected required
                sequencing_proof required
                winner_reasons required

            agent MultiDecisionDemo:
                role: "Follow {{PlayableStrategyChoice:title}} and {{RepChoice:title}} before you lock the plan."
                workflow: "Choose"
                    "Use both attached decision scaffolds before you freeze the route and reps."
                decision: PlayableStrategyChoice
                decision: RepChoice
            """,
            agent_name="MultiDecisionDemo",
        )

        rendered = render_markdown(agent)
        self.assertIn("## Playable Strategy Choice", rendered)
        self.assertIn("## Rep Choice", rendered)
        self.assertIn(
            "Rank by Teaching Fit, Product Reality, Capstone Coherence, and Downstream Preservability.",
            rendered,
        )
        self.assertIn("You must explain why the winner won.", rendered)
        self.assertLess(rendered.index("## Playable Strategy Choice"), rendered.index("## Rep Choice"))

    def test_duplicate_decision_attachment_still_fails_loudly(self) -> None:
        error = self._compile_error(
            """
            decision PlayableStrategyChoice: "Playable Strategy Choice"
                candidates minimum 3
                rank required
                rejects required
                winner required
                rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}

            agent InvalidDuplicateDecisionRefDemo:
                role: "Repeat the same decision attachment."
                workflow: "Choose"
                    "Repeat the same decision attachment."
                decision: PlayableStrategyChoice
                decision: PlayableStrategyChoice
            """,
            agent_name="InvalidDuplicateDecisionRefDemo",
        )

        self.assertEqual(error.code, "E204")
        self.assertIn("Duplicate typed field", str(error))
        self.assertIn("decision:PlayableStrategyChoice", str(error))
