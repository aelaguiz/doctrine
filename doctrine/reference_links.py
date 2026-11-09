from __future__ import annotations

import re
from html import unescape
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_links import markdown_destinations


def check_settings(config):
    settings = config.raw_check or {}
    if not isinstance(settings, dict) or not ({"raw_links", "reference"} & settings.keys()):
        return "off", []
    mode = settings.get("raw_links", "off")
    if mode not in ("off", "error") or not isinstance(mode, str):
        raise compile_error(code="E639", summary="Invalid check settings", detail="`raw_links` must be `off` or `error`.")
    entries = settings.get("reference", [])
    if not isinstance(entries, list):
        raise compile_error(code="E639", summary="Invalid check settings", detail="`reference` must be an array of paths.")
    for entry in entries:
        suffix = isinstance(entry, str) and entry.startswith("*")  # `*-record.md`: any name ending so
        if (not isinstance(entry, str) or not entry or entry.startswith(("/", "!"))
                or (suffix and (len(entry) < 2 or entry[1] == "." or "/" in entry))
                or any(char in entry[suffix:] for char in "*?[]\\")
                or any(part in ("", ".", "..") for part in entry.rstrip("/").split("/"))
                or entry.endswith("//")):
            raise compile_error(code="E639", summary="Invalid check settings", detail=f"Invalid reference entry: {entry!r}.")
    return mode, entries


def links(target, files):
    for name, content in files.items():
        if not name.endswith(".md") or isinstance(content, Path):
            continue
        text = content.decode()
        for start, end, is_import in markdown_destinations(text):
            if is_import and text[end:].split("\n", 1)[0].strip():
                continue
            dest = text[start:end]
            url = urlsplit(dest)
            if url.scheme or url.netloc or not url.path:
                continue
            path = re.sub(r"\\([ !\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", unquote(unescape(url.path)))
            resolved = ((target.output_dir / name).parent / Path(path).expanduser()).resolve()
            yield name, dest, resolved


def matches(entry, path):
    if entry.startswith("*"):
        return path.name.endswith(entry[1:])
    folder = entry.endswith("/")
    parts = PurePosixPath(entry.rstrip("/")).parts
    if folder:
        parents = path.parts[:-1]
        return parts[0] in parents if len(parts) == 1 else parents[:len(parts)] == parts
    return path.name == entry if len(parts) == 1 else path.parts == parts
