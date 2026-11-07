from __future__ import annotations

from glob import glob
from pathlib import Path

from doctrine import model
from doctrine._compiler.diagnostics import compile_error
from doctrine._compiler.source_graph import declaration_match


def declaration_owners(context, declarations, base):
    owners = {name: set() for name in declarations}
    for name, (unit, person) in declarations.items():
        if not isinstance(person, model.Person):
            continue
        for item in person.owns:
            if isinstance(item, str):
                paths = {Path(path).resolve() for path in glob(str(base / item), recursive=True)
                         if Path(path).is_file()}
                if not paths:
                    raise compile_error(code="E651", summary="Invalid owner",
                        detail=f"Glob `{item}` in `owns:` matches no file.",
                        path=unit.prompt_file.source_path, source_span=person.source_span)
                owned = [key for key, (owner, declaration) in declarations.items()
                         if owner.prompt_file.source_path.resolve() in paths or (
                             isinstance(declaration, (model.Agent, model.WorkflowDecl))
                             and declaration.markdown_path and
                             (base / declaration.markdown_path).resolve() in paths)]
            else:
                match = declaration_match(context, item, unit)
                if match is None:
                    ref = ".".join((*item.module_parts, item.declaration_name))
                    raise compile_error(code="E651", summary="Invalid owner",
                        detail=f"`{ref}` in `owns:` resolves to nothing.",
                        path=unit.prompt_file.source_path, source_span=person.source_span)
                target = ".".join((*match[0].module_parts, match[1].name))
                owned = [target]
                if isinstance(match[1], model.Team):
                    owned.extend(key for key in declarations if key.startswith(target + "."))
            for key in owned:
                owners[key].add(name)
    return owners

