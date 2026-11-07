from __future__ import annotations

import hashlib
import json
import tomllib
import unittest
from pathlib import Path

from doctrine.emit_common import load_emit_targets
from doctrine.homes import compile_homes

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

    def test_load_lists_team_homes(self):
        root = self.project(SOURCE)
        code, output, error = self.cli(root, "load")
        self.assertEqual(code, 0, error)
        rows = [line.split() for line in output.splitlines()[1:]]
        self.assertEqual({(row[0], row[1]) for row in rows}, {(".", "claude"), (".", "codex"), ("qa", "claude"), ("qa", "codex")})
        self.assertEqual([int(row[4].replace(",", "")) for row in rows], sorted(int(row[4].replace(",", "")) for row in rows))

    def test_single_home_load_report(self):
        root = self.project(example="183_load_budgets")
        cases = tomllib.loads((Path(__file__).resolve().parents[1] / "examples/183_load_budgets/cases.toml").read_text())["cases"]
        case = next(case for case in cases if case["name"] == "one home prints its files and its biggest parts")
        code, output, error = self.cli(root, *case["args"])
        self.assertEqual(code, 0, error)
        self.assertEqual(output.splitlines(), case["expected_stdout_lines"])

    def test_entries_never_double_count(self):
        root = self.project('''abstract agent Base:
    role: "Role 🙂."
    work: "Work"
        "Parent."
        child: "Child"
            "Child text."
            deep: "Deep"
                "Deep text."
        sibling: "Sibling"
            "Sibling text."
        details cases: "Cases"
            "Long case."
        rule divider
team T: "Team"
    home: "t"
    member qa[Base]: "QA"
        override work.child:
            "Replacement."
            deep: "Deep"
                "Deep replacement."
''')
        target = load_emit_targets(root / "pyproject.toml")["homes"]
        homes, _ = compile_homes(target)
        entries = homes["t/qa"]["map"].entries
        expected = {
            ("role",): ("Base", "Role 🙂."),
            ("work",): ("Base", "## Work\n\nParent."),
            ("work", "child"): ("T.qa", "### Child\n\nReplacement.\n\n#### Deep\n\nDeep replacement."),
            ("work", "sibling"): ("Base", "### Sibling\n\nSibling text."),
            ("work", "cases"): ("Base", "### Cases\n\nLong case."),
            ("work", "divider"): ("Base", "---"),
        }
        self.assertEqual(len(entries), len(expected))
        for entry in entries:
            origin, text = expected[entry.path]
            self.assertEqual(entry.always_on, entry.path != ("work", "cases"))
            self.assertEqual(entry.origin, origin)
            self.assertEqual(entry.text_hash, hashlib.sha256(text.encode()).hexdigest())
            self.assertEqual(entry.size_bytes, len(text.encode()))
            self.assertEqual(entry.size_utf16, len(text.encode("utf-16-le")) // 2)
        code, output, error = self.cli(root, "load", "T.qa", "--json")
        self.assertEqual(code, 0, error)
        report = json.loads(output)["homes"][0]
        for runtime, size in (("claude", "size_utf16"), ("codex", "size_bytes")):
            self.assertEqual(sum(part["size"] for part in report["runtimes"][runtime]["parts"]), sum(getattr(entry, size) for entry in entries if entry.always_on))
            self.assertNotIn("text", report["runtimes"][runtime]["files"][0])

    def test_biggest_parts_order_and_smaller_row(self):
        source = "".join(f'workflow W{i}: "Work {i}"\n    "' + "x" * (10 * i) + '"\n' for i in range(1, 8))
        source += 'team T: "Team"\n    home: "t"\n' + "".join(f'    work{i}: W{i}\n' for i in range(1, 8))
        root = self.project(source, settings='[tool.doctrine.runtimes.codex]\nlimit = 1\n')
        code, output, error = self.cli(root, "load", "T", "--runtime", "codex")
        self.assertEqual(code, 0, error)
        expected = "Biggest parts:\n" + "\n".join(f"  W{i}: {11 + 10*i}" for i in range(7, 2, -1)) + "\n  And 2 smaller parts: 52"
        self.assertIn(expected, output)
        code, _, error = self.cli(root, "check")
        self.assertEqual(code, 1)
        self.assertEqual(error, "E630 compile error: Over load budget\n\nDetail:\n"
            "- t loads 482 of 1 bytes on codex.\n"
            "- Biggest parts:\n"
            "  - W7: 81\n  - W6: 71\n  - W5: 61\n  - W4: 51\n  - W3: 41\n"
            "  - And 2 smaller parts: 52\n")

    def test_drops_keep_the_declaration_that_wrote_them(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        "Parent."
        old: "Old"
            "Old text."
abstract agent Child[Base]:
    inherit *
    drop work.old: "Use the new path."
team T: "Team"
    home: "t"
    member qa[Child]: "QA"
''')
        code, output, error = self.cli(root, "load", "T.qa", "--json")
        self.assertEqual(code, 0, error)
        drops = json.loads(output)["homes"][0]["drops"]
        self.assertEqual(drops, [{"path": ["work", "old"], "origin": "Child", "reason": "Use the new path."}])
        self.assertIn("  work.old from Child: Use the new path.", self.cli(root, "load", "T.qa")[1])

    def test_template_member_keeps_patch_origins(self):
        root = self.project('''abstract agent Base:
    role: "Test."
    work: "Work"
        child: "Child"
            "Old text."
        old: "Old"
            "Old case."
abstract team Template:
    member qa[Base]: "QA"
        override work.child:
            "Template text."
        drop work.old: "Use the new path."
team T[Template]: "Team"
    home: "t"
''')
        target = load_emit_targets(root / "pyproject.toml")["homes"]
        homes, _ = compile_homes(target)
        home_map = homes["t/qa"]["map"]
        child = next(entry for entry in home_map.entries if entry.path == ("work", "child"))
        self.assertEqual(child.origin, "Template.qa")
        self.assertEqual(child.origin_path, ("work", "child"))
        self.assertEqual(child.site, "prompts/AGENTS.prompt:10")
        self.assertEqual(home_map.drops[0].origin, "Template.qa")
