from __future__ import annotations

import unittest

from doctrine._skill_graph_render.d2 import render_skill_graph_d2
from doctrine._skill_graph_render.markdown import render_flow_registry, render_skill_inventory
from doctrine._skill_graph_render.mermaid import render_skill_graph_mermaid
from tests.test_skill_graph_semantics import _compile_graph


class SkillGraphRenderingTests(unittest.TestCase):
    def test_markdown_tables_escape_authored_delimiters(self) -> None:
        graph = _compile_graph(
            """\
            skill AuthorSkill: "Author | Skill"
                purpose: \"\"\"Own authoring | review.
            Keep rows stable.\"\"\"

            skill ReviewSkill: "Review Skill"
                purpose: "Review."

            stage DraftStage: "Draft Stage"
                owner: AuthorSkill
                intent: "Draft."
                durable_target: "Draft."
                durable_evidence: "Draft."
                advance_condition: "Draft lands."

            stage ReviewStage: "Review Stage"
                owner: ReviewSkill
                intent: "Review."
                durable_target: "Review."
                durable_evidence: "Review."
                advance_condition: "Review lands."

            skill_flow GraphFlow: "Graph Flow"
                start: DraftStage
                edge DraftStage -> ReviewStage:
                    why: "Move draft | review."

            skill_graph Graph: "Graph \\"Render\\" | Audit"
                purpose: "Graph."
                roots:
                    flow GraphFlow
            """
        )

        # Authored prose can use pipes and multiline strings. Graph Markdown
        # tables must keep that text inside one cell instead of changing columns.
        skill_inventory = render_skill_inventory(graph)
        flow_registry = render_flow_registry(graph)
        self.assertIn("Author \\| Skill", skill_inventory)
        self.assertIn("Own authoring \\| review.<br>Keep rows stable.", skill_inventory)
        self.assertIn("Move draft \\| review.", flow_registry)

    def test_diagram_labels_escape_syntax_delimiters(self) -> None:
        graph = _compile_graph(
            """\
            skill AuthorSkill: "Author Skill"
                purpose: "Own authoring."

            stage DraftStage: "Draft | Stage \\"Alpha\\""
                owner: AuthorSkill
                intent: "Draft."
                durable_target: "Draft."
                durable_evidence: "Draft."
                advance_condition: "Draft lands."

            stage ReviewStage: "Review Stage"
                owner: AuthorSkill
                intent: "Review."
                durable_target: "Review."
                durable_evidence: "Review."
                advance_condition: "Review lands."

            skill_flow GraphFlow: "Graph Flow"
                start: DraftStage
                edge DraftStage -> ReviewStage:
                    why: "Move \\"quoted\\" draft | review \\\\ backslash."

            skill_graph Graph: "Graph \\"Render\\" | Audit"
                purpose: "Graph."
                roots:
                    flow GraphFlow
            """
        )

        # D2 and Mermaid use quotes, pipes, and backslashes as syntax. Escaping
        # keeps labels renderable while preserving the author's visible words.
        d2 = render_skill_graph_d2(graph)
        mermaid = render_skill_graph_mermaid(graph)
        self.assertIn(r'title: "Graph \"Render\" | Audit"', d2)
        self.assertIn(r'Move \"quoted\" draft | review \\ backslash.', d2)
        self.assertIn(
            "Draft &#124; Stage &quot;Alpha&quot;<br/>owner: AuthorSkill",
            mermaid,
        )
        self.assertIn(
            "Move &quot;quoted&quot; draft &#124; review &#92; backslash.",
            mermaid,
        )


if __name__ == "__main__":
    unittest.main()
