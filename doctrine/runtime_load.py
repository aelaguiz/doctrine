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
            external.append({"path": item["path"], "size": size, "kind": "external", "text": text})
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
        owner, unit = data["owner"], data["unit"]
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
            for level, item in sorted(homes.items(), key=lambda pair: len(PurePosixPath(pair[0]).parts)):
                if level == home or PurePosixPath(level) in PurePosixPath(home).parents:
                    path = str(PurePosixPath(level) / RUNTIMES[runtime][0])
                    if path in files:
                        content = files[path]
                        if isinstance(content, Path):
                            content = files[str(PurePosixPath(level) / str(content))]
                        text = content.decode()
                        loaded.append({"path": path, "size": text_size(text, runtime), "kind": "home", "text": text})
            limit = next((budget[runtime] for budget in budgets if runtime in budget), setting["limit"])
            total = sum(item["size"] for item in loaded)
            details_size = sum(text_size(files[path].decode(), runtime) for path in data["pointers"])
            runtimes[runtime] = {"unit": RUNTIMES[runtime][1], "total": total, "limit": int(limit),
                "headroom": int(limit) - total, "files": loaded, "details_size": details_size}
        loads.append({"home": home, "agent": owner.name, "runtimes": runtimes})
    return loads


def budget_findings(loads, settings, *, build=False):
    findings = []
    failed = False
    for home in loads:
        for runtime, load in home["runtimes"].items():
            if load["total"] > load["limit"] and not build and settings[runtime]["over"] == "error":
                findings.append(compile_error(code="E630", summary="Over load budget",
                    detail=f"{home['home']} loads {load['total']:,} of {load['limit']:,} {'characters' if runtime == 'claude' else 'bytes'} on {runtime}.\nBiggest parts:"))
                failed = True
            elif load["total"] >= settings[runtime]["warn_at"] * load["limit"]:
                findings.append(f"W306 near budget: {home['home']} loads {load['total']:,} of {load['limit']:,} on {runtime}.")
    return findings, failed
