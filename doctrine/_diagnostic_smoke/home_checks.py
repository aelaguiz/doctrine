from contextlib import chdir, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.cli import main
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file
from doctrine._diagnostic_smoke.fixtures import _expect


HOME_FAILURES = {
    "E607": ('team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: "Test."\nteam Other: "Other"\n    home: "t/qa"\n    role: "Other."\n', ''),
    "E621": ('abstract agent R:\n    role: "Test."\n    work: "Work"\n        details:\n            "{{agent:title}}"\nteam T: "Team"\n    home: "t"\n    member qa[R]: "QA"\n', ''),
    "E630": ('team T: "Team"\n    home: "t"\n    role: "Test."\n    budget:\n        codex: 1\n', ''),
    "E631": ('team T: "Team"\n    home: "t"\n    role: "Test."\n    budget:\n        codex: 0\n', ''),
    "E632": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', '[tool.doctrine.runtimes.codex]\nlimit = 0\n'),
    "E633": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', '[tool.doctrine.runtimes.codex]\nexternal = [{path = "absent.md"}]\n'),
    "E634": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ''),
    "E640": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ''),
    "E641": ('team T: "Team"\n    home: "t"\n    role: "Test."\n', ''),
}


def run_home_checks():
    for code, (source, settings) in HOME_FAILURES.items():
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            (root / "prompts/AGENTS.prompt").write_text(source)
            (root / "pyproject.toml").write_text('[[tool.doctrine.emit.targets]]\nname = "homes"\nentrypoint = "prompts/AGENTS.prompt"\noutput_dir = "."\n' + settings)
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
            error = StringIO()
            with chdir(root), redirect_stderr(error), redirect_stdout(StringIO()):
                result = main(args)
            _expect(result == 1 and code in error.getvalue(), f"expected {code}, got {result}: {error.getvalue()}")
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
