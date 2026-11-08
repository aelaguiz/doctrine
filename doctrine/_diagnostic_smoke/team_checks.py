from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine._diagnostic_smoke.fixtures import SmokeFailure, _expect, _write_prompt


TEAM_FAILURES = {
    "E601": ('agent A:\n    role: "{{agent:blank}}"\n', {}),
    "E602": ('agent A:\n    role: "{{team:title}}"\n', {}),
    "E603": ('agent A:\n    role: "{{agent:a}}"\n    values:\n        a: "{{agent:b}}"\n        b: "{{agent:a}}"\n', {}),
    "E604": ('agent A:\n    role: "A."\n    values:\n        key: "forbidden"\n', {}),
    "E606": ('team A: "Team"\n    role: "A."\n', {}),
    "E608": ('agent A:\n    role: "A."\n    values:\n        unit: "first"\n        unit: "second"\n', {}),
    "E609": ('agent A:\n    role: "A."\n    work: "Work"\n        roster r: "Roster"\n            who: "Who" = "{{agent:title}}"\n', {}),
    "E652": ('abstract agent B from "absent.md"\nagent A[B]:\n    inherit *\n', {}),
    "E653": ('abstract agent B from "role.md"\nagent A[B]:\n    inherit *\n', {"role.md": "Role.\n## Same\nOne.\n## Same\nTwo.\n"}),
}


def run_team_checks():
    for code, (source, files) in TEAM_FAILURES.items():
        with TemporaryDirectory() as directory:
            path = _write_prompt(directory, source)
            for name, text in files.items():
                (Path(directory) / name).write_text(text)
            try:
                compile_prompt(parse_file(path), "A")
            except CompileError as exc:
                _expect(exc.code == code, f"expected {code}, got {exc}")
            else:
                raise SmokeFailure(f"expected {code}")
