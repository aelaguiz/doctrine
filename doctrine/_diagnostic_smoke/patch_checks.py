from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file
from doctrine._diagnostic_smoke.fixtures import SmokeFailure, _expect, _write_prompt


PATCH_FAILURES = {
    "E134": (
        "agent A:\n"
        '    role: "A."\n'
        '    work: "Work"\n'
        "        table calls_table:\n"
        '            "Text."\n'
    ),
    "E605": (
        "agent A:\n"
        '    role: "A."\n'
        '    work: "Work"\n'
        '        "```bash"\n'
        '        "make all"\n'
        '        "```"\n'
    ),
    "E610": (
        "abstract agent Base:\n"
        '    role: "A."\n'
        "agent A[Base]:\n"
        "    inherit role\n"
        '    drop missing: "Gone."\n'
    ),
    "E611": (
        "abstract agent Base:\n"
        '    role: "A."\n'
        '    work: "Work"\n'
        "        paragraph lead:\n"
        '            "Text."\n'
        "agent A[Base]:\n"
        "    inherit role\n"
        '    drop work.lead.child: "Gone."\n'
    ),
    "E612": ('abstract agent Base:\n    role: "A."\nagent A[Base]:\n    drop role: "Gone."\n'),
    "E614": (
        'agent A:\n    role: "A."\n    work: "Work"\n        super\n'
    ),
    "E613": (
        'abstract agent Base:\n    role: "A."\nagent A[Base]:\n    inherit *\n    inherit *\n'
    ),
}


def run_patch_checks():
    for code, source in PATCH_FAILURES.items():
        with TemporaryDirectory() as directory:
            path = _write_prompt(directory, source)
            try:
                compile_prompt(parse_file(path), "A")
            except Exception as exc:
                _expect(getattr(exc, "code", None) == code, f"expected {code}, got {exc}")
            else:
                raise SmokeFailure(f"expected {code}")
