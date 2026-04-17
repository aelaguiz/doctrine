from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_skill import emit_target_skill
from doctrine.parser import parse_file, parse_text
from doctrine.renderer import render_markdown


class SkillPackageHostBindingTests(unittest.TestCase):
    def test_parser_keeps_package_link_host_contract_and_binds(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                skill DemoSkill: "Demo Skill"
                    purpose: "Run the demo package."
                    package: "demo-package"

                skill package DemoPackage: "Demo Package"
                    host_contract:
                        document section_map: "Section Map"
                        final_output final_response: "Final Response"
                    "Read {{host:section_map.title}}."

                skills DemoSkills: "Skills"
                    skill demo: DemoSkill
                        bind:
                            section_map: SectionMap
                            final_response: final_output
                """
            )
        )

        skill_decl = prompt.declarations[0]
        package_decl = prompt.declarations[1]
        skills_decl = prompt.declarations[2]

        self.assertEqual(skill_decl.package_link.package_id, "demo-package")
        self.assertEqual(package_decl.host_contract[0].family, "document")
        self.assertEqual(package_decl.host_contract[0].key, "section_map")
        self.assertEqual(package_decl.host_contract[1].family, "final_output")
        self.assertEqual(package_decl.host_contract[1].key, "final_response")
        entry = skills_decl.body.items[0]
        self.assertEqual(len(entry.binds), 2)
        self.assertEqual(entry.binds[0].key, "section_map")
        self.assertEqual(entry.binds[1].key, "final_response")

    def test_agent_compile_resolves_package_bindings_from_skill_package_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            package_root = root / "prompts" / "skills" / "demo"
            (package_root / "refs").mkdir(parents=True)
            (package_root / "agents").mkdir(parents=True)
            (package_root / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    from refs.query_patterns import QueryPatterns

                    skill package DemoPackage: "Demo Package"
                        metadata:
                            name: "demo-package"
                        emit:
                            "references/query-patterns.md": QueryPatterns
                        host_contract:
                            document section_map: "Section Map"
                            final_output final_response: "Final Response"
                        "Read {{host:section_map.title}}."
                    """
                ),
                encoding="utf-8",
            )
            (package_root / "refs" / "query_patterns.prompt").write_text(
                textwrap.dedent(
                    """\
                    document QueryPatterns: "Query Patterns"
                        section summary: "Summary"
                            "Use {{host:section_map.title}}."
                    """
                ),
                encoding="utf-8",
            )
            (package_root / "agents" / "reviewer.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the package output."
                        workflow: "Review"
                            output: "Output"
                                host:final_response
                    """
                ),
                encoding="utf-8",
            )
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    document SectionMap: "Section Map"
                        section title: "Title"
                            "Map title."

                    output FinalResponse: "Final Response"
                        target: TurnResponse
                        shape: MarkdownDocument
                        requirement: Required

                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."
                        package: "demo-package"

                    agent Demo:
                        role: "Use the packaged method."
                        outputs: "Outputs"
                            FinalResponse
                        final_output: FinalResponse
                        skills: "Skills"
                            skill demo: DemoSkill
                                bind:
                                    section_map: SectionMap
                                    final_response: final_output
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt"))
            compiled = session.compile_agent("Demo")

        rendered = render_markdown(compiled)
        self.assertIn("### Demo Skill", rendered)
        self.assertIn("Run the demo package.", rendered)
        self.assertNotIn("package:", rendered)
        self.assertNotIn("bind:", rendered)

    def test_agent_compile_fails_when_package_id_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."
                        package: "missing-package"

                    agent Demo:
                        role: "Use the packaged method."
                        skills: "Skills"
                            skill demo: DemoSkill
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt")).compile_agent(
                    "Demo"
                )

        self.assertIn("Missing skill package id", str(ctx.exception))
        self.assertIn("missing-package", str(ctx.exception))

    def test_agent_compile_fails_when_bind_is_used_without_package_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    document SectionMap: "Section Map"
                        section title: "Title"
                            "Map title."

                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."

                    agent Demo:
                        role: "Use the packaged method."
                        skills: "Skills"
                            skill demo: DemoSkill
                                bind:
                                    section_map: SectionMap
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt")).compile_agent(
                    "Demo"
                )

        self.assertIn("uses `bind:`", str(ctx.exception))
        self.assertIn("does not declare `package:`", str(ctx.exception))

    def test_agent_compile_fails_when_visible_package_ids_are_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            packages_root = root / "prompts" / "packages"
            packages_root.mkdir(parents=True)
            (packages_root / "one.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package OnePackage: "One Package"
                        metadata:
                            name: "shared-package"
                        "One."
                    """
                ),
                encoding="utf-8",
            )
            (packages_root / "two.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package TwoPackage: "Two Package"
                        metadata:
                            name: "shared-package"
                        "Two."
                    """
                ),
                encoding="utf-8",
            )
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import packages.one
                    import packages.two

                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."
                        package: "shared-package"

                    agent Demo:
                        role: "Use the packaged method."
                        skills: "Skills"
                            skill demo: DemoSkill
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt")).compile_agent(
                    "Demo"
                )

        self.assertIn("Ambiguous skill package id", str(ctx.exception))
        self.assertIn("shared-package", str(ctx.exception))

    def test_agent_compile_fails_when_required_bind_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            package_root = root / "prompts" / "skills" / "demo"
            package_root.mkdir(parents=True)
            (package_root / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package DemoPackage: "Demo Package"
                        metadata:
                            name: "demo-package"
                        host_contract:
                            final_output final_response: "Final Response"
                        "Emit through {{host:final_response}}."
                    """
                ),
                encoding="utf-8",
            )
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    output FinalResponse: "Final Response"
                        target: TurnResponse
                        shape: MarkdownDocument
                        requirement: Required

                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."
                        package: "demo-package"

                    agent Demo:
                        role: "Use the packaged method."
                        outputs: "Outputs"
                            FinalResponse
                        final_output: FinalResponse
                        skills: "Skills"
                            skill demo: DemoSkill
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt")).compile_agent(
                    "Demo"
                )

        self.assertIn("missing required binds", str(ctx.exception))
        self.assertIn("final_response", str(ctx.exception))

    def test_agent_compile_fails_when_host_path_is_invalid_for_bound_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            package_root = root / "prompts" / "skills" / "demo"
            package_root.mkdir(parents=True)
            (package_root / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package DemoPackage: "Demo Package"
                        metadata:
                            name: "demo-package"
                        host_contract:
                            document section_map: "Section Map"
                        "Read {{host:section_map.missing_child}}."
                    """
                ),
                encoding="utf-8",
            )
            (root / "prompts" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    document SectionMap: "Section Map"
                        section title: "Title"
                            "Map title."

                    skill DemoSkill: "Demo Skill"
                        purpose: "Run the demo package."
                        package: "demo-package"

                    agent Demo:
                        role: "Use the packaged method."
                        skills: "Skills"
                            skill demo: DemoSkill
                                bind:
                                    section_map: SectionMap
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(root / "prompts" / "AGENTS.prompt")).compile_agent(
                    "Demo"
                )

        self.assertIn("Unknown addressable path", str(ctx.exception))
        self.assertIn("missing_child", str(ctx.exception))

    def test_emit_skill_writes_contract_json_for_mixed_tree_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "demo_package"
            (prompts / "refs").mkdir(parents=True)
            (prompts / "agents").mkdir(parents=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    from refs.query_patterns import QueryPatterns

                    skill package DemoPackage: "Demo Package"
                        metadata:
                            name: "demo-package"
                        emit:
                            "references/query-patterns.md": QueryPatterns
                        host_contract:
                            document section_map: "Section Map"
                            final_output final_response: "Final Response"
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
                            "Keep {{host:section_map.title}} stable."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "agents" / "reviewer.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the output."
                        workflow: "Review"
                            output: "Output"
                                host:final_response
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
                    entrypoint = "prompts/skills/demo_package/SKILL.prompt"
                    output_dir = "build"
                    """
                ),
                encoding="utf-8",
            )

            emitted = emit_target_skill(load_emit_targets(pyproject)["demo"])
            contract_path = root / "build" / "skills" / "demo_package" / "SKILL.contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))

        self.assertIn(contract_path, emitted)
        self.assertEqual(payload["package"]["name"], "demo-package")
        self.assertEqual(payload["host_contract"]["section_map"]["family"], "document")
        self.assertEqual(
            payload["artifacts"]["SKILL.md"]["referenced_host_paths"],
            ["section_map.title"],
        )
        self.assertEqual(
            payload["artifacts"]["references/query-patterns.md"]["referenced_host_paths"],
            ["section_map.title"],
        )
        self.assertEqual(
            payload["artifacts"]["agents/reviewer.md"]["referenced_host_paths"],
            ["final_response"],
        )


if __name__ == "__main__":
    unittest.main()
