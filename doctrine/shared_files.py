import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath

from doctrine import model
from doctrine._compiler.constants import FILE_REF_MARKER
from doctrine._compiler.details import reject_details
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.late_binding import reject_case_links, reject_late_roots
from doctrine._compiler.markdown_links import render_file_refs
from doctrine._compiler.markdown_reader import fenced_lines, heading_anchor
from doctrine.renderer import render_readable_block
from doctrine.passages import place_passages


HEADER = re.compile(
    r"<!-- doctrine sha256=([a-f0-9]{12}) source=(.*)\. Do not edit\. "
    r'Run: doctrine where "<words>" -->\n\n'
)


def header_match(text, *, frontmatter=False):
    if frontmatter and text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            return HEADER.match(text, end + 5)
    return HEADER.match(text)


def file_state(path, fresh, recorded_hash=None):
    if path.is_symlink():
        if recorded_hash is None and path.name == "CLAUDE.md" and os.readlink(path) == "AGENTS.md":
            return "unchanged" if isinstance(fresh, Path) else "stale"
        return "edited"
    if not path.exists():
        return "missing"
    content = path.read_bytes()
    if recorded_hash is not None:
        if hashlib.sha256(content).hexdigest() != recorded_hash:
            return "edited"
        return "unchanged" if content == fresh else "stale"
    if path.suffix == ".md":
        try:
            text = content.decode()
        except UnicodeDecodeError:
            return "edited"
        match = header_match(text, frontmatter=path.name == "SKILL.md")
        if (
            match is None
            or hashlib.sha256(text[match.end() :].encode()).hexdigest()[:12] != match[1]
        ):
            return "edited"
    return "unchanged" if content == fresh else "stale"


def with_header(text, source):
    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
    return (
        f"<!-- doctrine sha256={digest} source={source}. Do not edit. "
        f'Run: doctrine where "<words>" -->\n\n{text}'
    )


def compile_shared_files(target, context, files, declarations, referenced, whole):
    written, links = {}, {}
    pending = [(unit, decl) for unit, decl in declarations if decl.body is not None and (
        (whole and context.session.flow_for_unit(unit) is context.session.root_flow)
        or (target.output_dir / decl.path).resolve() in referenced)]
    while pending:
        unit, decl = pending.pop(0)
        path = str(PurePosixPath(decl.path))
        if (target.output_dir / path).is_dir():
            raise compile_error(code="E652", summary="Missing Markdown source",
                detail=f"`{decl.name}` has a body, so `{decl.path}` must be a file, but it's a folder.")
        if path in written:
            if written[path] is not decl:
                raise compile_error(code="E607", summary="Two homes, one path",
                    detail=f"`{decl.name}` and `{written[path].name}` both land at `{path}`.")
            continue
        if path in files:
            raise compile_error(code="E607", summary="Two homes, one path",
                detail=f"`{decl.name}` and another output both land at `{path}`.")
        written[path] = decl
        if decl.markdown_path:
            source_path = (target.project_config.config_dir / decl.markdown_path).resolve()
            if source_path == (target.output_dir / path).resolve():
                raise compile_error(code="E656", summary="Markdown source is the output",
                    detail=f"`{decl.name}` reads and writes `{decl.path}`. Choose a different source or output path.",
                    path=unit.prompt_file.source_path, source_span=decl.source_span)
            raw = source_path.read_bytes().decode("utf-8")
            if context.session.passages is not None:
                raw = place_passages(raw, context.session.passages, path=source_path)
            links[path] = []
            source = os.path.relpath(source_path, target.project_config.config_dir)
            files[path] = with_header(raw, source).encode()
            continue
        reject_details(decl.body, "a shared file")
        reject_case_links(decl.body, unit=unit)
        reject_late_roots(decl.body, unit=unit, why="a shared file belongs to no home")
        document = model.DocumentDecl(decl.name, decl.body, render_profile_ref=decl.render_profile_ref,
                                      source_span=decl.source_span)
        body = context._compile_document_decl(document, unit=unit)
        raw = render_readable_block(body, depth=1) + "\n"
        refs = [Path(json.loads(match[1])[2]) for match in FILE_REF_MARKER.finditer(raw)]
        referenced.update(refs)
        links[path] = [str(ref.relative_to(target.output_dir)) for ref in refs if ref.is_relative_to(target.output_dir)]
        pending.extend((other_unit, other) for other_unit, other in declarations
                       if other.body is not None and other.path not in written
                       and (target.output_dir / other.path).resolve() in referenced)
        source = os.path.relpath(unit.prompt_file.source_path, target.project_config.config_dir)
        files[path] = with_header(render_file_refs(raw, (target.output_dir / path).parent, target.project_config), source).encode()
    for path in written:
        seen = {}
        for line, inside in fenced_lines(files[path].decode().splitlines()):
            if not inside and (heading := re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*$", line)):
                heading_anchor(heading[1], seen)
        for linked_path, anchor, name in context.session.file_section_links:
            if Path(linked_path) == target.output_dir / path and seen.get(anchor, 0) > 1:
                raise compile_error(code="E637", summary="Dead case link",
                    detail=f"`{name}` shares its heading with another in `{path}`. Give it a title of its own.")
    return written, links
