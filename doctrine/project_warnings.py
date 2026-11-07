from __future__ import annotations

import ast
import re
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from os.path import relpath
from pathlib import PurePosixPath

from lark import Token

from doctrine import model
from doctrine._compiler.teams import _message_target
from doctrine._compiler.naming import _dotted_ref_name
from doctrine._compiler.provenance import collect_quotes
from doctrine._compiler.naming import model_walk
from doctrine._compiler.teams import resolve_message_recipient, team_members
from doctrine.parser import _build_lark_parser
from doctrine.runtime_load import loaded_levels


def near_copy_warnings(session):
    paragraphs, unused, from_files = [], {}, set()
    base = session.project_config.config_dir
    units = {unit.prompt_file.source_path: unit for unit in session.units()}
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
        texts = []
        tree = _build_lark_parser().parse(path.read_text())
        for token in tree.scan_values(lambda value: isinstance(value, Token)):
            if token.type not in {"ESCAPED_STRING", "MULTILINE_STRING"}:
                continue
            declaration = next(
                declaration for declaration in reversed(declarations)
                if declaration.source_span.line <= token.line
            )
            name = ".".join((*unit.module_parts, declaration.name))
            texts.append((name, path, token.line, ast.literal_eval(str(token))))
        for declaration in declarations:
            if (isinstance(declaration, (model.Agent, model.WorkflowDecl))
                    and declaration.markdown_path):
                source = base / declaration.markdown_path
                if source.resolve() not in from_files:
                    from_files.add(source.resolve())
                    name = ".".join((*unit.module_parts, declaration.name))
                    texts.append((name, source, 1, source.read_text()))
        for name, source, line, text in texts:
            offset = 0
            for paragraph in re.split(r"(\n\s*\n)", text):
                paragraph = re.sub(
                    r"(?<!\w)(_+)(?=\S)(.+?)(?<=\S)\1(?!\w)", r"\2", paragraph, flags=re.S
                )
                tokens = re.findall(r"\w+", paragraph.casefold())
                if len(tokens) >= 12:
                    paragraphs.append((name, f"{relpath(source, base)}:{line + offset}", tokens))
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
        text = (
            f"W301 near copy: {a} and {b} share {len(examples)} "
            f"{'paragraph' if len(examples) == 1 else 'paragraphs'} "
            "that differ by a few words."
        )
        for example in examples[:3]:
            text += "\n- " + " and ".join(example["sites"])
            if example["words"]:
                text += ": " + " / ".join(example["words"])
        text += "\nHint: Share the paragraph and put the different words in `values:`."
        warnings.append({"code": "W301", "text": text, "examples": examples})
    return warnings, unused


def double_load_warnings(homes, loads):
    warnings = []
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
    return warnings


def project_warnings(session, homes, loads, context, all_declarations):
    warnings, unused = near_copy_warnings(session)
    base = session.project_config.config_dir
    warnings.extend(double_load_warnings(homes, loads))
    for (path, line), key in unused.items():
        if (path, line) not in session.value_reads:
            warnings.append({"code": "W304", "text": (
                f"W304 unused value: {key} at {relpath(path, base)}:{line} is read by no home."
            )})
    for row in collect_quotes(context, all_declarations, base):
        if not row["cited_in"]:
            warnings.append({"code": "W305", "text": (
                f"W305 unused quote: {row['key']} at {row['site']} is cited nowhere."
            )})
    warnings.extend(message_warnings(context, homes))
    return warnings


def message_warnings(context, homes):
    outputs, warnings = {}, []
    for data in homes.values():
        outputs.update(context._resolve_agent_contract(data["owner"], unit=data["unit"]).outputs)
    for key, (unit, declaration) in outputs.items():
        target = _message_target(declaration)
        if not target:
            continue
        recipient = next(item.value for item in target.body if item.key == "to")
        if not isinstance(recipient, model.NameRef):
            continue
        recipient_unit, receiver = resolve_message_recipient(context, recipient, unit=unit)
        if receiver.abstract:
            continue
        if isinstance(receiver, model.Team):
            flow = context.session.flow_for_unit(recipient_unit)
            readers = (
                context._resolve_agent_contract(member, unit=team_unit).inputs
                for team_unit in flow.units_by_path.values()
                for team in team_unit.declarations.teams_by_name.values()
                if not team.abstract and (
                    team.home == receiver.home
                    or PurePosixPath(receiver.home) in PurePosixPath(team.home).parents
                )
                for member in team_members(context, team, unit=team_unit)
            )
        else:
            readers = (context._resolve_agent_contract(receiver, unit=recipient_unit).inputs,)
        if not any(key in inputs for inputs in readers):
            warnings.append({"code": "W303", "text": (
                f"W303 message without reader: {'.'.join((*unit.module_parts, declaration.name))} "
                f"goes to {_dotted_ref_name(recipient)}, "
                "and nothing there reads it."
            )})
    return warnings
