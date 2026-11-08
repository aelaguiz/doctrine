from __future__ import annotations

import tomllib
import subprocess
from functools import cache
import os
import re
from html import unescape
from os.path import relpath
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from doctrine import model

from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.markdown_links import markdown_destinations
from doctrine._compiler.teams import agent_parents
from doctrine.project_config import project_file_path, real_project_path


RUNTIMES = {"claude": ("CLAUDE.md", "utf16", 150000), "codex": ("AGENTS.md", "bytes", 32768)}


def text_size(text, runtime):
    return len(text.encode("utf-16-le")) // 2 if runtime == "claude" else len(text.encode("utf-8"))


def runtime_settings(target):
    def bad(detail):
        raise compile_error(code="E632", summary="Invalid runtime settings", detail=detail)

    settings = {}
    raw = target.project_config.raw_runtimes
    raw = {} if raw is None else raw
    base = target.project_config.config_dir
    for runtime in (*target.runtimes, *raw):
        if runtime not in RUNTIMES:
            bad(f"Unknown runtime `{runtime}`.")
    for runtime in target.runtimes:
        values = raw.get(runtime, {})
        for key in values.keys() - {"limit", "warn_at", "over", "external", "file_limit"}:
            bad(f"`{key}` for `{runtime}`: unknown setting.")
        limit = RUNTIMES[runtime][2]
        config = base / ".codex/config.toml"
        if runtime == "codex" and "limit" not in values and config.is_file():
            try:
                limit = tomllib.loads(config.read_text()).get("project_doc_max_bytes", limit)
            except (tomllib.TOMLDecodeError, UnicodeDecodeError):
                bad("`.codex/config.toml` for `codex`: invalid TOML.")
        values = {"limit": limit, "warn_at": 0.95, "over": "error", "external": [],
                  "file_limit": 150000 if runtime == "claude" else None, **values}
        for key, valid, detail in (
            (
                "limit",
                type(values["limit"]) is int and values["limit"] > 0,
                "must be a positive integer",
            ),
            (
                "warn_at",
                type(values["warn_at"]) in (int, float) and 0 < values["warn_at"] <= 1,
                "must be greater than 0 and at most 1",
            ),
            ("over", values["over"] in ("error", "warn"), "must be error or warn"),
            ("file_limit", values["file_limit"] is None or type(values["file_limit"]) is int and values["file_limit"] > 0, "must be a positive integer or none"),
        ):
            if not valid:
                bad(f"`{key}` for `{runtime}`: {detail}.")
        if not isinstance(values["external"], list) or any(
            not isinstance(item, dict) or not isinstance(item.get("path"), str)
            for item in values["external"]
        ):
            bad(f"`external` for `{runtime}`: each entry needs a string `path`.")
        for item in values["external"]:
            if "reserve" in item and type(item["reserve"]) is not int:
                bad(f"`reserve` for `{runtime}`: must be an integer.")
        settings[runtime] = values
    return settings


def validate_budget(field, settings):
    for key, value in field.items:
        if key not in RUNTIMES:
            detail = f"`budget` names unknown runtime `{key}`."
        elif value <= 0 or not value.is_integer():
            detail = f"`budget` for `{key}` must be a positive integer."
        elif key in settings and value > settings[key]["limit"]:
            detail = (
                f"`budget` for `{key}` is over the runtime's limit of {settings[key]['limit']}."
            )
        else:
            continue
        raise compile_error(code="E631", summary="Invalid budget", detail=detail)


def home_budgets(owner, unit, context):
    return [
        [field for field in declaration.fields if isinstance(field, model.BudgetField)]
        for declaration, _ in [(owner, unit), *agent_parents(context, owner, unit)]
    ]


def loaded_levels(homes, home):
    levels = [
        (level, data)
        for level, data in homes.items()
        if level == home or PurePosixPath(level) in PurePosixPath(home).parents
    ]
    return sorted(levels, key=lambda pair: len(PurePosixPath(pair[0]).parts))


def follow_imports(path, text, reader, seen, depth, config):
    if depth == 4:
        return []
    rows = []
    for start, end, is_import in markdown_destinations(text):
        if not is_import:
            continue
        imported = Path(os.path.abspath(path.parent / Path(text[start:end]).expanduser()))
        real = project_file_path(config, imported)
        if real in seen:
            continue
        seen.add(real)
        content = reader(real)
        if content is None:
            continue
        rows.append((imported, content))
        rows.extend(follow_imports(real, content, reader, seen, depth + 1, config))
    return rows


def home_loads(target, homes, files, settings, selected):
    loads = []
    config = target.project_config
    generated = {(target.output_dir / path).resolve(): content for path, content in files.items()
                 if isinstance(content, bytes)}
    generated.update({(target.output_dir / path).resolve(): files[str(PurePosixPath(path).parent / str(content))]
                      for path, content in files.items() if isinstance(content, Path)})
    for runtime, values in settings.items():
        external = []
        for item in values["external"]:
            path = project_file_path(target.project_config, item["path"])
            if path in generated or path.is_file():
                try:
                    text = (generated[path] if path in generated else path.read_bytes()).decode("utf-8")
                except UnicodeDecodeError:
                    raise compile_error(code="E632", summary="Invalid runtime settings",
                        detail=f"`external` for `{runtime}`: `{item['path']}` is not UTF-8.")
                size = text_size(text, runtime)
            elif "reserve" in item:
                text, size = "", item["reserve"]
            else:
                raise compile_error(
                    code="E633",
                    summary="External file missing",
                    detail=f"`{item['path']}` is listed for {runtime}, "
                    "but it is absent and has no `reserve`.",
                )
            external.append(
                {
                    "path": item["path"],
                    "size": size,
                    "kind": "external" if path in generated or path.is_file() else "reserved",
                    "text": text,
                    "on_disk": path.is_file(),
                }
            )
        values["external"] = external
    @cache  # homes share files, and a revision build reads each one through git
    def file_text(path):
        path = project_file_path(config, path)
        if path in generated:
            return generated[path].decode("utf-8", errors="replace")
        if config.revision:
            root, scratch, _, revision, overlays = config.revision
            if path.is_relative_to(scratch) and real_project_path(config, path) not in overlays:
                result = subprocess.run(["git", "show", f"{revision}:{path.relative_to(scratch)}"],
                                        cwd=root, capture_output=True)
                return result.stdout.decode("utf-8", errors="replace") if not result.returncode else None
        real = real_project_path(config, path)
        return real.read_bytes().decode("utf-8", errors="replace") if real.is_file() else None
    for home, data in homes.items():
        if home not in selected:
            continue
        levels = loaded_levels(homes, home)
        budgets = []
        declarations = [
            declaration
            for level, declaration in reversed(levels)
            if level == home or isinstance(declaration["owner"], model.Team)
        ]
        defaults = (
            declarations[:1]
            if isinstance(data["owner"], model.Team)
            else declarations[1:2] + declarations[:1]
        )
        fields = [
            *(declaration["budgets"][0] for declaration in declarations),
            *(fields for declaration in defaults for fields in declaration["budgets"][1:]),
        ]
        for group in fields:
            for field in group:
                validate_budget(field, settings)
                budgets.append(dict(field.items))
        runtimes = {}
        for runtime in target.runtimes:
            setting = settings[runtime]
            loaded = list(setting["external"])
            parts = {}
            on_demand = {}
            root = target.project_config.config_dir
            home_dir = target.output_dir / home
            by_folder = {(target.output_dir / level): (level, item)
                         for level, item in levels}
            folders = [root, *(root.joinpath(*home_dir.relative_to(root).parts[:i])
                               for i in range(1, len(home_dir.relative_to(root).parts) + 1))]
            for folder in folders:
                level, item = by_folder.get(folder, (None, None))
                candidate = folder / RUNTIMES[runtime][0]
                if item is None or str(PurePosixPath(level) / RUNTIMES[runtime][0]) not in files:
                    text = file_text(project_file_path(config, candidate))
                    if text is not None:
                        loaded.append({"path": relpath(candidate, root), "size": text_size(text, runtime),
                            "kind": "level", "text": text, "on_disk": real_project_path(config, candidate).is_file()})
                    if item is None:
                        continue
                path = str(PurePosixPath(level) / RUNTIMES[runtime][0])
                if path in files:
                    on_disk = (target.output_dir / path).is_file()
                    content = files[path]
                    if isinstance(content, Path):
                        target_path = str(PurePosixPath(level) / str(content))
                        content = files[target_path]
                        path = target_path
                    for entry in item["map"].entries:
                        if entry.always_on:
                            size = entry.size_utf16 if runtime == "claude" else entry.size_bytes
                            parts[entry.origin] = parts.get(entry.origin, 0) + size
                    text = content.decode()
                    loaded.append(
                        {
                            "path": path,
                            "size": text_size(text, runtime),
                            "kind": "home",
                            "text": text,
                            "on_disk": on_disk,
                        }
                    )
                for pointer in item["pointers"]:
                    path = (target.output_dir / pointer).resolve()
                    on_demand[relpath(path, target.project_config.config_dir)] = text_size(file_text(path), runtime)
                for ref, always_on in item["file_refs"]:
                    path = Path(ref[2])
                    if project_file_path(config, path).is_dir():
                        continue
                    name = relpath(real_project_path(config, path), real_project_path(config, root))
                    if ref[0] == "load" and always_on:
                        if runtime == "codex" and not any(file["path"] == name for file in loaded):
                            text = file_text(path)
                            loaded.append({"path": name, "size": text_size(text, runtime),
                                "kind": "read_first", "text": text, "on_disk": path.is_file()})
                    else:
                        on_demand[name] = text_size(file_text(path), runtime)
            expanded, seen = [], set()
            home_paths = {project_file_path(config, root / entry["path"])
                          for entry in loaded if entry["kind"] == "home"}
            for entry in loaded:
                path = project_file_path(config, root / entry["path"])
                if entry["kind"] == "external" and path in home_paths:
                    continue
                if path in seen:
                    continue
                seen.add(path)
                expanded.append(entry)
                if runtime == "claude" and entry["kind"] != "reserved":
                    for imported, text in follow_imports(path, entry["text"], file_text, seen, 0, config):
                        expanded.append({"path": relpath(real_project_path(config, imported), real_project_path(config, root)),
                            "size": text_size(text, runtime), "kind": "import", "text": text,
                            "on_disk": real_project_path(config, imported).is_file()})
            loaded = expanded
            loaded_paths = {((target.output_dir if entry["kind"] == "home" else root) / entry["path"]).resolve()
                            for entry in loaded}
            for entry in loaded:
                source = (target.output_dir if entry["kind"] == "home" else root) / entry["path"]
                text = entry["text"]
                for start, end, is_import in markdown_destinations(text):
                    if is_import:
                        continue
                    url = urlsplit(text[start:end])
                    if url.scheme or url.netloc or not url.path:
                        continue
                    path = re.sub(r"\\([ !\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", unquote(unescape(url.path)))
                    resolved = (source.parent / Path(path).expanduser()).resolve()
                    if (resolved.is_relative_to(root.resolve()) and resolved not in loaded_paths
                            and not project_file_path(config, resolved).is_dir()
                            and (content := file_text(resolved)) is not None):
                        on_demand[relpath(resolved, root)] = text_size(content, runtime)
            on_demand = {path: size for path, size in on_demand.items()
                         if not any(item["path"] == path for item in loaded)}
            limit = next(
                (budget[runtime] for budget in budgets if runtime in budget), setting["limit"]
            )
            total = sum(item["size"] for item in loaded if item["kind"] != "read_first")
            details_size = sum(
                text_size(files[path].decode(), runtime) for path in data["pointers"]
            )
            runtimes[runtime] = {
                "unit": RUNTIMES[runtime][1],
                "total": total,
                "limit": int(limit),
                "headroom": int(limit) - total,
                "files": loaded,
                "on_demand": [{"path": path, "size": size} for path, size in
                    sorted(on_demand.items(), key=lambda row: (-row[1], row[0]))],
                "details_size": details_size,
                "parts": [
                    {"origin": origin, "size": size}
                    for origin, size in sorted(parts.items(), key=lambda part: (-part[1], part[0]))
                ],
            }
        loads.append(
            {
                "home": home,
                "agent": data["owner"].name,
                "runtimes": runtimes,
                "drops": [
                    {"path": list(drop.path), "origin": drop.origin, "reason": drop.reason}
                    for drop in data["map"].drops
                ],
            }
        )
    return loads


def budget_findings(loads, settings):
    findings = []
    failed = False
    warned = set()
    for home in loads:
        for runtime, load in home["runtimes"].items():
            file_limit = settings[runtime]["file_limit"]
            for file in load["files"]:
                key = (runtime, file["path"])
                if (file["kind"] == "home" and file_limit is not None
                        and file["size"] > file_limit and key not in warned):
                    warned.add(key)
                    findings.append(
                        f"W309 long file: {file['path']} is {file['size']:,} "
                        f"of {file_limit:,} on {runtime}."
                    )
            if load["total"] > load["limit"] and settings[runtime]["over"] == "error":
                unit = "characters" if runtime == "claude" else "bytes"
                findings.append(
                    "E630 compile error: Over load budget\n\nDetail:\n"
                    f"- {home['home']} loads {load['total']:,} of {load['limit']:,} "
                    f"{unit} on {runtime}.\n- "
                    + biggest_parts(load["parts"]).replace("\n  ", "\n  - ")
                )
                failed = True
            elif load["total"] >= settings[runtime]["warn_at"] * load["limit"]:
                findings.append(
                    f"W306 {'over' if load['total'] > load['limit'] else 'near'} budget: "
                    f"{home['home']} loads {load['total']:,} "
                    f"of {load['limit']:,} on {runtime}."
                )
    return findings, failed


def biggest_parts(parts):
    lines = ["Biggest parts:", *(f"  {part['origin']}: {part['size']:,}" for part in parts[:5])]
    if len(parts) > 5:
        lines.append(
            f"  And {len(parts) - 5} smaller parts: {sum(part['size'] for part in parts[5:]):,}"
        )
    return "\n".join(lines)


def padded_rows(rows):
    widths = [max(len(row[column]) for row in rows) for column in range(len(rows[0]))]
    return "\n".join(
        "".join(value.ljust(width + 2) for value, width in zip(row, widths)).rstrip()
        for row in rows
    )


def has_home_file(load):
    return any(file["kind"] in ("home", "level") for file in load["files"])


def is_missing(file):
    return not file["on_disk"] and file["kind"] != "reserved"


def render_load(loads):
    if len(loads) != 1:
        rows = [("Home", "Runtime", "Load", "Limit", "Headroom")]
        rows.extend(
            (
                home["home"],
                runtime,
                f"{load['total']:,}" if has_home_file(load) else "no file",
                f"{load['limit']:,}",
                f"{load['headroom']:,}",
            )
            for home, runtime, load in sorted(
                (
                    (home, runtime, load)
                    for home in loads
                    for runtime, load in home["runtimes"].items()
                ),
                key=lambda row: (row[2]["headroom"], row[0]["home"], row[1]),
            )
        )
        return padded_rows(rows)
    home = loads[0]
    blocks = []
    for runtime, load in home["runtimes"].items():
        if not has_home_file(load):
            blocks.append(
                f"{home['home']} on {runtime}: no {RUNTIMES[runtime][0]} here, "
                f"so {runtime} loads nothing from this home"
            )
            continue
        headroom = load["headroom"]
        unit = "characters" if runtime == "claude" else "bytes"
        read_first = [file for file in load["files"] if file["kind"] == "read_first"]
        blocks.append(
            f"{home['home']} on {runtime}: {load['total']:,} of {load['limit']:,} "
            f"{unit}, {abs(headroom):,} {'left' if headroom >= 0 else 'over'}"
            + (f", plus {sum(file['size'] for file in read_first):,} to read first" if read_first else "")
        )
        if load["files"]:
            rows = [
                (
                    "  " + file["path"],
                    f"{file['size']:,}",
                    "read first" if file["kind"] == "read_first" else "hand-written" if file["kind"] == "level" else "import" if file["kind"] == "import" else "missing" if is_missing(file)
                    else "" if file["kind"] == "home" else file["kind"],
                )
                for file in load["files"]
            ]
            blocks.append("Files:\n" + padded_rows(rows))
        if load["parts"]:
            blocks.append(biggest_parts(load["parts"]))
        if load["on_demand"]:
            blocks.append("On demand:\n" + padded_rows([
                ("  " + file["path"], f"{file['size']:,}") for file in load["on_demand"]]))
    if home["drops"]:
        blocks.append(
            "Dropped:\n"
            + "\n".join(
                f"  {'.'.join(drop['path'])} from {drop['origin']}: {drop['reason']}"
                for drop in home["drops"]
            )
        )
    return "\n\n".join(blocks)
