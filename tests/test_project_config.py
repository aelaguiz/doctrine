from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.diagnostics import EmitError
from doctrine.emit_common import load_emit_targets, resolve_direct_emit_target
from doctrine.project_config import (
    ProjectConfigError,
    ProvidedPromptRoot,
    load_project_config,
)


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
            self.assertEqual(exc_info.exception.path, pyproject.resolve())
            self.assertEqual(exc_info.exception.line, 2)
            self.assertIsNotNone(exc_info.exception.column)

    def test_additional_prompt_roots_type_error_carries_key_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = "shared/prompts"
                    """
                )
            )

            project_config = load_project_config(pyproject)
            with self.assertRaises(ProjectConfigError) as exc_info:
                project_config.resolve_compile_config()

            self.assertIn("additional_prompt_roots must be an array of strings", str(exc_info.exception))
            self.assertEqual(exc_info.exception.path, pyproject.resolve())
            self.assertEqual(exc_info.exception.line, 2)
            self.assertIsNotNone(exc_info.exception.column)

    def test_invalid_configured_prompt_root_carries_array_item_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/not_prompts"]
                    """
                )
            )

            project_config = load_project_config(pyproject)
            with self.assertRaises(ProjectConfigError) as exc_info:
                project_config.resolve_compile_config()

            self.assertIn("Configured additional prompts root", str(exc_info.exception))
            self.assertEqual(exc_info.exception.path, pyproject.resolve())
            self.assertEqual(exc_info.exception.line, 2)
            self.assertIsNotNone(exc_info.exception.column)

    def test_provider_prompt_roots_normalize_as_compile_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            provider_prompts = root / "framework" / "prompts"
            provider_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "doctrine-test"
                    version = "0.0.0"
                    """
                )
            )

            project_config = load_project_config(
                pyproject,
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", provider_prompts),
                ),
            )
            compile_config = project_config.resolve_compile_config()

            self.assertEqual(
                compile_config.provided_prompt_roots,
                (
                    ProvidedPromptRoot(
                        "framework_stdlib",
                        provider_prompts.resolve(),
                    ),
                ),
            )

    def test_invalid_provider_prompt_root_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            not_prompts = root / "framework" / "not_prompts"
            not_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "doctrine-test"
                    version = "0.0.0"
                    """
                )
            )

            project_config = load_project_config(
                pyproject,
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", not_prompts),
                ),
            )
            with self.assertRaises(ProjectConfigError) as exc_info:
                project_config.resolve_compile_config()

            self.assertIn("Provided prompt root `framework_stdlib`", str(exc_info.exception))
            self.assertIn("existing prompts directory", str(exc_info.exception))

    def test_emit_targets_attach_provider_prompt_roots_to_project_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                """agent Demo:\n    role: "Own the emitted surface."\n"""
            )
            provider_prompts = root / "framework" / "prompts"
            provider_prompts.mkdir(parents=True)
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/AGENTS.prompt"
                    output_dir = "build"
                    """
                )
            )

            targets = load_emit_targets(
                pyproject,
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", provider_prompts),
                ),
            )
            compile_config = targets["demo"].project_config.resolve_compile_config()

            self.assertEqual(
                compile_config.provided_prompt_roots,
                (
                    ProvidedPromptRoot(
                        "framework_stdlib",
                        provider_prompts.resolve(),
                    ),
                ),
            )

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

    def test_emit_targets_reject_output_dir_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                """agent Demo:\n    role: "Own the emitted surface."\n"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "prompts/AGENTS.prompt"
                    output_dir = "../outside"
                    """
                )
            )

            with self.assertRaises(EmitError) as exc_info:
                load_emit_targets(pyproject)

            self.assertEqual(exc_info.exception.code, "E520")
            self.assertIn("outside the target project root", str(exc_info.exception))

    def test_emit_targets_reject_entrypoint_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            outside = root.parent / f"{root.name}_outside"
            (outside / "prompts").mkdir(parents=True)
            (outside / "prompts" / "AGENTS.prompt").write_text(
                """agent Demo:\n    role: "Own the emitted surface."\n"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    f"""\
                    [tool.doctrine.emit]

                    [[tool.doctrine.emit.targets]]
                    name = "demo"
                    entrypoint = "../{outside.name}/prompts/AGENTS.prompt"
                    output_dir = "build"
                    """
                )
            )

            # Configured emit targets are part of the owning project contract.
            # They must not pull source from a sibling prompts tree outside that
            # project root, or repo-local builds can start depending on ambient
            # files that are not part of the checked project.
            with self.assertRaises(EmitError) as exc_info:
                load_emit_targets(pyproject)

            self.assertEqual(exc_info.exception.code, "E521")
            self.assertIn("outside the target project root", str(exc_info.exception))

    def test_direct_emit_target_rejects_output_dir_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                """agent Demo:\n    role: "Own the emitted surface."\n"""
            )
            pyproject = root / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "demo"
                    version = "0.0.0"
                    """
                )
            )

            with self.assertRaises(EmitError) as exc_info:
                resolve_direct_emit_target(
                    pyproject_path=pyproject,
                    entrypoint="prompts/AGENTS.prompt",
                    output_dir="../outside",
                )

            self.assertEqual(exc_info.exception.code, "E520")
            self.assertIn("outside the target project root", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
