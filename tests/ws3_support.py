from __future__ import annotations

import io
import shutil
import tempfile
from contextlib import chdir, redirect_stderr, redirect_stdout
from pathlib import Path

from doctrine.cli import main
from doctrine.emit_common import load_emit_targets
from doctrine.homes import compile_homes
from doctrine.runtime_load import home_loads, runtime_settings


class HomeProject:
    def project(self, source=None, *, example="184_doctrine_build_modes", fixture="project", runtimes='["claude", "codex"]', settings=""):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        if source is None:
            shutil.copytree(Path(__file__).resolve().parents[1] / "examples" / example / fixture, root, dirs_exist_ok=True)
        else:
            (root / "prompts").mkdir()
            (root / "prompts/AGENTS.prompt").write_text(source)
            (root / "pyproject.toml").write_text(f'[[tool.doctrine.emit.targets]]\nname = "homes"\nentrypoint = "prompts/AGENTS.prompt"\noutput_dir = "."\nruntimes = {runtimes}\n{settings}')
        return root

    def cli(self, root, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with chdir(root), redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = main(list(args))
            except SystemExit as error:
                code = error.code
        return code, stdout.getvalue(), stderr.getvalue()

    def loads(self, root):
        target = load_emit_targets(root / "pyproject.toml")["homes"]
        homes, files = compile_homes(target)
        return home_loads(target, homes, files, runtime_settings(target))
