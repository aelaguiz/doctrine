from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.parser import parse_file


REPO_ROOT = Path(__file__).resolve().parents[1]


class ImportLoadingTests(unittest.TestCase):
    def _write_runtime_package(
        self,
        package_root: Path,
        *,
        agent_name: str = "RuntimeHome",
    ) -> None:
        package_root.mkdir(parents=True, exist_ok=True)
        (package_root / "AGENTS.prompt").write_text(
            textwrap.dedent(
                f"""\
                agent {agent_name}:
                    role: "Own the runtime package."
                """
            ),
            encoding="utf-8",
        )

    def _write_cyclic_sibling_prompts(self, prompts: Path, *, import_from_root: bool) -> None:
        (prompts / "cyclic_siblings").mkdir(parents=True)
        if import_from_root:
            root_prompt = """\
            import cyclic_siblings.alpha
            import cyclic_siblings.beta

            agent Demo:
                role: "demo"
                workflow: "Imported Steps"
                    "This compile should fail with a cyclic import."
                    use alpha: cyclic_siblings.alpha.Alpha
            """
        else:
            root_prompt = """\
            agent Demo:
                role: "demo"
                workflow: "Imported Steps"
                    "demo"
            """
        (prompts / "AGENTS.prompt").write_text(textwrap.dedent(root_prompt), encoding="utf-8")
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

    def test_sibling_import_cycle_fails_loud_instead_of_hanging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts = Path(temp_dir) / "prompts"
            self._write_cyclic_sibling_prompts(prompts, import_from_root=True)

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

    def test_concurrent_top_level_module_load_cycle_fails_loud_instead_of_deadlocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts = Path(temp_dir) / "prompts"
            self._write_cyclic_sibling_prompts(prompts, import_from_root=False)

            script = textwrap.dedent(
                f"""\
                import queue
                import threading
                from doctrine.compiler import CompilationSession
                from doctrine.diagnostics import DoctrineError
                from doctrine.parser import parse_file

                session = CompilationSession(parse_file({repr(str(prompts / "AGENTS.prompt"))}))
                results = queue.Queue()

                def load(module_parts):
                    try:
                        session.load_module(module_parts)
                    except DoctrineError as exc:
                        results.put(("error", str(exc)))
                    except Exception as exc:
                        results.put(("unexpected", f"{{type(exc).__name__}}: {{exc}}"))
                    else:
                        results.put(("ok", ".".join(module_parts)))

                # Two compile tasks can ask for different imported modules at the same time.
                # This must raise the same cyclic-import error as the single-threaded path.
                for module_parts in (
                    ("cyclic_siblings", "alpha"),
                    ("cyclic_siblings", "beta"),
                ):
                    threading.Thread(target=load, args=(module_parts,), daemon=True).start()

                seen = []
                try:
                    for _ in range(2):
                        seen.append(results.get(timeout=2))
                except queue.Empty:
                    raise SystemExit("timed out waiting for concurrent module loads")

                for kind, payload in seen:
                    print(kind)
                    print(payload)
                    if kind != "error":
                        raise SystemExit(f"unexpected concurrent load result: {{kind}}")

                raise SystemExit(1)
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
        self.assertIn("cyclic_siblings.beta", combined_output)
        self.assertNotIn("timed out waiting for concurrent module loads", combined_output)
        self.assertNotIn("unexpected concurrent load result", combined_output)
        self.assertNotIn("Traceback", combined_output)

    def test_directory_backed_runtime_package_loads_with_explicit_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            self._write_runtime_package(prompts / "runtime_home")
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import runtime_home

                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            loaded = session.load_module(("runtime_home",))

        self.assertEqual(loaded.module_source_kind, "runtime_package")
        self.assertEqual(loaded.prompt_root, prompts)
        self.assertEqual(loaded.package_root, prompts / "runtime_home")
        self.assertEqual(loaded.prompt_file.source_path, prompts / "runtime_home" / "AGENTS.prompt")
        self.assertIn(("runtime_home",), session.root_unit.imported_units)

    def test_file_and_directory_module_collision_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "shared").mkdir(parents=True, exist_ok=True)
            (prompts / "shared" / "speaker.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow SpeakerGuide: "Speaker Guide"
                        "Use the local speaker guide."
                    """
                ),
                encoding="utf-8",
            )
            self._write_runtime_package(
                prompts / "shared" / "speaker",
                agent_name="SpeakerHome",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared.speaker

                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(DoctrineError) as ctx:
                CompilationSession(parse_file(prompts / "AGENTS.prompt"))

        error_text = str(ctx.exception)
        self.assertIn("Ambiguous import module: shared.speaker", error_text)
        self.assertIn("shared/speaker.prompt", error_text)
        self.assertIn("shared/speaker/AGENTS.prompt", error_text)
        self.assertNotIn("Traceback", error_text)

    def test_directory_backed_runtime_package_uses_additional_prompt_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            shared_prompts = root / "shared" / "prompts"
            prompts.mkdir(parents=True, exist_ok=True)
            self._write_runtime_package(shared_prompts / "shared" / "runtime_home")
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared.runtime_home

                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "doctrine-test"
                    version = "0.0.0"

                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts"]
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            loaded = session.load_module(("shared", "runtime_home"))

        self.assertEqual(loaded.module_source_kind, "runtime_package")
        self.assertEqual(loaded.prompt_root, shared_prompts)
        self.assertEqual(loaded.package_root, shared_prompts / "shared" / "runtime_home")
        self.assertEqual(
            loaded.prompt_file.source_path,
            shared_prompts / "shared" / "runtime_home" / "AGENTS.prompt",
        )


if __name__ == "__main__":
    unittest.main()
