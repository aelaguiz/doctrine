from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine._verify_skill_examples import (
    default_skill_roots,
    extract_prompt_blocks,
    iter_markdown_files,
    run_skill_example_checks,
)


class ExtractPromptBlocksTests(unittest.TestCase):
    def test_extracts_only_prompt_tagged_fences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "guide.md"
            md.write_text(
                textwrap.dedent(
                    """
                    Intro.

                    ```prompt
                    agent Demo:
                        role: "Say hi."
                    ```

                    A fragment that is not a whole prompt:

                    ```prompt-fragment
                    output: Fragment
                    ```

                    ```text
                    agent WrongFence:
                        role: "Ignored."
                    ```
                    """
                ).strip()
                + "\n"
            )

            blocks = extract_prompt_blocks(md)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0].lang, "prompt")
            self.assertIn("agent Demo", blocks[0].body)


class RunSkillExampleChecksTests(unittest.TestCase):
    def test_complete_prompt_parses_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide.md").write_text(
                textwrap.dedent(
                    """
                    ```prompt
                    agent Demo:
                        role: "Say hi."
                    ```
                    """
                ).strip()
                + "\n"
            )
            self.assertEqual(run_skill_example_checks([root]), [])

    def test_broken_prompt_surfaces_as_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide.md").write_text(
                textwrap.dedent(
                    """
                    ```prompt
                    agent Demo
                        role "missing colons"
                    ```
                    """
                ).strip()
                + "\n"
            )
            failures = run_skill_example_checks([root])
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0].block.lang, "prompt")
            self.assertIn("ParseError", failures[0].message)

    def test_prompt_fragment_blocks_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide.md").write_text(
                textwrap.dedent(
                    """
                    ```prompt-fragment
                    this is not valid doctrine and must not run through the parser
                    ```
                    """
                ).strip()
                + "\n"
            )
            self.assertEqual(run_skill_example_checks([root]), [])


class SkillRootDiscoveryTests(unittest.TestCase):
    def test_default_skill_roots_point_at_source_prompts(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        roots = default_skill_roots(repo_root)
        self.assertTrue(roots, "expected at least one skill prompts root in the repo")
        for root in roots:
            self.assertEqual(root.name, "prompts")
            self.assertTrue(root.is_dir())
            # Source-only: no build output and no curated public mirror.
            self.assertNotIn(".curated", root.parts)
            self.assertNotIn("build", root.parts)

    def test_iter_markdown_files_yields_md_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("a\n")
            nested = root / "nested"
            nested.mkdir()
            (nested / "b.md").write_text("b\n")
            (root / "c.txt").write_text("c\n")
            md_files = list(iter_markdown_files([root]))
            self.assertEqual(
                sorted(p.name for p in md_files),
                ["a.md", "b.md"],
            )


class ShippedSkillExamplesTests(unittest.TestCase):
    def test_shipped_skill_fences_parse(self) -> None:
        # Guards the teaching surface: every ```prompt block in shipped skill
        # reference markdown must parse as a standalone prompt file.
        repo_root = Path(__file__).resolve().parents[1]
        roots = default_skill_roots(repo_root)
        failures = run_skill_example_checks(roots)
        if failures:
            details = "\n".join(
                f"  {failure.block.path.relative_to(repo_root)}:{failure.block.line} :: {failure.message}"
                for failure in failures
            )
            self.fail(f"Skill-bundled prompt fences failed to parse:\n{details}")


if __name__ == "__main__":
    unittest.main()
