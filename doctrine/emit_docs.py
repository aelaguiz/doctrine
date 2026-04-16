from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from doctrine.compiler import CompilationSession
from doctrine._compiler.package_layout import (
    BundledPackageFile,
    bundle_ordinary_package_files,
    new_package_output_registry,
)
from doctrine.diagnostics import CompileError, DoctrineError
from doctrine.emit_common import (
    DOCS_ENTRYPOINTS,
    EmitTarget,
    RuntimeEmitRoot,
    agent_slug,
    collect_runtime_emit_roots,
    display_path,
    ensure_supported_entrypoint,
    emit_error,
    entrypoint_output_name,
    entrypoint_relative_dir,
    load_emit_targets,
    path_location,
    resolve_pyproject_path,
)
from doctrine.project_config import ProvidedPromptRoot
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

FINAL_OUTPUT_CONTRACT_FILENAME = "final_output.contract.json"
FINAL_OUTPUT_CONTRACT_VERSION = 1


@dataclass(slots=True, frozen=True)
class RuntimeEmitPlan:
    root: RuntimeEmitRoot
    markdown_path: Path
    provider_root: ProvidedPromptRoot | None = None
    bundled_files: tuple[BundledPackageFile, ...] = ()
    soul_prompt_path: Path | None = None
    soul_output_path: Path | None = None


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
            emitted = emit_target(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled Markdown trees for configured Doctrine targets."
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


def emit_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    ensure_supported_entrypoint(
        target.entrypoint,
        allowed_entrypoints=DOCS_ENTRYPOINTS,
        owner_label=f"emit_docs target `{target.name}`",
    )
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=path_location(target.entrypoint),
        )
    session = CompilationSession(prompt_file, project_config=target.project_config)
    runtime_roots = _runtime_emit_roots_for_target(session, target=target)
    if not runtime_roots:
        raise emit_error(
            "E502",
            "Emit target has no concrete agents",
            f"Emit target `{target.name}` has no concrete agents in `{target.entrypoint}`.",
            location=path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    planned_emits = tuple(
        _build_runtime_emit_plan(
            runtime_root,
            target=target,
            output_root=output_root,
            provider_root=session.provided_prompt_root_for(
                runtime_root.unit.prompt_root
            ),
        )
        for runtime_root in runtime_roots
    )

    seen_paths: dict[Path, str] = {}
    for plan in planned_emits:
        owner_label = ".".join((*plan.root.unit.module_parts, plan.root.agent_name)) or plan.root.agent_name
        markdown_path = plan.markdown_path
        prior_agent = seen_paths.get(markdown_path)
        if prior_agent is not None:
            raise emit_error(
                "E505",
                "Emit target path collision",
                f"Emit target `{target.name}` maps both `{prior_agent}` and `{owner_label}` to `{markdown_path}`.",
                location=path_location(markdown_path),
            )
        seen_paths[markdown_path] = owner_label
        if plan.soul_output_path is not None:
            prior_agent = seen_paths.get(plan.soul_output_path)
            if prior_agent is not None:
                raise emit_error(
                    "E505",
                    "Emit target path collision",
                    f"Emit target `{target.name}` maps both `{prior_agent}` and `{owner_label}` to `{plan.soul_output_path}`.",
                    location=path_location(plan.soul_output_path),
                )
            seen_paths[plan.soul_output_path] = owner_label
        for bundled_file in plan.bundled_files:
            bundled_path = markdown_path.parent / bundled_file.path
            prior_agent = seen_paths.get(bundled_path)
            if prior_agent is not None:
                raise emit_error(
                    "E505",
                    "Emit target path collision",
                    f"Emit target `{target.name}` maps both `{prior_agent}` and `{owner_label}` to `{bundled_path}`.",
                    location=path_location(bundled_path),
                )
            seen_paths[bundled_path] = owner_label

    try:
        compiled_agents = session.compile_agents_from_units(
            tuple((plan.root.unit, plan.root.agent_name) for plan in planned_emits)
        )
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}`",
            location=path_location(target.entrypoint),
        )

    emitted_paths: list[Path] = []
    for plan, compiled in zip(
        planned_emits,
        compiled_agents,
        strict=True,
    ):
        rendered = render_markdown(compiled)
        plan.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        plan.markdown_path.write_text(rendered)
        emitted_paths.append(plan.markdown_path)
        final_output = compiled.final_output
        if (
            final_output is not None
            and final_output.generated_schema_relpath is not None
            and final_output.lowered_schema is not None
        ):
            schema_path = plan.markdown_path.parent / final_output.generated_schema_relpath
            schema_path.parent.mkdir(parents=True, exist_ok=True)
            schema_path.write_text(
                json.dumps(final_output.lowered_schema, indent=2) + "\n",
                encoding="utf-8",
            )
            emitted_paths.append(schema_path)
        final_output_contract_payload = _final_output_contract_payload(
            plan=plan,
            compiled=compiled,
            target=target,
        )
        if final_output_contract_payload is not None:
            final_output_contract_path = (
                plan.markdown_path.parent / FINAL_OUTPUT_CONTRACT_FILENAME
            )
            final_output_contract_path.write_text(
                json.dumps(final_output_contract_payload, indent=2) + "\n",
                encoding="utf-8",
            )
            emitted_paths.append(final_output_contract_path)
        if plan.soul_prompt_path is not None and plan.soul_output_path is not None:
            soul_compiled = _compile_runtime_package_soul(
                plan,
                target=target,
            )
            plan.soul_output_path.parent.mkdir(parents=True, exist_ok=True)
            plan.soul_output_path.write_text(
                render_markdown(soul_compiled),
                encoding="utf-8",
            )
            emitted_paths.append(plan.soul_output_path)
        for bundled_file in plan.bundled_files:
            bundled_path = plan.markdown_path.parent / bundled_file.path
            bundled_path.parent.mkdir(parents=True, exist_ok=True)
            bundled_path.write_bytes(bundled_file.content)
            emitted_paths.append(bundled_path)

    return tuple(emitted_paths)


def _final_output_contract_payload(
    *,
    plan: RuntimeEmitPlan,
    compiled,
    target: EmitTarget,
) -> dict[str, object] | None:
    if compiled.final_output is None and compiled.review is None:
        return None
    return {
        "contract_version": FINAL_OUTPUT_CONTRACT_VERSION,
        "agent": {
            "name": compiled.name,
            "slug": agent_slug(compiled.name),
            "entrypoint": _agent_entrypoint_relpath(plan=plan, target=target),
        },
        "route": _serialize_route_contract(compiled.route),
        "final_output": _serialize_final_output_contract(compiled.final_output),
        **(
            {"review": _serialize_review_contract(compiled.review)}
            if compiled.review is not None
            else {}
        ),
    }


def _agent_entrypoint_relpath(*, plan: RuntimeEmitPlan, target: EmitTarget) -> str:
    source_path = plan.root.unit.prompt_file.source_path
    if source_path is None:
        return target.entrypoint.as_posix()
    if plan.provider_root is not None:
        provider_path = Path(plan.provider_root.path).resolve()
        try:
            provider_relpath = source_path.resolve().relative_to(provider_path)
        except ValueError:
            pass
        else:
            return f"{plan.provider_root.name}:{provider_relpath.as_posix()}"
    project_root = target.project_config.config_dir.resolve()
    resolved = source_path.resolve()
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError:
        return resolved.as_posix()


def _serialize_route_contract(route) -> dict[str, object]:
    if route is None:
        return {
            "exists": False,
            "behavior": "never",
            "has_unrouted_branch": False,
            "unrouted_review_verdicts": [],
            "branches": [],
        }
    return {
        "exists": route.exists,
        "behavior": route.behavior,
        "has_unrouted_branch": route.has_unrouted_branch,
        "unrouted_review_verdicts": list(route.unrouted_review_verdicts),
        **(
            {
                "selector": {
                    "surface": route.selector.surface,
                    **(
                        {"field_path": list(route.selector.field_path)}
                        if route.selector.field_path is not None
                        else {}
                    ),
                    **(
                        {"null_behavior": route.selector.null_behavior}
                        if route.selector.null_behavior is not None
                        else {}
                    ),
                }
            }
            if route.selector is not None
            else {}
        ),
        "branches": [
            {
                "target": {
                    "key": branch.target.key,
                    "module_parts": list(branch.target.module_parts),
                    "name": branch.target.name,
                    "title": branch.target.title,
                },
                "label": branch.label,
                "summary": branch.summary,
                **(
                    {"review_verdict": branch.review_verdict}
                    if branch.review_verdict is not None
                    else {}
                ),
                "choice_members": [
                    {
                        "member_key": member.member_key,
                        "member_title": member.member_title,
                        "member_wire": member.member_wire,
                        **(
                            {"enum_module_parts": list(member.enum_module_parts)}
                            if member.enum_module_parts
                            else {}
                        ),
                        **(
                            {"enum_name": member.enum_name}
                            if member.enum_name is not None
                            else {}
                        ),
                    }
                    for member in branch.choice_members
                ],
            }
            for branch in route.branches
        ],
    }


def _serialize_final_output_contract(final_output) -> dict[str, object]:
    if final_output is None:
        return {
            "exists": False,
            "declaration_key": None,
            "declaration_name": None,
            "format_mode": None,
            "schema_profile": None,
            "emitted_schema_relpath": None,
        }
    return {
        "exists": True,
        "declaration_key": _output_decl_key_text(final_output.output_key),
        "declaration_name": final_output.output_name,
        "format_mode": final_output.format_mode,
        "schema_profile": final_output.schema_profile,
        "emitted_schema_relpath": final_output.generated_schema_relpath,
    }


def _serialize_review_contract(review) -> dict[str, object]:
    return {
        "exists": True,
        "comment_output": {
            "declaration_key": _output_decl_key_text(review.comment_output.output_key),
            "declaration_name": review.comment_output.output_name,
        },
        "carrier_fields": {
            field_name: _field_path_text(field_path)
            for field_name, field_path in review.carrier_fields
        },
        "final_response": {
            "mode": review.final_response.mode,
            "declaration_key": (
                _output_decl_key_text(review.final_response.output_key)
                if review.final_response.output_key is not None
                else None
            ),
            "declaration_name": review.final_response.output_name,
            "review_fields": {
                field_name: _field_path_text(field_path)
                for field_name, field_path in review.final_response.review_fields
            },
            "control_ready": review.final_response.control_ready,
        },
        "outcomes": {
            outcome_name: {
                "exists": outcome.exists,
                "verdict": outcome.verdict,
                "route_behavior": outcome.route_behavior,
            }
            for outcome_name, outcome in review.outcomes
        },
    }


def _output_decl_key_text(output_key: tuple[tuple[str, ...], str]) -> str:
    module_parts, declaration_name = output_key
    if not module_parts:
        return declaration_name
    return ".".join((*module_parts, declaration_name))


def _field_path_text(field_path: tuple[str, ...]) -> str:
    return ".".join(field_path)


def _emit_path_for_agent(emitted_dir: Path, agent_name: str, *, output_name: str) -> Path:
    slug = agent_slug(agent_name)
    if emitted_dir.parts and emitted_dir.parts[-1] == slug:
        return emitted_dir / output_name
    return emitted_dir / slug / output_name


def _runtime_emit_roots_for_target(
    session: CompilationSession,
    *,
    target: EmitTarget,
) -> tuple[RuntimeEmitRoot, ...]:
    if target.entrypoint.name == "SOUL.prompt":
        return tuple(
            RuntimeEmitRoot(unit=session.root_unit, agent_name=agent_name)
            for agent_name in session.root_unit.agents_by_name
            if not session.root_unit.agents_by_name[agent_name].abstract
        )
    return collect_runtime_emit_roots(session)


def _build_runtime_emit_plan(
    runtime_root: RuntimeEmitRoot,
    *,
    target: EmitTarget,
    output_root: Path,
    provider_root: ProvidedPromptRoot | None,
) -> RuntimeEmitPlan:
    if runtime_root.unit.module_source_kind != "runtime_package":
        emitted_dir = output_root / entrypoint_relative_dir(target.entrypoint)
        return RuntimeEmitPlan(
            root=runtime_root,
            markdown_path=_emit_path_for_agent(
                emitted_dir,
                runtime_root.agent_name,
                output_name=entrypoint_output_name(target.entrypoint),
            ),
            provider_root=provider_root,
        )

    source_path = runtime_root.unit.prompt_file.source_path
    package_root = runtime_root.unit.package_root
    if source_path is None or package_root is None:
        dotted_name = ".".join(runtime_root.unit.module_parts)
        raise CompileError(
            f"Runtime package {dotted_name or runtime_root.agent_name} is missing package metadata."
        )
    emitted_dir = output_root / entrypoint_relative_dir(source_path)
    soul_prompt_path = package_root / "SOUL.prompt"
    has_soul = soul_prompt_path.is_file()
    registry = new_package_output_registry(
        owner_label=f"runtime package {'.'.join(runtime_root.unit.module_parts) or runtime_root.agent_name}",
        compiler_owned_paths=("AGENTS.md", "SOUL.md"),
    )
    ordinary_files: list[Path] = []
    for bundled_path in sorted(path for path in package_root.rglob("*") if path.is_file()):
        if bundled_path == source_path:
            continue
        if has_soul and bundled_path == soul_prompt_path:
            continue
        if bundled_path.suffix == ".prompt":
            raise CompileError(
                "Runtime packages may not contain extra prompt files: "
                f"{bundled_path.relative_to(package_root).as_posix()}"
            ).ensure_location(path=bundled_path)
        ordinary_files.append(bundled_path)
    return RuntimeEmitPlan(
        root=runtime_root,
        markdown_path=emitted_dir / "AGENTS.md",
        provider_root=provider_root,
        bundled_files=bundle_ordinary_package_files(
            package_root,
            ordinary_files,
            registry=registry,
        ),
        soul_prompt_path=soul_prompt_path if has_soul else None,
        soul_output_path=emitted_dir / "SOUL.md" if has_soul else None,
    )


def _compile_runtime_package_soul(
    plan: RuntimeEmitPlan,
    *,
    target: EmitTarget,
):
    if plan.soul_prompt_path is None:
        raise CompileError("Internal compiler error: missing SOUL prompt plan.")
    prompt_file = parse_file(plan.soul_prompt_path)
    session = CompilationSession(prompt_file, project_config=target.project_config)
    concrete_agents = tuple(
        agent_name
        for agent_name, agent in session.root_unit.agents_by_name.items()
        if not agent.abstract
    )
    # Keep the package companion explicit: one concrete agent, same identity.
    if len(concrete_agents) != 1:
        raise CompileError(
            "Runtime package sibling `SOUL.prompt` must define exactly one concrete agent."
        ).ensure_location(path=plan.soul_prompt_path)
    if concrete_agents[0] != plan.root.agent_name:
        raise CompileError(
            "Runtime package sibling `SOUL.prompt` must match the concrete agent name in sibling `AGENTS.prompt`."
        ).ensure_location(path=plan.soul_prompt_path)
    return session.compile_agent(concrete_agents[0])


if __name__ == "__main__":
    raise SystemExit(main())
