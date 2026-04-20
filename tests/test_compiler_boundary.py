from __future__ import annotations

import ast
import tempfile
import textwrap
import unittest
from pathlib import Path

import doctrine.compiler as compiler_api
from doctrine.compiler import CompilationSession
from doctrine.emit_common import collect_runtime_emit_roots
from doctrine.parser import parse_file


class CompilerBoundaryTests(unittest.TestCase):
    def test_compile_agents_preserves_requested_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompts" / "AGENTS.prompt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    agent FirstAgent:
                        role: "Own the first reply."
                        workflow: "Reply"
                            "Answer as the first agent."

                    agent SecondAgent:
                        role: "Own the second reply."
                        workflow: "Reply"
                            "Answer as the second agent."
                    """
                ),
                encoding="utf-8",
            )

            prompt = parse_file(prompt_path)
            compiled_agents = CompilationSession(prompt).compile_agents(
                ("SecondAgent", "FirstAgent")
            )

        # Emit callers zip planned output paths against compile_agents(). If this order
        # drifts, the repo can write the wrong contract under the wrong agent path.
        self.assertEqual(
            tuple(agent.name for agent in compiled_agents),
            ("SecondAgent", "FirstAgent"),
        )

    def test_compiler_module_hides_accidental_helper_exports(self) -> None:
        # doctrine.compiler is the stable compile boundary. Helper imports must not leak
        # through it, or downstream callers can bind to internals that were never meant
        # to stay stable across compiler refactors.
        self.assertIn("CompilationSession", compiler_api.__all__)
        self.assertIn("CompiledAgent", compiler_api.__all__)
        self.assertIn("compile_prompt", compiler_api.__all__)

        leaked_names = (
            "Path",
            "ThreadPoolExecutor",
            "TypeAlias",
            "dataclass",
            "json",
            "model",
            "parse_file",
            "re",
            "replace",
        )
        for name in leaked_names:
            self.assertNotIn(name, compiler_api.__all__)
            self.assertFalse(hasattr(compiler_api, name), name)

    def test_public_resolved_exports_matches_resolved_types_import_block(self) -> None:
        # `doctrine.compiler` re-exports resolved_types names via two lists that
        # must agree: the `from doctrine._compiler.resolved_types import (...)`
        # block at module top, and `_PUBLIC_RESOLVED_EXPORTS` (which `__all__`
        # splats). Drift between them silently changes the public boundary —
        # an imported-but-unexported name becomes an accidental private leak,
        # and an exported-but-unimported name is an AttributeError on access.
        # A within-list duplicate does not change the exported *set* but does
        # indicate a hand-edit slip that will drift further over time. This
        # test is the single safeguard: parse the source with `ast` so any
        # future edit that breaks the invariant fails loud here.
        source = Path(compiler_api.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported_from_resolved_types: set[str] = set()
        public_resolved_exports: list[str] | None = None
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "doctrine._compiler.resolved_types"
            ):
                imported_from_resolved_types.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "_PUBLIC_RESOLVED_EXPORTS"
                        and isinstance(node.value, ast.List)
                    ):
                        public_resolved_exports = [
                            element.value
                            for element in node.value.elts
                            if isinstance(element, ast.Constant)
                            and isinstance(element.value, str)
                        ]

        self.assertIsNotNone(
            public_resolved_exports,
            "_PUBLIC_RESOLVED_EXPORTS list not found in doctrine/compiler.py",
        )
        duplicates = sorted(
            {
                name
                for name in public_resolved_exports
                if public_resolved_exports.count(name) > 1
            }
        )
        self.assertEqual(duplicates, [], f"duplicate exports: {duplicates}")
        self.assertEqual(
            set(public_resolved_exports),
            imported_from_resolved_types,
            "drift between `from doctrine._compiler.resolved_types import (...)` "
            "and `_PUBLIC_RESOLVED_EXPORTS`",
        )

    def test_compile_agent_from_imported_runtime_package_unit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Own the runtime package."
                        workflow: "Reply"
                            "Reply from the imported package."
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = prompts / "AGENTS.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    import runtime_home

                    agent BuildHandle:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompt_path))
            runtime_root = collect_runtime_emit_roots(session)[1]
            compiled = session.compile_agent_from_unit(
                runtime_root.unit,
                runtime_root.agent_name,
            )

        self.assertEqual(compiled.name, "RuntimeHome")

    def test_compile_agent_from_alias_imported_runtime_package_unit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "runtime_home").mkdir(parents=True)
            (prompts / "runtime_home" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent RuntimeHome:
                        role: "Own the runtime package."
                        workflow: "Reply"
                            "Reply from the imported package."
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = prompts / "AGENTS.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    import runtime_home as runtime_alias

                    agent BuildHandle:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompt_path))
            runtime_root = collect_runtime_emit_roots(session)[1]
            compiled = session.compile_agent_from_unit(
                runtime_root.unit,
                runtime_root.agent_name,
            )

        self.assertEqual(compiled.name, "RuntimeHome")


if __name__ == "__main__":
    unittest.main()
