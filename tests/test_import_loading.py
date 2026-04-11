from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ImportLoadingTests(unittest.TestCase):
    def test_sibling_import_cycle_fails_loud_instead_of_hanging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts = Path(temp_dir) / "prompts"
            (prompts / "cyclic_siblings").mkdir(parents=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import cyclic_siblings.alpha
                    import cyclic_siblings.beta

                    agent Demo:
                        role: "demo"
                        workflow: "Imported Steps"
                            "This compile should fail with a cyclic import."
                            use alpha: cyclic_siblings.alpha.Alpha
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "cyclic_siblings" / "alpha.prompt").write_text(
                textwrap.dedent(
                    """\
                    import cyclic_siblings.beta

                    workflow Alpha: "Alpha"
                        "Alpha side"
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "cyclic_siblings" / "beta.prompt").write_text(
                textwrap.dedent(
                    """\
                    import cyclic_siblings.alpha

                    workflow Beta: "Beta"
                        "Beta side"
                    """
                ),
                encoding="utf-8",
            )

            script = textwrap.dedent(
                f"""\
                from doctrine.compiler import CompilationSession
                from doctrine.diagnostics import DoctrineError
                from doctrine.parser import parse_file

                try:
                    prompt = parse_file({repr(str(prompts / "AGENTS.prompt"))})
                    CompilationSession(prompt).compile_agent("Demo")
                except DoctrineError as exc:
                    print(exc)
                    raise SystemExit(1)
                raise SystemExit("expected compile failure")
                """
            )

            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        combined_output = f"{result.stdout}{result.stderr}"
        self.assertIn("E289 compile error: Cyclic import module", combined_output)
        self.assertIn("cyclic_siblings.alpha", combined_output)
        self.assertNotIn("Traceback", combined_output)


if __name__ == "__main__":
    unittest.main()
