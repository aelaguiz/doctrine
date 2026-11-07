from __future__ import annotations

import argparse
import json
import shutil
from contextlib import nullcontext
from tempfile import TemporaryDirectory
from pathlib import Path

from doctrine import model
from doctrine._compiler.declaration_kinds import DECLARATION_KINDS
from doctrine._compiler.source_graph import source_hash
from doctrine.home_commands import resolve_target
from doctrine.emit_common import resolve_pyproject_path
from doctrine.homes import compile_homes, select_homes
from doctrine.runtime_load import home_loads, loaded_levels, runtime_settings, text_size


def diff(args):
    base_args = argparse.Namespace(**vars(args))
    base_args.overlays = []
    base_args.rev = None if args.base_tree else args.base
    if args.base_tree:
        base_args.pyproject = str(Path(args.base_tree) / "pyproject.toml")
    with resolve_target(base_args) as (target, session, _):
        if target is None:
            return 2
        before, old_files, _, _ = compile_homes(target, session=session)
        old_loads = home_loads(target, before, old_files, runtime_settings(target))
        old_hashes = {
            name: source_hash(declaration, target.project_config.config_dir)
            for data in before.values()
            for name, (_, declaration, _) in data["deps_graph"].items()
        }
    new_args = argparse.Namespace(**vars(args))
    if args.overlays:
        new_args.rev = args.base
    with (TemporaryDirectory() if args.base_tree and args.overlays else nullcontext(None)) as temporary:
        if temporary is not None:
            root = Path(temporary)
            shutil.copytree(args.base_tree, root, dirs_exist_ok=True)
            config = resolve_pyproject_path(args.pyproject)
            for path in args.overlays:
                source = (Path.cwd() / path).resolve()
                destination = root / source.relative_to(config.parent)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            new_args.pyproject, new_args.rev = str(root / "pyproject.toml"), None
        with resolve_target(new_args) as (target, session, _):
            if target is None:
                return 2
            after, new_files, _, _ = compile_homes(target, session=session)
            loads = home_loads(target, after, new_files, runtime_settings(target))
            graph = {name: node for data in after.values() for name, node in data["deps_graph"].items()}
            new_hashes = {
                name: source_hash(declaration, target.project_config.config_dir)
                for name, (_, declaration, _) in graph.items()
            }
            selected = select_homes(
                [(home, data["owner"], data["unit"], None) for home, data in {**before, **after}.items()],
                args.selectors,
            )
            outputs = sorted(path for path in old_files.keys() | new_files.keys() if old_files.get(path) != new_files.get(path))
            if sorted(old_files) != sorted(new_files):
                outputs.append("HOMES.contract.json")
                outputs.sort()
            changed_levels = {
                home for home, data in {**before, **after}.items()
                if any(path in outputs and Path(path).name in {"AGENTS.md", "CLAUDE.md"} for path in data["files"])
            }
            old_by_home = {load["home"]: load for load in old_loads}
            by_home = {load["home"]: load for load in loads}
            home_changes, new_sections, details_changes = [], {}, set()
            for home in sorted(selected):
                old, new = before.get(home), after.get(home)
                details_changed = any(
                    old_files.get(path) != new_files.get(path)
                    for data in (old, new) if data for path in data["pointers"]
                )
                if details_changed:
                    details_changes.add(home)
                signatures = [
                    {runtime: [(file["path"], file["text"]) for file in values["files"]]
                     for runtime, values in all_loads[home]["runtimes"].items()} if home in all_loads else {}
                    for all_loads in (old_by_home, by_home)
                ]
                if not details_changed and signatures[0] == signatures[1]:
                    continue
                sizes = []
                for all_loads in (old_by_home, by_home):
                    if home not in all_loads:
                        sizes.append(0)
                    else:
                        runtime = next(iter(all_loads[home]["runtimes"].values()))
                        sizes.append(sum(text_size(file["text"], "claude") for file in runtime["files"]))
                details = [
                    sum(text_size(files[path].decode(), "claude") for path in data["pointers"]) if data else 0
                    for data, files in ((old, old_files), (new, new_files))
                ]
                old_entries = {(entry.path, entry.always_on): entry for entry in old["map"].entries} if old else {}
                new_entries = {(entry.path, entry.always_on): entry for entry in new["map"].entries} if new else {}
                entries = []
                for key in sorted(old_entries.keys() | new_entries.keys()):
                    path = key[0]
                    a, b = old_entries.get(key), new_entries.get(key)
                    if a and b and a.text_hash == b.text_hash:
                        continue
                    entry = b or a
                    entries.append({
                        "path": list(path), "status": "added" if a is None else "removed" if b is None else "changed",
                        "origin": entry.origin,
                        "delta": (b.size_utf16 if b else 0) - (a.size_utf16 if a else 0),
                    })
                    if a is None and path in new["map"].wildcard_keys:
                        new_sections.setdefault((entry.origin, entry.origin_path), []).append(home)
                home_changes.append({"home": home, "delta": {"always_on": sizes[1] - sizes[0], "details": details[1] - details[0]}, "entries": entries})
            result = {
                "homes": home_changes, "changed_levels": changed_levels,
                "new_sections": [{"origin": origin, "path": list(path), "homes": paths} for (origin, path), paths in sorted(new_sections.items())],
                "outputs": outputs,
            }
            changed = []
            for name in sorted(old_hashes.keys() | new_hashes.keys()):
                if old_hashes.get(name) == new_hashes.get(name):
                    continue
                reached = []
                for home in result["homes"]:
                    path = home["home"]
                    levels = loaded_levels(after, path)
                    if any(
                        name in data["map"].deps and level in result["changed_levels"]
                        for level, data in levels
                    ) or (path in details_changes and path in after and name in after[path]["map"].deps):
                        reached.append(path)
                if not reached:
                    continue
                unit, declaration, _ = graph[name]
                kind = next(kind.name for kind in DECLARATION_KINDS if isinstance(declaration, kind.decl_type))
                if isinstance(declaration, model.Agent) and declaration.abstract:
                    kind = "abstract " + kind
                deltas = [home["delta"] for home in result["homes"] if home["home"] in reached]
                changed.append({
                    "name": name, "kind": kind,
                    "site": f"{unit.prompt_file.source_path.relative_to(target.project_config.config_dir)}:{declaration.source_span.line}",
                    "owners": [], "homes": reached, "delta": deltas[0],
                })
            result = {
                "format_version": 1, "base": args.base_tree or args.base,
                "changed_declarations": changed,
                **{key: value for key, value in result.items() if key != "changed_levels"},
                "owned": [],
                "over_budget": [
                    {"home": load["home"], "runtime": runtime, "total": values["total"], "limit": values["limit"]}
                    for load in loads if load["home"] in selected
                    for runtime, values in load["runtimes"].items() if values["total"] > values["limit"]
                ],
            }
            if args.json:
                print(json.dumps(result))
            else:
                declarations, homes = result["changed_declarations"], result["homes"]
                blocks = [f"{len(declarations)} {'declaration' if len(declarations) == 1 else 'declarations'} changed. {len(homes)} {'home' if len(homes) == 1 else 'homes'} changed."]
                for declaration in declarations:
                    deltas = [home["delta"] for home in homes if home["home"] in declaration["homes"]]
                    a, b = min(delta["always_on"] for delta in deltas), max(delta["always_on"] for delta in deltas)
                    size = f"{a:+,}" if a == b else f"{a:+,} to {b:+,}"
                    count = len(deltas)
                    line = f"{declaration['name']} ({declaration['site'].rsplit(':', 1)[0]}) reaches {count} {'home' if count == 1 else 'homes'}, {size} characters"
                    if count > 1 and a == b:
                        line += " each"
                    a, b = min(delta["details"] for delta in deltas), max(delta["details"] for delta in deltas)
                    if a or b:
                        line += " (details " + (f"{a:+,}" if a == b else f"{a:+,} to {b:+,}") + ")"
                    blocks.append(line + ":\n  " + ", ".join(declaration["homes"]))
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
                print("\n\n".join(blocks))
            return 0
