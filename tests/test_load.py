from __future__ import annotations

import unittest

from tests.ws3_support import HomeProject


SOURCE = 'team T: "Team"\n    home: "."\n    role: "Shared."\n    member qa: "QA"\n        role: "Test 🙂."\n'


class LoadTests(HomeProject, unittest.TestCase):
    def test_full_prints_every_file_in_order(self):
        root = self.project(SOURCE, settings='[tool.doctrine.runtimes.codex]\nexternal = [{path="outside.md"}]\n')
        (root / "outside.md").write_text("External.\n")
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        code, output, error = self.cli(root, "load", "T.qa", "--runtime", "codex", "--full")
        self.assertEqual(code, 0, error)
        expected = ""
        for name in ("outside.md", "AGENTS.md", "qa/AGENTS.md"):
            content = (root / name).read_bytes()
            expected += f"===== {name} ({len(content):,}) =====\n" + content.decode()
        self.assertEqual(output, expected)

    def test_claude_counts_utf16_units(self):
        root = self.project(SOURCE)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        load = self.loads(root)[1]["runtimes"]["claude"]
        self.assertEqual(load["total"], sum(len((root / path).read_bytes().decode().encode("utf-16-le")) // 2 for path in ("CLAUDE.md", "qa/CLAUDE.md")))
        self.assertGreater(load["total"], sum(len((root / path).read_text()) for path in ("CLAUDE.md", "qa/CLAUDE.md")))

    def test_codex_counts_bytes(self):
        root = self.project(SOURCE)
        self.assertEqual(self.cli(root, "build", ".")[0], 0)
        self.assertEqual(self.loads(root)[1]["runtimes"]["codex"]["total"], sum((root / path).stat().st_size for path in ("AGENTS.md", "qa/AGENTS.md")))

    def test_codex_limit_read_from_project_config(self):
        root = self.project(SOURCE)
        (root / ".codex").mkdir()
        (root / ".codex/config.toml").write_text("project_doc_max_bytes = 4096\n")
        self.assertEqual(self.loads(root)[1]["runtimes"]["codex"]["limit"], 4096)

    def test_external_present_counts_real_size(self):
        root = self.project(SOURCE, settings='[tool.doctrine.runtimes.claude]\nexternal = [{path="outside.md", reserve=999}]\n')
        (root / "outside.md").write_bytes("Shared 🙂.\r\n".encode())
        load = self.loads(root)[1]["runtimes"]["claude"]
        self.assertEqual(load["files"][0]["size"], len("Shared 🙂.\r\n".encode("utf-16-le")) // 2)

    def test_external_absent_counts_reserve(self):
        root = self.project(SOURCE, settings='[tool.doctrine.runtimes.claude]\nexternal = [{path="outside.md", reserve=99}]\n')
        self.assertEqual(self.loads(root)[1]["runtimes"]["claude"]["files"][0]["size"], 99)

    def test_e633_absent_no_reserve(self):
        root = self.project(SOURCE, settings='[tool.doctrine.runtimes.claude]\nexternal = [{path="absent.md"}]\n')
        result = self.cli(root, "check")
        self.assertEqual(result[0], 1)
        self.assertIn('`absent.md` is listed for claude, but it is absent and has no `reserve`.', result[2])

    def test_nearest_budget_wins(self):
        root = self.project('team T: "Team"\n    home: "."\n    budget:\n        codex: 2000\n    member qa: "QA"\n        role: "Test."\n        budget:\n            codex: 1000\n    member analyst: "Analyst"\n        role: "Read."\n')
        loads = {item["home"]: item for item in self.loads(root)}
        self.assertEqual(loads["qa"]["runtimes"]["codex"]["limit"], 1000)
        self.assertEqual(loads["analyst"]["runtimes"]["codex"]["limit"], 2000)

    def test_e631_over_runtime_limit(self):
        root = self.project(SOURCE.replace('    role: "Shared."', '    budget:\n        codex: 999999\n    role: "Shared."'))
        result = self.cli(root, "check")
        self.assertEqual(result[0], 1)
        self.assertIn('`budget` for `codex` is over the runtime\'s limit of 32768.', result[2])
