from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine._package_release import (
    load_package_release_metadata,
    resolve_distribution_artifact,
    write_github_outputs,
)


class PackageReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_package_release_metadata_reads_explicit_release_fields(self) -> None:
        self._write_pyproject(
            """\
            [project]
            name = "doctrine-agents"
            version = "1.0.2"

            [tool.doctrine.package]
            import_name = "doctrine"
            pypi_environment = "pypi"
            testpypi_environment = "testpypi"
            """
        )

        metadata = load_package_release_metadata(self.root)

        self.assertEqual(metadata.distribution_name, "doctrine-agents")
        self.assertEqual(metadata.version, "1.0.2")
        self.assertEqual(metadata.import_name, "doctrine")
        self.assertEqual(metadata.pypi_environment, "pypi")
        self.assertEqual(metadata.testpypi_environment, "testpypi")
        self.assertEqual(metadata.pypi_project_url, "https://pypi.org/project/doctrine-agents/")
        self.assertEqual(
            metadata.testpypi_project_url,
            "https://test.pypi.org/project/doctrine-agents/",
        )

    def test_load_package_release_metadata_requires_tool_doctrine_package_table(self) -> None:
        self._write_pyproject(
            """\
            [project]
            name = "doctrine-agents"
            version = "1.0.2"
            """
        )

        with self.assertRaisesRegex(RuntimeError, r"must contain a `\[tool.doctrine.package\]` table"):
            load_package_release_metadata(self.root)

    def test_load_package_release_metadata_requires_named_release_fields(self) -> None:
        self._write_pyproject(
            """\
            [project]
            name = "doctrine-agents"
            version = "1.0.2"

            [tool.doctrine.package]
            import_name = "doctrine"
            pypi_environment = "release"
            """
        )

        with self.assertRaisesRegex(
            RuntimeError,
            r"`\[tool.doctrine.package\]\.testpypi_environment` must be a non-empty string",
        ):
            load_package_release_metadata(self.root)

    def test_resolve_distribution_artifact_requires_exactly_one_match(self) -> None:
        dist_dir = self.root / "dist"
        dist_dir.mkdir()
        (dist_dir / "doctrine_agents-1.0.2-py3-none-any.whl").write_text("", encoding="utf-8")

        resolved = resolve_distribution_artifact(dist_dir=dist_dir, artifact_type="wheel")

        self.assertTrue(resolved.name.endswith(".whl"))

    def test_write_github_outputs_uses_metadata_fields(self) -> None:
        self._write_pyproject(
            """\
            [project]
            name = "doctrine-agents"
            version = "1.0.2"

            [tool.doctrine.package]
            import_name = "doctrine"
            pypi_environment = "pypi"
            testpypi_environment = "testpypi"
            """
        )
        output_path = self.root / "github-output.txt"

        write_github_outputs(
            metadata=load_package_release_metadata(self.root),
            output_path=output_path,
        )

        text = output_path.read_text(encoding="utf-8")
        self.assertIn("distribution_name=doctrine-agents", text)
        self.assertIn("import_name=doctrine", text)
        self.assertIn("pypi_project_url=https://pypi.org/project/doctrine-agents/", text)

    def _write_pyproject(self, text: str) -> None:
        (self.root / "pyproject.toml").write_text(
            textwrap.dedent(text),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
