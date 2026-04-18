from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession, ProvidedPromptRoot
from doctrine._compiler.indexing import unit_declarations, unit_loaded_imports
from doctrine._compiler.support import resolve_prompt_root
from doctrine.diagnostics import CompileError, DoctrineError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


REPO_ROOT = Path(__file__).resolve().parents[1]


class ImportLoadingTests(unittest.TestCase):
    def test_resolve_prompt_root_requires_source_path(self) -> None:
        with self.assertRaises(CompileError) as ctx:
            resolve_prompt_root(None)

        self.assertEqual(ctx.exception.code, "E291")
        self.assertIn("Prompt source path is required for compilation", str(ctx.exception))

    def test_prompt_file_outside_prompts_root_fails_with_file_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompt_path = root / "AGENTS.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(DoctrineError) as ctx:
                CompilationSession(parse_file(prompt_path))

        self.assertEqual(ctx.exception.code, "E292")
        self.assertEqual(ctx.exception.location.path, prompt_path.resolve())
        self.assertIn("Could not resolve prompts/ root", str(ctx.exception))

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

    def _write_cyclic_sibling_prompts(
        self,
        prompts: Path,
        *,
        import_from_root: bool,
        include_sibling_imports: bool,
    ) -> None:
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
        alpha_source = (
            "import cyclic_siblings.beta\n\n" if include_sibling_imports else ""
        ) + textwrap.dedent(
            """\
            workflow Alpha: "Alpha"
                "Alpha side"
            """
        )
        beta_source = (
            "import cyclic_siblings.alpha\n\n" if include_sibling_imports else ""
        ) + textwrap.dedent(
            """\
            workflow Beta: "Beta"
                "Beta side"
            """
        )
        (prompts / "AGENTS.prompt").write_text(textwrap.dedent(root_prompt), encoding="utf-8")
        (prompts / "cyclic_siblings" / "alpha.prompt").write_text(
            alpha_source,
            encoding="utf-8",
        )
        (prompts / "cyclic_siblings" / "beta.prompt").write_text(
            beta_source,
            encoding="utf-8",
        )

    def test_same_flow_sibling_imports_fail_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts = Path(temp_dir) / "prompts"
            self._write_cyclic_sibling_prompts(
                prompts,
                import_from_root=False,
                include_sibling_imports=True,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompts / "AGENTS.prompt"))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E315")
        self.assertEqual(error.diagnostic.location.path, (prompts / "cyclic_siblings" / "alpha.prompt").resolve())
        self.assertEqual(error.diagnostic.location.line, 1)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.path,
            (prompts / "cyclic_siblings" / "beta.prompt").resolve(),
        )
        self.assertIn("Same-flow import retired", str(error))
        self.assertIn("already share one flat namespace", str(error))

    def test_concurrent_same_flow_module_loads_share_one_flow_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts = Path(temp_dir) / "prompts"
            self._write_cyclic_sibling_prompts(
                prompts,
                import_from_root=False,
                include_sibling_imports=False,
            )

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
                        loaded = session.load_module(module_parts)
                    except DoctrineError as exc:
                        results.put(("error", str(exc)))
                    except Exception as exc:
                        results.put(("unexpected", f"{{type(exc).__name__}}: {{exc}}"))
                    else:
                        results.put(("ok", ".".join(loaded.module_parts)))

                # Two compile tasks can ask for sibling modules at the same time.
                # They should share one flow cache instead of deadlocking or racing.
                for module_parts in (
                    ("cyclic_siblings", "alpha"),
                    ("cyclic_siblings", "beta"),
                ):
                    threading.Thread(target=load, args=(module_parts,), daemon=True).start()

                seen = []
                try:
                    for _ in range(2):
                        seen.append(results.get(timeout=15))
                except queue.Empty:
                    raise SystemExit("timed out waiting for concurrent module loads")

                for kind, payload in seen:
                    print(kind)
                    print(payload)
                    if kind != "ok":
                        raise SystemExit(f"unexpected concurrent load result: {{kind}}")

                raise SystemExit(0)
                """
            )

            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        combined_output = f"{result.stdout}{result.stderr}"
        self.assertIn("ok", combined_output)
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
        self.assertIn(
            ("runtime_home",),
            unit_loaded_imports(session.root_flow.entrypoint_unit).imported_units,
        )

    def test_module_alias_and_symbol_imports_resolve_through_existing_name_ref_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "shared" / "greeting").mkdir(parents=True, exist_ok=True)
            (prompts / "shared" / "greeting" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export workflow Greeting: "Greeting"
                        "Say hello."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "shared" / "review").mkdir(parents=True, exist_ok=True)
            (prompts / "shared" / "review" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export output DraftReviewComment: "Draft Review Comment"
                        target: TurnResponse
                        shape: Comment
                        requirement: Required

                        current_artifact: "Current Artifact"
                            "Keep the current artifact visible."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared.greeting as shared_steps
                    from shared.review import DraftReviewComment as ImportedComment

                    agent Demo:
                        role: "Use alias-aware imports across workflow and outputs."
                        workflow: "Imported Steps"
                            use greeting: shared_steps.Greeting
                        outputs: "Outputs"
                            ImportedComment
                        final_output: ImportedComment
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "AGENTS.prompt"))
            compiled = session.compile_agent("Demo")

        rendered = render_markdown(compiled)
        self.assertIn(
            ("shared_steps",),
            unit_loaded_imports(session.root_flow.entrypoint_unit).visible_imported_units,
        )
        self.assertIn(
            "ImportedComment",
            unit_loaded_imports(session.root_flow.entrypoint_unit).imported_symbols_by_name,
        )
        self.assertIn("### Greeting", rendered)
        self.assertIn("### Draft Review Comment", rendered)

    def test_from_import_does_not_make_the_module_path_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "shared" / "review").mkdir(parents=True, exist_ok=True)
            (prompts / "shared" / "review" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export workflow ImportedFlow: "Imported Flow"
                        "Use the imported flow."
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = (prompts / "AGENTS.prompt").resolve()
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    from shared.review import ImportedFlow

                    agent Demo:
                        role: "Keep symbol imports and module imports separate."
                        workflow: "Imported Steps"
                            # This protects the fail-loud import contract. A symbol import
                            # keeps `ImportedFlow` visible, but it must not silently make
                            # `shared.review.ImportedFlow` behave like a module import.
                            use imported: shared.review.ImportedFlow
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.code, "E280")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(error.diagnostic.location.line, 9)
        self.assertIn("Missing import module: shared.review", str(error))

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
        self.assertIn("E287 compile error: Ambiguous import module", error_text)
        self.assertIn("Import module `shared.speaker` matches more than one prompt file shape", error_text)
        self.assertIn("file module:", error_text)
        self.assertIn("shared/speaker.prompt", error_text)
        self.assertIn("runtime package:", error_text)
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

    def test_directory_backed_runtime_package_uses_provider_prompt_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            provider_prompts = root / "framework" / "prompts"
            prompts.mkdir(parents=True, exist_ok=True)
            self._write_runtime_package(provider_prompts / "framework" / "stdlib")
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import framework.stdlib

                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(
                parse_file(prompts / "AGENTS.prompt"),
                provided_prompt_roots=(
                    ProvidedPromptRoot("framework_stdlib", provider_prompts),
                ),
            )
            loaded = session.load_module(("framework", "stdlib"))

        self.assertEqual(loaded.module_source_kind, "runtime_package")
        self.assertEqual(loaded.prompt_root, provider_prompts)
        self.assertEqual(
            loaded.package_root,
            provider_prompts / "framework" / "stdlib",
        )
        self.assertEqual(
            loaded.prompt_file.source_path,
            provider_prompts / "framework" / "stdlib" / "AGENTS.prompt",
        )

    def test_duplicate_provider_prompt_root_matches_local_root_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True, exist_ok=True)
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent Demo:
                        role: "Own the build handle."
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(DoctrineError) as ctx:
                CompilationSession(
                    parse_file(prompts / "AGENTS.prompt"),
                    provided_prompt_roots=(
                        ProvidedPromptRoot("framework_stdlib", prompts),
                    ),
                )

        self.assertEqual(ctx.exception.code, "E286")
        self.assertIn("Duplicate active prompts root", str(ctx.exception))
        self.assertIn("provided prompts root `framework_stdlib`", str(ctx.exception))
        self.assertEqual(ctx.exception.location.path, prompts.resolve())
        self.assertEqual(len(ctx.exception.diagnostic.related), 1)
        self.assertEqual(
            ctx.exception.diagnostic.related[0].location.path,
            prompts.resolve(),
        )
        self.assertIn("entrypoint prompts root", ctx.exception.diagnostic.related[0].label)

    def test_ambiguous_module_across_configured_and_provider_roots_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            configured_prompts = root / "shared" / "prompts"
            provider_prompts = root / "framework" / "prompts"
            prompts.mkdir(parents=True, exist_ok=True)
            (configured_prompts / "shared").mkdir(parents=True, exist_ok=True)
            (provider_prompts / "shared").mkdir(parents=True, exist_ok=True)
            (configured_prompts / "shared" / "guide.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow SharedGuide: "Shared Guide"
                        "Use the configured guide."
                    """
                ),
                encoding="utf-8",
            )
            (provider_prompts / "shared" / "guide.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow SharedGuide: "Shared Guide"
                        "Use the provider guide."
                    """
                ),
                encoding="utf-8",
            )
            (prompts / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared.guide

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

            with self.assertRaises(DoctrineError) as ctx:
                CompilationSession(
                    parse_file(prompts / "AGENTS.prompt"),
                    provided_prompt_roots=(
                        ProvidedPromptRoot("framework_stdlib", provider_prompts),
                    ),
                )

        self.assertEqual(ctx.exception.code, "E287")
        error_text = str(ctx.exception)
        self.assertIn("Ambiguous import module", error_text)
        self.assertIn("configured prompts root", error_text)
        self.assertIn("provided prompts root `framework_stdlib`", error_text)

    def test_skill_package_entrypoint_loads_package_local_prompt_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts" / "skills" / "reference_docs"
            refs = prompts / "refs"
            refs.mkdir(parents=True, exist_ok=True)
            (prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    skill package ReferenceDocs: "Reference Docs"
                        emit:
                            "references/query-patterns.md": QueryPatterns
                        "Keep the root file short."
                    """
                ),
                encoding="utf-8",
            )
            (refs / "query_patterns.prompt").write_text(
                textwrap.dedent(
                    """\
                    document QueryPatterns: "Query Patterns"
                        section summary: "Summary"
                            "Pick the right query."
                    """
                ),
                encoding="utf-8",
            )

            session = CompilationSession(parse_file(prompts / "SKILL.prompt"))
            loaded = session.load_module(("refs", "query_patterns"))

        self.assertEqual(loaded.prompt_root, prompts)
        self.assertEqual(loaded.package_root, prompts)
        self.assertEqual(loaded.prompt_file.source_path, refs / "query_patterns.prompt")
        self.assertEqual(
            unit_loaded_imports(session.root_flow.entrypoint_unit).imported_symbols_by_name,
            {},
        )

    def test_skill_package_entrypoint_fails_loud_on_local_import_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            package_prompts = root / "prompts" / "skills" / "reference_docs"
            global_shared = root / "prompts" / "shared"
            local_shared = package_prompts / "shared"
            global_shared.mkdir(parents=True, exist_ok=True)
            local_shared.mkdir(parents=True, exist_ok=True)
            (package_prompts / "SKILL.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared.guide

                    skill package ReferenceDocs: "Reference Docs"
                        "Fail loud when a package-local module collides with the repo root."
                    """
                ),
                encoding="utf-8",
            )
            (global_shared / "guide.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow GlobalGuide: "Global Guide"
                        "Use the repo-wide guide."
                    """
                ),
                encoding="utf-8",
            )
            (local_shared / "guide.prompt").write_text(
                textwrap.dedent(
                    """\
                    workflow LocalGuide: "Local Guide"
                        "Use the package-local guide."
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(DoctrineError) as ctx:
                CompilationSession(parse_file(package_prompts / "SKILL.prompt"))

        error_text = str(ctx.exception)
        self.assertEqual(ctx.exception.code, "E287")
        self.assertIn("Ambiguous import module", error_text)
        self.assertIn("skill package source root", error_text)
        self.assertIn("entrypoint prompts root", error_text)

    def test_two_sessions_in_one_process_keep_unit_state_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as a_dir, tempfile.TemporaryDirectory() as b_dir:
            prompts_a = Path(a_dir).resolve() / "prompts"
            prompts_b = Path(b_dir).resolve() / "prompts"
            prompts_a.mkdir(parents=True)
            prompts_b.mkdir(parents=True)
            (prompts_a / "shared").mkdir()
            (prompts_a / "shared" / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    export workflow Shared: "Shared"
                        "Use the shared step."
                    """
                ),
                encoding="utf-8",
            )
            (prompts_a / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    import shared

                    agent DemoA:
                        role: "Session A home."
                        workflow: "Run"
                            use step: shared.Shared
                    """
                ),
                encoding="utf-8",
            )
            (prompts_b / "AGENTS.prompt").write_text(
                textwrap.dedent(
                    """\
                    agent DemoB:
                        role: "Session B home. No imports, no declarations."
                    """
                ),
                encoding="utf-8",
            )

            session_a = CompilationSession(parse_file(prompts_a / "AGENTS.prompt"))
            session_b = CompilationSession(parse_file(prompts_b / "AGENTS.prompt"))

            entry_a = session_a.root_flow.entrypoint_unit
            entry_b = session_b.root_flow.entrypoint_unit

            self.assertIn("DemoA", unit_declarations(entry_a).agents_by_name)
            self.assertNotIn("DemoB", unit_declarations(entry_a).agents_by_name)
            self.assertIn("DemoB", unit_declarations(entry_b).agents_by_name)
            self.assertNotIn("DemoA", unit_declarations(entry_b).agents_by_name)

            self.assertIn(
                ("shared",),
                unit_loaded_imports(entry_a).imported_units,
            )
            self.assertEqual(unit_loaded_imports(entry_b).imported_units, {})


if __name__ == "__main__":
    unittest.main()
