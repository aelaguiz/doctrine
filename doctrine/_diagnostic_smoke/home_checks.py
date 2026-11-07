from contextlib import chdir, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.cli import main
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine._diagnostic_smoke.fixtures import _expect


HOME_DIAGNOSTICS = {
    "E607": (
        (
            'team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: '
            '"Test."\nteam Other: "Other"\n    home: "t/qa"\n    role: "Other."\n'
        ),
        "",
    ),
    "E621": (
        (
            'abstract agent R:\n    role: "Test."\n    work: "Work"\n        '
            'details:\n            "{{agent:title}}"\nteam T: "Team"\n    home: '
            '"t"\n    member qa[R]: "QA"\n'
        ),
        "",
    ),
    "E630": (
        ('team T: "Team"\n    home: "t"\n    role: "Test."\n    budget:\n        codex: 1\n'),
        "",
    ),
    "E631": (
        ('team T: "Team"\n    home: "t"\n    role: "Test."\n    budget:\n        codex: 0\n'),
        "",
    ),
    "E632": (
        'team T: "Team"\n    home: "t"\n    role: "Test."\n',
        "[tool.doctrine.runtimes.codex]\nlimit = 0\n",
    ),
    "E633": (
        'team T: "Team"\n    home: "t"\n    role: "Test."\n',
        '[tool.doctrine.runtimes.codex]\nexternal = [{path = "absent.md"}]\n',
    ),
    "E634": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ""),
    "E640": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ""),
    "E650": ('person P: "Person"\nquote Q: "Words"\n    by: P\n    on: "bad"\nteam T: "Team"\n    home: "t"\n    role: "{{Q}}"\n', ""),
    "W305": ('person P: "Person"\nquote Q: "Words"\n    by: P\n    on: "2026-11-05"\nteam T: "Team"\n    home: "t"\n    role: "Test."\n', ""),
    "E651": ('person P: "Person"\n    owns:\n        Missing\nteam T: "Team"\n    home: "t"\n    role: "Test."\n', ""),
    "E641": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ""),
    "W306": (
        'team T: "Team"\n    home: "t"\n    role: "Test."\n',
        "[tool.doctrine.runtimes.codex]\nlimit = 100\nover = \"warn\"\n",
    ),
    "W307": (
        (
            'team T: "Team"\n    home: "."\n    role: "Shared."\n    member qa: '
            '"QA"\n        role: "Test."\n'
        ),
        "",
    ),
}


HOME_DIAGNOSTICS.update({
    "RULE006": (
        'workflow Lesson: "Lesson"\n    "Use numbers."\nteam T: "Team"\n    home: "t"\n'
        '    member qa: "QA"\n        role: "Test."\nrule R: "Load lesson"\n    scope:\n'
        '        member: qa\n    assertions:\n        requires load Lesson\n'
        '    message: "Use numbers."\n', "",
    ),
    "RULE007": (
        'workflow Lesson: "Lesson"\n    "Use numbers."\nteam T: "Team"\n    home: "t"\n'
        '    member qa: "QA"\n        role: "Test."\n        work: Lesson\nrule R: "No lesson"\n'
        '    scope:\n        member: qa\n    assertions:\n        forbids load Lesson\n'
        '    message: "No lesson."\n', "",
    ),
    "W301": (
        'team T: "Team"\n    home: "t"\n'
        '    role: "Read every change with care and test each part that a user will meet today."\n'
        '    member qa: "QA"\n'
        '        role: "Read every change with care and test each part '
        'that a user will meet today."\n', "",
    ),
    "W302": (
        'workflow Shared: "Shared"\n    "Shared text."\nteam T: "Team"\n    home: "t"\n'
        '    work: Shared\n    member qa: "QA"\n        role: "Test."\n        work: Shared\n', "",
    ),
    "E660": (
        'output Note: "Note"\n    target: Message\n        to: "reader"\n    shape: Comment\n'
        'team T: "Team"\n    home: "t"\n    member a: "A"\n        role: "Test."\n'
        '        outputs: "Outputs"\n            Note\n', "",
    ),
    "W303": (
        'output Note: "Note"\n    target: Message\n        to: T.reader\n'
        'team T: "Team"\n    home: "t"\n    member reader: "Reader"\n        role: "Test."\n'
        '    member sender: "Sender"\n        role: "Send."\n'
        '        outputs: "Outputs"\n            Note\n', "",
    ),
    "W304": (
        'team T: "Team"\n    home: "t"\n    role: "Test."\n'
        '    values:\n        unused: "No reader."\n', "",
    ),
})


def run_home_checks():
    for code, (source, settings) in HOME_DIAGNOSTICS.items():
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            (root / "prompts/AGENTS.prompt").write_text(source)
            (root / "pyproject.toml").write_text(
                (
                    '[[tool.doctrine.emit.targets]]\nname = "homes"\nentrypoint = '
                    '"prompts/AGENTS.prompt"\noutput_dir = "."\n'
                )
                + settings
            )
            args = ["check"]
            if code == "E634":
                (root / "t").mkdir()
                (root / "t/AGENTS.md").write_text("Hand-written.\n")
                args = ["build"]
            elif code == "E640":
                args = ["build", "absent"]
            elif code == "E641":
                args = ["build", "--rev", "not-a-revision"]
                args += ["--pyproject", str(Path(__file__).resolve().parents[2] / "pyproject.toml")]
            elif code == "W306":
                args = ["build"]
            elif code == "W307":
                args = ["build", "T.qa"]
            error = StringIO()
            with chdir(root), redirect_stderr(error), redirect_stdout(StringIO()):
                result = main(args)
            _expect(
                result == (0 if code.startswith("W") else 1) and code in error.getvalue(),
                f"expected {code}, got {result}: {error.getvalue()}",
            )
    with TemporaryDirectory() as directory:
        path = Path(directory) / "prompts/SKILL.prompt"
        path.parent.mkdir()
        path.write_text('skill package S: "Skill"\n    details:\n        "Long case."\n')
        try:
            CompilationSession(parse_file(path)).compile_skill_package("S")
        except CompileError as error:
            _expect(error.code == "E620", f"expected E620, got {error}")
        else:
            _expect(False, "expected E620")
