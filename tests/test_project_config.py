from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.emit_common import load_emit_targets
from doctrine.project_config import ProjectConfigError, load_project_config


class ProjectConfigTests(unittest.TestCase):
    def test_compile_config_resolves_additional_prompt_roots_relative_to_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shared_prompts = root / "shared" / "prompts"
            shared_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts"]
                    """
                )
            )

            project_config = load_project_config(pyproject)
            compile_config = project_config.resolve_compile_config()

            self.assertEqual(
                compile_config.additional_prompt_roots,
                (shared_prompts.resolve(),),
            )

    def test_duplicate_configured_prompt_roots_fail_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shared_prompts = root / "shared" / "prompts"
            shared_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts", "./shared/prompts"]
                    """
                )
            )

            project_config = load_project_config(pyproject)
            with self.assertRaises(ProjectConfigError) as exc_info:
                project_config.resolve_compile_config()

            self.assertIn("Duplicate configured prompts root", str(exc_info.exception))

    def test_emit_targets_still_load_after_shared_project_config_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            entrypoint = prompts / "AGENTS.prompt"
            entrypoint.write_text(
                """agent Demo:\n    role: "Own the emitted surface."\n"""
            )
            shared_prompts = root / "shared" / "prompts"
            shared_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts"]

                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/AGENTS.prompt"
                    output_dir = "build"
                    """
                )
            )

            targets = load_emit_targets(pyproject)

            self.assertIn("demo", targets)
            self.assertEqual(targets["demo"].project_config.path, pyproject.resolve())


if __name__ == "__main__":
    unittest.main()
