from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations

from doctrine import model
from doctrine._compiler.source_graph import model_walk, source_strings
from doctrine.runtime_load import loaded_levels


def project_warnings(session, homes, loads):
    paragraphs, unused, units = [], {}, {}
    base = session.project_config.config_dir
    for flow in session._flow_cache.values():
        for unit in flow.units_by_path.values():
            units[unit.prompt_file.source_path] = unit
    for path, unit in units.items():
        declarations = [
            declaration for declaration in unit.prompt_file.declarations
            if not isinstance(declaration, model.ImportDecl)
        ]
        declarations.extend(
            member for declaration in tuple(declarations) if isinstance(declaration, model.Team)
            for member in declaration.fields if isinstance(member, model.Member)
        )
        declarations.sort(key=lambda declaration: declaration.source_span.line)
        for declaration in declarations:
            for value in model_walk(declaration):
                if isinstance(value, model.ValuesField):
                    for key, _, span in value.items:
                        unused[path, span.line] = key
        for text, line in source_strings(path):
            declaration = next(
                declaration for declaration in reversed(declarations)
                if declaration.source_span.line <= line
            )
            name = ".".join((*unit.module_parts, declaration.name))
            offset = 0
            for paragraph in re.split(r"(\n\s*\n)", text):
                paragraph = re.sub(r"(?<!\w)(_+)(?=\S)(.+?)(?<=\S)\1(?!\w)", r"\2", paragraph, flags=re.S)
                tokens = re.findall(r"\w+", paragraph.casefold())
                if len(tokens) >= 12:
                    paragraphs.append((name, f"{path.relative_to(base)}:{line + offset}", tokens))
                offset += paragraph.count("\n")
    index, candidates = defaultdict(set), defaultdict(int)
    for number, (_, _, tokens) in enumerate(paragraphs):
        for shingle in set(tuple(tokens[i:i + 4]) for i in range(len(tokens) - 3)):
            for other in index[shingle]:
                candidates[other, number] += 1
            index[shingle].add(number)
    groups = defaultdict(list)
    for (left, right), count in sorted(candidates.items()):
        a, b = paragraphs[left], paragraphs[right]
        if count < 3 or a[0] == b[0]:
            continue
        matcher = SequenceMatcher(None, a[2], b[2], autojunk=False)
        if matcher.ratio() < 0.85:
            continue
        words = []
        for tag, i, j, k, l in matcher.get_opcodes():
            if tag != "equal":
                words.extend((" ".join(a[2][i:j]), " ".join(b[2][k:l])))
        groups[a[0], b[0]].append({"sites": [a[1], b[1]], "words": words})
    warnings = []
    for (a, b), examples in groups.items():
        text = f"W301 near copy: {a} and {b} share {len(examples)} paragraphs that differ by a few words."
        for example in examples[:3]:
            text += "\n- " + " and ".join(example["sites"]) + ": " + " / ".join(example["words"])
        text += "\nHint: Share the paragraph and put the different words in `values:`."
        warnings.append({"code": "W301", "text": text, "examples": examples})
    for load in loads:
        for runtime in load["runtimes"].values():
            groups = defaultdict(set)
            paths = {file["path"] for file in runtime["files"] if file["kind"] == "home"}
            for level, data in loaded_levels(homes, load["home"]):
                for path in paths.intersection(data["files"]):
                    for entry in data["map"].entries:
                        if entry.always_on:
                            groups[entry.origin, entry.origin_path].add(path)
            for (origin, _), paths in groups.items():
                for a, b in combinations(sorted(paths), 2):
                    warning = {"code": "W302", "text": (
                        f"W302 double load: {origin} reaches {load['home']} from {a} and {b}."
                    )}
                    if warning not in warnings:
                        warnings.append(warning)
    for (path, line), key in unused.items():
        if (path, line) not in session.value_reads:
            warnings.append({"code": "W304", "text": (
                f"W304 unused value: {key} at {path.relative_to(base)}:{line} is read by no home."
            )})
    disabled = (session.project_config.raw_check or {}).get("disable", [])
    return [warning for warning in warnings if warning["code"] not in disabled]
