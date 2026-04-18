from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine._compiler.indexing import (
    build_indexed_flow,
    discover_flow_members,
    resolve_flow_entrypoint,
)
from doctrine.diagnostics import CompileError, ParseError
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown


class FlowNamespaceSurfaceTests(unittest.TestCase):
    def test_exported_declaration_is_unwrapped_and_recorded(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                export workflow SharedPlan: "Shared Plan"
                    "Do the shared thing."

                workflow LocalPlan: "Local Plan"
                    "Do the local thing."
                """
            )
        )

        self.assertEqual(prompt.exported_names, ("SharedPlan",))
        self.assertEqual(len(prompt.declarations), 2)
        self.assertIsInstance(prompt.declarations[0], model.WorkflowDecl)
        self.assertEqual(prompt.declarations[0].name, "SharedPlan")
        self.assertEqual(prompt.declarations[1].name, "LocalPlan")

    def test_relative_import_syntax_is_rejected(self) -> None:
        with self.assertRaises(ParseError):
            parse_text("import .shared.workflow\n")


class FlowNamespaceDiscoveryTests(unittest.TestCase):
    def test_resolve_flow_entrypoint_prefers_nearest_boundary_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            nested_flow_root = flow_root / "nested_skill"
            nested_source = nested_flow_root / "steps" / "draft.prompt"
            nested_source.parent.mkdir(parents=True)
            (flow_root / "AGENTS.prompt").write_text(
                'agent Writer:\n    role: "Own the draft."\n',
                encoding="utf-8",
            )
            (nested_flow_root / "SKILL.prompt").write_text(
                'skill package NestedSkill: "Nested Skill"\n    "Keep nested skills separate."\n',
                encoding="utf-8",
            )
            nested_source.write_text(
                'workflow DraftStep: "Draft Step"\n    "Write the draft."\n',
                encoding="utf-8",
            )

            entrypoint = resolve_flow_entrypoint(nested_source, prompt_root=prompts_root)

            self.assertEqual(entrypoint, (nested_flow_root / "SKILL.prompt").resolve())

    def test_discover_flow_members_skips_nested_hidden_backup_and_symlink_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            flow_root = Path(tmp_dir) / "writer_home"
            nested_flow_root = flow_root / "nested_flow"
            hidden_dir = flow_root / ".hidden"
            docs_dir = flow_root / "docs"
            flow_root.mkdir(parents=True)
            nested_flow_root.mkdir()
            hidden_dir.mkdir()
            docs_dir.mkdir()

            entrypoint = flow_root / "AGENTS.prompt"
            writer = flow_root / "writer.prompt"
            backup = docs_dir / "draft.prompt.bak"
            tilde_backup = docs_dir / "draft.prompt~"
            hidden_prompt = hidden_dir / "hidden.prompt"
            nested_entrypoint = nested_flow_root / "AGENTS.prompt"
            nested_prompt = nested_flow_root / "critic.prompt"

            entrypoint.write_text('agent Writer:\n    role: "Own the flow."\n', encoding="utf-8")
            writer.write_text('workflow Draft: "Draft"\n    "Write the draft."\n', encoding="utf-8")
            backup.write_text("", encoding="utf-8")
            tilde_backup.write_text("", encoding="utf-8")
            hidden_prompt.write_text("", encoding="utf-8")
            nested_entrypoint.write_text(
                'agent Nested:\n    role: "Own the nested flow."\n',
                encoding="utf-8",
            )
            nested_prompt.write_text(
                'workflow Critic: "Critic"\n    "Review the draft."\n',
                encoding="utf-8",
            )

            symlink_path = docs_dir / "linked.prompt"
            try:
                os.symlink(writer, symlink_path)
            except OSError:
                symlink_path = None

            members = discover_flow_members(flow_root)

            self.assertEqual(
                members,
                (
                    entrypoint.resolve(),
                    writer.resolve(),
                ),
            )
            if symlink_path is not None:
                self.assertNotIn(symlink_path, members)

    def test_build_indexed_flow_captures_boundary_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            member = flow_root / "writer.prompt"
            entrypoint.write_text('agent Writer:\n    role: "Own the flow."\n', encoding="utf-8")
            member.write_text('workflow Draft: "Draft"\n    "Write the draft."\n', encoding="utf-8")

            indexed_flow = build_indexed_flow(
                prompt_root=prompts_root,
                entrypoint_path=entrypoint,
            )

            self.assertEqual(indexed_flow.prompt_root, prompts_root)
            self.assertEqual(indexed_flow.flow_root, flow_root.resolve())
            self.assertEqual(indexed_flow.entrypoint_path, entrypoint.resolve())
            self.assertEqual(indexed_flow.boundary_kind, "agent_flow")
            self.assertEqual(
                indexed_flow.member_paths,
                (
                    entrypoint.resolve(),
                    member.resolve(),
                ),
            )

    def test_build_indexed_flow_excludes_peer_soul_prompt_from_agents_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            soul_prompt = flow_root / "SOUL.prompt"
            member = flow_root / "writer.prompt"
            entrypoint.write_text('agent Writer:\n    role: "Own the flow."\n', encoding="utf-8")
            soul_prompt.write_text('agent Writer:\n    role: "Carry the background."\n', encoding="utf-8")
            member.write_text('workflow Draft: "Draft"\n    "Write the draft."\n', encoding="utf-8")

            indexed_flow = build_indexed_flow(
                prompt_root=prompts_root,
                entrypoint_path=entrypoint,
            )

            self.assertEqual(
                indexed_flow.member_paths,
                (
                    entrypoint.resolve(),
                    member.resolve(),
                ),
            )

    def test_resolve_flow_entrypoint_honors_soul_prompt_as_explicit_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            soul_prompt = flow_root / "SOUL.prompt"
            soul_prompt.write_text('agent Writer:\n    role: "Carry the background."\n', encoding="utf-8")

            entrypoint = resolve_flow_entrypoint(soul_prompt, prompt_root=prompts_root)

            self.assertEqual(entrypoint, soul_prompt.resolve())

    def test_session_roots_itself_in_one_merged_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            writer = flow_root / "writer.prompt"
            critic = flow_root / "critic.prompt"
            entrypoint.write_text(
                'agent Home:\n    role: "Own the flow."\n',
                encoding="utf-8",
            )
            writer.write_text(
                'agent Writer:\n    role: "Write the draft."\n',
                encoding="utf-8",
            )
            critic.write_text(
                'workflow ReviewDraft: "Review Draft"\n    "Check the draft."\n',
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(writer))

            self.assertEqual(session.root_flow.entrypoint_path, entrypoint.resolve())
            self.assertEqual(set(session.root_flow.agents_by_name), {"Home", "Writer"})
            self.assertIn("ReviewDraft", session.root_flow.workflows_by_name)
            writer_decl = session.root_flow.agents_by_name["Writer"]
            owner_unit = session.root_flow.declaration_owner_units_by_id[id(writer_decl)]
            self.assertEqual(owner_unit.prompt_file.source_path, writer.resolve())

    def test_bare_workflow_ref_resolves_across_one_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            shared_workflow = flow_root / "shared.prompt"
            entrypoint.write_text(
                textwrap.dedent(
                    """\
                    agent Writer:
                        role: "Own the draft."
                        workflow: DraftStep
                    """
                ),
                encoding="utf-8",
            )
            shared_workflow.write_text(
                textwrap.dedent(
                    """\
                    workflow DraftStep: "Draft Step"
                        "Write the draft."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(entrypoint))
            rendered = render_markdown(session.compile_agent("Writer"))

            self.assertIn("## Draft Step", rendered)

    def test_review_contract_refs_resolve_across_one_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "review_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            shared_artifacts = flow_root / "shared.prompt"
            entrypoint.write_text(
                textwrap.dedent(
                    """\
                    workflow DraftReviewContract: "Draft Review Contract"
                        completeness: "Completeness"
                            "Check the draft."

                    agent ReviewLead:
                        role: "Own accepted follow-up."
                        workflow: "Follow Up"
                            "Carry the accepted draft forward."

                    agent DraftAuthor:
                        role: "Fix requested changes."
                        workflow: "Revise"
                            "Revise the draft."

                    review DraftReview: "Draft Review"
                        subject: DraftSpec
                        contract: DraftReviewContract
                        comment_output: DraftReviewComment

                        fields:
                            verdict
                            reviewed_artifact
                            analysis: analysis_performed
                            readback: output_contents_that_matter
                            current_artifact
                            failing_gates: failure_detail.failing_gates
                            next_owner

                        contract_checks: "Contract Checks"
                            accept "The draft passes review." when contract.passes

                        on_accept: "If Accepted"
                            current artifact DraftSpec via DraftReviewComment.current_artifact
                            route "Accepted draft returns to ReviewLead." -> ReviewLead

                        on_reject: "If Rejected"
                            current artifact DraftSpec via DraftReviewComment.current_artifact
                            route "Rejected draft returns to DraftAuthor." -> DraftAuthor

                    agent ReviewHome:
                        role: "Run the review."
                        review: DraftReview
                        inputs: "Inputs"
                            DraftSpec
                        outputs: "Outputs"
                            DraftReviewComment
                    """
                ),
                encoding="utf-8",
            )
            shared_artifacts.write_text(
                textwrap.dedent(
                    """\
                    input DraftSpec: "Draft Spec"
                        source: File
                            path: "unit_root/DRAFT_SPEC.md"
                        shape: MarkdownDocument
                        requirement: Required

                    output DraftReviewComment: "Draft Review Comment"
                        target: TurnResponse
                        shape: Comment
                        requirement: Required

                        verdict: "Verdict"
                            "Say whether the review accepted the draft or requested changes."

                        reviewed_artifact: "Reviewed Artifact"
                            "Name the reviewed artifact this review judged."

                        analysis_performed: "Analysis Performed"
                            "Summarize the review analysis that led to the verdict."

                        output_contents_that_matter: "Output Contents That Matter"
                            "Summarize the parts of the draft the next owner must read first."

                        current_artifact: "Current Artifact"
                            "Name the artifact that remains current after review."

                        next_owner: "Next Owner"
                            "Name the next owner, including {{ReviewLead}} when the draft is accepted and {{DraftAuthor}} when the draft is rejected."

                        failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                            failing_gates: "Failing Gates"
                                "Name the failing review gates in authored order."

                        trust_surface:
                            current_artifact
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(entrypoint))
            rendered = render_markdown(session.compile_agent("ReviewHome"))

            self.assertIn("## Draft Review", rendered)
            self.assertIn("Draft Review Comment", rendered)
            self.assertIn("Current Artifact", rendered)

    def test_sibling_declaration_collisions_fail_loud(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prompts_root = Path(tmp_dir) / "prompts"
            flow_root = prompts_root / "writer_home"
            flow_root.mkdir(parents=True)
            entrypoint = flow_root / "AGENTS.prompt"
            alpha = flow_root / "alpha.prompt"
            beta = flow_root / "beta.prompt"
            entrypoint.write_text(
                'agent Writer:\n    role: "Own the draft."\n',
                encoding="utf-8",
            )
            alpha.write_text(
                'workflow DraftStep: "Draft Step"\n    "Write the draft."\n',
                encoding="utf-8",
            )
            beta.write_text(
                'workflow DraftStep: "Draft Step"\n    "Write the backup draft."\n',
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(entrypoint))

            error = ctx.exception
            self.assertEqual(error.diagnostic.code, "E316")
            self.assertEqual(error.diagnostic.location.path, beta.resolve())
            self.assertEqual(error.diagnostic.location.line, 1)
            self.assertEqual(len(error.diagnostic.related), 1)
            self.assertEqual(error.diagnostic.related[0].location.path, alpha.resolve())
            self.assertEqual(error.diagnostic.related[0].location.line, 1)
            self.assertIn("Sibling declaration collision", str(error))


if __name__ == "__main__":
    unittest.main()
