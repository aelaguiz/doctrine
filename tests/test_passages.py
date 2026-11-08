import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file, parse_text
from doctrine.passages import collect_passages, place_passages


class PassageTests(unittest.TestCase):
    def test_placement_keeps_line_endings_and_other_bytes(self):
        source = "before\r\n{{passage:P}}\r\n{{passage:P}}\n {{passage:P}}\r{{passage:P}}"
        result = place_passages(source, {"P": "A\nB"}, path="page.md")
        self.assertEqual(result, "before\r\nA\nB\r\nA\nB\n {{passage:P}}\rA\nB")

    def test_passage_is_placed_once_without_expanding_its_text(self):
        self.assertEqual(place_passages("{{passage:P}}\n", {"P": "{{passage:Q}}"},
                                        path="page.md"), "{{passage:Q}}\n")

    def test_triple_quoted_string_and_file_keep_text(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "p.md").write_bytes(b"line\r\n")
            prompt = root / "AGENTS.prompt"
            prompt.write_text('passage P: """one\ntwo"""\npassage Q from "p.md"\n')
            self.assertEqual(collect_passages([parse_file(prompt)], root),
                             {"P": "one\ntwo", "Q": "line"})

    def test_missing_or_invalid_file_fails_loud(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = parse_text('passage P from "p.md"\n')
            for content in (None, b"\xff"):
                if content is not None:
                    (root / "p.md").write_bytes(content)
                with self.assertRaises(CompileError) as caught:
                    collect_passages([prompt], root)
                self.assertEqual(caught.exception.code, "E652")

    def test_unknown_and_standalone_markers_fail(self):
        for passages, code in (({}, "E658"), (None, "E659")):
            with self.assertRaises(CompileError) as caught:
                place_passages("{{passage:P}}", passages, path="page.md")
            self.assertEqual(caught.exception.code, code)


if __name__ == "__main__":
    unittest.main()
