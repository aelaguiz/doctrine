from __future__ import annotations

import argparse
import io
import os
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
from contextlib import contextmanager
from pathlib import Path

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine.emit_common import resolve_pyproject_path
from doctrine.parser import parse_file


def copy_overlay(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.copy2(source, destination)
    else:
        destination.unlink(missing_ok=True)


@contextmanager
def revision_source(args):
    config = resolve_pyproject_path(args.pyproject)
    root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=config.parent, text=True,
            stderr=subprocess.PIPE,
        ).strip()
    )
    for path in args.overlays:
        if not (Path.cwd() / path).resolve().is_relative_to(root):
            raise argparse.ArgumentError(None, f"--with path is outside the repository: {path}")
    valid = subprocess.run(
        ["git", "rev-parse", "--verify", args.rev + "^{commit}"], cwd=root, capture_output=True
    )
    if valid.returncode:
        raise compile_error(
            code="E641",
            summary="Bad revision",
            detail=f"`{args.rev}` is not a revision in this repository.",
        )
    revision = valid.stdout.decode().strip()
    relative = config.relative_to(root)
    with tempfile.TemporaryDirectory() as temporary:
        scratch = Path(temporary).resolve()
        paths = (root, scratch, config.parent, revision,
                 tuple((Path.cwd() / path).resolve() for path in args.overlays))

        def extract(paths):
            present = [
                str(path)
                for path in paths
                if subprocess.run(
                    ["git", "cat-file", "-e", f"{revision}:{path}"], cwd=root, capture_output=True
                ).returncode
                == 0
            ]
            if present:
                archive = subprocess.check_output(
                    ["git", "archive", revision, "--", *present], cwd=root
                )
                with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
                    stream.extractall(scratch, filter="data")
            for path in args.overlays:
                source = (Path.cwd() / path).resolve()
                name = source.relative_to(root)
                if name in paths or any(parent in paths for parent in name.parents):
                    destination = scratch / name
                    copy_overlay(source, destination)

        extract([relative])
        project = scratch / relative
        raw = tomllib.loads(project.read_text())["tool"]["doctrine"]
        targets = raw["emit"]["targets"]
        if args.target:
            selected = next((target for target in targets if target["name"] == args.target), None)
            if selected is None:
                yield project, (), config.parent, paths
                return
            targets = [
                target for target in targets if target["output_dir"] == selected["output_dir"]
            ]
        prompt_roots = set()
        for target in targets:
            path = relative.parent / target["entrypoint"]
            prompt_roots.add(next(parent for parent in path.parents if parent.name == "prompts"))
        prompt_roots.update(
            Path(os.path.normpath(relative.parent / path))
            for path in raw.get("compile", {}).get("additional_prompt_roots", [])
        )
        extract([*prompt_roots, relative.parent / ".codex/config.toml"])
        extra = set()
        for prompt_root in prompt_roots:
            for path in (scratch / prompt_root).rglob("*.prompt"):
                for declaration in parse_file(path).declarations:
                    if isinstance(declaration, model.FileDecl) and declaration.body is None and not declaration.markdown_path:
                        file_path = (config.parent / Path(declaration.path).expanduser()).resolve()
                        if file_path.is_relative_to(root):
                            extra.add(file_path.relative_to(root))
                    if (
                        isinstance(declaration, (model.Agent, model.WorkflowDecl, model.FileDecl, model.SkillPackageDecl))
                        and declaration.markdown_path
                    ):
                        extra.add(
                            Path(os.path.normpath(relative.parent / declaration.markdown_path))
                        )
        for runtime in raw.get("runtimes", {}).values():
            for item in runtime.get("external", []):
                file_path = (config.parent / Path(item["path"]).expanduser()).resolve()
                if file_path.is_relative_to(root):
                    extra.add(file_path.relative_to(root))
        extract(list(extra))
        yield project, tuple(target["name"] for target in targets), config.parent, paths
