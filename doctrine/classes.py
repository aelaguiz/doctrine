from __future__ import annotations

from os.path import relpath

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.constants import LATE_ROOT
from doctrine._compiler.late_binding import bind_home, map_text
from doctrine._compiler.naming import model_walk, _dotted_ref_name
from doctrine._compiler.resolved_types import ResolvedAgentSlot, ResolvedTypedAgentSlot
from doctrine._compiler.source_graph import declarations_in, declaration_match
from doctrine._compiler.teams import agent_parents, home_value_sources, team_members
from doctrine.homes import compile_homes, home_owners


def class_name(session, unit, decl):
    if isinstance(decl, model.Member):
        unit = decl.team_unit
    return ".".join((*(unit.module_parts if unit is not session.root_flow.entrypoint_unit else ()), decl.name))


def class_tree(target, session):
    context = CompilationContext(session)
    owners, _ = home_owners(target, session)
    declarations = {
        class_name(session, unit, declaration): (unit, declaration, None)
        for unit, declaration in declarations_in(session).values()
        if isinstance(declaration, (model.Agent, model.Team))
        and not isinstance(declaration, model.Member)
    }
    for home, owner, unit, _ in owners:
        name = class_name(session, unit, owner)
        declarations[name] = (unit, owner, home)
    nodes = {}
    parents = {}
    for name, (unit, decl, home) in declarations.items():
        parent = None
        broken = None
        if decl.parent_ref:
            match = declaration_match(context, decl.parent_ref, unit)
            if match and isinstance(match[1], model.Team if isinstance(decl, model.Team) else model.Agent):
                parent = class_name(session, *match)
            else:
                broken = {"name": _dotted_ref_name(decl.parent_ref), "reason": "not found"}
        parents[name] = parent
        uses = []
        def visit(ref, owner):
            if not context._ref_exists_in_registry(ref, unit=owner, registry_name="workflows_by_name"):
                return
            source, workflow = context._resolve_workflow_ref(ref, unit=owner)
            workflow_name = class_name(session, source, workflow)
            if workflow_name in uses:
                return
            uses.append(workflow_name)
            for item in model_walk(workflow.body):
                if isinstance(item, model.WorkflowUse):
                    visit(item.target, source)
        for field in decl.fields:
            if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride)):
                if isinstance(field.value, model.NameRef):
                    visit(field.value, unit)
                else:
                    for item in model_walk(field.value):
                        if isinstance(item, model.WorkflowUse):
                            visit(item.target, unit)
        overrides = [field.key for field in decl.fields if isinstance(field, model.AuthoredSlotOverride) or isinstance(field, model.Member) and field.override]
        overrides += [".".join(field.path) for field in decl.fields if isinstance(field, model.OverridePath)]
        nodes[name] = {
            "name": name, "abstract": decl.abstract, "home": home, "broken_parent": broken,
            "uses": uses,
            "abstract_slots": [field.key for field in decl.fields if isinstance(field, model.AuthoredSlotAbstract)],
            "members": [field.key for field in decl.fields if isinstance(field, model.Member) and not field.override],
            "overrides": overrides,
            "adds": [field.key for field in decl.fields if isinstance(field, model.AuthoredSlotField)] if parent else [],
            "drops": [".".join(field.path) for field in decl.fields if isinstance(field, model.DropItem)],
            "children": [],
        }
    for name in nodes:
        ancestor, seen = parents[name], {name}
        while ancestor in nodes and ancestor not in seen:
            seen.add(ancestor)
            ancestor = parents[ancestor]
        if ancestor == name:
            nodes[name]["broken_parent"] = {"name": parents[name], "reason": "cycle"}
    roots = {"agents": [], "teams": []}
    for name in sorted(nodes):
        parent = parents[name]
        ancestor, seen = parent, {name}
        while ancestor in nodes and ancestor not in seen:
            seen.add(ancestor)
            inherited = declarations[ancestor][1].fields
            inherited_keys = {field.key for field in inherited if isinstance(
                field, (model.AuthoredSlotField, model.AuthoredSlotAbstract, model.AuthoredSlotOverride))}
            nodes[name]["adds"] = [key for key in nodes[name]["adds"] if key not in inherited_keys]
            ancestor = parents[ancestor]
        if parent in nodes and not nodes[name]["broken_parent"]:
            nodes[parent]["children"].append(nodes[name])
        else:
            roots["teams" if isinstance(declarations[name][1], model.Team) else "agents"].append(nodes[name])
    return {"format_version": 1, "view": "tree", **roots}, declarations, parents


def render_tree(tree):
    lines = []
    def visit(nodes, prefix):
        for index, node in enumerate(nodes):
            last = index == len(nodes) - 1
            lead = ("└── " if last else "├── ") if prefix is not None else ""
            text = node["name"]
            if node["abstract"]:
                text += "  (abstract)"
            if node["home"] is not None:
                text += "  " + node["home"]
            for key, label in (("uses", "uses"), ("abstract_slots", "abstract"), ("members", "members"),
                               ("overrides", "overrides"), ("adds", "adds"), ("drops", "drops")):
                if node[key] and (key not in ("overrides", "adds", "drops") or not node["abstract"]):
                    text += "  " + label + " " + ", ".join(node[key])
            if node["broken_parent"]:
                broken = node["broken_parent"]
                text += " parent " + broken["name"] + (" not found" if broken["reason"] == "not found" else " makes a cycle")
            lines.append((prefix or "") + lead + text)
            visit(node["children"], (prefix or "") + ("    " if last else "│   ") if prefix is not None else "")
    for title, key in (("Agents", "agents"), ("Teams", "teams")):
        if lines:
            lines.append("")
        lines.append(title)
        visit(tree[key], None)
    return "\n".join(lines)


def read_values(context, pieces, agent_sources, team_sources):
    values = []
    seen = set()

    def read(text):
        for match in LATE_ROOT.finditer(text):
            root, key = match.groups()
            label = f"{root}:{key}"
            if label in seen:
                continue
            seen.add(label)
            sources = agent_sources if root == "agent" else team_sources
            source = next(((decl, scope, value) for decl, scope in sources
                           for field in decl.fields if isinstance(field, model.ValuesField)
                           for item_key, value, _ in field.items if item_key == key), None)
            setter = class_name(context.session, source[1], source[0]) if source else None
            values.append({"name": label, "default": source[2] if source else None, "set_by": setter})
            if source:
                text = context._interpolate_authored_prose_string(
                    source[2], unit=source[1], owner_label=f"value {key}", surface_label="value text")
                read(text)
        return text

    map_text(pieces, read)
    return values


def walk_classes(nodes):
    for node in nodes:
        yield node
        yield from walk_classes(node["children"])


def class_view(session, tree, declarations, parents, name):
    context = CompilationContext(session)
    unit, owner, _ = declarations[name]
    nodes = {node["name"]: node for node in walk_classes(tree["agents"] + tree["teams"])}
    node = nodes[name]
    slots = context._resolve_agent_slots(owner, unit=unit)
    chain = [(owner, unit), *agent_parents(context, owner, unit)]
    resolved = {slot.key: slot.body for slot in slots if isinstance(slot, ResolvedAgentSlot)}
    typed = {slot.key: slot for slot in slots if isinstance(slot, ResolvedTypedAgentSlot)}
    expanded, _ = context._expand_agent_patches(owner, unit=unit)
    contract = context._resolve_agent_contract(owner, unit=unit)
    pieces = []
    for field in expanded.fields:
        if isinstance(field, (model.RoleScalar, model.RoleBlock)):
            pieces.append(field)
        elif isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride, model.AuthoredSlotInherit)) and field.key in resolved:
            pieces.append(context._compile_resolved_workflow(resolved[field.key], unit=unit,
                          agent_contract=contract, owner_label=f"agent {name}", slot_key=field.key))
    team = isinstance(owner, model.Team)
    reads = read_values(context, tuple(pieces), chain, chain if team else [])
    members = []
    if team:
        for member in team_members(context, owner, unit=unit):
            members.append({"key": member.key, "class": class_name(session, *declaration_match(context, member.parent_ref, member.scope_unit or unit)) if member.parent_ref else None})
    own_slots = [{"key": field.key, "title": None if isinstance(field, model.AuthoredSlotAbstract) else
                  resolved[field.key].title if field.key in resolved else context._display_readable_decl(
                      context._resolve_decl_ref(typed[field.key].entity_ref, unit=unit,
                                                registry_name=f"{typed[field.key].family}s_by_name",
                                                missing_label=typed[field.key].family)[1]),
                  "abstract": isinstance(field, model.AuthoredSlotAbstract)} for field in owner.fields
                 if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride, model.AuthoredSlotAbstract))]
    descendants = list(walk_classes(node["children"]))
    changed = [{"owner": child["name"], "change": kind, "keys": child[kind]}
               for child in descendants for kind in ("overrides", "adds", "drops") if child[kind]]
    uses = list(dict.fromkeys(use for decl, scope in chain
                             for use in nodes[class_name(session, scope, decl)]["uses"]))
    return {"format_version": 1, "view": "class", "name": name,
            "kind": "abstract team" if team and owner.abstract else "team" if team else "abstract agent" if owner.abstract else "agent",
            "site": f'{relpath(unit.prompt_file.source_path, session.project_config.config_dir)}:{owner.source_span.line}',
            "title": owner.title, "parent": parents[name], "children": [child["name"] for child in node["children"]],
            "uses": uses, "homes": sum(child["home"] is not None for child in [node, *descendants]),
            "reads": reads, "slots": own_slots, "members": members, "changed_below": changed}


def agent_view(target, session, name, unit, owner, home):
    homes, _, _, _ = compile_homes(target, session=session, selectors=[home])
    data = homes[home]
    context = CompilationContext(session)
    source_unit = owner.scope_unit or unit if isinstance(owner, model.Member) else unit
    chain = [(owner, source_unit), *agent_parents(context, owner, source_unit)]
    agent_sources, team_sources = home_value_sources(context, owner, unit)
    compiled = context._compile_agent_decl(owner, unit=source_unit)
    values = read_values(context, compiled.fields, agent_sources, team_sources)
    values = [{"name": item["name"], "value": bind_home(context, "{{" + item["name"] + "}}", owner, unit=unit),
               "set_by": item["set_by"]} for item in values]
    sections = []
    for field in data["compiled"].fields:
        key = "role" if isinstance(field, model.RoleScalar) else field.key
        writer = next(((decl, scope) for decl, scope in chain for item in decl.fields
                       if (key == "role" and isinstance(item, (model.RoleScalar, model.RoleBlock)))
                       or (isinstance(item, (model.AuthoredSlotField, model.AuthoredSlotOverride))
                           and item.key == key)), None)
        sections.append({"key": key, "from": class_name(session, writer[1], writer[0]) if writer else field.origin.declaration})
    teams = [team_sources[0], *agent_parents(context, *team_sources[0])] if team_sources else []
    return {
        "format_version": 1, "view": "agent", "name": name,
        "kind": "member" if isinstance(owner, model.Member) else "agent", "home": home,
        "order": [class_name(session, scope, decl) for decl, scope in chain],
        "team": [class_name(session, scope, decl) for decl, scope in teams], "sections": sections, "values": values,
    }


def render_agent(view):
    lines = [f'{view["name"]}  ({view["kind"]})  {view["home"]}',
             "Order: " + ", ".join(view["order"])]
    if view["team"]:
        lines.append("Team: " + ", ".join(view["team"]))
    for title, key, columns in (("Sections", "sections", ("key", "from")),
                                ("Values", "values", ("name", "value", "set_by"))):
        if view[key]:
            lines.extend(("", title + ":"))
            rows = [[" ".join(str(item[column] or "").split()) for column in columns]
                    for item in view[key]]
            widths = [max(len(row[i]) for row in rows) for i in range(len(columns) - 1)]
            lines.extend("  " + "  ".join(value.ljust(widths[i]) if i < len(widths) else value
                                          for i, value in enumerate(row)).rstrip() for row in rows)
    return "\n".join(lines)


def render_class(view):
    lines = [f'{view["name"]}  ({view["kind"]})  {view["site"]}']
    if view["title"]:
        lines.append(view["title"])
    lines.append("")
    for label, key in (("Parent", "parent"), ("Children", "children"), ("Uses", "uses")):
        if view[key]:
            value = ", ".join(view[key]) if isinstance(view[key], list) else view[key]
            lines.append(f"{label}: {value}")
    lines.append(f'Homes: {view["homes"]}')
    for title, key in (("Reads", "reads"), ("Slots", "slots"), ("Members", "members"), ("Changed below", "changed_below")):
        if not view[key]:
            continue
        lines.extend(("", title + ":"))
        for item in view[key]:
            if key == "reads":
                text = item["name"]
                if item["default"] is not None:
                    text += f'  default {" ".join(item["default"].split())}, from {item["set_by"]}'
            elif key == "slots":
                text = item["key"] + "  " + ("(abstract)" if item["abstract"] else item["title"])
            elif key == "members":
                text = item["key"] + ("  " + item["class"] if item["class"] else "")
            else:
                text = item["owner"] + " " + item["change"] + " " + ", ".join(item["keys"])
            lines.append("  " + text)
    return "\n".join(lines)


def render_mermaid(session, tree, declarations, parents, selector):
    nodes = list(walk_classes(tree["agents"] + tree["teams"]))
    chosen = {node["name"] for node in nodes}
    if selector:
        selected = next(node for node in nodes if node["name"] == selector)
        chosen = {node["name"] for node in walk_classes([selected])}
        ancestor = parents[selector]
        while ancestor and ancestor not in chosen:
            chosen.add(ancestor)
            ancestor = parents[ancestor]
    nodes = [node for node in nodes if node["name"] in chosen]
    views = {node["name"]: class_view(session, tree, declarations, parents, node["name"]) for node in nodes}
    label = lambda name: f'`{name}`' if "." in name else name
    lines = ["classDiagram"]
    for node in nodes:
        view = views[node["name"]]
        inherited = {read["name"] for read in views[parents[node["name"]]]["reads"]} if parents[node["name"]] in views else set()
        body = (["<<abstract>>"] if node["abstract"] else [])
        body += [read["name"] for read in view["reads"] if read["name"] not in inherited]
        body += [slot["key"] + "()" + ("*" if slot["abstract"] else "") for slot in view["slots"]]
        lines.append("    class " + label(node["name"]) + (" {" if body else ""))
        lines.extend("        " + item for item in body)
        if body:
            lines.append("    }")
    for name in sorted({use for node in nodes for use in node["uses"]}):
        lines.extend(("    class " + label(name) + " {", "        <<workflow>>", "    }"))
    context = CompilationContext(session)
    for node in nodes:
        name = node["name"]
        if parents[name] in chosen and not node["broken_parent"]:
            lines.append(f"    {label(parents[name])} <|-- {label(name)}")
        unit, decl, _ = declarations[name]
        for field in decl.fields:
            if isinstance(field, (model.AuthoredSlotField, model.AuthoredSlotOverride)):
                refs = [field.value] if isinstance(field.value, model.NameRef) else [item.target for item in model_walk(field.value) if isinstance(item, model.WorkflowUse)]
                for ref in refs:
                    if not context._ref_exists_in_registry(ref, unit=unit, registry_name="workflows_by_name"):
                        continue
                    source, workflow = context._resolve_workflow_ref(ref, unit=unit)
                    lines.append(f'    {label(name)} *-- {label(".".join((*source.module_parts, workflow.name)))}')
    return "\n".join(lines)
