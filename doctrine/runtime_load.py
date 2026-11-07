from __future__ import annotations

import tomllib
from pathlib import Path, PurePosixPath

from doctrine import model

from doctrine._compiler.diagnostics import compile_error


RUNTIMES = {"claude": ("CLAUDE.md", "utf16", 150000), "codex": ("AGENTS.md", "bytes", 32768)}


def text_size(text, runtime):
    return len(text.encode("utf-16-le")) // 2 if runtime == "claude" else len(text.encode("utf-8"))


def runtime_settings(target):
    settings = {}
    raw = target.project_config.raw_runtimes
    raw = {} if raw is None else raw
    base = target.project_config.config_dir
    for runtime in (*target.runtimes, *raw):
        if runtime not in RUNTIMES:
            raise compile_error(code="E632", summary="Invalid runtime settings", detail=f"Unknown runtime `{runtime}`.")
    for runtime in RUNTIMES:
        values = raw.get(runtime, {})
        limit = RUNTIMES[runtime][2]
        config = base / ".codex/config.toml"
        if runtime == "codex" and "limit" not in values and config.is_file():
            limit = tomllib.loads(config.read_text()).get("project_doc_max_bytes", limit)
        values = {"limit": limit, "warn_at": .95, "over": "error", "external": [], **values}
        for key, valid, detail in (
            ("limit", type(values["limit"]) is int and values["limit"] > 0, "must be a positive integer"),
            ("warn_at", type(values["warn_at"]) in (int, float) and 0 < values["warn_at"] <= 1, "must be greater than 0 and at most 1"),
            ("over", values["over"] in ("error", "warn"), "must be error or warn"),
        ):
            if not valid:
                raise compile_error(code="E632", summary="Invalid runtime settings", detail=f"`{key}` for `{runtime}`: {detail}.")
        external = []
        for item in values["external"]:
            path = Path(item["path"]).expanduser()
            path = path if path.is_absolute() else base / path
            if path.is_file():
                text = path.read_bytes().decode("utf-8")
                size = text_size(text, runtime)
            elif "reserve" in item:
                text, size = "", item["reserve"]
            else:
                raise compile_error(code="E633", summary="External file missing", detail=f"`{item['path']}` is listed for {runtime}, but it is absent and has no `reserve`.")
            external.append({"path": item["path"], "size": size, "kind": "external" if path.is_file() else "reserved", "text": text})
        settings[runtime] = {**values, "external": external}
    return settings


def validate_budget(field, settings):
    for key, value in field.items:
        if key not in RUNTIMES:
            detail = f"`budget` names unknown runtime `{key}`."
        elif value <= 0 or not value.is_integer():
            detail = f"`budget` for `{key}` must be a positive integer."
        elif value > settings[key]["limit"]:
            detail = f"`budget` for `{key}` is over the runtime's limit of {settings[key]['limit']}."
        else:
            continue
        raise compile_error(code="E631", summary="Invalid budget", detail=detail)


def home_loads(target, homes, files, settings):
    loads = []
    for home, data in homes.items():
        budgets = []
        owner = data["owner"]
        team = homes[str(PurePosixPath(home).parent)]["owner"] if isinstance(owner, model.Member) else owner
        chain = [data]
        if team is not owner:
            chain.append(homes[str(PurePosixPath(home).parent)])
        chain.extend(item for level, item in sorted(homes.items(), key=lambda pair: len(PurePosixPath(pair[0]).parts), reverse=True)
                     if isinstance(item["owner"], model.Team) and PurePosixPath(level) in PurePosixPath(home).parents and item not in chain)
        for declaration in chain:
            for field in declaration["budgets"]:
                validate_budget(field, settings)
                budgets.append(dict(field.items))
        runtimes = {}
        for runtime in target.runtimes or ("codex",):
            setting = settings[runtime]
            loaded = list(setting["external"])
            parts = {}
            for level, item in sorted(homes.items(), key=lambda pair: len(PurePosixPath(pair[0]).parts)):
                if level == home or PurePosixPath(level) in PurePosixPath(home).parents:
                    path = str(PurePosixPath(level) / RUNTIMES[runtime][0])
                    if path in files:
                        content = files[path]
                        if isinstance(content, Path):
                            path = str(PurePosixPath(level) / str(content))
                            content = files[path]
                        for entry in item["map"].entries:
                            if entry.always_on:
                                parts[entry.origin] = parts.get(entry.origin, 0) + (entry.size_utf16 if runtime == "claude" else entry.size_bytes)
                        text = content.decode()
                        loaded.append({"path": path, "size": text_size(text, runtime), "kind": "home", "text": text})
            limit = next((budget[runtime] for budget in budgets if runtime in budget), setting["limit"])
            total = sum(item["size"] for item in loaded)
            details_size = sum(text_size(files[path].decode(), runtime) for path in data["pointers"])
            runtimes[runtime] = {"unit": RUNTIMES[runtime][1], "total": total, "limit": int(limit),
                "headroom": int(limit) - total, "files": loaded, "details_size": details_size,
                "parts": [{"origin": origin, "size": size} for origin, size in sorted(parts.items(), key=lambda part: (-part[1], part[0]))]}
        loads.append({"home": home, "agent": owner.name, "runtimes": runtimes,
            "drops": [{"path": list(drop.path), "origin": drop.origin, "reason": drop.reason} for drop in data["map"].drops]})
    return loads


def budget_findings(loads, settings, *, build=False):
    findings = []
    failed = False
    for home in loads:
        for runtime, load in home["runtimes"].items():
            if load["total"] > load["limit"] and not build and settings[runtime]["over"] == "error":
                findings.append("E630 compile error: Over load budget\n\nDetail:\n"
                    f"- {home['home']} loads {load['total']:,} of {load['limit']:,} {'characters' if runtime == 'claude' else 'bytes'} on {runtime}.\n- "
                    + biggest_parts(load["parts"]).replace("\n  ", "\n  - "))
                failed = True
            elif load["total"] >= settings[runtime]["warn_at"] * load["limit"]:
                findings.append(f"W306 near budget: {home['home']} loads {load['total']:,} of {load['limit']:,} on {runtime}.")
    return findings, failed


def biggest_parts(parts):
    lines = ["Biggest parts:", *(f"  {part['origin']}: {part['size']:,}" for part in parts[:5])]
    if len(parts) > 5:
        lines.append(f"  And {len(parts) - 5} smaller parts: {sum(part['size'] for part in parts[5:]):,}")
    return "\n".join(lines)


def padded_rows(rows):
    widths = [max(len(row[column]) for row in rows) for column in range(len(rows[0]))]
    return "\n".join("".join(value.ljust(width + 2) for value, width in zip(row, widths)).rstrip() for row in rows)


def render_load(loads):
    if len(loads) != 1:
        rows = [("Home", "Runtime", "Load", "Limit", "Headroom")]
        rows.extend((home["home"], runtime, f"{load['total']:,}", f"{load['limit']:,}", f"{load['headroom']:,}")
                    for home, runtime, load in sorted(
                        ((home, runtime, load) for home in loads for runtime, load in home["runtimes"].items()),
                        key=lambda row: (row[2]["headroom"], row[0]["home"], row[1])))
        return padded_rows(rows)
    home = loads[0]
    blocks = []
    for runtime, load in home["runtimes"].items():
        headroom = load["headroom"]
        blocks.append(f"{home['home']} on {runtime}: {load['total']:,} of {load['limit']:,} {'characters' if runtime == 'claude' else 'bytes'}, {abs(headroom):,} {'left' if headroom >= 0 else 'over'}")
        if load["files"]:
            blocks.append("Files:\n" + padded_rows([("  " + file["path"], f"{file['size']:,}", "" if file["kind"] == "home" else file["kind"]) for file in load["files"]]))
        if load["parts"]:
            blocks.append(biggest_parts(load["parts"]))
    if home["drops"]:
        blocks.append("Dropped:\n" + "\n".join(f"  {'.'.join(drop['path'])} from {drop['origin']}: {drop['reason']}" for drop in home["drops"]))
    return "\n\n".join(blocks)
