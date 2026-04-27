from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from doctrine import model
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import DoctrineError
from doctrine.emit_common import (
    EmitTarget,
    SKILL_ENTRYPOINTS,
    display_path,
    ensure_supported_entrypoint,
    emit_error,
    entrypoint_output_name,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_pyproject_path,
)
from doctrine.parser import parse_file
from doctrine.renderer import render_readable_block
from doctrine.skill_source_receipts import (
    SOURCE_RECEIPT_FILE_NAME,
    build_skill_source_receipt_payload,
    render_skill_source_receipt_json,
    update_skill_lock,
)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)

        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=path_location(config_path),
                )
            emitted = emit_target_skill(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled skill-package trees for configured Doctrine targets."
    )
    parser.add_argument(
        "--pyproject",
        help=(
            "Path to the pyproject.toml that defines [tool.doctrine.emit]. "
            "Defaults to the nearest parent pyproject.toml from the current working directory."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        required=True,
        help="Configured target name from [tool.doctrine.emit.targets]. Repeat to emit multiple targets.",
    )
    return parser


def emit_target_skill(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
    update_lock: bool = True,
) -> tuple[Path, ...]:
    ensure_supported_entrypoint(
        target.entrypoint,
        allowed_entrypoints=SKILL_ENTRYPOINTS,
        owner_label=f"emit_skill target `{target.name}`",
    )
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=path_location(target.entrypoint),
        )

    session = CompilationSession(prompt_file, project_config=target.project_config)
    try:
        compiled = session.compile_skill_package()
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )
    package_decl = _target_skill_package_decl(session)

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)
    markdown_path = emitted_dir / entrypoint_output_name(target.entrypoint)
    contract_path = emitted_dir / "SKILL.contract.json"
    source_receipt_path = emitted_dir / SOURCE_RECEIPT_FILE_NAME
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_skill_package_markdown(compiled), encoding="utf-8")
    emitted_paths: list[Path] = [markdown_path]
    if _should_emit_skill_package_contract_json(compiled):
        contract_path.write_text(render_skill_package_contract_json(compiled), encoding="utf-8")
        emitted_paths.append(contract_path)
    for bundled_file in compiled.files:
        bundled_path = emitted_dir / Path(bundled_file.path)
        bundled_path.parent.mkdir(parents=True, exist_ok=True)
        bundled_path.write_bytes(bundled_file.content)
        emitted_paths.append(bundled_path)
    source_receipt_payload = build_skill_source_receipt_payload(
        target=target,
        compiled=compiled,
        package_decl=package_decl,
        session=session,
        emitted_dir=emitted_dir,
        emitted_paths=tuple(emitted_paths),
    )
    source_receipt_path.write_text(
        render_skill_source_receipt_json(source_receipt_payload),
        encoding="utf-8",
    )
    emitted_paths.append(source_receipt_path)
    if update_lock and output_dir_override is None:
        update_skill_lock(
            target=target,
            receipt_payload=source_receipt_payload,
            receipt_path=source_receipt_path,
        )
    return tuple(emitted_paths)


def render_skill_package_markdown(compiled) -> str:
    frontmatter_lines = ["---"]
    for key, value in compiled.frontmatter:
        frontmatter_lines.append(f"{key}: {json.dumps(value)}")
    frontmatter_lines.extend(["---", ""])

    rendered_root = render_readable_block(compiled.root, depth=1).rstrip()
    if rendered_root:
        frontmatter_lines.append(rendered_root)
    return "\n".join(frontmatter_lines).rstrip() + "\n"


def render_skill_package_contract_json(compiled) -> str:
    payload = {
        "contract_version": compiled.contract.contract_version,
        "package": {
            "name": compiled.contract.package_name,
            "title": compiled.contract.package_title,
        },
        "host_contract": {
            slot.key: _render_host_slot(slot)
            for slot in compiled.contract.host_contract
        },
        "artifacts": {
            artifact.path: {
                "kind": artifact.kind,
                **({"source": artifact.source} if artifact.source is not None else {}),
                "referenced_host_paths": list(artifact.referenced_host_paths),
            }
            for artifact in compiled.contract.artifacts
        },
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def _render_host_slot(slot) -> dict:
    if isinstance(slot, model.ResolvedReceiptHostSlotRef):
        receipt = slot.receipt
        payload: dict = {
            "family": slot.family,
            "title": receipt.title,
            "receipt": slot.canonical_name,
            "fields": {
                field.key: _render_resolved_receipt_field(field)
                for field in receipt.fields
            },
            "json_schema": _render_resolved_receipt_json_schema(receipt),
        }
        if receipt.routes:
            payload["routes"] = {
                route.key: _render_resolved_receipt_route(route)
                for route in receipt.routes
            }
        return payload
    if isinstance(slot, model.ReceiptHostSlot):
        return {
            "family": slot.family,
            "title": slot.title,
            "fields": {field.key: _render_receipt_field(field) for field in slot.fields},
        }
    return {
        "family": slot.family,
        "title": slot.title,
    }


def _render_resolved_receipt_route(
    route: model.ResolvedReceiptRouteField,
) -> dict:
    return {
        "title": route.title,
        "choices": {
            choice.key: {
                "title": choice.title,
                "target_kind": choice.target_kind,
                "target": choice.target_name,
            }
            for choice in route.choices
        },
    }


def _render_receipt_field(field) -> dict:
    payload: dict = {"type": field.type_ref.declaration_name}
    if field.list_element:
        payload["list"] = True
    return payload


def _render_resolved_receipt_field(field: model.ResolvedReceiptField) -> dict:
    payload: dict = {"type": field.type_name, "kind": field.type_kind}
    if field.list_element:
        payload["list"] = True
    return payload


def _render_resolved_receipt_json_schema(
    receipt: model.ResolvedReceipt,
) -> dict:
    properties: dict[str, object] = {
        field.key: _render_resolved_receipt_field_json_schema(field)
        for field in receipt.fields
    }
    required = [field.key for field in receipt.fields]
    for route in receipt.routes:
        properties[route.key] = {
            "type": "string",
            "enum": [choice.key for choice in route.choices],
        }
        required.append(route.key)
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


def _render_resolved_receipt_field_json_schema(
    field: model.ResolvedReceiptField,
) -> dict:
    item_schema = _render_resolved_receipt_type_json_schema(
        type_kind=field.type_kind,
        type_name=field.type_name,
    )
    if field.list_element:
        return {
            "type": "array",
            "items": item_schema,
        }
    return item_schema


def _render_resolved_receipt_type_json_schema(
    *,
    type_kind: str,
    type_name: str,
) -> dict:
    if type_kind == "builtin":
        return {"type": type_name}
    if type_kind == "enum":
        return {"type": "string"}
    if type_kind in {"receipt", "schema", "table"}:
        return {"type": "object"}
    raise ValueError(f"Unsupported resolved receipt field kind: {type_kind}")


def _should_emit_skill_package_contract_json(compiled) -> bool:
    return bool(compiled.contract.host_contract or compiled.contract.artifacts)


def _target_skill_package_decl(session: CompilationSession) -> model.SkillPackageDecl:
    packages = tuple(session.root_flow.skill_packages_by_name.values())
    if len(packages) != 1:
        raise emit_error(
            "E558",
            "Emit target must resolve one skill package",
            "emit_skill expected the entrypoint to compile exactly one skill package.",
            location=path_location(session.root_flow.entrypoint_path),
        )
    return packages[0]


if __name__ == "__main__":
    raise SystemExit(main())
