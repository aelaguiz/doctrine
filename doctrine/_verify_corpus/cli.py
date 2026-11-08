from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from contextlib import chdir, redirect_stderr, redirect_stdout
from pathlib import Path

from doctrine.cli import main
from doctrine.homes import HEADER


def run_cli_contract(case):
    spec = case.cli
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        shutil.copytree(case.example_dir / spec["project"], project, symlinks=True)
        if "--rev" in spec["args"]:
            for args in (("init", "-q"), ("add", "."),
                         ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
                          "commit", "-qm", "Fixture [skip ci]")):
                subprocess.run(["git", *args], cwd=project, check=True, capture_output=True)
        with chdir(project):
            for args in (*spec.get("setup", []), spec["args"]):
                if args is spec["args"]:
                    for name in spec.get("remove", []):
                        (project / name).unlink()
                    for name, content in spec.get("edit", {}).items():
                        path = project / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(content, encoding="utf-8")
                stdout, stderr = io.StringIO(), io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        code = main(args)
                    except SystemExit as exc:
                        code = exc.code
                expected = spec["expected_exit"] if args is spec["args"] else 0
                assert code == expected, (f"Expected exit {expected}, got {code}.\n"
                                          f"{stdout.getvalue()}\n{stderr.getvalue()}")
            output, errors = stdout.getvalue(), stderr.getvalue()
            if "expected_stdout_lines" in spec:
                assert output.splitlines() == spec["expected_stdout_lines"], output
            for part in spec.get("stdout_contains", []):
                assert part in output, output
            for part in spec.get("stderr_contains", []):
                assert part in errors, errors
            for name, lines in spec.get("expected_file_lines", {}).items():
                text = (project / name).read_text(encoding="utf-8")
                header = HEADER.match(text)
                if header:
                    text = text[header.end():]
                    assert hashlib.sha256(text.encode()).hexdigest()[:12] == header[1], name
                assert text.splitlines() == lines, f"{name}:\n{text}"
            for name, target in spec.get("expected_links", {}).items():
                assert os.readlink(project / name) == target, name
            for name, expected_file in spec.get("expected_files", {}).items():
                actual = (project / name).read_bytes()
                expected = (case.example_dir / expected_file).read_bytes()
                if name.endswith(".json"):
                    assert json.loads(actual) == json.loads(expected), name
                else:
                    assert actual == expected, name
            for name in spec.get("absent_files", []):
                assert not (project / name).exists() and not (project / name).is_symlink(), name
