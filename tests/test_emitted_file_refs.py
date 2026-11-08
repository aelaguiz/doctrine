from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from doctrine.emit_flow import emit_target_flow
from doctrine.emit_skill import emit_target_skill
from doctrine.emit_skill_graph import emit_target_skill_graph
from doctrine.homes import compile_homes
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class EmittedFileRefsTests(unittest.TestCase):
    def assert_no_internal_links(self, data, name):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return
        self.assertNotIn("", text, str(name))
        self.assertNotIn("\\ue000", text, str(name))

    def test_all_shipped_example_targets_emit_no_internal_links(self):
        repo = Path(__file__).resolve().parents[1]
        examples = repo / "examples"
        known_errors = {
            "179_markdown_backed_declarations/pyproject.toml": "E503",
            "180_home_tree/project_collision/pyproject.toml": "E607",
            "181_details/project_case_duplicate/pyproject.toml": "E612",
            "181_details/project_case_missing/pyproject.toml": "E610",
            "181_details/project_soul_details/pyproject.toml": "E620",
            "190_quotes/project_bad_date/pyproject.toml": "E650",
            "75_cross_root_standard_library_imports/invalid_ambiguous/pyproject.toml": "E503",
            "75_cross_root_standard_library_imports/invalid_root_config/pyproject.toml": "E503",
            "75_cross_root_standard_library_imports/pyproject.toml": "E503",
        }
        count = 0
        for config in sorted(examples.glob("*/**/pyproject.toml")):
            with self.subTest(config=config):
                key = config.relative_to(examples).as_posix()
                try:
                    targets = load_emit_targets(config)
                    for target in targets.values():
                        session = CompilationSession(parse_file(target.entrypoint), project_config=target.project_config)
                        _, files, _, _ = compile_homes(target, session=session)
                        for path, content in files.items():
                            if isinstance(content, bytes):
                                self.assert_no_internal_links(content, path)
                        count += 1
                except DoctrineError as error:
                    self.assertIn(key, known_errors)
                    self.assertIn(known_errors[key], str(error))
                else:
                    self.assertNotIn(key, known_errors)
        targets = load_emit_targets(repo / "pyproject.toml")
        with tempfile.TemporaryDirectory() as temporary:
            for target in targets.values():
                if not target.entrypoint.is_relative_to(examples):
                    continue
                with self.subTest(target=target.name):
                    output = Path(temporary) / target.name
                    if target.graph is not None:
                        paths = emit_target_skill_graph(target, output_dir_override=output)
                    elif target.entrypoint.name == "SKILL.prompt":
                        paths = emit_target_skill(target, output_dir_override=output)
                    else:
                        paths = (*emit_target(target, output_dir_override=output),
                                 *emit_target_flow(target, output_dir_override=output))
                    for path in paths:
                        self.assert_no_internal_links(path.read_bytes(), path)
                    count += 1
        self.assertGreaterEqual(count, 90)

    def test_compile_api_emits_no_internal_links(self):
        root = Path(__file__).resolve().parents[1] / "examples/197_shared_files/render"
        session = CompilationSession(parse_file(root / "prompts/AGENTS.prompt"))
        text = render_markdown(session.compile_agent("Writer"))
        self.assert_no_internal_links(text.encode(), "compile API")
        self.assertEqual(text, "Before you write, read [Guide](shared/guide.md).\n")
