from __future__ import annotations

import os
from pathlib import Path

from doctrine._compiler.diagnostics import compile_error
from doctrine.compiler import CompilationSession
from doctrine.emit_skill import (
    _should_emit_skill_package_contract_json,
    _target_skill_package_decl,
    render_skill_package_contract_json,
    render_skill_package_markdown,
)
from doctrine.parser import parse_file
from doctrine.shared_files import with_header


def project_path(root, value, label):
    path = (root / value).resolve()
    if not value or Path(value).is_absolute() or not path.is_relative_to(root):
        raise compile_error(code="E520", summary="Path must stay within project root",
                            detail=f"{label} `{value}` must be relative to the project.")
    return path


def compile_project_skills(target, files):
    if target.skills is None:
        return {}, []
    root = target.project_config.config_dir.resolve()
    source = project_path(root, target.skills["source"], "Skill source")
    default = project_path(root, target.skills["install"], "Skill install folder")
    if not source.is_dir():
        raise compile_error(code="E550", summary="Skill source must be a directory",
                            detail=f"Skill source `{target.skills['source']}` is not a folder.")
    result, sources, destinations = {}, [], {}
    for entry in sorted(source.glob("*/SKILL.prompt")):
        if not entry.resolve().is_relative_to(root):
            raise compile_error(code="E521", summary="Skill source must stay within project root",
                                detail=f"Skill source `{entry}` is outside the project.")
        session = CompilationSession(parse_file(entry), project_config=target.project_config)
        compiled = session.compile_skill_package()
        package = _target_skill_package_decl(session)
        dest = (project_path(root, package.install, "Skill install folder")
                if package.install is not None else (default / entry.parent.name).resolve())
        if not dest.is_relative_to(root):
            raise compile_error(code="E520", summary="Path must stay within project root",
                                detail=f"Skill install folder `{dest}` is outside the project.")
        for other, prior in destinations.items():
            if dest == other:
                raise compile_error(code="E607", summary="Two skills, one path",
                                    detail=f"`{prior}` and `{entry}` both install at `{dest}`.")
        destinations[dest] = entry
        source_name = os.path.relpath(entry, root)
        markdown = render_skill_package_markdown(compiled)
        frontmatter, body = markdown.split("\n---\n", 1)
        body = body.removeprefix("\n")
        outputs = {"SKILL.md": (frontmatter + "\n---\n" + with_header(body, source_name)).encode()}
        if _should_emit_skill_package_contract_json(compiled):
            outputs["SKILL.contract.json"] = render_skill_package_contract_json(compiled).encode()
        outputs.update({item.path: item.content for item in compiled.files})
        for name, content in outputs.items():
            path = dest / name
            if not path.resolve().is_relative_to(root):
                raise compile_error(code="E520", summary="Path must stay within project root",
                                    detail=f"Skill output `{path}` is outside the project.")
            relative = os.path.relpath(path, target.output_dir)
            if relative in files or relative in result or path == entry:
                raise compile_error(code="E607", summary="Two outputs, one path",
                                    detail=f"Skill output `{relative}` shares a path with another output.")
            result[relative] = content
        sources.append((entry, compiled.name, markdown, session))
    return result, sources
