from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from doctrine.homes import HEADER
from doctrine.emit_common import load_emit_targets
from doctrine.emit_docs import emit_target
from tests.home_support import HomeProject


class HomeTreeTests(HomeProject, unittest.TestCase):
    def test_claude_md_is_relative_symlink(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(os.readlink(root / "pods/growth/qa/CLAUDE.md"), "AGENTS.md")

    def test_header_hash_matches_body(self):
        for source in ("prompts/AGENTS.prompt", "prompts/été/AGENTS.prompt"):
            with self.subTest(source=source):
                root = self.project()
                if source != "prompts/AGENTS.prompt":
                    (root / source).parent.mkdir()
                    (root / "prompts/AGENTS.prompt").rename(root / source)
                    config = root / "pyproject.toml"
                    config.write_text(config.read_text().replace("prompts/AGENTS.prompt", source))
                self.assertEqual(self.cli(root, "build", ".")[0], 0)
                for path in root.rglob("AGENTS.md"):
                    text = path.read_text()
                    header = HEADER.match(text)
                    self.assertIsNotNone(header)
                    self.assertEqual(
                        header[1], hashlib.sha256(text[header.end() :].encode()).hexdigest()[:12]
                    )
                    self.assertIn(f"source={source}.", header[0])
                self.assertEqual(self.cli(root, "build", ".")[0], 0)

    def test_emit_is_deterministic(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        original = {
            path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
        }
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(
            original,
            {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            },
        )

    def test_no_import_lines_emitted(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertFalse(
            any(
                line.startswith("@")
                for path in root.rglob("AGENTS.md")
                for line in path.read_text().splitlines()
            )
        )

    def test_concurrent_builds_are_safe(self):
        root = self.project()
        repo = str(Path(__file__).resolve().parents[1])
        processes = [
            subprocess.Popen(
                [sys.executable, "-m", "doctrine.cli", "build", "."],
                cwd=root,
                env={**os.environ, "PYTHONPATH": repo},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for _ in range(8)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=60)
            self.assertEqual(process.returncode, 0, (stdout, stderr))
        self.assertEqual(self.cli(root, "build", ".", "--check")[0], 0)

    def test_write_skipped_when_bytes_match(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        before = {path: path.lstat().st_mtime_ns for path in root.rglob("*") if path.is_file()}
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(before, {path: path.lstat().st_mtime_ns for path in before})

    def test_emit_docs_output_unchanged(self):
        root = self.project('agent A:\n    role: "Ordinary text."\n')
        emit_target(load_emit_targets(root / "pyproject.toml")["homes"])
        self.assertEqual((root / "a/AGENTS.md").read_bytes(), b"Ordinary text.\n")

    def test_plain_agent_gets_header_and_guard(self):
        root = self.project('agent A:\n    role: "Ordinary text."\n')
        self.assertEqual(self.cli(root, "build", "--target", "homes")[0], 0)
        path = root / "a/AGENTS.md"
        self.assertIsNotNone(HEADER.match(path.read_text()))
        path.write_text("Hand edit.\n")
        code, _, error = self.cli(root, "build", "--target", "homes")
        self.assertEqual(code, 1)
        self.assertIn("E634", error)
        self.assertEqual(path.read_text(), "Hand edit.\n")

    def test_written_files_follow_umask(self):
        root = self.project()
        previous = os.umask(0o022)
        try:
            code, _, error = self.cli(root, "build", ".")
        finally:
            os.umask(previous)
        self.assertEqual(code, 0, error)
        for path in root.rglob("*"):
            if path.is_file() and not path.is_symlink() and path.suffix in (".md", ".json"):
                self.assertEqual(path.stat().st_mode & 0o777, 0o644, path)

    def test_contract_files_have_no_guard(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        for path in (root / "HOMES.contract.json", root / "pods/growth/TEAM.contract.json"):
            path.write_text(
                '{"format_version": 1, "files": []}\n'
                if path.name == "HOMES.contract.json"
                else "{}\n"
            )
        self.assertEqual(self.cli(root, "build", ".", "--check")[0], 1)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(
            json.loads((root / "HOMES.contract.json").read_text())["format_version"], 1
        )

    def test_claude_md_link_left_alone(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        link = root / "pods/growth/CLAUDE.md"
        before = link.lstat().st_ino
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(link.lstat().st_ino, before)

    def test_real_claude_md_goes_through_guard(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        link = root / "pods/growth/CLAUDE.md"
        text = link.read_bytes()
        link.unlink()
        link.write_bytes(text + b"Hand edit.\n")
        self.assertIn("E634", self.cli(root, "build", ".")[2])
        link.write_bytes(text)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertTrue(link.is_symlink())

    def test_other_claude_md_link_is_e634(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        path = root / "pods/growth/CLAUDE.md"
        path.unlink()
        path.symlink_to("elsewhere.md")
        self.assertIn("E634", self.cli(root, "build", ".")[2])

    def test_record_lists_every_emitted_path_sorted(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        paths = json.loads((root / "HOMES.contract.json").read_text())["files"]
        expected = sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix != ".prompt"
            and path.name not in {"pyproject.toml", "HOMES.contract.json"}
        )
        self.assertEqual(paths, expected)

    def test_missing_record_means_nothing_obsolete(self):
        root = self.project()
        obsolete = root / "gone/AGENTS.md"
        obsolete.parent.mkdir()
        obsolete.write_text("Old file.\n")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(obsolete.read_text(), "Old file.\n")

    def test_conflicted_record_counts_as_missing(self):
        root = self.project()
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        record = root / "HOMES.contract.json"
        paths = json.loads(record.read_text())["files"]
        record.write_text('<<<<<<< HEAD\n{"files": []}\n=======\n{}\n>>>>>>> member\n')
        obsolete = root / "gone/AGENTS.md"
        obsolete.parent.mkdir()
        obsolete.write_text("Old file.\n")
        code, output, error = self.cli(root, "build", ".", "--check")
        self.assertEqual(code, 1, error)
        self.assertIn("stale HOMES.contract.json", output)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(json.loads(record.read_text())["files"], paths)
        self.assertEqual(obsolete.read_text(), "Old file.\n")
