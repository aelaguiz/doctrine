from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

import doctrine.compiler as compiler_api
from doctrine.compiler import CompilationSession
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


if __name__ == "__main__":
    unittest.main()
