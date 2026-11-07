from __future__ import annotations

import argparse
import json
import shutil
import sys
from contextlib import nullcontext
from os.path import relpath
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.declaration_kinds import DECLARATION_KINDS
from doctrine._compiler.source_graph import (
    build_home_deps, declarations_in, source_hash,
)
from doctrine._compiler.provenance import declaration_owners
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import resolve_pyproject_path
from doctrine.home_commands import resolve_target
from doctrine.homes import compile_homes, home_selectors, select_homes
from doctrine.runtime_load import home_loads, loaded_levels, runtime_settings, text_size


def compile_side(args):
    with resolve_target(args) as (target, session, _):
        if target is None:
            return None
        homes, files, _, _ = compile_homes(target, session=session)
        context = CompilationContext(session)
        build_home_deps(context, homes)
        declarations = declarations_in(session)
        base = target.project_config.config_dir
        return {
            "homes": homes, "files": files, "declarations": declarations, "base_dir": base,
            "owners": declaration_owners(context, declarations, base),
            "loads": home_loads(target, homes, files, runtime_settings(target)),
            "hashes": {
                name: source_hash(declaration, base)
                for name, (_, declaration) in declarations.items()
            },
        }


def compare_homes(before, after, selectors):
    old_homes, new_homes = before["homes"], after["homes"]
    old_files, new_files = before["files"], after["files"]
    selected = select_homes(
        [(home, data["owner"], data["unit"], None)
         for home, data in {**old_homes, **new_homes}.items()],
        home_selectors(
            [data["owner"] for data in {**old_homes, **new_homes}.values()
             if isinstance(data["owner"], model.Team)], selectors
        ),
    )
    outputs = sorted(
        path for path in old_files.keys() | new_files.keys()
        if old_files.get(path) != new_files.get(path)
    )
    if sorted(old_files) != sorted(new_files):
        outputs.append("HOMES.contract.json")
        outputs.sort()
    changed_levels = {
        home for homes in (old_homes, new_homes) for home, data in homes.items()
        if any(path in outputs and Path(path).name in {"AGENTS.md", "CLAUDE.md"}
               for path in data["files"])
    }
    old_loads = {load["home"]: load for load in before["loads"]}
    new_loads = {load["home"]: load for load in after["loads"]}
    home_changes, new_sections, details_changes = [], {}, set()
    levels = {
        level for home in selected for homes in (old_homes, new_homes)
        for level, _ in loaded_levels(homes, home)
    }
    for home in sorted(levels):
        old, new = old_homes.get(home), new_homes.get(home)
        details_changed = any(
            old_files.get(path) != new_files.get(path)
            for data in (old, new) if data for path in data["pointers"]
        )
        if details_changed:
            details_changes.add(home)
        signatures = [
            {runtime: [(file["path"], file["text"]) for file in values["files"]]
             for runtime, values in loads[home]["runtimes"].items()} if home in loads else {}
            for loads in (old_loads, new_loads)
        ]
        if not details_changed and signatures[0] == signatures[1]:
            continue
        sizes = []
        for loads in (old_loads, new_loads):
            if home not in loads:
                sizes.append(0)
            else:
                runtime = next(iter(loads[home]["runtimes"].values()))
                sizes.append(sum(text_size(file["text"], "claude") for file in runtime["files"]))
        details = [
            sum(text_size(files[path].decode(), "claude") for path in data["pointers"])
            if data else 0
            for data, files in ((old, old_files), (new, new_files))
        ]
        old_entries = {
            (entry.path, entry.origin_path, entry.always_on): entry for entry in old["map"].entries
        } if old else {}
        new_entries = {
            (entry.path, entry.origin_path, entry.always_on): entry for entry in new["map"].entries
        } if new else {}
        entries = []
        for key in sorted(old_entries.keys() | new_entries.keys()):
            path = key[0]
            a, b = old_entries.get(key), new_entries.get(key)
            if a and b and a.text_hash == b.text_hash:
                continue
            entry = b or a
            entries.append({
                "path": list(path),
                "status": "added" if a is None else "removed" if b is None else "changed",
                "origin": entry.origin,
                "delta": (b.size_utf16 if b else 0) - (a.size_utf16 if a else 0),
            })
            if old and new and a is None and path in new["map"].wildcard_keys:
                reached = {
                    child for child in selected
                    if child == home or (entry.always_on and any(
                        level == home for level, _ in loaded_levels(new_homes, child)
                    ))
                }
                if reached:
                    new_sections.setdefault((entry.origin, entry.origin_path), set()).update(
                        reached
                    )
        if home in selected:
            home_changes.append({
                "home": home,
                "delta": {"always_on": sizes[1] - sizes[0], "details": details[1] - details[0]},
                "entries": entries,
            })
    return {
        "homes": home_changes, "changed_levels": changed_levels,
        "details_changes": details_changes, "selected": selected,
        "new_sections": [
            {"origin": origin, "path": list(path), "homes": sorted(paths)}
            for (origin, path), paths in sorted(new_sections.items())
        ],
        "outputs": outputs,
    }


def build_result(before, after, comparison, base):
    changed, owned = [], []
    for key in sorted(before["hashes"].keys() | after["hashes"].keys(), key=lambda key: (key[0], key[1].__name__)):
        name = key[0]
        if before["hashes"].get(key) == after["hashes"].get(key):
            continue
        owners = sorted(before["owners"].get(key, set()) | after["owners"].get(key, set()))
        side = after if key in after["declarations"] else before
        unit, declaration = side["declarations"][key]
        if owners or isinstance(declaration, model.Person):
            owned.append({"name": name, "owners": owners})
        reached = []
        for home in comparison["homes"]:
            path = home["home"]
            if any(
                name in data["map"].deps and (
                    level in comparison["changed_levels"]
                    or (level == path and path in comparison["details_changes"])
                )
                for side in (before, after)
                for level, data in loaded_levels(side["homes"], path)
            ):
                reached.append({"home": path, "delta": home["delta"]})
        if not reached:
            continue
        kind = next(
            kind.name for kind in DECLARATION_KINDS if isinstance(declaration, kind.decl_type)
        )
        if isinstance(declaration, model.Agent) and declaration.abstract:
            kind = "abstract " + kind
        source = relpath(unit.prompt_file.source_path, side["base_dir"])
        changed.append({
            "name": name, "kind": kind, "site": f"{source}:{declaration.source_span.line}",
            "owners": owners, "homes": reached,
        })
    return {
        "format_version": 1, "base": base, "changed_declarations": changed,
        "homes": comparison["homes"], "new_sections": comparison["new_sections"],
        "outputs": comparison["outputs"], "owned": owned,
        "over_budget": [
            {"home": load["home"], "runtime": runtime,
             "total": values["total"], "limit": values["limit"]}
            for load in after["loads"] if load["home"] in comparison["selected"]
            for runtime, values in load["runtimes"].items() if values["total"] > values["limit"]
        ],
    }


def render_diff(result):
    declarations, homes = result["changed_declarations"], result["homes"]
    blocks = [
        f"{len(declarations)} {'declaration' if len(declarations) == 1 else 'declarations'} "
        f"changed. {len(homes)} {'home' if len(homes) == 1 else 'homes'} changed."
    ]
    for declaration in declarations:
        deltas = [home["delta"] for home in declaration["homes"]]
        a = min(delta["always_on"] for delta in deltas)
        b = max(delta["always_on"] for delta in deltas)
        size = f"{a:+,}" if a == b else f"{a:+,} to {b:+,}"
        count = len(deltas)
        line = (
            f"{declaration['name']} ({declaration['site'].rsplit(':', 1)[0]}) "
            f"reaches {count} {'home' if count == 1 else 'homes'}, {size} characters"
        )
        if count > 1 and a == b:
            line += " each"
        a = min(delta["details"] for delta in deltas)
        b = max(delta["details"] for delta in deltas)
        if a or b:
            line += " (details " + (f"{a:+,}" if a == b else f"{a:+,} to {b:+,}") + ")"
        blocks.append(line + ":\n  " + ", ".join(home["home"] for home in declaration["homes"]))
    if result["owned"]:
        blocks.append("Owned declarations changed:\n" + "\n".join(
            f"  {entry['name']}" + (f", owned by {', '.join(entry['owners'])}" if entry['owners'] else "")
            for entry in result["owned"]
        ))
    if result["new_sections"]:
        blocks.append("New sections that arrive through inherit *:\n" + "\n".join(
            f"  {entry['origin']}.{'.'.join(entry['path'])} reaches {', '.join(entry['homes'])}"
            for entry in result["new_sections"]
        ))
    if result["over_budget"]:
        blocks.append("Over budget:\n" + "\n".join(
            f"  {entry['home']} on {entry['runtime']}: {entry['total']:,} of {entry['limit']:,}"
            for entry in result["over_budget"]
        ))
    return "\n\n".join(blocks)


def diff(args):
    base_args = argparse.Namespace(**vars(args))
    base_args.overlays = []
    base_args.rev = None if args.base_tree else args.base
    if args.base_tree:
        base_args.pyproject = str(Path(args.base_tree) / "pyproject.toml")
    try:
        before = compile_side(base_args)
    except DoctrineError as exc:
        if exc.code == "E641":
            raise
        print(
            f"Base {args.base_tree or args.base} does not compile, so nothing was compared.",
            file=sys.stderr,
        )
        print(exc, file=sys.stderr)
        return 2
    if before is None:
        return 2
    new_args = argparse.Namespace(**vars(args))
    if args.overlays:
        new_args.rev = args.base
    scratch = TemporaryDirectory() if args.base_tree and args.overlays else nullcontext(None)
    with scratch as temporary:
        if temporary is not None:
            root = Path(temporary)
            shutil.copytree(args.base_tree, root, dirs_exist_ok=True)
            config = resolve_pyproject_path(args.pyproject)
            for path in args.overlays:
                source = (Path.cwd() / path).resolve()
                destination = root / source.relative_to(config.parent)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.exists():
                    shutil.copy2(source, destination)
                else:
                    destination.unlink(missing_ok=True)
            new_args.pyproject, new_args.rev = str(root / "pyproject.toml"), None
        after = compile_side(new_args)
        if after is None:
            return 2
        comparison = compare_homes(before, after, args.selectors)
        result = build_result(before, after, comparison, args.base_tree or args.base)
        print(json.dumps(result) if args.json else render_diff(result))
        return 0
