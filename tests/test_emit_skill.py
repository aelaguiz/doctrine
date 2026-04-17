from __future__ import annotations

import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.diagnostics import CompileError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_skill import emit_target_skill


class EmitSkillTests(unittest.TestCase):
    ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

    def test_emit_skill_emits_doctrine_agent_linter_bundle_without_scripts(self) -> None:
        # This protects the first-party source bundle shape that maintainers
        # sync into the public install tree. The emitted tree must stay
        # complete and script-free.
        repo_root = Path(__file__).resolve().parents[1]
        target = load_emit_targets(repo_root / "pyproject.toml")["doctrine_agent_linter_skill"]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir).resolve()
            emitted = emit_target_skill(target, output_dir_override=output_dir)

            expected_paths = (
                output_dir / "SKILL.md",
                output_dir / "agents" / "openai.yaml",
                output_dir / "references" / "audit-method.md",
                output_dir / "references" / "error-handling.md",
                output_dir / "references" / "examples.md",
                output_dir / "references" / "finding-catalog.md",
                output_dir / "references" / "install.md",
                output_dir / "references" / "product-boundary.md",
                output_dir / "references" / "report-contract.md",
            )

            self.assertCountEqual(emitted, expected_paths)
            for expected_path in expected_paths:
                self.assertTrue(expected_path.is_file(), expected_path)

            skill_markdown = (output_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("# Doctrine Agent Linter", skill_markdown)
            self.assertIn("Audit Doctrine agent authoring thoughtfully.", skill_markdown)
            self.assertIn("This skill is for human review reports.", skill_markdown)
            self.assertFalse((output_dir / "scripts").exists())
            self.assertFalse((output_dir / "schemas").exists())

    def test_public_curated_tree_matches_public_emit_target(self) -> None:
        # This protects the checked-in `npx skills` install surface. The public
        # curated tree must match fresh Doctrine emit output exactly.
        repo_root = Path(__file__).resolve().parents[1]
        target = load_emit_targets(repo_root / "pyproject.toml")[
            "doctrine_agent_linter_public_skill"
        ]
        expected_root = repo_root / "skills" / ".curated" / "agent-linter"
        self.assertTrue(expected_root.is_dir(), expected_root)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir).resolve()
            emit_target_skill(target, output_dir_override=output_dir)

            expected_files = sorted(
                path.relative_to(expected_root)
                for path in expected_root.rglob("*")
                if path.is_file()
            )
            emitted_files = sorted(
                path.relative_to(output_dir)
                for path in output_dir.rglob("*")
                if path.is_file()
            )

            self.assertEqual(emitted_files, expected_files)
            for relative_path in expected_files:
                self.assertEqual(
                    (output_dir / relative_path).read_bytes(),
                    (expected_root / relative_path).read_bytes(),
                    relative_path.as_posix(),
                )

    def test_emit_skill_emits_doctrine_learn_bundle_without_scripts(self) -> None:
        # This protects the first-party teaching bundle shape. The emitted
        # tree must stay complete and script-free across all twelve
        # references.
        repo_root = Path(__file__).resolve().parents[1]
        target = load_emit_targets(repo_root / "pyproject.toml")["doctrine_learn_skill"]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir).resolve()
            emitted = emit_target_skill(target, output_dir_override=output_dir)

            expected_paths = (
                output_dir / "SKILL.md",
                output_dir / "agents" / "openai.yaml",
                output_dir / "references" / "agents-and-workflows.md",
                output_dir / "references" / "authoring-patterns.md",
                output_dir / "references" / "documents-and-tables.md",
                output_dir / "references" / "emit-targets.md",
                output_dir / "references" / "examples-ladder.md",
                output_dir / "references" / "imports-and-refs.md",
                output_dir / "references" / "language-overview.md",
                output_dir / "references" / "outputs-and-schemas.md",
                output_dir / "references" / "principles.md",
                output_dir / "references" / "reviews.md",
                output_dir / "references" / "skills-and-packages.md",
                output_dir / "references" / "verify-and-ship.md",
            )

            self.assertCountEqual(emitted, expected_paths)
            for expected_path in expected_paths:
                self.assertTrue(expected_path.is_file(), expected_path)

            skill_markdown = (output_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("# Doctrine Learn", skill_markdown)
            self.assertIn("Teach Doctrine authoring end-to-end.", skill_markdown)
            self.assertFalse((output_dir / "scripts").exists())
            self.assertFalse((output_dir / "schemas").exists())

    def test_public_curated_tree_matches_doctrine_learn_public_emit_target(self) -> None:
        # This protects the checked-in `npx skills` install surface for the
        # Doctrine Learn teaching skill. The public curated tree must match
        # fresh Doctrine emit output exactly.
        repo_root = Path(__file__).resolve().parents[1]
        target = load_emit_targets(repo_root / "pyproject.toml")[
            "doctrine_learn_public_skill"
        ]
        expected_root = repo_root / "skills" / ".curated" / "doctrine-learn"
        self.assertTrue(expected_root.is_dir(), expected_root)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir).resolve()
            emit_target_skill(target, output_dir_override=output_dir)

            expected_files = sorted(
                path.relative_to(expected_root)
                for path in expected_root.rglob("*")
                if path.is_file()
            )
            emitted_files = sorted(
                path.relative_to(output_dir)
                for path in output_dir.rglob("*")
                if path.is_file()
            )

            self.assertEqual(emitted_files, expected_files)
            for relative_path in expected_files:
                self.assertEqual(
                    (output_dir / relative_path).read_bytes(),
                    (expected_root / relative_path).read_bytes(),
                    relative_path.as_posix(),
                )

    def test_pinned_skills_cli_lists_only_public_first_party_skills(self) -> None:
        # This protects the repo-root discovery story behind
        # `npx skills add .`. Users should see the real first-party skills,
        # not the example build refs.
        repo_root = Path(__file__).resolve().parents[1]
        skills_cli = self._skills_cli(repo_root)
        result = subprocess.run(
            [str(skills_cli), "add", ".", "--list"],
            cwd=repo_root,
            env=self._skills_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        output = self._strip_ansi(result.stdout + result.stderr)
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("agent-linter", output)
        self.assertIn("doctrine-learn", output)
        self.assertNotIn("bundled-agents-package", output)
        self.assertNotIn("release-compendium", output)
        self.assertNotIn("plugin-metadata-package", output)
        self.assertNotIn("greeting-skill", output)

    def test_pinned_skills_cli_installs_agent_linter_into_temp_codex_home(self) -> None:
        # This proves the local repo can act as a real `skills` source and
        # install the public skill for Codex through the normal universal
        # skills path that the `skills` CLI owns.
        repo_root = Path(__file__).resolve().parents[1]
        skills_cli = self._skills_cli(repo_root)

        with tempfile.TemporaryDirectory() as temp_dir:
            home_dir = Path(temp_dir).resolve()
            env = self._skills_env()
            env["HOME"] = str(home_dir)
            result = subprocess.run(
                [str(skills_cli), "add", ".", "-g", "-a", "codex", "-y"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            output = self._strip_ansi(result.stdout + result.stderr)
            self.assertEqual(result.returncode, 0, output)
            installed_root = home_dir / ".agents" / "skills" / "agent-linter"
            self.assertTrue((installed_root / "SKILL.md").is_file(), output)
            self.assertTrue((installed_root / "agents" / "openai.yaml").is_file(), output)
            self.assertTrue(
                (installed_root / "references" / "install.md").is_file(),
                output,
            )

    def test_emit_skill_keeps_runtime_metadata_in_agents_tree(self) -> None:
        # This protects the real skill-package shape where bundled agent prompts
        # and runtime metadata live in the same `agents/` tree. Users need both
        # files after emit, not just the compiled markdown companions.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "mixed_agents"
            (prompts / "agents").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package MixedAgents: "Mixed Agents"
                        metadata:
                            name: "mixed-agents"
                        "Keep runtime metadata and bundled agent prompts in one `agents/` tree."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "agents" / "reviewer.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the package."
                    """
                ),
                encoding="utf-8",
            )
            runtime_metadata = textwrap.dedent(
                """\
                interface:
                  display_name: Mixed Agents
                default_prompt: SKILL.md
                """
            )
            (prompts / "agents" / "openai.yaml").write_text(
                runtime_metadata,
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/mixed_agents/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target_skill(target)

            skill_path = root / "build" / "skills" / "mixed_agents" / "SKILL.md"
            reviewer_path = root / "build" / "skills" / "mixed_agents" / "agents" / "reviewer.md"
            metadata_path = root / "build" / "skills" / "mixed_agents" / "agents" / "openai.yaml"
            self.assertEqual(emitted[0], skill_path)
            self.assertCountEqual(emitted[1:], (reviewer_path, metadata_path))
            self.assertTrue(skill_path.is_file())
            self.assertFalse((skill_path.parent / "SKILL.contract.json").exists())
            self.assertTrue(reviewer_path.is_file())
            self.assertTrue(metadata_path.is_file())
            self.assertEqual(metadata_path.read_text(encoding="utf-8"), runtime_metadata)

    def test_emit_skill_emits_document_companions_from_emit_block(self) -> None:
        # This protects the new first-class package artifact map. A skill
        # package should emit prompt-authored companion docs from imported
        # `document` declarations while keeping ordinary bundled files and
        # bundled agents working on the same package path.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "emitted_docs"
            (prompts / "refs").mkdir(parents=True)
            (prompts / "agents").mkdir(parents=True)
            (prompts / "scripts").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    from refs.query_patterns import QueryPatterns
                    from refs.qa_guide import QaGuide

                    skill package EmittedDocs: "Emitted Docs"
                        metadata:
                            name: "emitted-docs"
                        emit:
                            "references/query-patterns.md": QueryPatterns
                            "references/qa.md": QaGuide
                        "Keep the root file short."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "refs" / "query_patterns.prompt").write_text(
                textwrap.dedent(
                    """\
                    document QueryPatterns: "Query Patterns"
                        section summary: "Summary"
                            "Pick the right query before you search."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "refs" / "qa_guide.prompt").write_text(
                textwrap.dedent(
                    """\
                    document QaGuide: "QA Guide"
                        section checks: "Checks"
                            "Run the package checks before shipping."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "agents" / "reviewer.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the package."
                    """
                ),
                encoding="utf-8",
            )
            runtime_metadata = textwrap.dedent(
                """\
                interface:
                  display_name: Emitted Docs
                default_prompt: SKILL.md
                """
            )
            (prompts / "agents" / "openai.yaml").write_text(
                runtime_metadata,
                encoding="utf-8",
            )
            helper_script = "print('emit docs helper')\n"
            (prompts / "scripts" / "helper.py").write_text(
                helper_script,
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/emitted_docs/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emitted = emit_target_skill(target)

            skill_path = root / "build" / "skills" / "emitted_docs" / "SKILL.md"
            query_patterns_path = (
                root / "build" / "skills" / "emitted_docs" / "references" / "query-patterns.md"
            )
            qa_path = root / "build" / "skills" / "emitted_docs" / "references" / "qa.md"
            reviewer_path = root / "build" / "skills" / "emitted_docs" / "agents" / "reviewer.md"
            metadata_path = root / "build" / "skills" / "emitted_docs" / "agents" / "openai.yaml"
            helper_path = root / "build" / "skills" / "emitted_docs" / "scripts" / "helper.py"

            self.assertEqual(emitted[0], skill_path)
            self.assertCountEqual(
                emitted[1:],
                (
                    query_patterns_path,
                    qa_path,
                    reviewer_path,
                    metadata_path,
                    helper_path,
                ),
            )
            self.assertFalse((skill_path.parent / "SKILL.contract.json").exists())
            self.assertEqual(
                query_patterns_path.read_text(encoding="utf-8"),
                "# Query Patterns\n\n## Summary\n\nPick the right query before you search.\n",
            )
            self.assertEqual(
                qa_path.read_text(encoding="utf-8"),
                "# QA Guide\n\n## Checks\n\nRun the package checks before shipping.\n",
            )
            self.assertEqual(metadata_path.read_text(encoding="utf-8"), runtime_metadata)
            self.assertEqual(helper_path.read_text(encoding="utf-8"), helper_script)

    def test_emit_skill_preserves_binary_assets_byte_for_byte(self) -> None:
        # This protects the user-visible outcome where skill packages can ship
        # real binary assets. The emitted file must keep the exact bytes so the
        # asset still opens and renders correctly downstream.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "binary_assets"
            (prompts / "assets").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package BinaryAssets: "Binary Assets"
                        metadata:
                            name: "binary-assets"
                        "Keep bundled binary assets byte-for-byte."
                    """
                ),
                encoding="utf-8",
            )
            asset_bytes = bytes.fromhex(
                "89504e470d0a1a0a"
                "0000000d4948445200000001000000010802000000907753de"
                "0000000c4944415408d763f8ffff3f0005fe02fea7e58f7f"
                "0000000049454e44ae426082"
            )
            (prompts / "assets" / "icon.png").write_bytes(asset_bytes)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/binary_assets/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            target = load_emit_targets(pyproject)["demo"]
            emit_target_skill(target)

            emitted_path = root / "build" / "skills" / "binary_assets" / "assets" / "icon.png"
            self.assertTrue(emitted_path.is_file())
            self.assertEqual(emitted_path.read_bytes(), asset_bytes)

    def test_emit_skill_reserves_contract_path_for_host_bound_bundled_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "reserved_path"
            prompts.mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package ReservedPath: "Reserved Path"
                        metadata:
                            name: "reserved-path"
                        host_contract:
                            final_output final_response: "Final Response"
                        "Emit through {{host:final_response}}."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "SKILL.contract.json").write_text("{}", encoding="utf-8")
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/reserved_path/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                emit_target_skill(load_emit_targets(pyproject)["demo"])

        self.assertIn("SKILL.contract.json", str(ctx.exception))

    def test_emit_skill_reserves_contract_path_for_host_bound_emitted_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "reserved_doc_path"
            (prompts / "refs").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    from refs.query_patterns import QueryPatterns

                    skill package ReservedDocPath: "Reserved Doc Path"
                        metadata:
                            name: "reserved-doc-path"
                        emit:
                            "SKILL.contract.json": QueryPatterns
                        host_contract:
                            document section_map: "Section Map"
                        "Read {{host:section_map.title}}."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "refs" / "query_patterns.prompt").write_text(
                textwrap.dedent(
                    """\
                    document QueryPatterns: "Query Patterns"
                        section summary: "Summary"
                            "Keep the host path stable."
                    """
                ),
                encoding="utf-8",
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/skills/reserved_doc_path/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                emit_target_skill(load_emit_targets(pyproject)["demo"])

        self.assertIn("SKILL.contract.json", str(ctx.exception))

    def _skills_cli(self, repo_root: Path) -> Path:
        cli_name = "skills.cmd" if os.name == "nt" else "skills"
        cli_path = repo_root / "node_modules" / ".bin" / cli_name
        if not cli_path.exists():
            self.skipTest("Run npm ci first to install the pinned `skills` CLI.")
        return cli_path

    def _skills_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["CI"] = "1"
        env["NO_COLOR"] = "1"
        env["FORCE_COLOR"] = "0"
        env["TERM"] = "dumb"
        return env

    def _strip_ansi(self, text: str) -> str:
        return self.ANSI_RE.sub("", text)


if __name__ == "__main__":
    unittest.main()
